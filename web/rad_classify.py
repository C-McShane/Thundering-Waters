#!/usr/bin/env python3
r"""rad_classify — decide which mapped sites belong on the radiation cross-list.

Membership used to be a hand-maintained dictionary, which is how Frontier Chemical Royal
Avenue (932110) stayed off the radiation tab while its own Final Engineering Report tabulated
Radium-226/228, Thorium-234, Uranium-235/238 in the soil. Membership is now the UNION of two
sources, and each site records which one put it there:

  derived   the chemistry pipeline VERIFIED a radionuclide detection against a table cell in
            that site's own documents. Self-maintaining: extract a radionuclide anywhere and
            the site appears on the radiation tab.
  agency    a named DOE / USACE / NYSDEC classification. These stay because an agency
            determination is stronger evidence than our extraction, and a site can be
            documented radioactive while our extractor finds nothing (no digitised tables,
            scans still behind OCR, or contamination recorded only in prose).

Union, not replacement: dropping an agency-classified FUSRAP site because the extractor came
up empty would be a regression, not a correction.

`rad_class` is the LABEL, and it is a separate question from membership. A site that is on the
list with no agency classification is **OTHER** — it holds radioactive material, but nothing in
our sources says which regulatory category it falls under.
"""
from __future__ import annotations

import csv
import glob
import json
import os
import re

import chem_site_match as M

BUILD_CHEM = M.BUILD_CHEM

# Curated chemical categories that are radiological, mapped to the isotope codes the map uses.
RADIOLOGICAL = {
    'Uranium': 'U',
    'Thorium': 'Th',
    'Radium / Radon': 'Ra',
}

# Hand validation reports specific isotopes rather than the pipeline's collapsed categories, so
# a decay-chain nuclide has to be resolved back to the parent series the map filters on.
ISOTOPE_SERIES = [
    (re.compile(r'^(uranium|u)[\s-]*\d', re.I), 'U'),
    (re.compile(r'^(thorium|th)[\s-]*\d', re.I), 'Th'),
    (re.compile(r'^(radium|ra)[\s-]*\d', re.I), 'Ra'),
    (re.compile(r'^protactinium', re.I), 'U'),      # Pa-231/234 — uranium series
    (re.compile(r'^actinium', re.I), 'Th'),         # Ac-228 — thorium series marker
    (re.compile(r'^(bismuth|lead|thallium|polonium|astatine|radon)', re.I), 'Ra'),
]

HAND_VERIFIED = r'C:\Users\mcsha\Niagra\csv\hand_verified_chemicals.json'


def isotope_code(name):
    """'Actinium-228' -> 'Th'; 'Uranium' -> 'U'; 'Potassium-40' -> None (not a decay series)."""
    if name in RADIOLOGICAL:
        return RADIOLOGICAL[name]
    for rx, code in ISOTOPE_SERIES:
        if rx.match(name.strip()):
            return code
    return None


def load_hand_verified():
    try:
        return json.load(open(HAND_VERIFIED, encoding='utf-8'))['sites']
    except (OSError, KeyError, ValueError):
        return {}

CLASS_OTHER = 'OTHER'

# Agency classifications. Each is a determination by DOE Legacy Management, USACE (FUSRAP) or
# NYSDEC, cited in the site's own record — NOT an inference of ours. Keyed by program number,
# with a name fallback for the sites that never received one.
#   value: (rad_class, [isotopes], basis)

