"""Write the deployed georef layers into the GeoPackage so the archive matches the map.

The georef work has only ever lived as GeoJSON under web/data. The gpkg -- which is the
analytical and archival artifact, the thing someone opens in QGIS -- had 23 layers and none of
them georef. So the map showed 1,511 sampling locations the geopackage did not contain.

Two layers are written, replacing any previous copy:

  Niagara_Georef_Sampling_Locations   points, one per located sample point
  Niagara_Georef_Boundaries           polygons, site outlines and area rings

Ring geometry is taken from the deployed GeoJSON rather than re-derived, so the gpkg cannot
drift from what is published.

  python georef_to_gpkg.py
"""
import io, json, os, shutil, time

import geopandas as gpd
from shapely.geometry import shape

NIAGRA = r"C:\Users\mcsha\Niagra"
DATA = os.path.join(NIAGRA, "_deploy", "Thundering-Waters", "web", "data")
GPKGS = [os.path.join(NIAGRA, "spatial", "Niagara_County_HazWaste.gpkg"),
         os.path.join(NIAGRA, "_deploy", "Thundering-Waters", "spatial_layers",
                      "Niagara_County_HazWaste.gpkg")]
STAMP = time.strftime("%Y%m%dT%H%M%S")


def load(name):
    gj = json.load(io.open(os.path.join(DATA, name), encoding="utf-8"))
    feats = gj["features"]
    rows = [f["properties"] | {"geometry": shape(f["geometry"])} for f in feats]
    return gpd.GeoDataFrame(rows, geometry="geometry", crs="EPSG:4326")


pts = load("georef_locations.geojson")
rings = load("georef_boundaries.geojson")
print(f"locations {len(pts)} features, {pts.site.nunique()} sites")
print(f"boundaries {len(rings)} rings")
print(rings.boundary_type.value_counts().to_string())

# Geometry sanity before it reaches the archive. Invalid here means self-intersecting -- a ring
# traced by hand whose outline crosses itself. The flag is RECORDED, not repaired: buffer(0)
# would silently change a published outline, and which of the two lobes is the real extent is a
# question for the person who traced it, not for this script.
rings["geometry_valid"] = rings.geometry.is_valid
bad = rings[~rings.geometry_valid]
print(f"\nself-intersecting rings: {len(bad)}  (flagged in `geometry_valid`, NOT repaired)")
for _, r in bad.iterrows():
    print(f"  {r['site'][:46]:<47} {r['boundary_name'][:22]:<23} "
          f"{r['n_vertices']} vertices  p{r['source_page']}")

import sqlite3

for g in GPKGS:
    if not os.path.exists(g):
        print(f"\nSKIP (missing) {g}")
        continue
    b = f"{g}.bak-before-georef-{STAMP}"
    shutil.copy2(g, b)
    pts.to_file(g, layer="Niagara_Georef_Sampling_Locations", driver="GPKG")
    rings.to_file(g, layer="Niagara_Georef_Boundaries", driver="GPKG")
    con = sqlite3.connect(g)
    n = con.execute("SELECT COUNT(*) FROM gpkg_contents").fetchone()[0]
    ln = con.execute("SELECT COUNT(*) FROM Niagara_Georef_Sampling_Locations").fetchone()[0]
    bn = con.execute("SELECT COUNT(*) FROM Niagara_Georef_Boundaries").fetchone()[0]
    con.close()
    print(f"\nwrote into {g}")
    print(f"  backup {os.path.basename(b)}")
    print(f"  layers now {n};  locations {ln}, boundaries {bn}")
