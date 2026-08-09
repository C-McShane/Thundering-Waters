# Georeferencing module — decisions, methods and measured results

Companion to `DECISIONS.md` (the wells module). Everything here is about turning a sampling
location's position on a PDF figure into a real coordinate. Written 2026-08-04.

Every claim with a number was measured, and the measurement is named. Where something is
assumed rather than measured, it says so.

---

## G1. The problem, and what the transform is actually for

A sampling location is known by the **label printed on a figure**. To place it on the map we
need a transform from figure position to real-world coordinate. Its job is to place the
locations that are **not** otherwise known — 846 of them on the surveyed sites alone.

That single fact decides several things below, most importantly G7.

## G2. Ground truth: survey tables in the reports

Some reports contain `Site ID / Northing / Easting` tables. These are exact and need no
georeferencing at all; they also provide the control to check figure-derived coordinates
against.

- `find_survey_tables.py` scans page text for a coordinate header + survey-magnitude numbers +
  sampling identifiers. **7,084 PDFs in ~70 min → 254 candidate pages on 34 sites.**
- `extract_survey_coords.py` parses and projects them. **810 locations on 13 sites; 738 (91%)
  were independently found by the wells module.**

**Projection is EPSG:2262 — NAD83 / New York West, US survey FEET.** Verified by landing inside
a hand-drawn site boundary, not assumed. 2823 / 2260 / 32116 / 32117 all put the wells in
Quebec or Massachusetts; the metre variants fail. All of Niagara County is in the West zone.

**Column order varies between reports** — NFSS prints `Northing Easting`, Carborundum prints
`Easting Northing`, and both are 7-digit values in overlapping ranges so magnitude cannot
disambiguate. Order is read from the page header and then **self-validated**: whichever reading
lands inside the Niagara County bbox wins; a row failing both ways is rejected, not published.
Getting this wrong silently cost 3 sites and ~160 wells before it was caught.

## G3. Transform model: 4-DOF similarity, reflection allowed

Measured on 53 surveyed labels on `NFSS_03.10_0048_a.pdf` p54:

| model | held-out median | 90th pct |
|---|--:|--:|
| **similarity (4-DOF)** | **7.4 m** | 39.6 m |
| affine (6-DOF) | 9.8 m | 47.8 m |

Similarity also leaves shear as a *detectable error signal* instead of a free parameter that
absorbs bad control. **Reflection must be permitted**: pdfplumber's `top` grows downward while
ENU north grows upward, so the true map has negative determinant. A similarity parameterised
`[[a,-b],[b,a]]` cannot express it and reports garbage (316 m) while affine silently succeeds.

## G4. Accuracy actually achieved

With consensus fitting on the same 53 points: **52/53 inliers within 12 m, inlier RMS 6.0 m,
held-out median 6.9 m, 90th percentile 14.1 m.** The entire error tail was ONE mismatched label
(410 m). Recovered scale ≈ 1 inch = 150 ft, a standard engineering scale — an independent
sanity check that the fit is physically real.

Across 66 auto-registrations: **leave-one-out median 4.8 m, worst 8.3 m.**

Accuracy is always reported as **leave-one-out**, never fit residual. A residual computed on
the same points used to fit understates error badly when control is sparse.

## G5. A consensus fit is required, not optional

Least squares spreads one bad control point across every residual. Measured: a point displaced
300 m produced **134 m on itself against a 77 m median** — no ratio test can separate those.

So: two points determine a similarity exactly, therefore every pair is tried and the pair whose
transform the most other points agree with (≤12 m) wins. Exhaustive, not random.

**Accepting a registration also requires the consensus to be broad** — ≥5 inliers AND ≥60% of
available control. On several NFSS pages the fit kept 3 control points and discarded 45, then
reported a *small* leave-one-out error, because with three points leaving one out leaves two,
which determine a similarity exactly and can never disagree. Low error on a hand-picked subset
is evidence the subset was chosen to agree, not evidence of a good registration. This rule cut
accepted registrations from 24 to 12 on the first site — and accuracy improved.

## G6. Insets get their own transform

Site plans carry blown-up detail boxes drawn at their own scale and origin. On p54, **5 frames
hold 108 of 484 labels (22%)**. Projecting those with the main transform puts them in the wrong
place silently. Detected from PDF rectangles (≥120 pt, <40% of the sheet, ≥4 labels); innermost
containing frame wins.

**The same identifier often appears twice** — once on the main map, once in the detail. Label
tokens therefore carry a `tid` and are keyed by it; keying by label text silently kept whichever
copy came last.

## G7. Control points are fitted at LABEL positions, deliberately

A printed label sits beside its symbol, not on it — about 6 m on p54, roughly one label width,
and bimodally left/right. It is tempting to correct control points onto their symbols. **It
makes the output worse**, measured by projecting held-out labels:

| fit on | held-out median | 90th pct |
|---|--:|--:|
| label positions | **6.41 m** | 11.41 m |
| corrected symbol positions | 8.07 m | 17.24 m |

Because the transform must place labels whose symbols are unknown (see G1), fitting label
positions against surveyed wells absorbs the average offset. Correcting the control removes that
absorption and hands every projected label its full offset.

**The label-to-symbol offset is therefore the accuracy floor (~6 m) and is not removable**
without detecting symbols for every label. It is recorded in exports, never applied to the fit.

## G8. Nothing is auto-accepted

