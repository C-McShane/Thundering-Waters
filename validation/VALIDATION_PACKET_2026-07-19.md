# Thundering Waters — Validation & Data-Collection Packet
_Generated 2026-07-19 for hand validation. Coordinates are (lat, lon), WGS84._

Three parts:
1. **Sample points per layer** — with source document + page/figure, for hand validation.
2. **Untagged hazard sites that may hold radioactive waste** — candidates to research.
3. **Niagara Falls (waterfall) monitoring-well data availability** — what exists + where to collect it.

---

## PART 1 — Validation sample points (by layer)

Pull the named document, find the well/point, confirm the coordinate and the chemistry we attached. Where a figure/table is listed, that's exactly where the value or location lives.

### A. Legacy wells & soil (`wells_legacy.geojson`, 233 features)

| Point | (lat, lon) | Site | Source document | Page / figure |
|---|---|---|---|---|
| C4R-MW-06 | (43.08313, -79.00610) | Covanta 15-Acre | Covanta/Praxair RI (LaBella, 2013) — `docs/radioactive_sites/Covanta_RI_Vol1.pdf` | **Fig 7** (p74) — MW locations |
| TP-17 | (43.08731, -79.00412) | Covanta 15-Acre | Covanta RI | **Fig 5** (test pits); metals **Table 3d** (p96) |
| SS-01 (benzo(a)pyrene 21.6) | (43.09015, -79.00303) | Covanta 15-Acre | Covanta RI | **Fig 4** (surface soil); PAHs **Table 2a** (p90); metals **Table 2c** (p92) |
| GP-16 | (43.08297, -79.00645) | Covanta 15-Acre | Covanta RI | **Fig 6** (p73) geoprobes; VOC/SVOC/PCB **Tables 5a–5c** (p101–103) |
| MW-02 | (43.08743, -79.01449) | Former Mill No. 2 | NYSDEC BCP C932150 Revised RI (ERM, 2012) — `docs/radioactive_sites/Mill2_RI_Report_2012.pdf` | **Fig 11** (MW locations) |
| MW-08 | (43.08673, -79.01296) | Former Mill No. 2 | Mill No. 2 RI | soil chem **Tables 6a–6d** / **Fig 4** |
| MW941 | (43.20519, -78.98432) | NFSS | NFSS RI Report Addendum (validated radiological & chemical data) | (validated data tables) |
| MW950 / MW944 | (43.20754, -78.98398) | NFSS | 2020 NFSS Environmental Surveillance Tech Memo (USACE Buffalo Dist.) | **Fig 5**; **Table 13** |
| MW-13 | (43.08996, -79.01017) | Frontier Chemical–Royal Ave | 2022 Periodic Review Report | digitized in `csv/to_add/Frontier_Chemical_Royal_Avenue_2008_2022_groundwater_detections.csv` |
| MW-4S | (43.11380, -79.00181) | Forest Glen | Forest Glen 3Q-2023 Groundwater Monitoring Results — **Table 1** | `csv/to_add/Forest_Glen_2021_2023_monitoring_well_detections.csv` |
| OW-21 | (43.06910, -78.85478) | Niagara Sanitation Co. | Groundwater & Surface Water Monitoring Report, Niagara Sanitation | `csv/to_add/Niagara_Sanitation_1984_2020_...csv` |
| F2M-09 | (43.13147, -79.03771) | Hooker (Hyde Park) Landfill | 2018 Annual Periodic Review Report | `csv/to_add/Hyde_Park_2018_bedrock_well_results.csv` |
| MW-14 / MW-01 / MW-19 | (43.18250, -78.69055) | Eighteenmile Creek | OU3 Phase I & II Data Evaluation Reports; OU3 Revised Proposed Plan | `csv/to_add/Eighteenmile_Creek_2007_2019_...csv` |
| NCR-3S | (43.06032, -78.90582) | Niagara County Refuse | Third Five-Year Review Report | `csv/to_add/Niagara_County_Refuse_2008_2018_...csv` |
| 93-03(1) | (43.10089, -78.93122) | Bell Aerospace Textron | Off-Site System Performance Review | `csv/to_add/Bell_Aerospace_Textron_2022_...csv` |
| 165 / SCMF5 | (43.09202, -78.99969) | CECOS International | HW Groundwater Task Force Evaluation of CECOS | `csv/to_add/CECOS_1986_1991_...csv` (⚠ some well IDs not public) |

### B. Radioactive soil zones (`soil_radzones.geojson`, 9 features)

| Zone | (lat, lon) | Source | Page / figure |
|---|---|---|---|
| Rad Zone 1–7 (Mill No. 2) | e.g. (43.08909, -79.01436) | NYSDEC BCP C932150 Revised RI (ERM, 2012) | **Fig 3** & **§3.2.7** |
| Covanta impacted-slag area | (43.08475, -79.00514) | Covanta RI, Gamma Walkover Survey (Appendix) | — |
| Covanta peak-gamma hot spot (420,000 CPM) | (43.09020, -79.00269) | Covanta RI **Fig 15** & **§7.2** (p45); Table I gamma readings (p646–647) | ⚠ located at the TP-03 test-pit cluster (RI text ties the peak here) |

