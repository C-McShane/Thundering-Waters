# Corrections log

Errors found in this project and how they were resolved. This log exists so that corrections are
part of the public record rather than quietly overwritten.

**On "affected versions":** the interactive map deploys continuously from the `main` branch to
GitHub Pages, so an error can be briefly live on the public site without ever appearing in a tagged
release. All tagged releases (v1.0.0 and later) were created on 2026-07-20. Where an error was
caught and fixed before the first freeze, it never entered a tagged release; the column notes when
it was nonetheless live on the site.

---

## Terms used in this log

These four words describe genuinely different actions and are not interchangeable. They had been
used loosely — "removed" in particular was doing the work of all four — so they are fixed here.

| Term | Meaning | Is the record still held? | Can it come back? |
|---|---|---|---|
| **withheld** | Retained in full in the underlying data, but not shown in the published map or exports, because it is not yet supported well enough to publish. **A withheld item is not a disproven item.** | Yes — in `csv/Niagara_Hazard_Sites_MASTER.csv` and the GeoPackage | Yes, as soon as it is substantiated |
| **withdrawn** | Was published, and has been taken down pending verification. A statement about confidence, not about correctness. | Yes | Yes, once verified |
| **removed** | Deleted from the active repository and not carried forward. | Only in Git history | Not without a deliberate decision |
| **corrected** / **replaced** | The item is still published, but its value, wording or basis changed. | Yes | n/a |

Where an outside body acts, that is said explicitly and attributed to them — for example "DOE
removed the site from FUSRAP" is the agency's own determination, not an editorial decision made
here.

---

## Open issues under review

A technical review initiated on 2026-07-20 identified unresolved questions concerning reconciliation
of co-located and repeated site records, calculation of reported site acreage, synchronization of
derived tract statistics, preservation of monitoring-result units, and reproducibility of the
complete data pipeline. The affected site-count, acreage, and monitoring-concentration claims should
be treated as provisional while this review is completed.


## Monitoring-well concentration plots withdrawn pending unit validation

A unit-handling error was identified in the translation of monitoring-well sample results into the web time-series format. Frontier Chemical is confirmed to be affected, with some plotted values materially misstated because source units were not consistently preserved or normalized. The full scope across other sites has not yet been established.

All monitoring-well concentration trend plots, and any displayed summaries derived from those values, have been temporarily withdrawn pending a site-by-site review. They will be restored only after the original value, unit, sample medium, conversion rule, and source record have been verified.

This issue affects the web presentation of concentration values. It does not, by itself, change the locations of monitoring points, sample identifiers, or the underlying regulatory documents. A separate technical incident record will document the affected datasets and versions, root cause, corrections, and validation results.

---

## Corrections to published output

Each of the following was, at some point, live on the public site.