Every automatic registration is written `pending_verification` however good its residuals look.
A clean fit proves the control agrees with itself, never that the right label was matched to the
right symbol. Verification is a human pass; the figure verdict is the gate downstream filters on.

## G9. Two paths, and the current split

- **Surveyed** — survey table seeds the control; the human verifies. `auto_register.py` →
  `build_verification_queue.py`. **66 figure-regions across 4 sites** (of 13 sites with tables —
  the other 9 had no identifier overlap between their tables and their figures).
- **Non-surveyed** — no control exists; the human places it. `build_placement_queue.py`.
  **93 sites, one figure each, 7,177 locations.** Two control points minimum; more improve it.

Figures are chosen by **greedy coverage per site** — repeatedly take the sheet carrying the most
locations not yet covered — because annual reports reprint the same site plan for years.
2,402 non-surveyed figures reduce to ~538 for full coverage, or 93 for the best sheet per site.

**31 sites have sampling locations but no map citation at all** and cannot be georeferenced this
way; they need a different source or a site-centroid fallback with an explicit precision tier.

## G10. Scale can be read off the sheet (partial)

`extract_figure_scale.py` recovers metres-per-point from a printed ratio ("1 inch = 300 feet",
"SCALE 1:2400") or a graphic scale bar. **Validated against 39 survey-fitted transforms: 13
figures yielded a scale, ALL within 5%, median |error| 2.3%, worst 3.0%.**

Errors are consistently **positive (+2.4% to +3.0%)** — sheets were plotted slightly under
nominal, so a measured bar beats the printed ratio. The bar detector did not fire on these
sheets and needs work; hit rate is only 13/39 (33%). Scale is used as an **independent
cross-check** on placed points, not as a substitute for them.

## G11. Coordinates are a derived view, never a stored column

Following the `georef-bench.html` schema: `figure_transform` / `control_point` /
`detected_symbol`, with coordinates computed from the transform. A registration that is later
corrected improves every location derived from it, with no re-entry.

Control points are stored in **native PDF points with y flipped north-up** — never display
pixels, which would be invalidated the first time a figure is re-rendered at a different
resolution.

## G12. Polygons

Traced on the drawing and projected, because parcels-inside-parcels — a disposal cell, a survey
unit, a radon flux area — are boundaries the engineering sheet defines and aerial imagery does
not show. Vertices stored in PDF points, so they survive a re-render and improve if the
transform is refined. Exported in the same format as the hand-built
`validated/Niagara-Falls-Storage-Site__932023/Boundary_Polygon.txt`:
`name= {[lat, lon, …]}` with CRLF.

---

## Scripts (all in `scripts/wells_module/` on E:, mirrored from `C:\Users\mcsha\Niagra\wells_module`)

| script | does |
|---|---|
| `find_survey_tables.py` | scans every PDF for coordinate-table pages |
| `extract_survey_coords.py` | parses + projects them → `csv/surveyed_well_coordinates.csv` |
| `auto_register.py` | registers cited figures from survey control, per region |
| `make_georef_case.py` | renders a figure + emits label positions and inset frames |
| `build_georef_tool.py` | writes the two-pane HTML (verification or placement mode) |
| `build_verification_queue.py` | pages + index for auto-registered figures |
| `build_placement_queue.py` | greedy-cover selection + pages for non-surveyed figures |
| `extract_figure_scale.py` | scale from printed ratio or graphic bar |
| `rerun_stale.py` | rebuilds wells outputs missing the provenance columns |

**Reproducing from scratch:**
```
python find_survey_tables.py --all --workers 4 --out csv/survey_coordinate_pages_ALL.csv
python extract_survey_coords.py --candidates csv/survey_coordinate_pages_ALL.csv
python auto_register.py --all --overwrite
python extract_figure_scale.py --validate
python build_verification_queue.py
python build_placement_queue.py --per-site 1
```
All are resumable; `auto_register` carries other sites' rows forward so a single-site run cannot
destroy corpus-wide results.

## Known gaps

- Scale-bar detection fires on 0 of the sheets tested; only printed ratios work (33% coverage).
- **No north-arrow detection**, so rotation always costs a placed point. With it, one point
  would register a figure.
- Chained registration (figures sharing ≥2 labels registering each other) is designed but **not
  built**; it would need residual propagation and a depth cap, since a chained transform
  inherits its parent's error.
- The 93 placement figures inherit the wells module's judgement that a page is a site map; some
  may be schematics with nothing matchable to imagery. Unverified.
- `C_structural_only` locations remain unvalidated at scale and dominate the totals.

---

# Part II — the per-site tool (2026-08-05)

`build_site_georef.py`. ONE page per hazard site, in a self-contained directory laid out like
SOURCE: the page, its figure renders, its libraries and an `exports/` folder together, so a site
is worked, exported and mirrored to E: as a single unit.

Earlier builds produced a page per FIGURE. A finished site had 25 files, a figure that turned
out not to be a map was a dead end with no way to move on, and one site's results arrived as
dozens of separate exports. The unit of work is the site.

## G13. Order of work, and why

1. **Mark north** — click the arrow's base, then its tip.
2. **Place at least two control points** — figure, then imagery.
3. **Calculate** — once, from the control points. Not before, not continuously.

**Two control points minimum, always.** A similarity has 4 unknowns; two points give exactly 4
equations, so the fit is exact by construction and **RMS is 0 no matter how badly you clicked**.
That zero is not a measurement. The third point onward is what makes the residual mean anything.

