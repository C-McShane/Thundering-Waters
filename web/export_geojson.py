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
cur.execute('''SELECT geom, site_name, designation, program_type, program_category,
               area_acres_best, chemicals, narrative, website, address, city, zip,
               latitude, longitude, npl_status, non_npl_status
               FROM Niagara_County_Hazard_Sites''')
rows = cur.fetchall()
features = []
for r in rows:
    geom_blob = r[0]
    g = geom_to_geojson(geom_blob, 4326)
    # Truncate narrative for popup (full text kept for detail panel)
    narr = r[7] or ''
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
        }
    })

with open(os.path.join(outdir, 'hazard_sites.geojson'), 'w') as f:
    json.dump({'type': 'FeatureCollection', 'features': features}, f, separators=(',',':'))
print(f'  {len(features)} sites written')

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

# ── 3. IMPACT ZONE ─────────────────────────────────────────────────────────────
print('Exporting impact zone...')
cur.execute('''SELECT geom, GEOID, NAME, NAMELSAD, aland_acres,
               site_count, total_acres, coverage_pct
               FROM NiagaraFalls_Area_ImpactZone''')
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
        }
    })
with open(os.path.join(outdir, 'impact_zone.geojson'), 'w') as f:
    json.dump({'type': 'FeatureCollection', 'features': features}, f, separators=(',',':'))
print(f'  {len(features)} impact zone tracts written')

# ── 4. COUNTY BOUNDARY ─────────────────────────────────────────────────────────
print('Exporting county boundary...')
cur.execute('SELECT geom FROM Niagara_County_Boundary')
rows = cur.fetchall()
features = [{'type':'Feature','geometry':geom_to_geojson(r[0],26917),'properties':{}} for r in rows]
with open(os.path.join(outdir, 'county_boundary.geojson'), 'w') as f:
    json.dump({'type': 'FeatureCollection', 'features': features}, f, separators=(',',':'))
print(f'  {len(features)} boundary feature written')

con.close()

# ── 5. MAJOR ROADS (arterials + highways, from shapefile, reprojected) ──────────
print('Exporting major roads...')
import shapefile as _shp
roads_shp = r'C:\Users\mcsha\Niagra\spatial\shp\select_roads.shp'
_rtf = Transformer.from_crs('EPSG:26917', 'EPSG:4326', always_xy=True)
_CLS = {'S1100': 'Highway', 'S1200': 'Arterial'}
_r = _shp.Reader(roads_shp)
_flds = [f[0] for f in _r.fields[1:]]
road_feats = []
for sh, rec in zip(_r.iterShapes(), _r.iterRecords()):
    d = dict(zip(_flds, rec))
    if d['MTFCC'] not in _CLS:
        continue
    pts = sh.points; parts = list(sh.parts) + [len(pts)]
    lines = []
    for i in range(len(parts) - 1):
        seg = [[round(x, 6), round(y, 6)] for x, y in (_rtf.transform(px, py) for px, py in pts[parts[i]:parts[i+1]])]
        if len(seg) >= 2:
            lines.append(seg)
    if not lines:
        continue
    geom = {'type': 'LineString', 'coordinates': lines[0]} if len(lines) == 1 else {'type': 'MultiLineString', 'coordinates': lines}
    road_feats.append({'type': 'Feature', 'geometry': geom,
                       'properties': {'name': (d['FULLNAME'] or '').strip(), 'road_class': _CLS[d['MTFCC']]}})
with open(os.path.join(outdir, 'major_roads.geojson'), 'w') as f:
    json.dump({'type': 'FeatureCollection', 'features': road_feats}, f, separators=(',', ':'))
print(f'  {len(road_feats)} road segments written')

print('\nAll exports complete.')

# Report file sizes
for fn in ['hazard_sites.geojson','census_tracts.geojson','impact_zone.geojson','county_boundary.geojson']:
    path = os.path.join(outdir, fn)
    kb = os.path.getsize(path) / 1024
    print(f'  {fn}: {kb:.0f} KB')
