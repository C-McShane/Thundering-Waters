// ── DESIGNATION COLORS ──────────────────────────────────────────────────────
// Neon palette — vivid solid cores over soft same-colour halos (heatmap × points).
const DESIG_COLOR = {
  'NY State Superfund':              '#ff2a2a',   // neon red
  'Brownfield':                      '#ffd400',   // neon yellow
  'Federal Facility':                '#22b0ff',   // neon blue
  'FUSRAP-LM':                       '#c24dff',   // neon violet
  'RCRA Corrective Action':          '#ff7a1a',   // neon orange
  'Federal NPL - Active':            '#ff0066',   // neon crimson
  'Federal NPL - Deleted':           '#9fb0bd',   // muted (deleted)
  'Federal CERCLA (Non-NPL)':        '#1cf0c8',   // neon teal
  'Federal CERCLA / Brownfield':     '#e0803a',   // burnt amber
  'Environmental Restoration Program':'#2bff7a',   // neon green
  'Voluntary Cleanup Program':       '#00e6a0',   // neon spring green
  'Information Not Available':        '#8a97a3',   // muted grey
};
function desigColor(d) { return DESIG_COLOR[d] || '#888'; }

// ── CHOROPLETH COLOR ─────────────────────────────────────────────────────────
function choroColor(pct) {
  if (!pct || pct === 0) return 'rgba(245,240,224,0.15)';
  if (pct <= 3.6)  return 'rgba(244,192,112,0.45)';
  if (pct <= 6.7)  return 'rgba(224,112,48,0.50)';
  if (pct <= 9.9)  return 'rgba(192,64,32,0.55)';
  if (pct <= 13.3) return 'rgba(160,32,16,0.60)';
  if (pct <= 20.2) return 'rgba(128,16,8,0.65)';
  if (pct <= 35.7) return 'rgba(96,0,4,0.70)';
  return 'rgba(64,0,2,0.75)';
}

// ── CANCER SIR (block-group choropleth) ──────────────────────────────────────
const SIR_BINS = [
  { max: 0.75,     color: '#3a6ea5', label: '< 0.75' },
  { max: 0.90,     color: '#7ea8c9', label: '0.75 – 0.90' },
  { max: 1.10,     color: '#ece6d6', label: '0.90 – 1.10' },
  { max: 1.33,     color: '#f0b85f', label: '1.10 – 1.33' },
  { max: 1.67,     color: '#e07d38', label: '1.33 – 1.67' },
  { max: 2.00,     color: '#c0392b', label: '1.67 – 2.00' },
  { max: Infinity, color: '#7a1212', label: '≥ 2.00' },
];
function sirColor(sir) {
  if (sir === null || sir === undefined) return null;   // no data / suppressed
  if (sir === 0) return '#5a5a63';                       // no cases recorded
  for (const b of SIR_BINS) if (sir <= b.max) return b.color;
  return '#7a1212';
}
let cancerData = null;
function renderCancer(cx) {
  layers.cancer.clearLayers();
  const legend = document.getElementById('cancer-legend');
  if (!cx) { map.removeLayer(layers.cancer); if (legend) legend.style.display = 'none'; return; }
  // avoid stacking two choropleths: switch the tract-contamination layer off while a cancer is shown
  if (map.hasLayer(layers.tracts)) {
    map.removeLayer(layers.tracts);
    const t = document.getElementById('toggle-tracts');
    if (t) { t.classList.remove('active'); const cb = t.querySelector('input'); if (cb) cb.checked = false; }
    const lg = document.getElementById('legend-tracts'); if (lg) lg.style.display = 'none';
  }
  L.geoJSON(cancerData, {
    pane: 'cancerPane',
    style: f => {
      const c = sirColor(f.properties['sir_' + cx]);
      if (c === null) return { fillColor: '#20202a', fillOpacity: 0.18, color: '#33333a', weight: 0.4, opacity: 0.5 };
      return { fillColor: c, fillOpacity: 0.72, color: '#141416', weight: 0.5, opacity: 0.8 };
    },
    onEachFeature: (f, layer) => {
      layer.bindPopup(cancerPopup(cx, f.properties), { maxWidth: 270 });
      layer.on('mouseover', function () { this.setStyle({ weight: 1.6, color: '#d4a843' }); });
      layer.on('mouseout',  function () { const c = sirColor(f.properties['sir_' + cx]); this.setStyle({ weight: c === null ? 0.4 : 0.5, color: c === null ? '#33333a' : '#141416' }); });
    }
  }).addTo(layers.cancer);
  if (!map.hasLayer(layers.cancer)) layers.cancer.addTo(map);
  if (legend) { legend.innerHTML = cancerLegendHTML(cx); legend.style.display = 'block'; }
}
function cancerPopup(cx, p) {
  const sir = p['sir_' + cx];
  const sirTxt = (sir === null || sir === undefined) ? 'No data' : (sir === 0 ? 'No cases' : sir.toFixed(2));
  const obs = (p['obs_' + cx] != null) ? p['obs_' + cx] : '\u2014';
  const exp = (p['exp_' + cx] != null) ? p['exp_' + cx].toFixed(1) : '\u2014';
  const hl = p['hlarea_' + cx];
  const hlTxt = hl === 1
    ? '<div class="cancer-pop-hl">Belongs to a NYSDOH <b>highlighted area</b> for ' + cx + ' \u2014 an area with at least 50% more cases than expected, unlikely to be chance.</div>'
    : hl === 0 ? '<div class="cancer-pop-nohl">Not in a NYSDOH highlighted area for ' + cx + '.</div>' : '';
  const nOther = (p.merged_bg_count || 1) - 1;
  const merged = p.merged_area
    ? '<div class="cancer-pop-merged">\u2691 NYSDOH merged this block group with ' + nOther + ' other'
      + (nOther === 1 ? '' : 's') + ' to protect privacy (fewer than 6 male or 6 female cases). '
      + 'The figures above are for the <b>combined area</b> (' + p.doh_region + '), not this block group alone.</div>'
    : '';
  return '<div class="popup-tract">'
    + '<div class="popup-tract-name">' + (p.name || p.geoid) + ' \u2014 ' + cx + '</div>'
    + '<div class="popup-tract-grid">'
    + '<div><div class="popup-tract-stat-val">' + sirTxt + '</div><div class="popup-tract-stat-lbl">SIR (obs/exp)</div></div>'
    + '<div><div class="popup-tract-stat-val">' + obs + '</div><div class="popup-tract-stat-lbl">Observed</div></div>'
    + '<div><div class="popup-tract-stat-val">' + exp + '</div><div class="popup-tract-stat-lbl">Expected</div></div>'
    + '<div><div class="popup-tract-stat-val">' + (p.pop ? Math.round(p.pop).toLocaleString() : '\u2014') + '</div><div class="popup-tract-stat-lbl">Population</div></div>'
    + '</div>' + hlTxt + merged + '</div>';
}
function cancerLegendHTML(cx) {
  let s = `<div class="cancer-legend-title">${cx} — SIR vs NYS</div>`;
  for (const b of SIR_BINS) s += `<div class="legend-item"><div class="legend-dot" style="border-radius:2px;background:${b.color}"></div><div class="legend-txt">${b.label}</div></div>`;
  s += `<div class="legend-item"><div class="legend-dot" style="border-radius:2px;background:#5a5a63"></div><div class="legend-txt">No cases recorded</div></div>`;
  s += `<div class="legend-item"><div class="legend-dot" style="border-radius:2px;background:#20202a;border:1px solid #33333a"></div><div class="legend-txt">No data / suppressed</div></div>`;
  return s;
}

// ── HIGHLIGHTED AREAS (NYSDOH spatial scan statistic) ────────────────────────
// Binary membership, deliberately NOT a gradient: NYSDOH states each block group either
// belongs to a highlighted area or it does not. This is a CLUSTER-level determination,
// not a significance test of an individual block group's own rate.
function clearTractChoropleth() {
  if (!map.hasLayer(layers.tracts)) return;
  map.removeLayer(layers.tracts);
  const t = document.getElementById('toggle-tracts');
  if (t) { t.classList.remove('active'); const cb = t.querySelector('input'); if (cb) cb.checked = false; }
  const lg = document.getElementById('legend-tracts'); if (lg) lg.style.display = 'none';
}
function hlStyle(h) {
  if (h === 1) return { fillColor: '#d1332e', fillOpacity: 0.62, color: '#141416', weight: 0.5, opacity: 0.85 };
  if (h === 0) return { fillColor: '#2a2a34', fillOpacity: 0.30, color: '#33333a', weight: 0.4, opacity: 0.6 };
  return { fillColor: '#20202a', fillOpacity: 0.15, color: '#33333a', weight: 0.4, opacity: 0.4 };
}
function renderCancerHighlight(cx) {
  layers.cancer.clearLayers();
  const legend = document.getElementById('cancer-legend');
  const note = document.getElementById('cancer-hl-note');
  if (!cx) {
    map.removeLayer(layers.cancer);
    if (legend) legend.style.display = 'none';
    if (note) note.textContent = 'Select a cancer to map the block groups belonging to a highlighted area.';
    return;
  }
  clearTractChoropleth();
  L.geoJSON(cancerData, {
    pane: 'cancerPane',
    style: f => hlStyle(f.properties['hlarea_' + cx]),
    onEachFeature: (f, layer) => {
      layer.bindPopup(cancerPopup(cx, f.properties), { maxWidth: 280 });
      layer.on('mouseover', function () { this.setStyle({ weight: 1.6, color: '#d4a843' }); });
      layer.on('mouseout',  function () { this.setStyle(hlStyle(f.properties['hlarea_' + cx])); });
    }
  }).addTo(layers.cancer);
  if (!map.hasLayer(layers.cancer)) layers.cancer.addTo(map);
  const st = STATS && STATS.cancer && STATS.cancer[cx];
  if (note && st) {
    const tot = STATS.counts.cancer_doh_regions;
    const big = st.highlighted_regions > tot * 0.6
      ? ' That is most of the county &mdash; NYSDOH&rsquo;s scan statistic found <b>one large contiguous cluster</b> here, not many separate hotspots.' : '';
    note.innerHTML = st.highlighted_regions === 0
      ? '<b>No</b> reporting region in Niagara County belongs to a highlighted area for <b>' + cx + '</b>.'
      : '<b>' + st.highlighted_regions + '</b> of <b>' + tot + '</b> NYSDOH reporting regions in Niagara County belong to a highlighted area for <b>' + cx + '</b>.' + big;
  }
  if (legend) {
    legend.innerHTML = '<div class="cancer-legend-title">' + cx + ' &mdash; NYSDOH highlighted areas</div>'
      + '<div class="legend-item"><div class="legend-dot" style="border-radius:2px;background:#d1332e"></div><div class="legend-txt">In a highlighted area (&ge;50% more cases than expected, unlikely to be chance)</div></div>'
      + '<div class="legend-item"><div class="legend-dot" style="border-radius:2px;background:#2a2a34"></div><div class="legend-txt">Not in a highlighted area</div></div>'
      + '<div class="legend-item"><div class="legend-dot" style="border-radius:2px;background:#20202a;border:1px solid #33333a"></div><div class="legend-txt">No data / suppressed (not zero)</div></div>';
    legend.style.display = 'block';
  }
}
// Both selectors are built from statistics.json — no county figure is ever hand-typed.
function buildCancerSelectors() {
  if (!STATS || !STATS.cancer) return;
  const cancers = Object.keys(STATS.cancer);
  const hlBox = document.getElementById('cancer-hl-select');
  const sirBox = document.getElementById('cancer-sir-select');
  const optOff = n => '<label class="cancer-opt active"><input type="radio" name="' + n + '" value="" checked><span class="cancer-name">Off</span></label>';
  if (hlBox) {
    hlBox.innerHTML = optOff('cancer-hl')
      + cancers.slice().sort((a, b) => STATS.cancer[b].highlighted_regions - STATS.cancer[a].highlighted_regions)
        .map(c => '<label class="cancer-opt"><input type="radio" name="cancer-hl" value="' + c + '"><span class="cancer-name">' + c
          + '</span><span class="cancer-sir">' + STATS.cancer[c].highlighted_regions + '</span></label>').join('');
  }
  if (sirBox) {
    sirBox.innerHTML = optOff('cancer')
      + cancers.slice().sort((a, b) => STATS.cancer[b].sir - STATS.cancer[a].sir)
        .map(c => '<label class="cancer-opt"><input type="radio" name="cancer" value="' + c + '"><span class="cancer-name">' + c
          + '</span><span class="cancer-sir">' + STATS.cancer[c].sir.toFixed(2) + '</span></label>').join('');
  }
  // one choropleth at a time: choosing in one section resets the other
  const mark = (box, el) => box.querySelectorAll('.cancer-opt').forEach(o => o.classList.toggle('active', o.contains(el)));
  if (hlBox) hlBox.querySelectorAll('input').forEach(r => r.addEventListener('change', () => {
    mark(hlBox, r);
    const off = sirBox && sirBox.querySelector('input[value=""]');
    if (off) { off.checked = true; mark(sirBox, off); }
    const lg = document.getElementById('cancer-legend'); if (lg) lg.style.display = 'none';
    renderCancerHighlight(r.value);
  }));
  if (sirBox) sirBox.querySelectorAll('input').forEach(r => r.addEventListener('change', () => {
    mark(sirBox, r);
    const off = hlBox && hlBox.querySelector('input[value=""]');
    if (off) { off.checked = true; mark(hlBox, off); }
    const note = document.getElementById('cancer-hl-note');
    if (note) note.textContent = 'Select a cancer to map the block groups belonging to a highlighted area.';
    if (cancerData) renderCancer(r.value);
  }));
}


// ── CITATIONS (URGENT_TODO item 5) ───────────────────────────────────────────
// Every "Selected high detection" must carry: report title, table, page, sample medium,
// sampling date, named comparison standard, source link and selection criterion.
// Until a field is sourced it reads "Information to be added" in findings.json, and the
// entry renders a visible PENDING marker — so an uncited number can never look finished.
function citePending(v) { return !v || v === 'Information to be added'; }
function citeHTML(c) {
  if (!c) return '';
  const filled = Object.keys(c).filter(k => !citePending(c[k]));
  if (!filled.length) return '<div class="finding-cite pending">\u2691 Source citation \u2014 information to be added</div>';
  const bits = [];
  if (!citePending(c.report_title)) bits.push(c.report_title);
  if (!citePending(c.table)) bits.push('Table ' + c.table);
  if (!citePending(c.page)) bits.push('p.' + c.page);
  if (!citePending(c.sample_medium)) bits.push(c.sample_medium);
  if (!citePending(c.sampling_date)) bits.push(c.sampling_date);
  let out = '<div class="finding-cite">' + bits.join(' \u00b7 ');
  if (!citePending(c.comparison_standard)) out += ' \u00b7 vs ' + c.comparison_standard;
  if (!citePending(c.source_link)) out += ' \u00b7 <a href="' + c.source_link + '" target="_blank" rel="noopener">source</a>';
  const missing = 8 - filled.length;
  if (missing > 0) out += ' <span class="pending">(' + missing + ' field' + (missing === 1 ? '' : 's') + ' pending)</span>';
  out += '</div>';
  return out;
}

