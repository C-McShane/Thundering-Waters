"""
build_site_roads.py — local-street context near the major regulated sites.

For every hazard site in the high-priority regulatory programmes (State Superfund,
FUSRAP-LM, RCRA Corrective Action, Federal NPL active/deleted, Federal CERCLA), find the
nearest 2-3 DISTINCT named local streets from the TIGER edge network, deduped against the
13 major arterials already labelled on the map. Output web/data/site_roads.geojson — a
zoom-gated wayfinding layer (shows at map zoom >= 16 when the Roads layer is on).

Reproducible: reads the master gpkg tiger_edges + web/data/hazard_sites.geojson.
Wayfinding context only — approximate nearest-road, no accuracy claim on the site itself.
"""
import geopandas as gpd, json
from shapely.geometry import shape

GPKG = 'spatial/Niagara_County_HazWaste.gpkg'
QUAL = {'NY State Superfund', 'FUSRAP-LM', 'RCRA Corrective Action', 'Federal NPL - Active',
        'Federal NPL - Deleted', 'Federal CERCLA (Non-NPL)', 'Federal CERCLA / Brownfield'}
MAXD = 400   # metres: only streets within this radius count as "near"
NPER = 3     # up to this many distinct named streets per site

major = {(f['properties'].get('name') or '').strip()
         for f in json.load(open('web/data/major_roads.geojson', encoding='utf-8'))['features']}
major.discard('')

roads = gpd.read_file(GPKG, layer='tiger_edges')
roads = roads[(roads['ROADFLG'] == 'Y') & roads['FULLNAME'].notna()
              & (roads['FULLNAME'].astype(str).str.strip() != '')].copy()
roads['nm'] = roads['FULLNAME'].astype(str).str.strip()
roads = roads[~roads['nm'].isin(major)].reset_index(drop=True)   # dedup vs arterials
sidx = roads.sindex

gj = json.load(open('web/data/hazard_sites.geojson', encoding='utf-8'))
qsites = [f for f in gj['features'] if f['properties'].get('designation') in QUAL]
gpts = gpd.GeoDataFrame(geometry=[shape(f['geometry']) for f in qsites],
                        crs='EPSG:4326').to_crs(roads.crs)   # 26917 (metres)

chosen = {}   # TLID -> (row index, anchor point in 26917 nearest the calling site)
for pt in gpts.geometry:
    cand = list(sidx.intersection(pt.buffer(MAXD).bounds))
    if not cand:
        continue
    sub = roads.iloc[cand]
    d = sub.geometry.distance(pt).sort_values()
    seen = set()
    for idx in d.index:
        if d[idx] > MAXD:
            break
        nm = roads.at[idx, 'nm']
        if nm in seen:
            continue
        seen.add(nm)
        tlid = roads.at[idx, 'TLID']
        if tlid not in chosen:                      # label anchored to the FIRST site that pulls it in
            seg = roads.at[idx, 'geometry']
            chosen[tlid] = (idx, seg.interpolate(seg.project(pt)))   # closest point on road to that site
        if len(seen) >= NPER:
            break

idxs = [v[0] for v in chosen.values()]
sel = roads.loc[idxs].to_crs(4326)
anchors = gpd.GeoSeries([v[1] for v in chosen.values()], crs=roads.crs).to_crs(4326)
feats = []
for (name, geom), anc in zip(zip(sel['nm'], sel.geometry), anchors):
    feats.append({"type": "Feature",
                  "geometry": json.loads(gpd.GeoSeries([geom], crs=4326).to_json())['features'][0]['geometry'],
                  "properties": {"name": name, "anchor": [round(anc.x, 6), round(anc.y, 6)]}})
json.dump({"type": "FeatureCollection", "features": feats},
          open('web/data/site_roads.geojson', 'w', encoding='utf-8'),
          ensure_ascii=False, separators=(',', ':'))
print(f"{len(feats)} segments, {len({f['properties']['name'] for f in feats})} distinct names")
