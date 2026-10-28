/* Compact treatment and evidence presentation (matrix-style rebuild, 27 October 2026; evidence lines 27 October 2026).
   Presentation only. Existing nodes are moved, never rewritten: clinical text, grades,
   matching, routing, calculators and high-risk status are unchanged.
   Every cited study is shown as one line in the format of the liver-directed matrix:
   name · PMID · arms · main result · limitation. A result reported in an option's own text for
   that study (explicit option mapping) is shown in place of the study-level line. Study-level
   lines are each study's own result in its own population, not a claim about the option.
   Non-PMID sources show their category and citation. */
(() => {
  'use strict';
  const DATA = window.CompactEvidenceData || {studies: {}};
  const plain = s => String(s || '').replace(/\s+/g, ' ').trim();
  const make = (tag, cls, text) => { const n = document.createElement(tag); if (cls) n.className = cls; if (text !== undefined) n.textContent = text; return n; };
  const isPm = k => /^\d{6,9}$/.test(k || '');
  let uid = 0, queued = false;
  const nextId = prefix => `${prefix}-${++uid}`;
  // Page slug: roadmap name, or 'transplant' / 'systemic' / 'lrt'.
  const slug = (() => { const parts = location.pathname.split('/').filter(Boolean); const i = parts.indexOf('mh-liver-pathways'); return parts[i + 1] || parts[0] || ''; })();
  const NONPM = (DATA.nonpm || {})[slug] || {};

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

  /* ---------- Evidence lines ---------- */
  function pmChip(id) {
    const a = make('a', 'ct-pm', id);
    a.href = `https://pubmed.ncbi.nlm.nih.gov/${id}/`; a.target = '_blank'; a.rel = 'noopener';
    a.setAttribute('aria-label', `PubMed ${id}`);
    return a;
  }
  function sourceLink(url) {
    const a = make('a', 'ct-ev-link', 'Source ↗');
    a.href = url; a.target = '_blank'; a.rel = 'noopener';
    return a;
  }
  // One line per source. `tied` is a result this option's own text reports for the study.
  function sourceRow({key, label, chip}, tied) {
    const li = make('li', 'ct-ev-row');
    const head = make('span', 'ct-ev-head');
    const name = make('button', 'ct-ev-label', label);
    name.type = 'button';
    name.title = 'Open this source in the evidence library';
    name.addEventListener('click', () => chip.click());
    head.append(name);
    li.append(head);
    if (isPm(key)) {
      const s = DATA.studies[key] || {};
      head.append(pmChip(key));
      if (s.a) head.append(make('span', 'ct-ev-arms', s.a));
      if (s.d && !(s.a || '').startsWith(s.d)) head.append(make('span', 'ct-ev-design', s.d));
      const result = tied ? tied.r : s.r, caution = tied ? tied.c : s.c;
      if (result) li.append(make('span', 'ct-ev-result', result));
      if (caution) li.append(make('span', 'ct-ev-caution', caution));
      li.classList.add(tied ? 'ct-ev-tied' : 'ct-ev-study');
    } else {
      const n = NONPM[key];
      li.classList.add('ct-ev-src');
      if (n) {
        head.append(make('span', 'ct-ev-kind', n.c));
        if (n.u) head.append(sourceLink(n.u));
        li.append(make('span', 'ct-ev-result ct-ev-cite', n.x));
      }
    }
    return li;
  }
  function refsFrom(nodes) {
    const seen = new Set(), refs = [];
    for (const chip of nodes) {
      const key = chip.dataset.ref;
      if (!key || seen.has(key)) continue;
      seen.add(key);
      refs.push({key, label: plain(chip.textContent), chip});
    }
    return refs;
  }
  function evidenceRows(refs, option, lead, skip = new Set()) {
    const list = make('ul', 'ct-ev');
    // Option-specific numbers come only from the explicit option mapping.
    const mapped = option && lead.startsWith(option.g) ? option.rows : [];
    const byStudy = new Map(mapped.map(r => [r.p, r]));
    let tied = 0;
    for (const ref of refs) {
      const row = byStudy.get(ref.key);
      if (!row && skip.has(ref.key)) continue;
      if (row) tied++;
      list.append(sourceRow(ref, row));
    }
    // Option-tied rows first, as in the LRT matrix; citation order is otherwise kept.
    [...list.children].filter(li => li.classList.contains('ct-ev-tied')).reverse().forEach(li => list.prepend(li));
    return {list, tied};
  }
  /* Reviewed links to this page's own treatment references (liver-directed reference or systemic matrix).
     Copied verbatim at build time; shown as source-study evidence for the modality or regimen. */
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
  /* The discussion text of an "Explanation and evidence" pop-up is shown in the panel instead.
     Its source chips stay in place (hidden) as the click targets for the evidence lines. */
  function takeDiscussion(unit) {
    const body = unit.querySelector('.ci-body');
    const parts = [];
    if (body) for (const child of [...body.children]) {
      if (child.matches('.ct-ev')) continue;
      const probe = child.cloneNode(true);
      probe.querySelectorAll('.refs,.refchip,.ct-ev,.ct-chip-meta').forEach(n => n.remove());
      if (plain(probe.textContent)) parts.push(child);
    }
    unit.classList.add('ct-emptied');
    return parts;
  }
  function discussionBlock(parts, label) {
    const d = make('div', 'ct-discussion');
    d.append(make('p', 'ct-ref-label', label), ...parts);
    return d;
  }

  /* ---------- Roadmap treatment options ---------- */
  function optionScope(host, tc) {
    const clone = host.cloneNode(true);
    const marker = tc.dataset.ctKey;
    clone.querySelectorAll('.opt').forEach(opt => { if (!opt.querySelector(`[data-ct-key="${marker}"]`)) opt.remove(); });
    clone.querySelectorAll('.refs,.refchip,.ct-peers,.ct-ev,.ct-ev-note,.ct-chip-meta,.ct-ref-label').forEach(n => n.remove());
    // Text nodes joined with spaces, so adjacent blocks never run together.
    const parts = [], walker = document.createTreeWalker(clone, NodeFilter.SHOW_TEXT);
    while (walker.nextNode()) parts.push(walker.currentNode.data);
    return plain(parts.join(' '));
  }
  // Stable key for an option: page slug plus a hash of its visible statement.
  function optionLead(host, tc) {
    const clone = host.cloneNode(true);
    clone.querySelectorAll('.ci-unit,.ci-treatment-criteria,.opts,.recmeta,.ct-peers,.grade,.optn,.ct-chip-meta,.ct-panels').forEach(n => n.remove());
    return plain(clone.textContent);
  }
  function hash(text) { let h = 5381; for (let i = 0; i < text.length; i++) h = ((h << 5) + h + text.charCodeAt(i)) >>> 0; return h.toString(36); }
  function optionKey(host, tc) { const lead = optionLead(host, tc); return {key: `${slug}:${hash(lead)}`, lead}; }
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
    const refs = refsFrom(unit ? unit.querySelectorAll('.refchip[data-ref]') : []);
    if (unit || refs.length) {
      const panel = make('details', 'ct-panel ct-evidence');
      panel.append(make('summary', '', 'Evidence & sources'));
      const groups = (DATA.references || {})[key] || [];
      // A source shown with its result in a linked reference group is not listed again.
      const inGroups = new Set(groups.flatMap(g => g.rows.flatMap(r => r[1])));
      const chipFor = new Map(refs.map(r => [r.key, r.chip]));
      if (refs.length) {
        const {list} = evidenceRows(refs, (DATA.options || {})[key], lead, inGroups);
        if (list.children.length) panel.append(list);
      }
      for (const group of groups) panel.append(referenceGroup(group, chipFor));
      if (unit) {
        const parts = takeDiscussion(unit);
        if (parts.length) panel.append(discussionBlock(parts, 'Discussion'));
        panel.append(unit);
      }
      tc.append(panel);
      const sourceCount = new Set([...refs.map(r => r.key), ...inGroups]).size;
      const b = peerButton('Evidence & sources', panel, sourceCount ? String(sourceCount) : '');
      b.classList.add('ct-peer-ev');
      row.append(b);
    }
    tc.before(row);
  }
  /* Items without indication/contraindication blocks (mostly "Avoid" items): the same control row,
     with the explanation and the evidence lines as peer panels. */
  function enhanceBare(rec) {
    if (rec.dataset.ctReady || rec.querySelector('.ci-treatment-criteria')) return;
    // Wait until the shared explanation layer has finished with this item.
    if (rec.querySelector(':scope>details:not([data-context-ready]),:scope>.recnote')) return;
    const units = [...rec.querySelectorAll(':scope>.ci-unit')].filter(u => {
      const label = plain(u.querySelector('.ci-label')?.textContent);
      return /evidence|sources|explanation/i.test(label) && !/^full explanation/i.test(label);
    });
    if (!units.length) return;
    rec.dataset.ctReady = 'true';
    const refs = refsFrom(units.flatMap(u => [...u.querySelectorAll('.refchip[data-ref]')]));
    const parts = units.flatMap(takeDiscussion);
    const row = make('div', 'ct-peers');
    row.setAttribute('role', 'group');
    row.setAttribute('aria-label', 'Details for this item');
    const holder = make('div', 'ct-panels ct-bare');
    units[0].before(row, holder);
    if (parts.length) {
      const avoid = !!rec.closest('.rf-cautions');
      const why = make('details', 'ct-panel ct-why');
      why.append(make('summary', '', avoid ? 'Why' : 'Explanation'));
      const body = make('div', 'ct-why-body');
      body.append(...parts);
      why.append(body);
      holder.append(why);
      const b = peerButton(avoid ? 'Why' : 'Explanation', why);
      b.classList.add('ct-peer-contra');
      row.append(b);
    }
    if (refs.length) {
      const panel = make('details', 'ct-panel ct-evidence');
      panel.append(make('summary', '', 'Evidence & sources'));
      panel.append(evidenceRows(refs, null, '').list);
      holder.append(panel);
      const b = peerButton('Evidence & sources', panel, String(refs.length));
      b.classList.add('ct-peer-ev');
      row.append(b);
    }
    units.forEach(u => holder.append(u));
  }

  /* ---------- Source chips elsewhere: a PMID and a short description next to every name ---------- */
  function chipMeta(chip, withArms) {
    if (chip.dataset.ctMeta) return;
    chip.dataset.ctMeta = 'true';
    const key = chip.dataset.ref;
    const meta = make('span', 'ct-chip-meta');
    if (isPm(key)) {
      const s = DATA.studies[key] || {};
      meta.append(pmChip(key));
      const what = withArms ? s.a : (s.d || s.a);
      if (what) meta.append(make('span', 'ct-chip-what', what));
      if (s.r) chip.title = [s.a, s.r, s.c && 'Limitation: ' + s.c].filter(Boolean).join(' — ');
    } else if (NONPM[key]) {
      meta.append(make('span', 'ct-chip-what', NONPM[key].c));
      chip.title = NONPM[key].x;
    }
    if (meta.childElementCount) chip.after(meta);
  }
  // A list of source chips becomes a list of evidence lines; the chips stay as click targets.
  function enhanceRefList(box) {
    if (box.dataset.ctReady) return;
    const chips = [...box.querySelectorAll(':scope>.refchip[data-ref]')];
    if (!chips.length) return;
    box.dataset.ctReady = 'true';
    const {list} = evidenceRows(refsFrom(chips), null, '');
    list.classList.add('ct-ev-list');
    box.classList.add('ct-refs-listed');
    box.after(list);
  }
  // Transplant pathways: citation buttons get their source type and PMID.
  let protocolSources = null;
  function sources() {
    if (protocolSources) return protocolSources;
    const node = document.getElementById('protocol-data');
    if (!node) return {};
    try { protocolSources = JSON.parse(node.textContent).sources || {}; } catch { protocolSources = {}; }
    return protocolSources;
  }
  function citeMeta(cite) {
    if (cite.dataset.ctMeta) return;
    const s = sources()[cite.dataset.ref];
    if (!s) return;
    cite.dataset.ctMeta = 'true';
    const meta = make('span', 'ct-chip-meta');
    if (s.kind) meta.append(make('span', 'ct-chip-what', s.kind));
    if (isPm(String(s.pmid || ''))) meta.append(pmChip(String(s.pmid)));
    const study = DATA.studies[String(s.pmid || '')];
    cite.title = study?.r ? [study.a, study.r].filter(Boolean).join(' — ') : (s.note || s.title || '');
    if (meta.childElementCount) cite.after(meta);
  }

  // Systemic matrix source lists and library: the study line under each citation.
  function sourceLine(node) {
    if (node.dataset.ctReady) return;
    const id = ((node.querySelector('a[href*="pubmed.ncbi.nlm.nih.gov"]') || {}).href || '').match(/(\d{6,9})/);
    const s = id && DATA.studies[id[1]];
    node.dataset.ctReady = 'true';
    if (!s || !s.r) return;
    const line = make('div', 'ct-src-line');
    const head = make('span', 'ct-ev-head');
    if (s.a) head.append(make('span', 'ct-ev-arms', s.a));
    if (s.d && !(s.a || '').startsWith(s.d)) head.append(make('span', 'ct-ev-design', s.d));
    if (head.childElementCount) line.append(head);
    line.append(make('span', 'ct-ev-result', s.r));
    if (s.c) line.append(make('span', 'ct-ev-caution', s.c));
    node.append(line);
  }

  // Transplant decision aids list sources as links: the same type and PMID beside each.
  let byUrl = null;
  function assistantSource(span) {
    if (span.dataset.ctMeta) return;
    span.dataset.ctMeta = 'true';
    if (!byUrl) byUrl = new Map(Object.values(sources()).map(s => [s.url, s]));
    const link = span.querySelector(':scope>a');
    const s = link && byUrl.get(link.getAttribute('href'));
    if (!s) return;
    const meta = make('span', 'ct-chip-meta');
    if (s.kind) meta.append(make('span', 'ct-chip-what', s.kind));
    if (isPm(String(s.pmid || ''))) meta.append(pmChip(String(s.pmid)));
    link.after(meta);
  }

  /* ---------- Revision history out of the clinical text ----------
     Version-history remarks are hidden where they occur and listed, verbatim, in a "Revision notes"
     disclosure beside the change log. Exact strings only; nothing else is altered. */
  const REVISION = {
    hcc: [
      'v0.8 removed the requirement that all three curative options be documented unsuitable first.',
      'v0.2 graded this A.',
      'v0.2 required biopsy for all tumour in vein; this is narrowed.',
      'v0.2 said microwave is “often favoured operationally”, which is accurate — but that is a workflow preference, not an outcome-based one.',
      'v0.2 omitted the “at least one lesion >3 cm” qualifier in the 2–3 lesion group, which would have incorrectly routed T2 disease into the downstaging pool.',
      'v0.2\'s figure graded this step A; that is corrected.',
      'v0.2 listed them in an order that implies a hierarchy; that implication is removed.',
      'v0.8 withdrew the fixed rule in favour of reassessment after each session.',
      'v0.2 stated that EMERALD-1 and LEAP-012 “improved progression-free survival, with higher toxicity and evolving overall-survival and regulatory context”, and deferred a decision. That framing is too permissive.',
      'v0.8 withdrew the fixed two-session rule: ',
      {callout: 'Corrected in v0.8 (HCC-03).', text: 'Corrected in v0.8 (HCC-03). Earlier versions said a safety signal of unexplained early deaths in EMERALD-1 had been raised in correspondence. That sentence was removed because no source in the depot supports it. Re-add it only with the correspondence citation.'}
    ],
    chcca: ['A previous version of this page quoted a within-series breakdown of recurrences by differentiation grade from that paper; it could not be verified from any source obtained and has been removed.'],
    nelm: ['This closes a gap the earlier draft acknowledged.'],
    pdac: ['The page previously quoted the placebo-arm median as 16.1 months; the published figure is 18.1.']
  }[slug] || [];
  const FRAGMENTS = REVISION.filter(f => typeof f === 'string');
  const CALLOUTS = REVISION.filter(f => f.callout);
  const logged = new Map();
  let loggedShown = 0;
  function hideRevision() {
    if (!REVISION.length) return;
    // The log lists every curated remark for the page, whichever decision is open.
    if (!logged.size) { FRAGMENTS.forEach(f => logged.set(f, f.trim())); CALLOUTS.forEach(c => logged.set(c.callout, c.text)); }
    const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT, {acceptNode: n =>
      n.data.length > 12 && /v0\.\d|previous|earlier draft/.test(n.data) && !n.parentElement.closest('script,style,.ct-rev,.ct-revision-log,title')
        ? NodeFilter.FILTER_ACCEPT : NodeFilter.FILTER_REJECT});
    const hits = [];
    while (walker.nextNode()) hits.push(walker.currentNode);
    for (let node of hits) {
      for (const f of FRAGMENTS) {
        const i = node.data.indexOf(f);
        if (i < 0) continue;
        const rest = node.splitText(i);
        const after = rest.splitText(f.length);
        const span = make('span', 'ct-rev');
        rest.before(span); span.append(rest);
        // A remark that opens a sentence leaves the next word to start it.
        if (/: $/.test(f) && after.data) span.parentElement.classList.add('ct-rev-lead');
        node = after;
      }
      for (const c of CALLOUTS) {
        if (!node.data.includes(c.callout)) continue;
        const box = node.parentElement.closest('.callout');
        if (box && plain(box.textContent) === c.text) box.classList.add('ct-rev');
      }
    }
    if (logged.size !== loggedShown) revisionLog();
  }
  function revisionLog() {
    let log = document.querySelector('.ct-revision-log');
    if (!log) {
      log = make('details', 'ct-revision-log');
      log.append(make('summary', ''), make('p', 'ct-revision-intro', 'Version-history remarks moved out of the clinical text, wording unchanged. They describe how earlier drafts differed; they are not clinical guidance.'), make('ul', ''));
      const wrap = document.querySelector('body>.wrap'), footer = document.querySelector('footer.portal-change-log');
      if (wrap) wrap.append(log); else if (footer) footer.before(log); else document.body.append(log);
    }
    const ul = log.querySelector('ul');
    ul.textContent = '';
    for (const text of logged.values()) ul.append(make('li', '', text));
    log.querySelector('summary').textContent = `Revision notes (${logged.size})`;
    loggedShown = logged.size;
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

  /* Reading mode ("Show explanations") also opens the explanation and evidence panels it would otherwise hide. */
  document.addEventListener('click', ev => {
    const b = ev.target.closest('[data-context-reading]');
    if (!b) return;
    requestAnimationFrame(() => {
      const on = b.getAttribute('aria-pressed') === 'true';
      document.querySelectorAll('details.ct-evidence,details.ct-why').forEach(d => { d.open = on; });
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
    document.querySelectorAll('.rf-option-group .rec:not([data-ct-ready])').forEach(enhanceBare);
    document.querySelectorAll('article.hr-study:not([data-ct-ready])').forEach(enhanceStudy);
    document.querySelectorAll('.hr-protocol:not([data-ct-ready])').forEach(enhanceProtocol);
    // Remaining chip lists and single chips, outside the option panels (which list sources themselves).
    document.querySelectorAll('.refs:not([data-ct-ready])').forEach(box => {
      if (!box.closest('.ct-panels,.ct-emptied,.ct-discussion,.rf-option-group .rec .ci-unit')) enhanceRefList(box);
    });
    document.querySelectorAll('.evline>.refchip[data-ref]:not([data-ct-meta])').forEach(c => chipMeta(c, true));
    document.querySelectorAll('.refchip[data-ref]:not([data-ct-meta])').forEach(c => {
      if (!c.closest('.refs,.evline,.ct-emptied,.ct-ev')) chipMeta(c, false);
    });
    document.querySelectorAll('.cite[data-ref]:not([data-ct-meta])').forEach(citeMeta);
    document.querySelectorAll('.assistant-evidence>span:not([data-ct-meta])').forEach(assistantSource);
    document.querySelectorAll('ul.sources>li:not([data-ct-ready]),.library-entry .paper-body>p:not([data-ct-ready])').forEach(sourceLine);
    hideRevision();
  }
  const schedule = () => { if (!queued) { queued = true; requestAnimationFrame(scan); } };
  new MutationObserver(records => { if (records.some(r => r.type === 'childList' && r.addedNodes.length)) schedule(); })
    .observe(document.documentElement, {childList: true, subtree: true});
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', scan); else scan();
  window.CompactTreatment = {scan, optionText: tc => optionScope(tc.parentElement, tc), optionLead: tc => optionLead(tc.parentElement, tc)};
})();