// ── CHEMICAL FILTER + RADIOACTIVE ────────────────────────────────────────────
const CHEM_TOP10 = ['Dioxins / TCDD','Asbestos','Benzene','Vinyl chloride','Arsenic','PCBs','Hexavalent chromium','TCE','Cadmium','Lead'];
const CHEM_ALSO  = ['Benzo(a)pyrene','Lindane / BHC','Beryllium','Mercury','Hexachlorobenzene','Cyanide'];
const ELEVATED = new Set(['mesothelioma','bladder','lung','esophagus','oral','brain']);
// type: 'cancer' items are phrased "increased risk of ___"; 'noncancer' items get a
// separate, non-carcinogenic-effects sentence so we never say e.g. "neurotoxicity cancer"
const CHEM_ASSOC = {
  'Dioxins / TCDD':      { type: 'cancer',    items: ['multiple cancer types'] },
  'Asbestos':            { type: 'cancer',    items: ['mesothelioma', 'lung cancer'] },
  'Benzene':             { type: 'cancer',    items: ['leukemia'] },
  'Vinyl chloride':      { type: 'cancer',    items: ['liver cancer'] },
  'Arsenic':             { type: 'cancer',    items: ['bladder cancer', 'lung cancer', 'skin cancer'] },
  'PCBs':                { type: 'cancer',    items: ['liver cancer'] },
  'Hexavalent chromium': { type: 'cancer',    items: ['lung cancer'] },
  'TCE':                 { type: 'cancer',    items: ['kidney cancer', 'non-Hodgkin lymphoma'] },
  'Cadmium':             { type: 'cancer',    items: ['lung cancer', 'kidney cancer', 'prostate cancer'] },
  'Lead':                { type: 'noncancer', items: ['neurotoxicity'] },
  'Benzo(a)pyrene':      { type: 'cancer',    items: ['lung cancer', 'skin cancer'] },
  'Lindane / BHC':       { type: 'cancer',    items: ['non-Hodgkin lymphoma'] },
  'Beryllium':           { type: 'cancer',    items: ['lung cancer'] },
  'Mercury':             { type: 'noncancer', items: ['neurotoxicity'] },
  'Hexachlorobenzene':   { type: 'cancer',    items: ['liver cancer'] },
  'Cyanide':             { type: 'noncancer', items: ['acute toxicity'] },
};
function formatAssociation(cx) {
  const a = CHEM_ASSOC[cx];
  if (!a) return '';
  const marked = a.items.map(item => {
    const isElev = [...ELEVATED].some(e => item.toLowerCase().includes(e));
    return isElev ? `<span class="elev">${item}↑</span>` : item;
  });
  const joined = marked.length <= 1 ? marked[0] : marked.slice(0, -1).join(', ') + ' and ' + marked[marked.length - 1];
  return a.type === 'cancer'
    ? `Associated with increased risk of ${joined} in toxicological or epidemiological research.`
    : `Associated with ${joined} in toxicological or epidemiological research.`;
}
function chemCount(cx) { return allSiteFeatures.filter(f => (f.properties.chems || []).includes(cx)).length; }
function populateChemDropdown() {
  const sel = document.getElementById('chem-select');
  sel.querySelector('option').textContent = `All sites (${allSiteFeatures.length})`;
  const present = [...new Set(allSiteFeatures.flatMap(f => f.properties.chems || []))].sort((a, b) => a.localeCompare(b));
  present.forEach(n => { const o = document.createElement('option'); o.value = n; o.textContent = `${n} (${chemCount(n)})`; sel.appendChild(o); });
  sel.addEventListener('change', () => filterByChemical(sel.value));
}
function filterByChemical(cx) {
  const note = document.getElementById('chem-note');
  if (!cx) { note.innerHTML = 'Shows sites that list the selected contaminant. Reflects <em>recorded</em> chemicals ' + chemCoverageText() + '.'; }
  else {
    const subset = allSiteFeatures.filter(f => (f.properties.chems || []).includes(cx));
    note.innerHTML = `<b>${subset.length}</b> sites list <b>${cx}</b>. ${formatAssociation(cx)} <span style="color:var(--dim)">(↑ = elevated in county)</span>`;
  }
  applySiteFilters();
}
// ── SITE-TYPE FILTER (Hazard Sites tab) ──────────────────────────────────────
// The programme-type checkboxes double as the colour legend; they combine with the
// chemical dropdown (a site must pass BOTH filters to render).
let activeDesignations = new Set(Object.keys(DESIG_COLOR));
function desigOf(p) { return p.designation || 'Information Not Available'; }
function populateSiteTypeFilter() {
  const counts = {};
  allSiteFeatures.forEach(f => { const d = desigOf(f.properties); counts[d] = (counts[d] || 0) + 1; });
  const order = Object.keys(DESIG_COLOR).filter(d => counts[d]);
  Object.keys(counts).forEach(d => { if (!order.includes(d)) order.push(d); });
  activeDesignations = new Set(order);
  const box = document.getElementById('site-type-filter');
  box.innerHTML = order.map(d =>
    `<label class="stf-opt"><input type="checkbox" class="stf-check-site" value="${d}" checked>`
    + `<span class="stf-swatch" style="background:${desigColor(d)};border:2px solid #0d0d0e"></span>`
    + `<span class="stf-name">${d}</span><span class="stf-count">${counts[d]}</span></label>`).join('');
  box.querySelectorAll('.stf-check-site').forEach(cb => cb.addEventListener('change', () => {
    if (cb.checked) activeDesignations.add(cb.value); else activeDesignations.delete(cb.value);
    applySiteFilters();
  }));
}
function applySiteFilters() {
  const cx = document.getElementById('chem-select').value;
  let feats = allSiteFeatures.filter(f => activeDesignations.has(desigOf(f.properties)));
  if (cx) feats = feats.filter(f => (f.properties.chems || []).includes(cx));
  renderSites(feats);
}
function radMatch(p, filters) {
  if (!p.rad_class) return false;
  return filters.some(fl => fl === 'TENORM' ? p.rad_class === 'TENORM' : (p.rad_iso || []).includes(fl));
}
// ── RADIATION TAB (sites + wells/soil, isotope-level) ────────────────────────
let radData = null;   // data/radionuclides.json
const RAD_SITE_ORDER  = ['Uranium','Thorium','Radium','TENORM','FUSRAP','MED-AEC'];
const RAD_SITE_LABEL  = { Uranium:'Uranium', Thorium:'Thorium', Radium:'Radium',
  TENORM:'TENORM (industrial slag)', FUSRAP:'FUSRAP (Manhattan Project legacy)', 'MED-AEC':'MED-AEC (weapons-era facility)' };
const RAD_PARENT_ORDER = ['Uranium','Thorium','Radium','Radon','Other'];
function radTrefoilIcon(sz) {
  return L.divIcon({ className:'well-droplet', iconSize:[sz,sz], iconAnchor:[sz/2,sz/2],
    html: RAD_TREFOIL.replace('width="20" height="20"', `width="${sz}" height="${sz}"`) });
}
function buildRadSelectors() {
  const sf = document.getElementById('rad-site-filter');
  sf.innerHTML = RAD_SITE_ORDER.filter(k => radData.sites[k]).map(k =>
    `<label class="rad-opt"><input type="checkbox" class="rad-site-check" value="${k}"><span class="rad-swatch"></span>`
    + `<span class="rad-name">${RAD_SITE_LABEL[k] || k}</span><span class="rad-count">${new Set(radData.sites[k].map(s=>s.program_number+'|'+s.site_name)).size}</span></label>`).join('');
  sf.querySelectorAll('.rad-site-check').forEach(cb => cb.addEventListener('change', renderRadSites));
  const wf = document.getElementById('rad-well-filter');
  let html = '';
  RAD_PARENT_ORDER.forEach(par => {
    const kids = radData.groups[par] || [];
    if (!kids.length) return;
    html += `<div class="rad-group-label">${par}</div>`;
    kids.forEach(rn => {
      const n = radData.wells[rn].points.length;
      const yrs = [...new Set(radData.wells[rn].points.flatMap(p => Object.keys(p.series)))].map(Number);
      const span = yrs.length ? (Math.min(...yrs) === Math.max(...yrs) ? `${Math.min(...yrs)}` : `${Math.min(...yrs)}–${Math.max(...yrs)}`) : '';
      html += `<label class="rad-opt"><input type="checkbox" class="rad-well-check" value="${rn}"><span class="rad-swatch"></span>`
        + `<span class="rad-name">${rn}<span class="rad-yr">${span}</span></span><span class="rad-count">${n}</span></label>`;
    });
  });
  wf.innerHTML = html;
  wf.querySelectorAll('.rad-well-check').forEach(cb => cb.addEventListener('change', renderRadWells));
}
function renderRadSites() {
  layers.radioactive.clearLayers();
  const sel = [...document.querySelectorAll('.rad-site-check:checked')].map(c => c.value);
  document.querySelectorAll('#rad-site-filter .rad-opt').forEach(o => o.classList.toggle('active', o.querySelector('input').checked));
  const note = document.getElementById('rad-site-note');
  if (!sel.length) { map.removeLayer(layers.radioactive); note.textContent = 'Select a material to show the sites that contain it.'; return; }
  const seen = new Set(); let n = 0;
  sel.forEach(mat => (radData.sites[mat] || []).forEach(s => {
    const id = s.program_number + '|' + s.site_name;
    if (seen.has(id)) return; seen.add(id); n++;
    L.circleMarker([s.lat, s.lon], { pane:'radioactivePane', renderer: radCanvas, radius:9, fillColor:'#f5e050', color:'#7a1212', weight:2.5, fillOpacity:0.9 })
      .bindPopup(radSitePopup(s), { maxWidth:290 }).addTo(layers.radioactive);
  }));
  if (!map.hasLayer(layers.radioactive)) layers.radioactive.addTo(map);
  note.innerHTML = `<b>${n}</b> radioactive site${n===1?'':'s'} — ${sel.map(s => RAD_SITE_LABEL[s] || s).join(', ')}.`;
}
function radSitePopup(s) {
  const names = { U:'Uranium', Th:'Thorium', Ra:'Radium' };
  const iso = (s.iso && s.iso.length) ? s.iso.map(i => names[i] || i).join(', ') : 'not specified';
  const CLASS = { FUSRAP:'FUSRAP — residual Manhattan Project / AEC radioactive contamination (DOE Legacy Mgmt / USACE).',
    TENORM:'TENORM — technologically-enhanced naturally-occurring radioactive material (industrial slag).',
    'MED-AEC':'Manhattan Engineer District / AEC facility documented to have handled radioactive material (EEOICPA).' };
  return `<div class="popup-inner"><div class="popup-tags"><span class="popup-tag" style="background:#f5e05022;color:#e8d44a;border:1px solid #f5e05055">${s.rad_class||'Radioactive'}</span></div>
    <div class="popup-name">${s.site_name}</div>
    <div class="popup-field"><div class="popup-field-lbl">Radionuclides</div><div class="popup-field-val">${iso}</div></div>
    <div class="popup-narrative">${s.basis || CLASS[s.rad_class] || ''}</div></div>`;
}
function renderRadWells() {
  layers.radWells.clearLayers();
  const sel = [...document.querySelectorAll('.rad-well-check:checked')].map(c => c.value);
  document.querySelectorAll('#rad-well-filter .rad-opt').forEach(o => o.classList.toggle('active', o.querySelector('input').checked));
  const note = document.getElementById('rad-well-note');
  if (!sel.length) { map.removeLayer(layers.radWells); note.innerHTML = 'Select a radionuclide to map the wells &amp; soil that carry it.'; updateRadTrend(null); return; }
  const seen = new Set(); let nw = 0, ns = 0;
  const parents = new Set(sel.map(rn => radData.wells[rn].parent));
  sel.forEach(rn => radData.wells[rn].points.forEach(p => {
    const id = 'w|' + rn + '|' + p.well_id + '|' + p.src;
    if (seen.has(id)) return; seen.add(id); nw++;
    L.marker([p.lat, p.lon], { icon: radTrefoilIcon(16), pane:'wellsPane' })
      .bindPopup(radWellPopup(rn, radData.wells[rn], p), { maxWidth:300 }).addTo(layers.radWells);
  }));
  (radData.soil || []).forEach(z => {
    if (!z.materials.some(m => parents.has(m))) return;
    const id = 's|' + z.zone_id; if (seen.has(id)) return; seen.add(id); ns++;
    L.marker([z.lat, z.lon], { icon: radTrefoilIcon(20), pane:'wellsPane' })
      .bindPopup(radSoilPopup(z), { maxWidth:300 }).addTo(layers.radWells);
  });
  if (!map.hasLayer(layers.radWells)) layers.radWells.addTo(map);
  note.innerHTML = `<b>${nw}</b> well${nw===1?'':'s'}${ns ? ` + <b>${ns}</b> soil zone${ns===1?'':'s'}` : ''} carry ${sel.join(', ')}.`;
  updateRadTrend(sel);
}
function radWellPopup(rn, w, p) {
  const has = Object.keys(p.series).length;
  const plot = `<div class="conc-plot-note plot-withdrawn">⚠ withdrawn pending unit validation</div>`;
  return `<div class="popup-inner"><div class="popup-tags"><span class="popup-tag" style="background:#f5d00022;color:#e0c000;border:1px solid #f5d00055">${p.src} · ${rn}</span></div>
    <div class="popup-name">${p.well_id}</div><div class="popup-addr">${p.site || ''} · ${p.medium || ''}</div>${plot}</div>`;
}
function radSoilPopup(z) {
  return `<div class="popup-inner"><div class="popup-tags"><span class="popup-tag" style="background:#f5d00022;color:#e0c000;border:1px solid #f5d00055">Soil / slag</span></div>
    <div class="popup-name">${z.zone_id}</div><div class="popup-addr">${z.site} · ${z.medium}</div>
    <div class="conc-plot-note" style="margin-top:6px">Radionuclides present: ${z.materials.join(', ')}. Gamma-survey readings ⚠ withdrawn pending unit validation.</div></div>`;
}
// Floating trend panel (same bottom-left control as the wells tab): x = year,
// y = cumulative number of wells & soil zones registering the selected radionuclide(s).
const SOIL_SURVEY_YEAR = 2012;   // Mill No. 2 gamma survey (RI year) — soil zones have no time series
function updateRadTrend(sel) {
  const _b = document.getElementById('rad-trend'); if (_b) { _b.style.display = 'none'; _b.innerHTML = ''; } return;  // WITHDRAWN pending validation
  if (!chemTrendEl) return;
  if (!sel || !sel.length) { chemTrendEl.style.display = 'none'; return; }
  const firstYear = {};   // well/soil key -> first year it registers the selection
  sel.forEach(rn => radData.wells[rn].points.forEach(p => {
    const yrs = Object.entries(p.series).filter(([y, v]) => v[1] === 'detect').map(([y]) => +y);
    if (!yrs.length) return;
    const k = 'w|' + p.well_id + '|' + p.src, y = Math.min(...yrs);
    if (firstYear[k] === undefined || y < firstYear[k]) firstYear[k] = y;
  }));
  const parents = new Set(sel.map(rn => radData.wells[rn].parent));
  let nsoil = 0;
  (radData.soil || []).forEach(z => { if (z.materials.some(m => parents.has(m))) { firstYear['s|' + z.zone_id] = SOIL_SURVEY_YEAR; nsoil++; } });
  const yearsArr = Object.values(firstYear);
  if (!yearsArr.length) { chemTrendEl.style.display = 'none'; return; }
  const y0 = Math.min(...yearsArr), y1 = Math.max(...yearsArr);
  const years = []; for (let y = y0; y <= y1; y++) years.push(y);
  const counts = years.map(y => yearsArr.filter(v => v <= y).length);
  chemTrendEl.innerHTML = radTrendSVG(sel, years, counts, yearsArr.length, nsoil);
  chemTrendEl.style.display = 'block';
}
function radTrendSVG(sel, years, counts, total, nsoil) {
  const W = 214, H = 116, x0 = 30, x1 = W - 8, yT = 24, yB = H - 18;
  const y0 = years[0], y1 = years[years.length - 1];
  const sx = yr => y1 === y0 ? (x0 + x1) / 2 : x0 + (yr - y0) / (y1 - y0) * (x1 - x0);
  const cmax = Math.max(...counts, 1);
  const sy = c => yB - c / cmax * (yB - yT);
  const linePts = counts.map((c, i) => `${sx(years[i]).toFixed(1)},${sy(c).toFixed(1)}`).join(' ');
  const title = sel.length === 1 ? sel[0] : `${sel.length} radionuclides`;
  return `<div class="ctp-title">Wells &amp; soil with <b>${title}</b></div>`
    + `<svg width="${W}" height="${H}" viewBox="0 0 ${W} ${H}">`
    + `<polygon points="${x0},${yB} ${linePts} ${x1},${yB}" fill="#f5d00030"/>`
    + `<polyline points="${linePts}" fill="none" stroke="#f5d000" stroke-width="1.8"/>`
    + `<line x1="${x0}" y1="${yB}" x2="${x1}" y2="${yB}" stroke="#ffffff22" stroke-width="0.5"/>`
    + `<text x="${x0 - 3}" y="${yB + 3}" text-anchor="end" font-size="8" fill="#9aa4b2">0</text>`
    + `<text x="${x0 - 3}" y="${(sy(cmax) + 3).toFixed(1)}" text-anchor="end" font-size="8" fill="#9aa4b2">${cmax}</text>`
    + `<text x="${x0}" y="${H - 5}" font-size="8" fill="#9aa4b2">${y0}</text>`
    + `<text x="${x1}" y="${H - 5}" text-anchor="end" font-size="8" fill="#9aa4b2">${y1}</text>`
    + `</svg><div class="ctp-sub">cumulative · ${total} site${total === 1 ? '' : 's'}${nsoil ? ` (incl. ${nsoil} soil)` : ''}</div><div class="ctp-caveat">Cumulative monitoring history &mdash; not contemporaneous plume extent. Additional points over time may reflect new sampling locations or newly available records as well as environmental change.</div>`;
}

