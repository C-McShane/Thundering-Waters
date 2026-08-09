"""Push georeferenced locations and boundaries from georef/sites/done into the dashboard data.

THE HARD RULE (see memory: do-not-override-existing-wells)

  Covanta, Love Canal, former Mill 2 and S-Area carry HAND-DERIVED well sets. The georef maps
  for those sites miss roughly 90% of the wells, so a georef push must never replace them. The
  merge is ADDITIVE ONLY: an existing location wins on coordinates, provenance is unioned, and
  `N_after >= N_before` is asserted per site at write time. The write aborts on violation --
  the assertion is what makes this safe, not the intention.

  Of the four protected sites only two are in this push: Covanta (C932160) and Mill 2.

MILL 2 IS NOT A NEW SITE. The `former_mill2` directory has no program number and duplicates
documents already filed under the real master row C932150 "Former Mill No. 2". Its locations
merge into C932150; it does not become a master row.

MATCH KEY IS (site, location_id) -- never the id alone. A dry run keyed on id alone paired
`MW3` at 624 River Road with a `MW3` at Love Canal 7.5 km away. Parentheses are preserved so
depth variants of one boring (`SB-03 (3')` vs `SB-03 (15')`) stay distinct.

OU# -> CONTAMINATED. `boundary_type == 'operable_unit'` is renamed to `contaminated`: these are
the Frontier "SOURCE AREA SOIL" polygons with depth ranges, which are contamination extents,
not administrative operable units.

  python push_georef.py --dry-run      # report only, writes nothing
  python push_georef.py                # writes, after backing up
"""
import argparse, csv, io, json, os, re, shutil, sys, time
from collections import Counter, defaultdict

NIAGRA = r"C:\Users\mcsha\Niagra"
DONE = os.path.join(NIAGRA, "georef", "sites", "done")
DATA = os.path.join(NIAGRA, "_deploy", "Thundering-Waters", "web", "data")
MASTER = os.path.join(NIAGRA, "csv", "Niagara_Hazard_Sites_MASTER.csv")
LOC_GJ = os.path.join(DATA, "georef_locations.geojson")
BND_GJ = os.path.join(DATA, "georef_boundaries.geojson")

# hand-derived well sets -- additive merge only, never replace
PROTECTED = {"Covanta-Niagara-Rail-to-Truck-Intermodal-Facility__C932160",
             "former_mill2", "Occidental-Love-Canal__932020", "S-Area"}
# directories that are not their own site
REMAP_SITE = {"former_mill2": ("Former-Mill-No-2__C932150", "C932150")}

STAMP = time.strftime("%Y%m%dT%H%M%S")


def backup(path):
    if os.path.exists(path):
        dst = f"{path}.bak-before-push-{STAMP}"
        shutil.copy2(path, dst)
        return dst
    return None


def pick_export(exp, kind):
    """Choose among re-pasted exports deliberately: prefer .corrected, then newest mtime.

    Sites have both `X_locations.csv` and `X_locations.corrected.csv`, and some carry a `(1)`
    suffix from a re-paste. Shipping the superseded file is silent and unrecoverable once the
    geojson is rebuilt, so the choice is logged per site.
    """
    cands = [f for f in os.listdir(exp) if f.endswith(".csv") and f"_{kind}" in f]
    if not cands:
        return None, []
    def rank(f):
        return (1 if ".corrected." in f else 0,
                os.path.getmtime(os.path.join(exp, f)))
    cands.sort(key=rank, reverse=True)
    return cands[0], cands


def read_csv(p):
    return list(csv.DictReader(io.open(p, encoding="utf-8-sig")))


