# Selected high detections — citation checklist

_Generated from `web/data/findings.json`. Every entry below renders a visible **PENDING** marker in the interface until its citation block is complete, so an uncited number can never look finished._

**Required per entry (8 fields):** `report_title`, `table`, `page`, `sample_medium`, `sampling_date`, `comparison_standard`, `source_link`, `selection_criterion`

**How to fill:** edit `web/data/findings.json` — replace `"Information to be added"` with the real value. No code change needed; the UI reads the JSON. Re-run nothing.

> ⚠️ The **Lead** column below is a *lead to verify against the source PDF*, not a filled value. Do not paste it in without checking the page.


## Radiation — Covanta Niagara Rail-to-Truck Intermodal Facility

### Site-wide gamma peak — 420,000 CPM
- **Missing (8/8):** `report_title`, `table`, `page`, `sample_medium`, `sampling_date`, `comparison_standard`, `source_link`, `selection_criterion`
- **Lead (verify):** Covanta RI (LaBella, 2013) §7.2 — PDF p.44; corroborated in Appendix S (GRD survey) §3.0 — PDF p.631. Gamma walkover survey, data through 8/7/2012. NOTE: exact location NOT stated in the RI.
- [ ] citation complete

### 120,000–170,000 CPM at the TP-03 cluster
- **Missing (8/8):** `report_title`, `table`, `page`, `sample_medium`, `sampling_date`, `comparison_standard`, `source_link`, `selection_criterion`
- **Lead (verify):** Covanta RI §7.3 — PDF p.45. Site background stated as 5,526–7,522 CPM (§7.2, p.44).
- [ ] citation complete

### Radium-226 in slag — up to 35 pCi/g
- **Missing (8/8):** `report_title`, `table`, `page`, `sample_medium`, `sampling_date`, `comparison_standard`, `source_link`, `selection_criterion`
- **Lead (verify):** Covanta RI, gamma-spectroscopy of slag samples (EPA 901.1m), Appendix. Value from spatial/covanta_slag_radionuclides.json (max Ra-226 = 35.1 pCi/g). Medium: soil/slag, pCi/g. 2012.
- [ ] citation complete

### Five gamma hot spots >16,000 CPM
- **Missing (8/8):** `report_title`, `table`, `page`, `sample_medium`, `sampling_date`, `comparison_standard`, `source_link`, `selection_criterion`
- **Lead (verify):** Covanta RI Figure 15 "Radiological Hot Spots" — PDF p.85. Areas 670 / 835 / 857 / 1,507 / 630 m². Survey data through 8/7/2012.
- [ ] citation complete

## Radiation — Former Mill No. 2 (Greenpac Mill)

### Seven gamma slag zones >10,000 CPM
- **Missing (8/8):** `report_title`, `table`, `page`, `sample_medium`, `sampling_date`, `comparison_standard`, `source_link`, `selection_criterion`
- **Lead (verify):** NYSDEC BCP C932150 Revised RI (ERM, 2012), Figure 3 & §3.2.7. Background stated 6,000–8,000 CPM.
- [ ] citation complete

## Chemicals — Frontier Chemical – Royal Ave

### Trichloroethene (TCE) — 180,000 µg/L
- **Missing (8/8):** `report_title`, `table`, `page`, `sample_medium`, `sampling_date`, `comparison_standard`, `source_link`, `selection_criterion`
- **Lead (verify):** 2022 Periodic Review Report, Frontier Chemical Royal Avenue Site. Digitised to csv/to_add/Frontier_Chemical_Royal_Avenue_2008_2022_groundwater_detections.csv. Medium: groundwater, µg/L. PAGE NOT YET PINNED.
- [ ] citation complete

### Tetrachloroethene (PCE) — 120,000 µg/L
- **Missing (8/8):** `report_title`, `table`, `page`, `sample_medium`, `sampling_date`, `comparison_standard`, `source_link`, `selection_criterion`
- **Lead (verify):** As TCE — same report/well (MW-88-8A). PAGE NOT YET PINNED.
- [ ] citation complete

