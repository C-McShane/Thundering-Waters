# Former Mill No. 2 (Greenpac Mill) — groundwater chemistry & radioactive characterization

Prepared 2026-07-18. NYSDEC BCP Site **C932150**. Source: **Revised RI Report (ERM, May 2012)**,
Tables 5, 6a–6d and §3.2.7; well locations from Figure 4 (site boring map). Integrated into
`web/data/wells_legacy.geojson` (site = "Former Mill No. 2 (Greenpac Mill)") — 15 wells.

## The radioactivity is SOIL, not groundwater — read this first
Mill No. 2's radioactive contamination is **radioactive slag** (uranium, thorium, radium) in
historic fill, delineated by a **gamma survey** (Ludlum 2221 meter) as "rad zones" exceeding the
NYSDEC guidance value of **10,000 cpm** (site background 6,000–8,000 cpm) and confirmed by
gamma/alpha spectroscopy (§3.2.7). It is **not a groundwater radionuclide plume** — there is no
uranium/radium groundwater time series here (unlike NFSS Lewiston). The wells' *groundwater*
contamination is a separate issue: chlorinated VOCs migrating from the adjacent **Frontier
Chemical property**. Both facts are carried in each well's `well_desc`.

## Groundwater dataset — a single snapshot per well, NOT a time series
Two distinct well sets, sampled once each; the PRRs (2013, 2018) contain **no** post-RI
groundwater monitoring, so no multi-year series exists.
- **2008** (Labella wells): MW-1, MW-2, MW-3 — VOCs/SVOCs/pesticides (no metals run).
- **2011** (RI wells): MW-02, MW-03, MW-04, MW-08, MW-09 — VOCs/SVOCs/pesticides/metals.
- Not sampled (carried as no-data wells): MW-01/05/06 (dry), MW-07 (dry), MW-10/11
  (destroyed), MW-4 (2008 Labella well, not sampled — kept for RI "MW-1 through MW-4" completeness).

### Critical: MW-1 ≠ MW-01 (and MW-2 ≠ MW-02, MW-3 ≠ MW-03)
The 2008 "MW-1/2/3/4" and 2011 "MW-0X" are **different physical boreholes** (Table 5: MW-3 total
depth 13.45 ft / unsurveyed vs MW-03 12.10 ft / elev 571.20; the site map labels them MW-1 (SB-5)
vs MW-01 (B-169)). They are **never merged** into a 2008→2011 trend — doing so would fabricate one.

### Toxic exceedances (bracketed = above NYS TOGS standard in the source tables)
- **MW-3** (2008): Chlorobenzene 6, 1,2-DCB 21, 1,3-DCB 34, 1,4-DCB 25, cis-1,2-DCE 13,
  1,2-DCA 0.7 µg/L — the Frontier Chemical VOC signature.
- **MW-2** (2008): Bis(2-ethylhexyl)phthalate 11 µg/L (the "one SVOC" of the RI narrative).
- **MW-09** (2011): Antimony 4.9 µg/L.
- Sodium / Iron / Magnesium / Manganese exceedances (MW-02/03/04/08) are **secondary
  (aesthetic)** standards only — flagged as such, not counted as toxic.

## Well locations
The 11 original wells were georeferenced from Figure 4; the two missing sampled/real wells
(**MW-2, MW-08**) and MW-07 were placed with the **same affine transform** fit to those 11
(RMS residual 0.1–0.2 m — the transform inverts the original georeferencing near-exactly).
`coord_precision = georeferenced_figure_approx` (approximate, not survey).

## Limits / vulnerabilities
1. **Curated-lexicon filter.** Analytes outside `well_chem_lexicon.py` are dropped from the
   filterable `chems` list; BEHP was re-injected by hand because it is MW-2's key exceedance.
   Other non-curated detections (e.g. phthalates elsewhere) may not appear in the dropdown.
2. **Position-based parse.** Values read by column x-position; exceedances are bracketed `[21]`
   and estimates carry a `J`. Spot-checked MW-3 and MW-04 against the source tables.
3. **No radionuclide quantification in groundwater** — the slag radioactivity is soil/cpm-survey
   (Appendix C); pCi/g soil values were not extracted into the well layer (soil, not per-well GW).

## Files
- `csv/mill2_gw_chemistry.json` — extracted per-well groundwater detections.
- `csv/mill2_exceedances_raw.json` — every bracketed (standard-exceeding) value, raw analyte names.
- `csv/mill2_wells.json`, `csv/mill2_missing_wells.json` — well coordinates.
- Extractor: `scratchpad/mill2_gw_extract.py`; integration: `scratchpad/mill2_integrate.py`.
