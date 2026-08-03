#!/usr/bin/env python3
r"""fetch_radiological_docs — download the source documents cited in the radiological summary.

Every URL comes from Niagara_Radiological_Sites_Investigation_Summary.html (2026-08-03). Only
direct document downloads are taken; the cumulis.epa.gov and epa.gov landing pages are indexes
rather than records and are recorded in the manifest instead.

Documents land in `SOURCE/<site-key>/` so the wells and chemistry modules pick them up on their
next pass. A few sources cover several sites (the 2015 technical review tabulates radionuclides
for three of them) and are written into each site they support, since the modules read per-site
directories.

Skips anything already downloaded, verifies each file really is a PDF before keeping it, and
writes a manifest recording url, destination, size and status.

Usage:
  python fetch_radiological_docs.py --dry-run
  python fetch_radiological_docs.py
"""
from __future__ import annotations

import argparse
import csv
import os
import time
import urllib.error
import urllib.request

SOURCE_ROOT = r'E:\Thundering_Waters_Backup_2026-07-20\SOURCE'
UA = 'Mozilla/5.0 (research archival; Thundering Waters project)'

WITMER = 'Witmer-Road-Drive-In__932118'
NFBLVD = 'Niagara-Falls-Boulevard-Radiological-Site__EPA-NYN000206699'
UMR738 = '738-Upper-Mountain-Road__EPA-NYN000206697'
UMR789 = '789-Upper-Mountain-Road__EPA-NYN000203537'
HOLYTR = 'Holy-Trinity-Cemetery-and-Adjacent-Residences__EPA-NYN000206698'
DONOVN = 'Donovan-Head-Start-Property__EPA-NYN000204317'

# (url, [site keys], filename)
DOCS = [
    # --- Witmer Road Drive-In, NYSDEC 932118 -------------------------------
    ('https://extapps.dec.ny.gov/data/DecDocs/932118/Report.HW.932118.1989-08-01.EnvironmentalSiteAssessment.pdf',
     [WITMER], 'Report.HW.932118.1989-08-01.EnvironmentalSiteAssessment.pdf'),
    ('https://extapps.dec.ny.gov/data/DecDocs/932118/Report.HW.932118.1990-06-01.LabDataPackage.pdf',
     [WITMER], 'Report.HW.932118.1990-06-01.LabDataPackage.pdf'),
    ('https://extapps.dec.ny.gov/data/DecDocs/932118/Report.HW.932118.1991-04-01.Phase_II_EnvSiteInvestigation.pdf',
     [WITMER], 'Report.HW.932118.1991-04-01.Phase_II_EnvSiteInvestigation.pdf'),
    ('https://extapps.dec.ny.gov/data/DecDocs/932118/Work%20Plan.HW.932118.2007-02-28.Technical%20Work%20Plan%20for%20Site%20Characterization.pdf',
     [WITMER], 'Work Plan.HW.932118.2007-02-28.Technical Work Plan for Site Characterization.pdf'),
    ('https://extapps.dec.ny.gov/data/DecDocs/932118/Report.HW.932118.2008-06-01.Site_Characterization_Report.pdf',
     [WITMER], 'Report.HW.932118.2008-06-01.Site_Characterization_Report.pdf'),
    # The land-bank minutes are the ONLY public source for the radiological claim at Witmer,
    # so they are the evidence of record until the FOIA'd Phase II is released.
    ('https://www.niagaraorleanslandbank.com/documents/June%202020%20Meeting%20Minutes.pdf',
     [WITMER], 'LandBank.932118.2020-06.June_2020_Meeting_Minutes.pdf'),
    ('https://www.niagaraorleanslandbank.com/documents/Aug%202020%20Meeting%20Minutes.pdf',
     [WITMER], 'LandBank.932118.2020-08.August_2020_Meeting_Minutes.pdf'),

    # --- Niagara Falls Boulevard ------------------------------------------
    ('https://www.epa.gov/sites/default/files/2020-07/documents/niagara_falls_blvd_rad_fact_sheet_july_2020_final.pdf',
     [NFBLVD], 'EPA.NYN000206699.2020-07.Completion_Fact_Sheet.pdf'),

    # --- 789 Upper Mountain Road: the primary evidence --------------------
    ('https://semspub.epa.gov/src/document/02/624954',
     [UMR789], 'EPA.NYN000203537.2021-07-15.Action_Memorandum_SEMS_624954.pdf'),

    # --- Holy Trinity Cemetery --------------------------------------------
    ('https://semspub.epa.gov/src/document/02/615821',
     [HOLYTR], 'EPA.NYN000206698.2020-10-01.Action_Memorandum_SEMS_615821.pdf'),
    ('https://www.epa.gov/sites/default/files/2018-08/documents/holy_trinity_cemetary_formatted_fact_sheet.pdf',
     [HOLYTR], 'EPA.NYN000206698.2016-04.Community_Fact_Sheet.pdf'),

    # --- Donovan Head Start -----------------------------------------------
    ('https://semspub.epa.gov/src/document/02/677170',
     [DONOVN], 'EPA.NYN000204317.2023-06.Community_Update_SEMS_677170.pdf'),

    # --- Multi-site: the 2015 review tabulates radionuclides for three sites
    ('https://www.philrutherford.com/consulting/investigative_post/NY_Contaminated_Sites.pdf',
     [NFBLVD, UMR738, HOLYTR], 'Technical_Review.2015.NY_Contaminated_Sites_radionuclide_tables.pdf'),

    # --- The FOIA log that documents the pending Witmer request ------------
    ('https://www.epa.gov/system/files/documents/2026-01/2024-3rd-quarter-foia-log.pdf',
     [WITMER], 'EPA.FY2024_Q3_FOIA_log.pdf'),
]

