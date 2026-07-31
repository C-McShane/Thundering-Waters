#!/usr/bin/env python3
r"""chem_site_match — join mapped hazard sites to the chemistry pipeline's built sites.

Program numbers are NOT a sufficient key. Some mapped places never got a government
designation and carry no program_number at all; some program numbers sit on more than one
mapped feature; and the same place is often named differently on the map than in the build
(e.g. map "Love Canal" vs build "Occidental -Love Canal", map "Niagara Falls Air Reserve
Station" vs build "914 Tactical Airlift Group"). So the join uses three signals in order and
records which one fired, so every match can be audited:

    name     exact match on the normalised site name
    program  same program_number on both sides
    geo      within GEO_TIGHT_M of the build site's coordinates, nearest wins;
             GEO_LOOSE_M is allowed when the names also share a distinctive token

Build-site coordinates come from csv/Niagara_Hazard_Sites_MASTER.csv, which every built site
resolves to. Writes an audit CSV so the matches can be eyeballed.

Usage:  python chem_site_match.py [--audit <path>]
"""
from __future__ import annotations

import argparse
import csv
import json
import math
import os
import re

GEO = r'C:\Users\mcsha\Niagra\web\data\hazard_sites.geojson'
COVERAGE = r'E:\Thundering_Waters_Backup_2026-07-20\SOURCE\_COVERAGE_by_site.csv'
SUMMARY = r'E:\Thundering_Waters_Backup_2026-07-20\build_chem\_partial_summary\partial_site_summary.csv'
BUILD_CHEM = r'E:\Thundering_Waters_Backup_2026-07-20\build_chem'
MASTER = r'C:\Users\mcsha\Niagra\csv\Niagara_Hazard_Sites_MASTER.csv'
EXCLUDED_BUILD_DIRS = {'former_mill2'}
DEFAULT_AUDIT = r'C:\Users\mcsha\Niagra\csv\chem_site_match_audit.csv'

GEO_TIGHT_M = 150.0   # unambiguous on position alone
GEO_LOOSE_M = 900.0   # allowed only when a distinctive name token also agrees

# Tokens too common in Niagara County site names to count as agreement on their own.
STOPWORDS = {
    'site', 'sites', 'the', 'of', 'and', 'co', 'inc', 'corp', 'corporation', 'company',
    'plant', 'landfill', 'street', 'st', 'road', 'rd', 'avenue', 'ave', 'drive', 'dr',
    'north', 'south', 'east', 'west', 'former', 'area', 'property', 'niagara', 'falls',
    'new', 'york', 'county', 'city', 'town', 'chemical', 'chemicals', 'llc', 'div',
    'division', 'no', 'number', 'building', 'bldg', 'lot', 'parcel', 'works', 'facility',
}


def nkey(s):
    return re.sub(r'[^a-z0-9]+', ' ', (s or '').lower()).strip()


def tightkey(s):
    """Punctuation- and space-free form, so "Ni-Mo" and "NiMo" collapse together."""
    return re.sub(r'[^a-z0-9]+', '', (s or '').lower())


def tokens(s):
    return {t for t in nkey(s).split() if t and t not in STOPWORDS and not t.isdigit()}


def clean_pn(v):
    s = '' if v is None else str(v).strip()
    return '' if s.lower() in ('', 'nan', 'none') else s


def haversine_m(lat1, lon1, lat2, lon2):
    r = 6371000.0
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp = math.radians(lat2 - lat1)
    dl = math.radians(lon2 - lon1)
    a = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * r * math.asin(math.sqrt(a))


def build_dir_index():
    """Index the per-site chemistry output folders by program number and by name slug.

    `former_mill2` is skipped on purpose: it carries a DO_NOT_INTEGRATE note because its site
    identity could not be resolved, so its rows must not be attached to any mapped site.
    """
    dirs = [d for d in os.listdir(BUILD_CHEM)
            if os.path.isdir(os.path.join(BUILD_CHEM, d)) and not d.startswith('_')
            and d not in EXCLUDED_BUILD_DIRS]
    by_pn, by_slug = {}, {}
    for d in dirs:
        name, _, pn = d.rpartition('__')
        if not name:
            name, pn = d, ''
        if pn:
            by_pn.setdefault(pn, d)
        by_slug.setdefault(tightkey(name), d)
    return by_pn, by_slug


def load_build_sites():
    """Every built site, with the coordinates its master-CSV row carries.

    A site collects every name it is known by — the coverage list, the rollup summary and the
    master row's alt_name — because the map routinely uses a different one than the build does.
    """
    master = list(csv.DictReader(open(MASTER, encoding='utf-8-sig')))
    by_name, by_pn = {}, {}
    for m in master:
        by_name.setdefault(nkey(m.get('site_name')), m)
        pn = clean_pn(m.get('program_number'))
        if pn:
            by_pn.setdefault(pn, m)

    # The rollup summary names each built site the way its own documents do.
    rollup_names = {}
    try:
        for r in csv.DictReader(open(SUMMARY, encoding='utf-8-sig')):
            key = (r.get('site') or '').strip()
            nm = (r.get('site_name') or '').strip()
            if key and nm:
                rollup_names[key] = nm
    except OSError:
        pass

    dirs_by_pn, dirs_by_slug = build_dir_index()

    sites = []
    for c in csv.DictReader(open(COVERAGE, encoding='utf-8-sig')):
        name = (c.get('site_name') or '').strip()
        pn = clean_pn(c.get('program_number'))
        m = by_name.get(nkey(name)) or by_pn.get(pn)
        lat = lon = None
        if m:
            try:
                lat = float(m['latitude'])
                lon = float(m['longitude'])
            except (TypeError, ValueError, KeyError):
                pass

        aliases = set()
        if m and (m.get('alt_name') or '').strip():
            aliases.add(m['alt_name'].strip())
        if pn:
            for key, nm in rollup_names.items():
                if key.endswith('__' + pn):
                    aliases.add(nm)
        aliases.discard(name)

        toks = tokens(name)
        for a in aliases:
            toks |= tokens(a)
        build_dir = dirs_by_pn.get(pn) if pn else None
        if not build_dir:
            build_dir = dirs_by_slug.get(tightkey(name))

        sites.append({
            'name': name, 'pn': pn, 'lat': lat, 'lon': lon, 'dir': build_dir,
            'nkeys': {nkey(name)}, 'tightkeys': {tightkey(name)},
            'alias_nkeys': {nkey(a) for a in aliases},
            'alias_tightkeys': {tightkey(a) for a in aliases},
            'tokens': toks,
        })
    return sites


