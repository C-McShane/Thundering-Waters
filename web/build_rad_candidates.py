#!/usr/bin/env python3
r"""build_rad_candidates — worksheet of radionuclide claims that did NOT reach the radiation tab.

One row per (site, radionuclide) claim the chemistry pipeline found but could not verify, so
each row is a single checkable statement rather than a whole site. Sites already on the
radiation cross-list are excluded — those are settled.

`tag` is why the claim failed, and it decides how much a row is worth:
  ocr pending    the page is a scan awaiting OCR validation — the strongest leads
  unresolved     a value exists but could not be tied to a detection
  named only     the radionuclide is named in a document with no result attached
  not detected   tested for and clean — a finding, not a gap

Caitlin fills `verified_YN` (Y = a real detection at this site / N = not) and `notes`.

Usage:  python build_rad_candidates.py [--out <path>]
"""
from __future__ import annotations

import argparse
import csv
import glob
import json
import os

import chem_site_match as M
import rad_classify as R

DEFAULT_OUT = r'C:\Users\mcsha\Niagra\csv\rad_candidates_REVIEW.csv'

TAGS = {
    'OCR_PENDING':  'ocr pending',
    'UNRESOLVED':   'unresolved',
    'NAMED_ONLY':   'named only',
    'NOT_DETECTED': 'not detected',
}
TAG_ORDER = ['ocr pending', 'unresolved', 'named only', 'not detected', 'not extracted']

# Problems already spotted, surfaced on the row they affect so they are seen at review time.
FLAGS = {
    ('C932172', '*'): ('MISATTRIBUTED SOURCE — the only radionuclide evidence for this site comes '
                       'from NFSS_EnvSurveillance_2020.pdf, a Niagara Falls Storage Site document '
                       'misfiled into SOURCE/Niacet-Site__C932172. It is not Niacet data.'),
}

# A site the four tags cannot express, but which belongs in this review: the pipeline extracted
# NO radionuclide rows at all, while its own document set is explicitly radiological. Leaving it
# out because it does not fit a tag is the same oversight that kept Frontier Chemical off the map.
EXTRA_ROWS = [{
    'site_name': 'Niacet Corporation',
    'also_mapped_as': '',
    'program_number': 'V00373',
    'radionuclide': '(none extracted)',
    'tag': 'not extracted',
    'chemistry_status': 'verified',
    'source_document': 'Report.VCP.V00373.2012-08-27.Rad_Investigation_Report.pdf; '
                       'Report.VCP.V00373.2013-01-30.Rad_Excav_Completion.pdf; '
                       'Work Plan.VCP.V00373.2014-07-31.Rad Work Plan Addenda.pdf',
    'n_rows_found': '0',
    'flag': 'RECALL FAILURE — three radiological reports in this site’s own document set '
            '(investigation, excavation completion, work plan addenda) yielded zero extracted '
            'radionuclide rows. Distinct site from Niacet Site C932172.',
    'verified_YN': '',
    'notes': '',
}]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', default=DEFAULT_OUT)
    args = ap.parse_args()

    features = json.load(open(M.GEO, encoding='utf-8'))['features']
    build_sites = M.load_build_sites()
    matches = M.match(features, build_sites)
    tagged = {i for i, f in enumerate(features) if f['properties'].get('rad_class')}

    # Collapse the duplicate map features that point at one built site.
    sites = {}
    for i, f in enumerate(features):
        if i in tagged:
            continue
        b = matches[i][0]
        bdir = (b or {}).get('dir')
        if not bdir:
            continue
        p = f['properties']
        s = sites.setdefault(bdir, {'names': set(), 'pn': '', 'chem': p.get('chem_status')})
        s['names'].add(p.get('site_name'))
        s['pn'] = s['pn'] or M.clean_pn(p.get('program_number'))

    rows = []
    for bdir, s in sites.items():
        for path in glob.glob(os.path.join(R.BUILD_CHEM, bdir, '*_detected_chemicals.csv')):
            for r in csv.DictReader(open(path, encoding='utf-8-sig')):
                chem = (r.get('chemical') or '').strip()
                if chem not in R.RADIOLOGICAL:
                    continue
                tag = TAGS.get((r.get('detection_status') or '').strip())
                if not tag:
                    continue
                names = sorted(s['names'], key=len)
                rows.append({
                    'site_name': names[-1],
                    'also_mapped_as': '; '.join(n for n in names if n != names[-1]),
                    'program_number': s['pn'],
                    'radionuclide': chem,
                    'tag': tag,
                    'chemistry_status': s['chem'],
                    'source_document': (r.get('example_provenance') or '').strip(),
                    'n_rows_found': r.get('n_unverified_rows') or r.get('n_verified_rows') or '',
                    'flag': FLAGS.get((s['pn'], chem)) or FLAGS.get((s['pn'], '*')) or '',
                    'verified_YN': '',
                    'notes': '',
                })

    rows.extend(EXTRA_ROWS)

    rows.sort(key=lambda x: (TAG_ORDER.index(x['tag']), x['site_name'], x['radionuclide']))

    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    with open(args.out, 'w', newline='', encoding='utf-8-sig') as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)

    n_sites = len({(r['site_name'], r['program_number']) for r in rows})
    print(f'wrote {args.out}')
    print(f'  {len(rows)} claims across {n_sites} sites')
    for t in TAG_ORDER:
        n = sum(1 for r in rows if r['tag'] == t)
        print(f'    {t:<14} {n}')


if __name__ == '__main__':
    main()
