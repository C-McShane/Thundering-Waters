"""
Build the per-year monitoring-well datasets that power the map's Year filter:
  csv/Niagara_DEC_Wells_ChemYears.json   {well_id: {curated_chemical: [years detected]}}
  csv/Niagara_WQP_Wells_ChemYears.json   {station_id: {curated_chemical: [years detected]}}
  csv/Niagara_SArea_TOC_Years.json       {well_id: {year: Total Organic Concentration ug/L}}

DEC/WQP feed the "which wells had chemical X detected by year Y" (cumulative) filter;
S-Area's TOC series feeds a separate intensity-over-time view (S-Area reports NAPL/TOC,
not named chemicals, so it doesn't fit the chemical dropdown).

Usage: python build_well_years.py [dec|wqp|toc|all]
DEC is slow (~8-9 min — parses 7 multi-hundred-page PDFs); run it standalone/in background.
"""
import sys, os, json, re
sys.path.insert(0, os.path.dirname(__file__))
from well_chem_lexicon import curated_name

DOCS = r'C:\Users\mcsha\Niagra\docs'
CSV  = r'C:\Users\mcsha\Niagra\csv'

# ── DEC: per-year (well, chemical) from cleanup-report analytical tables ───────
DEC_SITES = {
    "LoveCanal_932020": [
        "LoveCanal_932020_2015_Periodic_Review_Report.pdf",
        "LoveCanal_932020_2016_Periodic_Review_Report.pdf",
        "LoveCanal_932020_2017_Periodic_Review_Report.pdf",
        "LoveCanal_932020_2019_Periodic_Review_Report.pdf",
        "LoveCanal_932020_2022_Periodic_Review_Report.pdf",
    ],
    "102ndStreet_932022": ["102ndStreet_932022_2019_Periodic_Review_Report.pdf"],
    "DurezInlet_932018":  ["DurezInlet_932018_2024_Periodic_Review_Report.pdf"],
}

def build_dec():
    from wellextract import extract
    import time
    raw = {}
    t0 = time.time()
    for site, files in DEC_SITES.items():
        for fn in files:
            t1 = time.time()
            wells = extract(os.path.join(DOCS, fn))
            for wid, rec in wells.items():
                wd = raw.setdefault(wid, {})
                for chem, years in rec["found_by_year"].items():
                    wd.setdefault(chem, set()).update(years)
            print(f"  {fn}: {len(wells)} wells in {time.time()-t1:.0f}s", flush=True)
    # fold raw analyte names through the curated lexicon
    out = {}
    for wid, chems in raw.items():
        for rawchem, years in chems.items():
            cur = curated_name(rawchem)
            if cur:
                out.setdefault(wid, {}).setdefault(cur, set()).update(years)
    serial = {w: {c: sorted(y) for c, y in d.items()} for w, d in out.items()}
    json.dump(serial, open(os.path.join(CSV, 'Niagara_DEC_Wells_ChemYears.json'), 'w'), separators=(',', ':'))
    print(f"DEC done in {time.time()-t0:.0f}s | {len(serial)} wells with curated chem-year data")

# ── WQP: per-year (station, chemical) from the raw result pull ─────────────────
def build_wqp():
    import pandas as pd
    r = pd.read_parquet(os.path.join(CSV, '_wqp_raw_results_cache.parquet'))
    det = r[r.is_detect].copy()
    det['curated'] = det.CharacteristicName.map(curated_name)
    det = det[det.curated.notna()]
    out = {}
    for (station, chem), grp in det.groupby(['MonitoringLocationIdentifier', 'curated']):
        years = sorted(int(y) for y in grp.year.dropna().unique())
        if years:
            out.setdefault(station, {})[chem] = years
    json.dump(out, open(os.path.join(CSV, 'Niagara_WQP_Wells_ChemYears.json'), 'w'), separators=(',', ':'))
    print(f"WQP done | {len(out)} stations with curated chem-year data")