// ── MAP INIT ─────────────────────────────────────────────────────────────────
const map = L.map('map', {
  center: [43.14, -78.98],
  zoom: 11,
  zoomControl: true,
});

// Basemap — CartoDB dark, split into base + a separate labels layer so the place
// labels can be lightened independently of the rest of the basemap.
L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_nolabels/{z}/{x}/{y}{r}.png', {
  attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> &copy; <a href="https://carto.com/">CARTO</a>',
  subdomains: 'abcd', maxZoom: 19
}).addTo(map);
map.createPane('basemapLabels');
map.getPane('basemapLabels').style.zIndex = 210;          // just above the base tiles, below every overlay
map.getPane('basemapLabels').style.pointerEvents = 'none';
L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_only_labels/{z}/{x}/{y}{r}.png', {
  pane: 'basemapLabels', subdomains: 'abcd', maxZoom: 19
}).addTo(map);
// A CSS filter on a tile layer forces a full recomposite every frame, so only lighten the
// labels while the map is still — drop the filter during pan/zoom for smoothness.
const LABEL_FILTER = 'brightness(1.45)';
const labelsPaneEl = map.getPane('basemapLabels');
labelsPaneEl.style.filter = LABEL_FILTER;
map.on('movestart zoomstart', () => { labelsPaneEl.style.filter = 'none'; });
map.on('moveend zoomend',     () => { labelsPaneEl.style.filter = LABEL_FILTER; });

// ── LAYER GROUPS ─────────────────────────────────────────────────────────────
// water sits just above the basemap tiles (200) but below every data overlay
map.createPane('waterPane');
map.getPane('waterPane').style.zIndex = 250;
// dedicated pane so the cancer choropleth renders below roads/boundary but above the basemap
map.createPane('cancerPane');
map.getPane('cancerPane').style.zIndex = 350;
// hazard sites always render above every choropleth/roads/radioactive layer,
// regardless of toggle order — dedicated panes, not insertion order, control this
map.createPane('sitesPane');
map.getPane('sitesPane').style.zIndex = 450;         // above overlayPane (400)
map.createPane('radioactivePane');
map.getPane('radioactivePane').style.zIndex = 460;   // above sitesPane, so the
                                                       // radioactive highlight ring is never hidden by the base site dot
map.createPane('wellsPane');
map.getPane('wellsPane').style.zIndex = 470;         // droplets ride above hazard sites when both are shown
map.createPane('sareaTocPane');
map.getPane('sareaTocPane').style.zIndex = 480;      // TOC-over-time overlay rides above everything else
// Canvas renderers collapse the many circleMarkers (sites, radioactive) into one canvas per
// pane — far cheaper than one SVG path each, identical look, and it helps at every zoom.
const sitesCanvas = L.canvas({ pane: 'sitesPane', padding: 0.5 });
const radCanvas   = L.canvas({ pane: 'radioactivePane', padding: 0.5 });

const layers = {
  water:       L.layerGroup().addTo(map),   // on by default (base water context)
  cancer:      L.layerGroup(),              // off by default (selector)
  tracts:      L.layerGroup(),              // off by default
  iz:          L.layerGroup(),              // off by default
  roads:       L.layerGroup(),              // off by default (purple dashed; on-demand context)
  sites:       L.layerGroup().addTo(map),   // only hazard sites on at load
  radioactive: L.layerGroup(),              // off by default (isotope sub-filters)
  wellsWqp:    L.layerGroup(),              // off by default (Monitoring Wells tab)
  wellsDec:    L.layerGroup(),              // off by default (Monitoring Wells tab)
  wellsLegacy: L.layerGroup(),              // off by default (Monitoring Wells tab)
  lcPumps:     L.layerGroup(),              // Love Canal pump chambers / leachate tanks
  lcPiezo:     L.layerGroup(),              // Love Canal piezometers (water-level series)
  soilRad:     L.layerGroup(),              // radioactive soil/slag zones (non-well soil sites)
  radWells:    L.layerGroup(),              // Radiation tab: wells & soil selected by radionuclide
  lcWells:     L.layerGroup(),              // Love Canal monitoring wells (dedicated toggle)
  sareaToc:    L.layerGroup(),              // off by default (S-Area TOC-over-time selector); independent
                                             // of the wellsDec toggle/filter so the two features don't collide
};

// ── ROAD STYLE ───────────────────────────────────────────────────────────────
function roadStyle(cls) {
  return cls === 'Highway'
    ? { color: '#9d8fbf', weight: 2.4, opacity: 0.95, lineCap: 'round', dashArray: '5,3' }
    : { color: '#9d8fbf', weight: 1.9, opacity: 0.9,  lineCap: 'round', dashArray: '4,3' };
}
// rough geometry length (for picking one label anchor per road name)
function geomLen(g) {
  const seg = a => a.reduce((s, p, i) => i ? s + Math.hypot(p[0] - a[i-1][0], p[1] - a[i-1][1]) : 0, 0);
  if (g.type === 'LineString') return seg(g.coordinates);
  if (g.type === 'MultiLineString') return g.coordinates.reduce((s, l) => s + seg(l), 0);
  return 0;
}
const LABEL_ZOOM = 14;  // persistent road labels appear at/above this zoom
const SITE_ROAD_ZOOM = 16;  // local streets near regulated sites appear at/above this zoom

// ── POPUP HELPERS ────────────────────────────────────────────────────────────
function desigTag(d) {
  const color = desigColor(d);
  return `<span class="popup-tag" style="background:${color}22;color:${color};border:1px solid ${color}44">${d}</span>`;
}

function sitePopup(p) {
  const addr = [p.address, p.city].filter(Boolean).join(', ');
  const acres = p.acres != null ? `${parseFloat(p.acres).toLocaleString()} ac` : 'Not recorded';
  const link = p.website
    ? `<a class="popup-link" href="${p.website}" target="_blank" rel="noopener">View official record ↗</a>`
    : '';
  // Primary-source reports (verify the data) + the site's full document folder.
  const reps = (p.reports && p.reports.length) || p.docs_url
    ? `<div class="popup-reports">`
      + ((p.reports && p.reports.length) ? `<div class="popup-field-lbl">Source reports — verify the data</div>` : '')
      + (p.reports || []).map(rp => `<a class="popup-report" href="${rp.url}" target="_blank" rel="noopener">📄 ${rp.title} ↗</a>`).join('')
      + (p.docs_url ? `<a class="popup-report popup-report-all" href="${p.docs_url}" target="_blank" rel="noopener">📁 Browse all NYSDEC documents for this site ↗</a>` : '')
      + `</div>`
    : '';
  const narr = p.narrative
    ? `<div class="popup-narrative">${p.narrative}</div>` : '';
  const chems = p.chemicals
    ? `<div class="popup-field"><div class="popup-field-lbl">Contaminants</div><div class="popup-field-val">${p.chemicals.substring(0,120)}${p.chemicals.length>120?'…':''}</div></div>` : '';
  return `<div class="popup-inner">
    <div class="popup-tags">${desigTag(p.designation)}</div>
    <div class="popup-name">${p.site_name}</div>
    ${addr ? `<div class="popup-addr">${addr}</div>` : ''}
    <div class="popup-row">
      <div class="popup-field"><div class="popup-field-lbl">Acreage</div><div class="popup-field-val">${acres}</div></div>
      ${p.program_type ? `<div class="popup-field"><div class="popup-field-lbl">Program</div><div class="popup-field-val">${p.program_type}</div></div>` : ''}
    </div>
    ${chems}
    ${narr}
    ${reps}
    ${link}
  </div>`;
}

function tractPopup(p) {
  const pct = p.coverage_pct ? p.coverage_pct.toFixed(1) : '0.0';
  const acres = p.cont_acres ? p.cont_acres.toLocaleString(undefined,{maximumFractionDigits:0}) : '0';
  return `<div class="popup-tract">
    <div class="popup-tract-name">${p.namelsad || p.name}</div>
    <div class="popup-tract-grid">
      <div><div class="popup-tract-stat-val">${p.site_count}</div><div class="popup-tract-stat-lbl">Hazard Sites</div></div>
      <div><div class="popup-tract-stat-val">${pct}%</div><div class="popup-tract-stat-lbl">Land Contaminated</div></div>
      <div><div class="popup-tract-stat-val">${acres}</div><div class="popup-tract-stat-lbl">Contaminated Acres</div></div>
      <div><div class="popup-tract-stat-val">${p.aland_acres ? Math.round(p.aland_acres).toLocaleString() : '—'}</div><div class="popup-tract-stat-lbl">Total Land Acres</div></div>
    </div>
  </div>`;
}

// ── DATA LOADING ─────────────────────────────────────────────────────────────
let allSiteFeatures = [];

// ── STATISTICS ───────────────────────────────────────────────────────────────
// Every count the interface displays comes from data/statistics.json, generated by
// web/build_statistics.py. Nothing is hand-typed: re-run the generator after any data
// change and the UI follows. Elements opt in with data-stat="<key>" (+ optional
// data-suffix). This is the fix for the README/interface count drift.
let STATS = null;
function applyStatistics() {
  if (!STATS) return;
  document.querySelectorAll('[data-stat]').forEach(el => {
    const v = STATS.counts[el.dataset.stat];
    if (v != null) el.textContent = v.toLocaleString() + (el.dataset.suffix || '');
  });
  const sel = document.getElementById('chem-select');
  const note = document.getElementById('chem-note');
  if (note && sel && !sel.value)
    note.innerHTML = 'Shows sites that list the selected contaminant. Reflects <em>recorded</em> chemicals ' + chemCoverageText() + '.';
}
// Curated `chems` is what the filter actually searches — deliberately NOT the larger
// raw NYSDEC free-text population (hazard_sites_raw_chem_text), which is a different thing.
function chemCoverageText() {
  if (!STATS) return '';
  const c = STATS.counts;
  return `(${c.hazard_sites_with_chemicals} of ${c.hazard_sites} sites list any)`;
}

