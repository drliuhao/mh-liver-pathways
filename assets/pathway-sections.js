/* Closing sections of each transplant pathway page, matching the roadmaps (29 October 2026, Analyst B):
   Practice choices with limited evidence · Questions for consensus · Team responsibilities and quality monitoring ·
   Evidence library. Presentation only. Data: transplant/assets/pathway-sections.json (tools/build_pathway_sections.py).
   Questions for consensus is an index: each question opens where it is set out once (the meeting record or the
   high-risk view), and source chips open the page's own source dialog. Shown on the pathway and high-risk views. */
(() => {
  'use strict';
  const root = new URL('../', document.currentScript.src);
  const path = location.pathname.slice(root.pathname.length).split('/').filter(Boolean);
  const SLUGS = ['hcc', 'pcca', 'icca', 'crlm', 'nelm', 'hehe', 'hca'];
  if (path[0] !== 'transplant' || !SLUGS.includes(path[1]) || path.length > 2) return;
  const slug = path[1];
  const VIEWS = new Set(['pathway', 'high-risk']);
  const esc = s => String(s ?? '').replace(/[&<>"']/g, c => ({'&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;'}[c]));
  const css = document.createElement('link'); css.rel = 'stylesheet'; css.href = new URL('assets/pathway-sections.css?v=20261029-nav1', root); document.head.append(css);

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
    return `<div class="pw-actions"><a href="#evidence">Search all sources for this pathway →</a><a href="${esc(new URL('evidence-libraries/#standard_' + slug, root).href)}">Standard pathway library →</a><a href="${esc(new URL('evidence-libraries/#high_risk_' + slug, root).href)}">High-risk pathway library →</a></div>
      <div class="pw-tablewrap"><table class="pw-table"><thead><tr><th style="width:44%">Source</th><th>Type</th><th style="width:18%">Access</th></tr></thead><tbody>${d.sources.map(s =>
      `<tr><td><b>${esc(s.short)}</b><small>${esc(s.title)}</small></td><td>${esc(s.kind)}</td><td>${s.dialog ? `<span class="pw-refs"><button type="button" class="cite" data-ref="${esc(s.key)}">Details & full text ↗</button></span>` : s.url ? `<span class="pw-refs"><a href="${esc(s.url)}" target="_blank" rel="noopener">${s.pmid ? 'PubMed' : 'Source'} ↗</a></span>` : ''}</td></tr>`).join('')}</tbody></table></div>`;
  }
  function build(d) {
    const box = document.createElement('div'); box.id = 'pathway-closing'; box.className = 'pw-closing';
    box.innerHTML =
      section('pw-limited', 'Practice choices with limited evidence', 'These practice choices in the pathway rest mainly on clinical reasoning, expert opinion or non-comparative data. Discuss the uncertainty and track outcomes prospectively.', limited(d)) +
      section('pw-questions', 'Questions for consensus', 'Every decision this pathway still needs the programme to make. Each opens where it is set out once, with source positions, the proposed approach and the decision record; the same questions are in the Word files under <b>Documents</b> (top right).', questions(d)) +
      section('pw-team', 'Team responsibilities and quality monitoring', 'Decision owners, the team and the quality measures written in the protocols. They need local approval and rest on operational consensus, not comparative treatment trials.', team(d)) +
      section('pw-evidence', 'Evidence library', `Every source behind the pathway — policy, review guidance, clinical recommendations and studies — with its details and full-text access (${d.sources.length} sources).`, evidence(d));
    box.querySelectorAll('.pw-toggle').forEach(btn => btn.addEventListener('click', () => {
      const body = document.getElementById(btn.getAttribute('aria-controls')); const open = body.hidden;
      body.hidden = !open; btn.textContent = open ? 'Hide' : 'Show'; btn.setAttribute('aria-expanded', String(open));
    }));
    return box;
  }

  let data = null;
  const place = () => {
    if (!data) return;
    const main = document.querySelector('#app main.wrap');
    const current = document.getElementById('pathway-closing');
    if (!main || !VIEWS.has(document.body.dataset.pathwayView || 'pathway')) { if (current) current.remove(); return; }
    if (current && main.contains(current)) return;
    if (current) current.remove();
    main.append(build(data));
  };
  fetch(new URL('transplant/assets/pathway-sections.json?v=20261029-nav1', root)).then(r => r.ok ? r.json() : null).then(j => {
    data = j && j.pathways[slug];
    if (!data) return;
    const app = document.getElementById('app');
    const start = () => { place(); if (app) new MutationObserver(place).observe(app, {childList: true}); new MutationObserver(place).observe(document.body, {attributes: true, attributeFilter: ['data-pathway-view']}); };
    document.readyState === 'loading' ? document.addEventListener('DOMContentLoaded', start, {once: true}) : start();
  }).catch(() => {});
})();
