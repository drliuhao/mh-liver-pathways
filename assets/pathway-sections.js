/* Closing sections of each transplant pathway page, matching the roadmaps (29 October 2026, Analyst B):
   Practice choices with limited evidence · Questions for consensus · Team responsibilities and quality monitoring ·
   Evidence library. Presentation only. Data: transplant/assets/pathway-sections.json (tools/build_pathway_sections.py).
   Questions for consensus is an index: each question opens where it is set out once (the meeting record or the
   high-risk view), and source chips open the page's own source dialog. Shown on the pathway and high-risk views.
   Evidence library (30 October 2026): the roadmaps' library format, rows drawn by assets/roadmap-evidence.js, with
   search, category tabs and a one-line summary per source. It replaces the former card-grid "Evidence library"
   view: the tab, #evidence and the right-column link open this section (window.PathwaySections.open). */
(() => {
  'use strict';
  const root = new URL('../', document.currentScript.src);
  const path = location.pathname.slice(root.pathname.length).split('/').filter(Boolean);
  const SLUGS = ['hcc', 'pcca', 'icca', 'crlm', 'nelm', 'hehe', 'hca'];
  if (path[0] !== 'transplant' || !SLUGS.includes(path[1]) || path.length > 2) return;
  const slug = path[1];
  const VIEWS = new Set(['pathway', 'high-risk']);
  const esc = s => String(s ?? '').replace(/[&<>"']/g, c => ({'&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;'}[c]));
  const css = document.createElement('link'); css.rel = 'stylesheet'; css.href = new URL('assets/pathway-sections.css?v=20261031-ui1', root); document.head.append(css);

  const chip = r => r.dialog ? `<button type="button" class="cite" data-ref="${esc(r.key)}">${esc(r.label)} ↗</button>`
    : r.url ? `<a href="${esc(r.url)}" target="_blank" rel="noopener">${esc(r.label)} ↗</a>` : `<span>${esc(r.label)}</span>`;
  const head = (id, title, intro) => `<div class="pw-head"><h3>${esc(title)}</h3><p>${intro}</p><button class="pw-toggle" type="button" aria-expanded="false" aria-controls="${id}-body">Show</button></div>`;
  const section = (id, title, intro, body) => `<section class="pw-sec" id="${id}">${head(id, title, intro)}<div class="pw-body" id="${id}-body" hidden>${body}</div></section>`;

  function limited(d) {
    if (!d.limited.length) return '<p class="pw-none">The protocols name no practice choice of this kind.</p>';
    return `<div class="pw-tablewrap"><table class="pw-table"><thead><tr><th style="width:38%">What the pathway applies</th><th>Basis, limits and what to track</th></tr></thead><tbody>${d.limited.map(x =>
      `<tr><td><b>${esc(x.t)}</b>${x.setting === 'highrisk' ? '<span class="pw-tag">High-risk pathway</span>' : ''}</td>
      <td>${esc(x.why)}${x.refs.length ? `<div class="pw-refs">${x.refs.map(chip).join('')}</div>` : ''}${x.related ? `<p class="pw-related">Open question: <a href="${esc(x.related.href)}">${esc(x.related.label)}</a></p>` : ''}<small>${esc(x.locator)}</small></td></tr>`).join('')}</tbody></table></div>`;
  }
  function questions(d) {
    const std = d.questions.standard.map((q, n) => `<li><a href="${esc(q.href)}">${n + 1}. ${esc(q.question)}</a></li>`).join('');
    const hr = d.questions.highrisk.map(q => `<li><a href="${esc(q.href)}"><b>${esc(q.id)}</b>${esc(q.title)}</a><small>${esc(q.status)}</small></li>`).join('');
    return `<p class="pw-sub">Standard pathway · each opens in the meeting record</p>${std ? `<ol class="pw-list">${std}</ol>` : '<p class="pw-none">None.</p>'}
      <p class="pw-sub">High-risk pathway · each opens in the high-risk view</p>${hr ? `<ul class="pw-list">${hr}</ul>` : '<p class="pw-none">None.</p>'}`;
  }
  function team(d) {
    const owners = `<p class="pw-sub">Who owns each decision</p><div class="pw-tablewrap"><table class="pw-table"><thead><tr><th style="width:30%">Decision</th><th style="width:32%">Owner</th><th>When</th></tr></thead><tbody>${d.owners.map(o =>
      `<tr><td><a href="#${esc(o.id)}">${esc(o.title)}</a></td><td>${esc(o.owner)}</td><td>${esc(o.timing)}</td></tr>`).join('')}</tbody></table></div>`;
    const mdt = `<p class="pw-sub">Multidisciplinary team</p>${d.team ? `<p class="pw-text">${esc(d.team.text)}<small>${esc(d.team.locator)}</small></p>` : '<p class="pw-none">The protocols do not describe the team.</p>'}`;
    const q = d.quality;
    const std = `<p class="pw-sub">Quality measures · standard pathway</p>${q.standard.length ? `<ul class="pw-bullets">${q.standard.map(x => `<li>${esc(x)}</li>`).join('')}</ul>` : '<p class="pw-none">The standard protocol sets no quality measures yet.</p>'}`;
    const hr = q.highrisk.length ? `<p class="pw-sub">Quality measures · proposed for the high-risk pathway, not activated</p><ul class="pw-bullets">${q.highrisk.map(x => `<li>${esc(x)}</li>`).join('')}</ul>` : '';
    return owners + mdt + std + hr + (q.locator ? `<p class="pw-related"><small>${esc(q.locator)}</small></p>` : '');
  }
  function evidence(d) {
    const groups = [...new Set(d.sources.map(r => r.group))];
    return `<div class="pw-actions"><a href="${esc(new URL('evidence-libraries/#standard_' + slug, root).href)}">Standard pathway library and slide index →</a><a href="${esc(new URL('evidence-libraries/#high_risk_' + slug, root).href)}">High-risk pathway library and slide index →</a></div>
      <div class="evtools"><input type="search" id="pw-ev-search" placeholder="Search trial, author, guideline, topic…" aria-label="Search the evidence library"><div class="tabs" id="pw-ev-groups">${['All', ...groups].map(g =>
      `<button class="tab" type="button" data-group="${esc(g)}" aria-selected="${g === 'All'}">${esc(g)}</button>`).join('')}</div><span class="evcount" id="pw-ev-count"></span></div><div class="evlist" id="pw-ev-list"></div>`;
  }
  const rowOf = r => ({id: r.key, tag: r.tag, cit: r.cit, group: r.group, pmid: r.pmid, doi: r.doi, url: r.url, access: r.access, summary: r.summary, appraisal: r.appraisal, flag: r.flag});
  let evGroup = 'All', evQuery = '';
  function renderEv(box) {
    const list = box.querySelector('#pw-ev-list'); if (!list || !window.RoadmapEvidence) return;
    const q = evQuery.trim().toLowerCase(), all = data.sources.map(rowOf);
    const rows = all.filter((r, i) => (evGroup === 'All' || r.group === evGroup) &&
      (!q || [r.tag, r.cit, r.group, ...data.sources[i].keys, RoadmapEvidence.text(r, {})].join(' ').toLowerCase().includes(q)));
    list.innerHTML = rows.length ? rows.map(r => RoadmapEvidence.row(r, {})).join('')
      : `<div class="pw-text"><span class="pw-none">Nothing matches “${esc(evQuery)}”. Try a trial name, an author, or a guideline.</span></div>`;
    box.querySelector('#pw-ev-count').textContent = `${rows.length} of ${all.length} sources`;
  }
  function build(d) {
    const box = document.createElement('div'); box.id = 'pathway-closing'; box.className = 'pw-closing';
    box.innerHTML =
      section('pw-limited', 'Practice choices with limited evidence', 'These practice choices in the pathway rest mainly on clinical reasoning, expert opinion or non-comparative data. Discuss the uncertainty and track outcomes prospectively.', limited(d)) +
      section('pw-questions', 'Questions for consensus', 'Every decision this pathway still needs the programme to make. Each opens where it is set out once, with source positions, the proposed approach and the decision record<span data-doc-note>; the same questions are in the Word files under <b>Documents</b> (top right)</span>.', questions(d)) +
      section('pw-team', 'Team responsibilities and quality monitoring', 'Decision owners, the team and the quality measures written in the protocols. They need local approval and rest on operational consensus, not comparative treatment trials.', team(d)) +
      section('pw-evidence', 'Evidence library', `Every source behind the pathway — policy, review guidance, clinical recommendations and studies — each with a one-line summary, a link into the TMC library resolver and what it can and cannot show (${d.sources.length} sources).`, evidence(d));
    box.querySelectorAll('.pw-toggle').forEach(btn => btn.addEventListener('click', () => {
      const body = box.querySelector('#' + btn.getAttribute('aria-controls')); fold(btn, body.hidden);
    }));
    box.querySelector('#pw-ev-groups').addEventListener('click', e => {
      const b = e.target.closest('.tab'); if (!b) return;
      evGroup = b.dataset.group; box.querySelectorAll('#pw-ev-groups .tab').forEach(x => x.setAttribute('aria-selected', String(x === b))); renderEv(box);
    });
    box.querySelector('#pw-ev-search').addEventListener('input', e => { evQuery = e.target.value; renderEv(box); });
    box.querySelector('#pw-ev-search').value = evQuery;
    box.querySelectorAll('#pw-ev-groups .tab').forEach(x => x.setAttribute('aria-selected', String(x.dataset.group === evGroup)));
    renderEv(box);
    return box;
  }
  function fold(btn, open) {
    const body = document.getElementById(btn.getAttribute('aria-controls')) || btn.closest('.pw-sec').querySelector('.pw-body');
    body.hidden = !open; btn.textContent = open ? 'Hide' : 'Show'; btn.setAttribute('aria-expanded', String(open));
  }

  let data = null, pending = null;
  const place = () => {
    if (!data) return;
    const main = document.querySelector('#app main.wrap');
    const current = document.getElementById('pathway-closing');
    if (!main || !VIEWS.has(document.body.dataset.pathwayView || 'pathway')) { if (current) current.remove(); return; }
    if (!(current && main.contains(current))) { if (current) current.remove(); main.append(build(data)); }
    if (pending) { const id = pending; pending = null; open(id); }
  };
  /* Open one closing section and bring it into view: the tab and right-column link "Evidence library" and #evidence. */
  function open(id) {
    const sec = document.getElementById(id);
    if (!sec) { pending = id; place(); return; }
    fold(sec.querySelector('.pw-toggle'), true);
    requestAnimationFrame(() => sec.scrollIntoView({block: 'start'}));
  }
  window.PathwaySections = {open};
  if (!window.RoadmapEvidence) {
    const ev = document.createElement('script'); ev.async = false; ev.src = new URL('assets/roadmap-evidence.js?v=20261030-docs2', root); document.head.append(ev);
    const evCss = document.createElement('link'); evCss.rel = 'stylesheet'; evCss.href = new URL('assets/roadmap-evidence.css?v=20261031-ui1', root); document.head.append(evCss);
    ev.addEventListener('load', () => { const box = document.getElementById('pathway-closing'); if (box) renderEv(box); });
  }
  fetch(new URL('transplant/assets/pathway-sections.json?v=20261030-docs2', root)).then(r => r.ok ? r.json() : null).then(j => {
    data = j && j.pathways[slug];
    if (!data) return;
    const app = document.getElementById('app');
    const start = () => { if (location.hash === '#evidence') pending = pending || 'pw-evidence'; place(); if (app) new MutationObserver(place).observe(app, {childList: true}); new MutationObserver(place).observe(document.body, {attributes: true, attributeFilter: ['data-pathway-view']}); };
    document.readyState === 'loading' ? document.addEventListener('DOMContentLoaded', start, {once: true}) : start();
  }).catch(() => {});
})();
