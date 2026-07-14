"""
Export key GPKG layers to GeoJSON for the web map.
Run once; outputs go to web/data/
"""
import sqlite3, json, struct, os
from pyproj import Transformer
from shapely import wkb
from shapely.ops import transform as shp_transform
import functools

gpkg  = r'C:\Users\mcsha\Niagra\spatial\Niagara_County_HazWaste.gpkg'
outdir = r'C:\Users\mcsha\Niagra\web\data'
os.makedirs(outdir, exist_ok=True)

def strip_header(blob):
    flags = blob[3]
    env_code = (flags >> 1) & 0x07
    env_sizes = {0:0, 1:32, 2:48, 3:48, 4:64}
    return bytes(blob[8 + env_sizes.get(env_code, 0):])

def to_wgs84(geom, from_epsg):
    if from_epsg == 4326:
        return geom
    t = Transformer.from_crs(f'EPSG:{from_epsg}', 'EPSG:4326', always_xy=True)
    return shp_transform(t.transform, geom)

def geom_to_geojson(blob, from_epsg=4326):
    g = wkb.loads(strip_header(blob))
    g = to_wgs84(g, from_epsg)
    return json.loads(json.dumps(g.__geo_interface__))

def safe(v):
    if v is None: return None
    if isinstance(v, float) and (v != v): return None  # NaN
    return v

con = sqlite3.connect(gpkg)
cur = con.cursor()

# ── 1. HAZARD SITES ────────────────────────────────────────────────────────────
print('Exporting hazard sites...')
import re as _re

# Danger-ranked chemicals → regex matched against each site's `chemicals` field
CHEM_RX = [(n, _re.compile(p, _re.I)) for n, p in [
    ('Dioxins / TCDD',      r'dioxin|tcdd|2,3,7,8'),
    ('Asbestos',            r'asbestos'),
    ('Benzene',             r'\bbenzene\b'),
    ('Vinyl chloride',      r'vinyl chloride'),
    ('Arsenic',             r'arsenic'),
    ('PCBs',                r'\bpcb'),
    ('Hexavalent chromium', r'chromium|hexavalent'),
    ('TCE',                 r'trichloroethene|\btce\b'),
    ('Cadmium',             r'cadmium'),
    ('Lead',                r'\blead\b'),
    ('Benzo(a)pyrene',      r'benzo\(a\)pyrene'),
    ('Lindane / BHC',       r'lindane|\bbhc\b|hexachlorocyclohexane'),
    ('Beryllium',           r'beryllium'),
    ('Mercury',             r'mercury'),
    ('Hexachlorobenzene',   r'hexachlorobenzene'),
    ('Cyanide',             r'cyanide'),
]]
# Curated radioactive classification. FUSRAP isotope tags are DOE/USACE-sourced (our
# narratives don't list them); TENORM sites get a TENORM tag (isotopes only where recorded).
RADIO_BY_CODE = {
    '932023': ('FUSRAP', ['U', 'Th', 'Ra']),   'FUSRAP-LOOW': ('FUSRAP', ['U', 'Th', 'Ra']),
    'NFSS-VP-H-PRIME': ('FUSRAP', ['U', 'Th', 'Ra']), 'NFSS-VP-X': ('FUSRAP', ['U', 'Th', 'Ra']),
    'NFSS-ANOMALY-CC': ('FUSRAP', ['U', 'Th', 'Ra']), 'NFSS-CENTRAL-DITCH': ('FUSRAP', ['U', 'Th', 'Ra']),
    '932032': ('FUSRAP', ['U', 'Th']),         # Guterl Specialty Steel
    '932028': ('TENORM', ['U', 'Th', 'Ra']),   # TAM Ceramics (explicit in data)
    'C932143': ('TENORM', ['U', 'Th']),        # Northern Ethanol (explicit)
    'C932150': ('TENORM', []), 'C932157': ('TENORM', []), '932136': ('TENORM', []),
    'C932159': ('TENORM', []), 'C932160': ('TENORM', []),
}
RADIO_BY_NAME = {
    'balmer road school': ('FUSRAP', ['U', 'Th', 'Ra']),
    'st marys and bishop duffy school': ('TENORM', []),
}
def _namekey(s): return _re.sub(r'[^a-z0-9]+', ' ', (s or '').lower()).strip()

cur.execute('''SELECT geom, site_name, designation, program_type, program_category,
               area_acres_best, chemicals, narrative, website, address, city, zip,
               latitude, longitude, npl_status, non_npl_status, program_number
               FROM Niagara_County_Hazard_Sites''')
