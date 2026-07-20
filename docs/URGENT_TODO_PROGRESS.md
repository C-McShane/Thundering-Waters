# URGENT_TODO — progress tracker
_Started 2026-07-20. Fallbacks: git tag `pre-refactor-2026-07-20` (GitHub) · full mirror `E:\Thundering_Waters_Backup_2026-07-20\`_

Working order: **6 → 1 → 3,4,5 → 2,7,10,12 → 8 → 11**

| # | Item | Status |
|---|---|---|
| 6 | Split monolith → `map.html` / `styles.css` / `app.js` / `config.json` / `findings.json` / generated `statistics.json` | **in progress** — Stage 1 (CSS) ✅ · Stage 2 (JS) ✅ · Stage 3 (JSON) next |
| 1 | Count drift → all counts generated from data or one shared config | not started (depends on 6) |
| 3 | Cancer tab: "risk" → "incidence" + permanent limitations statement | not started — **unblocked**, A2 resolved 2026-07-20 |
| 4 | Cumulative well-plot wording ("not contemporaneous plume extent") | not started |
| 5 | "Strongest findings" → **"Selected high detections"** + full citations (radiation too) | not started — placeholders now, `CITATIONS_TODO.md` to be generated |
| 2 | DATA_SOURCES.txt → verify accuracy, then move to repo root | not started |
| 7 | License (code + data), CITATION.cff, changelog | not started |
| 10 | Expose complete provenance | not started |
| 12 | Hand-validation folder + upload working validation efforts | not started |
| 8 | "START HERE" panel (3 sourced headlines, can/cannot establish, 3 buttons) | not started |
| 9 | README titles → "Thundering Waters: The Toxic Legacy of Niagara County" | not started |
| 11 | Frozen validated v1 release | not started (last) |

## Added this round (approved 2026-07-20)

| # | Item | Status |
|---|---|---|
| A1 | **Fix 420,000 CPM location wording.** Map says "RI text locates the peak gamma here" at the TP-03 cluster. RI actually ties **120–170k CPM** to TP-03 and the **420k** to the northern rail-line area (football-sized surface slag piece). Overstates precision — fold into item 5. | not started |
| A2 | **Verify cancer data provenance.** | ✅ **RESOLVED 2026-07-20** (see below) |
| A7 | **Reconcile block-group count: 176 vs 161.** `cancer_sir.geojson` has **176** features; NYSDOH source documents **161** Niagara County BGs (14 suppressed for low population). Determine whether we pulled in neighbouring-county BGs or unsuppressed rows. Must resolve before item 3 ships. | not started |
| A8 | **Carry the NYSDOH `highlight_` significance flag into the data.** Our geojson has only `obs_ / exp_ / sir_`. NYSDOH publishes its own significance determination (+1 elevated / 0 not significant / −1 low, 95% CI). Without it we display raw ratios and cannot legitimately say "statistically elevated." Required for item 3's language. | not started |
| A3 | **Approximate-location inventory** — aggregate every `coord_precision` flag (site-centroid, map-relative) into one public list. Part of item 10. | not started |
| A4 | **License nuance** — code and data need *different* licenses; third-party data (NYSDEC, USACE, USGS, EPA; Microsoft / NYS Office of Cyber Security basemaps) requires **attribution, not relicensing**. Part of item 7. | not started |
| A5 | **Data dictionary** — field-level definitions (`n_found`, `coord_precision`, `sir_*`, `rad_class`, `sample_type`). Complements item 2. | not started |
| A6 | **"Report an error" link** (GitHub issues) — invites correction. | not started |

## Cancer data provenance (resolves A2)
- **Source:** NYSDOH Cancer Mapping Data 2011–2015 — `NYSDOH_CancerMapping_Data_2011_2015.xlsx`
- **Location:** `Niagra\spatial\shp\cancer_mapping\` (+ DataDictionary.pdf, Overview.pdf)
- **Publisher/program:** New York State Dept. of Health — Environmental Facilities Cancer Mapping
- **URL:** https://www.health.ny.gov/statistics/cancer/registry/vol1/
- **Period:** 2011–2015, 5-year aggregated incidence · **Unit:** census block group (12-digit FIPS)
- **Coverage:** 161 Niagara County BGs (14 suppressed for low population) — cf. **A7**
- **Fields:** `observed_{cancer}`, `expected_{cancer}`, `highlight_{cancer}` (+1/0/−1, 95% CI), `total_pop`
- **⚠ Benchmark is NEW YORK STATE, not US national.** NYS is itself elevated vs. the national rate for industrial cancers, so any "X× the national average" claim compounds two elevations and **must** state both benchmarks. NYS-benchmarked SIR is the conservative, publishable figure.
- Suppressed values are **not zero** (already reflected in item 3's required statement).
- Analysis scripts: `Niagra\scripts\lung_cancer_analysis.py`, `meso_sites.py`

**Candidate headline for item 8 (START HERE):** the **mesothelioma cluster in North Tonawanda** (tracts 228–233, 246; county SIR 2.34) is the most causally defensible finding in the project — mesothelioma has few causes besides asbestos, and the cluster coincides with documented asbestos users carrying litigation/remediation records: Buffalo Pumps/Buffalo Forge (932044), Roblin Steel (932059 / B00025), Durez–Occidental (932018). Notably it is a **different** geography from the Niagara Falls chemical corridor. Stronger than any chemical-corridor correlation (cf. the 2026-07-19 ecological regression, which was confounded and not published).

## Refactor staging (item 6)
1. **CSS → `styles.css`** ✅ *done 2026-07-20* — 410 lines out; map.html 2147 → 1736 lines. Verified: external stylesheet loads, computed styles identical, 5 tabs / 255 markers / 1,083 search index, map renders unchanged.
2. **JS → `app.js`** ✅ *done 2026-07-20* — 1,457 lines out; map.html 1736 → **278 lines** (clean HTML skeleton). Kept as **one file** to preserve top-level hoisting + shared globals (`layers`, `wellsLegacyF`, `SEARCH_INDEX`); loaded after Leaflet via `app.js?v=1`. Verified: **zero console errors**, 5 tabs, 255 markers, 1,083 search index, wells 293/259/233, 9 rad zones, 40 tiles, ID search returns C4R-MW-04, 9 chem findings, layer toggles work.
3. **Data → `config.json` / `findings.json` / `statistics.json`** — highest risk: introduces async load ordering. `statistics.json` must be emitted by a generator script run on every data change, or the drift just moves.

**Cache-busting:** every split file needs a `?v=` query or returning visitors get a stale JS/CSS mix.