**Report LEAVE-ONE-OUT, not fit RMS.** The fit residual is measured on the same points that
determined the transform. Leave-one-out refits without each point and tests on the one withheld,
which is the situation every calculated location is actually in. It requires 3+ points and says
so below that.

## G14. Named control points are direct measurements

A control point placed on a well and tagged with its ID gives that location **the exact clicked
coordinate**, exported as `measured_control_point` rather than
`similarity_from_hand_control_points`. It is not averaged with the projected value — the click
is the better measurement. It also proves the figure is the right map, which is why the earlier
random-sample confirmation step was removed: naming one well does the same job and yields a
coordinate.

## G15. Duplicated identifiers are excluded, not guessed

An identifier printed twice on one sheet has two candidate positions — main plan plus detail
inset, a section-line callout, or both ends of a leader. Ten such IDs appeared on a single Hyde
Park sheet. **They are excluded from the calculation and written to
`<site>_ambiguous_ids.csv`.** The only thing that resolves one is a hand control point tagged
with that ID; that click then becomes the location's position. Guessing would place wells tens
of metres out with nothing to signal it.

## G16. Extrapolation is flagged

Control points bound the region the transform was fitted over. A location inside that convex
hull is interpolated; one outside is extrapolated, and error grows with distance past the edge.
Every location carries `outside_control_hull` and `outside_hull_by_m`. Nothing is rejected — the
reader is told which coordinates lean on the transform rather than being pinned by it.

## G17. Label matching — the bug that mattered most

Shipped finding **30 of 254** identifiers on Hyde Park p65. Final result **199**. Three faults:

- exact string match only → ignore punctuation (58)
- joined adjacent tokens **by list order** — but `extract_words()` does not return visually
  adjacent pieces consecutively. `IFW` and `-1` sit flush on the page (gap 0.0 pt) and far apart
  in the list. **Group into lines, sort by x, walk left to right** (130)
- a 3-token cap matched the PREFIX of longer glued labels, turning `MW-12`, `MW-11` and `MW-16`
  into **seven phantom `MW1`s at wrong wells**. Now a match is refused when the next token
  continues at ≤1.5 pt gap (199)

The third would have shipped wrong coordinates, not merely missing ones.

## G18. North arrow detection — attempted and abandoned

`detect_north_arrow.py` exists and **does not work**. Three approaches found legend text, fence
linework, and nothing at all. On sheets whose annotation is outlined, every letter is a closed
polygon, and on the reference sheet the real arrow was not even among the candidates — it is not
a 3-10 point closed path in that file.

Rotation is a human click. This costs two clicks and is certain, and two control points
determine rotation independently anyway. Do not revisit without a vision model.

## G19. Measured accuracy of the hand path

| site | scale | control pts | fit RMS | leave-one-out |
|---|--:|--:|--:|--:|
| 97th St Methodist Church 932084A | 0.25 m/pt | 6 | 2.76 m | **3.81 m** (worst 6.93) |
| Hooker-Hyde Park Landfill 932021 | 2.54 m/pt | 6 | 18.33 m | ~18 m |

**The difference is sheet scale, not operator skill.** At 0.25 m/pt a five-point click slip
costs 1.2 m; at 2.54 m/pt the same slip costs 13 m. Tight site plans are forgiving, regional
sheets are not — and the metre error on a regional sheet is dominated by the drawing side, not
the imagery. Control points on named wells also beat road intersections, which are 10-20 m of
ambiguous asphalt.

## G20. Interface failures worth remembering

Every one of these shipped and had to be found by the user, not by a test:

- `setPointerCapture` on pointerdown retargets the following `click` to the capturing element,
  so markers became unclickable. Capture only after ~4 px of movement — or bind selection to
  pointerup and record the pressed element yourself.
- A literal newline inside a quoted JS string is a syntax error: **the whole script never parses**
  and the page is blank and dead. Identical symptom to a stale-state crash, so it was misdiagnosed.
- A markup insertion whose target string had a leading space the file lacked applied to nothing,
  leaving handlers bound to buttons that were never added. `$('#id').onclick` on null **kills the
  entire script**. Handlers now attach through an `on(id, ev, fn)` guard that reports the gap to
  an on-page error banner and continues. **Always verify a replacement actually landed.**
- Clicks before the image loads, or a pane reporting zero width, produce NaN coordinates that are
  stored silently. Reject non-finite points at entry and sanitise saved state on load.
- Saved work lives in the browser, not on disk, so a rebuilt page inherits a previous attempt's
  points. The page needs its own reset — `?reset=1`, plus per-figure and whole-site buttons.

## G21. Layout

```
georef/sites/
    ready/      104 sites — one directory each, workable now
    needs_ocr/  126 sites — manifest CSV + README, two distinct problems:
                  31 have locations but no citable figure  -> find the map, hand-plot
                  95 produced zero locations (scan-locked) -> OCR the TABLES first
    done/       move a site here once its CSVs are in its exports/
```

## G22. Callout figures break projection entirely — the label is not the sample

Found 2026-08-05 on 211 Main Street C932171, by Caitlin: *"there are no points in those
locations."* She was right, and the reason invalidates the projected coordinates for that site.

**Two figure styles, and only one is projectable.**

- **Annotated plan** — the identifier is printed beside its symbol. Label position ≈ sample
  position, offset ≈ 6 m (one label width). This is what G19's accuracy numbers were measured
  on, and projection is valid.