### C. NYSDEC cleanup-site wells (`wells_dec.geojson`, 259 features)

Source: **NYSDEC Environmental Site Remediation database** (DEC DecInfo / DecDocs). 4 program sites:

| Well | (lat, lon) | Program | Site |
|---|---|---|---|
| OW222 | (43.07774, -79.01178) | 932019A | S-Area Landfill (Occidental Buffalo Ave) — 184 wells |
| 10210A | (43.07592, -78.95022) | 932020 | Love Canal (Occidental) — 55 wells |
| PCBM-01 | (43.07172, -78.94738) | 932022 | 102nd Street Landfill — see `docs/102ndStreet_932022_2019_Periodic_Review_Report.pdf` |
| MW-22I | (43.03532, -78.88626) | 932018 | Durez Inlet (Occidental/Glenn Springs) |

DEC document portal pattern: `https://extapps.dec.ny.gov/data/DecDocs/<program_number>/` (e.g. `.../932020/`).

### D. Water Quality Portal wells (`wells_wqp.geojson`, 293 features)

Source: **Water Quality Portal** (waterqualitydata.us) — two providers:
- **NWIS** (USGS National Water Information System) — 244 sites (wells, streams, lakes). e.g. USGS-04219670 (43.27144, -78.95754).
- **STORET/WQX** (EPA legacy + NARS) — 49 sites, mostly surface water / beach program. e.g. NARS_WQX-NCCAGL10-1220 (43.31064, -78.96755).
- Rebuild cache: `csv/_wqp_raw_results_cache.parquet`. Site page pattern: `https://waterdata.usgs.gov/monitoring-location/USGS-<id>/`.

### E. Love Canal infrastructure (`wells_lc_piezometers.geojson` 28, `wells_lc_pumps.geojson` 6)

Source: CRA/GSH 2011 work plans + EPA 4th Five-Year Review (2019); DecDocs 932020. e.g. piezometer 1174 (43.08168, -78.95056); pump chamber PC-2A (43.08194, -78.94970).

### F. Hazard sites (`hazard_sites.geojson`, 255 features)

Source: **NYSDEC Environmental Site Remediation database** (+ EPA Superfund for federal sites). Designation mix: 150 NY State Superfund, 44 Brownfield, 14 Federal Facility, 13 RCRA, 12 ERP, 6 VCP, plus NPL/CERCLA/FUSRAP-LM. 11 carry a `docs_url` to the DEC portal. e.g. [932002] Airco Speer Carbon-Graphite (43.09520, -79.00395).

### G. Cancer (`cancer_sir.geojson`, 176 block groups)

Standardized incidence ratios (observed/expected) by census block group for bladder, brain, esophagus, lung, mesothelioma, oral. **Verify the underlying source** — this should be NYS Cancer Registry / NYSDOH Environmental Facilities & Cancer Maps; confirm the vintage and geography before NYT.

---

## PART 2 — Untagged hazard sites that MAY hold radioactive waste

Niagara Falls was a Manhattan-Project/AEC hub (cheap hydropower → electrometallurgy, graphite, ore refining). These sites are **not yet rad-tagged** in our data but have a credible radioactive-legacy basis. Ranked by strength of evidence.

