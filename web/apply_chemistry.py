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

SHIP_VERIFICATION = 'VERIFIED'
SHIP_DETECTION = 'DETECTED'

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


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--geojson', default=DEFAULT_GEOJSON)
    ap.add_argument('--report', default=DEFAULT_REPORT)
    args = ap.parse_args()

    doc = json.load(open(args.geojson, encoding='utf-8'))
    features = doc['features']

    build_sites = M.load_build_sites()
    matches = M.match(features, build_sites)

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