- **Callout sheet** — every identifier sits in a boxed text block around the sheet margin, tied
  to its symbol by a leader line. C&S Engineers' Figures 3 / 4a / 4b for 211 Main are this
  style: the boxes carry an ID plus its contaminant results, and the symbols cluster in the
  middle. **Label position is unrelated to sample position.** Projecting places every well at
  its text box, tens of metres from the real point.

**The test — free, and it uses data already collected.** A named control point records where a
human clicked the *symbol*. The text layer records where that same ID is *printed*. The distance
between them is the projection error, measured directly:

| site | figure style | n | median | max | verdict |
|---|---|--:|--:|--:|--:|
| 97th St Methodist 932084A p36 | annotated | 3 | **5.6 m** | 6.5 | projection valid |
| 401-402-430 Buffalo Ave C932164 | annotated | 9 | **4.7 m** | 8.0 | projection valid |
| 211 Main C932171 p19 (short leaders) | callout | 5 | **4.1 m** | 50.3 | borderline |
| 211 Main C932171 p18 | callout | 6 | **10.4 m** | 15.4 | **invalid** |
| 211 Main C932171 p17 | callout | 8 | **20.1 m** | 43.7 | **invalid** |

The ~5 m results on annotated sheets match G19's predicted label offset, which is the
confirmation that the test measures what it claims to.

**Consequence for reporting.** Leave-one-out is computed among control points, which sit on
symbols. On a callout sheet it therefore describes the transform and says *nothing* about the
projected rows. 211 Main's LOO of 4.34 / 5.10 / 6.03 m was quoted as the site's accuracy; the
projected rows are out by 10–44 m. **On a callout sheet LOO is not the site's accuracy.**

**Rules adopted.**
1. Require ≥3 named control points, then compute median label→click displacement. **If it
   exceeds 8 m, suppress projection on that figure** — every location there is a hand click or
   nothing. Implemented as the callout guard in `build_site_georef.py` (`labelOffsets()`,
   `CALLOUT_LIMIT_M`) and auditable after the fact with `check_callout.py`.

   **The 8 m threshold comes from the gap in the measured data, not from theory.** 12 m — twice
   the ~6 m label offset — was tried first and let 211 Main p18 through, a sheet that is
   unmistakably callout on sight. Confirmed-annotated sheets score 4.4 / 5.4 / 5.6 m; confirmed
   callout sheets score 10.4 / 20.1 m. 8 m sits inside that gap.

   A callout sheet with SHORT leaders passes, and that is intended: 211 Main p19 scores 4.1 m
   because its boxes sit beside their symbols, so its error is inside the transform's own noise.
   The guard measures error, not drafting style.

   **Structural pre-detection was attempted and does not work.** Three signals were tested
   against the figures whose style was confirmed by eye — labels enclosed by a filled rectangle
   (0% on every sheet; the boxes are paths, not rects), volume of neighbouring text (211 Main p17
   88 chars vs 97th St p18 113 chars — the annotated sheet scores higher), and labels touching a
   long line end (Buffalo Ave p60 35.1%, the highest of any sheet, and it is annotated). All
   three overlap. That is why the guard needs control points and therefore fires during the work
   rather than before it.
2. On a callout sheet the only valid outputs are the hand-placed control points.
3. Leader-line tracing (box → symbol) would recover the rest and the geometry is present in the
   vector layer, but it is unbuilt and sits behind the shipping HOLD.

## G23. Duplicate identifiers: depth variants are not ambiguity

G15 excludes any identifier printed twice. That rule over-fires on **depth variants** — one
borehole logged at two intervals, `SB-03 (3')` and `SB-03 (15')`, printed twice against a single
symbol. Caitlin: *"one hole could have different testing depths so they stay in the same spot."*

The 12 pt clustering already separates the two cases:

- same ID at **≈ the same position** (< 12 pt ≈ 1.5 m) → **one hole**; assign one coordinate to
  every depth variant instead of excluding them.
- same ID at **genuinely different positions** → ambiguous, exclude per G15.

On 211 Main p19 all four flagged IDs (`SB03`, `SB08`, `SB12`, `SB15`) are depth variants and
should never have been excluded.

## G24. Numeric pseudo-identifiers reach the figure matcher

211 Main p17 returned 70 "locations", of which **40 are bare numbers** — and the sheet shows what
they are: contaminant results inside the callout boxes (`Lead 220`, `Copper 131`, `Zinc 610`),
plus `9999`, `5833`, `6667` lifted straight from the projection block (`Scale Factor 0.9999`,
`Central Meridian -78.5833`, `False Easting 1,148,291.6667`). These entered the figure matcher
because they are present in that site's `_sampling_locations.csv`.

Corpus-wide, bare numbers are **17,990 of 87,140 location rows (20.6%) across 117 sites** — but
that number is a *proxy, not a finding*. Numeric identifiers are legitimate at many DEC sites
(borings numbered 100/200/300; Love Canal well designations). The list also contains the site's
own street address (`6200`, `6390`) and Niagara Falls ZIP codes (`14304`, `14303`).

**Do not quote 20.6% as a contamination rate.** Discriminators to test on a 3–4 site sample
first: does the number share a text line with a chemical name or a unit, and does it appear in
the site's sampling-locations *table* or only in figure callouts?

## G25. Boundaries are their own export, and they check the transform