### Tier 1 — Documented AEC/MED radioactive handling (highest priority)
- **Great Lakes Carbon Corp. [932016], Niagara Falls** — ⭐ **Documented**: studied graphite for the AEC (1952), did TREAT reactor-fuel work for Argonne (1958), and **handled radioactive uranium and thorium under AEC contract**. EPA Superfund profile id `0201403`. Collect: EPA Superfund docs + DOE LM considered-sites entry.
- **Airco Speer Carbon-Graphite [932002], Niagara Falls** — Speer Carbon supplied **Manhattan-Project graphite** (Szilárd's 1940 purchase; graphitizing plant since 1920). MED-connected; check for reactor-contact contamination vs. clean feedstock.
- **NFSS Vicinity Properties (the other ~22)** — DOE lists **26** vicinity properties near Lewiston (LOOW), **23 contaminated** (U/Th/Ra). We currently map only **4** (VP H-Prime, VP X, Anomaly CC, Central Drainage Ditch). The remaining properties are documented FUSRAP — pull the full list from the DOE fact sheet / certification summary (URLs below).

### Tier 2 — Union Carbide / electrometallurgy lineage
- **GrafTech Intl. / former Union Carbide [932035]** and **Union Carbide Site [B00079]**, Niagara Falls — Union Carbide's Electro-Metallurgical Division turned "green salt" (UF4) into uranium metal in Niagara Falls (that specific plant = our already-tagged Northern Ethanol/Electromet). These related Union Carbide parcels warrant a check for shared radioactive legacy.
- **Carbide/Graphite history**: `lipsitzponterio.com/jobsites-Carbide_Graphite_Niagara_Falls_History.html`.

### Tier 3 — Ferroalloy / ore-slag (likely TENORM at most — verify, don't assume)
- **SKW Newco Inc. [932001C]** and **Witmer Road Site [932027]** — ferroalloy slag, adjacent to the Vanadium Corp parcel. Ferroalloy slag can be TENORM but is often not radioactive.
- **3807 Highland Avenue [C932145]**, **Former Military Road School [C932175]** — "slag" fill; worth a gamma check given the TENORM slag pattern seen at Mill No. 2 / Covanta.
- Steel mills (Roblin, Ross, Apollo) — only relevant if they rolled U/Th metal (as Guterl did); low prior probability, quick to rule out.

### ⛔ Ruled out (do not tag)
- **Vanadium Corporation of America [932001]** — ferroalloy metallurgy site; NOT radioactive. VCA's uranium mills are all out West (Durango CO, Shiprock NM, Monticello UT, Red Valley AZ). See memory note.

### Where to collect Part-2 data
- DOE Office of Legacy Management **Considered Sites** (searchable by state — authoritative determinations): https://lmpublicsearch.lm.doe.gov/ConsideredSites/
- NFSS Vicinity Properties fact sheet: https://www.energy.gov/sites/default/files/2022-09/NiagaraFallsVPFactSheet.pdf
- NFSS VP FUSRAP Site Certification Summary (lists properties): https://www.energy.gov/sites/default/files/2023-11/NiagaraFallsSSVP_FUSRAP_Site_Certification_Summary.pdf
- Great Lakes Carbon EPA Superfund profile: https://cumulis.epa.gov/supercpad/CurSites/csitinfo.cfm?id=0201403
- Great Lakes Carbon history (EECAP): https://eecap.org/great-lakes-carbon-corporation-information/

---

## PART 3 — Monitoring-well data around Niagara Falls (the waterfall)

**Does it exist? Yes — but thinly, and we already hold most of what's public.** Reference point: Horseshoe Falls ≈ (43.0793, -79.0745).

### What we already have (within 3 km of the falls)
- **4 USGS/NWIS groundwater wells** (in `wells_wqp.geojson`), all east of the falls in the city:
  - USGS-430508079034601 (~1.2 km) · USGS-430527079034401 (~1.6 km, "test hole not completed as a well") · USGS-430445079030201 (~2.0 km) · USGS-430515079024101 (~2.6 km)
- **0** NYSDEC cleanup wells and **0** legacy wells that close to the falls (the dense clusters — Love Canal, S-Area, Covanta, Frontier — sit 3–8 km east/northeast).

### What likely exists to collect
- **USGS NWIS** (NY Water Science Center): groundwater levels + water-quality for the city of Niagara Falls / Niagara River corridor. This is the primary source. Note the hydrology: ~6 million gal/day of groundwater drains into the **Falls Street Tunnel** and discharges to the gorge below the falls — a documented pathway worth representing.
  - Site inventory (bounding box query): https://waterdata.usgs.gov/nwis/inventory (set a box around the falls; site types GW = groundwater)
  - National Ground Water Monitoring Network: https://www.usgs.gov/apps/ngwmn/provider/USGS/
- **Water Quality Portal** (one-stop, EPA+USGS+state): https://www.waterqualitydata.us/ — query by bounding box or Niagara County; returns NWIS + STORET/WQX in one download (this is how our WQP layer was built).
- **NYSDEC–USGS ambient groundwater network**: cooperative statewide monitoring; western NY River Basins round sampled 34 wells (16 sand/gravel, 18 bedrock). Report: https://pubs.usgs.gov/publication/ofr20221021/full
- **NYPA / Niagara Power Project**: the power project's intake/conduits sit just above the falls; NYPA and the Niagara River Toxics/Remediation programs may hold monitoring near the intake — worth a records request if you want data right at the brink.
- **City of Niagara Falls / NF Water Board [932080A/B]**: the former drinking-water plant and treatment plant are near the river; DEC DecDocs for those program numbers may have well data.

### Bottom line for Part 3
Genuine groundwater monitoring *right at the waterfall* is sparse — the falls itself is bedrock gorge, not an industrial site. The realistic collectible data is: (a) the handful of **USGS city wells** we already have, (b) a fuller **WQP / NWIS bounding-box pull** for the Niagara Falls corridor, and (c) **NYPA/city** records near the intake if you want brink-adjacent coverage. Recommend starting with the WQP bounding-box download to confirm we've captured everything public.

---

_Sources consulted 2026-07-19: DOE Office of Legacy Management; EPA Superfund site profiles; USGS NWIS / NY Water Science Center; energy.gov FUSRAP fact sheets; EECAP; Wikipedia (Lake Ontario Ordnance Works, Nuclear graphite)._
