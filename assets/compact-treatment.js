/* Compact treatment and evidence presentation (matrix-style rebuild, 27 October 2026).
   Presentation only. Existing nodes are moved, never rewritten: clinical text, grades,
   matching, routing, calculators and high-risk status are unchanged. A numerical study
   result appears under an option only through the explicit option mapping in
   assets/compact-evidence-data.js: results that the option's own text already reports and
   attributes to that cited study. Other sources are listed without a result. */
(() => {
  'use strict';
  const DATA = window.CompactEvidenceData || {studies: {}};
  const plain = s => String(s || '').replace(/\s+/g, ' ').trim();
  const make = (tag, cls, text) => { const n = document.createElement(tag); if (cls) n.className = cls; if (text !== undefined) n.textContent = text; return n; };
  let uid = 0, queued = false;
  const nextId = prefix => `${prefix}-${++uid}`;

  /* A small peer toggle that opens a full-width panel below the control row. */
  const SHORT = {'Contraindications & cautions': 'Cautions', 'Evidence & sources': 'Evidence'};
  function peerButton(label, panel, extra, options = {}) {
    const b = make('button', 'ct-peer');
    b.type = 'button';
    const visible = options.visible || label;
    const short = options.short || SHORT[label];
    b.append(make('span', 'ct-peer-label' + (short ? ' ct-long' : ''), visible));
    if (short) b.append(make('span', 'ct-peer-label ct-short', short));
    if (extra) b.append(make('span', 'ct-peer-count', extra));
    if (short || options.visible || extra) b.setAttribute('aria-label', [options.full || label, extra && !options.full ? extra : ''].filter(Boolean).join(', '));
    if (!panel.id) panel.id = nextId('ct-panel');
    b.setAttribute('aria-controls', panel.id);
    const isOpen = () => panel.matches('details') ? panel.open : !panel.hidden;
    const sync = () => b.setAttribute('aria-expanded', String(isOpen()));
    b.addEventListener('click', () => {
      if (panel.matches('details')) panel.open = !panel.open; else panel.hidden = !panel.hidden;
      sync();
    });
    if (panel.matches('details')) panel.addEventListener('toggle', sync);
    sync();
    return b;
  }

  /* ---------- Roadmap treatment options ---------- */
  function optionScope(host, tc) {
    const clone = host.cloneNode(true);
    const marker = tc.dataset.ctKey;
    clone.querySelectorAll('.opt').forEach(opt => { if (!opt.querySelector(`[data-ct-key="${marker}"]`)) opt.remove(); });
    clone.querySelectorAll('.refs,.refchip,.ct-peers,.ct-ev,.ct-ev-note').forEach(n => n.remove());
    return plain(clone.textContent);
  }
  // Stable key for an option: page slug plus a hash of its visible statement.
  const slug = (() => { const parts = location.pathname.split('/').filter(Boolean); const i = parts.indexOf('mh-liver-pathways'); return parts[i + 1] || parts[0] || ''; })();
  function optionLead(host, tc) {
    const clone = host.cloneNode(true);
    clone.querySelectorAll('.ci-unit,.ci-treatment-criteria,.opts,.recmeta,.ct-peers,.grade,.optn').forEach(n => n.remove());
    return plain(clone.textContent);
  }
  function hash(text) { let h = 5381; for (let i = 0; i < text.length; i++) h = ((h << 5) + h + text.charCodeAt(i)) >>> 0; return h.toString(36); }
  function optionKey(host, tc) { const lead = optionLead(host, tc); return {key: `${slug}:${hash(lead)}`, lead}; }
  function evidenceRows(refs, option, lead, skip = new Set()) {
    const list = make('ul', 'ct-ev');
    // Numbers come only from the explicit option mapping: results this option's own text reports for that study.
    const mapped = option && lead.startsWith(option.g) ? option.rows : [];
    const byStudy = new Map(mapped.map(r => [r.p, r]));
    let tied = 0;
    for (const {key, label, chip} of refs) {
      const study = /^\d{6,9}$/.test(key) ? DATA.studies[key] : null;
      const li = make('li', 'ct-ev-row');
      const head = make('span', 'ct-ev-head');
      const name = make('button', 'ct-ev-label', label);
      name.type = 'button';
      name.title = 'Open this source in the evidence library';
      name.addEventListener('click', () => chip.click());
      head.append(name);
      if (study?.d) head.append(make('span', 'ct-ev-design', study.d));
      if (/^\d{6,9}$/.test(key)) head.append(pmChip(key));
      li.append(head);
      const row = byStudy.get(key);
      if (!row && skip.has(key)) continue;
      if (row) {
        tied++;
        li.classList.add('ct-ev-tied');
        li.append(make('span', 'ct-ev-result', row.r));
        if (row.c) li.append(make('span', 'ct-ev-caution', row.c));
      }
      list.append(li);
    }
    // Rows with a result first, as in the LRT matrix; citation order is otherwise kept.
    [...list.children].filter(li => li.classList.contains('ct-ev-tied')).reverse().forEach(li => list.prepend(li));
    return {list, tied};
  }
  /* Reviewed links to this page's own treatment references (liver-directed reference or systemic matrix).
     Copied verbatim at build time; shown as source-study evidence for the modality or regimen. */
  function pmChip(id) {
    const a = make('a', 'ct-pm', id);
    a.href = `https://pubmed.ncbi.nlm.nih.gov/${id}/`; a.target = '_blank'; a.rel = 'noopener';
    a.setAttribute('aria-label', `PubMed ${id}`);
    return a;
  }
  function referenceGroup(g, chipFor = new Map()) {
    const box = make('section', 'ct-ref ct-ref-' + g.k);
    const head = make('p', 'ct-ref-head');
    head.append(make('span', 'ct-ref-kind', g.k === 'lrt' ? 'Liver-directed therapy evidence' : 'Systemic therapy evidence'));
    const title = make('span', 'ct-ref-title');
    title.append(make('b', '', g.t));
    if (g.s) title.append(' ', make('span', 'ct-ref-sub', g.s));
    if (g.pos) title.append(' ', make('span', 'ct-ref-tier', g.pos));
    head.append(title);
    box.append(head);
    const when = make('p', 'ct-ref-when');
    when.append(make('span', 'ct-ref-label', 'Studied population'), ' ', g.w);
    box.append(when);
    const list = make('ul', 'ct-ev');
    for (const [trial, ids, text, arms, caution] of g.rows) {
      const li = make('li', 'ct-ev-row ct-ev-ref');
      const top = make('span', 'ct-ev-head');
      const chip = ids.map(id => chipFor.get(id)).find(Boolean);
      if (chip) {
        const name = make('button', 'ct-ev-label', trial);
        name.type = 'button'; name.title = 'Open this source in the evidence library';
        name.addEventListener('click', () => chip.click());
        top.append(name);
      } else top.append(make('span', 'ct-ev-trial', trial));
      for (const id of ids) top.append(pmChip(id));
      if (arms) top.append(make('span', 'ct-ev-arms', arms));
      li.append(top, make('span', 'ct-ev-result', text));
      if (caution) li.append(make('span', 'ct-ev-caution', caution));
      list.append(li);
    }
    box.append(list);
    if (g.l) { const lim = make('p', 'ct-ref-limits'); lim.append(make('span', 'ct-ref-label', 'Limits of the evidence'), ' ', g.l); box.append(lim); }
    const open = make('a', 'ct-ref-open', g.k === 'lrt' ? 'Open the liver-directed therapy reference →' : 'Open in the systemic therapy matrix →');
    open.href = g.k === 'lrt' ? '#lrt' : new URL(`../systemic/?tumor=${slug}#${g.card}`, location.href).href;
    box.append(open);
    return box;
  }
  function enhanceOption(tc) {
    if (tc.dataset.ctReady) return;
    const host = tc.parentElement;
    if (!host) return;
    tc.dataset.ctReady = 'true';
    tc.dataset.ctKey = String(++uid);
    const {key, lead} = optionKey(host, tc);
    tc.dataset.ctOption = key;
    tc.classList.add('ct-panels');
    const panels = [...tc.querySelectorAll(':scope>details')];
    const row = make('div', 'ct-peers');
    row.setAttribute('role', 'group');
    row.setAttribute('aria-label', 'Details for this option');
    for (const d of panels) {
      d.classList.add('ct-panel');
      const b = peerButton(plain(d.querySelector('summary')?.textContent), d);
      b.classList.add(d.classList.contains('ci-contraindications') ? 'ct-peer-contra' : 'ct-peer-ind');
      row.append(b);
    }
    // The option's "Explanation and evidence" unit follows its criteria block.
    let unit = null;
    for (let n = tc.nextElementSibling; n; n = n.nextElementSibling) {
      if (n.matches('.ci-unit') && /evidence/i.test(n.querySelector('.ci-label')?.textContent || '')) { unit = n; break; }
      if (n.matches('.ci-treatment-criteria,.opts,.opt')) break;
    }
    const chips = unit ? [...unit.querySelectorAll('.refchip[data-ref]')] : [];
    const seen = new Set(), refs = [];
    for (const chip of chips) {
      if (seen.has(chip.dataset.ref)) continue;
      seen.add(chip.dataset.ref);
      refs.push({key: chip.dataset.ref, label: plain(chip.textContent), chip});
    }
    if (unit || refs.length) {
      const panel = make('details', 'ct-panel ct-evidence');
      panel.append(make('summary', '', 'Evidence & sources'));
      const groups = (DATA.references || {})[key] || [];
      // A source shown with its result in a linked reference group is not listed again without one.
      const inGroups = new Set(groups.flatMap(g => g.rows.flatMap(r => r[1])));
      const chipFor = new Map(refs.map(r => [r.key, r.chip]));
      if (refs.length) {
        const {list} = evidenceRows(refs, (DATA.options || {})[key], lead, inGroups);
        if (list.children.length) panel.append(list);
      }
      for (const group of groups) panel.append(referenceGroup(group, chipFor));
      if (unit) { unit.classList.add('ct-discussion'); panel.append(unit); }
      tc.append(panel);
      const sourceCount = new Set([...refs.map(r => r.key), ...inGroups]).size;
      const b = peerButton('Evidence & sources', panel, sourceCount ? String(sourceCount) : '');
      b.classList.add('ct-peer-ev');
      row.append(b);
    }
    tc.before(row);
  }

  /* ---------- Transplant high-risk study summaries ---------- */
  function enhanceStudy(article) {
    if (article.dataset.ctReady) return;
    const grid = article.querySelector(':scope>.hr-study-grid');
    const results = grid?.querySelector(':scope>.hr-field-results');
    if (!grid || !results) return;
    article.dataset.ctReady = 'true';
    article.classList.add('ct-study');
    const heading = article.querySelector(':scope>.hr-study-heading');
    const pubmed = article.querySelector('.hr-identifiers a[href*="pubmed.ncbi.nlm.nih.gov"]');
    if (heading && pubmed) {
      const id = (pubmed.href.match(/(\d{6,9})/) || [])[1];
      if (id) {
        const a = make('a', 'ct-pm', id);
        a.href = pubmed.href; a.target = '_blank'; a.rel = 'noopener';
        a.setAttribute('aria-label', `PubMed ${id}`);
        heading.append(a);
      }
    }
    // Population and arms stay visible with the result: a number needs its comparison.
    const population = grid.querySelector(':scope>.hr-field-design_population');
    results.classList.add('ct-study-result');
    (heading || grid).after(results);
    if (population) { population.classList.add('ct-study-population'); results.before(population); }
    const row = make('div', 'ct-peers');
    row.setAttribute('role', 'group');
    row.setAttribute('aria-label', 'Study details');
    const holder = make('div', 'ct-study-panels');
    for (const section of [...grid.querySelectorAll(':scope>section')]) {
      section.hidden = true;
      section.classList.add('ct-panel');
      row.append(peerButton(plain(section.querySelector('h6')?.textContent) || 'Details', section));
      holder.append(section);
    }
    const access = make('div', 'ct-panel ct-study-source');
    access.hidden = true;
    for (const n of [...article.querySelectorAll(':scope>.hr-review-depth,:scope>.hr-locator,:scope>.hr-study-access')]) access.append(n);
    if (access.childElementCount) { row.append(peerButton('Source & full-text access', access)); holder.append(access); }
    grid.remove();
    results.after(row, holder);
  }

  /* ---------- Orange protocol cards: one compact control row for their disclosures ---------- */
  function enhanceProtocol(card) {
    if (card.dataset.ctReady) return;
    const panels = [...card.querySelectorAll(':scope>details.hr-criteria,:scope>details.hr-information,:scope>details.hr-rationale,:scope>details.hr-evidence')];
    if (panels.length < 2) return;
    card.dataset.ctReady = 'true';
    const row = make('div', 'ct-peers ct-protocol-peers');
    row.setAttribute('role', 'group');
    row.setAttribute('aria-label', 'Protocol details');
    const holder = make('div', 'ct-protocol-panels');
    panels[0].before(row, holder);
    const CONCISE = {'hr-criteria': 'Criteria & limits', 'hr-information': 'Tests & information', 'hr-rationale': 'Why this position', 'hr-evidence': 'Studies'};
    for (const d of panels) {
      d.classList.add('ct-panel');
      const summary = d.querySelector('summary');
      const count = summary?.querySelector('span');
      const label = plain([...(summary?.childNodes || [])].filter(n => n !== count).map(n => n.textContent).join(' ')) || plain(summary?.textContent);
      const meta = count ? plain(count.textContent) : '';
      const n = (meta.match(/\d+/) || [])[0] || '';
      const concise = CONCISE[[...d.classList].find(c => CONCISE[c])] || label;
      row.append(peerButton(label, d, n, {visible: concise, full: [label, meta].filter(Boolean).join(': ')}));
      // The full requirement/status/count wording stays visible at the top of the panel.
      if (meta) { const m = make('p', 'ct-panel-meta', meta); summary.after(m); }
      holder.append(d);
    }
  }

  /* Reading mode ("Show explanations") also opens the evidence panels it would otherwise hide. */
  document.addEventListener('click', ev => {
    const b = ev.target.closest('[data-context-reading]');
    if (!b) return;
    requestAnimationFrame(() => {
      const on = b.getAttribute('aria-pressed') === 'true';
      document.querySelectorAll('details.ct-evidence').forEach(d => { d.open = on; });
    });
  });
  // Print shows every panel, then restores the previous state.
  let printState = [];
  window.addEventListener('beforeprint', () => {
    printState = [...document.querySelectorAll('.ct-panel')].map(p => [p, p.matches('details') ? p.open : !p.hidden]);
    printState.forEach(([p]) => { if (p.matches('details')) p.open = true; else p.hidden = false; });
  });
  window.addEventListener('afterprint', () => {
    printState.forEach(([p, open]) => { if (p.matches('details')) p.open = open; else p.hidden = !open; });
    printState = [];
  });

  function scan() {
    queued = false;
    document.querySelectorAll('.rec .ci-treatment-criteria:not([data-ct-ready])').forEach(enhanceOption);
    document.querySelectorAll('article.hr-study:not([data-ct-ready])').forEach(enhanceStudy);
    document.querySelectorAll('.hr-protocol:not([data-ct-ready])').forEach(enhanceProtocol);
  }
  const schedule = () => { if (!queued) { queued = true; requestAnimationFrame(scan); } };
  new MutationObserver(records => { if (records.some(r => r.type === 'childList' && r.addedNodes.length)) schedule(); })
    .observe(document.documentElement, {childList: true, subtree: true});
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', scan); else scan();
  window.CompactTreatment = {scan, optionText: tc => optionScope(tc.closest('.ct-panels') ? tc.parentElement : tc.parentElement, tc), optionLead: tc => optionLead(tc.parentElement, tc)};
})();
