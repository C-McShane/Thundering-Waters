# Thundering Waters: The Toxic Legacy of Niagara County
### Spatial Data & Interactive Map Repository

**Companion data repository for *Thundering Waters: The Toxic Legacy of Niagara County* by Christen Civiletto**

> *"1 in every 5 acres of the Niagara Falls area is contaminated by hazardous waste."*

---

## 🗺️ Live Resources

| Resource | Link |
|---|---|
| Thundering Waters — Interactive Map | [Open Map](https://c-mcshane.github.io/Thundering-Waters/web/map.html) |
| Site Narratives (89 documented sites) | [Read Narratives](https://c-mcshane.github.io/Thundering-Waters/Niagara_Site_Narratives_updated.html) |

---

## About This Repository

This repository contains the spatial dataset, interactive web map, and site narrative documentation underlying the environmental analysis in *Thundering Waters*. It documents **<!--stat:hazard_sites-->248<!--/stat--> hazardous waste sites** across Niagara County, New York — one of the most contaminated regions in the United States — compiled from federal and state regulatory databases and cross-referenced with geographic boundary data and cancer incidence records.

> Every count in this README is generated from [`web/data/statistics.json`](web/data/statistics.json) by `web/build_statistics.py`, and verified by `python web/update_readme_counts.py --check`. Do not edit the figures by hand.

The data supports the book's core findings:

- **<!--stat:hazard_sites-->248<!--/stat--> documented hazardous waste sites** across Niagara County
- **~5% of the county's total land area** is contaminated by recorded waste site footprints
- In the Niagara Falls impact zone, **1 in every 5 acres** is contaminated
- **<!--stat:hazard_sites_in_impact_zone-->147<!--/stat--> sites** fall within the Niagara Falls area impact zone, affecting approximately 47,000 residents
- **<!--stat:cancer.Lung.highlighted_regions-->112<!--/stat--> of <!--stat:cancer_doh_regions-->161<!--/stat--> NYSDOH reporting regions (70%)** fall within a *highlighted area* for lung cancer — areas NYSDOH identified using a spatial scan statistic as having at least 50% more cases than expected, at a level unlikely to be chance (NYSDOH, 2011–2015). This is a **cluster-level** determination, not a significance test of any single block group.
- **<!--stat:cancer.Bladder.highlighted_regions-->103<!--/stat--> of <!--stat:cancer_doh_regions-->161<!--/stat--> regions (64%)** fall within a highlighted area for bladder cancer
- County-wide mesothelioma rates are **more than double the New York State average**

---

## Repository Contents

```
/
├── Niagara_Site_Narratives_updated.html   — Interactive site narrative browser (89 sites)
├── spatial_layers/
│   └── Niagara_County_HazWaste.gpkg        — Master GeoPackage (<!--stat:gpkg_layers-->25<!--/stat--> spatial layers)
├── csv/
│   ├── Niagara_DEC_Wells_ConcSeries.json   — Per-well contaminant concentration time series (µg/L by year)
│   ├── Niagara_DEC_Wells_ChemYears.json    — Per-well detected-by-year index (drives the map year filter)
│   ├── Niagara_WQP_Wells_*.json            — Same, for USGS/EPA Water Quality Portal stations
└── web/
    ├── map.html                            — Interactive Leaflet web map
    └── data/
        ├── hazard_sites.geojson            — <!--stat:hazard_sites-->248<!--/stat--> hazardous waste site points
        ├── census_tracts.geojson           — <!--stat:census_tracts-->66<!--/stat--> Niagara County census tracts with contamination metrics
        ├── impact_zone.geojson             — 26 Niagara Falls area impact zone tracts
        ├── georef_locations.geojson        — <!--stat:georef_locations-->1,511<!--/stat--> sampling locations georeferenced from report figures, across <!--stat:georef_sites-->17<!--/stat--> sites
        ├── georef_boundaries.geojson       — <!--stat:georef_boundary_rings-->58<!--/stat--> traced site-boundary & contamination-area rings, across <!--stat:georef_boundary_sites-->18<!--/stat--> sites
        ├── major_roads.geojson             — Highways + arterials for spatial reference (<!--stat:major_road_names-->13<!--/stat--> named roads)
        ├── cancer_sir.geojson              — Block-group cancer SIR + NYSDOH highlighted-area flags, 6 cancers, 2011–2015
        ├── water.geojson                   — Niagara River, canals, reservoirs & ponds (hydrography context)
        ├── wells_wqp.geojson               — <!--stat:wells_wqp-->293<!--/stat--> USGS/EPA Water Quality Portal sampling stations
        ├── wells_dec.geojson               — <!--stat:wells_dec-->259<!--/stat--> NYSDEC remediation monitoring wells (with 2000–2019 chem time series)
        ├── wells_legacy.geojson            — <!--stat:wells_legacy-->233<!--/stat--> legacy-site monitoring wells, soil borings and test pits
        ├── wells_lc_piezometers.geojson    — <!--stat:lc_piezometers-->28<!--/stat--> Love Canal barrier-drain piezometers (multi-year water-level series)
        └── wells_lc_pumps.geojson          — <!--stat:lc_pumps-->6<!--/stat--> Love Canal leachate pump chambers & storage tanks
```

---

## The GeoPackage

`Niagara_County_HazWaste.gpkg` is a GeoPackage (SQLite-based) file readable in QGIS, ArcGIS, R (`sf`), Python (`geopandas`), and most modern GIS tools. It contains <!--stat:gpkg_layers-->25<!--/stat--> layers:

| Layer | Description |
|---|---|
| `Niagara_County_Hazard_Sites` | <!--stat:gpkg_layer_rows.Niagara_County_Hazard_Sites-->249<!--/stat--> hazardous waste site points (EPSG:4326) with full attributes |
| `Niagara_Water_Testing_Sites` | <!--stat:gpkg_layer_rows.Niagara_Water_Testing_Sites-->293<!--/stat--> USGS/EPA Water Quality Portal sampling stations |
| `Niagara_DEC_Monitoring_Wells` | <!--stat:gpkg_layer_rows.Niagara_DEC_Monitoring_Wells-->259<!--/stat--> NYSDEC remediation monitoring wells |
| `Niagara_Legacy_Monitoring_Wells` | <!--stat:gpkg_layer_rows.Niagara_Legacy_Monitoring_Wells-->233<!--/stat--> monitoring wells, soil borings and test pits across the hand-compiled legacy sites |
| `Niagara_Georef_Sampling_Locations` | <!--stat:gpkg_layer_rows.Niagara_Georef_Sampling_Locations-->1,511<!--/stat--> sampling locations georeferenced from report figures — see [`GEOREFERENCING_PRECISION.md`](GEOREFERENCING_PRECISION.md) before relying on any single position |
| `Niagara_Georef_Boundaries` | <!--stat:gpkg_layer_rows.Niagara_Georef_Boundaries-->58<!--/stat--> traced site-boundary and contamination-area rings |
| `Niagara_Mill2_Radioactive_Soil_Zones` | <!--stat:gpkg_layer_rows.Niagara_Mill2_Radioactive_Soil_Zones-->8<!--/stat--> slag zones flagged by gamma survey (uranium / thorium / radium) |
| `Niagara_LoveCanal_Piezometers` | <!--stat:gpkg_layer_rows.Niagara_LoveCanal_Piezometers-->28<!--/stat--> barrier-drain piezometers (multi-year water-level series in `water_series`) |
| `Niagara_LoveCanal_Pumps` | <!--stat:gpkg_layer_rows.Niagara_LoveCanal_Pumps-->6<!--/stat--> Love Canal leachate pump chambers & storage tanks |
| `Niagara_LoveCanal_Colvin_Sewer_2011` | 2011 Colvin Blvd sewer NAPL remediation corridor + investigation wells |
| `census_tracts_contamination` | <!--stat:gpkg_layer_rows.census_tracts_contamination-->66<!--/stat--> census tracts with contamination acreage and coverage % |
| `NiagaraFalls_Area_ImpactZone` | <!--stat:gpkg_layer_rows.NiagaraFalls_Area_ImpactZone-->26<!--/stat--> tracts defining the Niagara Falls impact zone |
| `block_group_healthPOP_stats` | <!--stat:gpkg_layer_rows.block_group_healthPOP_stats-->176<!--/stat--> block groups with cancer SIR data, demographics, and contamination metrics |
| `Niagara_County_Boundary` | County boundary polygon |
| `nysdec_site_boundaries` | <!--stat:gpkg_layer_rows.nysdec_site_boundaries-->148<!--/stat--> NYSDEC remediation site boundary polygons |
| + the remaining reference layers | Roads, railways, hydrology, crime, census health data |

> **The GeoPackage row count is not the map count.** The hazard-sites layer holds <!--stat:gpkg_layer_rows.Niagara_County_Hazard_Sites-->249<!--/stat--> rows while the published map shows <!--stat:hazard_sites-->248<!--/stat-->: one site is deliberately withheld from the map and retained in the data. See [`CORRECTIONS.md`](CORRECTIONS.md).

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

## Monitoring Wells & Groundwater Chemistry

Beyond the site inventory, the map's **Monitoring Wells** tab plots individual groundwater sampling points and their contaminant history:

- **785 monitoring points** across three sources — 293 Water Quality Portal stations (USGS/EPA), 259 NYSDEC remediation wells, and 233 legacy-site points — droplet-sized by number of contaminants detected, outlined by sampling type (bedrock, overburden, surface water, remediation).
- **Per-well concentration-vs-year plots**: click a well with a chemical selected to see a log-scale trend line (detected vs non-detect at the reporting limit).
- **Chemical + year filters**: show wells where a given contaminant had been detected by a given year (cumulative), across a **1948–2025** span.
- Chemistry is extracted directly from the primary regulatory record (NYSDEC analytical-results tables, WQP water-media results), not modeled.

## Love Canal

The Love Canal site (NYSDEC #932020) is represented by its **monitoring layers**: 55 monitoring
wells with chemistry, 28 barrier-drain piezometers with multi-year water-level series, and 6
leachate pump chambers and storage tanks. These are drawn from the NYSDEC DecDocs 932020 record
(1977–2024), which is archived for verification.

The piezometers report the geologic unit each is screened in. Those medium labels come from a
per-well lookup built from the authoritative 2016–2022 Periodic Review Report headers, correcting an
earlier assumption that the letter block in the 2015 tables encoded the medium — see
[`DATA_SOURCES.txt`](DATA_SOURCES.txt).

> **Scope note.** An earlier set of exploratory Love Canal analyses (containment-gradient
> interpretation, a 2011 sewer-pathway hypothesis, and rainfall/migration tests) was removed from
> this repository on 2026-07-20. They were incomplete, had not undergone independent methodological
> review, and did not support any published map feature. See [`CORRECTIONS.md`](CORRECTIONS.md).


> **Counts in this README are generated.** Every figure above is taken from
> [`web/data/statistics.json`](web/data/statistics.json), which is emitted by
> [`web/build_statistics.py`](web/build_statistics.py) directly from the data files. If a count
> here ever disagrees with the interface, the generator has not been re-run — the data is the
> source of truth, never the prose.

### Documentation

- **[GEOREFERENCING_PRECISION.md](GEOREFERENCING_PRECISION.md)** — what the georeferenced sampling points are and are not. They are read off scanned figures, not surveyed. Median leave-one-out error is about 9 m, a quarter of points are worse than 20 m, and one site is far worse. Read this before relying on any individual position.
- **[methods/GEOREF_DECISIONS.md](methods/GEOREF_DECISIONS.md)** — the georeferencing method and the errors found in it, including ones found after publication.
- **[methods/push_georef.py](methods/push_georef.py)** — how the exports become the published layers.
| File | What it covers |
|---|---|
| [`AI_DISCLOSURE.md`](AI_DISCLOSURE.md) | AI assistance and human responsibility |
| [`VALIDATION_STATUS.md`](VALIDATION_STATUS.md) | What has and has not been source-verified |
| [`CORRECTIONS.md`](CORRECTIONS.md) | Corrections log and open issues under review |
| [`DATA_SOURCES.txt`](DATA_SOURCES.txt) | Full provenance log, per layer and per source document |
| [`docs/DATA_DICTIONARY.md`](docs/DATA_DICTIONARY.md) | Field-level definitions |
| [`docs/APPROXIMATE_LOCATIONS.md`](docs/APPROXIMATE_LOCATIONS.md) | Every point whose position is not surveyed |
| [`docs/CITATIONS_TODO.md`](docs/CITATIONS_TODO.md) | Outstanding source citations for Selected high detections |
| [`validation/`](validation/) | Hand-validation packet, sample points, placement checks |
| [`LICENSE-DATA.md`](LICENSE-DATA.md) | Data licence and third-party attribution |
| [`CHANGELOG.md`](CHANGELOG.md) | Release history |

## Data Sources

- **New York State Department of Environmental Conservation (NYSDEC)** — Remediation database, site boundary shapefiles, program records for HW, BCP, ERP, VCP, and RCRA sites; site document repositories (DecDocs) for monitoring reports and analytical data
- **U.S. Environmental Protection Agency (EPA)** — CERCLA/Superfund site profiles, NPL listings, RCRA Corrective Action records; five-year review reports
- **USGS / EPA Water Quality Portal** (waterqualitydata.us) — groundwater and surface-water analytical results for Niagara County (FIPS 36063), water-media only
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
- Two entry points — **Start Here** (what the project documents and three sourced findings) and **Address Lookup** (nearest documented site/sample, explicitly not a risk assessment) — plus five data tabs: **Hazard Sites**, **Monitoring Wells**, **Radiation**, **Chemicals**, and **Cancer Incidence**
- Toggle layers on/off (hazard sites, contamination choropleth, impact zone, major roads, rivers & water) — hazard sites and water are on at load
- Filter sites by any of 16 danger-ranked chemicals (with cancer-association notes), or by radionuclide (Uranium / Thorium / Radium / TENORM)
- Mobile-friendly: the controls collapse into a bottom sheet on phones, reopened via a "Layers & Search" button
- **Cancer Incidence** tab, split into two clearly-separated readings of NYSDOH 2011–2015 data for mesothelioma, esophagus, bladder, lung, oral and brain:
  - **Highlighted Areas** — NYSDOH’s own determination via spatial scan statistic (≥50% more cases than expected, unlikely to be chance). Cluster-level, not a per-block-group test.
  - **Standardized Incidence Ratio** — observed ÷ expected, age/sex-adjusted and benchmarked to **New York State** (not national). A ratio, not a significance test; small-area values are unstable and suppressed counts are not zero.
- **Filter sites by chemical** (dropdown of 16 danger-ranked contaminants; each labeled with its associated cancer, cancers with highlighted areas in the county flagged). Reflects *recorded* contaminants
- **Radioactive · Nuclear Legacy** sub-filters — Uranium / Thorium / Radium / TENORM. FUSRAP isotope attributions are DOE Legacy Management / USACE-sourced; TENORM = industrial radioactive slag
- Click any site for a popup with name, designation, acreage, contaminants, and narrative excerpt
- Click any census tract for contamination statistics
- Search sites by name, address, city, or designation type
- Download the GeoJSON files directly from the footer

---

## Building and reproducing

**The interactive map is static.** `web/map.html` loads the published GeoJSON in `web/data/` directly. To run it locally, serve the `web/` directory with any static file server — for example, from inside `web/`:

```
python -m http.server 8000
# then open http://localhost:8000/map.html
```

Opening the file over `file://` will not work, because the browser blocks the local data fetches.

**Python environment.** The data-processing scripts under `web/` were developed with Python 3.11 and the packages pinned in [`requirements.txt`](requirements.txt) — `pip install -r requirements.txt`.

**What regenerates from this repository.** The *derived* products regenerate from the published source layers, and re-running them reproduces the numbers shown in the interface exactly (the only per-run difference is a `generated_utc` timestamp recording when the file was written):

```
python web/build_statistics.py            # -> web/data/statistics.json (every count in the UI and this README)
python web/update_readme_counts.py --check  # verify this README against statistics.json; --write to fix
python web/build_recency.py               # -> the last_sampled field on the well layers
python web/build_radionuclides.py         # -> web/data/radionuclides.json
```

Every figure in this README sits between a paired set of `stat` HTML comments — invisible on
GitHub, visible in the raw markdown. `update_readme_counts.py` rewrites what is between them
from `statistics.json`, so a count can no longer drift out of step with the data. Run `--check`
after any data change; it exits non-zero on drift.

⚠ **`export_geojson.py` is not the whole pipeline.** It rebuilds *base* layers; the verified
chemistry on hazard sites and the `doh_region` / `merged_area` fields on the cancer layer are
applied afterwards by other scripts. Running it alone discards them. Back up `web/data/*.geojson`
first, and re-check the counts afterwards — `cancer_doh_regions` dropping to `0` is the signal
that enrichment was lost.

**What does *not* regenerate from this repository — and why.** The upstream compilation — scraping the NYSDEC and EPA records, OCR of scanned documents, the tiered chemical extraction, and the block-group cancer join — was carried out with an evolving set of working scripts run against a local data store, a local cache of source documents, and downloaded imagery. Those scripts were edited in place over the life of the project rather than maintained as a released, path-independent pipeline; they contain absolute local paths and depend on inputs that are not all redistributable here. **This repository is therefore not a turnkey reproduction of the raw-source-to-dataset pipeline.**

What the repository *does* provide is the compiled output — `spatial_layers/Niagara_County_HazWaste.gpkg` and the `web/data/*.geojson` layers — with its provenance documented per layer in [`DATA_SOURCES.txt`](DATA_SOURCES.txt), and the underlying public records are all obtainable from the agencies named there. This gap is tracked as an open issue in [`CORRECTIONS.md`](CORRECTIONS.md).

Script filenames that appear in the documentation but are not present under `web/` are part of that local compilation code and are not redistributed.

## Citation

If you use this data, please cite:

> McShane, C. (2026). *Niagara County Hazardous Waste Spatial Dataset* [Data repository]. GitHub. https://github.com/C-McShane/Thundering-Waters

And the companion book:

> Civiletto, C. *Thundering Waters: The Toxic Legacy of Niagara County.*

---

## Credits

**Spatial data compilation & GIS analysis:** Caitlin McShane
**Map infographic:** Caitlin McShane
**Author:** Christen Civiletto

---

*Data current as of July 2026. Site counts and acreage reflect best available information from regulatory databases at time of compilation. See `DATA_SOURCES.txt` for full methodology.*
