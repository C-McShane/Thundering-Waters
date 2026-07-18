# Direction #2 — Love Canal chemistry extended to 2010–2019

Prepared 2026-07-17. Source: DecDocs 932020 PRRs for 2010–2014 (downloaded to
`docs/`, Table 3.2/3.3 analytical results), parsed by `/tmp/extract_ext.py` →
`csv/lovecanal_analysis/lc_extended_chem_2010_2014.csv` (1,024 well×chem×year rows,
49 wells, mobile VOCs). Merged with existing 2015–2019 ConcSeries → 2010–2019 view.

## Data quality notes (hand-check targets)
- YEAR-PARSE BUG caught + fixed: first pass read the day from "6/13/2012" as the
  year (→ 2013). Fixed to capture the 3rd date field. Validated: 10135 chlorobenzene
  2010–2019 = 1300,1100,2500,(2013 n/a),2300,2600,2700,2600,2400 — coherent.
- **2013 PRR under-extracted** (only 96 values vs 280–688 for other years; the 60 MB
  file's body tables parsed poorly). 2013 is a GAP. 2018 also absent (not in the
  2015–2022 PRR tables we parsed). So usable Love Canal years = 2010,2011,2012,2014,
  2015,2016,2017,2019 (8 of 10).
- Detect logic: value with no U/UJ/R qualifier = detect; U/UJ/R = non-detect at that
  reporting limit. Watch detection-limit changes across years (a lower limit reveals
  trace that was always there — NOT an increase; see 2019 BTEX below).

## The sewer-event signature test (the point of extending)
Question: did the groundwater near the Colvin corridor show any contaminant response
to the Feb 2011 sewer NAPL discovery/excavation?
- **No coherent spike.** The near-corridor overburden wells (8106, 8110, 8140, 7161,
  7155, 7132, 7130, 8210, 3257, 10278) are non-detect or sub-1 µg/L trace throughout
  2010–2019, INCLUDING 2011–2012.
- Only two trace, one-off hits near the event: 7130 toluene 1.2 µg/L (2011) and
  10225B toluene 3.0 µg/L (2012) — both trace, non-persistent, single-well. Not a plume.
- The 2019 BTEX at 8110/8140/10278 is the known detection-limit artifact (values below
  the earlier 5.0 limit), not a real arrival.
- 10225C bedrock (near the repair) carries persistent trace TCE (13→6.5) + chlorobenzene
  (~1–2), essentially flat/declining — no event step.

INTERPRETATION: consistent with everything prior. The sewer NAPL rode the trench
bedding, not the aquifer these wells sample, so the groundwater network did not register
it — matching MW-3's no-NAPL-recurrence (2011–2018) and the clean nearby groundwater.
The extension neither reveals a groundwater plume nor refutes the sewer pathway; it
confirms the monitoring network is blind to a trench-bedding pathway.

## 10135 (SW source, opposite flank) 2010–2019
Chlorobenzene ~1,300→2,500 (rose 2010–12, then stable ~2,500); benzene ~3,400→~6,000
(stable from 2012); toluene ~11,000→~20,000 (stable from 2012); TCE 140→28 (declining).
A stable-to-slightly-rising DNAPL source pocket, SW, ~950 m from the pool digger —
unrelated to the Colvin/99th corridor. Matches EPA's "isolated, stable" characterization.

## Map-ready / saved
- `csv/lovecanal_analysis/lc_extended_chem_2010_2014.csv` — the new years, durable.
- Georeferenceable figures identified in the 2012 PRR (not yet extracted): site plan
  (barrier drain, lateral trenches, 102nd St transfer line), 1180 cross-section, June
  2012 flow contours — candidates for a future map layer.

## Still chasing (as we go)
- March 2011 SSIR report (actual NAPL/sediment concentrations near the leak) — not yet
  located; try DEC DER search / EPA SEMS / the 2011–2012 PRR appendices.
- Primary DEC "predates" determination — exact wording for citation.
