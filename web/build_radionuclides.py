"""
build_radionuclides.py — assemble the isotope-level radionuclide dataset for the Radiation tab.

Pulls per-well / per-soil radionuclide results (keyed by SPECIFIC radionuclide, not the
collapsed curated categories) from every source and writes web/data/radionuclides.json:
  - WQP raw parquet: Total Uranium (µg/L series), Radon-222, Tritium, Gross Alpha/Beta, K-40 (pCi/L)
  - NFSS 2009 validated csv: U-233/234, U-235/236, U-238, Th-228/230/232, Ra-226, Ra-228 (pCi/L)
  - NFSS ESP tech-memo series: Total Uranium (µg/L) + Radium-226 (pCi/L), 2011-2020
  - Mill No. 2 soil rad zones: gamma-survey slag (U/Th/Ra), no isotope values / no time series
  - Hazard sites: rad-tagged sites grouped by isotope (U/Th/Ra) and class (TENORM/FUSRAP/MED-AEC)
"""
import pandas as pd, json, os
os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # repo root

# radionuclide -> (parent group, unit)
RN = {
    'Total Uranium':   ('Uranium', 'µg/L'),
    'Uranium-233/234': ('Uranium', 'pCi/L'),
    'Uranium-235/236': ('Uranium', 'pCi/L'),
    'Uranium-238':     ('Uranium', 'pCi/L'),
    'Thorium-228':     ('Thorium', 'pCi/L'),
    'Thorium-230':     ('Thorium', 'pCi/L'),
    'Thorium-232':     ('Thorium', 'pCi/L'),
    'Radium-226':      ('Radium',  'pCi/L'),
    'Radium-228':      ('Radium',  'pCi/L'),
    'Radon-222':       ('Radon',   'pCi/L'),
    'Tritium':         ('Other',   'pCi/L'),
    'Gross Alpha':     ('Other',   'pCi/L'),
    'Gross Beta':      ('Other',   'pCi/L'),
    'Potassium-40':    ('Other',   'pCi/L'),
}
wells = {k: {'parent': v[0], 'unit': v[1], 'points': []} for k, v in RN.items()}

def add_point(rn, well_id, src, lat, lon, site, medium, year, val, detect):
    if lat is None or lon is None:
        return
    pts = wells[rn]['points']
    p = next((x for x in pts if x['well_id'] == well_id and x['src'] == src), None)
    if p is None:
        p = {'well_id': well_id, 'src': src, 'lat': round(lat, 6), 'lon': round(lon, 6),
             'site': site, 'medium': medium, 'series': {}}
        pts.append(p)
    y = str(int(year)); cur = p['series'].get(y)
    st = 'detect' if detect else 'nondetect'
    if cur is None or (detect and (cur[1] == 'nondetect' or (val or 0) > (cur[0] or 0))):
        p['series'][y] = [val, st]

# ---- coord lookups ----
def load_coords(path, key='well_id', site_field='site'):
    gj = json.load(open(path, encoding='utf-8'))
    d = {}
    for f in gj['features']:
        pr = f['properties']; lon, lat = f['geometry']['coordinates']
        d[pr.get(key)] = (lat, lon, pr.get(site_field) or pr.get('site_name') or pr.get('site_type'))
    return d
wqp_c = load_coords('web/data/wells_wqp.geojson', site_field='site_type')
leg_c = load_coords('web/data/wells_legacy.geojson', site_field='site')

# ---- 1) WQP parquet ----
WQP_MAP = {'Uranium': 'Total Uranium', 'Radon-222': 'Radon-222', 'Tritium': 'Tritium',
           'Alpha particle': 'Gross Alpha', 'Beta particle': 'Gross Beta', 'Potassium-40': 'Potassium-40'}
df = pd.read_parquet('csv/_wqp_raw_results_cache.parquet')
df['yr'] = pd.to_datetime(df['ActivityStartDate'], errors='coerce').dt.year
detcol = 'ResultDetectionConditionText' if 'ResultDetectionConditionText' in df.columns else None
for char, rn in WQP_MAP.items():
    sub = df[df['CharacteristicName'] == char]
    for _, r in sub.iterrows():
        wid = r['MonitoringLocationIdentifier']
        if wid not in wqp_c or pd.isna(r['yr']):
            continue
        lat, lon, site = wqp_c[wid]
        val = pd.to_numeric(r['ResultMeasureValue'], errors='coerce')
        nd = detcol and isinstance(r.get(detcol), str) and r[detcol].strip() != ''
        detect = (not nd) and pd.notna(val)
        add_point(rn, wid, 'WQP', lat, lon, site or 'Water Quality Portal', 'groundwater/surface water',
                  r['yr'], float(val) if pd.notna(val) else None, detect)