def match(features=None, build_sites=None):
    """Return {feature_index: build_site_dict|None} plus the rule that matched."""
    if features is None:
        features = json.load(open(GEO, encoding='utf-8'))['features']
    if build_sites is None:
        build_sites = load_build_sites()

    # Five normalised names are shared by two build sites each (Tract II Highland Ave,
    # Whirlpool Rapids Bridge, U.S. Airforce Plant 68, Power Authority Road Site, and
    # La Salle Expressway's alt_name colliding with Robert Moses Parkway). Only the program
    # number separates those, so an exact program number wins when both sides carry one.
    # Aliases are indexed separately and never allowed to shadow another site's real name.
    by_pn, by_nkey, by_tight = {}, {}, {}
    for b in build_sites:
        if b['pn']:
            by_pn.setdefault(b['pn'], b)
        for k in b['nkeys']:
            by_nkey.setdefault(k, b)
        for k in b['tightkeys']:
            by_tight.setdefault(k, b)
    by_alias, by_alias_tight = {}, {}
    for b in build_sites:
        for k in b['alias_nkeys']:
            if k not in by_nkey:
                by_alias.setdefault(k, b)
        for k in b['alias_tightkeys']:
            if k not in by_tight:
                by_alias_tight.setdefault(k, b)

    out = {}
    for i, f in enumerate(features):
        p = f['properties']
        name = p.get('site_name')
        pn = clean_pn(p.get('program_number'))

        b = by_pn.get(pn) if pn else None
        if b:
            out[i] = (b, 'program', 0.0)
            continue

        b = by_nkey.get(nkey(name)) or by_tight.get(tightkey(name))
        if b:
            out[i] = (b, 'name', 0.0)
            continue

        b = by_alias.get(nkey(name)) or by_alias_tight.get(tightkey(name))
        if b:
            out[i] = (b, 'alias', 0.0)
            continue

        try:
            lat, lon = float(p['lat']), float(p['lon'])
        except (TypeError, ValueError, KeyError):
            out[i] = (None, 'none', None)
            continue

        # Rank every build site in range: strongest name agreement first, then nearest.
        # Taking the single closest point alone mis-assigns dense clusters like Buffalo Ave.
        toks = tokens(name)
        cands = []
        for b in build_sites:
            if b['lat'] is None:
                continue
            d = haversine_m(lat, lon, b['lat'], b['lon'])
            if d <= GEO_LOOSE_M:
                cands.append((len(toks & b['tokens']), -d, b, d))
        if not cands:
            out[i] = (None, 'none', None)
            continue

        cands.sort(reverse=True)
        overlap, _, b, d = cands[0]
        if overlap:
            out[i] = (b, 'geo' if d <= GEO_TIGHT_M else 'geo+name', d)
        elif d <= GEO_TIGHT_M:
            out[i] = (b, 'geo', d)
        else:
            out[i] = (None, 'none', d)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--audit', default=DEFAULT_AUDIT)
    args = ap.parse_args()

    features = json.load(open(GEO, encoding='utf-8'))['features']
    build_sites = load_build_sites()
    m = match(features, build_sites)

    rules = {}
    rows = []
    for i, f in enumerate(features):
        p = f['properties']
        b, rule, dist = m[i]
        rules[rule] = rules.get(rule, 0) + 1
        rows.append({
            'map_site_name': p.get('site_name'),
            'map_program_number': clean_pn(p.get('program_number')),
            'map_lat': p.get('lat'), 'map_lon': p.get('lon'),
            'matched_build_site': b['name'] if b else '',
            'matched_build_pn': b['pn'] if b else '',
            'matched_build_dir': (b.get('dir') or '') if b else '',
            'rule': rule,
            'distance_m': '' if dist is None else round(dist, 1),
            'chemicals_shown_today': len(p.get('chems') or []),
        })

    os.makedirs(os.path.dirname(args.audit), exist_ok=True)
    with open(args.audit, 'w', newline='', encoding='utf-8-sig') as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)

    matched = sum(1 for i in m if m[i][0])
    used = {b['name'] for b, _, _ in m.values() if b}
    print(f'map features        {len(features)}')
    print(f'build sites         {len(build_sites)}')
    print(f'matched             {matched}   ({len(features) - matched} unmatched)')
    print(f'build sites reached {len(used)}   ({len(build_sites) - len(used)} never matched)')
    for r, n in sorted(rules.items(), key=lambda kv: -kv[1]):
        print(f'  by {r:<9} {n}')
    print(f'wrote {args.audit}')


if __name__ == '__main__':
    main()
