"""
Export the two monitoring-well layers to GeoJSON for the web map.
  Niagara_Water_Testing_Sites  -> web/data/wells_wqp.geojson   (USGS/EPA Water Quality Portal)
  Niagara_DEC_Monitoring_Wells -> web/data/wells_dec.geojson   (NYSDEC cleanup-report wells)
Each well carries n_chemicals_found (drives droplet size) and a curated `chems` array
(drives the "filter wells by chemical" dropdown, same idea as the hazard-site dropdown).
"""
import sqlite3, json, os, re
from shapely import wkb

gpkg   = r'C:\Users\mcsha\Niagra\spatial\Niagara_County_HazWaste.gpkg'
outdir = r'C:\Users\mcsha\Niagra\web\data'

def strip_header(blob):
    flags = blob[3]; env = (flags >> 1) & 0x07
    return bytes(blob[8 + {0:0,1:32,2:48,3:48,4:64}.get(env,0):])
def pt(blob):
    g = wkb.loads(strip_header(blob)); return [round(g.x,6), round(g.y,6)]
def safe(v):
    if v is None: return None
    if isinstance(v,float) and v!=v: return None
    return v

# curated well contaminants → matched against the well's chemicals_found string
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

con = sqlite3.connect(gpkg); cur = con.cursor()

# ── WQP wells ────────────────────────────────────────────────────────────────
cur.execute('''SELECT geom, station_id, station_name, site_type, n_chemicals_found,
               chemicals_found, latest_year_tested, latest_year_detected, nearest_hazard_site,
               nearest_hazard_distance_m, source_database FROM Niagara_Water_Testing_Sites''')
feats = []
for r in cur.fetchall():
    cf = r[5] or ''
    feats.append({'type':'Feature','geometry':{'type':'Point','coordinates':pt(r[0])},'properties':{
        'well_id': safe(r[1]), 'name': safe(r[2]) or safe(r[1]), 'site_type': safe(r[3]),
        'n_found': int(safe(r[4]) or 0), 'chemicals_found': cf,
        'latest_year': safe(r[6]), 'latest_detect': safe(r[7]),
        'nearest_hazard': safe(r[8]), 'nearest_m': safe(r[9]), 'source_db': safe(r[10]),
        'chems': chems_of(cf), 'src': 'WQP'}})
json.dump({'type':'FeatureCollection','features':feats}, open(os.path.join(outdir,'wells_wqp.geojson'),'w'), separators=(',',':'))
print(f'WQP wells: {len(feats)} ({sum(1 for f in feats if f["properties"]["chems"])} with a curated chemical)')

# ── DEC cleanup-report wells ─────────────────────────────────────────────────
cur.execute('''SELECT geom, well_id, site_name, well_role, data_type, n_chemicals_found,
               chemicals_found, latest_year_tested, latest_year_detected, coord_precision,
               toc_latest_ugL, toc_max_ugL, program_number FROM Niagara_DEC_Monitoring_Wells''')
feats = []
for r in cur.fetchall():
    cf = r[6] or ''
    feats.append({'type':'Feature','geometry':{'type':'Point','coordinates':pt(r[0])},'properties':{
        'well_id': safe(r[1]), 'site': safe(r[2]), 'well_role': safe(r[3]), 'data_type': safe(r[4]),
        'n_found': int(safe(r[5]) or 0), 'chemicals_found': cf,
        'latest_year': safe(r[7]), 'latest_detect': safe(r[8]), 'coord_precision': safe(r[9]),
        'toc_latest': safe(r[10]), 'toc_max': safe(r[11]), 'program_number': safe(r[12]),
        'chems': chems_of(cf), 'src': 'DEC'}})
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