rows = cur.fetchall()
features = []
for r in rows:
    g = geom_to_geojson(r[0], 4326)
    narr = r[7] or ''
    chem_txt = r[6] or ''
    chems = [n for n, rx in CHEM_RX if rx.search(chem_txt)]
    rad = RADIO_BY_CODE.get((r[16] or '').strip()) or RADIO_BY_NAME.get(_namekey(r[1]))
    features.append({
        'type': 'Feature',
        'geometry': g,
        'properties': {
            'site_name':       safe(r[1]) or 'Unnamed Site',
            'designation':     safe(r[2]) or 'Information Not Available',
            'program_type':    safe(r[3]),
            'program_category':safe(r[4]),
            'acres':           safe(r[5]),
            'chemicals':       safe(r[6]),
            'narrative':       narr[:600] + ('…' if len(narr) > 600 else ''),
            'website':         safe(r[8]),
            'address':         safe(r[9]),
            'city':            safe(r[10]),
            'zip':             safe(r[11]),
            'lat':             safe(r[12]),
            'lon':             safe(r[13]),
            'chems':           chems,
            'rad_class':       rad[0] if rad else None,
            'rad_iso':         rad[1] if rad else [],
        }
    })

with open(os.path.join(outdir, 'hazard_sites.geojson'), 'w') as f:
    json.dump({'type': 'FeatureCollection', 'features': features}, f, separators=(',',':'))
n_chem = sum(1 for ft in features if ft['properties']['chems'])
n_rad  = sum(1 for ft in features if ft['properties']['rad_class'])
print(f'  {len(features)} sites written ({n_chem} chemical-tagged, {n_rad} radioactive)')

# ── 2. CENSUS TRACTS ───────────────────────────────────────────────────────────
print('Exporting census tracts...')
cur.execute('''SELECT geom, GEOID, NAME, NAMELSAD, aland_acres,
               site_count, total_acres, coverage_pct, sites_per_sqmi
               FROM census_tracts_contamination''')
rows = cur.fetchall()
features = []
for r in rows:
    g = geom_to_geojson(r[0], 26917)
    features.append({
        'type': 'Feature',
        'geometry': g,
        'properties': {
            'geoid':        r[1],
            'name':         r[2],
            'namelsad':     r[3],
            'aland_acres':  safe(r[4]),
            'site_count':   safe(r[5]) or 0,
            'cont_acres':   safe(r[6]) or 0,
            'coverage_pct': safe(r[7]) or 0,
            'sites_per_sqmi': safe(r[8]) or 0,
        }
    })
with open(os.path.join(outdir, 'census_tracts.geojson'), 'w') as f:
    json.dump({'type': 'FeatureCollection', 'features': features}, f, separators=(',',':'))
print(f'  {len(features)} tracts written')

# ── 3. IMPACT ZONE (dissolved to a single perimeter) ────────────────────────────
print('Exporting impact zone (dissolved perimeter)...')
from shapely.ops import unary_union
cur.execute('''SELECT geom, aland_acres, site_count, total_acres
               FROM NiagaraFalls_Area_ImpactZone''')
rows = cur.fetchall()
geoms = [wkb.loads(strip_header(r[0])) for r in rows]
dissolved = unary_union(geoms).buffer(0)                    # merge tracts, drop internal edges
dissolved = to_wgs84(dissolved, 26917)
aland = sum(safe(r[1]) or 0 for r in rows)
sites = sum(int(safe(r[2]) or 0) for r in rows)
acres = sum(safe(r[3]) or 0 for r in rows)
feat = {
    'type': 'Feature',
    'geometry': json.loads(json.dumps(dissolved.__geo_interface__)),
    'properties': {
        'name':        'Niagara Falls Area Impact Zone',
        'tracts':      len(rows),
        'site_count':  sites,
        'cont_acres':  round(acres, 1),
        'aland_acres': round(aland, 1),
    }
}
with open(os.path.join(outdir, 'impact_zone.geojson'), 'w') as f:
    json.dump({'type': 'FeatureCollection', 'features': [feat]}, f, separators=(',',':'))
print(f'  1 dissolved impact-zone perimeter written (from {len(rows)} tracts)')

# ── 4b. CANCER SIR (block groups) — statistically elevated cancers ──────────────
print('Exporting cancer SIR (block groups)...')
CANCERS = ['Mesothelioma', 'Lung', 'Bladder', 'Esophagus', 'Oral', 'Brain']
cur.execute('SELECT * FROM block_group_healthPOP_stats')
bgcols = [d[0] for d in cur.description]
def _bi(name): return bgcols.index(name) if name in bgcols else None
gi = _bi('geom')
rows = cur.fetchall()
features = []
for r in rows:
    props = {'geoid': r[_bi('GEOID')], 'name': r[_bi('NAMELSAD')], 'pop': safe(r[_bi('total_pop')])}
    for cx in CANCERS:
        oi, ei = _bi('observed_%s' % cx), _bi('expected_%s' % cx)
        try:    o = float(r[oi]); e = float(r[ei])
        except (TypeError, ValueError): o = e = None
        props['obs_%s' % cx] = o
        props['exp_%s' % cx] = round(e, 2) if e is not None else None
        props['sir_%s' % cx] = round(o / e, 3) if (o is not None and e and e > 0) else None
    features.append({'type': 'Feature', 'geometry': geom_to_geojson(r[gi], 26917), 'properties': props})
