#!/usr/bin/env python3
r"""host_fusrap_docs — mirror the CITED FUSRAP documents into the repository.

Why only these: the federal hosts are the fragile ones. `lm.doe.gov` has already died outright
(DNS no longer resolves; DOE Legacy Management moved to energy.gov), `lrb.usace.army.mil` fails
certificate verification, and the FUDS portal needs a client cipher override to connect at all.
The five NFSS/FUSRAP sites depend on exactly the links most likely to rot.

Why not more: LOOW alone is 281 files / 541 MB in SOURCE, and Git history is permanent. Only
documents actually cited in a site popup are mirrored — two files, 2.3 MB total.

The agency URL stays the primary citation. The mirrored copy is added as a second, clearly
labelled "archived copy" link, so a reader always sees where the record really lives and still
has a working copy if the agency moves it again.

Usage:
  python host_fusrap_docs.py --dry-run
  python host_fusrap_docs.py
"""
from __future__ import annotations

import argparse
import hashlib
import io
import json
import os
import shutil
import ssl
import time
import urllib.request

REPO = r'C:\Users\mcsha\Niagra\_deploy\Thundering-Waters'
DEST_REL = 'docs/source_documents/fusrap'
PAGES = 'https://c-mcshane.github.io/Thundering-Waters/' + DEST_REL
REPORTS = r'C:\Users\mcsha\Niagra\csv\site_source_reports.json'
UA = {'User-Agent': 'Mozilla/5.0 (Thundering Waters archival)'}

# (agency url, filename, [site keys], title)
DOCS = [
    ('https://www.energy.gov/sites/default/files/2022-09/NiagaraFallsVPFactSheet.pdf',
     'DOE-LM_NFSS_Vicinity_Properties_Fact_Sheet_2022-09.pdf',
     ['NFSS-VP-H-PRIME', 'NFSS-VP-X', 'NFSS-ANOMALY-CC', 'NFSS-CENTRAL-DITCH'],
     'DOE Legacy Management fact sheet — NFSS Vicinity Properties (Sept 2022)'),
    ('https://usace.contentdm.oclc.org/utils/getfile/collection/p16021coll7/id/27306',
     'USACE_Niagara_Falls_Storage_Site_record.pdf',
     ['932023'],
     'USACE record — Niagara Falls Storage Site'),
]
# Balmer Road School has no program number; it is linked by name.
BY_NAME = {'Balmer Road School': 'DOE-LM_NFSS_Vicinity_Properties_Fact_Sheet_2022-09.pdf'}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--dry-run', action='store_true')
    args = ap.parse_args()

    dest = os.path.join(REPO, *DEST_REL.split('/'))
    ctx = ssl.create_default_context()
    ctx.set_ciphers('DEFAULT@SECLEVEL=1')   # usace/fuds need this; verification stays ON
    os.makedirs(dest, exist_ok=True)

    fetched = {}
    for url, fname, sites, title in DOCS:
        out = os.path.join(dest, fname)
        if os.path.isfile(out) and os.path.getsize(out) > 1024:
            data = open(out, 'rb').read()
            print(f'  already present  {len(data):>9,} B  {fname}')
        elif args.dry_run:
            print(f'  would fetch                {fname}  <- {url[:52]}')
            continue
        else:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA),
                                        timeout=60, context=ctx) as r:
                data = r.read()
            if not data[:5].startswith(b'%PDF'):
                print(f'  NOT A PDF, skipped         {fname}')
                continue
            open(out, 'wb').write(data)
            print(f'  fetched          {len(data):>9,} B  {fname}')
            time.sleep(1)
        fetched[fname] = {'sites': sites, 'title': title, 'url': url,
                          'sha256': hashlib.sha256(data).hexdigest(),
                          'bytes': len(data)}

    if args.dry_run:
        print('\n(dry run) nothing written')
        return

    d = json.load(io.open(REPORTS, encoding='utf-8'))
    for fname, meta in fetched.items():
        archived = {'title': meta['title'] + ' — archived copy',
                    'url': f'{PAGES}/{fname}'}
        for pn in meta['sites']:
            e = d.setdefault(pn, {'reports': []})
            e.setdefault('reports', [])
            if not any(r['url'] == archived['url'] for r in e['reports']):
                e['reports'].append(archived)
    for name, fname in BY_NAME.items():
        e = d.get('_inherited_by_name', {}).get(name)
        if e is not None:
            e.setdefault('reports', [])
            u = f'{PAGES}/{fname}'
            if not any(r['url'] == u for r in e['reports']):
                e['reports'].append({'title': fetched[fname]['title'] + ' — archived copy',
                                     'url': u})

    manifest = os.path.join(dest, 'MANIFEST.json')
    json.dump({'note': 'Mirrored because the agency hosts for these records have proven '
                       'unstable: lm.doe.gov no longer resolves and USACE links cannot be '
                       'verified. The agency URL remains the primary citation.',
               'documents': fetched}, io.open(manifest, 'w', encoding='utf-8'), indent=1)

    shutil.copy2(REPORTS, REPORTS + f'.bak-{time.strftime("%Y%m%dT%H%M%S")}')
    json.dump(d, io.open(REPORTS, 'w', encoding='utf-8'), indent=1, ensure_ascii=False)
    total = sum(m['bytes'] for m in fetched.values())
    print(f'\nmirrored {len(fetched)} documents, {total/1e6:.1f} MB -> {DEST_REL}')


if __name__ == '__main__':
    main()
