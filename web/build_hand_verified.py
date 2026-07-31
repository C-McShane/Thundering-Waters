#!/usr/bin/env python3
r"""build_hand_verified — turn Caitlin's hand-validation workbooks into csv/hand_verified_chemicals.json.

Hand validation is a STRONGER provenance than the extraction pipeline, not a weaker one: a
person read the source document and confirmed the chemical. These claims therefore publish even
where the pipeline's own rows for the same site are stuck at OCR_PENDING — which is the whole
point, since the sites being hand-validated are the ones the extractor could not read.

Each source workbook lists chemicals under category headings that sit inline in the same column
as the chemicals themselves (VOCs / SVOCs / PCBs / Pesticides / Metals / Other), so headings are
recognised by name and used to tag the rows that follow rather than being emitted as chemicals.

Usage:  python build_hand_verified.py
"""
from __future__ import annotations

import json
import os
import re

import pandas as pd

CSV_DIR = r'C:\Users\mcsha\Niagra\csv'
OUT = os.path.join(CSV_DIR, 'hand_verified_chemicals.json')

# Headings that appear as values inside the chemical column.
HEADINGS = {
    'vocs': 'VOC', 'svocs': 'SVOC', 'svocs and other organics': 'SVOC',
    'pcbs': 'PCB', 'pesticides and herbicides': 'Pesticide/herbicide',
    'pesticides, herbicides and pcbs': 'Pesticide/herbicide/PCB',
    'metals': 'Metal', 'metals and metalloids': 'Metal', 'other': 'Other',
}


def _clean_heading(s):
    # "Metals and metalloids — 13" / "VOCs — 7": strip the trailing count.
    return re.sub(r'\s*[—–-]\s*\d+\s*$', '', str(s)).strip()


def read_workbook(path):
    """[(chemical, category)] from a two-column hand-validation workbook."""
    df = pd.read_excel(path)
    header_cat = HEADINGS.get(_clean_heading(df.columns[-1]).lower())
    col = df.columns[-1]

    out, cat = [], header_cat
    for raw in df[col]:
        if pd.isna(raw):
            continue
        text = str(raw).strip()
        if not text:
            continue
        maybe = HEADINGS.get(_clean_heading(text).lower())
        if maybe:
            cat = maybe
            continue
        # A cell may hold one chemical or a semicolon-separated run of them.
        for part in text.split(';'):
            name = part.strip().rstrip('.').strip()
            if name:
                out.append((name, cat))
    return out


# 64th Street North was hand-validated in the notes column of csv/rad_candidates_REVIEW.csv
# rather than in a workbook. Transcribed here with the obvious slips corrected — each one is
# listed so the change from what was written is auditable rather than silent:
#   "Flouranthene"           -> Fluoranthene
#   "Napthalene"             -> Naphthalene
#   "arsnic"                 -> Arsenic          (also ran together as "cobalt arsnic")
#   "H-Nitrosodiphenylamine" -> N-Nitrosodiphenylamine
#   "methylene, chloride"    -> Methylene chloride  (one analyte split by the comma)
#   "1,1,1 Trichloroethane"  -> 1,1,1-Trichloroethane
#   "lead" listed twice; lower-case metals title-cased.
# DDT and DDE are kept exactly as written — the isomer prefix (4,4'-) was not stated and is
# not ours to add.
SIXTY_FOURTH_NORTH = [
    ('Iron', 'Metal'), ('Mercury', 'Metal'), ('Cadmium', 'Metal'), ('Lead', 'Metal'),
    ('Thallium', 'Metal'), ('Vanadium', 'Metal'), ('Copper', 'Metal'), ('Cobalt', 'Metal'),
    ('Arsenic', 'Metal'), ('Barium', 'Metal'),
    ('Benzo(a)pyrene', 'SVOC'), ('Benzo(b)fluoranthene', 'SVOC'), ('Fluoranthene', 'SVOC'),
    ('Phenanthrene', 'SVOC'), ('Chrysene', 'SVOC'), ('Indeno(1,2,3-cd)pyrene', 'SVOC'),
    ('Naphthalene', 'SVOC'), ('N-Nitrosodiphenylamine', 'SVOC'),
    ('Methylene chloride', 'VOC'), ('Toluene', 'VOC'), ('1,1,1-Trichloroethane', 'VOC'),
    ('Benzene', 'VOC'),
    ('DDT', 'Pesticide/herbicide'), ('DDE', 'Pesticide/herbicide'),
]

