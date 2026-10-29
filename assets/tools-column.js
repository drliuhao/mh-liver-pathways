/* Tools & resources column: one hierarchy on every roadmap and transplant decision (Analyst B, 28 October 2026).
   Presentation only. Existing reference nodes are moved and restyled, never rewritten; scores and
   calculators come from ClinicalScores and are reference tools that store nothing and apply nothing.
     Decision team
     Scores & classifications   every score, grade, classification or criterion the decision names
     Treatment resources        systemic and liver-directed matrices (both whenever the tumor has them),
                                treatment reference, treatment guides
     Decision references        the decision's other quick references
     Evidence & documents       evidence library, protocol documents, labels and grades
   Also: the matrices folded at the bottom of treatment decisions in the transplant pathways and of
   each roadmap, loaded only when opened. */
(() => {
  'use strict';
  const S = window.ClinicalScores;
  if (!S) return;
  const root = new URL('../', document.currentScript.src);
  S.setRoot(root.href);
  const parts = location.pathname.slice(root.pathname.length).split('/').filter(Boolean);
  const transplant = parts[0] === 'transplant';
  const slug = transplant ? parts[1] : parts[0];
  const page = transplant ? 'T:' + slug : slug;
  const make = (tag, cls, text) => { const n = document.createElement(tag); if (cls) n.className = cls; if (text !== undefined) n.textContent = text; return n; };
  const plain = s => String(s || '').replace(/\s+/g, ' ').trim();
  let queued = false, uid = 0;

  /* ---------- Matrices ---------- */
  const TUMOR = {hcc: ['hcc', 'HCC'], crlm: ['crlm', 'CRLM'], icca: ['icca', 'iCCA'], hilar: ['pcca', 'pCCA'], pcca: ['pcca', 'pCCA'], nelm: ['nelm', 'NELM'],
    chcca: ['chcca', 'cHCC–CCA'], pdac: ['pdac', 'PDAC'], pnet: ['pnet', 'pNET'], ampullary: ['ampullary', 'Ampullary']};
  const HAS_LRT = new Set(['hcc', 'icca', 'pcca', 'crlm', 'nelm']);
  const HAS_SYSTEMIC = new Set(['hcc', 'pcca', 'icca', 'crlm', 'nelm', 'pdac', 'pnet', 'ampullary', 'chcca']);
  const [tumor, tumorLabel] = TUMOR[slug] || [null, ''];
  const matrices = () => [
    HAS_SYSTEMIC.has(tumor) && {kind: 'systemic', title: 'Systemic therapy matrix', href: new URL('systemic/?tumor=' + tumor, root).href},
    HAS_LRT.has(tumor) && {kind: 'lrt', title: 'Liver-directed therapy matrix', href: new URL('lrt/#' + tumor, root).href}
  ].filter(Boolean);
  // Transplant decisions where treatment is chosen or delivered.
  const TREATMENT_STEPS = {hcc: ['curative-route', 'treatment', 'waitlist'], pcca: ['neoadjuvant'], icca: ['therapy', 'stability'],
    crlm: ['unresectability', 'control'], nelm: ['options', 'exposure']};

  let systemicData = null, lrtData = null;
  const loadSystemic = () => systemicData || (systemicData = fetch(new URL('systemic/matrix.json?v=20261029-ehd1', root)).then(r => { if (!r.ok) throw new Error('Matrix unavailable'); return r.json(); }));
  // All roadmap and pathway views use the same reviewed matrix data.
  const loadLrt = () => lrtData || (lrtData = fetch(new URL('lrt/matrix.json?v=20261029-ehd1', root)).then(r => { if (!r.ok) throw new Error('Matrix unavailable'); return r.json(); }));
  const SETTINGS = [['first', 'Initial advanced disease'], ['later', 'Subsequent'], ['biomarker', 'Molecularly selected'],
    ['perioperative', 'Around curative local treatment'], ['combination', 'Combination / sequencing'], ['transplant', 'Transplant strategy']];

  function fillSystemic(body) {
    return loadSystemic().then(data => {
      const cards = data.cards.filter(c => c.tumors.includes(tumor));
      body.replaceChildren();
      for (const [key, label] of SETTINGS) {
        const group = cards.filter(c => c.setting === key);
        if (!group.length) continue;
        body.append(make('h5', 'tc-mx-group', label));
        const ul = make('ul', 'tc-mx-list');
        for (const c of group) {
          const li = make('li');
          const a = make('a', 'tc-mx-name', c.title); a.href = new URL('systemic/?tumor=' + tumor + '#' + c.id, root).href;
          li.append(a, make('span', 'tc-mx-what', c.position));
          ul.append(li);
        }
        body.append(ul);
      }
      const all = make('a', 'tc-link', 'Open the full systemic therapy matrix'); all.href = new URL('systemic/?tumor=' + tumor, root).href;
      body.append(all);
      return cards.length;
    });
  }
  function fillLrt(body) {
    return loadLrt().then(data => {
      body.replaceChildren();
      const ul = make('ul', 'tc-mx-list');
      let n = 0;
      for (const [key, name, sub] of data.modalities) {
        const cell = data.cells[tumor + '|' + key];
        if (!cell) continue;
        n++;
        const li = make('li');
        const a = make('a', 'tc-mx-name', name); a.href = new URL('lrt/#' + tumor, root).href;
        const tier = data.tiers[cell.tier];
        li.append(a);
        if (tier) li.append(make('span', 'tc-tier tc-t' + cell.tier, tier.short));
        li.append(make('span', 'tc-mx-what', cell.head));
        if (sub) a.title = sub;
        ul.append(li);
      }
      body.append(ul);
      const all = make('a', 'tc-link', 'Open the full liver-directed therapy matrix'); all.href = new URL('lrt/#' + tumor, root).href;
      body.append(all);
      return n;
    });
  }
  // A folded matrix: loads when first opened.
  function matrixFold(m) {
    const d = make('details', 'tc-fold tc-fold-' + m.kind);
    const s = make('summary');
    s.append(make('span', 'tc-fold-name', (m.kind === 'lrt' ? 'Liver-directed therapy' : 'Systemic therapy') + ' · ' + tumorLabel), make('span', 'tc-kind', 'Matrix'));
    const body = make('div', 'tc-fold-body');
    body.append(make('p', 'tc-note', 'Opens the published matrix for this tumor.'));
    d.append(s, body);
    d.addEventListener('toggle', () => {
      if (!d.open || d.dataset.loaded) return;
      d.dataset.loaded = 'loading';
      body.replaceChildren(make('p', 'tc-note', 'Loading…'));
      (m.kind === 'lrt' ? fillLrt : fillSystemic)(body).then(() => { d.dataset.loaded = 'true'; }).catch(() => {
        d.dataset.loaded = '';
        body.replaceChildren(make('p', 'tc-note', 'The matrix could not be loaded here. '));
        const a = make('a', 'tc-link', 'Open the ' + m.title.toLowerCase()); a.href = m.href; body.lastChild.append(a);
      });
    });
    return d;
  }

  /* ---------- Calculators ---------- */
  function calculator(id) {
    const spec = S.forms[id];
    if (!spec) return null;
    const n = ++uid;
    const form = make('form', 'tc-calc');
    form.noValidate = true;
    form.addEventListener('submit', ev => ev.preventDefault());
    form.append(make('p', 'tc-calc-title', 'Calculate'));
    const grid = make('div', 'tc-fields');
    for (const f of spec.fields) {
      const fid = `tc-${id}-${f.id}-${n}`;
      const wrap = make('div', 'tc-field' + (f.type === 'check' ? ' tc-check' : ''));
      let input;
      if (f.type === 'select') {
        input = make('select');
        for (const [value, label] of f.options) { const o = make('option', '', label); o.value = value; input.append(o); }
      } else {
        input = make('input');
        input.type = f.type === 'check' ? 'checkbox' : 'number';
        if (f.type === 'number') { input.inputMode = 'decimal'; input.step = f.step || 'any'; input.min = '0'; }
      }
      input.id = fid; input.name = f.id;
      const label = make('label', '', f.label + (f.unit ? ` (${f.unit})` : ''));
      label.htmlFor = fid;
      if (f.type === 'check') wrap.append(input, label); else wrap.append(label, input);
      grid.append(wrap);
    }
    const out = make('output', 'tc-result', 'Enter values to calculate.');
    out.setAttribute('aria-live', 'polite');
    out.htmlFor = [...grid.querySelectorAll('input,select')].map(x => x.id).join(' ');
    form.append(grid, out, make('p', 'tc-calc-note', 'Reference only. Nothing is saved or applied to the pathway.'));
    const update = () => {
      const v = {};
      for (const x of form.querySelectorAll('input,select')) v[x.name] = x.type === 'checkbox' ? x.checked : x.value;
      const r = spec.run(spec.collect ? spec.collect(v) : v);
      out.replaceChildren();
      if (!r.ok) { out.classList.remove('has-result'); out.textContent = r.message; return; }
      out.classList.add('has-result');
      const lines = [].concat(spec.read(r));
      out.append(make('strong', '', lines[0]));
      for (const line of lines.slice(1)) out.append(make('span', '', line));
    };
    form.addEventListener('input', update);
    form.addEventListener('change', update);
    if (spec.fields.every(f => f.type === 'check')) update();
    return form;
  }

  /* ---------- Rows ---------- */
  function rowSummary(d, name, kind) {
    let s = d.querySelector(':scope>summary');
    if (!s) { s = make('summary'); d.prepend(s); }
    s.removeAttribute('hidden');
    s.replaceChildren(make('span', 'tc-name', name), make('span', 'tc-kind', kind));
  }
  function scoreRow(id) {
    const item = S.items[id];
    const d = make('details', 'tc-row');
    d.dataset.tc = id;
    rowSummary(d, item.name, item.kind);
    const body = make('div', 'tc-body');
    body.innerHTML = item.html();
    const calc = calculator(id);
    if (calc) body.append(calc);
    d.append(body);
    return d;
  }
  // A page's own quick reference becomes a row; a calculator is added when the page has none.
  function adoptReference(node, id, kind) {
    const label = node.dataset.tcLabel || plain(node.querySelector(':scope>summary')?.textContent);
    node.dataset.tcLabel = label;
    node.classList.add('tc-row');
    // A scale or score keeps one name across pages; a broader page reference keeps its own label.
    const name = ['child', 'ecog'].includes(id) ? S.items[id].name : label;
    if (id) node.dataset.tc = id;
    const hasInputs = !!node.querySelector('input,select');
    const calc = id && !hasInputs && !node.querySelector('.tc-calc') ? calculator(id) : null;
    if (calc) node.append(calc);
    rowSummary(node, name, calc || hasInputs ? 'Calculator' : kind);
    node.open = false;
  }
  function linkRow(a, text) {
    a.classList.remove('clinical-button');
    a.classList.add('tc-link');
    if (text) a.textContent = text;
  }

  function section(list, cls, title) {
    let s = list.querySelector(':scope>.' + cls);
    if (!s) { s = make('section', cls); list.append(s); }
    if (!s.classList.contains('tc-section')) s.classList.add('tc-section');
    let h = s.querySelector(':scope>h4');
    if (!h) { h = make('h4'); s.prepend(h); }
    if (h.className !== 'tc-heading') h.className = 'tc-heading';
    if (h.textContent !== title) h.textContent = title;
    return s;
  }
  // Append in the given order only when the order differs, so a settled column causes no mutations.
  function ensureOrder(parent, nodes) {
    const current = [...parent.children].filter(n => nodes.includes(n));
    if (current.length === nodes.length && current.every((n, i) => n === nodes[i])) return;
    nodes.forEach(n => parent.append(n));
  }
  // Text of the decision itself, used to find the scores it names: a roadmap decision's visible content,
  // or a transplant decision's own protocol data (its step, decision aid and the high-risk reviews it covers).
  let protocol;
  try { protocol = JSON.parse(document.getElementById('protocol-data')?.textContent || 'null'); } catch { protocol = null; }
  function decisionText(w) {
    if (protocol?.pathway && w.classList.contains('dw-protocol')) {
      const id = w.querySelector('.permalink')?.getAttribute('href')?.slice(1);
      const step = protocol.pathway.steps.find(s => s.id === id);
      const reviews = (protocol.high_risk?.pathways?.[protocol.pathway.slug]?.reviews || []).filter(r => (r.steps || []).includes(id));
      return JSON.stringify([step, protocol.assistants?.[protocol.pathway.slug + '/' + id], reviews.map(r => [r.title, r.context, r.rules])]);
    }
    return [...w.querySelectorAll('.ahead,.question-head,.contextline,.dw-inputs,.dw-criteria')].filter(n => !n.closest('.dw-tools')).map(n => n.textContent).join(' ');
  }
  const decisionId = w => w.classList.contains('dw-protocol') ? w.querySelector('.permalink')?.getAttribute('href')?.slice(1) : w.dataset.workspaceKey?.split('/')[1];

  function arrange(w) {
    const tools = w.querySelector('.dw-tools');
    const list = tools?.querySelector(':scope>.dw-tool-list');
    if (!list) return;
    tools.classList.add('tc-ready');
    const scores = section(list, 'dw-tool-calculators', 'Scores & classifications');
    const treatments = section(list, 'dw-tool-treatments', 'Treatment resources');
    const references = section(list, 'ch-decision-references', 'Decision references');
    const documents = section(list, 'dw-tool-documents', 'Evidence & documents');
    const present = new Set([...list.querySelectorAll('[data-tc]')].map(n => n.dataset.tc));

    // Existing nodes, wherever an earlier script placed them (content-hierarchy.js moves a page's quick
    // references into each new decision, so their section is checked on every pass).
    for (const node of [...list.querySelectorAll(':scope>section>*:not(h4)')]) {
      if (node.matches('details.ch-reference.tc-row')) {
        const id = node.dataset.tc;
        const target = id ? scores : node.dataset.referenceKind === 'guide' ? treatments : references;
        if (node.parentElement !== target) target.append(node);
        if (id) { list.querySelectorAll(`.tc-row:not(.ch-reference)[data-tc="${id}"]`).forEach(n => n.remove()); present.add(id); }
        continue;
      }
      if (node.matches('.tc-row,.tc-link,.tc-mx-links')) continue;
      if (node.matches('button.dw-calculator')) { node.remove(); continue; }
      if (node.matches('.ci-unit.clinical-term-unit,.clinical-term')) {
        const title = (node.matches('.clinical-term') ? node : node.querySelector('.clinical-term'))?.dataset.contextTitle || '';
        const key = Object.entries(window.ClinicalReference?.terms || {}).find(([, t]) => t.title === title)?.[0];
        const id = {lr5: 'lirads'}[key] || key;
        node.remove();
        if (id && S.items[id] && !present.has(id)) { scores.append(scoreRow(id)); present.add(id); }
        continue;
      }
      if (node.matches('details.ch-reference')) {
        const label = node.dataset.tcLabel || plain(node.querySelector(':scope>summary')?.textContent);
        const id = S.quickref[label];
        if (id) {
          // The page's own reference replaces a generic row for the same item.
          list.querySelectorAll(`.tc-row:not(.ch-reference)[data-tc="${id}"]`).forEach(n => n.remove());
          adoptReference(node, id, S.quickrefKind[id] || S.items[id]?.kind || 'Reference');
          scores.append(node); present.add(id);
        } else if (node.dataset.referenceKind === 'guide') { adoptReference(node, null, 'Guide'); treatments.append(node); }
        else { adoptReference(node, null, 'Reference'); references.append(node); }
        continue;
      }
      if (node.matches('details.rf-legend')) { adoptReference(node, null, 'Guide'); documents.append(node); continue; }
      if (node.matches('a.clinical-button,a.tc-link') && /\/(?:lrt|systemic)\//.test(node.href)) { node.remove(); continue; }
      if (node.matches('a,button.clinical-button')) {
        if (node.dataset.view === 'care') { linkRow(node, 'Treatment reference'); treatments.append(node); }
        else { linkRow(node); documents.append(node); }
        continue;
      }
    }

    // Scores the decision names that no existing node covers.
    const ids = [...S.detect(decisionText(w), page), ...(S.extra[page]?.[decisionId(w)] || [])];
    for (const id of ids) if (!present.has(id) && S.items[id]) { scores.append(scoreRow(id)); present.add(id); }
    // One order everywhere.
    const rank = id => { const i = S.order.indexOf(id); return i < 0 ? 999 : i; };
    ensureOrder(scores, [...scores.querySelectorAll(':scope>.tc-row')].sort((a, b) => rank(a.dataset.tc) - rank(b.dataset.tc)));

    // Matrices: the same links on every decision of a tumor that has them.
    if (!treatments.querySelector(':scope>.tc-mx-links')) {
      const box = make('div', 'tc-mx-links');
      for (const m of matrices()) {
        const a = make('a', 'tc-link');
        a.href = m.href;
        a.append(make('span', 'tc-name', m.title), make('span', 'tc-kind', tumorLabel));
        box.append(a);
      }
      if (box.childElementCount) treatments.querySelector(':scope>h4').after(box);
    }
    // Links first, then disclosures, inside each section.
    for (const s of [treatments, documents]) {
      const kids = [...s.children].filter(n => n.tagName !== 'H4');
      ensureOrder(s, kids.filter(n => n.tagName !== 'DETAILS').concat(kids.filter(n => n.tagName === 'DETAILS')));
    }
    for (const s of [scores, treatments, references, documents]) { const empty = !s.querySelector(':scope>:not(h4)'); if (s.hidden !== empty) s.hidden = empty; }
    ensureOrder(list, [scores, treatments, references, documents]);
  }

  /* Transplant: matrices folded at the bottom of a treatment decision, beside its evidence. */
  function transplantBottom(w) {
    const id = w.querySelector('.permalink')?.getAttribute('href')?.slice(1);
    const middle = w.querySelector('.dw-criteria');
    if (!id || !middle) return;
    const wanted = (TREATMENT_STEPS[slug] || []).includes(id) ? matrices() : [];
    let more = middle.querySelector(':scope>.tw-more');
    if (!wanted.length) { more?.querySelectorAll(':scope>.tc-fold:not(.tw-evidence-fold)').forEach(n => n.remove()); return; }
    if (!more) { more = make('section', 'tw-more'); middle.append(more); }
    if (more.dataset.tcStep === id) return;
    more.dataset.tcStep = id;
    more.querySelectorAll(':scope>.tc-fold:not(.tw-evidence-fold)').forEach(n => n.remove());
    for (const m of wanted) more.append(matrixFold(m));
  }

  /* Roadmaps: the page's own liver-directed section is folded, and the systemic matrix sits beside it. */
  function roadmapMatrices() {
    if (transplant || !tumor || !document.querySelector('#answer.dw-ready')) return;
    const host = document.getElementById('lrt');
    const anchor = host && !host.hidden ? host : document.getElementById('honest') || document.getElementById('evidence');
    if (!anchor || document.querySelector('.tc-roadmap-matrices')) return;
    if (host && !host.hidden && !host.querySelector(':scope>details.tc-fold')) {
      if (!host.querySelector('[id]') || host.childElementCount < 2) return; // wait until the page has rendered it
      const d = make('details', 'tc-fold tc-fold-lrt tc-roadmap-lrt');
      const s = make('summary');
      s.append(make('span', 'tc-fold-name', 'Liver-directed therapy · ' + tumorLabel), make('span', 'tc-kind', 'Matrix'));
      const body = make('div', 'tc-fold-body');
      body.append(...host.childNodes);
      d.append(s, body);
      host.append(make('h2', 'tc-mx-title', 'Treatment matrices'), d);
    }
    const box = make('section', 'tc-roadmap-matrices');
    box.setAttribute('aria-label', 'Treatment matrices');
    if (!(host && !host.hidden)) box.append(make('h2', 'tc-mx-title', 'Treatment matrices'));
    if (HAS_SYSTEMIC.has(tumor)) box.append(matrixFold(matrices().find(m => m.kind === 'systemic')));
    // A roadmap without its own liver-directed section (pCCA) gets the published matrix, folded.
    if (HAS_LRT.has(tumor) && !(host && !host.hidden)) box.append(matrixFold(matrices().find(m => m.kind === 'lrt')));
    // Systemic first, then liver-directed: the order of the Treatment resources links.
    if (host && !host.hidden) { host.classList.add('tc-roadmap-host'); host.querySelector(':scope>.tc-roadmap-lrt').before(box); }
    else if (box.childElementCount) anchor.before(box);
  }

  function scan() {
    queued = false;
    document.querySelectorAll('.dw-ready').forEach(w => {
      arrange(w);
      if (transplant && w.classList.contains('dw-protocol')) transplantBottom(w);
    });
    roadmapMatrices();
  }
  new MutationObserver(records => {
    if (queued || !records.some(r => r.type === 'childList' && !(r.target.nodeType === 1 && r.target.closest('.tc-calc,.tc-fold-body,.tc-row')))) return;
    queued = true;
    requestAnimationFrame(scan);
  }).observe(document.body, {childList: true, subtree: true});
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', scan); else scan();
  window.TreatmentMatrices = {fold: matrixFold, matrices};
})();