Caitlin, 2026-08-05: *"have the boundaries as a specific export because then we would avoid the
confusion but there should be in the background geocoding process that all points on plot have to
be within the bounding boxes that get selected — that way it can also be added to the database we
are building as part of the spatial information."*

**Traced on the FIGURE only, then projected.** A boundary vertex is NOT a paired figure+imagery
click like a control point. Two reasons: a parcel outline is many vertices and pairing each would
be slow, and — the one that matters — the transform is fitted from SYMBOL clicks, so it stays
valid on a callout sheet even where the label positions are worthless (G22). A traced boundary
therefore works on exactly the sheets where projection of labels does not.

**Kept in its own file** so a polygon is never mistaken for a sample:
- `<site>_boundaries.csv` — one row per vertex, in ring order, 23 columns.
- `Boundary_Polygon.derived.txt` — the same rings in Caitlin's hand-built geometry format,
  `name= {[lat, lon, ...]}` with CRLF.

⚠ **Never written as `Boundary_Polygon.txt`.** That format keys rings by NAME, so a tool write
would silently clobber a hand-placed ring sharing a name. NFSS 932023 has a hand-built one in
`validated/`. Merge by hand if both are wanted in one file.

**A ring is only as good as the transform under it**, so every vertex carries the same provenance
a location does — `figure_style`, `fit_rms_m`, `leave_one_out_median_m`, `n_control_points`,
`label_offset_median_m`, source document and page. A ring projected off a callout sheet with 3
control points and one off an annotated sheet with 8 are different objects; without these columns
the spatial database cannot tell them apart.

**Containment FLAGS, it never drops.** Every location row gains `inside_boundary` (ring name or
empty) and `outside_boundary_by_m`. A sample outside its own site boundary is not a sample that
moved — **it is a transform that is wrong**, and that is the most useful signal the geometry
produces. Dropping the row would remove the evidence of the failure it exists to reveal. The
count surfaces on the page alongside the hull violations.

## G26. Rebuild of 2026-08-05 — 104 + 2 pages, guard and boundaries

`--all` rebuilds into `ready/` only, so the sites in `done/` need an explicit `--out-dir`.
Verified afterwards, because a previous bulk rebuild wrote broken pages until it was killed:
- 104 built, **0 failures**; all 104 swept for `CALLOUT_LIMIT_M`, `pointInRing` and the new
  export buttons — **0 missing**.
- 3 random pages opened in a browser: scripts run, no console errors, every handler bound.
- **A rebuild does not touch `exports/`, added notes, or `localStorage`.** The key is
  `site_v1_<site>` and state within it is keyed by figure `stem`, so the risk is not the rebuild
  itself but a CHANGED FIGURE SET orphaning saved work. Checked explicitly: every page carrying
  existing control points (211 Main 17/18/19, Buffalo Ave 20/52/60, 97th St 36) still appears in
  its rebuilt figure list.

## G27. A fixed-height stats block silently ate the workflow

Caitlin, immediately after G25 shipped: *"I see that there is an export boundary button but no
option to actually put the boundary on the figure."* The button existed and was bound — it was
1.5 screens below the fold, in a region collapsed to almost nothing.

The right-hand column is `#scroll` (the workflow: mark north, control points, trace, calculate)
above `#stat` (hero, detail line, exports, resets). The CSS was:

```css
#scroll{flex:1;min-height:0;overflow-y:auto}
#stat{flex:none}
```

`#stat` never shrinks and `#scroll` absorbs whatever is left, so **every button added to `#stat`
comes straight out of the workflow's space.** The two new boundary export buttons took `#stat`
to 246 px of a 415 px window and left `#scroll` **54 px** to display a 353 px panel. The steps
were technically present, reachable only by scrolling a 54-pixel slot — which is indistinguishable
from missing.

Fixes, all three needed:
1. `#scroll{min-height:240px}` — the workflow must never be the thing that collapses.
2. `#stat{max-height:55vh;overflow-y:auto}` — it can no longer grow without bound.
3. **Exports and resets moved into a `<details>` closed by default.** They are used once per
   figure; the steps are used constantly. `#stat` fell from 246 px to 99 px.

Also corrected: the trace button was numbered ④ and rendered **above** ③ Calculate. Renumbered so
the panel reads ① north · ② control points · ③ trace boundary (optional) · ④ calculate.

**The lesson is about verification, not CSS.** The page was checked with `getElementById` and a
screenshot, and both passed — the element existed and the visible area looked fine. Neither asks
*can a person reach this control*. Measure the container: if a panel is taller than the box
holding it, the feature is not shipped. Verified afterwards by clicking through the real UI —
enter trace mode, click four corners, watch the polygon draw, close the ring.

## G28. The boundary tool computed everything and showed nothing

Caitlin, 2026-08-06: *"we were running a fix on the tool to create site boundaries but the tool
isn't really working that well."* Two defects, both confirmed by driving the real page rather
than by reading the source.

**1. A traced ring was never drawn on the imagery.** `calculate()` built `s.ringGeo` with a
projected lat/lon per vertex, and both exporters consumed it — but `ringGeo` appeared in exactly
three places in the file and none of them was `paint()`. The map carried `cpLayer` and
`locLayer`; there was no ring layer at all. Measured on a live page: after tracing a four-corner
ring and calculating, `ringGeo` held 4 projected vertices and the map held **0 layers with any
geometry**. The boundary existed as data, was written to both export files, and was invisible to
the person who drew it.

