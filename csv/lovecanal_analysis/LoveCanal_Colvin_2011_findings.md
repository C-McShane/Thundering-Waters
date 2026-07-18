# Direction #1 — the pool-digger numbers: 2011 Colvin Blvd sewer NAPL

Prepared 2026-07-17. Sources: DecDocs 932020 (2011 work plans, text-extractable),
EPA Fourth Five-Year Review (2019, `docs/LoveCanal_932020_2019_EPA_Fourth_FiveYearReview.pdf`,
text-extractable), Niagara Gazette + Buffalo News + Courthouse News (secondary).

## What happened (documented, authoritative)
- Early 2011: the Niagara Falls Water Board found chemically-impacted sediments —
  **including NAPL (non-aqueous phase liquid, i.e. pure product)** — in the sanitary
  sewer along **Colvin Blvd, east of 96th St** (LaSalle area).
- Feb 1–23, 2011: GSH/OCC (contractor Conestoga-Rovers/CRA) **replaced ~50 ft of
  sewer** (Colvin, between 96th & 97th), **excavated impacted bedding + soil to
  bedrock**, removed NAPL + liquids, and **removed contaminated sediment along
  Colvin from 97th St to the 91st St lift station**.
- The work + results were documented in the **March 4, 2011 "Sanitary Sewer
  Investigation and Remediation Report" (SSIR, CRA)** — the report with the actual
  concentrations, NAPL extent, and sample maps. **NOT yet located** in the DecDocs
  932020 folder listing (the two 2011 docs there are *work plans*, not results).
- **MW-3** installed July 1, 2011 in the repaired-sewer bedding to watch for
  residual NAPL. Weekly monitoring Jul 19–Oct 7, 2011, then quarterly since Nov
  2012: **no NAPL or sheen through Dec 2018.** EPA conclusion: the sporadically-
  observed NAPL "was likely limited in volume and mobility." (MW-3 reads clean in
  our well dataset — now explained.)
- **MW-01 / MW-02** bedrock wells installed up/downgradient of the repair.

## The source/age conclusion (KEY for the "old event" hypothesis)
- Regulatory finding (per news coverage of the DEC determination): the contaminated
  sewer bedding is **"not a result of current operations at the Love Canal site,"**
  and DEC stated the chemical **"likely predates the Love Canal facility."**
  ==> This is the official version of the user's "one big event years ago / outside
  of 1978" idea: legacy contamination residing in the sewer bedding, NOT an active
  containment breach.
- CAVEAT: the "predates" phrasing is from SECONDARY (news) coverage. For NYT use,
  the PRIMARY DEC determination (letter/report) must be obtained and quoted exactly
  — "predates the facility" (pre-1942 dumping?) vs "predates the current
  remediation/containment (pre-1978)" are very different claims and the news
  headline may be imprecise.

## Pathway reframing (reconciles all prior null results)
The transport route to the Colvin/99th corridor is the **sanitary-sewer bedding /
utility trench** — a man-made preferential conduit, historically THE Love Canal
off-site migration route — NOT diffuse clay migration. This is why:
- the groundwater monitoring wells near 99th St read clean (contamination was in the
  sewer corridor, not the aquifer they sample);
- there is no rainfall correlation (a NAPL/sewer-sediment problem isn't rain-modulated
  like a water-table plume);
- the pool digger hit contamination at 10–15 ft (sewer-depth bedding), not a deep plume.

## EPA 2019 containment statement (context, and a reconciliation note)
EPA 4th FYR: during ~2014–2018 the inward gradient "ranged from 0.98 ft to 3.70 ft
outside the barrier drain at each of the six nested-piezometer strings," and flow
inside the drain is also toward the drain → containment capturing leachate + some
outside groundwater. This is the AGGREGATE per-string statement; our finer per-medium
analysis (deep Glacial Till reversal at 1190) is a sub-string nuance EPA does not
break out — consistent, not contradictory. MW-10135 (23,000 ug/L) is described by EPA
as "isolated to the immediate area around the well," stable — matches our finding.

## Plottable spatial features saved (map-ready)
`web/data/lovecanal_colvin_2011.geojson` (6 features):
- sewer sediment-removal corridor, Colvin 97th→91st (LineString, precision=approx_street_grid)
- 50-ft repair + NAPL-excavation segment, Colvin 96th–97th (LineString, approx)
- MW-3 (in sewer bedding), MW-01, MW-02 (Points, precision=surveyed, from wells_dec)
- pool-digger reported contamination point (approx, user report), ~230 m E of the
  documented 2011 sewer NAPL — same Colvin corridor, adjacent but not identical spot.
NOTE: corridor lines are grid-estimated (intersection geocoding failed); wells are
surveyed. Upgrade the corridor with the SSIR figure or a proper sewer GIS layer.

## Open items / prizes still to get
1. **March 2011 SSIR report** — actual sediment/NAPL concentrations + sample map near
   the leak. Try: DEC DER search (SiteCode 932020), EPA SEMS (semspub.epa.gov), or the
   2011/2012 PRR appendices.
2. **Primary DEC "predates" determination** — exact wording, for citation.
3. **Eastward extent** — the documented work stopped at 97th; the pool digger is at
   99th (2 blocks E). Whether contamination was characterized east toward 99th is a gap.
