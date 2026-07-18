# Love Canal — "Can any signal be traced to a well?" + migration/rainfall test

Prepared 2026-07-17. Scripts: `web/lovecanal_outboard_chem.py` and the ranked/
trend queries logged in this analysis. Chemistry source: `Niagara_DEC_Wells_
ConcSeries.json` (2015, 2016, 2017, 2019 — 2018 not sampled). Precip: `lc_annual_
load_precip.csv`.

## Question
Test the hypothesis that Love Canal contamination — from a discrete past event
(pre-1978 or later), not catastrophic failure — is migrating slowly through clay
and now showing up in outboard wells, possibly amplified by wet years, en route to
the confirmed 99th St / pool-digger contamination (10–15 ft deep, ~176 m N of the
nearest well).

## The one genuine hotspot
- **10135** (overburden, OUTSIDE the barrier, ~948 m SW of the pool digger):
  Toluene ~20,000, Benzene ~6,000, Chlorobenzene ~2,600 µg/L. A real, large
  off-barrier contaminant body. Answers "can anything be traced to a well?" — YES,
  but it is on the **opposite (SW) flank** from 99th St, and it is **flat-to-
  declining** (TCE 110→28, PCE 17→5.3, VC 15→3.9, chloroform 180→60 across
  2015–2019). Also a real bedrock cluster at 10225A/B/C (~780 m, peak TCE 15,
  also declining).
- Near 99th St (the pool-digger flank): everything is **trace** (<1.1 µg/L).

## The migration test (controlling for detection limits) — decisive
A later DETECT only counts as a real increase if it **exceeds what earlier years
could have hidden** (their reporting limit). Result:
- **No well anywhere shows a genuine, physically coherent increase.**
- The apparent "increases" are artifacts:
  1. **2016 Lindane lab-batch artifact.** Lindane "spikes" (0.1–0.6 µg/L) appear
     *simultaneously* in 2016 across wells spanning **780–1294 m apart**, then
     vanish in 2017. Physical migration cannot hit wells that far apart in the same
     year and then disappear — this is a laboratory batch/calibration artifact, not
     an environmental signal.
  2. **2019 BTEX detection-limit artifact.** Benzene/toluene/xylene "appear" at
     8110/8140 (99th St flank) in 2019 at 0.3–1.1 µg/L — but every value is **below
     the 5.0 µg/L limit** the 2015/2017 samples were reported to. A 0.33 detect is
     not more benzene than a 2015 "non-detect <5.0". The lab looked harder in 2019;
     the contaminant was plausibly always present at trace level.
- Therefore the "cyclic/sinusoidal" appearance (2015 high → 2016–17 low → 2019
  high) is **two unrelated causes at opposite ends** (2015 trace pesticides; 2019
  limit-revealed BTEX), not one oscillating plume.
- Genuine temporal trends that ARE real all point **down** (declines at the 10135
  source and across the site).

## The 1190 deep-pressure "pocket" under a relaxed (not-necessarily-natural) assumption
Facts that survive scrutiny:
- **Unique:** 1190 is the only string whose DEEP Glacial Till reverses (inside
  higher than outside); 1140/1170/1180 deep till are all strongly inward (+2 to +5).
- **Small & deep:** ~1–3 ft, in the basal till *below* the drain/leachate zone,
  with **no chemistry** screened there to corroborate.
- **Transient:** gone by 2022 (all four quarters back to inward).

Claims that DO NOT survive scrutiny (do not use):
- "It tracks precipitation." corr = −0.45 looks suggestive but is **pseudo-
  replicated**: 16 quarterly points carry only **4 distinct annual precip values**,
  so effective n = 4 (significance threshold r ≈ 0.95). Not meaningful. Worse, the
  single most-reversed reading (2016-03, −3.28 ft) falls in the **driest** year —
  contradicting the correlation.
- "Rain-response proves it's not natural." False lever: confined tills respond to
  seasonal recharge routinely, so a correlation (even if real) wouldn't distinguish
  natural from anthropogenic.

Verdict on 1190: a documented **footnote curiosity** (unique, small, gone), not a
demonstrated pathway to the pool digger 560 m north.

## Bottom line — untestable, NOT refuted
The slow-clay-migration-from-an-old-event hypothesis is **largely untestable with
the current data**, for two hard reasons:
1. **No wells at the pool-digger location** (nearest is 176 m S, at the canal edge).
2. **Only 4 annual chemistry years (2015–2019).** A declining 4-year snapshot is
   equally consistent with "nothing was ever there" AND with "we are on the down-
   slope of a pulse that peaked before 2015." Decline does not distinguish them.

So the data does not show arrival, and it does not rule out a past pulse.

## 102nd St 18-year test (the fair test of the rainfall/lag idea) — NULL
102nd St (932022), adjacent to Love Canal, shares the aquifer + rainfall and has
~18 annual chemistry years (2002-2019). Wells PCM-03/04/05 carry continuous
high-concentration detects (chlorobenzene up to 12,000 ug/L) — high enough that
detection-limit artifacts are irrelevant. Scripts: `web/lovecanal_102nd_lag.py`,
outputs `lc_102nd_lag_results.csv`, `lc_102nd_series.csv`.

Pearson r between precipitation (lagged 0-3 yr) and concentration, on raw levels
AND year-to-year first differences (detrended):
- **24 lag tests, 1 "significant" at p<0.05 — exactly the ~1.2 expected by chance.**
  Largest |r| = 0.34 (below significance). The one hit (PCM-03 Lindane, lag-1) is
  NEGATIVE (wrong direction) and in the artifact-prone pesticide.
- **Conclusion: contaminant concentration does NOT track rainfall at any lag**, even
  with 18 years and full statistical power. The "wet year -> contaminant spike"
  mechanism is not operating here.
- What the chemistry DOES do is slow and decadal, unrelated to rain: chlorobenzene
  a decade-long rise-then-fall (PCM-04 6,300 -> 12,000 by ~2008-10 -> 8,000);
  benzene a steady multi-year decline (PCM-03 133 -> 36; PCM-04 228 -> 27). This is
  source/attenuation behavior.

Scope note: this tests rainfall-modulation of concentration at ALREADY-contaminated
wells (strongly refuted). It does NOT test lateral migration to NEW locations (no
clean 102nd St well turns contaminated in the record). The decadal benzene decline
is itself consistent with the receding tail of an older/attenuating source — i.e.
it neither proves nor disproves the "old pulse" idea, but shows the system is driven
by slow internal dynamics, not rain pulses.

## To actually test it — data to hunt (answers "can we find more?")
- **Pre-2015 RI/RA reports** for Love Canal (surveyed wells + older chemistry) —
  the only way to see whether a pulse peaked and receded before the current window.
- **102nd St site (932022) 2002–2019** time series (already flagged in project
  notes) — adjacent, longer record, connected by the leachate transfer line.
- **Quarterly chemistry** if any exists in PRR appendices (current JSON is annual).
- **New shallow/overburden wells between the canal edge and the pool digger** on
  99th St — the actual gap.
