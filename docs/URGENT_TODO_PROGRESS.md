# URGENT_TODO — progress tracker
_Started 2026-07-20. Fallbacks: git tag `pre-refactor-2026-07-20` (GitHub) · full mirror `E:\Thundering_Waters_Backup_2026-07-20\`_

Working order: **6 → 1 → 3,4,5 → 2,7,10,12 → 8 → 11**

| # | Item | Status |
|---|---|---|
| 6 | Split monolith → `map.html` / `styles.css` / `app.js` / `config.json` / `findings.json` / generated `statistics.json` | **in progress** — Stage 1 (CSS) ✅ done; Stage 2 (JS) next; Stage 3 (JSON) last |
| 1 | Count drift → all counts generated from data or one shared config | not started (depends on 6) |
| 3 | Cancer tab: "risk" → "incidence" + permanent limitations statement | not started — ⚠ blocked-ish, see A2 |
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
| A2 | **Verify cancer data provenance.** `cancer_sir.geojson` has no source field; registry/vintage/geography unconfirmed. Should not ship a rewritten cancer tab whose source we can't cite → gates item 3. | not started |
| A3 | **Approximate-location inventory** — aggregate every `coord_precision` flag (site-centroid, map-relative) into one public list. Part of item 10. | not started |
| A4 | **License nuance** — code and data need *different* licenses; third-party data (NYSDEC, USACE, USGS, EPA; Microsoft / NYS Office of Cyber Security basemaps) requires **attribution, not relicensing**. Part of item 7. | not started |
| A5 | **Data dictionary** — field-level definitions (`n_found`, `coord_precision`, `sir_*`, `rad_class`, `sample_type`). Complements item 2. | not started |
| A6 | **"Report an error" link** (GitHub issues) — invites correction. | not started |

## Refactor staging (item 6)
1. **CSS → `styles.css`** ✅ *done 2026-07-20* — 410 lines out; map.html 2147 → 1736 lines. Verified: external stylesheet loads, computed styles identical, 5 tabs / 255 markers / 1,083 search index, map renders unchanged.
2. **JS → `app.js`** — keep as **one file** (code relies on top-level function hoisting + shared globals `layers`, `wellsLegacyF`, `SEARCH_INDEX`). Do *not* split into ES modules.
3. **Data → `config.json` / `findings.json` / `statistics.json`** — highest risk: introduces async load ordering. `statistics.json` must be emitted by a generator script run on every data change, or the drift just moves.

**Cache-busting:** every split file needs a `?v=` query or returning visitors get a stale JS/CSS mix.
