#!/usr/bin/env python3
r"""add_radiological_gpkg — add the radiological sites as point features to the GeoPackage.

The GeoPackage and the master CSV are PARALLEL artifacts — no script derives one from the
other, and `web/export_geojson.py` reads the GeoPackage, so a CSV row alone never reaches the
map. Tagging a program number in the radiological classifier without a matching gpkg feature is
a silent no-op.

GeoPackage RTree triggers call ST_IsEmpty / ST_MinX and friends, which plain sqlite3 does not
provide, so no-op Python functions are registered before any write or the insert fails. The
triggers are never dropped — Python autocommits DDL and losing them would corrupt the index.

Usage:
  python add_radiological_gpkg.py --dry-run
  python add_radiological_gpkg.py
"""
from __future__ import annotations

import argparse
import csv
import io
import os
import shutil
import sqlite3
import struct
import time

GPKG = r'C:\Users\mcsha\Niagra\spatial\Niagara_County_HazWaste.gpkg'
TABLE = 'Niagara_County_Hazard_Sites'
MASTER = r'C:\Users\mcsha\Niagra\csv\Niagara_Hazard_Sites_MASTER.csv'
ADDED = ['EPA-NYN000206699', 'EPA-NYN000206697', 'EPA-NYN000203537',
         'EPA-NYN000206698', 'EPA-NYN000204317']


def gpkg_point(lon, lat, srs_id=4326):
    """GeoPackage BLOB for a 2D point: magic, version, flags, srs_id, then WKB."""
    header = b'GP' + bytes([0]) + bytes([1]) + struct.pack('<i', srs_id)
    wkb = bytes([1]) + struct.pack('<I', 1) + struct.pack('<dd', lon, lat)
    return header + wkb


def register_noops(con):
    """RTree triggers call these; plain sqlite3 has no spatial functions."""
    for name, argc in (('ST_IsEmpty', 1), ('ST_MinX', 1), ('ST_MaxX', 1),
                       ('ST_MinY', 1), ('ST_MaxY', 1)):
        con.create_function(name, argc, lambda *a: None)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--gpkg', default=GPKG)
    ap.add_argument('--dry-run', action='store_true')
    args = ap.parse_args()

    master = {r['program_number'].strip(): r
              for r in csv.DictReader(io.open(MASTER, encoding='utf-8-sig'))}

    con = sqlite3.connect(args.gpkg)
    register_noops(con)
    cur = con.cursor()
    cols = [r[1] for r in cur.execute(f'PRAGMA table_info({TABLE})')]
    pk = cols[0]
    have = {(r[0] or '').strip() for r in cur.execute(f'SELECT program_number FROM {TABLE}')}
    n_before = cur.execute(f'SELECT COUNT(*) FROM {TABLE}').fetchone()[0]
    print(f'{TABLE}: {n_before} features, {len(cols)} columns, pk={pk}')

    todo = [p for p in ADDED if p not in have]
    for p in ADDED:
        if p in have:
            print(f'  SKIP {p} — already a feature')
    if not todo:
        con.close()
        return

    inserts = []
    for pn in todo:
        m = master.get(pn)
        if not m:
            print(f'  MISSING from master: {pn}')
            continue
        lat, lon = float(m['latitude']), float(m['longitude'])
        vals = {'geom': gpkg_point(lon, lat)}
        for c in cols:
            if c in (pk, 'geom'):
                continue
            v = (m.get(c) or '').strip()
            vals[c] = v or None
        # area_acres_best is numeric in the gpkg; keep types clean
        for numcol in ('area_acres_best', 'latitude', 'longitude'):
            if numcol in vals and vals[numcol] not in (None, ''):
                try:
                    vals[numcol] = float(vals[numcol])
                except ValueError:
                    vals[numcol] = None
        inserts.append((pn, vals, lat, lon))
        print(f'  ADD  {pn:<20} {(m.get("site_name") or "")[:44]:<44} {lat:.6f},{lon:.6f}')

    if args.dry_run:
        print(f'\n(dry run) would insert {len(inserts)} features')
        con.close()
        return

    con.close()
    backup = args.gpkg + f'.bak-{time.strftime("%Y%m%dT%H%M%S")}'
    shutil.copy2(args.gpkg, backup)
    print(f'\nbackup: {os.path.basename(backup)}')

    con = sqlite3.connect(args.gpkg)
    register_noops(con)
    cur = con.cursor()
    for pn, vals, lat, lon in inserts:
        keys = [k for k in vals]
        collist = ','.join('"' + k + '"' for k in keys)
        placeholders = ','.join('?' for _ in keys)
        cur.execute(f'INSERT INTO {TABLE} ({collist}) VALUES ({placeholders})',
                    [vals[k] for k in keys])
    con.commit()
    n_after = cur.execute(f'SELECT COUNT(*) FROM {TABLE}').fetchone()[0]
    print(f'features: {n_before} -> {n_after}')
    con.close()


if __name__ == '__main__':
    main()