async function loadAll() {
  // revalidate data files so an updated map never renders against a stale cached GeoJSON
  const gj = u => fetch(u, { cache: 'no-cache' }).then(r => r.json());
  const [sitesData, tractsData, izData, roadsData, cancerGeo, waterData, wellsWqpData, wellsDecData, wellsLegacyData] = await Promise.all([
    gj('data/hazard_sites.geojson'),
    gj('data/census_tracts.geojson'),
    gj('data/impact_zone.geojson'),
    gj('data/major_roads.geojson'),
    gj('data/cancer_sir.geojson'),
    gj('data/water.geojson'),
    gj('data/wells_wqp.geojson'),
    gj('data/wells_dec.geojson'),
    gj('data/wells_legacy.geojson'),
  ]);
  const [lcPumpsData, lcPiezoData, soilRadData, siteRoadsData, radNuclides, statsData, findingsData] = await Promise.all([
    gj('data/wells_lc_pumps.geojson'), gj('data/wells_lc_piezometers.geojson'),
    gj('data/soil_radzones.geojson'), gj('data/site_roads.geojson'), gj('data/radionuclides.json'),
    gj('data/statistics.json'), gj('data/findings.json'),
  ]);
  STATS = statsData; applyStatistics(); buildCancerSelectors();
  SITE_FINDINGS = {};   // WITHDRAWN pending validation (was findingsData.radiation_by_site)
  CHEM_FINDINGS = [];   // WITHDRAWN pending validation (was findingsData.chemicals_by_site)
  renderLcPumps(lcPumpsData.features); lcPumpsF = lcPumpsData.features;
  renderLcPiezo(lcPiezoData.features); lcPiezoF = lcPiezoData.features;
  soilRadFeatures = soilRadData.features;   // per-site toggles built after the wells load (below)
  radData = radNuclides; buildRadSelectors();
  cancerData = cancerGeo;

  // Water — polygon bodies get a stark semi-transparent fill; creek lines (added
  // where a monitoring site sits on/beside them) render as visible blue strokes.
  L.geoJSON(waterData, {
    pane: 'waterPane',
    style: f => f.properties.kind === 'line'
      ? { color: '#5fd0ff', weight: 1.7, opacity: 0.85, lineCap: 'round' }
      : { fillColor: '#1fa6e0', fillOpacity: 0.42, color: '#5fd0ff', weight: 0.8, opacity: 0.75 },
    onEachFeature: (f, layer) => {
      if (f.properties.name) layer.bindTooltip(f.properties.name, { sticky: true, direction: 'top', className: 'road-tip' });
      if (f.properties.kind === 'line') {
        layer.on('mouseover', function () { this.setStyle({ weight: 3.2, opacity: 1 }); });
        layer.on('mouseout',  function () { this.setStyle({ weight: 1.7, opacity: 0.85 }); });
      }
    }
  }).addTo(layers.water);

  // Major roads (arterials + highways) — purple dashed, on by default, with dynamic
  // viewport-following labels: whenever a road is on screen its label is placed on the
  // visible part of it (the vertex nearest the map centre that is within the view).
  const roadReps = {};  // road name -> longest feature (representative geometry)
  const roadsGeo = L.geoJSON(roadsData, {
    style: f => roadStyle(f.properties.road_class),
    onEachFeature: (f, layer) => {
      const name = f.properties.name;
      layer.on('mouseover', function () { this.setStyle({ weight: roadStyle(f.properties.road_class).weight + 2, opacity: 1 }); });
      layer.on('mouseout',  function () { this.setStyle(roadStyle(f.properties.road_class)); });
      if (name) {
        const len = geomLen(f.geometry);
        if (!roadReps[name] || len > roadReps[name].len) roadReps[name] = { len, geom: f.geometry };
      }
    }
  });
  roadsGeo.addTo(layers.roads);
  // representative polyline per road name (longest segment) as [lat,lng] vertices
  const roadLineByName = {};
  Object.entries(roadReps).forEach(([name, rep]) => {
    const g = rep.geom;
    const coords = g.type === 'LineString' ? g.coordinates
      : (g.coordinates.reduce((a, b) => (a && a.length >= b.length ? a : b), null) || []);
    roadLineByName[name] = coords.map(c => [c[1], c[0]]);
  });
  const _emptyIcon = L.divIcon({ className: '', html: '', iconSize: [0, 0] });
  let roadLabelMarkers = [];
  function updateRoadLabels() {
    roadLabelMarkers.forEach(m => layers.roads.removeLayer(m));
    roadLabelMarkers = [];
    if (!map.hasLayer(layers.roads)) return;
    const b = map.getBounds().pad(-0.03), c = map.getCenter();
    const placed = [];   // container-pixel positions of labels already placed (greedy de-overlap)
    // longest roads first so arterials win label priority when two would collide
    Object.keys(roadLineByName).sort((a, z) => roadReps[z].len - roadReps[a].len).forEach(name => {
      const pts = roadLineByName[name];
      let best = null, bd = Infinity;
      for (const p of pts) { if (!b.contains(p)) continue; const d = map.distance(c, p); if (d < bd) { bd = d; best = p; } }
      if (!best) return;
      const cp = map.latLngToContainerPoint(best);
      if (placed.some(q => Math.abs(q.x - cp.x) < 52 && Math.abs(q.y - cp.y) < 15)) return;   // would overlap → skip
      placed.push(cp);
      const mk = L.marker(best, { icon: _emptyIcon, interactive: false, keyboard: false })
        .bindTooltip(name, { permanent: true, direction: 'center', className: 'road-label' });
      layers.roads.addLayer(mk);
      roadLabelMarkers.push(mk);
    });
  }
  window.__updateRoadLabels = updateRoadLabels;   // let the roads toggle refresh labels immediately
  updateRoadLabels();
  map.on('moveend', updateRoadLabels);   // moveend fires after both pan and zoom

  // Local streets near major regulated sites (Superfund/FUSRAP/RCRA/NPL/CERCLA) — appear
  // only when the Roads layer is on AND you're zoomed into a site. Purplish-grey + dashed
  // to read as local wayfinding, distinct from the tan arterials.
  const siteRoadBase = { color: '#9d8fbf', weight: 1.6, opacity: 0.92, lineCap: 'round', dashArray: '4,3' };
  const siteRoadsGeo = L.geoJSON(siteRoadsData, {
    style: () => siteRoadBase,
    onEachFeature: (f, l) => {
      l.on('mouseover', function () { this.setStyle({ weight: 3.4, opacity: 1 }); });
      l.on('mouseout',  function () { this.setStyle(siteRoadBase); });
    }
  });
  // labels anchored at the point on each road nearest the site that pulled it in
  const siteRoadLabels = L.layerGroup();
  siteRoadsData.features.forEach(f => {
    const a = f.properties.anchor; if (!a) return;
    L.marker([a[1], a[0]], { icon: _emptyIcon, interactive: false, keyboard: false })
      .bindTooltip(f.properties.name, { permanent: true, direction: 'center', className: 'site-road-label' })
      .addTo(siteRoadLabels);
  });
  function refreshSiteRoads() {
    const show = map.getZoom() >= SITE_ROAD_ZOOM;
    if (show) {
      if (!layers.roads.hasLayer(siteRoadsGeo))   layers.roads.addLayer(siteRoadsGeo);
      if (!layers.roads.hasLayer(siteRoadLabels)) layers.roads.addLayer(siteRoadLabels);
    } else {
      if (layers.roads.hasLayer(siteRoadsGeo))   layers.roads.removeLayer(siteRoadsGeo);
      if (layers.roads.hasLayer(siteRoadLabels)) layers.roads.removeLayer(siteRoadLabels);
    }
  }
  refreshSiteRoads();
  map.on('zoomend', refreshSiteRoads);

  // Census tracts choropleth
  L.geoJSON(tractsData, {
    style: f => ({
      fillColor: choroColor(f.properties.coverage_pct),
      fillOpacity: 1,
      color: '#3a3a42', weight: 0.8, opacity: 0.8
    }),
    onEachFeature: (f, layer) => {
      layer.bindPopup(tractPopup(f.properties), { maxWidth: 280 });
      layer.on('mouseover', function() { this.setStyle({ color: '#d4a843', weight: 1.5 }); });
      layer.on('mouseout',  function() { this.setStyle({ color: '#3a3a42', weight: 0.8 }); });
    }
  }).addTo(layers.tracts);

  // Impact zone — single dissolved perimeter
  L.geoJSON(izData, {
    style: { color: '#d4a843', weight: 2.5, fill: true, fillColor: '#d4a843', fillOpacity: 0.05, dashArray: '5 4' },
    onEachFeature: (f, layer) => {
      const p = f.properties;
      layer.bindPopup(`<div class="popup-tract">
        <div class="popup-tract-name">${p.name}</div>
        <div class="popup-tract-grid">
          <div><div class="popup-tract-stat-val">${p.site_count}</div><div class="popup-tract-stat-lbl">Hazard Sites</div></div>
          <div><div class="popup-tract-stat-val">${p.cont_acres != null ? Math.round(p.cont_acres).toLocaleString() : '—'}</div><div class="popup-tract-stat-lbl">Contaminated Acres</div></div>
        </div></div>`, { maxWidth: 240 });
      layer.on('mouseover', function () { this.setStyle({ weight: 3.5, fillOpacity: 0.09 }); });
      layer.on('mouseout',  function () { this.setStyle({ weight: 2.5, fillOpacity: 0.05 }); });
    }
  }).addTo(layers.iz);

  // Hazard sites
  allSiteFeatures = sitesData.features;
  renderSites(sitesData.features);

  // Monitoring wells (off by default; toggled from the Monitoring Wells tab)
  wellsWqpF = wellsWqpData.features;
  wellsDecF = wellsDecData.features;
  wellsLegacyF = wellsLegacyData.features;
  renderWells(wellsWqpF, layers.wellsWqp);
  renderWells(wellsDecF, layers.wellsDec);
  renderWells(wellsLegacyF, layers.wellsLegacy);
  renderWells(wellsDecF.filter(f => f.properties.site === 'Love Canal (Occidental)'), layers.lcWells);   // dedicated Love Canal wells toggle
  buildSoilSiteToggles();   // Radiation-tab per-site toggles (wells + soil), now that legacy wells are loaded
  populateWellDropdown();
  buildChemFindings();      // Chemicals-tab strongest-findings highlights
  buildSearchIndex();       // unified search over sites + wells/pits/soil/piezometers
  buildRecencyFilter();     // "last sampled" encoding + filter
  populateSampleTypeFilter();
  populateWellYearDropdown();
  populateSAreaTocYearDropdown();

  // Chemical dropdown + site-type filter
  populateChemDropdown();
  populateSiteTypeFilter();
}

function renderSites(features) {
  layers.sites.clearLayers();
  features.forEach(f => {
    const p = f.properties;
    const color = desigColor(p.designation);
    const [lon, lat] = f.geometry.coordinates;
    // large soft halo of the same colour — where sites cluster the halos stack and
    // read like a heatmap, while each retains a precise point
    L.circleMarker([lat, lon], {
      pane: 'sitesPane', renderer: sitesCanvas, interactive: false,
      radius: 15, fillColor: color, fillOpacity: 0.14, color: color, weight: 0, opacity: 0,
    }).addTo(layers.sites);
    // small, intense, neon solid core
    const marker = L.circleMarker([lat, lon], {
      pane: 'sitesPane', renderer: sitesCanvas,
      radius: 3.4, fillColor: color, color: '#0a0a0c', weight: 0.7, fillOpacity: 1,
    });
    marker.bindPopup(sitePopup(p), { maxWidth: 340 });
    marker.addTo(layers.sites);
    marker._siteProps = p;
  });
}

