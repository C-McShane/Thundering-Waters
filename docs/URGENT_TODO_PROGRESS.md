# URGENT_TODO — progress tracker
_Started 2026-07-20. Fallbacks: git tag `pre-refactor-2026-07-20` (GitHub) · full mirror `E:\Thundering_Waters_Backup_2026-07-20\`_

Working order: **6 → 1 → 3,4,5 → 2,7,10,12 → 8 → 11**

| # | Item | Status |
|---|---|---|
| 6 | Split monolith → `map.html` / `styles.css` / `app.js` / `config.json` / `findings.json` / generated `statistics.json` | **in progress** — Stage 1 (CSS) ✅ · Stage 2 (JS) ✅ · Stage 3 (JSON) next |
| 1 | Count drift → all counts generated from data or one shared config | not started (depends on 6) |
| 3 | Cancer tab: "risk" → "incidence" + permanent limitations statement | ✅ **done 2026-07-20** (see below) |
| 4 | Cumulative well-plot wording ("not contemporaneous plume extent") | ✅ **done 2026-07-20** — caveat rendered under both cumulative plots (radionuclide + chemical) |
| 5 | "Strongest findings" → **"Selected high detections"** + full citations (radiation too) | ✅ **structure done 2026-07-20** — renamed, citation blocks render with visible PENDING markers, `docs/CITATIONS_TODO.md` generated (14 entries, **112 fields outstanding**). Filling the citations is Caitlin's systematic pass. |
| A1 | 420,000 CPM location wording | ✅ **RESOLVED 2026-07-20** — now presented as a *site-wide* figure from the northern rail-line area (exact position not stated in the RI), with the 120,000–170,000 CPM TP-03 reading split out as its own correctly-located entry. |
| 2 | DATA_SOURCES.txt → verify accuracy, then move to repo root | ✅ **done** — at root; 192-line current-provenance section appended to the preserved session log |
| 7 | License (code + data), CITATION.cff, changelog | ✅ **done** — `LICENSE` (MIT, code only), `LICENSE-DATA.md` (CC BY 4.0 + third-party attribution table), `CITATION.cff`, `CHANGELOG.md` |
| 10 | Expose complete provenance | ✅ **done** — `docs/APPROXIMATE_LOCATIONS.md` (480 flagged points + georeferencing accuracy), `docs/DATA_DICTIONARY.md` |
| 12 | Hand-validation folder + upload working validation efforts | ✅ **done** — `validation/` incl. the unpublished cancer regression |
| 8 | "START HERE" panel (3 sourced headlines, can/cannot establish, 3 buttons) | ✅ **done** — landing tab, counts from `statistics.json` |
| 9 | README titles → "Thundering Waters: The Toxic Legacy of Niagara County" | ✅ **done** — also completed item 1's README counts |
| 11 | Frozen validated v1 release | ✅ **v1.0.0 tagged 2026-07-20** — frozen with pending work labelled, not hidden |
| A3 | Approximate-location inventory | ✅ done (`docs/APPROXIMATE_LOCATIONS.md`) |
| A4 | License nuance — third-party data not relicensed | ✅ done (`LICENSE-DATA.md`) |
| A5 | Data dictionary | ✅ done (`docs/DATA_DICTIONARY.md`) |
| A6 | "Report an error" link | ✅ done (sidebar footer → GitHub issues) |

## Added this round (approved 2026-07-20)

| # | Item | Status |
|---|---|---|
| A1 | **Fix 420,000 CPM location wording.** Map says "RI text locates the peak gamma here" at the TP-03 cluster. RI actually ties **120–170k CPM** to TP-03 and the **420k** to the northern rail-line area (football-sized surface slag piece). Overstates precision — fold into item 5. | not started |
| A2 | **Verify cancer data provenance.** | ✅ **RESOLVED 2026-07-20** (see below) |
| A7 | **Reconcile block-group count: 176 vs 161.** | ✅ **RESOLVED 2026-07-20** (see below) |
| A8 | **Carry the NYSDOH highlight flag into the data.** | ✅ **RESOLVED 2026-07-20** — added as `hlarea_{Cancer}`, but semantics corrected (see below) |
| A9 | **Recover the 27 merged block groups via the crosswalk.** NYSDOH merges small-population BGs into custom `DOH####` codes; `NYSDOH_CancerMapping_Crosswalk_2011_2015.xlsx` (already on disk) maps them back. Those 27 currently render blank on the map even though their data exists in merged form. | not started |
| A10 | **Study-period discrepancy.** | ✅ **RESOLVED 2026-07-20** — period is **2011–2015**. The DataDictionary's "between 2005 and 2009" wording is stale text carried over from the prior NYSDOH release. Publish 2011–2015. |
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

### NYSDOH "highlighted area" methodology — authoritative (retrieved 2026-07-20)
Source: https://www.health.ny.gov/statistics/cancer/environmental_facilities/mapping/about/

- **Method:** the **spatial scan statistic**, applied among locations with a **≥50% difference between observed and expected cases**, where *"the ratio of observed to expected cases had to be such that it was unlikely to be a chance occurrence."* Method reference: Boscoe FP, McLaughlin CC, Schymura MJ, Kielb CL, "Visualization of the Spatial Scan Statistic Using Nested Circles," *Health and Place* 2003, 9(3):273–277.
- 50% threshold chosen to balance statistical vs. epidemiological relevance; maximum highlighted-area size capped at **2% of statewide population (~400,000)**.
- **Membership is per block group:** *"each block group either belongs to a highlighted area or does not belong… The true shape of a highlighted area is irregular, though roughly circular."* The circles on NYSDOH's own map are a drawing simplification.
- ⇒ **"Statistically elevated" IS defensible**, provided we convey it is a *cluster-level* determination: a block group belongs to an area with ≥50% more cases than expected, at a level unlikely to be chance. It is **not** a per-block-group significance test of that BG's own rate.
- **Expected cases** are age- and sex-adjusted to statewide rates.
- **Populations:** 2010 census reference; 2011–2015 block-group populations estimated by iterative proportional fitting from county estimates (assumes BG growth matches its county).
- **Timeframe confirmed 2011–2015.** (The DataDictionary's "between 2005 and 2009" on `Observed_Bladder` is stale text from the prior release — NYSDOH's own page states 2011–2015 for all cancer data. **A10 closed.**)
- **Data are provisional as of December 2017.**
- **Privacy merging:** BGs with <6 male or <6 female cases were merged, statewide 15,194 → 13,823 → 13,513; merged regions carry `DOH####` identifiers.

