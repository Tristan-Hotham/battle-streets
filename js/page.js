/* Waterloo Road and the clock in the streets: every UK street named after a battle, coloured by the battle's date, with a
 * date slider and rings at the median distance of each war's streets from the town centre. Plain OpenFreeMap Positron base
 * map. Dr Tristan Hotham, Independent researcher, 2026. MIT licence. */
(function () {
  'use strict';
  const qs = new URLSearchParams(location.search);
  const STYLE = 'https://tiles.openfreemap.org/styles/positron';
  const esc = s => String(s ?? '').replace(/[&<>"]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
  const norm = s => String(s).normalize('NFD').replace(/[̀-ͯ]/g, '').toLowerCase();
  const small = matchMedia('(max-width:800px)').matches;
  const START = small ? [[-7.4, 50.0], [1.8, 58.8]] : [[-8.2, 49.9], [2.0, 58.9]];
  const STOPS = [[1793, '#2D1E6B'], [1818, '#5B2A86'], [1843, '#8E3A88'], [1868, '#BF4F6E'], [1894, '#DE7445'], [1919, '#E9A33A'], [1945, '#D9C23A']];
  const ycol = ['interpolate', ['linear'], ['get', 'y'], ...STOPS.flat()];
  const FLAGS = ['in the clock', 'older battle (before 1793): named long after the event', 'ambiguous name: often the place, a person or a colour', 'near a place of the same name: probably named after the place'];
  let map = null, D = null, PL = null, year = +(qs.get('year') || 1945), popup = null;

  document.getElementById('theme').addEventListener('click', () => {
    const r = document.documentElement, dark = r.dataset.theme ? r.dataset.theme === 'dark' : matchMedia('(prefers-color-scheme: dark)').matches;
    r.dataset.theme = dark ? 'light' : 'dark';
  });
  const ct = document.getElementById('cartouche');
  const fold = f => ct.classList.toggle('folded', f);
  if (small) fold(true);
  document.getElementById('ctToggle').addEventListener('click', () => fold(!ct.classList.contains('folded')));
  document.getElementById('ctFold').addEventListener('click', () => fold(true));
  const fmtDate = s => { const [y, m, d] = s.split('-').map(Number); return `${d} ${['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'][m - 1]} ${y}`; };

  function showPopup(r, ll) {
    const b = D.battles[r[2]];
    let h = `<b class="t">${esc(r[3])}</b><div class="nt">${esc(r[4] ? r[4] + ', ' : '')}${esc(r[9])}</div><table>`;
    h += `<tr><td>Battle</td><td><b>${esc(b[1])}</b>, ${fmtDate(b[2])}</td></tr><tr><td>War</td><td>${esc(b[3])}</td></tr>`;
    if (b[5]) h += `<tr><td>Note</td><td>${esc(b[5])}</td></tr>`;
    if (r[4] && r[5] !== null) h += `<tr><td>From centre</td><td>${r[5].toLocaleString('en-GB', { maximumFractionDigits: 1 })} km from the centre of ${esc(r[4])}</td></tr>`;
    h += `<tr><td>Status</td><td>${esc(FLAGS[r[6]])}${r[6] === 3 ? ' (' + esc(r[10]) + ')' : ''}</td></tr>`;
    h += `<tr><td>Streets</td><td>${b[6].toLocaleString('en-GB')} in the UK named after ${esc(b[1])}</td></tr></table>`;
    h += `<p class="nt">Street name from OpenStreetMap. The name records the battle, not when the street was built; most were named within a few years of the battle, some long after.${r[8] > 1 ? ' ' + r[8] + ' mapped pieces joined.' : ''}</p>`;
    h += `<div class="lk"><a href="https://www.openstreetmap.org/way/${r[7]}" target="_blank" rel="noopener">OpenStreetMap way ${r[7]}</a></div>`;
    if (popup) popup.remove();
    popup = new maplibregl.Popup({ maxWidth: '330px', offset: 8 }).setLngLat(ll).setHTML(h).addTo(map);
  }

  function apply() {
    const sO = document.getElementById('ckOld').checked, sA = document.getElementById('ckAmb').checked, sC = document.getElementById('ckClock').checked;
    const f = ['all', ['<=', ['get', 'y'], year]];
    const fl = ['any'];
    if (sC) fl.push(['==', ['get', 'f'], 0], ['==', ['get', 'f'], 3]);
    if (sO) fl.push(['==', ['get', 'f'], 1]);
    if (sA) fl.push(['==', ['get', 'f'], 2]);
    f.push(fl);
    ['st', 'stl'].forEach(id => map.setFilter(id, f));
    map.setFilter('rg', ['<=', ['get', 'y'], year]); map.setFilter('rgl', ['<=', ['get', 'y'], year]);
    const vis = (id, v) => map.setLayoutProperty(id, 'visibility', v ? 'visible' : 'none');
    vis('rg', document.getElementById('ckRing').checked); vis('rgl', document.getElementById('ckRing').checked);
    vis('stl', document.getElementById('ckLab').checked);
    document.getElementById('yr').textContent = year >= 1945 ? 'all dates' : 'to ' + year;
    document.getElementById('yrs').value = year;
    const n = D.rows.filter(r => D.battles[r[2]][2].slice(0, 4) <= year && ((sC && (r[6] === 0 || r[6] === 3)) || (sO && r[6] === 1) || (sA && r[6] === 2))).length;
    document.getElementById('cnt').textContent = n.toLocaleString('en-GB') + ' streets';
    const u = new URL(location.href); year >= 1945 ? u.searchParams.delete('year') : u.searchParams.set('year', year); history.replaceState(null, '', u);
  }

  function setupLayers() {
    const before = (map.getStyle().layers.find(l => l.type === 'symbol') || {}).id;
    const feats = D.rows.map((r, i) => ({ type: 'Feature', properties: { i, y: +D.battles[r[2]][2].slice(0, 4), f: r[6], n: r[3] }, geometry: { type: 'Point', coordinates: [r[0], r[1]] } }));
    map.addSource('rg', { type: 'geojson', data: 'data/rings.geojson' });
    map.addLayer({ id: 'rg', type: 'line', source: 'rg', minzoom: 7, paint: { 'line-color': ycol, 'line-width': ['interpolate', ['linear'], ['zoom'], 7, 1.2, 12, 3], 'line-opacity': 0.85,
      'line-dasharray': [3, 1.5] } }, before);
    map.addLayer({ id: 'rgl', type: 'symbol', source: 'rg', minzoom: 10, layout: { 'symbol-placement': 'line', 'text-field': ['concat', ['get', 'era'], ': median ', ['to-string', ['get', 'km']], ' km'], 'text-font': ['Noto Sans Italic'], 'text-size': 11 },
      paint: { 'text-color': '#2B2119', 'text-halo-color': 'rgba(255,255,255,.95)', 'text-halo-width': 1.6 } });
    map.addSource('st', { type: 'geojson', data: { type: 'FeatureCollection', features: feats }, attribution: 'Streets: <a href="https://www.openstreetmap.org/copyright" target="_blank">OpenStreetMap</a> contributors (ODbL)' });
    map.addLayer({ id: 'st', type: 'circle', source: 'st', layout: { 'circle-sort-key': ['case', ['==', ['get', 'f'], 0], 2, ['==', ['get', 'f'], 3], 2, 1] }, paint: {
      'circle-radius': ['interpolate', ['linear'], ['zoom'], 4, ['case', ['any', ['==', ['get', 'f'], 0], ['==', ['get', 'f'], 3]], 3.2, 2.6], 8, 5, 13, 8],
      'circle-color': ['case', ['==', ['get', 'f'], 1], '#A8A29E', ['==', ['get', 'f'], 2], '#D6D3D1', ycol],
      'circle-stroke-color': ['case', ['==', ['get', 'f'], 3], '#2B2119', '#FFFFFF'], 'circle-stroke-width': ['interpolate', ['linear'], ['zoom'], 4, 0.6, 10, 1.5] } });
    map.addLayer({ id: 'stl', type: 'symbol', source: 'st', minzoom: 12,
      layout: { 'text-field': ['get', 'n'], 'text-font': ['Noto Sans Italic'], 'text-size': 12, 'text-offset': [0, 0.9], 'text-anchor': 'top', 'text-optional': true },
      paint: { 'text-color': '#2B2119', 'text-halo-color': 'rgba(255,255,255,0.95)', 'text-halo-width': 1.6 } });
    map.on('click', e => {
      const f = map.queryRenderedFeatures([[e.point.x - 6, e.point.y - 6], [e.point.x + 6, e.point.y + 6]], { layers: ['st'] })[0];
      if (f) showPopup(D.rows[f.properties.i], f.geometry.coordinates);
    });
    map.on('mouseenter', 'st', () => map.getCanvas().style.cursor = 'pointer'); map.on('mouseleave', 'st', () => map.getCanvas().style.cursor = '');
    const lp = document.getElementById('lp'), btn = document.getElementById('lyrBtn');
    btn.addEventListener('click', e => { e.stopPropagation(); const o = lp.classList.toggle('open'); btn.setAttribute('aria-expanded', o); });
    document.addEventListener('click', e => { if (!lp.contains(e.target) && e.target !== btn) { lp.classList.remove('open'); btn.setAttribute('aria-expanded', false); } });
    ['ckClock', 'ckOld', 'ckAmb', 'ckRing', 'ckLab'].forEach(id => document.getElementById(id).addEventListener('change', apply));
    const s = document.getElementById('yrs'); s.addEventListener('input', () => { year = +s.value; apply(); });
    let timer = null; const play = document.getElementById('play');
    play.addEventListener('click', () => { if (timer) { clearInterval(timer); timer = null; play.textContent = '▶'; return; } play.textContent = '❚❚';
      if (year >= 1945) year = 1793; timer = setInterval(() => { year = Math.min(1945, year + 3); apply(); if (year >= 1945) { clearInterval(timer); timer = null; play.textContent = '▶'; } }, 160); });
    document.querySelectorAll('.chip[data-t]').forEach(b => b.addEventListener('click', () => flyTown(b.dataset.t)));
    document.querySelectorAll('a[data-t]').forEach(a => a.addEventListener('click', e => { e.preventDefault(); flyTown(a.dataset.t); document.getElementById('mapWrap').scrollIntoView({ behavior: 'smooth' }); }));
    apply();
  }
  function flyTown(t) {
    const p = PL.places.find(p => p[0] === t); if (!p) return; fold(true);
    map.flyTo({ center: [p[1], p[2]], zoom: t === 'London' ? 9.6 : 11.2, duration: 1300 });
  }

  function setupSearch() {
    const q = document.getElementById('q'), sug = document.getElementById('sug');
    let items = [], k = -1;
    const sts = D.rows.map(r => ({ t: 's', name: r[3], sub: (r[4] || r[9]) + ' · ' + D.battles[r[2]][2].slice(0, 4), lon: r[0], lat: r[1], r }));
    const towns = PL.places.map(p => ({ t: 'p', name: p[0], sub: 'town', lon: p[1], lat: p[2] }));
    const bat = D.battles.filter(b => b[6] > 0).map(b => ({ t: 'b', name: b[1], sub: 'battle, ' + b[2].slice(0, 4) + ' · ' + b[6] + ' streets', b }));
    const show = () => {
      const v = norm(q.value.trim()); sug.innerHTML = ''; k = -1;
      if (v.length < 2) { sug.style.display = 'none'; return; }
      const m = arr => arr.filter(p => norm(p.name).startsWith(v)).concat(arr.filter(p => !norm(p.name).startsWith(v) && v.length > 2 && norm(p.name).includes(v)));
      items = m(towns).slice(0, 4).concat(m(bat).slice(0, 2), m(sts).slice(0, 8));
      items.forEach((p, i) => { const li = document.createElement('li'); li.setAttribute('role', 'option'); li.innerHTML = `${esc(p.name)} <span>${esc(p.sub)}</span>`;
        li.addEventListener('mousedown', e => { e.preventDefault(); pick(i); }); sug.appendChild(li); });
      sug.style.display = items.length ? 'block' : 'none';
    };
    const pick = i => {
      const p = items[i]; if (!p) return; q.value = p.name; sug.style.display = 'none'; fold(true);
      if (p.t === 'b') { const pts = D.rows.filter(r => D.battles[r[2]] === p.b); const b = new maplibregl.LngLatBounds(); pts.forEach(r => b.extend([r[0], r[1]])); map.fitBounds(b, { padding: 60, maxZoom: 11 }); return; }
      map.flyTo({ center: [p.lon, p.lat], zoom: p.t === 's' ? 15 : 12, duration: 1300 });
      if (p.t === 's') map.once('moveend', () => showPopup(p.r, [p.lon, p.lat]));
    };
    q.addEventListener('input', show);
    q.addEventListener('keydown', e => {
      const lis = [...sug.children];
      if (e.key === 'ArrowDown' || e.key === 'ArrowUp') { e.preventDefault(); k = Math.max(0, Math.min(lis.length - 1, k + (e.key === 'ArrowDown' ? 1 : -1))); lis.forEach((l, i) => l.setAttribute('aria-selected', i === k)); }
      else if (e.key === 'Enter') { e.preventDefault(); if (!items.length) show(); pick(k < 0 ? 0 : k); }
      else if (e.key === 'Escape') sug.style.display = 'none';
    });
    q.addEventListener('blur', () => setTimeout(() => sug.style.display = 'none', 150));
  }

  Promise.all([fetch('data/streets.json').then(r => r.json()), fetch('data/places.json').then(r => r.json())]).then(([d, p]) => {
    D = d; PL = p;
    const at = (qs.get('at') || '').split(',').map(Number);
    const mo = at.length === 3 && at.every(isFinite) ? { center: [at[1], at[0]], zoom: at[2] } : { bounds: START, fitBoundsOptions: { padding: 6 } };
    const m0 = new maplibregl.Map(Object.assign({ container: 'map', style: STYLE, attributionControl: { compact: true }, maxZoom: 18 }, mo));
    return new Promise((res, rej) => { m0.once('load', () => res(m0)); m0.once('error', e => { if (!m0.loaded()) rej(e.error || e); }); });
  }).then(m => {
    map = m; window.__map = m;
    m.on('error', e => { const er = e && e.error; if (er && (er.name === 'AbortError' || /abort/i.test(er.message || ''))) return; console.error(er || e); });
    const n = document.getElementById('nojs'); if (n) n.remove();
    m.addControl(new maplibregl.NavigationControl({ showCompass: false }), 'bottom-right');
    const foldAt = () => document.querySelectorAll('.maplibregl-ctrl-attrib.maplibregl-compact').forEach(a => { a.classList.remove('maplibregl-compact-show'); a.removeAttribute('open'); });
    m.once('idle', foldAt); setTimeout(foldAt, 1500);
    setupLayers(); setupSearch();
    document.getElementById('mapWrap').addEventListener('pointerdown', e => { if (e.target.closest && e.target.closest('.cartouche,.ov,.lp,.keys,.tl,.mfs-btn,.maplibregl-ctrl,.maplibregl-popup')) return; fold(true); }, { capture: true, passive: true, once: true });
    if (qs.get('open')) { const r = D.rows.find(r => String(r[7]) === qs.get('open')); if (r) { m.jumpTo({ center: [r[0], r[1]], zoom: 14 }); showPopup(r, [r[0], r[1]]); } }
  }).catch(e => { console.error(e); const n = document.getElementById('nojs'); if (n) n.textContent = 'The map could not load: ' + e.message; });
})();
