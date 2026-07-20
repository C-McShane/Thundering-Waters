# Data licence and attribution

Code in this repository is MIT-licensed (see `LICENSE`). **Data is different**, and this file
governs it. Full per-layer provenance is in [`DATA_SOURCES.txt`](DATA_SOURCES.txt).

---

## What we license

**Our compiled work** — the curated site list, the digitised analytical tables, the
georeferenced sample-point coordinates, the derived fields (`chems`, `rad_class`, `rad_basis`,
`coord_precision`, `hlarea_*`, `doh_region`), `statistics.json`, `findings.json`, and the
documentation — is released under
**[Creative Commons Attribution 4.0 International (CC BY 4.0)](https://creativecommons.org/licenses/by/4.0/)**.

Attribute as: *Thundering Waters: The Toxic Legacy of Niagara County* (C. McShane), with a link
to this repository. See `CITATION.cff`.

## What we do NOT license

**We cannot and do not relicense third-party source data.** The underlying records remain the
work of their originating agencies and are used here under their own terms. Redistribution of
those materials is subject to the originator's conditions, not ours.

| Source | Material | Terms |
|---|---|---|
| **NYSDEC** — Environmental Site Remediation database (DecInfo / DecDocs) | Hazard site records, program numbers, narratives, site documents | NYS public records; consult NYSDEC |
| **NYSDOH** — Environmental Facilities & Cancer Mapping | Block-group cancer counts, expected counts, highlighted-area flags | NYS public health data; **provisional as of Dec 2017**; consult NYSDOH |
| **USACE / DOE** — FUSRAP, NFSS RI, environmental surveillance | Radiological records, monitoring results | US federal government works |
| **US EPA** | Superfund records, STORET/WQX water quality | US federal government works |
| **USGS** | NWIS water quality and groundwater records | US federal government works |
| **US Census Bureau** | TIGER block group / tract boundaries | US federal government works |
| **LaBella Associates**, **ERM**, and other consultants | Remedial Investigation reports and their figures/tables | Copyright of the authoring firms; cited, quoted and digitised here for documentary purposes |
| **CARTO** + **OpenStreetMap** | Basemap tiles | © OpenStreetMap contributors, © CARTO — see their terms |
| **Microsoft Corporation (2010)**, **NYS Office of Cyber Security** | Aerial imagery appearing *within reproduced report figures* | Credited within the source reports |

## Important caveats for anyone reusing this data

1. **This is a documentary compilation, not a regulatory dataset.** Nothing here supersedes the
   agency records it draws on. Where our reading and the source disagree, **the source governs**.
2. **Some coordinates are approximate.** Points carrying a `coord_precision` flag were placed by
   georeferencing scanned figures or anchored to a site address. Each discloses this in its popup.
   See `validation/` for placement checks.
3. **Sampling dates vary enormously.** Each monitoring point reflects conditions as of its own
   last sampling date. Those span **1969–2024**; roughly a third of sampled points were last
   visited in 2020 or later. This is **not** a synchronised present-day snapshot, and an old
   record is not evidence that conditions are unchanged.
4. **Cancer data are ecological.** Population-level patterns do not establish individual exposure,
   disease causation, or a causal link to mapped sites. Expected counts are benchmarked to
   **New York State**, not the national rate. Suppressed values are not zero.
5. **Selected high detections are pending full citations** (`docs/CITATIONS_TODO.md`). Verify
   against the cited report before reusing any individual figure.
6. **Chemical flags on hazard sites are *recorded* chemicals**, not measurements.

If you find an error, please open an issue — corrections are welcome and wanted.