# Landing pages, not documents. Recorded so the trail is complete.
INDEX_PAGES = [
    ('https://extapps.dec.ny.gov/data/DecDocs/932118/', WITMER, 'NYSDEC document directory'),
    ('https://cumulis.epa.gov/supercpad/CurSites/csitinfo.cfm?id=0206699', NFBLVD, 'EPA CERCLA site profile'),
    ('https://www.epa.gov/ny/niagara-county-radiation-removal-sites', NFBLVD, 'EPA county radiation-removal summary'),
    ('https://cumulis.epa.gov/supercpad/CurSites/csitinfo.cfm?id=0206697', UMR738, 'EPA CERCLA site profile'),
    ('https://cumulis.epa.gov/supercpad/CurSites/csitinfo.cfm?id=0203537', UMR789, 'EPA CERCLA site profile'),
    ('https://cumulis.epa.gov/supercpad/CurSites/cadminrecord.cfm?id=0203537', UMR789, 'EPA administrative-record index'),
    ('https://cumulis.epa.gov/supercpad/CurSites/csitinfo.cfm?id=0202808', UMR789, 'Legacy PASNY-Upper Mountain profile'),
    ('https://cumulis.epa.gov/supercpad/CurSites/csitinfo.cfm?id=0206698', HOLYTR, 'EPA CERCLA site profile'),
    ('https://cumulis.epa.gov/supercpad/CurSites/cadminrecord.cfm?id=0206698', HOLYTR, 'EPA administrative-record index'),
    ('https://www.epa.gov/ny/donovan-head-start-removal-site', DONOVN, 'EPA project page'),
    ('https://cumulis.epa.gov/supercpad/CurSites/csitinfo.cfm?id=0204317', DONOVN, 'EPA CERCLA site profile'),
    ('https://cumulis.epa.gov/supercpad/CurSites/ccontinfo.cfm?id=0204317', DONOVN, 'EPA contaminant page (soil U-238)'),
]


def fetch(url, dest, timeout=90):
    req = urllib.request.Request(url, headers={'User-Agent': UA})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        data = r.read()
    if not data[:5].startswith(b'%PDF'):
        return None, f'not a PDF (starts {data[:12]!r})'
    with open(dest, 'wb') as fh:
        fh.write(data)
    return len(data), 'ok'


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--source-root', default=SOURCE_ROOT)
    ap.add_argument('--dry-run', action='store_true')
    args = ap.parse_args()

    manifest = []
    for url, sites, fname in DOCS:
        primary = os.path.join(args.source_root, sites[0], fname)
        if args.dry_run:
            print(f'  would fetch {fname[:64]:<64} -> {", ".join(sites)}')
            continue
        os.makedirs(os.path.dirname(primary), exist_ok=True)
        if os.path.isfile(primary) and os.path.getsize(primary) > 1024:
            size, status = os.path.getsize(primary), 'already present'
        else:
            try:
                size, status = fetch(url, primary)
            except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, OSError) as e:
                size, status = None, f'FAILED {type(e).__name__}: {e}'
            time.sleep(1.5)
        print(f'  {status:<26} {size or 0:>9,} B  {fname[:56]}')
        manifest.append({'url': url, 'site': sites[0], 'file': fname,
                         'bytes': size or '', 'status': status})
        # copy into the other sites this document supports
        if size and status != 'already present':
            for extra in sites[1:]:
                d = os.path.join(args.source_root, extra, fname)
                os.makedirs(os.path.dirname(d), exist_ok=True)
                if not os.path.isfile(d):
                    with open(primary, 'rb') as a, open(d, 'wb') as b:
                        b.write(a.read())
                    manifest.append({'url': url, 'site': extra, 'file': fname,
                                     'bytes': size, 'status': 'copied (multi-site source)'})

    for url, site, what in INDEX_PAGES:
        manifest.append({'url': url, 'site': site, 'file': '', 'bytes': '',
                         'status': f'index page not downloaded — {what}'})

    if args.dry_run:
        print(f'\n(dry run) {len(DOCS)} documents, {len(INDEX_PAGES)} index pages recorded')
        return

    mpath = os.path.join(args.source_root, '_radiological_docs_manifest.csv')
    with open(mpath, 'w', newline='', encoding='utf-8-sig') as fh:
        w = csv.DictWriter(fh, fieldnames=['url', 'site', 'file', 'bytes', 'status'])
        w.writeheader()
        w.writerows(manifest)
    ok = sum(1 for m in manifest if m['status'] in ('ok', 'already present')
             or m['status'].startswith('copied'))
    print(f'\n{ok} files in place; manifest -> {mpath}')


if __name__ == '__main__':
    main()
