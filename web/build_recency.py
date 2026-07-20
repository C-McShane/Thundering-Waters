"""
build_recency.py — stamp a normalised `last_sampled` year onto every monitoring point.

Recency was previously only discoverable by opening a popup, which let a reader treat a 1969
reading and a 2024 reading as equivalent. This writes one canonical field so the map can encode
"how long ago was this last sampled" visually, and so anyone downloading the geojson gets it too.

`last_sampled` is the most recent year found across, in order of reliability:
  conc_series / chems_years  (an actual dated result)
  latest_detect              (most recent detection)
  latest_year / year         (most recent sampling event)

Points with no date at all get `last_sampled: null` and are treated as a distinct
"date not recorded" category — never silently grouped with old or new points.

    python web/build_recency.py
"""
import json, os

os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # repo root
D = 'web/data'
FILES = ['wells_legacy.geojson', 'wells_dec.geojson', 'wells_wqp.geojson']


def derive(p):
    years = set()
    for ser in (p.get('conc_series') or {}).values():
        for y in ser:
            try: years.add(int(y))
            except (TypeError, ValueError): pass
    for yy in (p.get('chems_years') or {}).values():
        for y in (yy or []):
            try: years.add(int(y))
            except (TypeError, ValueError): pass
    for k in ('latest_detect', 'latest_year', 'year'):
        v = p.get(k)
        if v not in (None, ''):
            try: years.add(int(v))
            except (TypeError, ValueError): pass
    years = {y for y in years if 1900 < y <= 2100}
    return max(years) if years else None


total = dated = 0
spread = {}
for fn in FILES:
    path = os.path.join(D, fn)
    with open(path, encoding='utf-8') as fh:
        gj = json.load(fh)
    n = d = 0
    for f in gj['features']:
        p = f['properties']
        y = derive(p)
        p['last_sampled'] = y
        n += 1
        if y:
            d += 1
            spread[y] = spread.get(y, 0) + 1
    with open(path, 'w', encoding='utf-8') as fh:
        json.dump(gj, fh, ensure_ascii=False, separators=(',', ':'))
    total += n; dated += d
    print('%-28s %3d points | %3d dated | %2d without a date' % (fn, n, d, n - d))

print('\ntotal %d points | %d dated (%.0f%%) | %d date not recorded'
      % (total, dated, 100.0 * dated / total, total - dated))
if spread:
    ys = sorted(spread)
    print('range %d–%d' % (ys[0], ys[-1]))
    bands = [('2020 or later', lambda y: y >= 2020),
             ('2010–2019',     lambda y: 2010 <= y <= 2019),
             ('2000–2009',     lambda y: 2000 <= y <= 2009),
             ('before 2000',   lambda y: y < 2000)]
    for label, test in bands:
        print('  %-14s %4d points' % (label, sum(c for y, c in spread.items() if test(y))))