# 3125 Highland Avenue / Tulip Molded Plastics. Held in a variable because the P-site (932169)
# and the BCP site (C932169) are the SAME PROPERTY under two program numbers, 24 m apart on the
# map — tagging one and not the other would put a radioactive pin beside a clean one.
_RAD_TULIP = ('TENORM', [],
              'TENORM — GAMMA SCREENING, NOT YET CONFIRMED BY LABORATORY. NYSDEC-approved '
              'Remedial Investigation Work Plan (Mar 2026) required a screening survey under '
              'DMM-5, "Management of Soils Contaminated with Technically Enhanced Naturally '
              'Occurring Radioactive Materials". MJW GPS gamma walkover (Ludlum 3000 / 44-10 '
              'NaI), 30 April - 1 May 2026, Phase 1 outdoor areas only: 12,136 data points '
              'against a 2,362-point Hyde Park background mean of 7,732 CPM. 69 points exceeded '
              'the 1.5x criterion (11,598 CPM). The primary cluster of 52 points, immediately '
              'north of the former coal storage silo, ran 11,600-29,500 CPM (~1.5x-3.8x '
              'background) with 14 points above 3x. MJW conclusion: the scans "indicated the '
              'presence of elevated material on-site and potential TENORM material", and '
              '"additional screening and sampling is required to accurately characterize the '
              'material". Soil sampling for Ra-226 was PENDING at the report date and Phase 2 '
              '(inside the structures) awaits demolition. The same ground carries the 2010 '
              'Phase I ESA recognised environmental condition "Former Coal Storage Pile and '
              'Unknown Historical Disposal of Fly Ash" and the pre-remediation lead maximum of '
              '90,100 mg/kg. Source: Gamma Walkover Survey Report, MJW Doc. 26.1015.5, '
              '26 May 2026, pp2-4.')

