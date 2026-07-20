# Data dictionary

Field-level definitions for `web/data/*.geojson`. Provenance for each layer is in
[`DATA_SOURCES.txt`](../DATA_SOURCES.txt).

## Shared / point layers

| Field | Meaning |
|---|---|
| `well_id` | Identifier exactly as printed in the source report (e.g. `C4R-MW-04`, `TP-14`, `SS-01`, `GP-16`). Searchable in the interface. |
| `site` / `site_name` | Parent site the point belongs to. |
| `program_number` | NYSDEC program identifier. Document portal: `https://extapps.dec.ny.gov/data/DecDocs/<program_number>/` |
| `sample_type` | What the point samples (e.g. `Overburden groundwater`, `Soil / test hole`, `Soil / geoprobe boring`). Drives the ring colour in the Monitoring Wells tab. |
| `src` | Origin dataset: `WQP`, `DEC`, `LEGACY`, `COVANTA`, `LC_PIEZO`, `LC_INFRA`. |
| `source` / `source_url` | The specific report the values were taken from. |
| `coord_precision` | **Present only when the position is not surveyed.** See [`APPROXIMATE_LOCATIONS.md`](APPROXIMATE_LOCATIONS.md). |
| `n_found` | Count of distinct chemicals **detected** at this point. Drives droplet size. Absent/zero means none tabulated — it is *not* a statement that the point is clean. |
| `chems` | Curated chemical names detected here (mapped through `web/well_chem_lexicon.py`). |
| `chemicals_found` | Human-readable summary string of detections. |
| `conc_series` | `{chemical: {year: [value, "detect"\|"nondetect"]}}` — drives the per-point concentration-vs-year plot. |
| `conc_units` | Units per chemical (`µg/L` water, `mg/Kg` soil). **Units differ between water and soil — never compare across media.** |
| `chems_years` | Years in which each chemical was detected. |

## Hazard sites (`hazard_sites.geojson`)

| Field | Meaning |
|---|---|
| `designation` | NYSDEC/EPA programme (State Superfund, Brownfield, RCRA, Federal NPL, FUSRAP-LM, …). |
| `chemicals` | **Raw NYSDEC free text.** Not measurements. |
| `chems` | Curated list parsed from the above — this is what the chemical filter searches. The two populations differ (106 vs 121 sites) and are reported separately in `statistics.json`. |
| `rad_class` | Radiological classification: `FUSRAP`, `MED-AEC`, or `TENORM`. Absent = not established (**not** "not radioactive"). |
| `rad_iso` | Isotope families implicated: `U`, `Th`, `Ra`. |
| `rad_basis` | Prose justification with its source. Every rad tag must have one. |

## Radioactive soil zones (`soil_radzones.geojson`)

| Field | Meaning |
|---|---|
| `zone_id` | Zone name (searchable). |
| `gamma_cpm` | Gamma reading(s) in counts per minute, **as stated in the source**, with the location each reading applies to. |
| `hazard` / `desc` | What the material is and how it was characterised. |
| `coord_precision` | How the zone was placed, including where it was *not* georeferenced. |

## Cancer (`cancer_sir.geojson`)

NYSDOH Environmental Facilities & Cancer Mapping, **2011–2015**, 2010-vintage census block groups.

| Field | Meaning |
|---|---|
| `geoid` | 12-digit block-group FIPS code. |
| `obs_<Cancer>` | Observed cases, 2011–2015. |
| `exp_<Cancer>` | Expected cases if **New York State** age- and sex-specific rates applied to this population. **The benchmark is NYS, not national.** |
| `sir_<Cancer>` | `observed ÷ expected`. 1.0 = exactly what NYS demographics predict. **A ratio, not a significance test.** |
| `hlarea_<Cancer>` | `1` = this block group belongs to a NYSDOH **highlighted area**; `0` = it does not. Determined by the **spatial scan statistic** among locations with ≥50% more observed than expected cases where the ratio was unlikely to be chance. **A cluster-level determination, not a test of this block group's own rate.** |
| `doh_region` | NYSDOH reporting region. For unmerged block groups this equals `geoid`. |
| `merged_area` | `true` = NYSDOH merged this block group with others (fewer than 6 male or 6 female cases) for privacy. Its counts are for the **combined** area. |
| `merged_bg_count` | How many block groups were combined into this region. |

> ⚠️ **Always aggregate cancer data by `doh_region`, never by block group** — merged regions share
> one set of counts and would otherwise be counted several times. `build_statistics.py` does this.

> ⚠️ **Suppressed values are not zero.** Absent data means NYSDOH withheld or merged it.

## Generated files

| File | Meaning |
|---|---|
| `statistics.json` | Every count shown in the interface, emitted by `build_statistics.py`. **Never hand-edit.** Re-run after any data change. |
| `findings.json` | "Selected high detections" entries and their citation blocks. Fields reading `Information to be added` are pending — see [`CITATIONS_TODO.md`](CITATIONS_TODO.md). |
| `radionuclides.json` | Isotope-level well/soil results, emitted by `build_radionuclides.py`. |
