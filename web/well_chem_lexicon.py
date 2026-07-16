"""
Shared curated-contaminant lexicon for the monitoring-well map layers.
Used by export_wells.py (the flat `chems` filter) and build_well_years.py
(the per-year `chems_years` filter) so both features show the exact same
chemical categories and counts.
"""
import re

CHEM_RX = [(n, re.compile(p, re.I)) for n, p in [
    ('Trichloroethene (TCE)',   r'trichloroethene|\btce\b'),
    ('Tetrachloroethene (PCE)', r'tetrachloroethene|tetrachloroethylene|perchloroethylene|\bpce\b'),
    ('Vinyl chloride',          r'vinyl chloride'),
    ('Benzene',                 r'(?<![a-z])benzene\b'),
    ('Arsenic',                 r'arsenic'),
    ('Lead',                    r'\blead\b'),
    ('Mercury',                 r'mercury'),
    ('PFAS (PFOA/PFOS)',        r'perfluoro|pfoa|pfos'),
    ('PCBs',                    r'\bpcb|aroclor|polychlorinated biphenyl|chlorobiphenyl'),
    ('Dioxins / furans',        r'dioxin|furan|tcdd'),
    ('Benzo(a)pyrene',          r'benzo[\(\[]a[\)\]]pyrene'),
    ('Chromium',                r'chromium'),
    ('Cadmium',                 r'cadmium'),
    ('Chloroform / THMs',       r'chloroform|trihalomethane|bromoform|bromodichloro|dibromochloro'),
    ('Toluene',                 r'\btoluene\b'),
    ('Xylene',                  r'xylene'),
    ('Ethylbenzene',            r'ethylbenzene'),
    ('Chlorobenzene',           r'\bchlorobenzene\b'),
    ('1,2-Dichloroethane',      r'1,2-dichloroethane'),
    ('Atrazine',                r'atrazine'),
    ('Lindane / BHC',           r'lindane|\bbhc\b|hexachlorocyclohexane|gamma-hch'),
    ('DDT / DDE / DDD',         r"\bdd[tde]\b|p,p'-dd"),
    ('Dieldrin',                r'dieldrin'),
    ('Cyanide',                 r'cyanide'),
    ('Naphthalene',             r'naphthalene'),
    ('Uranium',                 r'uranium'),
    ('Radium / Radon',          r'radium|radon'),
    ('Tritium',                 r'tritium'),
]]
PRIORITY = ['Trichloroethene (TCE)','Tetrachloroethene (PCE)','Vinyl chloride','Benzene','Arsenic',
            'Lead','Mercury','PFAS (PFOA/PFOS)','PCBs','Dioxins / furans','Benzo(a)pyrene','Chromium','Cadmium']

def chems_of(txt):
    txt = txt or ''
    return [n for n, rx in CHEM_RX if rx.search(txt)]

def curated_name(raw_chemical_name):
    """Map one raw analyte name (e.g. from a DEC table or WQP CharacteristicName)
    to its curated category, or None if it doesn't match any curated chemical."""
    for n, rx in CHEM_RX:
        if rx.search(raw_chemical_name or ''):
            return n
    return None
