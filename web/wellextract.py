"""Generic NYSDEC periodic-review analytical-table extractor.
Auto-detects pages with a 'Sample Location:' header, position-bins values to well columns,
classifies detects (U/UJ/R = non-detect; numeric or J = detect), captures sample years.
"""
import pdfplumber, re
UNITS={"�g/L","µg/L","ug/L","mg/L","pCi/L","ug/l","�g/kg","mg/kg","ng/L"}
# tokens on a Sample Location: row that are NOT wells (regulatory-standard columns etc.)
NONWELL={"standard","guidance","class","ga","gb","criteria","units","limit","limits","standards",
         "value","mcl","twa","ngwqs","tsc","tscs","tal","tcl","and","or","the","na"}

def words_by_line(page, ytol=2.5):
    ws=page.extract_words(keep_blank_chars=False)
    ws.sort(key=lambda w:(round(w["top"]/ytol), w["x0"]))
    lines=[]; cur=[]; cy=None
    for w in ws:
        if cy is None or abs(w["top"]-cy)<=ytol: cur.append(w); cy=w["top"] if cy is None else cy
        else: lines.append(cur); cur=[w]; cy=w["top"]
    if cur: lines.append(cur)
    return lines

# a well ID is a structured token: 0-5 leading letters, optional dash, 2-5 digits, 0-2 trailing letters
WELLID=re.compile(r"[A-Za-z]{0,5}-?\d{2,5}[A-Za-z]{0,2}$")
def header(lines):
    # take structured well-ID tokens after the 'Location:' token on the sample-location row
    for ln in lines:
        texts=[w["text"] for w in ln]
        if "Location:" in texts:
            li=texts.index("Location:")
            wells=[(w["text"],(w["x0"]+w["x1"])/2) for w in ln[li+1:]
                   if w["text"].lower() not in NONWELL and WELLID.fullmatch(w["text"])]
            if wells: return wells
    return []

DATERE=re.compile(r"\d{1,2}/\d{1,2}/(\d{2,4})")
def date_row(lines, ids, bounds):
    yrs={i:set() for i in ids}
    for ln in lines:
        texts=[w["text"] for w in ln]
        if "Date:" not in texts: continue
        for w in ln:
            m=DATERE.fullmatch(w["text"])
            if not m: continue
            y=int(m.group(1)); y=y+2000 if y<100 else y
            if not (1980<=y<=2030): continue
            xc=(w["x0"]+w["x1"])/2
            for k,(lo,hi) in enumerate(bounds):
                if lo<=xc<hi: yrs[ids[k]].add(y); break
    return yrs

def is_detect(cell):
    if not cell: return None
    toks=cell.split()
    if any(t.startswith("<") for t in toks): return False   # "<5.0" = below detection limit = non-detect
    if any(t in ("U","UJ","UR","R","U*","NA","--","ND","NS","NR") for t in toks): return False
    if any(re.fullmatch(r"\d*\.?\d+",t) for t in toks): return True
    return None

def cell_value(cell):
    """Return (value, status) for a result cell. status: 'detect' | 'nondetect' | 'none'.
    '34 J'->(34,detect)  '5.0 U'/'<5.0'->(5.0,nondetect: the number IS the detection limit)
    'R'/'--'/'NS'->(None,none)  bare 'ND'->(None,nondetect, no limit)."""
    if not cell: return (None,'none')
    toks=cell.split()
    if any(t in ('R','UR','NS','NR','--','-') for t in toks): return (None,'none')
    num=None
    for t in toks:
        tt=t.lstrip('<').replace(',','')
        if re.fullmatch(r"\d*\.?\d+", tt): num=float(tt); break
    if num is None:
        if any(t in ('ND','U','UJ') for t in toks): return (None,'nondetect')
        return (None,'none')
    nd = any(t in ('U','UJ','U*') for t in toks) or any(t.startswith('<') for t in toks)
    return (num, 'nondetect' if nd else 'detect')

def _agg_conc(a, b):
    """Combine two (value,status) samples for the same analyte/year: a detection beats a
    non-detect; among detections take the max; among non-detects take the lowest limit."""
    if a is None: return b
    if b is None: return a
    (va,sa),(vb,sb)=a,b
    if sa=='detect' and sb=='detect':
        vals=[v for v in (va,vb) if v is not None]; return (max(vals) if vals else None,'detect')
    if sa=='detect': return a
    if sb=='detect': return b
    vals=[v for v in (va,vb) if v is not None]; return (min(vals) if vals else None,'nondetect')

