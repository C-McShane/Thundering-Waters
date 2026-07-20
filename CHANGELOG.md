# Changelog

All notable changes to this project are documented here.
Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [Unreleased]

### Removed
- **Scope clarification.** Removed exploratory Love Canal analyses and the preliminary ecological
  cancer regression from the active repository. These analyses were incomplete, had not undergone
  independent methodological review, and do not support the interactive map's published findings.
  Their removal does not alter the underlying public-source datasets or current map layers. Previous
  versions remain documented in Git history. The Love Canal piezometer geologic-medium correction,
  on which a published map feature depends, is retained as a note in `DATA_SOURCES.txt`.

## [1.2.0] — 2026-07-20

### Added
- **"Last sampled" temporal transparency.** Sampling in this dataset spans **1948–2025**, and until
  now a point's date was only visible by opening its popup — letting a 1970s reading and a 2024
  reading look like equivalent statements about today.
  - `web/build_recency.py` stamps a normalised **`last_sampled`** year onto all 785 monitoring
    points (764 dated, 21 with no recorded date), so the field is available to anyone downloading
    the geojson, not just the map.
  - **Droplets now fade with age.** Opacity was chosen deliberately: fill already means
    "contamination", size means "number of chemicals detected", and ring colour means "sample
    type" — recency needed a channel of its own.
  - **"Filter by When Last Sampled"** in the Monitoring Wells tab: 2020 or later (141) · 2010–2019
    (412) · 2000–2009 (29) · before 2000 (182) · date not recorded (21).
  - Every well popup now opens with **Last sampled: <year>**, or "date not recorded".
  - Points with no date are a **distinct category**, never silently grouped with old or new.
  - The legend and filter both state that fading shows **age, not severity** — an older point is an
    older observation, not a cleaner one.

### Fixed
- **Corrected the recency figures in the START HERE panel.** They previously read "1969–2024" and
  "about a third were sampled in 2020 or later", both derived from a partial subset. The canonical
  `last_sampled` field gives **1948–2025** and **141 of 785** (18%). Now generated from
  `statistics.json` rather than written by hand.

## [1.1.0] — 2026-07-20

### Added
- **Address Lookup tool.** Enter an address and it reports the straight-line distance to the
  nearest documented hazard site and to the nearest sampling point where a contaminant was
  detected. Geocoding uses the US Census Bureau geocoder, called client-side; the address is not
  stored and is not sent anywhere else.

  Built to a single constraint: **the output must not be readable as a safety verdict.**
  - Distances are rounded hard (never "1,247 m") and there is no red/green result styling.
  - Three limits render *with every result*, not in a collapsed note: distance is not exposure
    (groundwater moves directionally, not radially); a **large** distance may only mean nobody
    sampled nearby; site points are centroids, and large sites extend far beyond them.
  - Geocode quality is surfaced — Census matches to a street segment, not a rooftop (~100 m).
  - Out-of-county addresses and geocoder misses fail gracefully rather than returning a
    confident distance from a bad origin.
  - **Footprint containment is evaluated across every site, not just the nearest.** LOOW is
    7,500 acres (~3.1 km equivalent radius), so an address can sit inside its footprint while a
    small site 500 m away is "nearest by centroid" — checking only the nearest would have
    silently hidden the site that actually matters. Because we hold acreage and a centre point
    rather than a surveyed boundary, this is reported as *may fall within*, never as a
    determination.

## [1.0.1] — 2026-07-20

### Fixed
- **Corrected an over-cautious limitation.** The START HERE panel said the map cannot show
  "present-day conditions — many records are historical". That undersold the data: sampling spans
  **1969–2024** and about a third of sampled points were last visited in 2020 or later. The real
  limitation is that the map is not a *synchronised* snapshot — each point reflects its own last
  sampling date. Reworded in the interface and added as a caveat in `LICENSE-DATA.md`.

## [1.0.0] — 2026-07-20

First frozen, validated release.

