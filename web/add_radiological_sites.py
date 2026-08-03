#!/usr/bin/env python3
r"""add_radiological_sites — add the 2026-08-03 radiological investigation sites to the master.

Source: E:\Thundering_Waters_Backup_2026-07-20\Niagara_Radiological_Sites_Investigation_Summary.html

Five site groups. Four carry EPA identifiers and action-memorandum isotope data; Witmer Road
Drive-In is graded UNRESOLVED in that document (2020 land-bank meeting minutes only) but is
already in the master as NYSDEC 932118, so it needs a radiological tag rather than a new row.
Caitlin's call 2026-08-03: include all of them — the Witmer evidence exists but sits behind a
pending FOIA request.

The Upper Mountain Road cluster is TWO rows, not one: 738 and 789 carry distinct EPA IDs and had
separate removals. They are linked by `base_num` so the cluster stays relationally intact.

Coordinates: US Census geocoder (Nominatim fallback for the Niagara Falls Boulevard parcels,
which Census could not match), all verified inside the Niagara County bounding box.

Adding a site touches THREE artifacts and NOTHING syncs them — this script does the master CSV
only. The GeoPackage feature and the radiological tag are separate steps.

Usage:
  python add_radiological_sites.py --dry-run
  python add_radiological_sites.py
"""
from __future__ import annotations

import argparse
import csv
import io
import os
import shutil
import time

MASTER = r'C:\Users\mcsha\Niagra\csv\Niagara_Hazard_Sites_MASTER.csv'
SRC_DOC = 'Niagara_Radiological_Sites_Investigation_Summary.html (2026-08-03)'

COMMON = {
    'master_source': 'radiological_investigation_2026-08-03',
    'program_label': 'EPA CERCLA (Non-NPL) — Radiological',
    'program_type': 'CERCLA',
    'program_category': 'CERCLA',
    'designation': 'Federal CERCLA (Non-NPL)',
    'npl_status': 'Not on NPL',
    'epa_region': '2.0',
    'county': 'Niagara',
    'fuds_flag': 'False',
    'in_dataset': 'YES',
    'section': '6 - ADDED FROM radiological investigation summary',
    'data_source': 'EPA SEMS/CERCLA action memoranda and fact sheets; ' + SRC_DOC,
    'area_source': 'unavailable',
}

