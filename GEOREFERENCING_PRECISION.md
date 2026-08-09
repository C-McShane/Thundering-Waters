# Georeferenced sampling locations: what these points are, and what they are not

## They are not surveyed coordinates

The sampling locations and area outlines on this map were **read off scanned figures in site
reports** — not surveyed, and not taken from a coordinate table. A person opened a figure,
clicked several features they could identify on both the figure and current aerial imagery
(building corners, road intersections, parcel corners), and the software fitted a transform from
those pairs. Every other symbol on the figure was then carried through that transform.

A surveyed coordinate is a measurement of the ground. These are an estimate of where a printed
symbol on a scanned page corresponds to on a map. The two should not be confused, and nothing
here should be used as though it were the former.

## Precision was not the objective of this pass

The purpose was to show, at map scale, **roughly where sampling happened and roughly what area a
report was describing** — so that a reader can see that a site has 200 sample points rather than
a single dot, and see approximately where they sit relative to a road, a school, or a property
line. It was not to establish the position of any individual well.

Where the project holds surveyed coordinates from report tables, those are used instead, and are
labelled as such. They are better evidence and should be preferred wherever they exist.

## What the numbers say

Each point carries its own error estimates, visible in its popup and in the downloadable data.
Across the 1,511 published locations:

| | median | upper quartile | worst |
|---|---|---|---|
| fit RMS (how well the control points themselves fit) | 5.2 m | 11.6 m | 92.8 m |
| leave-one-out error (a fairer estimate) | 9.1 m | 19.9 m | 255.3 m |

Per site, the leave-one-out median ranges from about **5 m** (624 River Road) to **20 m**
(Niagara Falls Storage Site) — and **132 m at Lake Ontario Ordnance Works**, where the figure
covers several thousand acres and a small angular error becomes a large distance on the ground.

Three further limits are worth stating plainly:

- **511 of the points fall outside the area enclosed by their control points.** A transform
  interpolates reliably between its control points; beyond them it extrapolates, and the error
  grows with distance in a way the summary figures above do not capture. These points are
  flagged `outside_hull` in the data.
- **Some figures were fitted from only two control points.** Two points determine a similarity
  transform exactly, which means there is no redundancy and therefore *no error estimate at all*
  — a fit RMS of zero on such a figure means nothing has been tested, not that the fit is
  perfect. The number of control points is recorded per point.
- **125 of the 1,511 points were clicked directly on the imagery; the rest were projected**
  through the transform. Directly-placed points and projected points are drawn differently on
  the map and are distinguished by the `measured` field.

Three published area outlines are self-intersecting — traced rings whose outline crosses itself.
They are flagged `geometry_valid = false` in the geopackage and have deliberately not been
auto-repaired, because an automatic repair would silently change a published outline.

## Any site can be redone properly

The point of publishing the exports and the scripts is that nobody has to take these positions
on trust.

Every location and every outline carries the **source document and page** it came from. The
control points used for each figure are exported alongside. Anyone with QGIS, ArcGIS or similar
can open the same figure, place their own control points, and produce a better-controlled result
for a site they care about — using a higher-order transform, more control points, or ground
control that we did not have.

If a specific site matters to your work and the precision here is insufficient, that is a
reasonable position, and we would rather redo it than have the current figures relied on. Ask,
via <https://github.com/C-McShane/Thundering-Waters/issues>, and we will run a precision pass on
that site — or you can run one yourself from the published material.

## Where this is documented

- `wells_module/GEOREF_DECISIONS.md` — the method, and the errors found in it along the way
- `web/push_georef.py` — how the exports become the published layers
- `CORRECTIONS.md` — errors found after publication, and how each was caught
- geopackage layers `Niagara_Georef_Sampling_Locations` and `Niagara_Georef_Boundaries`

Where this project differs from a cited primary source, the primary source governs.