// ── MONITORING WELLS ─────────────────────────────────────────────────────────
// Water-droplet symbol, height scaled by the number of chemicals detected at the
// well (sqrt so a well with 100 detects isn't 100× a well with 1). Two sources
// coloured distinctly; a shared chemical dropdown filters both.
let wellsWqpF = [], wellsDecF = [], wellsLegacyF = [], lcPiezoF = [], lcPumpsF = [];
// Water-drop symbol: blue rim (the water) + blood-red core (the contamination).
// WQP = bright red, DEC = deep blood-red, so the two sources stay distinguishable.
const WELL_OUTLINE = '#8b1a2b';                                   // dark rim used by the S-Area TOC view
const WELL_FILL = '#b81d24';                                     // blood-red droplet fill (contamination) — same for every well
// Sampling TYPE is encoded by the droplet OUTLINE colour — bright hues spread across the
// wheel for max contrast on the red fill + dark map. Keep in sync with web/well_types.py.
const SAMPLE_TYPE_ORDER = ['Bedrock groundwater','Overburden groundwater','Groundwater (unspecified)','Surface water','Remediation / recovery','Soil / test hole'];
const SAMPLE_TYPE_COLORS = {
  'Bedrock groundwater':      '#2fe0d4',   // cyan
  'Overburden groundwater':   '#8de81e',   // lime
  'Groundwater (unspecified)':'#f2f2f2',   // white
  'Surface water':            '#4d9bff',   // blue
  'Remediation / recovery':   '#ffd21e',   // yellow
  'Soil / test hole':         '#ff56c4',   // magenta
};
// Sampling-type FILTER: the set of types the user has ticked. Empty by default → every well
// shows as a blood-red drop with a light-grey outline. Tick one or more types → only those
// wells show (the rest are hidden) and their outlines take the type colour.
let activeSampleTypes = new Set();
function typeStroke(t) { return SAMPLE_TYPE_COLORS[t] || '#f2f2f2'; }
const WELL_OUTLINE_DEFAULT = '#cfcfcf';
function wellHeight(n) { return Math.min(44, 13 + 3.0 * Math.sqrt(n || 0)); }
function dropletSVG(h, fill, stroke, sw, ageOpacity) {
  const w = h * 0.72, o = ageOpacity == null ? 1 : ageOpacity;
  // whole-glyph opacity carries RECENCY (older = fainter); fill/size/ring stay free for
  // contamination, chemical count and sample type respectively
  return `<svg width="${w}" height="${h}" viewBox="0 0 24 32" opacity="${o}">`
    + `<path d="M12 1 C12 1 3 14 3 21 a9 9 0 0 0 18 0 C21 14 12 1 12 1 Z" `
    + `fill="${fill}" fill-opacity="0.9" stroke="${stroke}" stroke-width="${sw || 1.7}"/></svg>`;
}
function dropletIcon(n, sampleType, lastSampled) {
  const h = wellHeight(n), w = h * 0.72;
  const lit = activeSampleTypes.has(sampleType);   // this type is ticked → light it up
  const stroke = lit ? typeStroke(sampleType) : WELL_OUTLINE_DEFAULT;
  const sw = lit ? 2.8 : 1.7;
  return L.divIcon({ className: 'well-droplet',
    html: dropletSVG(h, WELL_FILL, stroke, sw, recencyOpacity(lastSampled)),
    iconSize: [w, h], iconAnchor: [w/2, h/2] });
}
// Radiation-tab droplet: blood-red drop ringed with a black-&-yellow hazard-striped border.
function dropletSVGHazard(h, fill) {
  const w = h * 0.72, d = "M12 1 C12 1 3 14 3 21 a9 9 0 0 0 18 0 C21 14 12 1 12 1 Z";
  return `<svg width="${w}" height="${h}" viewBox="0 0 24 32">`
    + `<path d="${d}" fill="${fill}" fill-opacity="0.92" stroke="#111" stroke-width="3.6"/>`
    + `<path d="${d}" fill="none" stroke="#f5d000" stroke-width="3.6" stroke-dasharray="4.5 4.5" stroke-linecap="butt"/></svg>`;
}
function dropletIconHazard(n, lastSampled) {
  const h = wellHeight(n), w = h * 0.72;
  const o = recencyOpacity(lastSampled);
  return L.divIcon({ className: 'well-droplet',
    html: '<span style="display:block;opacity:' + o + '">' + dropletSVGHazard(h, WELL_FILL) + '</span>',
    iconSize: [w, h], iconAnchor: [w/2, h/2] });
}
// concPlotSVG: a small log-scale concentration-vs-year chart for one well+chemical.
// series = { "year": [value, "detect"|"nondetect"] }. Detected points join into a red
// line; non-detects show as hollow markers at their detection limit (tested-but-clean).
function concPlotSVG(series, title, unit) {
  unit = unit || 'µg/L';
  const yrs = Object.keys(series).map(Number).sort((a, b) => a - b);
  const pts = yrs.map(y => ({ yr: y, v: series[String(y)][0], nd: series[String(y)][1] === 'nondetect' }));
  const pos = pts.filter(p => p.v != null && p.v > 0).map(p => p.v);
  if (!pos.length) return `<div class="conc-plot-note">${title}: tested, no numeric values to plot</div>`;
  const W = 250, H = 122, x0 = 42, x1 = W - 10, yT = 8, yB = H - 22;
  const yr0 = yrs[0], yr1 = yrs[yrs.length - 1];
  const sx = yr => yr1 === yr0 ? (x0 + x1) / 2 : x0 + (yr - yr0) / (yr1 - yr0) * (x1 - x0);
  const lmin = Math.floor(Math.log10(Math.min(...pos)));
  let lmax = Math.ceil(Math.log10(Math.max(...pos))); if (lmax <= lmin) lmax = lmin + 1;
  const floor = Math.pow(10, lmin);
  const sy = v => { const lv = Math.log10((v == null || v <= 0) ? floor : v); return yB - (lv - lmin) / (lmax - lmin) * (yB - yT); };
  let grid = '';
  const step = Math.max(1, Math.ceil((lmax - lmin) / 4));
  for (let e = lmin; e <= lmax; e += step) {
    const yy = sy(Math.pow(10, e)).toFixed(1);
    const lbl = e >= 6 ? `1e${e}` : Math.pow(10, e).toLocaleString();
    grid += `<line x1="${x0}" y1="${yy}" x2="${x1}" y2="${yy}" stroke="#ffffff1a" stroke-width="0.5"/>`
      + `<text x="${x0 - 3}" y="${(+yy + 3)}" text-anchor="end" font-size="8" fill="#9aa4b2">${lbl}</text>`;
  }
  const dets = pts.filter(p => !p.nd && p.v != null && p.v > 0);
  let line = '';
  if (dets.length > 1) line = `<polyline points="${dets.map(p => `${sx(p.yr).toFixed(1)},${sy(p.v).toFixed(1)}`).join(' ')}" fill="none" stroke="#d1332e" stroke-width="1.6"/>`;
  let dots = '';
  pts.forEach(p => {
    if (p.v == null) return;
    const cx = sx(p.yr).toFixed(1), cy = sy(p.v).toFixed(1);
    dots += p.nd
      ? `<circle cx="${cx}" cy="${cy}" r="2.6" fill="none" stroke="#9aa4b2" stroke-width="1"/>`
      : `<circle cx="${cx}" cy="${cy}" r="2.8" fill="#d1332e" stroke="#4db8f0" stroke-width="0.8"/>`;
  });
  const xlab = `<text x="${x0}" y="${H - 6}" font-size="8" fill="#9aa4b2">${yr0}</text>`
    + `<text x="${x1}" y="${H - 6}" text-anchor="end" font-size="8" fill="#9aa4b2">${yr1}</text>`;
  const hasND = pts.some(p => p.nd && p.v != null);
  return `<div class="conc-plot"><div class="conc-plot-title">${title} · ${unit} (log)</div>`
    + `<svg width="${W}" height="${H}" viewBox="0 0 ${W} ${H}">${grid}${line}${dots}${xlab}</svg>`
    + `<div class="conc-plot-legend"><span class="cd">● detected</span>${hasND ? '  <span class="cn">○ non-detect (limit)</span>' : ''}</div></div>`;
}
// headlineChem: the chemical with the highest DETECTED concentration at this well —
// used to show a plot by default (no chemical picked yet) so every well with numeric
// data surfaces its worst contaminant on click, not just after using the filter.
function headlineChem(series) {
  let best = null, bestPeak = -1;
  for (const [chem, yd] of Object.entries(series)) {
    for (const v of Object.values(yd)) {
      if (v[1] === 'detect' && v[0] != null && v[0] > bestPeak) { bestPeak = v[0]; best = chem; }
    }
  }
  return bestPeak > 0 ? best : null;
}
function wellPlotBlock(p) {
  return '<div class="conc-plot-note plot-withdrawn">⚠ Concentration time-series plots are temporarily withdrawn pending source-unit validation (see CORRECTIONS.md).</div>';
}
// Remove any embedded concentration value+unit from narrative strings shown in popups,
// while sample-level values are withdrawn (e.g. well_desc "uranium exceeds 30 µg/L").
function stripValues(str) {
  if (!str) return str;
  const rx = /\d[\d.,]*\s*(µg\/L|ug\/L|mg\/kg|ng\/L|pci[\/a-z]*|cpm)/i;
  str = str.split('|').filter(seg => !rx.test(seg)).join(' · ');
  str = str.replace(/\d[\d.,]*\s*(µg\/L|ug\/L|mg\/kg|ng\/L|pci[\/a-z]*|cpm)/ig, '[value withdrawn]');
  return str.replace(/\s+/g, ' ').replace(/[·\s]+$/, '').trim();
}
function wellPopup(p) {
  const isW = p.src === 'WQP', isL = p.src === 'LEGACY';
  const title = isW ? 'Water Quality Portal' : isL ? (p.site || 'Legacy hazardous site') : (p.site || 'NYSDEC cleanup site');
  const tagc = isW ? '#e0554e' : isL ? '#d67a1e' : '#c65a68';
  const sub = stripValues(isW ? (p.site_type || 'Sampling station')
                  : isL ? (p.well_desc || p.well_role || 'Monitoring well')
                        : (p.well_role || 'Monitoring well'));
  const yr = p.latest_detect || p.latest_year;
  const lastSampledLine = '<div class="popup-lastsampled">Last sampled: <b>'
    + recencyLabel(p.last_sampled) + '</b></div>';
  // Names only — never chemicals_found, which embeds concentration values for soil sites.
  const chemNames = (p.chems && p.chems.length) ? p.chems.join('; ') : '';
  const chem = chemNames
    ? `<div class="popup-field"><div class="popup-field-lbl">Chemicals detected (${p.n_found || p.chems.length})</div><div class="popup-field-val">${chemNames.substring(0,180)}${chemNames.length>180?'…':''}</div><div class="popup-field-lbl" style="margin-top:3px;opacity:.7">Concentration values ⚠ withdrawn pending unit validation</div></div>`
    : `<div class="popup-field"><div class="popup-field-lbl">Chemicals detected</div><div class="popup-field-val">${p.n_found ? p.n_found + ' distinct' : 'none tabulated (location point)'}</div></div>`;
  const toc = '';   // Total Organic Concentration values ⚠ withdrawn pending unit validation
  const near = (isW && p.nearest_hazard)
    ? `<div class="popup-field"><div class="popup-field-lbl">Nearest hazard site</div><div class="popup-field-val">${p.nearest_hazard}${p.nearest_m!=null?` (${Math.round(p.nearest_m)} m)`:''}</div></div>` : '';
  const cp = p.coord_precision || '';
  const corridor = p.program_number === '932156'
    ? ` These wells span the multi-mile Eighteenmile Creek corridor; they are shown clustered, not at their true spread.` : '';
  const loc = /map_relative/.test(cp)
    ? `<div class="popup-loc">⚑ Well layout traced from the site's surveyed map, so the wells' <b>positions relative to each other</b> are accurate; the cluster is anchored to the site's street address, so its absolute position on this map is approximate.</div>`
    : /centroid|approx/.test(cp)
    ? `<div class="popup-loc">⚑ Approximate location — the source report gives no surveyed well coordinates, so this well is grouped at the site's mapped location.${corridor}</div>`
    : '';
  return `<div class="popup-inner">
    <div class="popup-tags"><span class="popup-tag" style="background:${tagc}22;color:${tagc};border:1px solid ${tagc}44">${title}</span></div>
    <div class="popup-name">${p.well_id || 'Well'}</div>
    <div class="popup-addr">${sub}${yr?` · latest ${yr}`:''}</div>
    ${lastSampledLine}
    ${chem}${toc}${near}
    ${wellPlotBlock(p)}
    ${loc}
  </div>`;
}
// wellPassesFilter: cx = curated chemical name or '' (any); year = integer or null (all time).
// Cumulative semantics: a (chemical,year) match counts if it was detected in `year` OR EARLIER —
// this is what makes a plume look like it's spreading to more wells as the year advances,
// rather than flickering on/off based on which exact year a well happened to be sampled.
function wellPassesFilter(p, cx, year) {
  const cy = p.chems_years || {};
  if (cx) {
    const years = cy[cx];
    if (!years) return false;
    return year == null || years.some(y => y <= year);
  }
  if (year == null) return true;
  return Object.values(cy).some(years => years.some(y => y <= year));
}
function renderWells(features, layer, filterChem, filterYear) {
  layer.clearLayers();
  features.forEach(f => {
    const p = f.properties;
    if (activeSampleTypes.size && !activeSampleTypes.has(p.sample_type)) return;   // types selected → show only those
    if (!recencyPasses(p.last_sampled)) return;                                    // "last sampled" filter
    if (!wellPassesFilter(p, filterChem, filterYear)) return;
    const [lon, lat] = f.geometry.coordinates;
    L.marker([lat, lon], { icon: dropletIcon(p.n_found, p.sample_type, p.last_sampled), pane: 'wellsPane' })
      .bindPopup(wellPopup(p), { maxWidth: 300 }).addTo(layer);
  });
}
// ── LOVE CANAL DETAIL LAYERS ─────────────────────────────────────────────────
// Piezometers carry a water-level-over-time series {medium:{'YYYY-MM-DD':elev_ft}};
// pumps/tanks are containment infrastructure (no data). Both off by default.
const LC_MEDIUM_COLORS = { 'Silty Sand/Fill':'#e0b93a', 'Fractured Clay':'#39c46a', 'Soft Clay':'#4d9bff', 'Glacial Till':'#c66ad0' };
function isoToYr(iso){ const p = iso.split('-'); return (+p[0]) + (+p[1]-1)/12; }
function waterPlotSVG(series){
  const media = Object.keys(series).filter(m => Object.keys(series[m]).length);
  if(!media.length) return '';
  const all = []; media.forEach(m => Object.entries(series[m]).forEach(([iso,e]) => all.push({x:isoToYr(iso), e})));
  const xs = all.map(p=>p.x), es = all.map(p=>p.e);
  const W=262,H=142,x0=46,x1=W-8,yT=10,yB=H-24;
  const xmin=Math.min(...xs), xmax=Math.max(...xs), emin=Math.min(...es), emax=Math.max(...es);
  const pad=(emax-emin)*0.08||1, lo=emin-pad, hi=emax+pad;
  const sx=x => xmax===xmin ? (x0+x1)/2 : x0+(x-xmin)/(xmax-xmin)*(x1-x0);
  const sy=e => yB-(e-lo)/(hi-lo)*(yB-yT);
  let grid='';
  for(let k=0;k<=3;k++){ const e=lo+(hi-lo)*k/3, yy=sy(e).toFixed(1);
    grid+=`<line x1="${x0}" y1="${yy}" x2="${x1}" y2="${yy}" stroke="#ffffff14" stroke-width="0.5"/>`
      +`<text x="${x0-3}" y="${(+yy+3)}" text-anchor="end" font-size="8" fill="#9aa4b2">${e.toFixed(0)}</text>`; }
  let lines='';
  media.forEach(m => {
    const seq = Object.entries(series[m]).map(([iso,e]) => ({x:isoToYr(iso), e})).sort((a,b)=>a.x-b.x);
    const poly = seq.map(p => `${sx(p.x).toFixed(1)},${sy(p.e).toFixed(1)}`).join(' ');
    const c = LC_MEDIUM_COLORS[m] || '#ccc';
    lines += `<polyline points="${poly}" fill="none" stroke="${c}" stroke-width="1.5"/>`
      + seq.map(p => `<circle cx="${sx(p.x).toFixed(1)}" cy="${sy(p.e).toFixed(1)}" r="1.7" fill="${c}"/>`).join('');
  });
  const xlab = `<text x="${x0}" y="${H-6}" font-size="8" fill="#9aa4b2">${Math.floor(xmin)}</text>`
    + `<text x="${x1}" y="${H-6}" text-anchor="end" font-size="8" fill="#9aa4b2">${Math.ceil(xmax)}</text>`;
  const leg = media.map(m => `<span style="color:${LC_MEDIUM_COLORS[m]||'#ccc'}">■</span> ${m}`).join('&nbsp; ');
  return `<div class="conc-plot"><div class="conc-plot-title">Water level · ft above sea level</div>`
    + `<svg width="${W}" height="${H}" viewBox="0 0 ${W} ${H}">${grid}${lines}${xlab}</svg>`
    + `<div class="conc-plot-legend" style="font-size:8.5px;line-height:1.5">${leg}</div></div>`;
}
function renderLcPiezo(features){
  layers.lcPiezo.clearLayers();
  features.forEach(f => {
    const p = f.properties, [lon,lat] = f.geometry.coordinates;
    const icon = L.divIcon({ className:'well-droplet', iconSize:[14,14], iconAnchor:[7,7],
      html:`<svg width="14" height="14" viewBox="0 0 14 14"><circle cx="7" cy="7" r="5" fill="#2f6fd0" fill-opacity="0.85" stroke="#bfe0ff" stroke-width="1.6"/></svg>` });
    const plot = `<div class="conc-plot-note plot-withdrawn">Water-level time-series plots ⚠ withdrawn pending unit validation.</div>`;
    const html = `<div class="popup-inner"><div class="popup-tags"><span class="popup-tag" style="background:#2f6fd022;color:#7fb2ff;border:1px solid #2f6fd044">Love Canal piezometer</span></div>`
      + `<div class="popup-name">${p.well_id}</div><div class="popup-addr">Groundwater level · ${p.media.length} geologic layer${p.media.length===1?'':'s'}</div>${plot}</div>`;
    L.marker([lat,lon], { icon, pane:'wellsPane' }).bindPopup(html, { maxWidth:300 }).addTo(layers.lcPiezo);
  });
}
function renderLcPumps(features){
  layers.lcPumps.clearLayers();
  features.forEach(f => {
    const p = f.properties, [lon,lat] = f.geometry.coordinates;
    const col = p.kind==='Leachate Tank' ? '#d94f4f' : '#e0b93a';
    const icon = L.divIcon({ className:'well-droplet', iconSize:[15,15], iconAnchor:[7.5,7.5],
      html:`<svg width="15" height="15" viewBox="0 0 15 15"><rect x="2.5" y="2.5" width="10" height="10" fill="${col}" fill-opacity="0.9" stroke="#111" stroke-width="1.4"/></svg>` });
    const html = `<div class="popup-inner"><div class="popup-tags"><span class="popup-tag" style="background:${col}22;color:${col};border:1px solid ${col}44">${p.kind}</span></div>`
      + `<div class="popup-name">${p.well_id}</div><div class="popup-addr">Love Canal leachate collection infrastructure</div></div>`;
    L.marker([lat,lon], { icon, pane:'wellsPane' }).bindPopup(html, { maxWidth:260 }).addTo(layers.lcPumps);
  });
}
// radiation-trefoil marker: yellow disc + 3 black blades + hub — reads "radioactive", not a water well
const RAD_TREFOIL = '<svg width="20" height="20" viewBox="0 0 18 18">'
  + '<circle cx="9" cy="9" r="8.4" fill="#f5d000" stroke="#111" stroke-width="1"/>'
  + '<path d="M9,9 L5.5,2.94 A7,7 0 0 1 12.5,2.94 Z" fill="#111"/>'
  + '<path d="M9,9 L16,9 A7,7 0 0 1 12.5,15.06 Z" fill="#111"/>'
  + '<path d="M9,9 L5.5,15.06 A7,7 0 0 1 2,9 Z" fill="#111"/>'
  + '<circle cx="9" cy="9" r="2" fill="#111"/></svg>';
