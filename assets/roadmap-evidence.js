/* One evidence card per source. Clinical categories, never revision batches.
   Every card carries a one-line summary (30 October 2026): a PubMed paper's compact study line (design and
   population, main result; window.CompactEvidenceData.studies), otherwise the source's line in
   CompactEvidenceData.nonpm[<roadmap>][<key>].s (tools/source_summaries.json), or row.summary when the caller
   supplies it (the transplant pathway libraries). Cards drawn before the data loads are filled on window load. */
(() => {
  'use strict';
  const esc = value => String(value ?? '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  const data = () => JSON.parse(document.getElementById('roadmap-evidence-data')?.textContent || '{"papers":[]}');
  let revealedHash = null;
  window.addEventListener('hashchange', () => { revealedHash = null; });
  const doi = row => (row.doi || (String(row.url || '') + ' ' + row.cit).match(/10\.\d{4,9}\/[^\s<>]+/i)?.[0] || '').replace(/[.,;]+$/, '').toLowerCase();
  const labels = {'24646562':'HAI conversion study','27566258':'HAI refractory disease','39565488':'HAI program outcomes',
    '39962001':'HAI program requirements','36346892':'HAI surgical toolkit','37210451':'Transplant after HAI',
    '24154839':'HAI–bevacizumab toxicity','41082695':'PUMP-2','42331230':'HAI pooled trials','pump2026':'Dutch PUMP (conference abstract)'};
  const category = row => {
    if (/^Liver-directed \(/.test(row.group || '')) return 'Liver-directed';
    if (!/^HAI (evidence|library access|randomized conference results)/.test(row.group || '')) return row.group;
    const id = String(row.id).replace(/^tmc/, '');
    return id === '37210451' ? 'Transplant' : id === '39962001' ? 'Guidelines & policy' : 'Liver-directed';
  };
  function merge(rows) {
    for (const row of rows) {
      row.group = category(row);
      if (labels[row.id]) row.tag = labels[row.id];
    }
    // Old TMC-only records are access links to a paper, not additional papers.
    for (let i = rows.length - 1; i >= 0; i--) {
      const row = rows[i];
      if (!/^tmc/.test(row.id)) continue;
      const target = rows.find(r => r.id === row.id.replace(/^tmc/, ''));
      if (!target) continue;
      target.access = [...new Map([...(target.access || []), {label:'TMC alternate access', url:row.url}].filter(x=>x.url).map(x=>[x.url,x])).values()];
      target.aliases = [...new Set([...(target.aliases || []), row.id])];
      rows.splice(i, 1);
    }
    // Sources the roadmap's Word document cites that the page data lacks (assets/document-references.js).
    const docs = ((typeof window !== 'undefined' && window.DocumentReferences) || {})[page()] || [];
    for (const doc of docs) {
      if (rows.some(r => r.id === doc.id || (doc.pmid && r.pmid === doc.pmid))) continue;
      rows.push({...doc, appraisal:{cited:doc.cited}});
    }
    for (const paper of data().papers) {
      let row = rows.find(r => r.pmid === paper.pmid || (doi(r) && doi(r) === doi(paper)));
      if (!row) { row = {...paper, id:paper.pmid || paper.id}; rows.push(row); }
      row.aliases = [...new Set([...(row.aliases || []), paper.id])];
      row.appraisal = paper.appraisal;
      row.design = paper.design;
      row.doi = paper.doi;
      row.depot = paper.depot;
      row.access = [...new Map([...(row.access || []), ...(paper.access || [])].map(x=>[x.url,x])).values()];
    }
    return rows;
  }
  function critique(row, critiques) { return critiques[row.pmid] || critiques[row.id] || null; }
  const page = () => { try { const parts = location.pathname.split('/').filter(x => x && !/\.html?$/.test(x)); return parts[parts.length - 1] || ''; } catch { return ''; } };
  const ids = row => [row.pmid, row.id, ...(row.aliases || [])].filter(Boolean).map(String);
  function lookup(list) {
    const d = (typeof window !== 'undefined' && window.CompactEvidenceData) || null;
    if (!d) return null;
    for (const id of list) { const s = d.studies[id.replace(/^tmc/, '')]; if (s && s.r) return {lead:s.a || s.d || '', text:s.r}; }
    const nonpm = (d.nonpm || {})[page()] || {};
    for (const id of list) if (nonpm[id] && nonpm[id].s) return {lead:'', text:nonpm[id].s};
    return {lead:'', text:''};
  }
  function summary(row) { return row.summary || lookup(ids(row)); }
  const summaryHtml = s => s.lead ? `<b>${esc(s.lead)}.</b> ${esc(s.text)}` : esc(s.text);
  function summaryLine(row) {
    const s = summary(row);
    if (!s) return `<p class="evsum" data-ev-sum="${esc(ids(row).join(' '))}" hidden></p>`;
    return s.text ? `<p class="evsum">${summaryHtml(s)}</p>` : '';
  }
  function fill() {
    document.querySelectorAll('[data-ev-sum]').forEach(p => {
      const s = lookup(p.dataset.evSum.split(' '));
      if (!s) return;
      p.removeAttribute('data-ev-sum');
      if (s.text) { p.innerHTML = summaryHtml(s); p.hidden = false; } else p.remove();
    });
  }
  if (typeof window !== 'undefined') window.addEventListener('load', fill);
  function text(row, critiques) {
    const c = critique(row, critiques), s = summary(row);
    return [row.doi, row.pmid, row.design, s?.lead, s?.text, ...(row.aliases || []), ...Object.values(row.appraisal || {}),
      ...(c?.limitations || []), ...(c?.critique || []), c?.n, c?.bottom_line, c?.funding].filter(Boolean).join(' ');
  }
  function render(row, critiques) {
    const links = [];
    if (row.pmid) {
      links.push({label:'TMC full text',url:`https://libkey.io/libraries/480/pmid/${row.pmid}`});
      links.push({label:`PubMed ${row.pmid}`,url:`https://pubmed.ncbi.nlm.nih.gov/${row.pmid}/`});
    } else if (row.url) links.push({label:'Source',url:row.url});
    if (row.doi) links.push({label:'Publisher',url:`https://doi.org/${row.doi}`});
    links.push(...(row.access || []));
    const access = [...new Map(links.map(x=>[x.url,x])).values()].map(x=>{
      const label = x.url.startsWith('https://doi.org/') ? 'Publisher' : /libkey.io\/libraries\/480\/10\./.test(x.url) ? 'TMC DOI access' : x.label;
      return `<a class="lnk" href="${esc(x.url)}" target="_blank" rel="noopener">${esc(label)}</a>`;
    }).join('');
    const depot = row.depot === undefined ? '' : `<span class="chip${row.depot ? '' : ' warn'}" style="font-size:11px">${row.depot ? 'In depot' : 'To download'}</span>`;
    const c = critique(row, critiques), a = row.appraisal;
    const paragraphs = [];
    if (row.design) paragraphs.push(`<p><b>Study design.</b> ${esc(row.design)}</p>`);
    if (a) for (const [key,label] of [['note','Pathway note'],['cited','Cited in'],['scope','Design and population'],['application','Application'],['population','Population'],['results','Results'],['limitations','Limits of this evidence'],['locator','Source location']]) {
      if (a[key]) paragraphs.push(`<p><b>${label}.</b> ${esc(a[key])}</p>`);
    }
    if (c) {
      if (c.n) paragraphs.push(`<p><b>Population.</b> ${esc(c.n)}</p>`);
      if (c.bottom_line) paragraphs.push(`<p><b>Bottom line.</b> ${esc(c.bottom_line)}</p>`);
      if (c.funding) paragraphs.push(`<p><b>Funding.</b> ${esc(c.funding)}</p>`);
    }
    const list = values => (values || []).map(v=>`<li>${esc(v)}</li>`).join('') || '<li>None recorded in this appraisal.</li>';
    const oldCritique = c ? `<div class="evcritin"><div class="lim"><h5>Limitations the authors state</h5><ul>${list(c.limitations)}</ul></div><div class="crit"><h5>What they do not say</h5><ul>${list(c.critique)}</ul></div></div>` : '';
    const disclosure = (a || c) ? `<details class="evcrit"><summary>How far this one goes</summary><div class="evmeta">${paragraphs.join('')}</div>${oldCritique}</details>` : '';
    const aliases = (row.aliases || []).flatMap(id=>[id,`ev-${id}`]).filter(id=>id!==`ev-${row.id}`).map(id=>`<span id="${esc(id)}" class="evidence-anchor" aria-hidden="true"></span>`).join('');
    const flag = row.flag ? `<span class="chip evflag">${esc(row.flag)}</span>` : '';
    return `<div class="ev" id="ev-${esc(row.id)}">${aliases}<div class="evtag">${esc(row.tag)}</div><div class="evcit">${esc(row.cit)}${summaryLine(row)}</div><div class="evlinks">${flag}${depot}${access || '<span class="chip">Internal document</span>'}</div>${disclosure}</div>`;
  }
  function reveal() {
    let id; try { id = decodeURIComponent(location.hash.slice(1)); } catch { return; }
    const target = document.getElementById(id);
    if (!target || (!target.closest('#evidence') && id !== 'evidence')) return;
    const body = document.getElementById('evBody'); if (body) body.hidden = false;
    const toggle = document.querySelector('[data-fold="evBody"]');
    if (toggle) { toggle.textContent = 'Hide'; toggle.setAttribute('aria-expanded','true'); }
    const card = target.closest('.ev');
    if (card) { card.classList.add('hit'); const detail = card.querySelector('.evcrit'); if(detail) detail.open = true; }
    if (target.tagName === 'DETAILS') target.open = true;
    if (revealedHash !== id) {
      revealedHash = id;
      requestAnimationFrame(() => (card || target).scrollIntoView({block:card ? 'center' : 'start'}));
    }
  }
  // A link to #evidence (the right-column "Evidence library" link) opens the folded library, as the section menu does.
  if (typeof document !== 'undefined' && document.addEventListener) document.addEventListener('click', e => {
    if (!e.target.closest || !e.target.closest('a[href="#evidence"]') || !document.getElementById('evBody')) return;
    revealedHash = null; setTimeout(reveal, 0);
  });
  window.RoadmapEvidence = {merge, row:render, text, reveal, summary, fill};
})();
