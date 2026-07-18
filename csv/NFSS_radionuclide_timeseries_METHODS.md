# NFSS radionuclide time series — methods & limits

Prepared 2026-07-18. Per-well **Total Uranium** (µg/L) and **Radium-226** (pCi/L)
groundwater trends for the Niagara Falls Storage Site (NFSS, Lewiston, FUSRAP-LM),
integrated into `web/data/wells_legacy.geojson` (site = "Niagara Falls Storage Site").

## Source
USACE Buffalo District **NFSS Environmental Surveillance Technical Memoranda** (annual).
The radionuclide groundwater results table has an **identical layout every year**; only the
table number changes (e.g. 2013 = Table 15, 2020 = Table 13). Semiannual sampling; the
value carried per year is the reported result (higher of the two events where both detect).
- Uranium NYSDOH standard 30 µg/L; Radium-226 criterion 5 pCi/L.

## Coverage — 5 years extracted: 2011, 2012, 2013, 2019, 2020
- 55 NFSS wells updated; **51 carry a 3+-year uranium series**; Radium-226 where reported.
- Examples: MW954 U 687 → 532 → 561 (2013/2019/2020); OW11B U 378→353→355→450→401
  (2011–2020); MW921 U 30→26→31→35→43 (slow rise). Hotspot uranium is broadly
  **stable-to-slightly-declining**, not a runaway trend.

## Limits / vulnerabilities to verify by hand
1. **2014–2018 gap.** 2014/2015/2016 memos are **truncated in the Internet Archive**
   (each capture is exactly 1 MB, header valid but body cut off) and blocked at the USACE
   `.mil` origin (Akamai CDN + shared DoD TLS cert). 2017 memo downloads intact but its
   radionuclide table uses a **different, non-position-parseable layout** (no "Location
   Identifier" header) — not yet extracted. → get full 2014–2017 PDFs via **FOIA/USACE
   direct request** or a non-truncated archive capture.
2. **Pre-2011 (2006–2010).** 2008–2010 memos downloaded but use an **older table format**
   (finder returns 0 pages); 2006/2007 returned HTTP 401 from Wayback. Not extracted.
3. **Position-based parsing.** Values are read by column x-position and analyte-row y-band
   (nondetect = a 'U' qualifier token immediately right of the value). Criteria columns
   (3/5/15/27/30) are skipped by x<235. Spot-check a handful of wells against the source
   tables — jumbled-text pages (qualifiers interspersed) are the main risk.
4. **Well-ID normalization.** GW→MW; trailing "R" (replacement wells) stripped so a
   replacement joins its predecessor's series. Confirm no two physically distinct wells
   were merged.
5. **Coordinates** are `coord_precision = georeferenced_2015_ESP_aerial` (from the 2015
   ESP figure), i.e. approximate placements, not survey coordinates.

## Files
- `csv/nfss_radionuclide_timeseries.json` — raw extracted series `{well:{analyte:{year:[value,detect]}}}`.
- `csv/nfss_radionuclides_2020.json`, `csv/nfss_wells_figure5.json` — 2020 snapshot + well locations.
- Extractor: `scratchpad/nfss_series_extract.py` (working tree). Fast page-find via
  pypdfium2, then pdfplumber position-based table parse of only the matched pages.
