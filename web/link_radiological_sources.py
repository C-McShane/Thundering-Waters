#!/usr/bin/env python3
r"""link_radiological_sources — put clickable source links on the radiological sites.

Two places feed the popup:
  csv/site_source_reports.json   per-site `reports` list + `docs_url`, surfaced as
                                 "Source reports — verify the data"
  master `website` column        surfaced as "View official record"

Every URL is the one cited in Niagara_Radiological_Sites_Investigation_Summary.html, so a reader
lands on the same record the site's claims were built from. Where a document was archived into
SOURCE the link still points at the agency's copy, not ours — the agency URL is the citation.

Usage:
  python link_radiological_sources.py --dry-run
  python link_radiological_sources.py
"""
from __future__ import annotations

import argparse
import csv
import io
import json
import os
import shutil
import time

REPORTS_JSON = r'C:\Users\mcsha\Niagra\csv\site_source_reports.json'
MASTER = r'C:\Users\mcsha\Niagra\csv\Niagara_Hazard_Sites_MASTER.csv'

DEC = 'https://extapps.dec.ny.gov/data/DecDocs/932118/'

ENTRIES = {
    '932118': {
        'website': DEC,
        'docs_url': DEC,
        'reports': [
            {'title': '2020 land-bank minutes (June) — the radiological statement of record',
             'url': 'https://www.niagaraorleanslandbank.com/documents/June%202020%20Meeting%20Minutes.pdf'},
            {'title': '2020 land-bank minutes (August) — Phase II result discussion',
             'url': 'https://www.niagaraorleanslandbank.com/documents/Aug%202020%20Meeting%20Minutes.pdf'},
            {'title': '2008 Site Characterization Report (NYSDEC)',
             'url': DEC + 'Report.HW.932118.2008-06-01.Site_Characterization_Report.pdf'},
            {'title': '1991 Phase II Environmental Site Investigation (NYSDEC)',
             'url': DEC + 'Report.HW.932118.1991-04-01.Phase_II_EnvSiteInvestigation.pdf'},
        ],
    },
    'EPA-NYN000206699': {
        'website': 'https://cumulis.epa.gov/supercpad/CurSites/csitinfo.cfm?id=0206699',
        'docs_url': 'https://www.epa.gov/ny/niagara-county-radiation-removal-sites',
        'reports': [
            {'title': 'EPA July 2020 removal completion fact sheet',
             'url': 'https://www.epa.gov/sites/default/files/2020-07/documents/'
                    'niagara_falls_blvd_rad_fact_sheet_july_2020_final.pdf'},
            {'title': '2015 technical review with radionuclide tables',
             'url': 'https://www.philrutherford.com/consulting/investigative_post/NY_Contaminated_Sites.pdf'},
        ],
    },
    'EPA-NYN000206697': {
        'website': 'https://cumulis.epa.gov/supercpad/CurSites/csitinfo.cfm?id=0206697',
        'docs_url': 'https://www.epa.gov/ny/niagara-county-radiation-removal-sites',
        'reports': [
            {'title': '2015 technical review with radionuclide tables',
             'url': 'https://www.philrutherford.com/consulting/investigative_post/NY_Contaminated_Sites.pdf'},
        ],
    },
    'EPA-NYN000203537': {
        'website': 'https://cumulis.epa.gov/supercpad/CurSites/csitinfo.cfm?id=0203537',
        'docs_url': 'https://cumulis.epa.gov/supercpad/CurSites/cadminrecord.cfm?id=0203537',
        'reports': [
            {'title': 'EPA action memorandum, 15 July 2021 — isotope results (SEMS 624954)',
             'url': 'https://semspub.epa.gov/src/document/02/624954'},
        ],
    },
    'EPA-NYN000206698': {
        'website': 'https://cumulis.epa.gov/supercpad/CurSites/csitinfo.cfm?id=0206698',
        'docs_url': 'https://cumulis.epa.gov/supercpad/CurSites/cadminrecord.cfm?id=0206698',
        'reports': [
            {'title': 'EPA action memorandum, 1 October 2020 (SEMS 615821)',
             'url': 'https://semspub.epa.gov/src/document/02/615821'},
            {'title': 'EPA April 2016 community fact sheet',
             'url': 'https://www.epa.gov/sites/default/files/2018-08/documents/'
                    'holy_trinity_cemetary_formatted_fact_sheet.pdf'},
            {'title': '2015 technical review with radionuclide tables',
             'url': 'https://www.philrutherford.com/consulting/investigative_post/NY_Contaminated_Sites.pdf'},
        ],
    },
    'EPA-NYN000204317': {
        'website': 'https://cumulis.epa.gov/supercpad/CurSites/csitinfo.cfm?id=0204317',
        'docs_url': 'https://www.epa.gov/ny/donovan-head-start-removal-site',
        'reports': [
            {'title': 'EPA June 2023 community update (SEMS 677170)',
             'url': 'https://semspub.epa.gov/src/document/02/677170'},
            {'title': 'EPA contaminant record — Uranium-238 in soil',
             'url': 'https://cumulis.epa.gov/supercpad/CurSites/ccontinfo.cfm?id=0204317'},
        ],
    },
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--dry-run', action='store_true')
    args = ap.parse_args()

    data = json.load(io.open(REPORTS_JSON, encoding='utf-8'))
    for pn, e in ENTRIES.items():
        data[pn] = {'reports': e['reports'], 'docs_url': e['docs_url']}
        print(f'  {pn:<20} {len(e["reports"])} report link(s) + document index')

    rows = list(csv.DictReader(io.open(MASTER, encoding='utf-8-sig')))
    fields = list(rows[0])
    n_web = 0
    for r in rows:
        pn = (r.get('program_number') or '').strip()
        if pn in ENTRIES and not (r.get('website') or '').strip():
            r['website'] = ENTRIES[pn]['website']
            r['cite'] = r['cite'] or ENTRIES[pn]['website']
            n_web += 1
    print(f'  master `website` set on {n_web} rows')

    if args.dry_run:
        print('\n(dry run) nothing written')
        return

    shutil.copy2(REPORTS_JSON, REPORTS_JSON + f'.bak-{time.strftime("%Y%m%dT%H%M%S")}')
    with io.open(REPORTS_JSON, 'w', encoding='utf-8') as fh:
        json.dump(data, fh, indent=1, ensure_ascii=False)
    shutil.copy2(MASTER, MASTER + f'.bak-{time.strftime("%Y%m%dT%H%M%S")}')
    with io.open(MASTER, 'w', encoding='utf-8-sig', newline='') as fh:
        w = csv.DictWriter(fh, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)
    print(f'\nwrote {os.path.basename(REPORTS_JSON)} and master (both backed up)')


if __name__ == '__main__':
    main()