### Added
- **Searchable sample points.** The search box resolves any well, test pit, geoprobe, soil
  zone or piezometer by its identifier (e.g. `C4R-MW-04`, `TP-14`, `SS-01`) across 1,083
  indexed points, so a cited figure can be looked up and verified independently.
- **Selected high detections** (formerly "Strongest findings") in the Chemicals and Radiation
  tabs, each carrying a source-citation block. Uncited entries render a visible *pending*
  marker so an unsourced number cannot look finished.
- **Covanta 15-Acre Site**: 21 geoprobe soil borings georeferenced from RI Fig 6 with
  BTEX/PAH chemistry; surface-soil PAHs including benzo(a)pyrene; peak-gamma hot spot.
- **Cancer Incidence tab** split into *Highlighted Areas* (NYSDOH spatial scan statistic) and
  *Standardized Incidence Ratio*, with a permanent limitations statement.
- `statistics.json`, generated by `build_statistics.py` — the single source of truth for every
  count shown in the interface.
- `DATA_SOURCES.txt` at repository root; `validation/` folder; `LICENSE`, `LICENSE-DATA.md`,
  `CITATION.cff`.

### Changed
- Split the 2,147-line `map.html` monolith into `map.html` / `styles.css` / `app.js` plus
  generated data files.
- Radiation-tab droplets now carry a black-and-yellow hazard-striped border.
- Cancer tab renamed from "Cancer Risk" to "Cancer Incidence"; "risk" replaced with
  "incidence" throughout that tab.

### Fixed
- **Count drift.** Interface labels read `256 pts` and the chemicals note disagreed with itself
  (`107 of 256` static vs `122 of 256` after clearing the filter). True values are 255 sites and
  106 with curated chemicals; all counts now derive from `statistics.json`.
- **Overclaim removed** from the cancer tab: "These six are statistically elevated countywide
  (95% CI > 1)".
- **420,000 CPM attribution.** No longer implied to have been measured at the TP-03 cluster; it
  is the site-wide peak from a surface slag piece in the northern rail-line area, with the RI's
  silence on its exact position stated outright.
- **Census tract and impact-zone popups** were unclickable — the hazard-site canvas pane spanned
  the map above them and swallowed clicks.
- Location-only wells rendered "undefined distinct" chemicals; now "none tabulated (location point)".
- Recovered 25 cancer block groups that NYSDOH had merged into `DOH####` regions for privacy and
  which previously rendered blank.
- Corrected a lexicon mis-map that labelled dibenzofuran as "Dioxins / furans".

### Notes
- An ecological regression of cancer SIR against hazard-site density was run and deliberately
  **not published** (lung confounded by smoking/SES; bladder null). It was **removed** from the
  repository on 2026-07-20 as unvalidated and out of scope, together with an exploratory set of
  Love Canal analyses; both remain in Git history. See `CORRECTIONS.md`.
- **Vanadium Corporation of America (932001) is not radioactive** and is not tagged as such. It
  is a ferroalloy site; VCA's uranium mills are all in the western United States.

### Known pending at v1.0.0
This release is frozen deliberately, with incomplete work labelled rather than hidden:

- **112 source-citation fields** across 14 "Selected high detections" remain to be filled
  (`docs/CITATIONS_TODO.md`). Affected entries render a visible *pending* marker in the interface.
  A pending marker means the figure is **not yet fully sourced** — not that it is disputed.
- **Comparison standards not yet named.** Whether groundwater figures are compared against the
  federal MCL or NYSDEC AWQS, and which Part 375 SCO tier applies to soil, is still to be settled.
- **Covanta peak-gamma marker is not georeferenced.** RI Figure 15 is raster-only; the marker is
  anchored to the TP-03 test-pit cluster and says so in its popup.
- **480 points carry approximate positions** (`docs/APPROXIMATE_LOCATIONS.md`).
- Radiological candidates identified but not yet added: Great Lakes Carbon (932016), Airco Speer
  Carbon-Graphite (932002), and ~22 further NFSS vicinity properties
  (`validation/rad_candidate_sites.csv`).

These will be closed iteratively. The frozen tag exists so that anything cited from this map has a
stable, reproducible reference point.

