#!/usr/bin/env python3
r"""apply_chemistry — put the pipeline's verified chemistry onto the mapped sites.

Run AFTER export_geojson.py; it rewrites web/data/hazard_sites.geojson in place. The site
popup then shows one of exactly three things, never a mixture:

  verified         the chemicals the pipeline verified against a source table cell
  ocr_constrained  the documents yielded chemicals but every one is stuck behind OCR or an
                   unresolved verification, so nothing is claimed yet
  in_process       no chemistry has been extracted for this site yet

Only verified sites display a chemical listing. A site whose chemicals could not be verified
shows the pending note instead of its old free-text list — the free-text `chemicals` field
from the master CSV was never checked against a document and must not sit beside verified
data looking equivalent.

Site identity comes from chem_site_match (program number, then name, then coordinates).

Usage:  python apply_chemistry.py [--geojson <path>] [--report <path>]
"""
from __future__ import annotations

import argparse
import collections
import csv
import glob
import json
import os
import re

import chem_site_match as M

BUILD_CHEM = M.BUILD_CHEM
DEFAULT_GEOJSON = r'C:\Users\mcsha\Niagra\web\data\hazard_sites.geojson'
DEFAULT_REPORT = r'C:\Users\mcsha\Niagra\csv\chem_map_status.csv'
HAND_VERIFIED = r'C:\Users\mcsha\Niagra\csv\hand_verified_chemicals.json'

SHIP_VERIFICATION = 'VERIFIED'
SHIP_DETECTION = 'DETECTED'

# The pipeline reports collapsed categories ("PCBs"); hand validation reports the specific
# compounds ("Aroclor 1248"). Listing both makes one finding look like several, so an umbrella
# term is dropped when the hand list already supplies its members. Extend this as more sites are
# hand-validated — an umbrella with no match here simply stays, which is the safe direction.
SUPERSEDED_BY_SPECIFIC = {
    'PCBs':            re.compile(r'^aroclor', re.I),
    'PAHs (other)':    re.compile(r'^(acenaphth|anthracene|benzo|chrysene|dibenz|fluoranth|'
                                  r'fluorene|indeno|naphthalene|perylene|phenanthrene|pyrene)', re.I),
    'DDT / DDE / DDD': re.compile(r'dd[tde]\b', re.I),
    'Chromium':        re.compile(r'^chromium\s*,', re.I),
    'Lindane / BHC':   re.compile(r'\bbhc\b|lindane', re.I),
    'BHC isomers (alpha/beta/delta)': re.compile(r'\bbhc\b', re.I),
    'Acetone / ketones': re.compile(r'^(acetone|2-butanone|2-hexanone|4-methyl-2-pentanone)', re.I),
    'Phthalates':      re.compile(r'phthalate', re.I),
    'Phenols':         re.compile(r'phenol', re.I),
    'Dichlorobenzenes': re.compile(r'-dichlorobenzene', re.I),
    'Trimethylbenzenes': re.compile(r'-trimethylbenzene', re.I),
    'Xylene':          re.compile(r'xylene', re.I),
}

NOTE_OCR = ('OCR Constrained. Hand validation pending. Chemical lists will be added upon '
            'human verification of detected chemicals')
NOTE_PENDING = ('New reports added to database and are in process - detected chemicals will '
                'be added upon completion')

# Same danger-ranked list export_geojson.py uses for the chemical dropdown, matched here
# against the verified chemical NAMES rather than the unverified free-text blob.
CHEM_RX = [(n, re.compile(p, re.I)) for n, p in [
    ('Dioxins / TCDD',      r'dioxin|tcdd|2,3,7,8'),
    ('Asbestos',            r'asbestos'),
    ('Benzene',             r'\bbenzene\b'),
    ('Vinyl chloride',      r'vinyl chloride'),
    ('Arsenic',             r'arsenic'),
    ('PCBs',                r'\bpcb'),
    ('Hexavalent chromium', r'chromium|hexavalent'),
    ('TCE',                 r'trichloroethene|\btce\b'),
    ('Cadmium',             r'cadmium'),
    ('Lead',                r'\blead\b'),
    ('Benzo(a)pyrene',      r'benzo\(a\)pyrene'),
    ('Lindane / BHC',       r'lindane|\bbhc\b|hexachlorocyclohexane'),
    ('Beryllium',           r'beryllium'),
    ('Mercury',             r'mercury'),
    ('Hexachlorobenzene',   r'hexachlorobenzene'),
    ('Cyanide',             r'cyanide'),
]]


def read_site_rollup(build_dir):
    """Verified detections and withheld counts for one built site."""
    hits = glob.glob(os.path.join(BUILD_CHEM, build_dir, '*_detected_chemicals.csv'))
    if not hits:
        return None
    verified, waste = [], []
    withheld = collections.Counter()
    n_rows = 0
    for path in hits:
        for r in csv.DictReader(open(path, encoding='utf-8-sig')):
            chem = (r.get('chemical') or '').strip()
            if not chem:
                continue
            n_rows += 1
            ver = (r.get('verification_status') or '').strip()
            det = (r.get('detection_status') or '').strip()
            is_waste = (r.get('waste_status') or '').strip().upper().startswith('WASTE')
            if ver == SHIP_VERIFICATION and det == SHIP_DETECTION:
                entry = {'chemical': chem,
                         'provenance': (r.get('example_provenance') or '').strip()}
                (waste if is_waste else verified).append(entry)
            else:
                withheld[det if det and det != SHIP_DETECTION else (ver or 'UNKNOWN')] += 1
    return {'verified': verified, 'waste': waste,
            'withheld': dict(withheld), 'n_rows': n_rows}