| Error | Effect on published output | Correction date | Affected versions |
|---|---|---|---|
| NYSDOH highlighted areas described as "statistically elevated block groups". The flag marks membership in a spatial-scan-statistic *cluster* (≥50% more cases than expected, unlikely to be chance), not a significance test of an individual block group's rate. | Overstated the statistical claim in the cancer tab and README. Corrected to "falls within a NYSDOH-designated highlighted area", a cluster-level statement. | 2026-07-20 | Live on the site before the v1.0.0 freeze; not in a tagged release. A residual instance in the README was corrected 2026-07-20 after v1.2.0. |
| The 420,000 CPM gamma reading was implied to have been measured at the TP-03 cluster. The remedial investigation attributes it to the northern rail-line area and does not state its exact position. | The peak-gamma marker's text implied a false precision of location. Reworded as a site-wide figure; the 120,000–170,000 CPM TP-03 reading is now a separate, correctly located entry. | 2026-07-20 | Live on the site 2026-07-18 to 2026-07-20; fixed before the v1.0.0 freeze. |
| Sampling range stated as "1969–2024" with "about a third" of points sampled recently. Both figures were computed from a partial subset of points. | Understated the true span and overstated recency in the Start Here panel. The canonical `last_sampled` field gives 1948–2025 and 141 of 785 points (18%) sampled 2020 or later. | 2026-07-20 | v1.0.1, v1.1.0. Fixed in v1.2.0. |
| Start Here panel stated the map "cannot show present-day conditions — many records are historical." | Understated the data: some sampling is from 2022–2024. An over-cautious claim is still inaccurate. Reworded to describe the map as not a synchronised snapshot. | 2026-07-20 | v1.0.0. Fixed in v1.0.1. |
| Census-tract and impact-zone popups became unclickable after a performance change placed the hazard-site markers on a canvas layer spanning the map above them. | Tract statistics could not be opened on the live site. Fixed with a map-level hit test. | 2026-07-19 | Live on the site before the v1.0.0 freeze; not in a tagged release. |
| Location-only wells (mapped for position, without attached chemistry) displayed "undefined distinct" under chemicals detected. | Cosmetic but misleading popup text. Changed to "none tabulated (location point)". | 2026-07-19 | Live on the site before the v1.0.0 freeze; not in a tagged release. |
| The Frontier Chemical Royal Avenue site (932110) was absent from the radiation tab. Its own Final Engineering Report (April 2014) devotes section 5.10 to radiological material and heads Table 5.10 "TENORM Waste Characterization", tabulating Radium-226/228, Thorium-234, Uranium-235/238 and their decay products in site soil; 608 cubic yards of TENORM remain on site beneath the cover. The site was missing because membership of the radiation cross-list was a hand-maintained list, and it had never been added. | The site is now listed as TENORM, raising the radiation cross-list from 17 sites to 18. Membership is no longer hand-maintained: a site joins the list either from a named agency determination (DOE, USACE, NYSDEC) or automatically from a radionuclide detection verified against a table cell in its own documents, so a site can no longer be omitted by oversight. Sites on the list with no agency classification are labelled "Other". | 2026-07-31 | v1.0.0 onward. |
| Site popups listed contaminants taken from the free-text `chemicals` field of the NYSDEC site record. That text was never checked against a source document — no measurement, table cell or report page stood behind any of it — yet it was presented under the heading "Contaminants" exactly as verified data would be. | Every chemical listing on the map has been replaced with the output of the document-extraction pipeline, which publishes a chemical only when a human-checkable table cell in that site's own reports reports it as detected. 117 of 254 sites now carry verified listings (3,669 site-chemical entries, 102 distinct chemicals). Sites whose chemicals exist but are not yet verifiable — almost always because the source pages are scans awaiting OCR validation — now list nothing and say so (41 sites). Sites with no extracted chemistry yet say that instead (96 sites). Some sites therefore show fewer chemicals than before, or none; the earlier lists were not evidence, and replacing them is not a reduction in what is known. | 2026-07-31 | v1.2.0 onward. |
| A mapped site at 3640 Packard Road, Niagara Falls (shown as "Unnamed Site", designation "Information Not Available") is not corroborated by any agency record. Checked against the full NYSDEC remediation registry, EPA's facility and Superfund records, and the USACE Formerly Used Defense Sites inventory: none of them list it. Its only source was an internal candidate list. | **As recorded 2026-07-21:** the site was removed from the map; it carried no chemical or radiological data, so no other figure was affected, and the mapped site count changed from 255 to 254. The record was retained in the project's internal data, marked as unverified.<br><br>**Revised 2026-07-30 — the accurate word is *withheld*, not *removed*.** The entry is withheld at export while the record is deliberately kept in both `csv/Niagara_Hazard_Sites_MASTER.csv` and the GeoPackage, which is why the GeoPackage carries one more hazard-site row than the map shows. It is withheld because it renders as "Unnamed Site / Information Not Available" with nothing behind it — **not because it has been disproven.** Absence from the agency registries is not proof the property does not exist, and the non-agency avenues have not been worked yet: county parcel and assessment records, the deed index, Sanborn fire-insurance maps, city directories, historical aerials and newspaper archives. It republishes if any evidence of existence is found. | 2026-07-21, revised 2026-07-30 | v1.0.0 onward. |

---


## Errors caught before publication

These were found during development or testing and **never reached the live site or any tagged
release**. They are recorded because they show the quality-assurance process working, not because
they affected published output.

| Error | How it was caught | Date |
|---|---|---|
| Dibenzofuran was mapped to the "Dioxins / furans" category because a text pattern matched "furan". Would have implied TCDD-class dioxin contamination the data does not support. | AI review before deploy; the category mapping was corrected. | 2026-07-18 |
| Northern Ethanol Redevelopment Site was nearly tagged as a FUSRAP radioactive site. The DOE elimination report shows natural-ratio TENORM from licensed commercial operations, and DOE removed the site from FUSRAP; it is tagged TENORM. | Caught by reading the primary document before tagging. | 2026-07-18 |
| The Address Lookup tool evaluated site-footprint containment only for the nearest site by centroid, so a location inside a large site (e.g. LOOW, ~7,500 acres) could have been shown a small nearby site instead. Now evaluated across all sites. | Caught in testing during the v1.1.0 build. | 2026-07-20 |
| Boundary rings were grouped by (site, name, type, document, page), which merged genuinely separate polygons and then sorted their vertices together — scrambling them. LOOW's five hazard areas (14 + 4 + 6 … vertices) rendered as one 36-vertex tangle; Carborundum's six became 33, and 914 Tactical's two became 11. Rings are delimited by `vertex_seq` restarting, not by name. | Reported by C. McShane on seeing the rendered subsite outlines; fix validated by checking every ring's vertex count against the exported `n_vertices` (0 disagreements). | 2026-08-08 |
| Deployed sampling locations were about to be indexed by (site, location_id), which would have silently collapsed duplicate ids already present — cutting Niagara Falls Storage Site from 645 points to 420. Deployed features are now the base list and are never deduplicated. | Caught by the N_after ≥ N_before assertion, which aborted the write. | 2026-08-08 |
| Former Mill No. 2 was about to be duplicated: 223 locations filed under the directory name `former_mill2` plus 223 "new" ones under master row C932150. The directory-to-site remap is now applied to existing features as well as incoming ones. | Caught by the same assertion in the same dry run. | 2026-08-08 |

---

## Scope clarification (2026-07-20)

Removed exploratory Love Canal analyses and the preliminary ecological cancer regression from the
active repository. These analyses were incomplete, had not undergone independent methodological
review, and do not support the interactive map's published findings. Their removal does not alter
the underlying public-source datasets or current map layers. Previous versions remain documented in
Git history.

---

If you find an error not listed here, please open an issue:
<https://github.com/C-McShane/Thundering-Waters/issues/new>. Where this project differs from a cited
primary source, the primary source governs.