SOURCES = [
    {
        'build_dir': 'Fashion-Outlets-of-Niagara-Falls-Expansion__C932162',
        'program_number': 'C932162',
        'site_name': 'Fashion Outlets of Niagara Falls Expansion',
        'workbook': 'Fashion_Outlet_Chemicals.xlsx',
        'document': 'Report.BCP.C932162.2014-11-15.FinalFER-AppendicesA-F',
        # Verified from the rad_candidates review: the full decay-series suite, hand-confirmed.
        'radionuclides': ['Radium / Radon', 'Thorium', 'Uranium', 'Actinium-228', 'Bismuth-212',
                          'Bismuth-214', 'Lead-212', 'Lead-214', 'Potassium-40', 'Thallium-208'],
    },
    {
        'build_dir': 'Kozdranski-Property__932117',
        'program_number': '932117',
        'site_name': 'Kozdranski Property',
        'workbook': 'Kozdranksi_Property.xlsx',   # filename misspelling is Caitlin's; kept as-is
        'document': 'Work_Plan.HW.932117.2005-01-01.Site_Characterization_Workplan',
        # Reviewed and NOT verified — this site stays off the radiation cross-list.
        'radionuclides': [],
    },
    {
        'build_dir': '64th-Street-North__932085A',
        'program_number': '932085A',
        'site_name': '64th Street North Site',
        'inline': SIXTY_FOURTH_NORTH,
        'document': 'Report.HW.932085A.1992-01-01.RemedialActionSiteInvestigation',
        # Reviewed and NOT verified — stays off the radiation cross-list.
        'radionuclides': [],
    },
]


def main():
    sites = {}
    for spec in SOURCES:
        if spec.get('inline'):
            pairs = list(spec['inline'])
        else:
            pairs = read_workbook(os.path.join(CSV_DIR, spec['workbook']))
        seen, chems = set(), []
        for name, cat in pairs:
            key = re.sub(r'[^a-z0-9]', '', name.lower())
            if key in seen:
                continue
            seen.add(key)
            chems.append({'chemical': name, 'category': cat})
        # Keyed by BUILD DIRECTORY, not program number. "64th Street North Site" carries a
        # program_number of `nan` while its twin feature "64th Street - North" carries 932085A;
        # keying on the number would reach only one of the two markers for the same place.
        sites[spec['build_dir']] = {
            'site_name': spec['site_name'],
            'program_number': spec['program_number'],
            'source_workbook': spec.get('workbook', '(inline — rad_candidates_REVIEW.csv notes)'),
            'source_document': spec['document'],
            'verified_by': 'hand validation',
            'verified_date': '2026-07-31',
            'chemicals': chems,
            'radionuclides': spec['radionuclides'],
        }
        print(f"{spec['build_dir'][:42]:<42} {len(chems):>3} chemicals, "
              f"{len(spec['radionuclides'])} radionuclides")

    payload = {
        '_meta': {
            'note': 'Hand-validated chemical detections. A person read the source document and '
                    'confirmed each entry; these publish even where the extraction pipeline is '
                    'blocked on OCR for the same site.',
            'generated_from': 'web/build_hand_verified.py',
        },
        'sites': sites,
    }
    with open(OUT, 'w', encoding='utf-8') as fh:
        json.dump(payload, fh, indent=1, ensure_ascii=False)
    print(f'wrote {OUT}')


if __name__ == '__main__':
    main()
