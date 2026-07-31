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
AGENCY_BY_CODE = {
    '932023':             ('FUSRAP', ['U', 'Th', 'Ra'], 'USACE FUSRAP — Niagara Falls Storage Site.'),
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
    # Frontier Chemical Royal Avenue. Its 2014 Final Engineering Report devotes section 5.10 to
    # radiological material and Table 5.10 is headed "TENORM Waste Characterization"; 608 cubic
    # yards of TENORM remain on site under the cover, enveloped in orange filter fabric, managed
    # by environmental easement and site management plan.
    '932110':             ('TENORM', ['U', 'Th', 'Ra'],
                           'TENORM — Final Engineering Report (April 2014) section 5.10 and Table 5.10; '
                           '608 cubic yards retained on site beneath the cover.'),
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