def load_hand_verified():
    """{program_number: record} of chemicals a person confirmed against the source document."""
    try:
        return json.load(open(HAND_VERIFIED, encoding='utf-8'))['sites']
    except (OSError, KeyError, ValueError):
        return {}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--geojson', default=DEFAULT_GEOJSON)
    ap.add_argument('--report', default=DEFAULT_REPORT)
    args = ap.parse_args()

    doc = json.load(open(args.geojson, encoding='utf-8'))
    features = doc['features']

    build_sites = M.load_build_sites()
    matches = M.match(features, build_sites)
    hand = load_hand_verified()

    cache = {}
    counts = collections.Counter()
    report = []

    for i, f in enumerate(features):
        p = f['properties']
        b, rule, dist = matches[i]
        bdir = (b or {}).get('dir')

        roll = None
        if bdir:
            if bdir not in cache:
                cache[bdir] = read_site_rollup(bdir)
            roll = cache[bdir]

        # Hand-validated claims outrank the extractor and publish on their own. These sites are
        # precisely the ones the pipeline could not read, so waiting for it would bury them.
        hv = hand.get(bdir) if bdir else None
        if hv:
            roll = roll or {'verified': [], 'waste': [], 'withheld': {}, 'n_rows': 0}
            hand_names = [e['chemical'] for e in hv['chemicals']]
            superseded = {u for u, rx in SUPERSEDED_BY_SPECIFIC.items()
                          if any(rx.search(n) for n in hand_names)}
            roll['verified'] = [e for e in roll['verified'] if e['chemical'] not in superseded]
            have = {e['chemical'].lower() for e in roll['verified']}
            for name in hand_names:
                if name.lower() in have:
                    continue
                roll['verified'].append({
                    'chemical': name,
                    'provenance': f"hand-validated against {hv['source_document']}",
                })
            p['chem_hand_verified'] = [e['chemical'] for e in hv['chemicals']]
            p['chem_hand_verified_source'] = hv['source_document']
        else:
            p['chem_hand_verified'] = []
            p['chem_hand_verified_source'] = None

        if roll and roll['verified']:
            names = sorted({e['chemical'] for e in roll['verified']}, key=str.lower)
            prov = {}
            for e in roll['verified']:
                prov.setdefault(e['chemical'], e['provenance'])
            status = 'verified'
            p['chemicals'] = ' | '.join(names)
            p['chem_verified'] = names
            p['chem_provenance'] = [prov[n] for n in names]
            p['chem_note'] = ''
            p['chems'] = [n for n, rx in CHEM_RX if any(rx.search(x) for x in names)]
            p['chem_waste'] = sorted({e['chemical'] for e in roll['waste']}, key=str.lower)
        else:
            status = 'ocr_constrained' if (roll and roll['n_rows']) else 'in_process'
            p['chemicals'] = ''
            p['chem_verified'] = []
            p['chem_provenance'] = []
            p['chem_note'] = NOTE_OCR if status == 'ocr_constrained' else NOTE_PENDING
            p['chems'] = []
            p['chem_waste'] = []

        p['chem_status'] = status
        p['chem_withheld'] = (roll or {}).get('withheld', {})
        counts[status] += 1

        report.append({
            'map_site_name': p.get('site_name'),
            'program_number': p.get('program_number') or '',
            'status': status,
            'n_verified_chemicals': len(p['chem_verified']),
            'n_withheld_rows': sum(p['chem_withheld'].values()),
            'ocr_pending_rows': p['chem_withheld'].get('OCR_PENDING', 0),
            'n_hand_verified': len(p['chem_hand_verified']),
            'matched_build_dir': bdir or '',
            'match_rule': rule,
        })

    with open(args.geojson, 'w', encoding='utf-8') as fh:
        json.dump({'type': 'FeatureCollection', 'features': features}, fh,
                  separators=(',', ':'), ensure_ascii=False)

    os.makedirs(os.path.dirname(args.report), exist_ok=True)
    with open(args.report, 'w', newline='', encoding='utf-8-sig') as fh:
        w = csv.DictWriter(fh, fieldnames=list(report[0]))
        w.writeheader()
        w.writerows(report)

    total_claims = sum(len(f['properties']['chem_verified']) for f in features)
    distinct = {c for f in features for c in f['properties']['chem_verified']}
    print(f'{len(features)} mapped sites')
    print(f"  verified         {counts['verified']}")
    print(f"  ocr_constrained  {counts['ocr_constrained']}")
    print(f"  in_process       {counts['in_process']}")
    print(f'  verified chemical listings: {total_claims} across {len(distinct)} distinct chemicals')
    print(f'wrote {args.geojson}')
    print(f'wrote {args.report}')


if __name__ == '__main__':
    main()