### A9 resolved — merged block groups recovered
Used `NYSDOH_CancerMapping_Crosswalk_2011_2015.xlsx` (`geoid10 → dohregion`) to recover **25** of the 27 previously-blank block groups, drawn from **12 merged DOH regions**. Coverage went **149 → 174 of 176**.

**Full reconciliation — all three numbers now explained:**
| Count | Meaning |
|---|---|
| **176** | every 2010-vintage Niagara County BG polygon we draw |
| **174** | BGs carrying NYSDOH values |
| **161** | **distinct NYSDOH reporting regions** (149 unmerged + 12 merged) — matches the documented "161" exactly ✅ |
| **2** | genuinely no data: tract **9900** (census water) and tract **9401**, both null population |

⚠️ **Merged BGs share one region's counts.** Each carries `merged_area: true`, `doh_region`, `merged_bg_count`. **Always aggregate by `doh_region`, never by block group**, or merged areas are double-counted. `build_statistics.py` reports `cancer_doh_regions` for this reason.

### A8 resolved — the flag and its correct phrasing
Added to `cancer_sir.geojson` as **`hlarea_{Cancer}`** for all 6 cancers across the 149 matched BGs.

> ⚠️ **The NYSDOH DataDictionary defines this field as "membership in highlighted areas" — NOT per-block-group statistical significance.** A highlighted *area* is a contiguous region NYSDOH designates; every block group inside it is flagged `1`.

**Therefore we must never write "N block groups are statistically elevated."** The only defensible phrasing is *"falls within a NYSDOH-designated highlighted area for [cancer]."* This is why the field is named `hlarea_`, not `hl_` — the shorter name invites exactly the misreading item 3 exists to prevent.

The giveaway that forced this check: **esophagus flagged 130 of 149 BGs (87%)** while only 4.8% of block groups statewide are flagged — statistically impossible as per-BG significance when the county records just 95 esophageal cases total. Area membership explains it.

Flag counts across our 149 BGs (area membership): Lung 102 · Bladder 96 · Esophagus 130 · Mesothelioma 13 · Oral 0 · Brain 0.

**Candidate headline for item 8 (START HERE):** the **mesothelioma cluster in North Tonawanda** (tracts 228–233, 246; county SIR 2.34) is the most causally defensible finding in the project — mesothelioma has few causes besides asbestos, and the cluster coincides with documented asbestos users carrying litigation/remediation records: Buffalo Pumps/Buffalo Forge (932044), Roblin Steel (932059 / B00025), Durez–Occidental (932018). Notably it is a **different** geography from the Niagara Falls chemical corridor. Stronger than any chemical-corridor correlation (cf. the 2026-07-19 ecological regression, which was confounded and not published).

## Item 3 — Cancer Incidence tab (built 2026-07-20)
Tab renamed **"Cancer Risk" → "Cancer Incidence."** Permanent, always-visible limitations statement at the top of the panel (never collapsed), plus a source line: NYSDOH · **2011–2015** · block groups · age/sex-adjusted to **New York State** (explicitly "not a national benchmark") · provisional Dec 2017 · link to the method page.

Split into two clearly-described sections, per Caitlin's call that the infographic used highlights and the two must not be conflated:

**① Highlighted Areas** — NYSDOH's own determination via the spatial scan statistic (≥50% more cases than expected, unlikely to be chance). Binary shading, deliberately not a gradient. Copy states plainly it is a **cluster-level** finding, not a test of the block group's own rate. Counts shown as *N of 161 reporting regions*: Esophagus 142 · Lung 112 · Bladder 103 · Mesothelioma 13 · Oral 0 · Brain 0.

**② Standardized Incidence Ratio** — observed ÷ expected per block group; copy states plainly it is *"a ratio, not a significance test"* and that a high SIR on a small population can rest on very few cases. County SIRs: Mesothelioma 2.34 · Esophagus 1.49 · Bladder 1.40 · Lung 1.38 · Oral 1.37 · Brain 1.27.

Both selectors are **generated from `statistics.json`** — no county figure is hand-typed. Only one choropleth renders at a time (choosing in one section resets the other). Popups now disclose highlighted-area status **and** carry a merged-area warning naming the DOH region and how many block groups were combined.

**Esophagus handled explicitly:** 142 of 161 regions would read as an error without context, so the note says so inline — *"That is most of the county — NYSDOH's scan statistic found one large contiguous cluster here, not many separate hotspots."*

### ⚠ One deliberate non-change (needs Caitlin's sign-off)
Item 3 says replace "risk" with "incidence" **in all locations**. I did so everywhere in the cancer tab and the tab label, but **left the toxicology phrasing in the Chemicals tab**: *"Associated with increased **risk** of bladder cancer in toxicological or epidemiological research."* That is the scientifically correct term — toxicology establishes *risk*, not *incidence*, and "associated with increased incidence in toxicological research" would be wrong. Flagging rather than silently deviating.

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
