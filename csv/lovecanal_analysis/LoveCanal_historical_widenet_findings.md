# Direction #3 — historical record + widened net (blind to the 99th pathway)

Prepared 2026-07-17. Goal: archive everything (audit survival); look for ANY
Love Canal contamination/pathway anywhere, deliberately NOT focused on 99th St.

## Archive (audit-survival copy) — in progress
Downloading the full DecDocs 932020 repository (176 PDFs, 1977–2024) to
`docs/DecDocs_932020_archive/`. At last check: ~79/176 files, ~730 MB, still
running. Plus `docs/occ_annuals/` = 11 OCC/O&M annual reports (1999–2009 data)
pulled separately for analysis. Script: `scratchpad/dl_archive.py`
(re-runnable; skips already-downloaded files).

## Wide-net result A — 2015–2019, all wells / all chemicals / all directions
`csv/lovecanal_analysis/lc_widenet_contamination_2015_2019.csv`. Contamination is
overwhelmingly SOUTH: MW-10135 (23,000 µg/L toluene/benzene/chlorobenzene) + the
10225 bedrock cluster (TCE 15). North (99th flank) and East are all trace (<1.1).
No hidden hotspot in another direction. NOTE: current set = 55 of ~153 site wells.

## Wide-net result B — narrative sweep 1999–2009 (Track A, text)
Every OCC annual's own conclusion: "chemical analytical results are consistent with
previous Long-Term Monitoring analytical results" (1999–2000 add "minimal detection
of chemicals"). NO year flagged an anomaly, new hotspot, or barrier failure.
Discrete-compound counts where stated: 2008=34, 2009=44 (a modest rise worth a
detection-limit check, not an alarm). Caveat: this is the OPERATOR's self-report —
independent table verification below.

## Wide-net result C — historical detected-compound tables (Track B, text!)
KEY DISCOVERY: the OCC annual DATA TABLES are TEXT-extractable in the older reports
(narrative said scanned, but Tables 3.2/3.3/3.4 in OCC_2000–2006 are text; figures
are the scanned pages). Parsed Table 3.2 (per-well VOC/SVOC/Pesticide detection
counts) for 1999–2001 → `lc_historical_detected_counts_1999_2009.csv`:
- **10135 is the sole major hotspot** (max total 37 detections); every other well
  ≤8, most ≤4 — trace. Independently confirms the operator narrative.
- Historical wells NOT in the current 55-well set (10113,10147,10174A,10178,3151,
  5222,7120,8120,9105,9110,9113,9115,9118,9120,9125,9140) were all LOW-count in
  1999–2001 → no hidden historical hotspot at a now-unmonitored well.
- (Parser got 1999–2001 cleanly; 2002–2009 Table 3.2 has a layout variant — refine
  regex to complete. Narrative sweep already covers all years.)

## THE BIG UNTAPPED SOURCE — Table 3.4 reaches back to 1990
Each OCC annual contains **Table 3.4 "SUMMARY OF DETECTED COMPOUNDS FOR SELECTED
WELLS, 1990 TO <year>"** — a per-well multi-year concentration series from 1990.
OCC_2007's version spans 1990–2007 (TEXT). Plus Table 3.3 gives full current-year
analytical results (text) for 2000,2001,2002,2003,2005,2006,2009.
=> A continuous ~1990–2019 Love Canal concentration series is extractable WITHOUT
OCR. This is the record depth needed to finally test the "old pulse crested before
2015" hypothesis. NOT yet extracted — the next concrete build.

## Bottom line so far
Widening the net across space (all directions), the full current chemical suite, and
two decades of the operator's own record: the only significant off-barrier
contamination is the SOUTH 10135 pocket (stable, isolated per EPA) — NOT the 99th
corridor, and no anomalous year or hidden well anywhere. The 99th sewer pathway
remains a real but low-concentration, point-source issue; it is not where the mass is.

## Next build
1. Extract Table 3.4 (1990–2007) + Table 3.3 (annual) → continuous 1990–2019 series.
2. Re-run the genuine-increase / old-pulse test on the full 30-year record.
3. Finish the archive; refine the 2002–2009 Table 3.2 parser.