That is the worst possible failure for this particular feature. **A ring's second job is to test
the transform** — a sample outside its own site boundary means the transform is wrong — so the
one independent check the geometry provides could not itself be checked. The page would report
`8 of 13 locations fall outside the traced boundary` while giving no way to see whether the
boundary or the transform was at fault.

**2. Placing a boundary corner deleted the calculated coordinates.** The vertex-click path,
`closeRing` and `delRing` each ran `if(s.coords) s.coords=null`. Measured: 13 coordinates before
the first corner click, **0 after**, and every location marker gone from the map. The panel asks
for the trace at step ③ and the calculation at ④, so the prescribed order hid this; anyone who
calculated first and then traced — the natural order, since the boundary is a check on the
result — watched their work disappear on the first click and traced the rest of the outline
against an empty map.

**The fix, and why it is not simply "stop nulling".** The nulling guarded something real:
`inside_boundary`, `outside_boundary_by_m` and the two fit counters genuinely go stale when a
ring changes. But containment is a property of the RING — *moving a corner cannot move a sample*
— so it recomputes without refitting anything. Extracted as `applyContainment(s)` and called
from all three edit paths plus `calculate()`, which now shares one routine, so a ring means the
same thing whether it was traced before or after the button was pressed.

- **Distances are computed in figure points and need the transform's scale only to become
  metres.** Tracing before Calculate therefore still flags inside/outside honestly and leaves
  `outside_boundary_by_m` **null** rather than inventing a number.
- **`fit(cps)` is standalone**, so a transform exists as soon as there are two control points.
  Rings render live from `ringLayer` at step ③ instead of waiting for ④ — otherwise the corners
  stay invisible for the whole of the step that places them. An unclosed trace draws as a
  **polyline**, not a filled polygon: filling it would imply an edge not yet placed.

**Verified through the UI, not through `getElementById`** — G27's lesson applied to its own
successor. Traced before Calculate: 1 polyline + 4 vertex dots on the imagery. Closed and
calculated: 1 polygon, `n_outside_boundary` 0 of 4. Started a second ring afterwards: coordinates
held at **4, not 0**, and the location markers stayed. The polygon was then measured on screen —
**365 × 412 px, 173 × 179 m on the ground, intersecting the viewport** — because a layer that
exists can still be off-screen, zero-area or under the tiles.

## G29. The callout guard had never once fired

Found 2026-08-06 while assessing the exports in `done/`. **Every figure in all five worked
sites reported `figure_style = untested` and `label_offset_n = 0`** — including 97th St p36 and
Buffalo Ave p20, both of which G22–G24 record as *measured* annotated sheets. The guard added in
G24 to stop 211 Main shipping wrong coordinates had never run on a single figure.

**The cause is one line.** `labelOffsets()` matched a control point's typed id to a printed
label with `l.label.toUpperCase() !== k` — an exact string compare:

- a human types the id **as the report writes it**, `GW-3155`; the sheet prints it **as the
  draughtsman drew it**, `GW3155`
- worse, on 211 Main p18 the control points carry the **depth interval the sample came from** —
  `BH-10(3'-4')`, `TP-4(1'-2')` — against a bare `BH10`, `TP4` on the sheet

Measured across the 36 figures in `done/`: **exact matches = 0 on every single figure.** So
`off.length >= 3` was never true, `suppress` stayed false, `figure_style` fell through to
`untested`, and projection went ahead unguarded — including on sheets already measured as
callout.

**`check_callout.py` was right the whole time and disagreed silently.** The offline audit
normalises with `norm()` and reported 3 callout figures against the tool's 0. A backstop that
contradicts the tool it backs up is worth more than either alone — but only if someone runs it.

**The fix: `normId()`, and the same normalisation as `check_callout.py` on purpose.** Strip a
parenthetical, uppercase, strip non-alphanumerics. The audit and the guard must not disagree.
Verified collision-free before shipping: across all 36 figures, **no two printed labels and no
two control-point names collapse onto one key**, so the `named{}` map cannot silently
last-writer-wins.

**`count{}` is deliberately NOT normalised, and this must stay that way.** It answers a
different question — *is this string printed twice on this sheet* — which is a fact about the
drawing. Normalising it would collapse `SB-03 (3')` and `SB-03 (15')`, one hole logged at two
depths (G15), into a false duplicate and delete both coordinates. Two questions, two keys: `k`
raw for `count`, `nk` normalised for `named`.

**Measured effect, replaying Caitlin's own control points:**

| figure | before | after |
|---|---|---|
| 211 Main p17 | untested, 70 loc, 62 projected | **callout 20.07 m, suppressed, 0 projected** |
| 211 Main p18 | untested, 38 loc, 32 projected | **callout 10.43 m, suppressed, 0 projected** |
| 211 Main p19 | untested | annotated 4.09 m, projects |
| 97th St p36 | untested, 19 loc | annotated **5.59 m**, 16 loc |

All three now agree with `check_callout.py` to 0.1 m (20.1 / 10.4 / 4.1 / 5.6). **The validated
97th St numbers are unchanged** — LOO 3.81 m, RMS 2.76 m — because leave-one-out is computed
among control points and never depended on this.