def parse_page(page):
    lines=words_by_line(page); wells=header(lines)
    if not wells: return None
    centers=[c for _,c in wells]; ids=[i for i,_ in wells]
    bounds=[]
    for k in range(len(centers)):
        lo=(centers[k-1]+centers[k])/2 if k>0 else centers[k]-45
        hi=(centers[k]+centers[k+1])/2 if k<len(centers)-1 else centers[k]+55
        bounds.append((lo,hi))
    yrs=date_row(lines, ids, bounds)  # {col_index-ish} -> years per well-id (merged); recompute per-column below
    # per-column year: bin each date token to its column
    col_year=[None]*len(ids)
    for ln in lines:
        if "Date:" not in [w["text"] for w in ln]: continue
        for w in ln:
            m=DATERE.fullmatch(w["text"])
            if not m: continue
            y=int(m.group(1)); y=y+2000 if y<100 else y
            if not (1980<=y<=2030): continue
            xc=(w["x0"]+w["x1"])/2
            for k,(lo,hi) in enumerate(bounds):
                if lo<=xc<hi: col_year[k]=y; break
    # per column accumulate detects/tested + numeric values
    cols=[{"id":ids[k],"year":col_year[k],"detects":set(),"tested":set(),"values":{}} for k in range(len(ids))]
    for ln in lines:
        ui=None
        for j,w in enumerate(ln):
            if w["text"] in UNITS: ui=j; break
        if ui is None: continue
        name_parts=[w["text"] for w in ln[:ui]]
        while len(name_parts)>1 and re.fullmatch(r"\d{1,3}(\.\d+)?|\d+\.\d+", name_parts[-1]):
            name_parts.pop()
        analyte=" ".join(name_parts).strip()
        if not analyte or "Location" in analyte or "Sample" in analyte: continue
        cell=[[] for _ in ids]
        for w in ln[ui+1:]:
            xc=(w["x0"]+w["x1"])/2
            for k,(lo,hi) in enumerate(bounds):
                if lo<=xc<hi: cell[k].append(w["text"]); break
        for k in range(len(ids)):
            cs=" ".join(cell[k]).strip()
            d=is_detect(cs)
            if d is not None: cols[k]["tested"].add(analyte)
            if d: cols[k]["detects"].add(analyte)
            val,status=cell_value(cs)
            if status!='none':
                cols[k]["values"][analyte]=_agg_conc(cols[k]["values"].get(analyte),(val,status))
    return cols

def extract(pdf_path):
    """returns {well_id: {'found':set,'tested':set,'years':set,'detect_years':set,
    'found_by_year':{chemical:set(years)}, 'conc':{analyte:{year:(value,status)}}}}.
    found_by_year answers "which wells had chemical X detected by year Y"; conc adds the
    numeric concentration series (value + detect/nondetect) for the pop-up plots."""
    wells={}
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            txt=page.extract_text() or ""
            if "Location:" not in txt: continue
            cols=parse_page(page)
            if not cols: continue
            for c in cols:
                w=wells.setdefault(c["id"],{"found":set(),"tested":set(),"years":set(),
                                             "detect_years":set(),"found_by_year":{},"conc":{}})
                w["found"].update(c["detects"]); w["tested"].update(c["tested"])
                if c["year"] is not None:
                    yr=c["year"]
                    if c["tested"] or c["detects"]: w["years"].add(yr)
                    if c["detects"]:
                        w["detect_years"].add(yr)
                        for chem in c["detects"]:
                            w["found_by_year"].setdefault(chem,set()).add(yr)
                    for analyte,(val,status) in c["values"].items():
                        yd=w["conc"].setdefault(analyte,{})
                        yd[yr]=_agg_conc(yd.get(yr),(val,status))
    return wells

if __name__=="__main__":
    import sys, glob
    for pdf in sorted(glob.glob(r"C:/Users/mcsha/Niagra/docs/LoveCanal_932020_*_Periodic_Review_Report.pdf")):
        w=extract(pdf)
        nd=sum(1 for x in w.values() if x["found"])
        yrs=sorted({y for x in w.values() for y in x["years"]})
        print(f"{pdf.split('/')[-1]:52s} wells={len(w):3d} with_detect={nd:3d} years={yrs}")
