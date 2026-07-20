"""
build_statistics.py — emit web/data/statistics.json, the single source of truth for
every count shown in the interface and the README.

Run this after ANY change to web/data/*.geojson. Nothing in the UI or the docs should
hard-code a count; they read from statistics.json (or are checked against it).

    python web/build_statistics.py
"""
import json, os, datetime

os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # repo root
D = 'web/data'


def feats(fn):
    with open(os.path.join(D, fn), encoding='utf-8') as fh:
        return json.load(fh)['features']


hazard = feats('hazard_sites.geojson')
wqp, dec, legacy = feats('wells_wqp.geojson'), feats('wells_dec.geojson'), feats('wells_legacy.geojson')
piezo, pumps = feats('wells_lc_piezometers.geojson'), feats('wells_lc_pumps.geojson')
radzones, tracts = feats('soil_radzones.geojson'), feats('census_tracts.geojson')
cancer, roads = feats('cancer_sir.geojson'), feats('major_roads.geojson')

# hazard sites: curated `chems` array is what the chemical filter actually searches.
# The raw NYSDEC `chemicals` free-text field is a different (larger) population — reported
# separately so the two are never conflated again.
with_curated = [f for f in hazard if (f['properties'].get('chems') or [])]
with_rawtext = [f for f in hazard if str(f['properties'].get('chemicals') or '').strip() not in ('', 'nan', 'None')]
distinct_chems = sorted({c for f in hazard for c in (f['properties'].get('chems') or [])})

lc_wells = [f for f in dec if str(f['properties'].get('program_number')) == '932020']

# Cancer geography has three distinct counts and they are NOT interchangeable:
#   cancer_block_groups         — every 2010-vintage Niagara BG polygon we draw (incl. water/no-data)
#   cancer_block_groups_with_data — those carrying NYSDOH values
#   cancer_doh_regions          — DISTINCT NYSDOH reporting regions. NYSDOH merges small-population
#                                 BGs (<6 male or <6 female cases) into `DOH####` regions for privacy,
#                                 so several BGs can share one region's counts. ALWAYS aggregate by
#                                 doh_region, never by block group, or merged areas get double-counted.
cancer_with_data = [f for f in cancer if (f['properties'].get('exp_Lung') or 0) > 0]
cancer_merged = [f for f in cancer if f['properties'].get('merged_area')]
cancer_regions = {f['properties'].get('doh_region') for f in cancer if f['properties'].get('doh_region')}


# Per-cancer county figures. Aggregated by DISTINCT doh_region so privacy-merged block
# groups (which share one region's counts) are never double-counted.
CANCERS = ['Lung', 'Bladder', 'Esophagus', 'Oral', 'Brain', 'Mesothelioma']
seen_region = {}
for f in cancer:
    pr = f['properties']
    r = pr.get('doh_region')
    if r and r not in seen_region:
        seen_region[r] = pr
cancer_stats = {}
for c in CANCERS:
    obs = sum((p.get('obs_' + c) or 0) for p in seen_region.values())
    exp = sum((p.get('exp_' + c) or 0) for p in seen_region.values())
    hl_regions = sum(1 for p in seen_region.values() if p.get('hlarea_' + c) == 1)
    hl_bgs = sum(1 for f in cancer if f['properties'].get('hlarea_' + c) == 1)
    cancer_stats[c] = {
        'observed': round(obs), 'expected': round(exp, 1),
        'sir': round(obs / exp, 3) if exp else None,
        'highlighted_regions': hl_regions, 'highlighted_block_groups': hl_bgs,
    }


# Recency: when was each monitoring point last sampled? Stamped by web/build_recency.py.
# Points with no recorded date are their own category — never grouped with old or new.
_wells_all = wqp + dec + legacy
_yrs = [f['properties'].get('last_sampled') for f in _wells_all]
_dated = [y for y in _yrs if y]
recency = {
    'points_total':      len(_yrs),
    'points_dated':      len(_dated),
    'points_undated':    len(_yrs) - len(_dated),
    'earliest':          min(_dated) if _dated else None,
    'latest':            max(_dated) if _dated else None,
    'since_2020':        sum(1 for y in _dated if y >= 2020),
    'band_2020_plus':    sum(1 for y in _dated if y >= 2020),
    'band_2010_2019':    sum(1 for y in _dated if 2010 <= y <= 2019),
    'band_2000_2009':    sum(1 for y in _dated if 2000 <= y <= 2009),
    'band_pre_2000':     sum(1 for y in _dated if y < 2000),
}

counts = {
    'hazard_sites':                len(hazard),
    'hazard_sites_with_chemicals': len(with_curated),      # curated `chems` — matches the filter
    'hazard_sites_raw_chem_text':  len(with_rawtext),      # raw NYSDEC free-text — NOT the filter
    'distinct_curated_chemicals':  len(distinct_chems),
    'census_tracts':               len(tracts),
    'cancer_block_groups':         len(cancer),
    'cancer_block_groups_with_data': len(cancer_with_data),
    'cancer_doh_regions':          len(cancer_regions),
    'cancer_block_groups_merged':  len(cancer_merged),
    'major_road_names':            len({f['properties'].get('name') for f in roads if f['properties'].get('name')}),
    'wells_wqp':                   len(wqp),
    'wells_dec':                   len(dec),
    'wells_legacy':                len(legacy),
    'wells_total':                 len(wqp) + len(dec) + len(legacy),
    'lc_wells':                    len(lc_wells),
    'lc_piezometers':              len(piezo),
    'lc_pumps':                    len(pumps),
    'rad_zones':                   len(radzones),
}
# every point the ID search can resolve
counts['search_index_total'] = (counts['hazard_sites'] + counts['wells_total']
                                + counts['rad_zones'] + counts['lc_piezometers'] + counts['lc_pumps'])

out = {
    'generated_utc': datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'),
    'note': 'Generated by web/build_statistics.py — do not hand-edit. Re-run after any data change.',
    'counts': counts,
    'recency': recency,
    'cancer': cancer_stats,
    'distinct_curated_chemicals': distinct_chems,
}
with open(os.path.join(D, 'statistics.json'), 'w', encoding='utf-8') as fh:
    json.dump(out, fh, ensure_ascii=False, indent=1)

print('wrote web/data/statistics.json')
for k, v in counts.items():
    print(f'  {k:32} {v}')