SITES = [
    {
        'program_number': 'EPA-NYN000206699',
        'site_name': 'Niagara Falls Boulevard Radiological Site',
        'epa_id_number_raw': 'NYN000206699',
        'address': '9512, 9524, 9540 and 9626 Niagara Falls Boulevard',
        'city': 'Niagara Falls', 'zip': '14304',
        'latitude': '43.096381', 'longitude': '-78.952432',
        'coord_flag': 'Centroid of the four geocoded parcels (Nominatim, 2026-08-03)',
        'non_npl_status': 'No Further Remedial Action Planned (non-NPL); removal completed 2021',
        'area_acres_best': '4.7',
        'acreage_note': '1.4-acre woodland plus 3.3-acre parking-lot area (EPA completion fact sheet)',
        'contaminants': 'Uranium-238 + daughters; Thorium-232 + daughters; Radium-226 + daughters',
        'waste_name': 'Low-level radioactive material in soil and fill',
        'narrative': ('EPA CERCLA removal site. Assessment data 2013-2015 report Uranium-238 max '
                      '196 pCi/g (avg 39.0), Thorium-232 max 541 pCi/g (avg 44.0) and Radium-226 '
                      'max 199 pCi/g (avg 43.8). Approximately 28,362 tons of low-level '
                      'radioactive material were excavated across a 1.4-acre woodland and a '
                      '3.3-acre parking-lot area; the site was backfilled, paved and restored, '
                      'with the removal completed in 2021.'),
        'review_notes': 'Added 2026-08-03. Radiological evidence grade CONFIRMED (EPA removal + isotope data).',
    },
    {
        'program_number': 'EPA-NYN000206697',
        'site_name': '738 Upper Mountain Road',
        'epa_id_number_raw': 'NYN000206697',
        'address': '738 Upper Mountain Road', 'city': 'Lewiston', 'zip': '14092',
        'latitude': '43.155630', 'longitude': '-79.021943',
        'coord_flag': 'US Census geocoder 2026-08-03 (738 UPPER MOUNTAIN RD, LEWISTON NY 14092)',
        'non_npl_status': 'No Further Remedial Action Planned (non-NPL); removal completed 2020',
        'base_num': 'EPA-UMR-CLUSTER', 'is_multi_ou': '1',
        'contaminants': 'Uranium-238 + daughters; Thorium-232 + daughters; Radium-226 + daughters',
        'waste_name': 'Radiologically contaminated soil and gravel',
        'narrative': ('EPA CERCLA removal site in the Upper Mountain Road cluster. Assessment data '
                      '2013-2014 report Uranium-238 max 26.7 pCi/g (avg 5.84), Thorium-232 max 116 '
                      'pCi/g (avg 21.4) and Radium-226 max 32.6 pCi/g (avg 8.15). Contamination '
                      'covered a culvert crossing and portions of the gravel driveway and access '
                      'road; material was removed and clean-backfilled, completed 2020. Final '
                      'disposal manifests and confirmation survey reports are not public.'),
        'review_notes': 'Added 2026-08-03. Radiological evidence grade CONFIRMED. Tonnage not publicly stated.',
    },
    {
        'program_number': 'EPA-NYN000203537',
        'site_name': '789 Upper Mountain Road',
        'epa_id_number_raw': 'NYN000203537',
        'address': '789 Upper Mountain Road and adjacent residence',
        'city': 'Lewiston', 'zip': '14092',
        'latitude': '43.156158', 'longitude': '-79.018352',
        'coord_flag': 'US Census geocoder 2026-08-03 (789 UPPER MOUNTAIN RD, LEWISTON NY 14092)',
        'non_npl_status': 'Removal action; residents temporarily relocated',
        'base_num': 'EPA-UMR-CLUSTER', 'is_multi_ou': '1',
        'contaminants': ('Thorium-232; Radium-228; Actinium-228; Bismuth-212; Lead-212; '
                         'Thallium-208; Radium-226; Uranium-238; Uranium-233/234; Thorium-234; radon'),
        'waste_name': 'Radiologically contaminated soil beneath basement/crawlspace and yard',
        'narrative': ('EPA CERCLA removal site, Upper Mountain Road cluster. The EPA 2021 action '
                      'memorandum reports crawlspace soil results of Thorium-232 up to 1,430 pCi/g, '
                      'Bismuth-212 519, Actinium-228 and Radium-228 518, Lead-212 502, Thallium-208 '
                      '184, Radium-226 107, Uranium-238 70.5, Uranium-233/234 70 and Thorium-234 '
                      '19.8 pCi/g, with crawlspace gamma exposure above 500 microroentgen/hour '
                      'measured in October 2019. About 2,000 cubic metres of contaminated material '
                      'were estimated; residents were temporarily relocated for excavation and '
                      'restoration.'),
        'review_notes': ('Added 2026-08-03. Radiological evidence grade CONFIRMED - PRIMARY (EPA action '
                         'memorandum). Volume is an action-memo ESTIMATE; do not report as final tonnage.'),
    },
    {
        'program_number': 'EPA-NYN000206698',
        'site_name': 'Holy Trinity Cemetery and Adjacent Residences',
        'epa_id_number_raw': 'NYN000206698',
        'address': '5401 Robert Avenue (cemetery); 5380 and 5382 Roberts Avenue (residences)',
        'city': 'Lewiston', 'zip': '14092',
        'latitude': '43.148840', 'longitude': '-79.032484',
        'coord_flag': 'US Census geocoder 2026-08-03 (5401 ROBERT AVE, LEWISTON NY 14092)',
        'non_npl_status': 'No Further Remedial Action Planned (non-NPL); residential removals completed',
        'contaminants': 'Uranium-238 + daughters; Thorium-232 + daughters; Radium-226 + daughters',
        'waste_name': 'Radiologically contaminated soil and fill',
        'narrative': ('EPA CERCLA removal site. Cemetery-property assessment data from 2013 report '
                      'Uranium-238 max 287 pCi/g (avg 37.8), Thorium-232 max 358 pCi/g (avg 61.3) '
                      'and Radium-226 max 360 pCi/g (avg 41.0). A 2016-2017 residential assessment '
                      'gave a Radium-226 exposure-point concentration of 85.8 pCi/g at Area 6. '
                      'Garage/driveway and driveway/patio removals were carried out at the adjacent '
                      'residences and the areas restored; the residual-material status of the '
                      'cemetery property itself is not established in the public record.'),
        'review_notes': ('Added 2026-08-03. Radiological evidence grade CONFIRMED. Cemetery residual '
                         'status is a documented GAP - quantities are planning ESTIMATES (about 99 cubic yards).'),
    },
    {
        'program_number': 'EPA-NYN000204317',
        'site_name': 'Donovan Head Start Property',
        'epa_id_number_raw': 'NYN000204317',
        'address': '1631 Main Street (playground and rear parking lot)',
        'city': 'Niagara Falls', 'zip': '14305',
        'latitude': '43.103932', 'longitude': '-79.052526',
        'coord_flag': 'US Census geocoder 2026-08-03 (1631 MAIN ST, NIAGARA FALLS NY 14305)',
        'non_npl_status': 'CERCLA Removal Only Site; owner-led removal under EPA oversight',
        'acreage_note': 'About 10,000 square feet of affected area (EPA site page)',
        'contaminants': 'Uranium-238 in industrial slag/fill',
        'waste_name': 'Uranium-bearing industrial slag and fill',
        'narrative': ('EPA CERCLA Removal Only site. EPA identifies Uranium-238 as the soil '
                      'contaminant of concern, present in industrial slag and fill 6 to 24 inches '
                      'below the surface over roughly 10,000 square feet of the playground and rear '
                      'parking lot. The removal was carried out by the Community Development '
                      'Institute under EPA oversight, with the parking lot and walkways restored. '
                      'No tonnage, volume or disposal destination has been published.'),
        'review_notes': ('Added 2026-08-03. Radiological evidence grade CONFIRMED. Quantities and final '
                         'status survey are a documented GAP. Property serves a Head Start facility.'),
    },
]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--master', default=MASTER)
    ap.add_argument('--dry-run', action='store_true')
    args = ap.parse_args()

    with io.open(args.master, encoding='utf-8-sig', newline='') as fh:
        reader = csv.DictReader(fh)
        fields = reader.fieldnames
        rows = list(reader)
    existing = {(r.get('program_number') or '').strip() for r in rows}
    print(f'master: {len(rows)} rows, {len(fields)} columns')

    new = []
    for spec in SITES:
        pn = spec['program_number']
        if pn in existing:
            print(f'  SKIP {pn} — already present')
            continue
        row = {k: '' for k in fields}
        row.update({k: v for k, v in COMMON.items() if k in row})
        for k, v in spec.items():
            if k in row:
                row[k] = v
            else:
                print(f'  WARNING column not in master, dropped: {k}')
        # The master carries two source vintages; populate both so either read path works.
        row['address1'] = row['address1'] or spec.get('address', '')
        row['locality'] = row['locality'] or spec.get('city', '')
        row['zipcode'] = row['zipcode'] or spec.get('zip', '')
        row['program_facility_name'] = row['program_facility_name'] or spec.get('site_name', '')
        row['site_name_clean'] = row['site_name_clean'] or spec.get('site_name', '')
        row['base_num'] = row['base_num'] or pn
        new.append(row)
        print(f'  ADD  {pn:<20} {spec["site_name"][:46]:<46} {spec["latitude"]}, {spec["longitude"]}')

    if not new:
        print('nothing to add')
        return
    if args.dry_run:
        print(f'\n(dry run) would append {len(new)} rows')
        return

    backup = args.master + f'.bak-{time.strftime("%Y%m%dT%H%M%S")}'
    shutil.copy2(args.master, backup)
    print(f'\nbackup: {os.path.basename(backup)}')
    with io.open(args.master, 'w', encoding='utf-8-sig', newline='') as fh:
        w = csv.DictWriter(fh, fieldnames=fields)
        w.writeheader()
        w.writerows(rows + new)
    print(f'wrote {len(rows) + len(new)} rows to {args.master}')


if __name__ == '__main__':
    main()
