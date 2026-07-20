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
| A7 | **Reconcile block-group count: 176 vs 161.** | ✅ **RESOLVED 2026-07-20** (see below) |
| A8 | **Carry the NYSDOH highlight flag into the data.** | ✅ **RESOLVED 2026-07-20** — added as `hlarea_{Cancer}`, but semantics corrected (see below) |
| A9 | **Recover the 27 merged block groups via the crosswalk.** NYSDOH merges small-population BGs into custom `DOH####` codes; `NYSDOH_CancerMapping_Crosswalk_2011_2015.xlsx` (already on disk) maps them back. Those 27 currently render blank on the map even though their data exists in merged form. | not started |
| A10 | **⚠ Resolve the study-period discrepancy.** Filename/notes say **2011–2015**, but the NYSDOH DataDictionary field definitions say cases diagnosed **"between 2005 and 2009."** Almost certainly a stale dictionary carried over from the prior release — but we must confirm before printing a period anywhere public. | not started |
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

### A7 resolved — the 176 / 161 / 149 reconciliation
- **176** = every 2010-vintage Niagara County block group (`niagara_county_bg_2010.shp`, built by `scripts/rebuild_bg_cancer_join.py`).
- **149** = those that match a NYSDOH record directly by 12-digit GEOID — these carry the cancer data.
- **27** = block groups NYSDOH **merged** for small population, re-coded as custom `DOH####` identifiers. Not missing data — recoverable via the crosswalk (**A9**).
- Vintage is correct and confirmed by the primary source: the DataDictionary states `Dohregion` is *"based on the 2010 census."* Matching 2010 boundaries to the 2011–2015 data was the right call.
- Cross-validation against the documented findings is good: our 149-BG subset gives **lung SIR 1.380** (doc: 1.375), **bladder 1.395** (doc: 1.401), **mesothelioma 2.425 with exactly 13 flagged BGs** (doc: 13). ✅

### A8 resolved — but the flag does NOT mean what the name suggests
Added to `cancer_sir.geojson` as **`hlarea_{Cancer}`** for all 6 cancers across the 149 matched BGs.

> ⚠️ **The NYSDOH DataDictionary defines this field as "membership in highlighted areas" — NOT per-block-group statistical significance.** A highlighted *area* is a contiguous region NYSDOH designates; every block group inside it is flagged `1`.

**Therefore we must never write "N block groups are statistically elevated."** The only defensible phrasing is *"falls within a NYSDOH-designated highlighted area for [cancer]."* This is why the field is named `hlarea_`, not `hl_` — the shorter name invites exactly the misreading item 3 exists to prevent.

The giveaway that forced this check: **esophagus flagged 130 of 149 BGs (87%)** while only 4.8% of block groups statewide are flagged — statistically impossible as per-BG significance when the county records just 95 esophageal cases total. Area membership explains it.

Flag counts across our 149 BGs (area membership): Lung 102 · Bladder 96 · Esophagus 130 · Mesothelioma 13 · Oral 0 · Brain 0.

**Candidate headline for item 8 (START HERE):** the **mesothelioma cluster in North Tonawanda** (tracts 228–233, 246; county SIR 2.34) is the most causally defensible finding in the project — mesothelioma has few causes besides asbestos, and the cluster coincides with documented asbestos users carrying litigation/remediation records: Buffalo Pumps/Buffalo Forge (932044), Roblin Steel (932059 / B00025), Durez–Occidental (932018). Notably it is a **different** geography from the Niagara Falls chemical corridor. Stronger than any chemical-corridor correlation (cf. the 2026-07-19 ecological regression, which was confounded and not published).

## Refactor staging (item 6)
1. **CSS → `styles.css`** ✅ *done 2026-07-20* — 410 lines out; map.html 2147 → 1736 lines. Verified: external stylesheet loads, computed styles identical, 5 tabs / 255 markers / 1,083 search index, map renders unchanged.
2. **JS → `app.js`** ✅ *done 2026-07-20* — 1,457 lines out; map.html 1736 → **278 lines** (clean HTML skeleton). Kept as **one file** to preserve top-level hoisting + shared globals (`layers`, `wellsLegacyF`, `SEARCH_INDEX`); loaded after Leaflet via `app.js?v=1`. Verified: **zero console errors**, 5 tabs, 255 markers, 1,083 search index, wells 293/259/233, 9 rad zones, 40 tiles, ID search returns C4R-MW-04, 9 chem findings, layer toggles work.
3. **Data → `statistics.json` / `findings.json`** ✅ *done 2026-07-20*
   - **`web/build_statistics.py` → `data/statistics.json`** (generated; never hand-edit). All 9 layer labels now carry `data-stat="<key>"` and are populated at load. **Zero hardcoded counts remain in map.html.**
   - **`data/findings.json`** — radiation + chemical highlight entries moved out of `app.js`, each carrying an empty `citation` block (8 fields, all "Information to be added") ready for item 5.
   - Verified: zero console errors, labels resolve (255 pts / 66 tracts / 293 / 259 / 233 / 55 / 28 / 6), 9 chem findings + 4 radiation findings render from JSON, search index still 1,083.
   - **`config.json` deliberately deferred** — see note below.

### Why `config.json` is deferred (not forgotten)
Map defaults (center/zoom/tiles) must run *before* any fetch resolves, so moving them into an async JSON would add real risk for no benefit. The genuinely useful thing to put in `config.json` is the **public wording** that items 3 and 4 introduce (cancer incidence statement, cumulative-plot note) — which would turn those into data edits rather than code edits. Creating an empty shell now would be cargo-cult; it gets created in item 3/4 when we know what belongs in it.

### Item 1 — count drift: what was actually wrong
| Label | Was shown | Truth (generated) |
|---|---|---|
| Hazard sites | `256 pts` | **255** |
| Chem note (static HTML) | `107 of 256` | **106 of 255** |
| Chem note (after clearing filter) | `122 of 256` | **106 of 255** |

The static and dynamic notes disagreed because they were typed at different times *and* counted different populations: **106** sites carry the curated `chems` array (what the filter actually searches) while **121** have raw NYSDEC free-text in `chemicals`. `statistics.json` now reports both separately (`hazard_sites_with_chemicals` vs `hazard_sites_raw_chem_text`) so they can never be conflated again. Remaining for item 1: the **README** counts (110 legacy sites / 662 monitoring points / 4 tabs) still need regenerating against `statistics.json`.

**Cache-busting:** every split file needs a `?v=` query or returning visitors get a stale JS/CSS mix.