AGENCY_BY_CODE = {
    '932023':             ('FUSRAP', ['U', 'Th', 'Ra'], 'USACE FUSRAP — Niagara Falls Storage Site.'),
    'FUSRAP-SEAWAY':      ('FUSRAP', ['U', 'Th', 'Ra'],
                           'USACE FUSRAP - Seaway Industrial Park, Tonawanda. Record of '
                           'Decision (Oct 2009): contaminants of concern Ra-226, Th-230 '
                           'and total uranium; Th-230 the principal contaminant at up to '
                           '2,800 pCi/g against a 15 pCi/g surface standard. Residues came '
                           'from the former Haist property (MED/AEC).'),
    'FUSRAP-LOOW':        ('FUSRAP', ['U', 'Th', 'Ra'], 'USACE FUSRAP — Lake Ontario Ordnance Works.'),
    'NFSS-VP-H-PRIME':    ('FUSRAP', ['U', 'Th', 'Ra'], 'USACE FUSRAP vicinity property.'),
    'NFSS-VP-X':          ('FUSRAP', ['U', 'Th', 'Ra'], 'USACE FUSRAP vicinity property.'),
    'NFSS-ANOMALY-CC':    ('FUSRAP', ['U', 'Th', 'Ra'], 'USACE FUSRAP vicinity property.'),
    'NFSS-CENTRAL-DITCH': ('FUSRAP', ['U', 'Th', 'Ra'], 'USACE FUSRAP supplemental limits area.'),
    '932032':             ('FUSRAP', ['U', 'Th'],       'USACE FUSRAP — Guterl Specialty Steel.'),
    '932028':             ('TENORM', ['U', 'Th', 'Ra'], 'TENORM recorded explicitly in the NYSDEC site record.'),
    'C932143':            ('TENORM', ['U', 'Th'],       'TENORM recorded explicitly in the NYSDEC site record.'),
    'C932150':            ('TENORM', [], ''),
    'C932157':            ('TENORM', [], ''),
    '932136':             ('TENORM', [], ''),
    'C932159':            ('TENORM', [], ''),
    'C932160':            ('TENORM', [], ''),

    # 3125 Highland Avenue / Tulip Molded Plastics, added 2026-08-11. ⚠ SCREENING ONLY — this is
    # the weakest basis in this table and the wording says so, because no laboratory result
    # exists yet. It is here rather than omitted because the survey was performed under the
    # NYSDEC-approved RI Work Plan expressly to the DMM-5 TENORM policy, and because BOTH
    # immediate neighbours (Tract I C932157 and Tract II 932136) are already TENORM-classified —
    # leaving the parcel between them untagged asserts an absence the record does not support.
    # ⛔ ISOTOPES DELIBERATELY EMPTY. Ra-226 is the PLANNED analyte (EPA 901.1m, 21-day
    # ingrowth), not a result — the same distinction drawn for C932164 above, where analytes
    # named in a work plan were excluded from the isotope list.
    '932169':             _RAD_TULIP,
    'C932169':            _RAD_TULIP,

    # Frontier Chemical Royal Avenue. Its 2014 Final Engineering Report devotes section 5.10 to
    # radiological material and Table 5.10 is headed "TENORM Waste Characterization"; 608 cubic
    # yards of TENORM remain on site under the cover, enveloped in orange filter fabric, managed
    # by environmental easement and site management plan.
    '932110':             ('TENORM', ['U', 'Th', 'Ra'],
                           'TENORM — Final Engineering Report (April 2014) section 5.10 and Table 5.10; '
                           '608 cubic yards retained on site beneath the cover.'),

    # 211 Main Street, North Tonawanda. NYSDEC Decision Document (9 Feb 2021) names radium among
    # the site's contaminants of concern, and the selected remedy removes "the area of elevated
    # gamma activity soil along the south side of the building" for off-site disposal. The extent
    # is drawn on Figure 4a of that document as "Approximate extent of elevated gamma activity".
    #
    # ⚠ The pCi/g figures below are read from the Pace Analytical report (Phase II ESA p90,
    # EPA 901.1), NOT from the narrative. The consultant's text in the Phase II, the RI and the
    # Decision Document all state "0.267 pCi/g Ra-226 and 0.136 pCi/g Ra-228 ... below the
    # guidance levels" — but that lab column is `Act ± Unc (MDC)`, so 0.267 and 0.136 are the
    # MINIMUM DETECTABLE CONCENTRATIONS, not the activities. The measured activities are
    # 2.426 ± 0.494 and 2.683 ± 0.547 pCi/g. The reported "result" for Ra-226 was also lower
    # than the method blank on the same run (0.295 pCi/g), which alone should have failed review.
    'C932171':            ('TENORM', ['Ra'],
                           'TENORM — NYSDEC Decision Document (Feb 2021) lists radium among the '
                           'contaminants of concern and the remedy removes the elevated gamma '
                           'activity soil for off-site disposal; extent mapped on Figure 4a. '
                           'Gamma spectroscopy (Pace, EPA 901.1): Ra-226 2.43 pCi/g, '
                           'Ra-228 2.68 pCi/g.'),

    # 401/402/430 Buffalo Avenue, Niagara Falls (Merani Hospitality). NYSDEC Decision Document
    # (28 Dec 2015) p9: "a post demolition radiological scan indicated the presence [of]
    # technically enhanced naturally occurring radioactive material (TENORM) slag used as fill on
    # site." p10: the IRMs "addressed the TENORM found on the 401 and 402 parcels. No detections
    # of radiation above normally expected background levels were observed on the 430 parcel."
    # The extent is drawn on Figure 5, "RI Radiologic Survey Results", legend "ELEVATED
    # RADIOLOGIC FIELD READING ABOVE BACKGROUND".
    #
    # Gamma walkover (FER p13): site background 6,000-8,000 cpm; an area beneath the asphalt lot
    # on 402 read 20,000-45,000 cpm, and locations on 401 read 10,000-20,000 cpm. Figure 8
    # tabulates 21 post-excavation readings, 2,410-44,441 cpm.
    #
    # Disposal is itself evidence of the classification: the 402 slag-fill went to Austin Master
    # Services' licensed radiologic handling facility (Martins Ferry, OH) and was trans-loaded to
    # the Energy Solutions licensed landfill at Clive, Utah; 72.5 tons from 401 went to WM's
    # Mahoning Landfill, Ohio.
    #
    # ⚠ Ra-226 ONLY, deliberately. In-situ gamma spectroscopy (Austin Master Services, ODH
    # In-Situ, RML #03219510000) on four containers reports `Activity | Uncertainty | MDA` —
    # the same column layout that produced the 211 Main error above. Read correctly:
    #   Ra-226  1.115 / 1.390 / 0.417 / 0.960 pCi/g   vs MDA 0.243 / 0.166 / 0.291 / 0.184  -> DETECTED in all four
    #   Ra-228  0.477 / 0.714 / 0.773 / 0.275 pCi/g   vs MDA 0.586 / 0.714 / 0.773 / 0.275  -> AT OR BELOW MDA in all four
    # Three of the four Ra-228 rows carry an uncertainty of exactly 0.000 and an activity equal
    # to the MDA — the signature of a non-detect reported at the detection limit. Ra-228 is
    # therefore NOT cross-listed. The Radiological Material Work Plan (19 Nov 2014) p15 names
    # U-234/235/238, Th-228/230/232 as the planned analyte suite, but those are analytes to be
    # tested for, not results; no isotope-specific data for them was located.
    'C932164':            ('TENORM', ['Ra'],
                           'TENORM — NYSDEC Decision Document (Dec 2015): post-demolition scan '
                           'found TENORM slag used as fill on the 401 and 402 parcels; extent '
                           'mapped on Figure 5 as "elevated radiologic field reading above '
                           'background". Gamma walkover 20,000-45,000 cpm against a 6,000-8,000 '
                           'cpm site background. Two waste streams: the 402 slag-fill went to a '
                           'licensed radiologic handling facility and on to the Energy Solutions '
                           'licensed landfill at Clive, Utah, while 72.5 tons from 401 went to '
                           "WM's Mahoning Landfill, Ohio. In-situ gamma spectroscopy on four of "
                           'the Ohio-bound containers (ODH In-Situ): Ra-226 0.42-1.39 pCi/g, '
                           'above the detection limit in all four; Ra-228 not detected.'),

    # ---- 2026-08-03 radiological investigation -------------------------------
    # Source: Niagara_Radiological_Sites_Investigation_Summary.html. Four carry EPA action
    # memoranda with isotope-specific results; Witmer's supporting record is pending FOIA and
    # is included on Caitlin's explicit call. Class MED-AEC is not used — these are CERCLA
    # removal actions on uranium/thorium-bearing industrial slag and fill, not Manhattan
    # Engineer District facilities, so they are TENORM.
    'EPA-NYN000206699':   ('TENORM', ['U', 'Th', 'Ra'],
                           'EPA CERCLA removal. Assessment 2013-2015: U-238 max 196, Th-232 max 541, '
                           'Ra-226 max 199 pCi/g. About 28,362 tons of low-level radioactive material '
                           'excavated from a 1.4-acre woodland and 3.3-acre parking area; completed 2021.'),
    'EPA-NYN000206697':   ('TENORM', ['U', 'Th', 'Ra'],
                           'EPA CERCLA removal, Upper Mountain Road cluster. Assessment 2013-2014: '
                           'U-238 max 26.7, Th-232 max 116, Ra-226 max 32.6 pCi/g. Culvert crossing and '
                           'gravel driveway removed and clean-backfilled; completed 2020.'),
    'EPA-NYN000203537':   ('TENORM', ['U', 'Th', 'Ra'],
                           'EPA 2021 action memorandum. Crawlspace soil: Th-232 up to 1,430 pCi/g, '
                           'Bi-212 519, Ac-228 and Ra-228 518, Pb-212 502, Tl-208 184, Ra-226 107, '
                           'U-238 70.5 pCi/g; crawlspace gamma above 500 microroentgen/hour (Oct 2019). '
                           'About 2,000 cubic metres estimated; residents temporarily relocated.'),
    'EPA-NYN000206698':   ('TENORM', ['U', 'Th', 'Ra'],
                           'EPA CERCLA removal. Cemetery assessment 2013: U-238 max 287, Th-232 max 358, '
                           'Ra-226 max 360 pCi/g. Adjacent residences 2016-2017: Ra-226 exposure-point '
                           'concentration 85.8 pCi/g. Cemetery residual status not established publicly.'),
    'EPA-NYN000204317':   ('TENORM', ['U'],
                           'EPA CERCLA Removal Only site. U-238 identified as the soil contaminant of '
                           'concern in industrial slag and fill 6-24 inches below surface over about '
                           '10,000 square feet of playground and rear parking lot; owner-led removal '
                           'under EPA oversight.'),
    # Witmer Road Drive-In. The investigation summary grades this UNRESOLVED — 2020 land-bank
    # meeting minutes only, with no isotope, concentration, exposure rate or quantity, and no
    # documented radiological remediation. Included on Caitlin's call 2026-08-03 because the
    # supporting record sits behind a pending FOIA request. The basis text says so plainly.
    '932118':             ('TENORM', [],
                           'Radiological material reported in June 2020 fieldwork per Niagara County '
                           'land-bank meeting minutes. No isotope, concentration, exposure rate or '
                           'quantity is in the public record and no radiological remediation is '
                           'documented; the supporting Phase II record is the subject of a pending '
                           'FOIA request. Evidence grade: UNRESOLVED pending release.'),
}
AGENCY_BY_NAME = {
    'balmer road school':               ('FUSRAP', ['U', 'Th', 'Ra'], 'USACE FUSRAP vicinity property.'),
    'st marys and bishop duffy school': ('TENORM', [], ''),
}

