# Northern Ethanol & Covanta — radioactive characterization (2026-07-18)

Two adjacent 47th-Street sites in the former Electro Metallurgical (Electromet) corridor.
Both carry the same radioactive legacy: **TENORM** (technologically-enhanced naturally-occurring
radioactive material) — thorium + radium + uranium slag from mid-century uranium/thorium
processing. Verified against DOE FUSRAP records and the NYSDEC BCP RI reports.

## Northern Ethanol Redevelopment Site [C932143] — 137 47th St (the former Electromet plant)
- **rad_class = TENORM; rad_iso = U, Th.** Basis: the DOE **FUSRAP Elimination Report for the
  Former Electro Metallurgical Company**. Electromet produced uranium metal from UF4 for the
  Manhattan Project/AEC (1942-53), then processed uranium AND thorium commercially under NYS
  radioactive-material license 950-0139 (1965-72: 505 tons of slag bearing 9,212 lb thorium
  dioxide + 1,293 lb uranium oxide). Surface soil around Buildings 163/166 (and Bldg 163
  wall/floor seams) has gamma-emitting radionuclides above DOE guidelines in the **thorium-232
  and uranium-238 decay chains**.
- **Key finding (verify-don't-assume):** DOE determined the U-238/Ra-226 ratio indicates
  NATURAL uranium — i.e. the contamination is TENORM from the *licensed commercial* operations,
  **not** the MED/AEC weapons work — and therefore **eliminated the site from FUSRAP** (no
  federal remedial authority). So TENORM is the correct class, NOT FUSRAP.
- **Data limit:** stalled BCP — only a BCP application + a fully **scanned** RI *Work Plan*
  (no published RI results). No monitoring-well / soil analytical data exists publicly to map.

## Covanta Niagara Rail-to-Truck Intermodal Facility [C932160] — 139 47th St (ex-Praxair "15-Acre")
- **rad_class = TENORM; rad_iso = Th, Ra, U.** Radioactive slag interspersed in surface
  soil/fill; NORM enhanced by industrial processing, primarily **thorium and radium** (Th-232
  and U-238/Ra-226 chains), tied to the Electromet uranium/thorium legacy.
- A **MARSSIM gamma walkover survey** (Ludlum 2×2 NaI, Bicron µRem; Ra-226 scan MDC <3 pCi/g)
  delineated the impacted-slag zones. Gamma-spectroscopy (EPA 901.1m) of slag samples detected
  Radium-226, Radium-228, Actinium-228, Thallium-208, Thorium-234, Uranium-235 and Bi/Pb
  daughters. Represented on the map as a **Radioactive Soil Zone** ("Covanta impacted-slag area").
- Duplicate C932160 hazard-site feature removed; site name normalized.

## STAGED (not yet done) — the full point-level Covanta extraction
The completed Covanta BCP has a rich 668-page RI (`docs/radioactive_sites/Covanta_RI_Vol1.pdf`)
with monitoring wells (MW), test pits (TP), geoprobes (GP), surface soils (SS) and the gamma
survey. Two reasons it is staged rather than rushed:
1. **Locations are in scanned figures** (only the test-pit page p71 has vector labels) — the
   MW/TP/GP/SS points need the RI figures hand-georeferenced (like the NFSS/Mill-2 method).
2. **Radiological lab pages stack multiple samples per page** — a naive parse mismatches
   radionuclide values (raw p655 shows a Bi-214 ≈29 pCi/g that a per-page parse drops). The
   per-sample gamma-spec results must be parsed carefully by lab-ID block before use.
Next installment: georeference the RI location figures, parse the per-sample radiological
tables by lab-ID, and map each MW/soil point with its chemistry + radiological result.
