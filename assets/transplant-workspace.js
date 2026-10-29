/* Transplant pathways in the cancer roadmap's visual language (28 October 2026). Presentation only.
   - The decision strip shows the pathway's phases and numbered decisions.
   - Each decision is one card: question, context, then the three columns.
   - By default the middle column lists every possible result of the decision the way a roadmap lists
     its options: grouped (continue · clarify · another route · stop · high-risk reviews · reasons to
     reassess), each with its next step and peer panels for its criteria and its evidence, every
     source shown as a matrix-style line. Nothing has to be chosen.
   - "Record findings step by step" in Tools switches to the original finding-by-finding view, whose
     nodes are regrouped (findings → criteria → result → reassess → other results) but not rewritten.
   Clinical text is taken verbatim from the page's own protocol data; routing and wording are unchanged. */
(() => {
  'use strict';
  let data = null;
  try { data = JSON.parse(document.getElementById('protocol-data')?.textContent || 'null'); } catch { data = null; }
  if (!data?.pathway) return;
  document.documentElement.classList.add('tw');
  const make = (tag, cls, text) => { const n = document.createElement(tag); if (cls) n.className = cls; if (text !== undefined) n.textContent = text; return n; };
  let queued = false;

  /* Decision strip: phase labels over numbered decisions, as the roadmap's decision tree orders questions. */
  function phases() {
    const box = document.querySelector('.dw-protocol-decisions');
    const journey = data.journeys?.[data.pathway.slug];
    if (!box || !journey || box.dataset.twReady) return;
    const buttons = [...box.querySelectorAll(':scope>.dw-protocol-topic')];
    if (!buttons.length) return;
    box.dataset.twReady = 'true';
    let group = null, last = null, n = 0;
    for (const b of buttons) {
      const index = journey.findIndex(p => p.steps.includes(b.dataset.step));
      const phase = index < 0 ? last : index;
      if (!group || phase !== last) {
        group = make('div', 'tw-phase');
        const label = make('span', 'tw-phase-label', journey[phase]?.title || '');
        label.setAttribute('aria-hidden', 'true');
        group.append(label, make('div', 'tw-phase-steps'));
        box.append(group);
        last = phase;
      }
      const num = make('span', 'tw-step-num', String(++n));
      num.setAttribute('aria-hidden', 'true');
      b.prepend(num);
      group.lastElementChild.append(b);
    }
    // Numbers only while the whole row fits; otherwise the row keeps its phases and scrolls as before.
    const fit = () => {
      box.classList.remove('tw-tight');
      if (box.scrollWidth > box.clientWidth + 1 && innerWidth > 760) box.classList.add('tw-tight');
    };
    fit();
    if (window.ResizeObserver) new ResizeObserver(fit).observe(box.parentElement || box);
    // The sticky strip is taller now; keep anchored scrolling clear of it.
    requestAnimationFrame(() => {
      const strip = document.querySelector('.dw-protocol-strip');
      if (strip) document.documentElement.style.setProperty('--pathway-nav-height', Math.ceil(strip.getBoundingClientRect().height) + 'px');
    });
  }

  /* Middle column: findings → criteria → result group (result, reasons to reassess, other results) → evidence. */
  function wrap(node, cls, title) {
    if (!node) return null;
    if (node.parentElement?.classList.contains(cls)) return node.parentElement;
    const box = make('div', cls);
    if (title) box.append(make('p', 'tw-kicker', title));
    node.before(box);
    box.append(node);
    return box;
  }
  function regroup(decision) {
    if (!decision.classList.contains('dw-ready')) return;
    const middle = decision.querySelector('.dw-criteria');
    const results = decision.querySelector('#decision-results');
    if (!middle || !results) return;
    if (!decision.classList.contains('tw-decision')) decision.classList.add('tw-decision');
    const findings = wrap(middle.querySelector('#layer-current'), 'tw-findings', 'Findings');
    // Findings already recorded belong in the same panel, above the next question.
    const recorded = middle.querySelector('.dw-recorded');
    if (findings && recorded && recorded.parentElement !== findings) findings.firstElementChild.after(recorded);
    if (findings) { const empty = !findings.querySelector('.layer-row') && (!recorded || recorded.hidden); if (findings.hidden !== empty) findings.hidden = empty; }
    wrap(middle.querySelector('.orders'), 'tw-criteria', 'Criteria for this decision');
    let group = middle.querySelector(':scope>.tw-outcome');
    if (!group) {
      group = make('section', 'tw-outcome');
      group.setAttribute('aria-label', 'Result within this decision');
      results.before(group);
    }
    if (results.parentElement !== group) group.prepend(results);
    // Reasons to reassess sit directly under the result they qualify, as Avoid sits under recommendations.
    const stops = decision.querySelector('.stops');
    if (stops) { if (!stops.classList.contains('tw-stops')) stops.classList.add('tw-stops'); if (results.nextElementSibling !== stops) results.after(stops); }
    const other = decision.querySelector('.other-results');
    if (other && other.parentElement !== group) group.append(other);
    if (other && stops && stops.nextElementSibling !== other) stops.after(other);
    const evidence = decision.querySelector('#outcome-evidence');
    if (evidence && middle.contains(evidence) && group.nextElementSibling !== evidence) group.after(evidence);
    // The same sentence twice in adjacent panels: keep it once, in the criteria with its source.
    const plain = s => String(s || '').replace(/\s+/g, ' ').trim();
    const help = middle.querySelector('#layer-current .layer-help');
    const summary = plain(middle.querySelector('.tw-criteria .ci-summary .ci-label')?.textContent);
    if (help) { const dup = !!summary && plain(help.textContent) === summary; if (help.classList.contains('tw-dup') !== dup) help.classList.toggle('tw-dup', dup); }
    // Kind of the current result, for the tint of the result panel.
    const current = decision.querySelector('#current-result>.branch');
    const kind = current ? ['advance', 'hold', 'redirect', 'stop', 'pending'].find(k => current.classList.contains(k)) || 'pending' : 'pending';
    if (group.dataset.kind !== kind) group.dataset.kind = kind;
  }

  /* ---------- Possible results of each decision, listed as roadmap options ---------- */
  const slug = data.pathway.slug;
  const STUDIES = () => (window.CompactEvidenceData || {}).studies || {};
  const GROUPS = [
    ['advance', 'Continue assessment'],
    ['hold', 'Clarify before continuing'],
    ['redirect', 'Another route'],
    ['stop', 'Stop under this pathway']
  ];
  let peerId = 0;
  function peer(label, panel, cls, count) {
    const b = make('button', 'ct-peer ' + cls);
    b.type = 'button';
    const short = {'Evidence & sources': 'Evidence'}[label];
    b.append(make('span', 'ct-peer-label', short || label));
    if (short) b.setAttribute('aria-label', label + (count ? ', ' + count : ''));
    if (count) b.append(make('span', 'ct-peer-count', String(count)));
    if (!panel.id) panel.id = 'tw-panel-' + (++peerId);
    b.setAttribute('aria-controls', panel.id);
    const sync = () => b.setAttribute('aria-expanded', String(panel.open));
    b.addEventListener('click', () => { panel.open = !panel.open; sync(); });
    panel.addEventListener('toggle', sync);
    sync();
    return b;
  }
  function cites(refs) {
    const span = make('span', 'citations');
    for (const id of [...new Set(refs || [])]) {
      const s = data.sources[id];
      if (!s) continue;
      const c = make('button', 'cite', s.short + ' ↗');
      c.type = 'button'; c.dataset.ref = id; c.setAttribute('aria-label', 'Evidence: ' + s.short);
      span.append(' ', c);
    }
    return span;
  }
  function criteriaList(items) {
    const ul = make('ul', 'tw-crit');
    for (const x of items || []) {
      const li = make('li', '', x.text);
      if (x.refs?.length) li.append(cites(x.refs));
      if (x.children?.length) li.append(criteriaList(x.children));
      ul.append(li);
    }
    return ul;
  }
  function refsOf(items, into = []) {
    for (const x of items || []) { into.push(...(x.refs || [])); refsOf(x.children, into); }
    return into;
  }
  // One line per source, in the liver-directed matrix format.
  function sourceLine(id) {
    const s = data.sources[id];
    if (!s) return null;
    const li = make('li', 'ct-ev-row');
    const head = make('span', 'ct-ev-head');
    const name = make('button', 'ct-ev-label', s.short);
    name.type = 'button'; name.dataset.ref = id; name.title = 'Open this source';
    head.append(name);
    li.append(head);
    // PMID from the record, or from its locator or PubMed link (older records keep it there).
    const pmid = String(s.pmid || (`${s.locator || ''} ${s.url || ''}`.match(/(?:PMID[:\s]*|pubmed\.ncbi\.nlm\.nih\.gov\/)(\d{6,9})/) || [])[1] || '');
    const study = /^\d{6,9}$/.test(pmid) ? STUDIES()[pmid] : null;
    if (/^\d{6,9}$/.test(pmid)) {
      const a = make('a', 'ct-pm', pmid);
      a.href = `https://pubmed.ncbi.nlm.nih.gov/${pmid}/`; a.target = '_blank'; a.rel = 'noopener';
      a.setAttribute('aria-label', 'PubMed ' + pmid);
      head.append(a);
    }
    if (study) {
      if (study.a) head.append(make('span', 'ct-ev-arms', study.a));
      if (study.d && !(study.a || '').startsWith(study.d)) head.append(make('span', 'ct-ev-design', study.d));
      if (study.r) li.append(make('span', 'ct-ev-result', study.r));
      if (study.c) li.append(make('span', 'ct-ev-caution', study.c));
      li.classList.add('ct-ev-study');
    } else {
      head.append(make('span', 'ct-ev-kind', s.kind || 'Source'));
      if (s.url) { const a = make('a', 'ct-ev-link', 'Source ↗'); a.href = s.url; a.target = '_blank'; a.rel = 'noopener'; head.append(a); }
      li.append(make('span', 'ct-ev-result ct-ev-cite', s.note || s.title || ''));
      if (s.locator) li.append(make('span', 'tw-ev-locator', s.locator));
      li.classList.add('ct-ev-src');
    }
    return li;
  }
  function evidencePanel(refs) {
    const ids = [...new Set(refs)].filter(id => data.sources[id]);
    if (!ids.length) return null;
    const panel = make('details', 'ct-panel ct-evidence');
    panel.append(make('summary', '', 'Evidence & sources'));
    const list = make('ul', 'ct-ev');
    // Studies with a result first, then guidance and policy, citation order otherwise kept.
    const lines = ids.map(sourceLine).filter(Boolean);
    lines.filter(li => li.classList.contains('ct-ev-study')).concat(lines.filter(li => !li.classList.contains('ct-ev-study'))).forEach(li => list.append(li));
    panel.append(list);
    return {panel, count: ids.length};
  }
  function actionsFor(step, index) {
    const list = (data.continuations?.[slug + '/' + step.id]?.branches?.[index] || []).filter(a => a.step !== step.id);
    if (!list.length) return null;
    if (typeof renderActions === 'function') {          // the page's own renderer, so links behave as before
      const box = make('div', 'tw-next');
      box.innerHTML = renderActions(list);
      return box;
    }
    return null;
  }
  function optionCard(step, branch, index) {
    const card = make('article', 'tw-option tw-k-' + branch.kind);
    card.dataset.branchIndex = String(index);
    card.append(make('h5', 'tw-option-title', branch.title));
    if (branch.action) card.append(make('p', 'tw-option-action', branch.action));
    const next = actionsFor(step, index);
    if (next) card.append(next);
    const row = make('div', 'ct-peers');
    row.setAttribute('role', 'group');
    row.setAttribute('aria-label', 'Details for this result');
    const panels = make('div', 'ct-panels tw-option-panels');
    if (branch.criteria?.length) {
      const crit = make('details', 'ct-panel ci-indications tw-when');
      crit.append(make('summary', '', 'Applies when'));
      const inner = make('div', 'moreinner');
      inner.append(criteriaList(branch.criteria));
      crit.append(inner);
      panels.append(crit);
      row.append(peer('Applies when', crit, 'ct-peer-ind'));
    }
    const ev = evidencePanel([...refsOf(branch.criteria), ...(branch.refs || [])]);
    if (ev) { panels.append(ev.panel); row.append(peer('Evidence & sources', ev.panel, 'ct-peer-ev', ev.count)); }
    if (row.childElementCount) card.append(row, panels);
    return card;
  }
  function highRiskGroup(step) {
    const reviews = (data.high_risk?.pathways?.[slug]?.reviews || []).filter(r => (r.steps || []).includes(step.id));
    if (!reviews.length) return null;
    const group = make('section', 'tw-group tw-k-risk');
    group.append(make('h4', '', 'High-risk protocol reviews'));
    for (const r of reviews) {
      const card = make('article', 'tw-option tw-k-risk');
      card.append(make('h5', 'tw-option-title', r.title));
      if (r.status) card.append(make('p', 'tw-option-status', r.status));
      if (r.context) card.append(make('p', 'tw-option-action', r.context));
      const a = make('a', 'route-button high-risk-route', 'Open the high-risk review →');
      a.href = '#high-risk-' + r.anchor; a.dataset.highRisk = r.anchor;
      const box = make('div', 'tw-next');
      box.append(a);
      card.append(box);
      group.append(card);
    }
    return group;
  }
  function criteriaCard(step) {
    const config = data.assistants?.[slug + '/' + step.id];
    const box = make('section', 'tw-static-criteria');
    box.append(make('p', 'tw-kicker', 'What this decision assesses'));
    const list = make('ul', 'tw-assess');
    const definitions = new Map();
    for (const q of config?.questions || []) {
      const li = make('li');
      li.append(make('b', '', q.label));
      if (q.help) li.append(make('span', 'tw-assess-help', q.help));
      // Its sources are listed once, with results, under Evidence & sources below.
      list.append(li);
      for (const c of q.criteria || []) if (!definitions.has(c.title)) definitions.set(c.title, c);
    }
    if (list.childElementCount) box.append(list);
    for (const c of definitions.values()) {
      const d = make('details', 'tw-definition');
      d.append(make('summary', '', c.title));
      const ul = make('ul');
      for (const item of c.items || []) ul.append(make('li', '', item));
      d.append(ul);
      if (c.refs?.length) { const p = make('p', 'tw-def-sources'); p.append(cites(c.refs)); d.append(p); }
      box.append(d);
    }
    // The papers and guidance behind these questions and definitions, as matrix-style lines.
    const refs = [...(config?.questions || []).flatMap(q => q.refs || []), ...[...definitions.values()].flatMap(c => c.refs || [])];
    // They sit folded at the bottom of the decision (Hao, 28 October), with the treatment matrices.
    const ev = evidencePanel(refs);
    let fold = null;
    if (ev) {
      fold = ev.panel;
      fold.className = 'tc-fold tw-evidence-fold ct-evidence';
      const s = fold.querySelector(':scope>summary');
      s.replaceChildren(make('span', 'tc-fold-name', 'Evidence & sources for this decision'), make('span', 'tc-kind', ev.count + (ev.count === 1 ? ' source' : ' sources')));
      const body = make('div', 'tc-fold-body');
      body.append(...[...fold.childNodes].filter(n => n !== s));
      fold.append(body);
    }
    return [list.childElementCount || definitions.size ? box : null, fold];
  }
  function staticOptions(decision) {
    const id = decision.querySelector('.permalink')?.getAttribute('href')?.slice(1);
    const step = data.pathway.steps.find(s => s.id === id);
    const middle = decision.querySelector('.dw-criteria');
    if (!step || !middle) return;
    if (decision.dataset.twOptions === id && middle.querySelector(':scope>.tw-options')) return;
    middle.querySelectorAll(':scope>.tw-options,:scope>.tw-static-criteria,:scope>.tw-more').forEach(n => n.remove());
    decision.dataset.twOptions = id;
    const [crit, evidence] = criteriaCard(step);
    const box = make('section', 'tw-options');
    box.setAttribute('aria-label', 'Possible results within this decision');
    box.append(make('h4', 'tw-options-title', 'Possible results within this decision'));
    for (const [kind, title] of GROUPS) {
      const branches = step.branches.map((b, i) => [b, i]).filter(([b]) => b.kind === kind);
      if (!branches.length) continue;
      const group = make('section', 'tw-group tw-k-' + kind);
      group.append(make('h4', '', title));
      for (const [b, i] of branches) group.append(optionCard(step, b, i));
      box.append(group);
    }
    const risk = highRiskGroup(step);
    if (risk) box.append(risk);
    if (step.stops?.length) {
      const group = make('section', 'tw-group tw-k-reassess');
      group.append(make('h4', '', 'Reasons to reassess'));
      const ul = make('ul', 'tw-reassess');
      for (const s of step.stops) { const li = make('li', '', s.text); if (s.refs?.length) li.append(cites(s.refs)); ul.append(li); }
      group.append(ul);
      box.append(group);
    }
    // Place after the title (and the wait-time sub-navigation), before the step-by-step panels.
    const anchor = middle.querySelector(':scope>.dw-wait-parts') || middle.querySelector(':scope>.dw-column-title');
    anchor.after(...[crit, box].filter(Boolean));
    // Folded at the bottom: this decision's evidence, then (tools-column.js) the treatment matrices.
    const more = make('section', 'tw-more');
    more.setAttribute('aria-label', 'Evidence and treatment matrices');
    if (evidence) more.append(evidence);
    middle.append(more);
  }
  /* Mode: possible results (default) or step-by-step finding entry. */
  const MODE_KEY = 'tw.mode.' + slug;
  let interactive = false;
  try { interactive = localStorage.getItem(MODE_KEY) === 'step'; } catch { interactive = false; }
  const applyMode = () => document.documentElement.classList.toggle('tw-interactive', interactive);
  applyMode();
  function modeControl(decision) {
    const tools = decision.querySelector('.dw-tools');
    if (!tools || tools.querySelector('.tw-mode')) return;
    const box = make('div', 'tw-mode');
    box.append(make('h4', '', 'For a specific patient'));
    const b = make('button', 'clinical-button tw-mode-button');
    b.type = 'button';
    const label = () => { b.textContent = interactive ? 'Show all possible results' : 'Record findings step by step'; b.setAttribute('aria-pressed', String(interactive)); };
    label();
    b.addEventListener('click', () => {
      interactive = !interactive;
      try { localStorage.setItem(MODE_KEY, interactive ? 'step' : 'all'); } catch { /* per-viewer convenience only */ }
      applyMode();
      document.querySelectorAll('.tw-mode-button').forEach(x => { x.textContent = interactive ? 'Show all possible results' : 'Record findings step by step'; x.setAttribute('aria-pressed', String(interactive)); });
      // On phones, show the requested view instead of leaving it hidden behind the Tools tab.
      if (matchMedia('(max-width:760px)').matches) document.getElementById('dw-tab-criteria')?.click();
    });
    box.append(b, make('p', 'tw-mode-note', 'Optional. Choosing findings highlights the matching result. Findings stay in this tab and are not saved.'));
    tools.append(box);
  }

  // On a phone the section tabs scroll sideways; keep the open section's tab in view (e.g. a link to
  // #high-risk lands with "High-risk protocols" visible, not scrolled off to the right).
  function revealTab() {
    const bar = document.querySelector('.viewbar'), tab = bar?.querySelector('[aria-selected="true"]');
    if (!tab || bar.scrollWidth <= bar.clientWidth) return;
    const left = tab.getBoundingClientRect().left - bar.getBoundingClientRect().left + bar.scrollLeft, right = left + tab.offsetWidth;
    if (left < bar.scrollLeft || right > bar.scrollLeft + bar.clientWidth) bar.scrollLeft = Math.max(0, left - 16);
  }

  function scan() {
    queued = false;
    revealTab();
    phases();
    document.querySelectorAll('.decision.dw-protocol').forEach(d => { regroup(d); if (d.classList.contains('dw-ready')) { staticOptions(d); modeControl(d); } });
  }
  new MutationObserver(records => {
    if (!queued && records.some(r => r.type === 'childList')) { queued = true; requestAnimationFrame(scan); }
  }).observe(document.body, {childList: true, subtree: true});
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', scan); else scan();
})();