// Radioactive soil zones — per-site toggles in the Radiation tab (grows as sites are added)
let soilRadFeatures = [];
const activeSoilSites = new Set();
function siteShort(s) { return (s || '').replace(/\s*\(.*?\)\s*/g, '').trim(); }   // "Former Mill No. 2 (Greenpac Mill)" -> "Former Mill No. 2"
// Editorial "strongest findings" per radioactive site — revealed when the site is toggled on.
let SITE_FINDINGS = {};   // loaded from data/findings.json
function flyToFinding(lat, lon) { map.flyTo([lat, lon], 18, { duration: 1.1 }); }
function buildSoilSiteToggles() {
  const box = document.getElementById('soil-site-toggles');
  if (!box) return;
  const bySite = {};
  soilRadFeatures.forEach(f => { const s = f.properties.site; (bySite[s] = bySite[s] || []).push(f); });
  const wellsBySite = {}, soilBySite = {};
  wellsLegacyF.forEach(f => {
    const s = f.properties.site; if (!bySite[s]) return;
    if (f.properties.sample_type === 'Soil / test hole') (soilBySite[s] = soilBySite[s] || []).push(f);
    else (wellsBySite[s] = wellsBySite[s] || []).push(f);
  });
  box.innerHTML = Object.keys(bySite).sort().map(s => {
    const nz = bySite[s].length, nw = (wellsBySite[s] || []).length, ns = (soilBySite[s] || []).length;
    const parts = [`${nz} zone${nz > 1 ? 's' : ''}`];
    if (nw) parts.push(`${nw} well${nw > 1 ? 's' : ''}`);
    if (ns) parts.push(`${ns} soil`);
    const cnt = parts.join(' · ');
    const fnd = SITE_FINDINGS[s] || null;
    const findHtml = fnd ? `<div class="site-findings" data-for="${s}" hidden>`
      + `<div class="findings-title" role="button">☢ Selected high detections<span class="findings-caret">▾</span></div>`
      + `<div class="findings-body">` + fnd.map(f =>
          `<div class="finding-wrap"><button class="finding" data-lat="${f.lat}" data-lon="${f.lon}">`
          + `<span class="finding-t">${f.t}</span><span class="finding-s">${f.s}</span></button>`
          + citeHTML(f.citation) + `</div>`).join('')
      + `</div></div>` : '';
    return `<div class="soil-site-item"><label class="layer-toggle" data-soilsite="${s}"><input type="checkbox" class="soil-site-check">`
      + `<span class="toggle-swatch" style="background:#f5d000; border:2px solid #111; border-radius:50%;"></span>`
      + `<span class="toggle-label">${siteShort(s)}</span><span class="toggle-count">${cnt}</span></label>${findHtml}</div>`;
  }).join('');
  box.querySelectorAll('.soil-site-check').forEach(cb => cb.addEventListener('change', () => {
    const lbl = cb.closest('.layer-toggle'), site = lbl.dataset.soilsite;
    if (cb.checked) { activeSoilSites.add(site); lbl.classList.add('active'); }
    else { activeSoilSites.delete(site); lbl.classList.remove('active'); }
    const fb = cb.closest('.soil-site-item').querySelector('.site-findings');
    if (fb) fb.hidden = !cb.checked;
    renderSoilRad();
  }));
  box.querySelectorAll('.findings-title').forEach(t => t.addEventListener('click', () =>
    t.parentElement.classList.toggle('collapsed')));
  box.querySelectorAll('.finding').forEach(b => b.addEventListener('click', () =>
    flyToFinding(parseFloat(b.dataset.lat), parseFloat(b.dataset.lon))));
}
function renderSoilRad() {
  layers.soilRad.clearLayers();
  // gamma slag zones for the active sites
  soilRadFeatures.forEach(f => {
    if (!activeSoilSites.has(f.properties.site)) return;
    const p = f.properties, [lon, lat] = f.geometry.coordinates;
    const icon = L.divIcon({ className:'well-droplet', iconSize:[20,20], iconAnchor:[10,10], html: RAD_TREFOIL });
    const html = `<div class="popup-inner"><div class="popup-tags"><span class="popup-tag" style="background:#f5d00022;color:#e0c000;border:1px solid #f5d00055">Radioactive soil zone</span></div>`
      + `<div class="popup-name">${p.zone_id}</div><div class="popup-addr">${p.site} · ${p.medium}</div>`
      + `<div class="conc-plot-note" style="margin-top:6px">${stripValues(p.hazard || '')} Gamma-survey readings and figures ⚠ withdrawn pending unit validation.</div>`
      + `<div class="popup-addr" style="margin-top:4px;opacity:0.75">⚑ ${stripValues(p.coord_precision)}. Source: ${p.source}</div></div>`;
    L.marker([lat, lon], { icon, pane:'wellsPane' }).bindPopup(html, { maxWidth:300 }).addTo(layers.soilRad);
  });
  // the monitoring wells that sit on those radioactive sites
  wellsLegacyF.forEach(f => {
    if (!activeSoilSites.has(f.properties.site)) return;
    const p = f.properties, [lon, lat] = f.geometry.coordinates;
    L.marker([lat, lon], { icon: dropletIconHazard(p.n_found, p.last_sampled), pane:'wellsPane' })
      .bindPopup(wellPopup(p), { maxWidth:300 }).addTo(layers.soilRad);
  });
  if (activeSoilSites.size && !map.hasLayer(layers.soilRad)) layers.soilRad.addTo(map);
  else if (!activeSoilSites.size && map.hasLayer(layers.soilRad)) map.removeLayer(layers.soilRad);
}
const WELL_CHEM_PRIORITY = ['Trichloroethene (TCE)','Tetrachloroethene (PCE)','Vinyl chloride','Benzene','Arsenic','Lead','Mercury','PFAS (PFOA/PFOS)','PCBs','Dioxins / furans','Benzo(a)pyrene','Chromium','Cadmium'];
function wellChemCount(cx) { return [...wellsWqpF, ...wellsDecF, ...wellsLegacyF].filter(f => (f.properties.chems || []).includes(cx)).length; }
function currentWellYear() {
  const v = document.getElementById('well-year-select').value;
  return v ? parseInt(v, 10) : null;
}
function autoEnableWellLayers(cx) {   // Chemicals tab: reveal the wells so a filter isn't invisible
  if (!cx) return;
  ['wellsWqp', 'wellsDec', 'wellsLegacy'].forEach(key => {
    if (!map.hasLayer(layers[key])) {
      map.addLayer(layers[key]);
      const t = document.getElementById('toggle-' + key);
      if (t) { t.classList.add('active'); const cb = t.querySelector('input'); if (cb) cb.checked = true; }
    }
  });
}
function populateWellDropdown() {
  const sel = document.getElementById('well-select');
  const total = wellsWqpF.length + wellsDecF.length + wellsLegacyF.length;
  sel.querySelector('option').textContent = `All wells (${total})`;
  const present = [...new Set([...wellsWqpF, ...wellsDecF, ...wellsLegacyF].flatMap(f => f.properties.chems || []))].sort((a, b) => a.localeCompare(b));
  present.forEach(n => { const o = document.createElement('option'); o.value = n; o.textContent = `${n} (${wellChemCount(n)})`; sel.appendChild(o); });
  sel.addEventListener('change', () => { autoEnableWellLayers(sel.value); filterWells(sel.value, currentWellYear()); updateChemTrend(); });
  // size legend
  const leg = document.getElementById('well-size-legend');
  leg.innerHTML = [1,10,40].map(n => {
    const h = wellHeight(n), w = h*0.72;
    return `<div class="wsl">${dropletSVG(h, WELL_FILL, '#cfcfcf')}<span>${n}</span></div>`;
  }).join('') + `<div class="wsl" style="align-self:center"><span>chemicals<br>detected</span></div>`;
}
// Editorial "strongest findings" for the Chemicals tab — the highest measured detections, by site.
let CHEM_FINDINGS = [];   // loaded from data/findings.json
function buildChemFindings() {
  const box = document.getElementById('chem-findings');
  if (box) box.innerHTML = '<div class="chem-note plot-withdrawn">⚠ Well/soil sample concentration values, time-series plots and selected-high-detection highlights are temporarily withdrawn pending source-unit and analyte validation. The chemical <em>lists</em> and everything else remain. See CORRECTIONS.md.</div>';
}
// Sampling-type filter: colour-coded checkboxes (double as the colour legend) that show/hide
// wells by what they sample, across all three source layers at once.
function populateSampleTypeFilter() {
  const wells = [...wellsWqpF, ...wellsDecF, ...wellsLegacyF];
  const counts = {};
  wells.forEach(f => { const t = f.properties.sample_type || 'Groundwater (unspecified)'; counts[t] = (counts[t]||0)+1; });
  const present = SAMPLE_TYPE_ORDER.filter(t => counts[t]);
  const box = document.getElementById('sample-type-filter');
  box.innerHTML = present.map(t =>
    `<label class="stf-opt"><input type="checkbox" class="stf-check" value="${t}">`
    + `<span class="stf-swatch" style="background:#b81d24;border:2px solid ${SAMPLE_TYPE_COLORS[t]}"></span>`
    + `<span class="stf-name">${t}</span><span class="stf-count">${counts[t]}</span></label>`).join('');
  box.querySelectorAll('.stf-check').forEach(cb => cb.addEventListener('change', () => {
    if (cb.checked) activeSampleTypes.add(cb.value); else activeSampleTypes.delete(cb.value);
    cb.closest('.stf-opt').classList.toggle('active', cb.checked);
    filterWells(document.getElementById('well-select').value, currentWellYear());   // re-render → outlines light up
  }));
}
function populateWellYearDropdown() {
  const sel = document.getElementById('well-year-select');
  const allYears = [...wellsWqpF, ...wellsDecF, ...wellsLegacyF]
    .flatMap(f => Object.values(f.properties.chems_years || {}))
    .flat();
  if (!allYears.length) return;
  const lo = Math.min(...allYears), hi = Math.max(...allYears);
  for (let y = hi; y >= lo; y--) {
    const o = document.createElement('option'); o.value = y; o.textContent = y;
    sel.appendChild(o);
  }
  sel.addEventListener('change', () => {
    document.getElementById('well-year-note').style.display = sel.value ? 'block' : 'none';
    filterWells(document.getElementById('well-select').value, currentWellYear());
  });
}
function filterWells(cx, year) {
  renderWells(wellsWqpF, layers.wellsWqp, cx, year);
  renderWells(wellsDecF, layers.wellsDec, cx, year);
  renderWells(wellsLegacyF, layers.wellsLegacy, cx, year);
  const note = document.getElementById('well-note');
  const matched = [...wellsWqpF, ...wellsDecF, ...wellsLegacyF].filter(f => (!activeSampleTypes.size || activeSampleTypes.has(f.properties.sample_type)) && wellPassesFilter(f.properties, cx, year)).length;
  const total = wellsWqpF.length + wellsDecF.length + wellsLegacyF.length;
  if (!cx && year == null) {
    note.innerHTML = 'Shows wells where the selected contaminant was <em>detected</em>. Turn a well layer on above to see results.';
  } else {
    const chemTxt = cx ? `<b>${cx}</b>` : 'a tracked contaminant';
    const yearTxt = year != null ? ` by <b>${year}</b> or earlier` : '';
    note.innerHTML = `Showing wells where ${chemTxt} was detected${yearTxt} (${matched} of ${total}). Turn a well layer on above to see them.`;
  }
  updateChemTrend();
}

// ── CHEMICAL SPREAD PANEL ────────────────────────────────────────────────────
// A floating chart that appears when a chemical is selected (and a well layer is on),
// showing the cumulative number of wells that had detected that chemical by each year
// — the same count the year slider paints on the map, as one spread curve. It updates
// when the chemical or the visible layers change, and hides when neither applies.
let chemTrendEl = null;
const chemTrendControl = L.control({ position: 'bottomleft' });
chemTrendControl.onAdd = function () {
  chemTrendEl = L.DomUtil.create('div', 'chem-trend-panel');
  chemTrendEl.style.display = 'none';
  L.DomEvent.disableClickPropagation(chemTrendEl);
  L.DomEvent.disableScrollPropagation(chemTrendEl);
  return chemTrendEl;
};
function onWellSources() {
  const s = [];
  if (map.hasLayer(layers.wellsWqp)) s.push(...wellsWqpF);
  if (map.hasLayer(layers.wellsDec)) s.push(...wellsDecF);
  if (map.hasLayer(layers.wellsLegacy)) s.push(...wellsLegacyF);
  return activeSampleTypes.size ? s.filter(f => activeSampleTypes.has(f.properties.sample_type)) : s;
}
function chemTrendSVG(chem, years, counts, total) {
  const W = 214, H = 116, x0 = 30, x1 = W - 8, yT = 24, yB = H - 18;
  const y0 = years[0], y1 = years[years.length - 1];
  const sx = yr => y1 === y0 ? (x0 + x1) / 2 : x0 + (yr - y0) / (y1 - y0) * (x1 - x0);
  const cmax = Math.max(...counts, 1);
  const sy = c => yB - c / cmax * (yB - yT);
  const linePts = counts.map((c, i) => `${sx(years[i]).toFixed(1)},${sy(c).toFixed(1)}`).join(' ');
  const area = `${x0},${yB} ${linePts} ${x1},${yB}`;
  return `<div class="ctp-title">Wells detecting <b>${chem}</b></div>`
    + `<svg width="${W}" height="${H}" viewBox="0 0 ${W} ${H}">`
    + `<polygon points="${area}" fill="#d1332e30"/>`
    + `<polyline points="${linePts}" fill="none" stroke="#d1332e" stroke-width="1.8"/>`
    + `<line x1="${x0}" y1="${yB}" x2="${x1}" y2="${yB}" stroke="#ffffff22" stroke-width="0.5"/>`
    + `<text x="${x0 - 3}" y="${yB + 3}" text-anchor="end" font-size="8" fill="#9aa4b2">0</text>`
    + `<text x="${x0 - 3}" y="${(sy(cmax) + 3).toFixed(1)}" text-anchor="end" font-size="8" fill="#9aa4b2">${cmax}</text>`
    + `<text x="${x0}" y="${H - 5}" font-size="8" fill="#9aa4b2">${y0}</text>`
    + `<text x="${x1}" y="${H - 5}" text-anchor="end" font-size="8" fill="#9aa4b2">${y1}</text>`
    + `</svg><div class="ctp-sub">cumulative · ${total} well${total === 1 ? '' : 's'} total</div><div class="ctp-caveat">Cumulative monitoring history &mdash; not contemporaneous plume extent. Additional points over time may reflect new sampling locations or newly available records as well as environmental change.</div>`;
}
function updateChemTrend() {
  const _b = document.getElementById('chem-trend'); if (_b) { _b.style.display = 'none'; _b.innerHTML = ''; } return;  // WITHDRAWN pending validation
  if (!chemTrendEl) return;
  const cx = (document.getElementById('well-select') || {}).value || '';
  const feats = cx ? onWellSources().filter(f => f.properties.chems_years && f.properties.chems_years[cx]) : [];
  if (!cx || !feats.length) { chemTrendEl.style.display = 'none'; return; }
  const allYrs = feats.flatMap(f => f.properties.chems_years[cx]);
  const y0 = Math.min(...allYrs), y1 = Math.max(...allYrs);
  const years = []; for (let y = y0; y <= y1; y++) years.push(y);
  const counts = years.map(y => feats.filter(f => f.properties.chems_years[cx].some(d => d <= y)).length);
  chemTrendEl.innerHTML = chemTrendSVG(cx, years, counts, feats.length);
  chemTrendEl.style.display = 'block';
}
chemTrendControl.addTo(map);

// ── S-AREA: TOC INTENSITY OVER TIME ──────────────────────────────────────────
// S-Area's wells report Total Organic Concentration (a single aggregate number),
// not named chemicals, so they don't fit the chemical dropdown above. This is a
// self-contained view: picking a year colors each S-Area well by the latest TOC
// reading known at or before that year, on its own layer (independent of the
// wellsDec toggle/filter above, so the two features never conflict).
const TOC_BINS = [
  { max: 1,     color: '#2ecc71', label: '< 1' },
  { max: 10,    color: '#a8d84a', label: '1–10' },
  { max: 100,   color: '#f0d020', label: '10–100' },
  { max: 1000,  color: '#e08a1e', label: '100–1,000' },
  { max: 10000, color: '#c0392b', label: '1,000–10,000' },
  { max: Infinity, color: '#6a1010', label: '> 10,000' },
];
function tocColor(v) { return (TOC_BINS.find(b => v < b.max) || TOC_BINS[TOC_BINS.length-1]).color; }
function latestTocByYear(series, year) {
  const yrs = Object.keys(series).map(Number).filter(y => y <= year);
  return yrs.length ? series[Math.max(...yrs)] : null;
}
function populateSAreaTocYearDropdown() {
  const sel = document.getElementById('sarea-toc-year-select');
  const years = wellsDecF.flatMap(f => Object.keys(f.properties.toc_series || {}).map(Number));
  if (!years.length) return;
  const lo = Math.min(...years), hi = Math.max(...years);
  for (let y = hi; y >= lo; y--) {
    const o = document.createElement('option'); o.value = y; o.textContent = y;
    sel.appendChild(o);
  }
  const leg = document.getElementById('sarea-toc-legend');
  leg.innerHTML = TOC_BINS.map(b => `<div class="wsl">${dropletSVG(18, b.color, WELL_OUTLINE)}<span>${b.label}</span></div>`).join('')
    + `<div class="wsl" style="align-self:center"><span>µg/L</span></div>`;
  sel.addEventListener('change', () => renderSAreaTocYear(sel.value ? parseInt(sel.value, 10) : null));
}
function renderSAreaTocYear(year) {
  layers.sareaToc.clearLayers();
  if (year == null) { map.removeLayer(layers.sareaToc); return; }
  wellsDecF.forEach(f => {
    const p = f.properties;
    const series = p.toc_series;
    if (!series) return;
    const v = latestTocByYear(series, year);
    if (v == null) return;
    const [lon, lat] = f.geometry.coordinates;
    const th = 24;   // fixed-size droplet; color carries the TOC intensity, not size
    L.marker([lat, lon], { pane: 'sareaTocPane', icon: L.divIcon({ className: 'well-droplet', html: dropletSVG(th, tocColor(v), WELL_OUTLINE), iconSize: [th*0.72, th], iconAnchor: [th*0.36, th/2] }) })
      .bindPopup(`<div class="popup-inner"><div class="popup-name">${p.well_id}</div><div class="popup-addr">${p.site}</div>
        <div class="popup-field"><div class="popup-field-lbl">TOC as of ${year}</div><div class="popup-field-val">${v.toLocaleString()} µg/L</div></div></div>`, { maxWidth: 260 })
      .addTo(layers.sareaToc);
  });
  if (!map.hasLayer(layers.sareaToc)) layers.sareaToc.addTo(map);
}

loadAll().catch(err => {
  console.error('Failed to load data:', err);
  document.getElementById('sidebar-body').innerHTML =
    '<p style="color:#c0392b;font-family:monospace;font-size:11px;padding:16px">Error loading data files.<br>Make sure you are serving this page over HTTP (not file://).</p>';
});

// ── LAYER TOGGLES ────────────────────────────────────────────────────────────
document.querySelectorAll('.toggle-check').forEach(cb => {
  cb.addEventListener('change', () => {
    const key = cb.dataset.layer;
    const toggle = cb.closest('.layer-toggle');
    if (cb.checked) {
      map.addLayer(layers[key]);
      toggle.classList.add('active');
    } else {
      map.removeLayer(layers[key]);
      toggle.classList.remove('active');
    }
    if (key === 'wellsWqp' || key === 'wellsDec' || key === 'wellsLegacy') updateChemTrend();
    if (key === 'roads' && cb.checked && window.__updateRoadLabels) window.__updateRoadLabels();
    // polygon layers reveal their legend automatically while toggled on
    if (key === 'tracts' || key === 'iz') {
      const lg = document.getElementById('legend-' + key);
      if (lg) lg.style.display = cb.checked ? 'block' : 'none';
    }
  });
});

