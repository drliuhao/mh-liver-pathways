/* Transplant pathways in the cancer roadmap's visual language (28 October 2026). Presentation only.
   - The decision strip shows the pathway's phases and numbered decisions.
   - Each decision is one card: question, context, then the three columns.
   - The middle column reads in clinical order: record the finding, the criteria for this decision,
     the result with its next step, the reasons to reassess beside it, other possible results,
     then outcome evidence.
   Existing nodes are moved, never rewritten; ids, handlers, routing and wording are unchanged. */
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

  function scan() {
    queued = false;
    phases();
    document.querySelectorAll('.decision.dw-protocol').forEach(regroup);
  }
  new MutationObserver(records => {
    if (!queued && records.some(r => r.type === 'childList')) { queued = true; requestAnimationFrame(scan); }
  }).observe(document.body, {childList: true, subtree: true});
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', scan); else scan();
})();