# ---- 2) NFSS 2009 validated csv ----
nf = pd.read_csv('csv/to_add/LOOW_NFSS_2009_monitoring_well_detections.csv', encoding='utf-8-sig')
nf = nf[nf['chemical_class'] == 'radionuclide']
for _, r in nf.iterrows():
    rn = str(r['analyte'])
    if rn not in wells:
        continue
    wid = r['well_id']; c = leg_c.get(wid)
    lat, lon, site = c if c else (None, None, 'Niagara Falls Storage Site')
    detect = 'detection' in str(r['detection_status'])
    add_point(rn, wid, 'LEGACY', lat, lon, site, 'groundwater', r['sample_year'],
              float(r['result_numeric']) if pd.notna(r['result_numeric']) else None, detect)

# ---- 3) NFSS ESP multi-year series ----
esp = json.load(open('spatial/nfss_radionuclide_timeseries.json', encoding='utf-8'))
ESP_MAP = {'Uranium': 'Total Uranium', 'Radium-226': 'Radium-226'}
for wid, analytes in esp.items():
    c = leg_c.get(wid)
    if not c:
        continue
    lat, lon, site = c
    for an, years in analytes.items():
        rn = ESP_MAP.get(an)
        if not rn:
            continue
        for y, (val, det) in years.items():
            add_point(rn, wid, 'LEGACY', lat, lon, site, 'groundwater', y, val, bool(det))

# ---- 4) Mill No. 2 soil rad zones (gamma slag, no isotope values) ----
soil = []
sz = json.load(open('web/data/soil_radzones.geojson', encoding='utf-8'))
for f in sz['features']:
    p = f['properties']; lon, lat = f['geometry']['coordinates']
    soil.append({'zone_id': p['zone_id'], 'lat': round(lat, 6), 'lon': round(lon, 6),
                 'site': p['site'], 'materials': ['Uranium', 'Thorium', 'Radium'],
                 'gamma_cpm': p.get('gamma_cpm'), 'medium': 'soil / fill (radioactive slag)',
                 'note': 'Gamma-survey delineation — no per-isotope concentrations or time series.'})

# ---- 5) Hazard sites by isotope + class ----
sites = {}
hs = json.load(open('web/data/hazard_sites.geojson', encoding='utf-8'))
ISO = {'U': 'Uranium', 'Th': 'Thorium', 'Ra': 'Radium'}
seen = set()
for f in hs['features']:
    p = f['properties']
    if not (p.get('rad_class') or p.get('rad_iso')):
        continue
    key = (p.get('site_name'), p.get('program_number'))
    if key in seen:
        continue
    seen.add(key)
    lon, lat = f['geometry']['coordinates']
    rec = {'site_name': p.get('site_name'), 'lat': round(lat, 6), 'lon': round(lon, 6),
           'rad_class': p.get('rad_class'), 'program_number': p.get('program_number'),
           'iso': p.get('rad_iso') or [], 'basis': p.get('rad_basis')}
    for i in (p.get('rad_iso') or []):
        sites.setdefault(ISO.get(i, i), []).append(rec)
    cls = p.get('rad_class')
    if cls:
        sites.setdefault(cls, []).append(rec)

# prune empty radionuclides + report
wells = {k: v for k, v in wells.items() if v['points']}
groups = {}
for k, v in wells.items():
    groups.setdefault(v['parent'], []).append(k)
out = {'wells': wells, 'soil': soil, 'sites': sites, 'groups': groups}
json.dump(out, open('web/data/radionuclides.json', 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
print("radionuclides with well/soil data:")
for k, v in wells.items():
    yrs = sorted({int(y) for p in v['points'] for y in p['series']})
    print(f"  {k:16} {len(v['points']):3} points  years {yrs[0] if yrs else '-'}-{yrs[-1] if yrs else '-'}  [{v['unit']}]")
print(f"\nsoil zones: {len(soil)} | hazard-site material keys: {sorted(sites)}")
print("site counts:", {k: len(v) for k, v in sites.items()})
