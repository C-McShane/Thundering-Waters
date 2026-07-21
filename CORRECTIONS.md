# Corrections log

Errors found in this project and how they were resolved. This log exists so that corrections are
part of the public record rather than quietly overwritten.

**On "affected versions":** the interactive map deploys continuously from the `main` branch to
GitHub Pages, so an error can be briefly live on the public site without ever appearing in a tagged
release. All tagged releases (v1.0.0 and later) were created on 2026-07-20. Where an error was
caught and fixed before the first freeze, it never entered a tagged release; the column notes when
it was nonetheless live on the site.

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

---


## Errors caught before publication

These were found during development or testing and **never reached the live site or any tagged
release**. They are recorded because they show the quality-assurance process working, not because
they affected published output.

| Error | How it was caught | Date |
|---|---|---|
| Dibenzofuran was mapped to the "Dioxins / furans" category because a text pattern matched "furan". Would have implied TCDD-class dioxin contamination the data does not support. | AI review before deploy; entry removed. | 2026-07-18 |
| Northern Ethanol Redevelopment Site was nearly tagged as a FUSRAP radioactive site. The DOE elimination report shows natural-ratio TENORM from licensed commercial operations, and DOE removed the site from FUSRAP; it is tagged TENORM. | Caught by reading the primary document before tagging. | 2026-07-18 |
| The Address Lookup tool evaluated site-footprint containment only for the nearest site by centroid, so a location inside a large site (e.g. LOOW, ~7,500 acres) could have been shown a small nearby site instead. Now evaluated across all sites. | Caught in testing during the v1.1.0 build. | 2026-07-20 |

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