def num(v):
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()

    print("=" * 96)
    print(f"GEOREF PUSH  {'(DRY RUN - nothing written)' if a.dry_run else ''}")
    print("=" * 96)

    # ---- existing deployed data -------------------------------------------------------------
    old_loc = json.load(io.open(LOC_GJ, encoding="utf-8"))["features"]
    old_bnd = json.load(io.open(BND_GJ, encoding="utf-8"))["features"]
    print(f"\ncurrently deployed: {len(old_loc)} locations, {len(old_bnd)} boundary vertices")

    # The deployed features are the BASE and every one of them is kept. An earlier version of
    # this script indexed them into a dict keyed on (site, location_id), which silently
    # collapsed duplicate ids already present in the deployed data -- NFSS went 645 -> 420. The
    # invariant caught it. Existing features are never deduplicated here; the key index is used
    # only to decide whether an incoming row is new.
    #
    # The deployed data also files Mill 2 under the directory name `former_mill2`, so existing
    # features are remapped to the canonical site too. Without that, the same 223 points would
    # be added a second time under the master name.
    for f in old_loc:
        d = f["properties"].get("site") or ""
        if d in REMAP_SITE:
            f["properties"]["site"] = REMAP_SITE[d][0]

    index = defaultdict(list)
    n_before = Counter()
    dup_existing = Counter()
    for f in old_loc:
        p = f["properties"]
        site = p.get("site") or ""
        lid = (p.get("location_id") or "").strip()
        n_before[site] += 1
        if index[(site, lid)]:
            dup_existing[site] += 1
        index[(site, lid)].append(f)

    if dup_existing:
        print("\n  NOTE: the deployed data already holds duplicate (site, location_id) pairs.")
        print("  They are preserved, not collapsed:")
        for s, n in dup_existing.most_common():
            print(f"    {n:5}  {s[:60]}")

    # ---- gather from done/ ------------------------------------------------------------------
    chosen, new_loc_rows, new_bnd_rows = {}, [], []
    for d in sorted(os.listdir(DONE)):
        exp = os.path.join(DONE, d, "exports")
        if not os.path.isdir(exp):
            continue
        lf, lall = pick_export(exp, "locations")
        bf, ball = pick_export(exp, "boundaries")
        chosen[d] = {"locations": lf, "boundaries": bf,
                     "loc_alts": [x for x in lall if x != lf],
                     "bnd_alts": [x for x in ball if x != bf]}
        if lf:
            for r in read_csv(os.path.join(exp, lf)):
                r["_dir"] = d
                new_loc_rows.append(r)
        if bf:
            for r in read_csv(os.path.join(exp, bf)):
                r["_dir"] = d
                new_bnd_rows.append(r)

    print("\n--- export files chosen ---")
    for d, c in sorted(chosen.items()):
        extra = ""
        if c["loc_alts"] or c["bnd_alts"]:
            extra = f"   (superseded: {', '.join(c['loc_alts'] + c['bnd_alts'])})"
        print(f"  {d[:48]:<49} {str(c['locations'])[:52]}{extra}")

    # ---- merge locations --------------------------------------------------------------------
    merged = list(old_loc)                 # every deployed feature survives, unconditionally
    added = Counter(); kept = Counter(); prov = Counter(); dup_new = Counter()
    seen_new = set()
    for r in new_loc_rows:
        d = r["_dir"]
        site, _ = REMAP_SITE.get(d, (d, None))
        lid = (r.get("location_id") or "").strip()
        if not lid:
            continue
        lat, lon = num(r.get("lat")), num(r.get("lon"))
        if lat is None or lon is None:
            continue
        key = (site, lid)
        props = {"site": site, "site_id": r.get("site_id") or "",
                 "location_id": lid, "measured": r.get("measured") or "",
                 "method": r.get("method") or "", "figure_style": r.get("figure_style") or "",
                 "fit_rms_m": r.get("fit_rms_m") or "", "loo_median_m": r.get("leave_one_out_median_m") or "",
                 "loo_max_m": r.get("leave_one_out_max_m") or "",
                 "n_control_points": r.get("n_control_points") or "",
                 "outside_hull": r.get("outside_hull") or "",
                 "outside_boundary_by_m": r.get("outside_boundary_by_m") or "",
                 "source_document": r.get("source_document") or "",
                 "source_page": r.get("source_page") or ""}
        if index.get(key):
            # EXISTING WINS on coordinates. Provenance is unioned so new pages are not lost.
            ex = index[key][0]["properties"]
            for fld in ("source_document", "source_page"):
                a_, b_ = str(ex.get(fld) or ""), str(props.get(fld) or "")
                parts = [x for x in dict.fromkeys(
                    [s.strip() for s in (a_ + " | " + b_).split("|")]) if x]
                if parts and " | ".join(parts) != a_:
                    ex[fld] = " | ".join(parts)
                    prov[site] += 1
            kept[site] += 1
        elif key in seen_new:
            # the incoming export itself repeats this id -- count it, add it once
            dup_new[site] += 1
        else:
            seen_new.add(key)
            feat = {"type": "Feature",
                    "geometry": {"type": "Point", "coordinates": [lon, lat]},
                    "properties": props}
            merged.append(feat)
            index[key].append(feat)
            added[site] += 1

    n_after = Counter()
    for f in merged:
        n_after[f["properties"].get("site") or ""] += 1
    if dup_new:
        print("\n  NOTE: incoming exports repeat some (site, location_id) pairs; "
              "added once each:")
        for s, n in dup_new.most_common():
            print(f"    {n:5}  {s[:60]}")

    print("\n--- locations merge, per site ---")
    print(f"  {'site':<52}{'before':>7}{'added':>7}{'matched':>9}{'after':>7}  protected")
    viol = []
    for site in sorted(set(list(n_before) + list(n_after))):
        b, af = n_before.get(site, 0), n_after.get(site, 0)
        prot = any(site == p or site.startswith(p.split("__")[0]) for p in PROTECTED) \
            or site == "Former-Mill-No-2__C932150"
        if af < b:
            viol.append((site, b, af))
        print(f"  {site[:50]:<52}{b:>7}{added.get(site,0):>7}{kept.get(site,0):>9}{af:>7}"
              f"  {'YES' if prot else ''}")
    print(f"\n  TOTAL  before {sum(n_before.values())}  ->  after {sum(n_after.values())}"
          f"   (+{sum(added.values())} new, {sum(kept.values())} matched, "
          f"{sum(prov.values())} provenance additions)")

    if viol:
        print("\n!! INVARIANT VIOLATED - N_after < N_before for:")
        for s, b, af in viol:
            print(f"     {s}: {b} -> {af}")
        print("   aborting, nothing written")
        return 1
    print("  invariant N_after >= N_before: OK for every site")

    # ---- boundaries, with OU# -> contaminated ------------------------------------------------
    # RINGS ARE DELIMITED BY vertex_seq RESTARTING, not by their name. Grouping on
    # (site, name, type, document, page) merged genuinely separate polygons into one and then
    # sorted their vertices together, which scrambled them: LOOW's five hazard areas
    # (14 + 4 + 6 ... vertices) became a single 36-vertex tangle, Carborundum's six became 33,
    # and 914 Tactical's two became 11. Each contiguous run of increasing vertex_seq is one
    # ring, and file order is preserved.
    bnd_feats = []
    renamed = 0
    ring_rows, cur, prev_key, prev_seq = [], [], None, None
    for r in new_bnd_rows:
        d = r["_dir"]
        site, _ = REMAP_SITE.get(d, (d, None))
        bt = (r.get("boundary_type") or "").strip()
        bn = (r.get("boundary_name") or "").strip()
        if bt == "operable_unit":
            bt = "contaminated"
            renamed += 1
        elif bt == "other" and re.search(r"contaminat", bn, re.I):
            # a free-text ring the tool recorded as `other` but NAMED "Contaminated" is the
            # same thing and must not sit in grey beside the magenta category
            bt = "contaminated"
            renamed += 1
        key = (site, bn, bt, r.get("source_document") or "", r.get("source_page") or "",
               r.get("figure_style") or "", r.get("fit_rms_m") or "",
               r.get("leave_one_out_median_m") or "", r.get("n_vertices") or "")
        seq = int(r.get("vertex_seq") or 0)
        if cur and (key != prev_key or seq <= prev_seq):
            ring_rows.append((prev_key, cur)); cur = []
        cur.append((seq, r))
        prev_key, prev_seq = key, seq
    if cur:
        ring_rows.append((prev_key, cur))

    mismatch = 0
    for k, rws in ring_rows:
        site, bn, bt, doc, page, style, rms, loo, nv_declared = k
        pts = []
        for _seq, r in rws:
            lat, lon = num(r.get("lat")), num(r.get("lon"))
            if lat is not None and lon is not None:
                pts.append([lon, lat])
        coords = list(pts)
        if len(coords) < 3:
            continue
        # the export states how many vertices the ring has; disagreeing means the split is wrong
        try:
            if nv_declared and int(nv_declared) != len(coords):
                mismatch += 1
        except ValueError:
            pass
        if coords[0] != coords[-1]:
            coords.append(coords[0])
        bnd_feats.append({
            "type": "Feature",
            "geometry": {"type": "Polygon", "coordinates": [coords]},
            "properties": {"site": site, "boundary_name": bn, "boundary_type": bt,
                           "n_vertices": len(coords) - 1, "figure_style": style,
                           "fit_rms_m": rms, "loo_median_m": loo, "source_page": page,
                           "source_document": doc}})

    print(f"\n--- boundaries ---")
    print(f"  rings whose vertex count disagrees with the exported n_vertices: {mismatch}")
    print(f"  {len(new_bnd_rows)} vertices -> {len(bnd_feats)} rings "
          f"(was {len(old_bnd)} features deployed)")
    print(f"  operable_unit -> contaminated: {renamed} vertices renamed")
    bt_count = Counter(f["properties"]["boundary_type"] for f in bnd_feats)
    print("  ring types now present:")
    for t, n in bt_count.most_common():
        print(f"    {n:5}  {t}")
    names = Counter(f["properties"]["boundary_name"] for f in bnd_feats
                    if f["properties"]["boundary_type"] == "other")
    if names:
        print("  free-text 'other' names (these become their own dashboard tags):")
        for t, n in names.most_common(12):
            print(f"    {n:5}  {t}")

    if a.dry_run:
        print("\nDRY RUN - nothing written.")
        return 0

    # ---- write ------------------------------------------------------------------------------
    for p in (LOC_GJ, BND_GJ):
        b = backup(p)
        print(f"\nbacked up {os.path.basename(p)} -> {os.path.basename(b)}")
    backup(MASTER)

    loc_out = {"type": "FeatureCollection", "features": merged}
    json.dump(loc_out, io.open(LOC_GJ, "w", encoding="utf-8"))
    json.dump({"type": "FeatureCollection", "features": bnd_feats},
              io.open(BND_GJ, "w", encoding="utf-8"))
    print(f"\nwrote {LOC_GJ}  ({len(loc_out['features'])} features)")
    print(f"wrote {BND_GJ}  ({len(bnd_feats)} features)")

    with io.open(os.path.join(DATA, "georef_push_log.txt"), "w", encoding="utf-8") as fh:
        fh.write(f"georef push {STAMP}\n")
        fh.write(f"locations {sum(n_before.values())} -> {sum(n_after.values())}\n")
        fh.write(f"boundaries {len(old_bnd)} -> {len(bnd_feats)} rings\n")
        fh.write(f"operable_unit renamed to contaminated: {renamed} vertices\n\n")
        for d, c in sorted(chosen.items()):
            fh.write(f"{d}: locations={c['locations']} boundaries={c['boundaries']}"
                     f" superseded={c['loc_alts'] + c['bnd_alts']}\n")
    print("wrote georef_push_log.txt")
    return 0


if __name__ == "__main__":
    sys.exit(main())