**A second defect fell out of the same bug.** Because `named` never matched, a named control
point could not replace the label it named, so it was appended by the "named point whose label
is not among the readable ones" fallback instead. **The same well exported twice** — `GW3155`
projected *and* `GW-3155` measured, 5.6 m apart, as two rows with two ids differing only in
punctuation. 97th St's "19 locations" were really 16 wells. Any merge keyed on `location_id`
(work-queue item 7) would have treated them as separate samples. Fixed by the same change.

⚠ **`S4` vs `SS-4` on 97th St is NOT this bug** — those differ by a letter, not punctuation, so
they are either a label misreading or two genuinely different points. Normalisation leaves them
separate, correctly. Needs a human look at the sheet.

## G30. Boundaries are placed in PAIRS, not traced through the transform

Caitlin, after asking for this more than once: *"I asked you repeatedly that the bounding box
control points be separated from the 'add control points' button — because drawing the box on
the figure was never going to work."*

G25 built boundary tracing as figure-only clicks projected through the transform. The reasoning
there was sound in isolation — the transform is fitted from symbol clicks, so it survives a
callout sheet where label positions are worthless — but it makes the ring only as good as the
fit, on sites where the fit is exactly what is in doubt.

**③ Place a boundary (corner pairs)** — click the corner on the figure, then the same corner on
the imagery, per vertex, under its own button that knows a polygon has to be closed. Each vertex
keeps **the coordinate that was clicked**. It never passes through the transform, so nothing can
pull it out of place, and it **works with zero control points**. Exported as
`measured_vertex_pairs` so a reader can tell it apart from a projected ring. Verified: the
exported lat/lon is byte-identical to the clicks.

Two clicks per corner, not a drag — `setPointerCapture` on pointerdown retargets the following
click and made markers unclickable once before (G20).

The figure-only trace remains, demoted, for the case where a ring is wanted on a sheet nobody
intends to register by hand.

**A projected ring below three control points is now drawn PROVISIONAL** — faint, dashed,
labelled. Two points determine a similarity exactly: the fit passes through both, RMS is 0 by
construction, and nothing in the data can contradict it. Drawn solid, that outline invites
placing the third control point where the boundary appears to want it, which fits the transform
to its own output and hides the disagreement the third point exists to expose.

## G31. Regions can be excluded, and it runs BEFORE the duplicate count

A figure's KEY lists every identifier on the sheet. Those strings are real ids at a real
position — the key's position — and nothing in the text marks them as not-a-sample, so they
project into a tight bogus cluster wherever the key sits.

**⊘ Exclude a region** — two clicks, opposite corners. Masked labels stay drawn in red rather
than disappearing, because otherwise there is no way to see whether the region covers what was
meant. Excluded ids are written to `<site>_excluded_labels.csv` with position, page and reason:
a reader who counts identifiers on the sheet and compares against the locations file must be
able to account for the difference by name.

**The ordering is the point.** Masking runs before `count{}`, so an id printed once on the map
and once in the key stops looking like a duplicate. On 915 Cleveland p62, 12 of 32 labels are the
key: masking it removed 7 junk points **and recovered 5 real wells** (`BH1`, `BH9`, `TPMW1`,
`TPMW4`, `OBMW1`) that were being discarded as ambiguous purely because the key reprinted them.
Ambiguous ids 6 → 1.

## G32. Saving is not allowed to fail quietly

`save()` was `try{ localStorage.setItem(...) }catch(_){}`. A swallowed write means the page keeps
showing work it never stored — the control points are on screen, the count climbs, and there is
nothing in storage. You find out when you reopen and it is gone, which is indistinguishable from
never having done the work.

Now: serialise → write → **read it back and compare**. Anything that does not round-trip raises a
persistent banner saying to export immediately, because the CSV is then the only copy. A save
badge under the site name reports `saved · N KB · HH:MM:SS`, and `beforeunload` warns when a
figure has calculated coordinates that were never exported.

⚠ **ALL `file://` PAGES SHARE ONE localStorage.** Proven by reading one site's keys from another
site's page. **Never call `localStorage.clear()`** — it wipes every site, not the page you are
on. Only `removeItem(KEY)`.

## G33. Figure ranking: the candidate set was the bug, not the order

Candidates came only from `cited_figures()` — pages where the wells module matched an identifier
in the TEXT layer. **A drawing whose annotation was converted to outlines carries no extractable
text, so it could never be a candidate at all**, however good a map it was. On Frontier Royal
Avenue the ROD amendment's own site figures (pp 26–33) hold ~2,090 lines and ~4,550 curves each
with **zero characters**, while the pipeline selected annotation-dense grading plans for a
*neighbouring property*.

`classify_map_pages.py` already detects exactly these pages — but it only ever ran over sites the
wells module found NO map for. **A site with bad maps rather than no maps fell straight through
that gap**, which is why the biggest sites came out worst: they are the ones most likely to have
some citation. Frontier had 0 rows in a 19,527-row cache.

- **`drawing_pages()`** — structural detection, ≥300 curves or ≥800 segments, no text required.
  Cached per site under `georef/map_pages_cache/`. Frontier: **312 drawing pages**.
- **Reserved slots** — half the figures to sheets carrying identifiers, half to text-free
  drawings. Making "is it a drawing" the first sort key did NOT work, because the pages crowding
  the good ones out are drawings too.
- **Max 2 pages per document.** The old selection was 5 of 8 from a single report.
- A text-free drawing is **kept, not dropped**: control points and boundaries are clicked, not
  read.

