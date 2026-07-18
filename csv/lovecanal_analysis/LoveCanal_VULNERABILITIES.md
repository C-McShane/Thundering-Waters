# Love Canal Analysis — Vulnerabilities, Limits & Hand-Check Guide

**Purpose.** Everything a reviewer must independently verify before any Love Canal
hydraulic claim goes public. Written for NYT-level scrutiny. Updated 2026-07-17
after a **major self-caught error** (see #1) that retracted the earlier
"string 1190 shallow weak-link" finding.

---

## 0. Bottom line after correction

- The geologic-medium labels in the first-cut analysis were **wrong** (a bad
  letter→medium assumption). Fixed by a per-well authoritative lookup.
- After correction: the **inside/outside well-pair gradient method does not apply
  to the shallow water-table unit (Silty Sand/Fill) at these strings.** All 6
  shallow wells in the network are OUTBOARD sentinels; none is screened inside the
  drain ring — as expected, since inside the ring is the buried waste mass, not a
  place to screen a clean water-table piezometer (the inside wells that exist,
  e.g. 1180A/1190A, are all deep). So "mean(out) − mean(in)" simply can't be formed
  for the shallow unit. This is a **method-applicability limit, not negligence and
  not evidence of a breach.**
- What the shallow data DOES show is **containment-consistent**: every outboard
  shallow head sits 6–13 ft ABOVE the local drain-invert elevation (water table
  drains down toward the lower barrier drain), and every *paired* deeper unit holds
  a strong inward gradient (+2 to +5 ft). Nothing here is alarming.
- The only persistent "outward" number is in the **deep Glacial Till at string
  1190** (single inside well 1190A reading high). The deep-till inside/outside
  comparison is **not a shallow-containment metric regardless of cause** — it
  reflects basal confined-aquifer head and requires hydrogeologic interpretation.

---

## 1. [CRITICAL, FIXED] Geologic medium was mislabeled from the 2015 letter blocks

**What happened.** The 2015 PRR tabulates water levels in letter blocks
("A Wells" … "D Wells"). The first-cut code assumed
`A=Silty Sand/Fill, B=Fractured Clay, C=Soft Clay, D=Glacial Till`.
**That mapping is false.** The suffix letter is *not* a medium code — it varies by
well cluster. Authoritative 2016–2022 headers show:

| well | true medium | | well | true medium |
|------|-------------|-|------|-------------|
| 1180A | Glacial Till | | 1140A | **Soft Clay** |
| 1190A | Glacial Till | | 1144A | **Silty Sand/Fill** |

So `A` means Glacial Till at 1180/1190 but Soft Clay at 1140 and Silty Sand at 1144.

**Impact.** The earlier headline — "string 1190's *shallow* gradient is
marginal/outward, 3 reversals, the containment-relevant weak link" — was the
**deep Glacial Till** readings mislabeled as shallow. Retracted.

**Fix.** `web/lovecanal_medium_lookup.py` builds `WELL_MEDIUM` from the 2016–2022
`"X Medium"` headers and assigns medium per well by ID (join key = suffixed well
ID, e.g. `1190A`). Applied in `lovecanal_aux.py` and `lovecanal_gradient_corrected.py`.

**Hand-check.** Open any 2016+ PRR, Tables 3.6A–F. Confirm the well IDs printed
under each `"… Medium"` header match `WELL_MEDIUM`. Run
`python web/lovecanal_medium_lookup.py` to list all 6 shallow wells.

**Residual risk.** The join assumes a 2015 block-letter well is the *same physical
well* as the identically-named 2016 well. Validated by value continuity (2015 vs
2016 means agree to < 0.6 ft for all 16 tested wells across 4 strings). Two
2015-only wells (**1173D, 1174D**, decommissioned) have no authoritative medium and
are **dropped** from medium-keyed outputs rather than guessed.

---

## 2. [STRUCTURAL] The well-pair gradient method doesn't apply to the shallow unit

Only **6 shallow (Silty Sand/Fill) wells exist** in the whole barrier-drain network:
`1144A, 1151D, 1163D, 1165C, 1165D, 1183D`. Every one that reports data sits
**outside** the tile drain (verified across all years: 1144A/1165C/1165D/1183D/1151D
= 100% outboard, never once inside; 1163D reports no water level). **No shallow well
is screened inside the drain ring** — by design, since inside the ring is the buried
canal waste. So `mean(out) − mean(in)` has an empty side and the classic inward-
gradient number can't be formed for the shallow unit at any string.

- Strings **1170 and 1190** (the 99th-St flank): **no shallow well at all**.
- String **1180** (closest to the leak): **one** shallow well (1183D), still no pair.

**Correct framing (do NOT overstate).** This is a *method-applicability* limit, not
a "monitoring gap"/negligence and not evidence of a breach. The site operator can
fairly say the outboard shallow wells are *detection sentinels*. Importantly, the
shallow data that exists is **containment-consistent**: outboard shallow heads sit
6–13 ft ABOVE the local drain invert (see #5), i.e. the water table slopes down
toward the lower drain. The defensible statement is: *"the inward-gradient method
cannot be applied to the shallow unit here; the available shallow heads and all
paired deeper gradients are containment-consistent."* **Hand-check:** run
`web/lovecanal_gradient_corrected.py` (prints "SHALLOW … computable? NO") and the
side/head verification in this analysis.

---

## 3. [STRUCTURAL] Every computable gradient rests on ONE inside well (n_in = 1)

For all computable string×medium cells except `1160 Fractured Clay` (n_in=2), the
"inside" side is a **single piezometer**. One survey-datum error, one screen-depth
quirk, or one bad reading flips the sign. The 1190 Glacial Till "outward" signal is
entirely well **1190A**. **Hand-check:** `wells_in` column in
`lc_gradient_records_CORRECTED.csv`.

---

## 4. [METHOD] Inside/outside — CONFIRMED by the report's own table note

Classification rule: within a medium block, a well is OUTSIDE if its column center
is left of the `"Tile Drain"` column, INSIDE if right. This is NOT a guess — the
Table 3.6 note states it verbatim: *"Wells listed from left to right in order from
most distant outside of tile drain, to tile drain, then inside of tile drain."* So
the base "…0" well of each string (1140A/B, 1160A/C, 1170A/B, 1180A/B/C, 1190A/B)
is the INSIDE-drain monitoring point; the satellites (114x, 116x, 117x, 118x, 119x)
are outside. String 1150 has NO inside well (all outside). This matches the site
operator's design intent and the field geometry.

Residual check the reviewer still owns: the note fixes the table *ordering*; our
parser must read column order correctly (validated well-by-well in the audit CSVs).
Blocks with **no Tile Drain column** (some intermediate-clay blocks) are **skipped**
— those cells are absent, not zero. **Hand-check:** `lc_gradient_audit_1180.csv` /
`lc_gradient_audit_1190.csv` list every well, side, and level per date; the
"blocks skipped" list is printed by `web/lovecanal_gradient_audit.py`.

---

## 5. [METHOD] Deep Glacial Till is not a shallow-containment metric

Note on the "Tile Drain" table column: its value is **constant per string across
every date and medium** (1140=561.70, 1150=561.85, 1160=560.60, 1170=555.60,
1180=560.00, 1190=554.80 ft) — i.e. it is the **drain invert elevation**, a fixed
datum, NOT a measured water level. That is precisely why there is no "inside water
level" to pair the shallow outboard heads against (#2). The outboard shallow heads
sit several feet above their string's invert (e.g. 1183D ~566.7 vs 560.0; 1165C/D
~570–574 vs 560.6), consistent with a water table draining toward the lower drain.

At string 1190 the inside deep well (1190A, ~565–568 ft) reads above the outboard
deep wells (~564–565 ft) and well above the 1190 drain invert (554.8 ft). An
upward gradient from the basal confined till is a **known regional condition** and
is hydraulically **separate from the shallow leachate-bearing zone the drain
targets**. Whether the elevated deep head is natural or partly anthropogenic is an
**open hydrogeologic question** — do NOT assert either. It does not by itself
indicate shallow containment failure.

---

## 6. [RESOLUTION] No event-scale data — transient overwhelm is untestable here

- Water levels (Tables 3.6) are **quarterly**; pump volumes (Table 3.1) are
  **monthly**. Neither resolves a **storm-peak** transient, which is exactly when a
  short-lived overwhelm would occur.
- The user's original "were the pumps overwhelmed in wet years?" question is
  answerable only at monthly resolution, where peak load (~30 GPM in the wettest
  year, 2017) stayed far under capacity (~50 GPM/pump, ~600 GPM system). **A
  transient overwhelm cannot be confirmed or excluded** from these documents.
- **To go further (hand):** request continuous transducer logs, daily precipitation
  (NCDC Niagara Falls Int'l), pump run-time/SCADA, and SPDES Discharge Monitoring
  Reports. None are in the PRR bodies checked.

---

## 7. [DATA] Table 3.1 volume parse — known soft spots

- 2022 PRR volume table = 22 tight columns; position-binning failed. Monthly
  **volumes** were taken from the **2019 PRR (2000–2019)**; **precipitation**
  2000–2021 recovered positionally from 2022. Any 2020–2022 monthly volume is NOT
  in the dataset. **Hand-check:** `lc_monthly_volumes.csv` ends 2019.
- Monthly GPM = Net gallons / (discharge-days × 1440). If "discharge-days" is
  reported inconsistently across years, per-month GPM drifts. Spot-check against the
  raw table.

---

## 8. [SPATIAL] Leak location and piezometer coords are hand-collected

- Piezometer lat/lons were read from report **figure** map positions + Google Maps —
  good to perhaps ±20–50 m, adequate for which-side-of-99th but not survey-grade.
- The confirmed contamination ("pool digger, residential side of 99th between
  Colvin Blvd and Moschel Ct") geocodes to ~43.0867, −78.9482. **Nearest string is
  1180** (~230 m), which holds a strong inward gradient in every *computable*
  (deep/intermediate) unit; string 1190 is ~560 m south. The data-anomaly (1190
  deep till) and the leak are **not co-located** — do not imply a direct pathway.
- **Hand-check:** `csv/love_canal_coords/love_canal_wells.csv` (raw hand picks);
  some rows store `"lat, lon"` combined in the lat cell (handled in code, worth a
  visual scan).

---

## 9. Files

| File | What |
|------|------|
| `web/lovecanal_medium_lookup.py` | authoritative well→medium (the fix) |
| `web/lovecanal_gradient_corrected.py` | corrected gradient analysis |
| `web/lovecanal_gradient_audit.py` | per-well raw dump for 1180/1190 |
| `lc_gradient_records_CORRECTED.csv` | per string×medium×date, with well lists |
| `lc_gradient_summary_CORRECTED.csv` | roll-up + computability |
| `lc_gradient_audit_1180.csv`, `_1190.csv` | fully auditable raw well readings |
| `lc_gradient_*.csv` (no _CORRECTED) | **SUPERSEDED** first-cut (bad media) — kept for provenance only |
| `METHODOLOGY.txt` | narrative (finding #4 retracted) |