// The hazard-site markers render on a canvas pane (z450) that sits above the tract/impact-zone
// polygons (SVG, z400), so the canvas swallows clicks before they reach those polygons. Restore
// polygon clicks with a map-level hit test: point markers still fire their own popups (guarded by
// popupopen so we don't double-fire), and clicks on open ground fall through to here.
function pointInRing(pt, ring) {
  let inside = false;
  for (let i = 0, j = ring.length - 1; i < ring.length; j = i++) {
    const xi = ring[i][0], yi = ring[i][1], xj = ring[j][0], yj = ring[j][1];
    if (((yi > pt[1]) !== (yj > pt[1])) && (pt[0] < (xj - xi) * (pt[1] - yi) / (yj - yi) + xi)) inside = !inside;
  }
  return inside;
}
function pointInFeature(latlng, feature) {
  const pt = [latlng.lng, latlng.lat], g = feature.geometry;
  const polys = g.type === 'Polygon' ? [g.coordinates] : g.type === 'MultiPolygon' ? g.coordinates : [];
  return polys.some(poly => pointInRing(pt, poly[0]));
}
let lastPopupOpen = 0;
map.on('popupopen', () => { lastPopupOpen = Date.now(); });
map.on('click', e => {
  if (!map.hasLayer(layers.tracts) && !map.hasLayer(layers.iz)) return;
  setTimeout(() => {
    if (Date.now() - lastPopupOpen < 80) return;   // a marker popup already answered this click
    for (const key of ['tracts', 'iz']) {
      if (!map.hasLayer(layers[key])) continue;
      const gj = layers[key].getLayers()[0];
      if (!gj) continue;
      let hit = null;
      gj.eachLayer(l => { if (!hit && l.feature && pointInFeature(e.latlng, l.feature)) hit = l; });
      if (hit) { hit.openPopup(e.latlng); return; }
    }
  }, 20);
});

// ── accordion sections (Monitoring Wells tab): header toggles the body; ⓘ toggles help ──
document.querySelectorAll('.acc-head').forEach(h => {
  h.addEventListener('click', e => {
    if (e.target.closest('.acc-info')) return;
    h.closest('.acc').toggleAttribute('data-open');
  });
});
document.querySelectorAll('.acc-info').forEach(b => {
  b.addEventListener('click', e => {
    e.stopPropagation();
    const help = b.closest('.acc').querySelector('.acc-help');
    if (help) help.classList.toggle('show');
  });
});

// ── CANCER SIR SELECTOR ──────────────────────────────────────────────────────
document.querySelectorAll('input[name="cancer"]').forEach(radio => {
  radio.addEventListener('change', () => {
    document.querySelectorAll('.cancer-opt').forEach(o => o.classList.remove('active'));
    radio.closest('.cancer-opt').classList.add('active');
    if (cancerData) renderCancer(radio.value);
  });
});

// (Radiation-tab selectors are wired in buildRadSelectors after radionuclides.json loads)

// ── FOLDER-TAB RAIL ──────────────────────────────────────────────────────────
// Each tab on the left rail slides out its own panel over the map; one open at a time.
// Clicking the active tab (or ✕ / Esc) closes it back to the full map. Purely a display
// switch — every control keeps working identically regardless of which tab is shown.
(function () {
  const panel = document.getElementById('panel');
  const dock = document.getElementById('dock');
  const titlecard = document.getElementById('titlecard');
  const railTabs = document.querySelectorAll('.rail-tab');
  const mqMobile = window.matchMedia('(max-width: 780px)');
  let activeTab = null;

  // keep the rail/panel clear of the (variable-height) title card on desktop
  function positionDock() {
    if (!dock) return;
    if (titlecard && !mqMobile.matches)
      dock.style.top = (titlecard.offsetTop + titlecard.offsetHeight + 12) + 'px';
    else dock.style.top = '';
  }
  window.addEventListener('resize', positionDock);

  const backdrop = document.getElementById('sheet-backdrop');
  function openTab(id) {
    activeTab = id;
    railTabs.forEach(b => {
      const on = b.dataset.tab === id;
      b.classList.toggle('active', on);
      b.setAttribute('aria-selected', on ? 'true' : 'false');
    });
    document.querySelectorAll('.tab-panel').forEach(p =>
      p.classList.toggle('active', p.dataset.tabPanel === id));
    panel.classList.add('open');
    if (backdrop && mqMobile.matches) backdrop.classList.add('visible');   // dim map behind bottom sheet
    const body = document.getElementById('sidebar-body');
    if (body) body.scrollTop = 0;
  }
  function closePanel() {
    activeTab = null;
    panel.classList.remove('open');
    if (backdrop) backdrop.classList.remove('visible');
    railTabs.forEach(b => { b.classList.remove('active'); b.setAttribute('aria-selected', 'false'); });
  }
  railTabs.forEach(btn => btn.addEventListener('click', () => {
    if (activeTab === btn.dataset.tab) closePanel(); else openTab(btn.dataset.tab);
  }));
  const closeBtn = document.getElementById('panel-close');
  if (closeBtn) closeBtn.addEventListener('click', closePanel);
  document.addEventListener('keydown', e => { if (e.key === 'Escape' && activeTab) closePanel(); });

  positionDock();
  // start with no panel open — a clean map; the rail invites the first click
  // Leaflet sized itself before the layout fully settled — nudge it to repaint tiles full-bleed
  setTimeout(() => window.dispatchEvent(new Event('resize')), 250);
  window.__twOpenTab = openTab;
  window.__twClosePanel = closePanel;
})();


// START HERE panel: the three front-door actions (URGENT_TODO item 8).
document.querySelectorAll('.sh-btn').forEach(btn => btn.addEventListener('click', () => {
  const go = btn.dataset.go;
  if (go === 'search') {
    const si = document.getElementById('search');
    if (si) { si.focus(); si.select(); }
    return;
  }
  const tab = document.querySelector('.tab-btn[data-tab="' + go + '"]');
  if (tab) tab.click();
  if (go === 'chemicals') {
    // open Selected high detections so the citations are the first thing seen
    const panel = document.querySelector('.tab-panel[data-tab-panel="chemicals"]');
    const acc = panel && panel.querySelector('.acc');
    if (acc) acc.setAttribute('data-open', '');
    if (acc) acc.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
  }
}));

// ── ADDRESS LOCATOR ──────────────────────────────────────────────────────────
// Reports straight-line distance from a geocoded address to (a) the nearest documented
// hazard site and (b) the nearest sampling point where a contaminant was DETECTED.
//
// Design constraint that governs everything here: THE OUTPUT MUST NOT BE READABLE AS A
// SAFETY VERDICT. Hence — distances are rounded hard (never "1,247 m"), there is no
// red/green styling, and the three limits below are rendered WITH every result rather
// than tucked into a collapsed methodology note:
//   1. distance is not exposure (groundwater moves directionally, not radially)
//   2. a LARGE distance may mean nobody sampled nearby, not that nothing is there
//   3. site points are centroids; large sites extend far beyond them
const AD_BBOX = { latMin: 42.95, latMax: 43.45, lonMin: -79.20, lonMax: -78.45 };  // Niagara Co. + margin

function adHaversine(lat1, lon1, lat2, lon2) {
  const R = 6371000, t = Math.PI / 180;
  const dLat = (lat2 - lat1) * t, dLon = (lon2 - lon1) * t;
  const a = Math.sin(dLat / 2) ** 2 + Math.cos(lat1 * t) * Math.cos(lat2 * t) * Math.sin(dLon / 2) ** 2;
  return 2 * R * Math.asin(Math.sqrt(a));
}
// Round hard. Precision here would imply an accuracy the inputs cannot support.
function adDist(m) {
  const mi = m / 1609.34;
  if (m < 400) return 'under a quarter mile';
  if (mi < 1) return 'about ' + (Math.round(mi * 10) / 10).toFixed(1) + ' miles (' + (Math.round(m / 100) * 100) + ' m)';
  return 'about ' + (Math.round(mi * 10) / 10).toFixed(1) + ' miles (' + (Math.round(m / 100) / 10).toFixed(1) + ' km)';
}
// Acreage -> radius of a circle of equal area. Used ONLY to decide whether the address may
// fall inside a site's footprint. We hold a centroid and an acreage, not a polygon, so we
// never publish "distance to boundary" as though it were measured.
function adEquivRadius(acres) {
  if (!acres || acres <= 0) return null;
  return Math.sqrt(acres * 4046.86 / Math.PI);
}
function adGeocode(addr) {
  return new Promise(resolve => {
    const cb = '__adg' + Math.random().toString(36).slice(2);
    let done = false;
    const finish = v => { if (!done) { done = true; resolve(v); cleanup(); } };
    window[cb] = d => finish(d);
    const s = document.createElement('script');
    s.src = 'https://geocoding.geo.census.gov/geocoder/locations/onelineaddress?address='
      + encodeURIComponent(addr) + '&benchmark=Public_AR_Current&format=jsonp&callback=' + cb;
    s.onerror = () => finish(null);
    function cleanup() { try { document.head.removeChild(s); delete window[cb]; } catch (e) {} }
    document.head.appendChild(s);
    setTimeout(() => finish(null), 10000);
  });
}
function adStatus(html, cls) {
  const el = document.getElementById('ad-status');
  el.className = 'ad-status' + (cls ? ' ' + cls : '');
  el.innerHTML = html;
  el.style.display = 'block';
}
async function adRun() {
  const q = document.getElementById('ad-input').value.trim();
  const res = document.getElementById('ad-results');
  res.style.display = 'none'; res.innerHTML = '';
  if (!q) { adStatus('Enter an address to look up.', 'warn'); return; }
  adStatus('Looking up address…');

  const d = await adGeocode(q);
  const matches = (d && d.result && d.result.addressMatches) || [];
  if (!matches.length) {
    adStatus('<b>No match.</b> The US Census geocoder could not find that address. Try including the street number, city and ZIP — e.g. <i>2001 Main St, Niagara Falls, NY 14305</i>. Some rural and newly-built addresses are not in the Census address file at all; that is a limitation of the geocoder, not a statement about the location.', 'warn');
    return;
  }
  const m = matches[0];
  const lat = m.coordinates.y, lon = m.coordinates.x;

  if (lat < AD_BBOX.latMin || lat > AD_BBOX.latMax || lon < AD_BBOX.lonMin || lon > AD_BBOX.lonMax) {
    adStatus('<b>Outside the mapped area.</b> That address geocoded to ' + lat.toFixed(3) + ', ' + lon.toFixed(3)
      + ', which is outside Niagara County. This map only documents Niagara County, so a distance from here would be meaningless.', 'warn');
    return;
  }

  // nearest documented hazard site (by centroid)
  let bestSite = null;
  // ...and, separately, EVERY site whose footprint may contain this address. These are not the
  // same question: LOOW is 7,500 acres (~3.1 km equivalent radius), so an address can sit inside
  // its footprint while some small site 500 m away is "nearest by centroid". Checking only the
  // nearest site would silently hide the one that actually matters.
  const containing = [];
  allSiteFeatures.forEach(f => {
    const c = f.geometry.coordinates;
    const dist = adHaversine(lat, lon, c[1], c[0]);
    if (!bestSite || dist < bestSite.dist) bestSite = { dist, p: f.properties };
    const r = adEquivRadius(f.properties.acres);
    if (r && dist < r) containing.push({ dist, r, p: f.properties });
  });
  containing.sort((a, b) => b.p.acres - a.p.acres);
  // nearest sampling point WITH a detection
  let bestPt = null;
  [...wellsWqpF, ...wellsDecF, ...wellsLegacyF].forEach(f => {
    const p = f.properties;
    if (!(p.n_found > 0)) return;
    const c = f.geometry.coordinates;
    const dist = adHaversine(lat, lon, c[1], c[0]);
    if (!bestPt || dist < bestPt.dist) bestPt = { dist, p };
  });

  adStatus('Matched to <b>' + m.matchedAddress + '</b><br>'
    + '<span class="ad-quality">The Census geocoder matches to a <b>street segment</b>, not a rooftop — the located point is typically within about 100 m of the actual parcel, and can be further on long or rural blocks. Everything below inherits that.</span>');

  let html = '';

  // ---- footprint containment first: more consequential than nearest-centroid ----
  if (containing.length) {
    html += '<div class="ad-card ad-inside"><div class="ad-card-h">Your address may fall within a mapped site footprint</div>'
      + '<div class="ad-note" style="border:0;padding:0;margin:0 0 7px">These sites are large enough that their boundaries may extend past your location, even though the distance figures below are measured to their centre points. We hold each site’s <b>acreage and centre point, not its surveyed boundary</b>, so this is an indication to check the site record — not a determination that you are inside it.</div>';
    containing.forEach(s => {
      html += '<div class="ad-inside-row"><b>' + (s.p.site_name || '—') + '</b> — about '
        + Math.round(s.p.acres).toLocaleString() + ' acres; its centre point is ' + adDist(s.dist)
        + ' away' + (s.p.designation ? ' · ' + s.p.designation : '') + '</div>';
    });
    html += '</div>';
  }

  // ---- hazard site ----
  if (bestSite) {
    const p = bestSite.p, r = adEquivRadius(p.acres);
    const inside = r && bestSite.dist < r;
    html += '<div class="ad-card"><div class="ad-card-h">Nearest documented hazard site</div>'
      + '<div class="ad-val">' + adDist(bestSite.dist) + '</div>'
      + '<div class="ad-name">' + (p.site_name || '—') + '</div>'
      + '<div class="ad-meta">' + (p.designation || '') + (p.city ? ' · ' + p.city : '') + '</div>';
    if (p.acres > 0) {
      html += '<div class="ad-note">This site covers about <b>' + Math.round(p.acres).toLocaleString() + ' acres</b>. '
        + 'The distance above is measured to the site’s <b>mapped point</b>, not its boundary — the site itself extends beyond that point in every direction.';
      if (inside) {
        html += ' <b>Given its size, your address may fall within this site’s mapped footprint.</b>';
      }
      html += '</div>';
    } else {
      html += '<div class="ad-note">No acreage is recorded for this site, so we cannot say how far its boundary extends from the mapped point.</div>';
    }
    html += '</div>';
  }

  // ---- sampled point with a detection ----
  if (bestPt) {
    const p = bestPt.p;
    const chems = (p.chems || []).slice(0, 4).join(', ');
    html += '<div class="ad-card"><div class="ad-card-h">Nearest sampling point with a detection</div>'
      + '<div class="ad-val">' + adDist(bestPt.dist) + '</div>'
      + '<div class="ad-name">' + (p.well_id || '—') + (p.site ? ' — ' + p.site : '') + '</div>'
      + '<div class="ad-meta">' + (p.n_found || 0) + ' contaminant' + (p.n_found === 1 ? '' : 's') + ' detected'
      + (chems ? ' · ' + chems + ((p.chems || []).length > 4 ? '…' : '') : '')
      + (p.latest_detect || p.latest_year ? ' · last detection ' + (p.latest_detect || p.latest_year) : '') + '</div>';
    if (p.coord_precision) {
      html += '<div class="ad-note">⚑ This point’s own position is approximate: <i>' + p.coord_precision + '</i></div>';
    }
    html += '</div>';
  }

  // ---- limits, rendered WITH the result, never collapsed ----
  html += '<div class="ad-limits"><div class="ad-limits-h">How to read these numbers</div><ul>'
    + '<li><b>Distance is not exposure.</b> Contamination travels through groundwater in a <b>direction</b>, following the water table — not outward in a circle. A site further away but upgradient of you can matter more than a closer one that drains elsewhere. Nothing here models that.</li>'
    + '<li><b>A large distance is not reassurance.</b> It may simply mean nobody has sampled near you. Absence of a record is not absence of contamination.</li>'
    + '<li><b>These are straight-line distances</b> between points on a map, ignoring roads, barriers, depth and geology.</li>'
    + '<li><b>This is orientation, not a risk assessment.</b> For questions about your own water, soil or health, contact the <a href="https://www.health.ny.gov/environmental/" target="_blank" rel="noopener">NYS Department of Health</a> or <a href="https://dec.ny.gov/environmental-protection/site-cleanup" target="_blank" rel="noopener">NYSDEC</a>.</li>'
    + '</ul></div>';

  html += '<button class="ad-show" id="ad-show">Show this location on the map</button>';

  res.innerHTML = html;
  res.style.display = 'block';
  const btn = document.getElementById('ad-show');
  if (btn) btn.addEventListener('click', () => {
    if (window.__adMarker) map.removeLayer(window.__adMarker);
    window.__adMarker = L.circleMarker([lat, lon], {
      pane: 'wellsPane', radius: 9, color: '#ffffff', weight: 2.5, fillColor: '#2f6fd0', fillOpacity: 0.85
    }).bindPopup('<div class="popup-inner"><div class="popup-name">Looked-up address</div>'
      + '<div class="popup-addr">' + m.matchedAddress + '</div>'
      + '<div class="popup-loc">⚑ Geocoded to a street segment — approximate.</div></div>').addTo(map);
    map.flyTo([lat, lon], 14, { duration: 1.1 });
    window.__adMarker.openPopup();
  });
}