⚠ **Honest limit.** With 312 drawings, no geometric rule knows WHICH is the right map — ranking
text-free sheets by segment count promotes the most *cluttered* drawing. The scan makes the good
pages **reachable**; `--figure "DOC.pdf:26-33"` makes them **chosen**.

## G34. Forcing figures the citations missed

`--figure "DOC.pdf:26-31,200-204,225"` — repeatable, accepts ranges, accepts an absolute path so
a 250 MB report can be staged on a fast disk, and forced pages are exempt from `--max-figures`.
A forced page yielding zero readable identifiers is kept anyway, and says so.

Two sites proved why this is needed and what it cannot fix:
- **Factory Outlet C932127** — 11 of 14 pages the operator found carry **no text layer at all**
  (vector linework with outlined text; one genuine scan). The 3 with text carry only street
  names. Hand-plot only.
- **LOOW** — the opposite. 12 of 13 pages have a real text layer, but the site's 717 extracted
  "locations" are ~97% noise (433 `C_structural_only`, 139 explicitly `G_map_furniture`, 25% bare
  numbers, one id reading `A1ALYSIS`). Only 15 are tier A or B. What matched on the good pages
  were contour elevations and scale-bar numbers. The real features are the `DU` decision units
  and `CWLS` wells on pp 8, 9 and 85.

## G35. Publishing the georef batch — the two things that nearly corrupted it

Push script: `web/push_georef.py` (`--dry-run` reports and writes nothing). Run 2026-08-08:
locations **1,237 → 1,511**, rings **38 → 59**.

### Rings are delimited by `vertex_seq` restarting, NOT by their name

The first version grouped vertices by `(site, boundary_name, boundary_type, document, page)`
and sorted each group by `vertex_seq`. Where one figure carries several rings **with the same
name**, that merged them into a single polygon and interleaved their vertices:

| site | truth | rendered as |
|---|---|---|
| LOOW p10 | 5 "Hazard Area" rings, 14 + 4 + 6 … vertices | one 36-vertex tangle |
| Carborundum p63 | 6 "Contaminated" rings | one 33-vertex tangle |
| 914 Tactical p33 | 2 rings, 5 + 6 vertices | one 11-vertex tangle |

Each contiguous run of increasing `vertex_seq` is one ring; file order is preserved. The
export's own `n_vertices` column is the check — after the fix **0 of 59 rings disagree with
it**, and that assertion is what makes the split trustworthy rather than plausible. Caitlin
caught this from the rendered subsite outlines, not from the numbers.

### The N_after ≥ N_before assertion earned its place twice in one dry run

It aborted the write and prevented two silent data losses:

- Indexing deployed features by `(site, location_id)` **collapsed duplicate ids already in the
  deployed data** — NFSS would have gone 645 → 420. Deployed features are now the base list and
  are never deduplicated; the key index only decides whether an INCOMING row is new.
- **Mill 2 would have doubled** — 223 under the directory name `former_mill2` plus 223 under
  master row C932150. `REMAP_SITE` must be applied to EXISTING features, not only incoming ones.

`former_mill2` is not a site. It maps to C932150 "Former Mill No. 2" and never becomes a master
row. Of the four protected hand-derived well sets only Covanta and Mill 2 appear in this batch;
Covanta held at 6 locations, coordinates untouched, provenance unioned.

### Superseded exports must be chosen deliberately

Several sites hold both `X_locations.csv` and `X_locations.corrected.csv`, some with a `(1)`
re-paste suffix. `pick_export()` prefers `.corrected` then newest mtime, and **logs the choice
and what it superseded** to `georef_push_log.txt`. Shipping the stale file is unrecoverable once
the geojson is rebuilt.

### Operable unit → contaminated

`boundary_type == 'operable_unit'` renames to `contaminated`, and a free-text `other` ring
*named* "Contaminated" is promoted too, or it sits in grey beside the magenta category. These
are source-area soil polygons with depth ranges — contamination extent, not an administrative
subdivision. Colour `#e0447c`, weight 3, fill .30.

### Free-text ring names become dashboard toggles

A ring's tag is its type EXCEPT free-text `other`, which is tagged by its own name. "Hazard
Area", "Area B Landfill", "Area T-4" each get a toggle with no code change — the alternative to
adding a site-specific enum, and a full rebuild, every time a figure names an area.

### The geopackage was not part of the push, and should have been

`web/georef_to_gpkg.py` writes `Niagara_Georef_Sampling_Locations` and
`Niagara_Georef_Boundaries` from the DEPLOYED GeoJSON, so the archive cannot drift from what is
published. Until this ran, the map showed 1,511 points the downloadable geopackage did not
contain. **3 self-intersecting rings** (401-402-430 Buffalo `other_1` p52, 914 Tactical
`site_boundary` p33, 97th St Methodist `site_boundary` p36) are flagged in a `geometry_valid`
column and **not repaired** — `buffer(0)` would silently change a published outline, and which
lobe is the real extent is a question for whoever traced it.

### The `?v=` trap, twice in one session

Bumped to 28, edited `app.js` again, and the live page served the stale copy — contaminated
still 5, no Mill 2 in the radiation tab. Bumped to 29, then 30 after the ring fix. Note that
`?v=` busts the ASSETS but cannot bust `map.html` itself; GitHub Pages served a cached document
even after the push landed, and only a cache-busting query on the page URL showed the new
version. Verify what the PAGE RENDERS.