_ISO_ORDER = ['U', 'Th', 'Ra']


def _namekey(s):
    return re.sub(r'[^a-z0-9]+', ' ', (s or '').lower()).strip()


def verified_radionuclides(build_dir):
    """Radiological categories VERIFIED as detected at one built site, with provenance."""
    found = {}
    for path in glob.glob(os.path.join(BUILD_CHEM, build_dir, '*_detected_chemicals.csv')):
        for r in csv.DictReader(open(path, encoding='utf-8-sig')):
            chem = (r.get('chemical') or '').strip()
            if chem not in RADIOLOGICAL:
                continue
            if (r.get('verification_status') or '').strip() != 'VERIFIED':
                continue
            if (r.get('detection_status') or '').strip() != 'DETECTED':
                continue
            found[chem] = (r.get('example_provenance') or '').strip()
    return found


def classify(features, matches=None, build_sites=None):
    """{feature_index: {rad_class, rad_iso, rad_basis, rad_source}} for radioactive sites only."""
    if matches is None:
        build_sites = build_sites or M.load_build_sites()
        matches = M.match(features, build_sites)

    hand = load_hand_verified()

    cache = {}
    out = {}
    for i, f in enumerate(features):
        p = f['properties']
        pn = M.clean_pn(p.get('program_number'))
        agency = AGENCY_BY_CODE.get(pn) if pn else None
        if not agency:
            agency = AGENCY_BY_NAME.get(_namekey(p.get('site_name')))

        b = matches[i][0]
        bdir = (b or {}).get('dir')
        found = {}
        if bdir:
            if bdir not in cache:
                cache[bdir] = verified_radionuclides(bdir)
            found = cache[bdir]

        hv = hand.get(bdir) if bdir else None
        hv_rn = list((hv or {}).get('radionuclides') or [])

        if not agency and not found and not hv_rn:
            continue

        iso = list(agency[1]) if agency else []
        for chem in found:
            code = RADIOLOGICAL[chem]
            if code not in iso:
                iso.append(code)
        for name in hv_rn:
            code = isotope_code(name)
            if code and code not in iso:
                iso.append(code)
        iso.sort(key=lambda c: _ISO_ORDER.index(c) if c in _ISO_ORDER else 99)

        parts = []
        if agency:
            parts.append('agency')
        if hv_rn:
            parts.append('hand')
        if found:
            parts.append('derived')
        source = '+'.join(parts)

        basis = (agency[2] if agency else '').strip()
        if hv_rn:
            detail = ('Hand-validated radionuclide detections against '
                      f"{hv['source_document']}: {', '.join(hv_rn)}.")
            basis = (basis + ' ' + detail).strip() if basis else detail
        if found:
            names = ', '.join(sorted(found))
            cite = sorted(found.values())[0]
            detail = (f'Verified radionuclide detections in this site’s own documents: {names}'
                      + (f' (e.g. {cite}).' if cite else '.'))
            basis = (basis + ' ' + detail).strip() if basis else detail

        out[i] = {
            'rad_class': agency[0] if agency else CLASS_OTHER,
            'rad_iso': iso,
            'rad_basis': basis,
            'rad_source': source,
        }
    return out
