#!/usr/bin/env python3
r"""build_site_document_links — give every site a verified link to its agency record.

Two links per site feed the popup:
  docs_url   the agency's document directory  ("Browse all NYSDEC documents for this site")
  website    the agency's site record          ("View official record")

**Every link is probed before it is published.** A dead link on a public map is worse than no
link, and the patterns are not universally valid: `932045` (CECOS) and `B00108` both return 404
from DecDocs despite being real sites.

The DEC record page at appfactory.dec.ny.gov cannot verify itself — it is a client-side app that
returns an identical 2,355-byte shell for any site code, valid or invented. So it is only emitted
for sites whose **DecDocs directory returned 200**, which independently proves DEC holds a record
under that code. That is the gate: one verifiable signal standing in for one that isn't.

Results are cached in csv/_site_link_probe_cache.json so re-runs cost nothing and a partial run
can be resumed.

Usage:
  python build_site_document_links.py --limit 20      # try a sample first
  python build_site_document_links.py
"""
from __future__ import annotations

import argparse
import io
import json
import os
import re
import shutil
import time
import urllib.error
import urllib.request

GEOJSON = r'C:\Users\mcsha\Niagra\web\data\hazard_sites.geojson'
REPORTS_JSON = r'C:\Users\mcsha\Niagra\csv\site_source_reports.json'
CACHE = r'C:\Users\mcsha\Niagra\csv\_site_link_probe_cache.json'
UA = {'User-Agent': 'Mozilla/5.0 (Thundering Waters research archival)'}

DECDOCS = 'https://extapps.dec.ny.gov/data/DecDocs/{code}/'
DECRECORD = ('https://appfactory.dec.ny.gov/DERExternalSearch/ERDDetails'
             '?CameFromList=false&SiteCode={code}')
# Site codes DEC issues: 6-digit hazardous-waste numbers, and the lettered
# Brownfield / ERP / Voluntary programmes.
DEC_CODE = re.compile(r'^(\d{6}[A-Z]?|[CEBV]\d{5,6}[A-Z]?)$')


def clean(v):
    s = '' if v is None else str(v).strip()
    return '' if s.lower() in ('', 'nan', 'none') else s


def probe(url, timeout=25):
    try:
        with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=timeout) as r:
            return r.status, len(r.read(2048))
    except urllib.error.HTTPError as e:
        return e.code, 0
    except Exception as e:
        return None, str(e)[:60]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--limit', type=int, default=0)
    ap.add_argument('--dry-run', action='store_true')
    args = ap.parse_args()

    feats = json.load(io.open(GEOJSON, encoding='utf-8'))['features']
    reports = json.load(io.open(REPORTS_JSON, encoding='utf-8'))
    cache = json.load(io.open(CACHE, encoding='utf-8')) if os.path.isfile(CACHE) else {}

    # One probe per distinct code, not per feature — codes repeat across operable units.
    codes = {}
    for f in feats:
        p = f['properties']
        pn = clean(p.get('program_number'))
        if not pn or not DEC_CODE.match(pn):
            continue
        has = clean(reports.get(pn, {}).get('docs_url')) if pn in reports else ''
        if has:
            continue
        codes.setdefault(pn, clean(p.get('site_name')) or '(unnamed)')

    todo = [c for c in sorted(codes) if c not in cache]
    if args.limit:
        todo = todo[:args.limit]
    print(f'DEC-coded sites needing a link: {len(codes)}   already probed: {len(codes) - len([c for c in codes if c not in cache])}')
    print(f'probing {len(todo)} codes\n')

    for i, code in enumerate(todo, 1):
        status, _ = probe(DECDOCS.format(code=code))
        cache[code] = {'decdocs_status': status, 'checked': time.strftime('%Y-%m-%d')}
        mark = 'OK  ' if status == 200 else f'{status} '
        print(f'  [{i}/{len(todo)}] {mark} {code:<10} {codes[code][:52]}', flush=True)
        time.sleep(0.7)
        if i % 25 == 0:
            json.dump(cache, io.open(CACHE, 'w', encoding='utf-8'), indent=1)

    json.dump(cache, io.open(CACHE, 'w', encoding='utf-8'), indent=1)

    live = [c for c in codes if cache.get(c, {}).get('decdocs_status') == 200]
    dead = [c for c in codes if c in cache and cache[c]['decdocs_status'] != 200]
    print(f'\nverified live: {len(live)}   no directory: {len(dead)}   unprobed: '
          f'{len(codes) - len(live) - len(dead)}')

    if args.dry_run:
        print('(dry run) nothing written')
        return

    added = 0
    for code in live:
        entry = reports.get(code) or {}
        entry.setdefault('reports', [])
        entry['docs_url'] = DECDOCS.format(code=code)
        entry['website'] = DECRECORD.format(code=code)
        reports[code] = entry
        added += 1
    if added:
        shutil.copy2(REPORTS_JSON, REPORTS_JSON + f'.bak-{time.strftime("%Y%m%dT%H%M%S")}')
        json.dump(reports, io.open(REPORTS_JSON, 'w', encoding='utf-8'), indent=1, ensure_ascii=False)
        print(f'wrote {added} verified document links to {os.path.basename(REPORTS_JSON)}')


if __name__ == '__main__':
    main()
