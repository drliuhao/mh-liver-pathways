/* Standardized documents (29 October 2026, Analyst B): a Documents menu in the top-right corner of every tumor page,
   and the roadmaps' "Questions for consensus" section. Presentation only: nothing is stored, nothing changes a
   recommendation, and every word shown comes from documents/<tumor>/questions.json, which is built from the roadmap,
   the transplant protocol data and the recorded reviews (tools/build_consensus.py).

   Each tumor has up to three sets (roadmap, standard pathway, high-risk pathway), each with
   a full-content Word file and a questions-for-consensus Word file, plus one decision-discussion file for all settings.
   The corner offers the set that belongs to the page in view, so every file has exactly one place to download it. */
(() => {
  'use strict';
  const root = new URL('../', document.currentScript.src);
  const KEY = '20261029-docs1';
  const path = location.pathname.slice(root.pathname.length).split('/').filter(Boolean);
  const ROADMAP = {hcc: 'hcc', hilar: 'pcca', icca: 'icca', crlm: 'crlm', nelm: 'nelm', adenoma: 'hca', chcca: 'chcca', pdac: 'pdac',
    pnet: 'pnet', ampullary: 'ampullary', pcyst: 'pcyst', incidental: 'incidental'};
  const TRANSPLANT = {hcc: 'hcc', pcca: 'pcca', icca: 'icca', crlm: 'crlm', nelm: 'nelm', hehe: 'hehe', hca: 'hca'};
  const transplant = path[0] === 'transplant';
  const key = transplant ? TRANSPLANT[path[1]] : ROADMAP[path[0]];
  if (!key) return;
  const esc = s => String(s ?? '').replace(/[&<>"']/g, c => ({'&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;'}[c]));
  const make = (tag, cls, text) => { const n = document.createElement(tag); if (cls) n.className = cls; if (text != null) n.textContent = text; return n; };
  const ready = fn => document.readyState === 'loading' ? document.addEventListener('DOMContentLoaded', fn, {once: true}) : fn();
  const setInView = () => !transplant ? 'roadmap' : /^#high-risk/.test(location.hash) ? 'highrisk' : 'standard';
  const LABELS = {
    roadmap: [['roadmap_info', 'Roadmap', 'Full content'], ['roadmap_questions', 'Roadmap questions for consensus', 'Positions, proposed selection, decision fields'],
      ['decision', 'Decision discussion', 'All settings for this tumor']],
    standard: [['standard_info', 'Standard pathway', 'Full content'], ['standard_questions', 'Standard pathway questions for consensus', 'Positions, proposed selection, decision fields'],
      ['decision', 'Decision discussion', 'All settings for this tumor']],
    highrisk: [['highrisk_info', 'High-risk pathway', 'Full content'], ['highrisk_questions', 'High-risk pathway questions for consensus', 'Positions, proposed selection, decision fields'],
      ['decision', 'Decision discussion', 'All settings for this tumor']]
  };

  function corner(t) {
    const nav = document.querySelector('nav.shared-portal-nav');
    if (!nav || nav.querySelector('.doc-corner')) return;
    const box = make('details', 'doc-corner'), summary = make('summary', '', 'Documents'), list = make('div', 'doc-corner-list');
    box.append(summary, list);
    const fill = () => {
      const set = setInView();
      list.innerHTML = `<p class="doc-corner-head">${esc(t.code)} · ${esc({roadmap: 'Roadmap', standard: 'Standard pathway', highrisk: 'High-risk pathway'}[set])}</p>` +
        LABELS[set].filter(([k]) => t.files[k]).map(([k, label, note]) =>
          `<a href="${esc(new URL(`documents/${key}/${t.files[k]}`, root).href)}" download data-doc="${esc(k)}"><b>${esc(label)}</b><small>${esc(note)} · Word</small></a>`).join('');
      box.dataset.set = set;
    };
    fill();
    if (transplant) window.addEventListener('hashchange', fill);
    nav.append(box);
    document.addEventListener('click', ev => { if (!box.contains(ev.target)) box.open = false; });
    box.addEventListener('keydown', ev => { if (ev.key === 'Escape') { box.open = false; summary.focus(); } });
  }

  /* ---------- roadmap: Questions for consensus ---------- */
  function rows(items, cols) {
    return `<div class="cq-table"><table><thead><tr>${cols.map(c => `<th>${esc(c[0])}</th>`).join('')}</tr></thead><tbody>${items.map(x =>
      `<tr>${cols.map(c => `<td>${c[1](x)}</td>`).join('')}</tr>`).join('')}</tbody></table></div>`;
  }
  function sourceLink(data, k, label) {
    const s = data.sources[k]; const L = s && s.links || {};
    const href = L.pubmed || L.doi || L.url || L.tmc;
    return href ? `<a href="${esc(href)}" target="_blank" rel="noopener">${esc(label)}</a>` : esc(label);
  }
  function card(data, q, slug) {
    const where = (q.where || []).map(w => `<a href="#${esc(w.url.split('#')[1])}">${esc(w.label)}</a>`).join(' · ');
    const pos = (q.positions || []).length ? rows(q.positions, [['Source', x => `<b>${sourceLink(data, x.key, x.source)}</b>`], ['Position', x => esc(x.says)], ['Where stated', x => `<small>${esc(x.locator)}</small>`]]) : '';
    const studies = (q.studies || []).length ? rows(q.studies, [['Source', x => `<b>${sourceLink(data, x.key, x.source)}</b>${x.read ? `<small>${esc(x.read)}</small>` : ''}`],
      ['Population and selection', x => esc(x.population)], ['Results and limits', x => `${esc(x.results)}${x.limits ? `<small>Limits: ${esc(x.limits)}</small>` : ''}<small>${esc(x.locator)}</small>`]]) : '';
    const n = (q.positions || []).length + (q.studies || []).length;
    const more = [['Why', q.rationale], ['Against, or uncertain', q.counter], ['Certainty', q.certainty], ['What would change the answer', q.change],
      ['Tests and records', q.tests], ['Allocation', q.allocation], ['Owners', q.owners], ['What gets audited', q.audit], ['Roadmap note', q.note]]
      .filter(x => x[1]).map(([l, v]) => `<p><b>${esc(l)}.</b> ${esc(v)}</p>`).join('');
    return `<article class="cq-card" id="question-${esc(q.id)}" data-question="${esc(q.id)}">
      <div class="cq-top"><span class="cq-id">${esc(q.id)}</span>${q.kind ? `<span class="cq-kind">${esc(q.kind)}</span>` : ''}<span class="cq-status">${esc(q.status)}</span></div>
      <h3>${esc(q.question)}</h3>${where ? `<p class="cq-where">Where it is decided: ${where}</p>` : ''}
      ${n ? `<details class="cq-fold"><summary>Positions of guidelines, trials and papers <span>${n}</span></summary>${pos}${studies}</details>` :
        '<p class="cq-none">No guideline, trial or paper takes a position on this question; it is a programme decision.</p>'}
      ${q.divergence ? `<p class="cq-diverge"><b>Where sources differ.</b> ${esc(q.divergence)}</p>` : ''}
      <div class="cq-proposal"><b>Proposed selection · OPEN</b><p>${esc(q.proposal || 'No proposal yet; the group decides.')}</p>${(q.rules || []).length ? `<ul>${q.rules.map(r => `<li>${esc(r)}</li>`).join('')}</ul>` : ''}${q.proposal_locator ? `<small>Basis in the roadmap: ${esc(q.proposal_locator)}</small>` : ''}</div>
      ${more ? `<details class="cq-fold"><summary>Rationale${q.audit ? ' and audit' : ''}</summary>${more}</details>` : ''}
      <p class="cq-decision">Group decision: <b>not yet recorded</b>.</p></article>`;
  }
  function questions(t) {
    const slug = path[0];
    const ops = document.getElementById('ops'), evidence = document.getElementById('evidence');
    const anchor = ops || evidence;
    if (!anchor || document.getElementById('questions')) return;
    fetch(new URL(`documents/${key}/questions.json?v=${KEY}`, root)).then(r => r.ok ? r.json() : null).then(data => {
      const set = data && data.sets.roadmap;
      if (!set) return;
      const sec = make('section', 'consensus-questions'); sec.id = 'questions'; sec.dataset.hierarchyRole = 'background';
      const ratify = set.ratify && set.ratify.length ? `<details class="cq-fold cq-ratify"><summary>Specialty ratification items <span>${set.ratify.length}</span></summary>${rows(set.ratify,
        [['Item', x => `<b>${esc(x.id)}</b><small>${esc(x.specialty)}</small>`], ['To ratify', x => esc(x.question)], ["Roadmap's stated position", x => `${esc(x.proposal)}<small>${esc(x.proposal_locator)}</small>`]])}</details>` : '';
      const na = (data.not_applicable || []).map(n => `<p class="cq-na"><b>Previously treated extrahepatic disease.</b> ${esc(n.text)}</p>`).join('');
      sec.innerHTML = `<div class="sechead"><h3 class="ch-background-title">Questions for consensus</h3><p>Every decision this roadmap still needs the programme to make: what guidelines, trials and papers say, the proposed selection, and the group decision. The same questions are in the Word files under <b>Documents</b> (top right).</p><button class="xpand" type="button" aria-expanded="false">Show</button></div>
        <div class="cq-body" hidden><nav class="cq-index" aria-label="Questions for consensus">${set.questions.map(q => `<a href="#question-${esc(q.id)}">${esc(q.id)}</a>`).join('')}</nav>
        ${set.questions.map(q => card(data, q, slug)).join('')}${ratify}${na}</div>`;
      anchor.before(sec);
      const body = sec.querySelector('.cq-body'), btn = sec.querySelector('.xpand');
      const show = open => { body.hidden = !open; btn.textContent = open ? 'Hide' : 'Show'; btn.setAttribute('aria-expanded', String(open)); };
      btn.addEventListener('click', () => show(body.hidden));
      const reveal = () => {
        let id; try { id = decodeURIComponent(location.hash.slice(1)); } catch { return; }
        if (id !== 'questions' && !id.startsWith('question-')) return;
        show(true);
        const target = document.getElementById(id);
        if (target) { target.querySelectorAll('details.cq-fold').forEach(d => { d.open = true; }); requestAnimationFrame(() => target.scrollIntoView({block: 'start'})); }
      };
      window.addEventListener('hashchange', reveal); reveal();
      const nav = document.querySelector('header.top nav.sec');
      if (nav && !nav.querySelector('a[href="#questions"]')) {
        const a = make('a', 'cq-nav', 'Questions for consensus'); a.href = '#questions';
        const menu = nav.querySelector('details'); menu ? menu.before(a) : nav.append(a);
      }
    }).catch(() => {});
  }

  fetch(new URL(`assets/documents.json?v=${KEY}`, root)).then(r => r.ok ? r.json() : null).then(m => {
    const t = m && m.tumors[key];
    if (!t) return;
    ready(() => { corner(t); if (!transplant) questions(t); });
  }).catch(() => {});
})();
