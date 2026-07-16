"""
Export the two monitoring-well layers to GeoJSON for the web map.
  Niagara_Water_Testing_Sites  -> web/data/wells_wqp.geojson   (USGS/EPA Water Quality Portal)
  Niagara_DEC_Monitoring_Wells -> web/data/wells_dec.geojson   (NYSDEC cleanup-report wells)
Each well carries n_chemicals_found (drives droplet size), a curated `chems` array
(drives the "filter wells by chemical" dropdown), and — if build_well_years.py has been
run — a `chems_years` map {chemical: [years detected]} that drives the Year filter
("show wells where chemical X had been detected by year Y", cumulative). S-Area DEC
wells additionally carry `toc_series` {year: value} for the separate TOC-over-time view,
since that site reports NAPL/Total Organic Concentration rather than named chemicals.
Run build_well_years.py first (or re-run it) to refresh the per-year source data;
this script just merges whatever's in csv/Niagara_*_ChemYears.json / _TOC_Years.json.
"""
import sqlite3, json, os, sys
from shapely import wkb
sys.path.insert(0, os.path.dirname(__file__))
from well_chem_lexicon import CHEM_RX, PRIORITY, chems_of

gpkg   = r'C:\Users\mcsha\Niagra\spatial\Niagara_County_HazWaste.gpkg'
outdir = r'C:\Users\mcsha\Niagra\web\data'
csvdir = r'C:\Users\mcsha\Niagra\csv'

def _load(name):
    p = os.path.join(csvdir, name)
    return json.load(open(p)) if os.path.exists(p) else {}

DEC_YEARS  = _load('Niagara_DEC_Wells_ChemYears.json')
WQP_YEARS  = _load('Niagara_WQP_Wells_ChemYears.json')
TOC_YEARS  = _load('Niagara_SArea_TOC_Years.json')

def strip_header(blob):
    flags = blob[3]; env = (flags >> 1) & 0x07
    return bytes(blob[8 + {0:0,1:32,2:48,3:48,4:64}.get(env,0):])
def pt(blob):
    g = wkb.loads(strip_header(blob)); return [round(g.x,6), round(g.y,6)]
def safe(v):
    if v is None: return None
    if isinstance(v,float) and v!=v: return None
    return v

con = sqlite3.connect(gpkg); cur = con.cursor()

# ── WQP wells ────────────────────────────────────────────────────────────────
cur.execute('''SELECT geom, station_id, station_name, site_type, n_chemicals_found,
               chemicals_found, latest_year_tested, latest_year_detected, nearest_hazard_site,
               nearest_hazard_distance_m, source_database FROM Niagara_Water_Testing_Sites''')
feats = []
for r in cur.fetchall():
    cf = r[5] or ''
    props = {
        'well_id': safe(r[1]), 'name': safe(r[2]) or safe(r[1]), 'site_type': safe(r[3]),
        'n_found': int(safe(r[4]) or 0), 'chemicals_found': cf,
        'latest_year': safe(r[6]), 'latest_detect': safe(r[7]),
        'nearest_hazard': safe(r[8]), 'nearest_m': safe(r[9]), 'source_db': safe(r[10]),
        'chems': chems_of(cf), 'src': 'WQP'}
    cy = WQP_YEARS.get(safe(r[1]))
    if cy: props['chems_years'] = cy
    feats.append({'type':'Feature','geometry':{'type':'Point','coordinates':pt(r[0])},'properties':props})
json.dump({'type':'FeatureCollection','features':feats}, open(os.path.join(outdir,'wells_wqp.geojson'),'w'), separators=(',',':'))
print(f'WQP wells: {len(feats)} ({sum(1 for f in feats if f["properties"]["chems"])} with a curated chemical)')

# ── DEC cleanup-report wells ─────────────────────────────────────────────────
cur.execute('''SELECT geom, well_id, site_name, well_role, data_type, n_chemicals_found,
               chemicals_found, latest_year_tested, latest_year_detected, coord_precision,
               toc_latest_ugL, toc_max_ugL, program_number FROM Niagara_DEC_Monitoring_Wells''')
feats = []
for r in cur.fetchall():
    cf = r[6] or ''
    wid = safe(r[1])
    props = {
        'well_id': wid, 'site': safe(r[2]), 'well_role': safe(r[3]), 'data_type': safe(r[4]),
        'n_found': int(safe(r[5]) or 0), 'chemicals_found': cf,
        'latest_year': safe(r[7]), 'latest_detect': safe(r[8]), 'coord_precision': safe(r[9]),
        'toc_latest': safe(r[10]), 'toc_max': safe(r[11]), 'program_number': safe(r[12]),
        'chems': chems_of(cf), 'src': 'DEC'}
    cy = DEC_YEARS.get(wid)
    if cy: props['chems_years'] = cy
    ts = TOC_YEARS.get(wid)
    if ts: props['toc_series'] = {int(k): v for k, v in ts.items()}
    feats.append({'type':'Feature','geometry':{'type':'Point','coordinates':pt(r[0])},'properties':props})
json.dump({'type':'FeatureCollection','features':feats}, open(os.path.join(outdir,'wells_dec.geojson'),'w'), separators=(',',':'))
print(f'DEC wells: {len(feats)} ({sum(1 for f in feats if f["properties"]["chems"])} with a curated chemical)')

con.close()
# report chem coverage for the dropdown
import collections
allf = json.load(open(os.path.join(outdir,'wells_wqp.geojson')))['features'] + json.load(open(os.path.join(outdir,'wells_dec.geojson')))['features']
c = collections.Counter(x for f in allf for x in f['properties']['chems'])
print('\nchemical -> #wells (dropdown):')
for n,_ in CHEM_RX:
    if c[n]: print(f'  {n}: {c[n]}')
for fn in ['wells_wqp.geojson','wells_dec.geojson']:
    print(f'  {fn}: {os.path.getsize(os.path.join(outdir,fn))/1024:.0f} KB')