# ── S-Area: per-year Total Organic Concentration (position-based table parse) ──
PROG = {36: "V-Area (Table 2.3)", 44: "Shallow Bedrock SBCP (Table 3.7)",
        46: "Intermediate/Deep Bedrock IDCP (Table 3.9)", 48: "Former EMP (Table 3.11)"}
WELL = re.compile(r'^([A-Z]{2,3}-?\d{1,4}[A-Z]?)$')
YEAR = re.compile(r'^(19|20)\d{2}$')

def _lines_of(page, ytol=2.5):
    ws = page.extract_words(x_tolerance=2)
    groups = {}
    for w in ws:
        y = round(w['top'] / ytol)
        groups.setdefault(y, []).append(w)
    return [sorted(v, key=lambda w: w['x0']) for _, v in sorted(groups.items())]

def _clean_val(tok):
    tok = re.sub(r'\(\d\)$', '', tok)
    if tok in ("ND", "ND/ND"): return 0.0
    if tok in ("NS", "--", "-", "", "NS/NS"): return None
    tok = tok.split("/")[0].replace(",", "")
    m = re.fullmatch(r'\d*\.?\d+', tok)
    return float(m.group()) if m else None

def _find_header_pair(lines, start_idx, max_scan=4):
    for i in range(start_idx, min(start_idx + max_scan, len(lines))):
        texts = [w['text'] for w in lines[i] if w['text'] != 'Well']
        yeartoks = [t for t in texts if YEAR.match(t)]
        if len(yeartoks) >= 3 and len(yeartoks) >= 0.5 * len(texts):
            year_line = lines[i]
            cand = []
            if i > 0: cand.append(lines[i-1])
            if i+1 < len(lines): cand.append(lines[i+1])
            subcol_line = max(cand, key=lambda l: len(l)) if cand else year_line
            if len(subcol_line) <= len(year_line):
                subcol_line = year_line
            return i, year_line, subcol_line
    return None, None, None

def build_toc():
    import pdfplumber
    pdf = pdfplumber.open(os.path.join(DOCS, 'SArea_932019A_2019_Evaluation_Report.pdf'))
    toc_years = {}
    for pn, prog in PROG.items():
        lines = _lines_of(pdf.pages[pn])
        i = 0; yanchors, sanchors = [], []
        while i < len(lines):
            texts = [w['text'] for w in lines[i]]
            if 'Total Organic Concentration' in ' '.join(texts) or (not yanchors and i == 0):
                hidx, yline, sline = _find_header_pair(lines, i)
                if yline is not None:
                    yanchors = [(w['text'], (w['x0']+w['x1'])/2) for w in yline if YEAR.match(w['text'])]
                    sanchors = [(w['x0']+w['x1'])/2 for w in sline if w['text'] != 'Well']
                    i = hidx + 2
                    continue
            if lines[i] and WELL.match(lines[i][0]['text']) and yanchors:
                wid = lines[i][0]['text']
                for w in lines[i][1:]:
                    xc = (w['x0']+w['x1'])/2
                    v = _clean_val(w['text'])
                    if v is None: continue
                    sc_x = min(sanchors, key=lambda a: abs(a-xc)) if sanchors else xc
                    yr_txt, _ = min(yanchors, key=lambda a: abs(a[1]-sc_x))
                    toc_years.setdefault(wid, {}).setdefault(int(yr_txt), []).append(v)
            i += 1
    pdf.close()
    toc_series = {w: {y: max(vs) for y, vs in yd.items()} for w, yd in toc_years.items()}
    json.dump(toc_series, open(os.path.join(CSV, 'Niagara_SArea_TOC_Years.json'), 'w'), separators=(',', ':'))
    print(f"S-Area TOC done | {len(toc_series)} wells with per-year TOC series")

if __name__ == '__main__':
    which = sys.argv[1] if len(sys.argv) > 1 else 'all'
    if which in ('dec', 'all'): build_dec()
    if which in ('wqp', 'all'): build_wqp()
    if which in ('toc', 'all'): build_toc()