with open(os.path.join(outdir, 'cancer_sir.geojson'), 'w') as f:
    json.dump({'type': 'FeatureCollection', 'features': features}, f, separators=(',', ':'))
print(f'  {len(features)} block groups written')

# ── 4c. WATER (hydro areas: Niagara River, canals, reservoirs, ponds) ───────────
print('Exporting water...')
cur.execute('SELECT geom, FULLNAME FROM hydro_area')
rows = cur.fetchall()
features = [{'type': 'Feature', 'geometry': geom_to_geojson(r[0], 26917),
            'properties': {'name': safe(r[1])}} for r in rows]
with open(os.path.join(outdir, 'water.geojson'), 'w') as f:
    json.dump({'type': 'FeatureCollection', 'features': features}, f, separators=(',', ':'))
print(f'  {len(features)} water bodies written')

con.close()

# ── 5. MAJOR ROADS (curated arterials + highways + named additions) ─────────────
print('Exporting major roads...')
import shapefile as _shp
_rtf = Transformer.from_crs('EPSG:26917', 'EPSG:4326', always_xy=True)

def _seglines(sh):
    pts = sh.points; parts = list(sh.parts) + [len(pts)]; out = []
    for i in range(len(parts) - 1):
        seg = [[round(x, 6), round(y, 6)] for x, y in (_rtf.transform(px, py) for px, py in pts[parts[i]:parts[i+1]])]
        if len(seg) >= 2:
            out.append(seg)
    return out

def _mkfeat(lines, name, cls):
    geom = {'type': 'LineString', 'coordinates': lines[0]} if len(lines) == 1 else {'type': 'MultiLineString', 'coordinates': lines}
    return {'type': 'Feature', 'geometry': geom, 'properties': {'name': name, 'road_class': cls}}

road_feats = []; _seen = set()
# curated select_roads (S1100 highway, S1200 arterial)
_CLS = {'S1100': 'Highway', 'S1200': 'Arterial'}
_r = _shp.Reader(r'C:\Users\mcsha\Niagra\spatial\shp\select_roads.shp')
_flds = [f[0] for f in _r.fields[1:]]
for sh, rec in zip(_r.iterShapes(), _r.iterRecords()):
    d = dict(zip(_flds, rec))
    if d['MTFCC'] not in _CLS:
        continue
    lines = _seglines(sh)
    if lines:
        _seen.add(d['TLID']); road_feats.append(_mkfeat(lines, (d['FULLNAME'] or '').strip(), _CLS[d['MTFCC']]))
# named additions from full TIGER edges (all classes, matched by name)
_WHITELIST = {'Lasalle Expy': 'Highway', 'Military Rd': 'Arterial', 'N Military Rd': 'Arterial',
              'S Military Rd': 'Arterial', 'Packard Rd': 'Arterial', 'Porter Rd': 'Arterial',
              'Portage Rd': 'Arterial', 'Pine Ave': 'Arterial', 'Walnut Ave': 'Arterial', 'Ferry Ave': 'Arterial'}
_r2 = _shp.Reader(r'C:\Users\mcsha\Niagra\spatial\tl_2023_36063_edges_utm17n.shp')
_f2 = [f[0] for f in _r2.fields[1:]]
for sh, rec in zip(_r2.iterShapes(), _r2.iterRecords()):
    d = dict(zip(_f2, rec))
    fn = (d['FULLNAME'] or '').strip()
    if fn in _WHITELIST and d['TLID'] not in _seen:
        lines = _seglines(sh)
        if lines:
            _seen.add(d['TLID']); road_feats.append(_mkfeat(lines, fn, _WHITELIST[fn]))
with open(os.path.join(outdir, 'major_roads.geojson'), 'w') as f:
    json.dump({'type': 'FeatureCollection', 'features': road_feats}, f, separators=(',', ':'))
print(f'  {len(road_feats)} road segments written')

print('\nAll exports complete.')

# Report file sizes
for fn in ['hazard_sites.geojson','census_tracts.geojson','impact_zone.geojson','cancer_sir.geojson','major_roads.geojson']:
    path = os.path.join(outdir, fn)
    kb = os.path.getsize(path) / 1024
    print(f'  {fn}: {kb:.0f} KB')