document.addEventListener('DOMContentLoaded', () => {
  const go = document.getElementById('ad-go');
  const inp = document.getElementById('ad-input');
  if (go) go.addEventListener('click', adRun);
  if (inp) inp.addEventListener('keydown', e => { if (e.key === 'Enter') adRun(); });
});

// ── RECENCY / "LAST SAMPLED" ─────────────────────────────────────────────────
// Temporal transparency. Sampling here spans 1948–2025, so a reader who cannot see WHEN a point
// was last visited may read a 1970s reading and a 2024 reading as equivalent statements about
// today. Recency is encoded as OPACITY (older = more faded) and is filterable.
//
// Opacity was chosen deliberately: fill colour already means "contamination", size means "number
// of chemicals detected", and ring colour means "sample type". Age needed a channel of its own.
// The legend states outright that fading indicates AGE, not severity — a faded point is not a
// cleaner point, it is an older observation.
const RECENCY_BANDS = [
  { key: '2020s',   label: '2020 or later', test: y => y >= 2020,          opacity: 1.00, swatch: '#b81d24' },
  { key: '2010s',   label: '2010–2019',     test: y => y >= 2010 && y <= 2019, opacity: 0.78, swatch: '#a3272d' },
  { key: '2000s',   label: '2000–2009',     test: y => y >= 2000 && y <= 2009, opacity: 0.58, swatch: '#8a3036' },
  { key: 'pre2000', label: 'Before 2000',   test: y => y < 2000,           opacity: 0.40, swatch: '#6d383c' },
  { key: 'unknown', label: 'Date not recorded', test: y => !y,             opacity: 0.40, swatch: '#4a4a52' },
];
let activeRecency = new Set();          // empty = show all (same convention as the sample-type filter)

function recencyBand(y) {
  return RECENCY_BANDS.find(b => b.test(y)) || RECENCY_BANDS[RECENCY_BANDS.length - 1];
}
function recencyOpacity(y) { return recencyBand(y).opacity; }
function recencyPasses(y) {
  if (!activeRecency.size) return true;
  return activeRecency.has(recencyBand(y).key);
}
function recencyLabel(y) {
  return y ? String(y) : 'date not recorded';
}

function buildRecencyFilter() {
  const box = document.getElementById('recency-filter');
  if (!box || !STATS || !STATS.recency) return;
  const r = STATS.recency;
  const counts = {
    '2020s': r.band_2020_plus, '2010s': r.band_2010_2019,
    '2000s': r.band_2000_2009, 'pre2000': r.band_pre_2000, 'unknown': r.points_undated,
  };
  box.innerHTML = RECENCY_BANDS.map(b =>
    '<label class="rc-opt"><input type="checkbox" class="rc-check" value="' + b.key + '">'
    + '<span class="rc-swatch" style="background:' + b.swatch + ';opacity:' + b.opacity + '"></span>'
    + '<span class="rc-name">' + b.label + '</span>'
    + '<span class="rc-count">' + (counts[b.key] || 0) + '</span></label>').join('');
  box.querySelectorAll('.rc-check').forEach(cb => cb.addEventListener('change', () => {
    if (cb.checked) activeRecency.add(cb.value); else activeRecency.delete(cb.value);
    box.querySelectorAll('.rc-opt').forEach(o => o.classList.toggle('active', o.querySelector('input').checked));
    refreshWellLayers();
  }));
  const note = document.getElementById('recency-note');
  if (note) {
    note.innerHTML = 'Monitoring points span <b>' + r.earliest + '&ndash;' + r.latest + '</b>. '
      + '<b>' + r.since_2020 + '</b> of ' + r.points_total + ' were last sampled in 2020 or later; '
      + '<b>' + r.band_pre_2000 + '</b> were last sampled before 2000. Fading shows <b>age, not severity</b> '
      + '&mdash; an older point is an older observation, not a cleaner one.';
  }
}
// Re-render whichever well layers are currently on, so the filter/opacity apply everywhere.
function refreshWellLayers() {
  const cx = (document.getElementById('well-select') || {}).value || '';
  const yr = currentWellYear();
  renderWells(wellsWqpF, layers.wellsWqp, cx, yr);
  renderWells(wellsDecF, layers.wellsDec, cx, yr);
  renderWells(wellsLegacyF, layers.wellsLegacy, cx, yr);
  if (typeof renderSoilRad === 'function' && activeSoilSites && activeSoilSites.size) renderSoilRad();
}

// ── SEARCH ───────────────────────────────────────────────────────────────────
const searchInput = document.getElementById('search');
const searchResults = document.getElementById('search-results');

// Unified search index: hazard sites + wells (WQP/DEC/legacy) + soil rad zones + Love Canal
// piezometers/pumps. Lets anyone look a specific sample point up by its ID (e.g. C4R-MW-04,
// TP-14, SS-01, MW-88-8A) for independent verification.
let SEARCH_INDEX = [];
function buildSearchIndex() {
  SEARCH_INDEX = [];
  const push = (o) => { if (o.id) SEARCH_INDEX.push(o); };
  allSiteFeatures.forEach(f => { const p = f.properties, c = f.geometry.coordinates;
    push({ kind:'site', id:p.site_name||'', label:p.site_name||'', sub:`${p.designation||''}${p.city?' · '+p.city:''}`, lat:c[1], lon:c[0], feature:f }); });
  [[wellsWqpF,'wellsWqp'],[wellsDecF,'wellsDec'],[wellsLegacyF,'wellsLegacy']].forEach(([arr,layer]) =>
    arr.forEach(f => { const p = f.properties, c = f.geometry.coordinates;
      push({ kind:'well', layer, id:p.well_id||p.name||'', label:p.well_id||p.name||'', sub:`${p.site||p.site_type||'well'}${p.sample_type?' · '+p.sample_type:''}`, lat:c[1], lon:c[0], props:p }); }));
  soilRadFeatures.forEach(f => { const p = f.properties, c = f.geometry.coordinates;
    push({ kind:'soil', id:p.zone_id||'', label:p.zone_id||'', sub:`${p.site||''} · radioactive soil zone`, lat:c[1], lon:c[0], props:p }); });
  lcPiezoF.forEach(f => { const p = f.properties, c = f.geometry.coordinates;
    push({ kind:'lc', layer:'lcPiezo', id:p.well_id||'', label:p.well_id||'', sub:'Love Canal · piezometer (water levels)', lat:c[1], lon:c[0], props:p, popupKind:'piezo' }); });
  lcPumpsF.forEach(f => { const p = f.properties, c = f.geometry.coordinates;
    push({ kind:'lc', layer:'lcPumps', id:p.well_id||'', label:p.well_id||'', sub:'Love Canal · pump chamber', lat:c[1], lon:c[0], props:p, popupKind:'pump' }); });
  // contaminants: searching one jumps to the Chemicals tab filtered to it
  const chemCounts = {};
  allSiteFeatures.forEach(f => (f.properties.chems || []).forEach(c => { chemCounts[c] = (chemCounts[c] || 0) + 1; }));
  Object.keys(chemCounts).forEach(c =>
    push({ kind:'chem', id:c, label:c, sub:`contaminant · listed at ${chemCounts[c]} site${chemCounts[c] === 1 ? '' : 's'}` }));
}
const BADGE = { well:'WELL', site:'SITE', soil:'SOIL', lc:'LC', chem:'CHEM' };
searchInput.addEventListener('input', () => {
  const q = searchInput.value.trim().toLowerCase();
  searchResults.innerHTML = '';
  if (!q || q.length < 2) { searchResults.style.display = 'none'; return; }
  const scored = [];
  for (const r of SEARCH_INDEX) {
    const id = r.label.toLowerCase(), sub = (r.sub || '').toLowerCase();
    let s = -1;
    if (id === q) s = 0; else if (id.startsWith(q)) s = 1; else if (id.includes(q)) s = 2; else if (sub.includes(q)) s = 3;
    if (s >= 0) scored.push([s, r]);
  }
  scored.sort((a, b) => a[0] - b[0]);
  const hits = scored.slice(0, 16).map(x => x[1]);
  if (!hits.length) { searchResults.style.display = 'none'; return; }
  hits.forEach(r => {
    const div = document.createElement('div');
    div.className = 'sr-item';
    div.innerHTML = `<div class="sr-name">${r.label}<span class="sr-badge sr-${r.kind}">${BADGE[r.kind]}</span></div>
      <div class="sr-sub">${r.sub || ''}</div>`;
    div.addEventListener('click', () => selectSearchResult(r));
    searchResults.appendChild(div);
  });
  searchResults.style.display = 'block';
});
function selectSearchResult(r) {
  searchResults.style.display = 'none';
  searchInput.value = r.label;
  // a contaminant isn't a point — open the Chemicals tab and filter the map to it
  if (r.kind === 'chem') {
    if (window.__twOpenTab) window.__twOpenTab('chemicals');
    const cs = document.getElementById('chem-select');
    if (cs && [...cs.options].some(o => o.value === r.id)) { cs.value = r.id; cs.dispatchEvent(new Event('change')); }
    const ws = document.getElementById('well-select');
    if (ws && [...ws.options].some(o => o.value === r.id)) { ws.value = r.id; ws.dispatchEvent(new Event('change')); }
    return;
  }
  // turn the point's layer on so the marker is visible after the popup closes
  if (r.layer) {
    const cb = document.querySelector(`.toggle-check[data-layer="${r.layer}"]`);
    if (cb && !cb.checked) { cb.checked = true; cb.dispatchEvent(new Event('change')); }
  }
  map.flyTo([r.lat, r.lon], r.kind === 'site' ? 15 : 17, { duration: 1.0 });
  if (r.kind === 'site') {
    let opened = false;
    layers.sites.eachLayer(m => { if (m._siteProps && m._siteProps.site_name === r.id) { m.openPopup(); opened = true; } });
    if (!opened && r.feature) L.popup({ maxWidth: 300 }).setLatLng([r.lat, r.lon]).setContent(sitePopup(r.feature.properties)).openOn(map);
    return;
  }
  const html = r.kind === 'well' ? wellPopup(r.props)
             : r.kind === 'soil' ? searchSoilPopup(r.props)
             : searchLcPopup(r);
  L.popup({ maxWidth: 300 }).setLatLng([r.lat, r.lon]).setContent(html).openOn(map);
}
function searchSoilPopup(p) {
  return `<div class="popup-inner"><div class="popup-tags"><span class="popup-tag" style="background:#f5d00022;color:#e0c000;border:1px solid #f5d00055">Radioactive soil zone</span></div>`
    + `<div class="popup-name">${p.zone_id}</div><div class="popup-addr">${p.site||''} · ${p.medium||''}</div>`
    + `<div class="popup-addr" style="margin-top:6px">Gamma-survey readings ⚠ withdrawn pending unit validation.</div>`
    + (p.source ? `<div class="popup-addr" style="margin-top:4px;opacity:.75">Source: ${p.source}</div>` : '') + `</div>`;
}
function searchLcPopup(r) {
  const p = r.props, isPiezo = r.popupKind === 'piezo';
  const col = isPiezo ? '#2f6fd0' : '#e0b93a';
  return `<div class="popup-inner"><div class="popup-tags"><span class="popup-tag" style="background:${col}22;color:${isPiezo?'#7fb2ff':'#e0c000'};border:1px solid ${col}55">${isPiezo?'Love Canal piezometer':'Love Canal pump chamber'}</span></div>`
    + `<div class="popup-name">${p.well_id}</div>`
    + `<div class="popup-addr" style="margin-top:4px">${isPiezo ? (p.n_readings ? p.n_readings+' water-level readings' : 'Water-level piezometer') : 'Leachate-containment infrastructure'}</div></div>`;
}

document.addEventListener('click', e => {
  if (!e.target.closest('#search-wrap')) searchResults.style.display = 'none';
});

// ── SHARE + share-click tracking ─────────────────────────────────────────────
// Cloudflare Web Analytics has no custom-event API, so a share click is recorded
// as a short-lived "virtual pageview" (?share=<network>) the beacon picks up.
(function () {
  function trackShare(net) {
    try {
      const clean = location.pathname + location.search;
      history.pushState(null, '', location.pathname + '?share=' + net);
      history.replaceState(null, '', clean);
    } catch (e) {}
  }
  function share(net, btn) {
    const url = location.href.split('#')[0];
    const u = encodeURIComponent(url), t = encodeURIComponent(document.title);
    if (net === 'copy') {
      const done = () => { btn.classList.add('share-copied'); btn.textContent = '✓';
        setTimeout(() => { btn.classList.remove('share-copied'); btn.textContent = 'Copy'; }, 1200); };
      const fallback = () => { try { const ta = document.createElement('textarea'); ta.value = url;
        ta.style.cssText = 'position:fixed;opacity:0'; document.body.appendChild(ta); ta.select();
        document.execCommand('copy'); document.body.removeChild(ta); done(); } catch (e) {} };
      if (navigator.clipboard) navigator.clipboard.writeText(url).then(done).catch(fallback); else fallback();
    } else if (net === 'email') {
      location.href = 'mailto:?subject=' + t + '&body=' + u;
    } else {
      const targets = {
        x: 'https://twitter.com/intent/tweet?url=' + u + '&text=' + t,
        facebook: 'https://www.facebook.com/sharer/sharer.php?u=' + u,
      };
      window.open(targets[net], '_blank', 'noopener,noreferrer,width=600,height=520');
    }
    trackShare(net);
  }
  document.querySelectorAll('.share-btn').forEach(b =>
    b.addEventListener('click', () => share(b.dataset.share, b)));
})();

// ── MOBILE BOTTOM SHEET ───────────────────────────────────────────────────────
// Sidebar becomes a collapsible bottom sheet on phones: closed on load, reopened
// via the "Layers & Search" button, dismissed via that button, the backdrop, or
// picking a search result. Desktop layout is completely unaffected (CSS-gated).
(function () {
  const mq = window.matchMedia('(max-width: 780px)');
  const backdrop = document.getElementById('sheet-backdrop');
  // On phones the rail is an always-visible bottom nav; tapping a tab raises its panel as a
  // bottom sheet (handled by the rail controller). Here we just let the backdrop dismiss it,
  // and close the sheet when a search result is chosen so the map is visible.
  if (backdrop) backdrop.addEventListener('click', () => { if (window.__twClosePanel) window.__twClosePanel(); });
  const sr = document.getElementById('search-results');
  if (sr) sr.addEventListener('click', e => {
    if (e.target.closest('.sr-item') && mq.matches && window.__twClosePanel) window.__twClosePanel();
  });
})();

// ── keep the mobile dock (rail + sheet) pinned to the VISIBLE viewport bottom ──
// Positions it above the browser toolbar AND above the on-screen keyboard, and — because
// it re-runs on every visual-viewport change — always returns cleanly when the keyboard
// dismisses. Fixes the rail vanishing after using the search box (which opens the keyboard).
(function () {
  const vv = window.visualViewport;
  const dock = document.getElementById('dock');
  if (!vv || !dock) return;
  const mq = window.matchMedia('(max-width: 780px)');
  function place() {
    if (mq.matches) {
      const gap = Math.max(0, Math.round(window.innerHeight - vv.height - vv.offsetTop));
      dock.style.bottom = gap + 'px';
    } else {
      dock.style.bottom = '';
    }
  }
  vv.addEventListener('resize', place);
  vv.addEventListener('scroll', place);
  window.addEventListener('orientationchange', () => setTimeout(place, 200));
  mq.addEventListener('change', place);
  place();
})();
