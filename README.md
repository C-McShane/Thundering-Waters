# Thundering Waters: The Toxic Legacy of Niagara Falls
### Spatial Data & Interactive Map Repository

**Companion data repository for *Thundering Waters: The Toxic Legacy of Niagara Falls* by Christen Civiletto**

> *"1 in every 5 acres of the Niagara Falls area is contaminated by hazardous waste."*

---

## 🗺️ Live Resources

| Resource | Link |
|---|---|
| Interactive Hazardous Waste Map | [Open Map](https://c-mcshane.github.io/Thundering-Waters/web/map.html) |
| Site Narratives (89 documented sites) | [Read Narratives](https://c-mcshane.github.io/Thundering-Waters/Niagara_Site_Narratives_updated.html) |

---

## About This Repository

This repository contains the spatial dataset, interactive web map, and site narrative documentation underlying the environmental analysis in *Thundering Waters*. It documents **256 hazardous waste sites** across Niagara County, New York — one of the most contaminated regions in the United States — compiled from federal and state regulatory databases and cross-referenced with geographic boundary data and cancer incidence records.

The data supports the book's core findings:

- **256 documented hazardous waste sites** across Niagara County
- **~5% of the county's total land area** is contaminated by recorded waste site footprints
- In the Niagara Falls impact zone, **1 in every 5 acres** is contaminated
- **158 sites** fall within the Niagara Falls area impact zone, affecting approximately 47,000 residents
- **70% of Niagara County block groups** have statistically significantly elevated lung cancer rates (NYS Dept. of Health, 2011–2015)
- **64%** have statistically significantly elevated bladder cancer rates
- County-wide mesothelioma rates are **more than double the New York State average**

---

## Repository Contents

```
/
├── Niagara_Site_Narratives_updated.html   — Interactive site narrative browser (89 sites)
├── Niagara_County_HazWaste.gpkg           — Master GeoPackage (15 spatial layers)
├── DATA_SOURCES.txt                        — Full data provenance and methods log
├── Thundering_Waters_Infographic_Cheatsheet.docx  — Statistics reference for the infographic
└── web/
    ├── map.html                            — Interactive Leaflet web map
    └── data/
        ├── hazard_sites.geojson            — 256 hazardous waste site points
        ├── census_tracts.geojson           — 66 Niagara County census tracts with contamination metrics
        ├── impact_zone.geojson             — 26 Niagara Falls area impact zone tracts
        ├── major_roads.geojson             — Highways + arterials for spatial reference (13 named roads)
        └── cancer_sir.geojson              — Block-group cancer SIR (6 statistically elevated cancers, NYSDOH 2011–2015)
```

---

## The GeoPackage

`Niagara_County_HazWaste.gpkg` is a GeoPackage (SQLite-based) file readable in QGIS, ArcGIS, R (`sf`), Python (`geopandas`), and most modern GIS tools. It contains 15 layers:

| Layer | Description |
|---|---|
| `Niagara_County_Hazard_Sites` | 256 hazardous waste site points (EPSG:4326) with full attributes |
| `census_tracts_contamination` | 66 census tracts with contamination acreage and coverage % |
| `NiagaraFalls_Area_ImpactZone` | 26 tracts defining the Niagara Falls impact zone |
| `block_group_healthPOP_stats` | 176 block groups with cancer SIR data, demographics, and contamination metrics |
| `Niagara_County_Boundary` | County boundary polygon |
| `nysdec_site_boundaries` | 148 NYSDEC remediation site boundary polygons |
| + 9 additional reference layers | Roads, railways, hydrology, crime, census health data |

### Key Fields — Hazard Sites Layer

| Field | Description |
|---|---|
| `site_name` | Site name |
| `designation` | Classification (NY State Superfund, Brownfield, Federal Facility, etc.) |
| `program_type` | Regulatory program (HW, BCP, ERP, FUDS, FUSRAP, RCRA, etc.) |
| `program_category` | Federal program identifier where applicable (FUDS, FUSRAP, FUSRAP-LM) |
| `area_acres_best` | Best available acreage from official records |
| `chemicals` | Key contaminants of concern |
| `narrative` | Site history and context |
| `latitude` / `longitude` | WGS84 coordinates |

---

## Site Designation Categories

| Designation | Description |
|---|---|
| NY State Superfund | Sites designated under the NYSDEC hazardous waste remediation program |
| Brownfield | Sites enrolled in the NYSDEC Brownfield Cleanup Program |
| Federal Facility | Federally-owned or formerly-owned sites (includes FUDS and FUSRAP) |
| FUSRAP-LM | Four NFSS vicinity properties contaminated with radioactive material from Manhattan Project-era uranium processing; under Army Corps long-term stewardship |
| RCRA Corrective Action | Facilities regulated under the federal Resource Conservation and Recovery Act |
| Federal NPL - Active | Sites on the EPA National Priorities List (active Superfund) |
| Federal NPL - Deleted | Former NPL sites where cleanup is complete |
| Federal CERCLA (Non-NPL) | Sites assessed under CERCLA but not placed on the NPL |
| Environmental Restoration Program | NYSDEC cleanup at state-owned properties |
| Voluntary Cleanup Program | Sites remediated voluntarily under NYSDEC oversight |

---

## Data Sources

- **New York State Department of Environmental Conservation (NYSDEC)** — Remediation database, site boundary shapefiles, program records for HW, BCP, ERP, VCP, and RCRA sites
- **U.S. Environmental Protection Agency (EPA)** — CERCLA/Superfund site profiles, NPL listings, RCRA Corrective Action records
- **U.S. Army Corps of Engineers** — FUDS (Formerly Used Defense Sites) inventory; FUSRAP/FUSRAP-LM program records
- **U.S. Department of Energy, Office of Legacy Management** — NFSS (Niagara Falls Storage Site) vicinity property documentation
- **NYS Department of Health** — Environmental Facilities Cancer Mapping dataset, 2011–2015 (cancer incidence by block group, Standardized Incidence Ratios)
- **U.S. Census Bureau** — TIGER/Line 2023 census tract and block group boundaries
- Site-specific acreage sourced from EPA Superfund profiles, NYSDEC program documents, and published environmental reports

Full provenance for every data point is documented in `DATA_SOURCES.txt`.

---

## Using the Interactive Map

The web map at `web/map.html` requires an internet connection (for the basemap and fonts) but all spatial data loads locally from the `web/data/` folder. It works in any modern browser.

**Features:**
- Toggle layers on/off (hazard sites, contamination choropleth, impact zone, major roads) — only hazard sites are on at load
- Select a per-cancer block-group **Cancer Incidence (SIR)** choropleth — the six cancers statistically elevated countywide (95% CI > 1) per NYSDOH 2011–2015: mesothelioma, esophagus, bladder, lung, oral, brain. SIR = observed ÷ expected (NYS-benchmarked); block groups with no cases or suppressed counts are shown distinctly
- **Filter sites by chemical** (dropdown of 16 danger-ranked contaminants; each labeled with its associated cancer, elevated county cancers flagged). Reflects *recorded* contaminants
- **Radioactive · Nuclear Legacy** sub-filters — Uranium / Thorium / Radium / TENORM. FUSRAP isotope attributions are DOE Legacy Management / USACE-sourced; TENORM = industrial radioactive slag
- Click any site for a popup with name, designation, acreage, contaminants, and narrative excerpt
- Click any census tract for contamination statistics
- Search sites by name, address, city, or designation type
- Download the GeoJSON files directly from the footer

---

## Citation

If you use this data, please cite:

> McShane, C. (2026). *Niagara County Hazardous Waste Spatial Dataset* [Data repository]. GitHub. https://github.com/C-McShane/Thundering-Waters

And the companion book:

> Civiletto, C. *Thundering Waters: The Toxic Legacy of Niagara Falls.*

---

## Credits

**Spatial data compilation & GIS analysis:** Caitlin McShane
**Map infographic:** Caitlin McShane
**Author:** Christen Civiletto

---

*Data current as of July 2026. Site counts and acreage reflect best available information from regulatory databases at time of compilation. See `DATA_SOURCES.txt` for full methodology.*