### Vinyl chloride — 25,000 µg/L
- **Missing (8/8):** `report_title`, `table`, `page`, `sample_medium`, `sampling_date`, `comparison_standard`, `source_link`, `selection_criterion`
- **Lead (verify):** As TCE — same report, well MW-88-12A. PAGE NOT YET PINNED.
- [ ] citation complete

### PFAS (PFOA/PFOS) — 1,700 µg/L
- **Missing (8/8):** `report_title`, `table`, `page`, `sample_medium`, `sampling_date`, `comparison_standard`, `source_link`, `selection_criterion`
- **Lead (verify):** As TCE — same report, well MW-01-9A, 2019. PAGE NOT YET PINNED.
- [ ] citation complete

## Chemicals — Covanta 15-Acre Site

### Chromium — 2,230 mg/Kg
- **Missing (8/8):** `report_title`, `table`, `page`, `sample_medium`, `sampling_date`, `comparison_standard`, `source_link`, `selection_criterion`
- **Lead (verify):** Covanta RI Table 3d (test-pit metals) — PDF p.96. Medium: soil, mg/Kg. 2012. Point TP-14.
- [ ] citation complete

### Benzo(a)pyrene — 21.6 mg/Kg
- **Missing (8/8):** `report_title`, `table`, `page`, `sample_medium`, `sampling_date`, `comparison_standard`, `source_link`, `selection_criterion`
- **Lead (verify):** Covanta RI Table 2a (surface-soil SVOCs) — PDF p.90. Medium: soil, mg/Kg. 2012. Point SS-01.
- [ ] citation complete

### Arsenic — 74.6 mg/Kg
- **Missing (8/8):** `report_title`, `table`, `page`, `sample_medium`, `sampling_date`, `comparison_standard`, `source_link`, `selection_criterion`
- **Lead (verify):** Covanta RI Table 3d (test-pit metals) — PDF p.96. Medium: soil, mg/Kg. 2012. Point TP-18.
- [ ] citation complete

## Chemicals — Niagara Sanitation Co.

### Xylene — 1,700 µg/L
- **Missing (8/8):** `report_title`, `table`, `page`, `sample_medium`, `sampling_date`, `comparison_standard`, `source_link`, `selection_criterion`
- **Lead (verify):** Groundwater & Surface Water Monitoring Report, Niagara Sanitation Site. Digitised to csv/to_add/Niagara_Sanitation_1984_2020_...csv. Well OW-36, 2014. PAGE NOT YET PINNED.
- [ ] citation complete

### Lead — 600 µg/L
- **Missing (8/8):** `report_title`, `table`, `page`, `sample_medium`, `sampling_date`, `comparison_standard`, `source_link`, `selection_criterion`
- **Lead (verify):** As Xylene — same report, well OW-16, 1988. PAGE NOT YET PINNED.
- [ ] citation complete

---

## Fields that still need a decision (not per-entry)

- **`comparison_standard`** — we must name the standard rather than implying one. Candidates to settle: federal **MCL** vs **NYSDEC AWQS** for groundwater (TCE/PCE/vinyl chloride/PFAS), and **NYSDEC Part 375 SCOs** (which use? Unrestricted / Residential / Industrial) for soil (chromium, benzo(a)pyrene, arsenic). The TCE line currently says "~36,000× the 5 µg/L water limit" — **5 µg/L is the federal MCL**; confirm before publishing, and state which standard.
- **`selection_criterion`** — one sentence per entry explaining *why this entry was selected* (e.g. "highest recorded value for this analyte in the mapped network"). Needs to be consistent across entries or the list looks arbitrary.
- **Page numbers for the CSV-derived sites** (Frontier Chemical, Niagara Sanitation) — we worked from digitised tables, so report + table are known but the page is not. Either pin the pages in the source PDFs or state "table digitised; page not recorded".

**Total fields outstanding: 112** across 14 entries.
