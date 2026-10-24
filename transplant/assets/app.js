/* Shared, buildless renderer. No patient data entry, scoring, or persistent decisions. */
'use strict';
const DATA = JSON.parse(document.getElementById('protocol-data').textContent);
const app = document.getElementById('app');
const escapeHTML = s => String(s ?? '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const e = escapeHTML;
let active = DATA.pathway || null;
let view = DATA.mode === 'alignment' ? 'meeting' : 'pathway';
let stepIndex = 0;
let lastTrigger = null;
const refs = ids => (ids || []).map(id => `<button type="button" class="cite" data-ref="${e(id)}" aria-label="Evidence: ${e(DATA.sources[id].short)}">${e(DATA.sources[id].short)} ↗</button>`).join(' ');
const bullets = items => `<ul>${items.map(x=>`<li>${x.children?`<b>${e(x.text)}</b>`:e(x.text)} ${x.children?bullets(x.children):`<span class="citations">${refs(x.refs)}</span>`}</li>`).join('')}</ul>`;
const external = (url,label,cls='') => `<a class="${cls}" href="${e(url)}" target="_blank" rel="noopener">${e(label)} ↗</a>`;
const allRefs = p => {
  const ids = new Set();
  p.steps.forEach(s=>{s.orders.forEach(g=>g.items.forEach(x=>x.refs.forEach(r=>ids.add(r))));s.branches.forEach(b=>{b.criteria.forEach(x=>x.refs.forEach(r=>ids.add(r)));b.refs.forEach(r=>ids.add(r));});s.stops.forEach(x=>x.refs.forEach(r=>ids.add(r)));});
  p.issues.forEach(i=>i.comparisons.forEach(c=>ids.add(c.ref)));
  return [...ids];
};

function header() {
 return `<div class="draftbar">Clinical review draft <span>Not approved institutional policy · Not an automated eligibility tool.</span></div>
 <header class="top"><a class="brand" href="/mh-liver-pathways/transplant/">Memorial Hermann<span>Transplant oncology pathways</span></a>
 <nav aria-label="Tumor pathways">${DATA.index.map(p=>`<a href="/mh-liver-pathways/transplant/${p.slug}/" ${active?.slug===p.slug?'aria-current="page"':''}>${e(p.code)}</a>`).join('')}</nav>
 <a class="cancer-link" href="https://drliuhao.github.io/mh-liver-pathways/" target="_blank" rel="noopener">Cancer roadmaps ↗</a></header>`;
}

function footer() {
 return `<footer><b>Clinical suitability and allocation eligibility are separate decisions.</b> This draft supports, but does not replace, specialist judgment and the center’s full transplant evaluation. Proposed local decisions are not institutional approvals.<br><span>Language revised October 23, 2026; clinical source review October 17, 2026 · OPTN policies checked October 17, 2026 (effective October 1, 2026) · NLRB guidance: December 2025. Check current requirements when submitting an exception request.</span></footer>`;
}

function home() {
 app.innerHTML = header()+`<main class="wrap home"><div class="homehero"><div><p class="eyebrow">Diagnosis → selection → disease control → transplant</p><h1>Liver transplant assessment and treatment pathways</h1><p class="lead">Transplant oncology pathways with the information to collect, the results that change the route, and the evidence beside each decision.</p></div><div class="how"><b>How to use the pathways</b><ol><li>Choose the tumor and current decision.</li><li>Review the required tests and findings.</li><li>Follow the matching result branch.</li><li>Open evidence or an unresolved meeting question in context.</li></ol></div></div>
 <div class="searchbar"><label for="search">Find a pathway or clinical question</label><input id="search" type="search" placeholder="Try “LR-4”, “biopsy”, “CEA”, “nodes” or “unresectability”…" autocomplete="off"><p id="search-count" class="muted small" aria-live="polite">Seven disease-specific pathways · different step counts, one shared decision structure.</p></div>
 <section id="pathway-grid" class="pathway-grid" aria-label="Choose a pathway">${DATA.index.map(p=>`<article class="pathway-tile" data-slug="${p.slug}"><div class="tiletop"><span class="code">${e(p.code)}</span><span class="small muted">${p.steps.length} decisions</span></div><h2><a href="/mh-liver-pathways/transplant/${p.slug}/">${e(p.name)}</a></h2><span class="authority">${e(p.route)}</span><p>${e(p.entry)}</p><div class="tileflow">${e(p.steps[0].title)} <span>→</span> ${e(p.steps[p.steps.length-1].title)}</div><a class="tilego" href="/mh-liver-pathways/transplant/${p.slug}/">Open pathway <span>→</span></a></article>`).join('')}</section><section id="search-results" hidden aria-label="Matching decisions"></section>
 <section class="key"><div><span class="keyline go"></span><b>Proceed</b><p>Required results support the next decision.</p></div><div><span class="keyline hold"></span><b>Pause and clarify</b><p>Assign a clinician to resolve missing or uncertain information.</p></div><div><span class="keyline stop"></span><b>Stop and review</b><p>Check whether the finding requires a temporary pause, a different pathway, or exclusion from this transplant protocol.</p></div><div><span class="keyline discuss"></span><b>Meeting question</b><p>Compare sources and see the proposed local approach.</p></div></section></main>`+footer();
 document.getElementById('search').addEventListener('input', ev=>{
  const q=ev.target.value.trim().toLowerCase();
  const results=document.getElementById('search-results');
  document.getElementById('pathway-grid').hidden=!!q;
  results.hidden=!q;
  if(!q){document.getElementById('search-count').textContent='Seven disease-specific pathways · different step counts, one shared decision structure.';return;}
  const found=[];
  DATA.index.forEach(p=>{
   p.steps.forEach(s=>{if(JSON.stringify(s).toLowerCase().includes(q)||p.name.toLowerCase().includes(q)||p.code.toLowerCase()===q)found.push(`<a class="search-result" href="/mh-liver-pathways/transplant/${p.slug}/#${s.id}"><span class="tag">${e(p.code)} · pathway decision</span><b>${e(s.question)}</b><span>${e(s.title)} →</span></a>`);});
   p.issues.forEach(i=>{if((i.question+' '+i.proposal).toLowerCase().includes(q))found.push(`<a class="search-result" href="/mh-liver-pathways/transplant/alignment/${p.slug}/#${i.id}"><span class="tag amber">${e(p.code)} · meeting question</span><b>${e(i.question)}</b><span>Compare sources →</span></a>`);});
  });
  document.getElementById('search-count').textContent=`${found.length} matching decisions or meeting questions`;
  results.innerHTML=found.length?found.join(''):'<p class="empty">No match. Try a tumor name or a shorter clinical term.</p>';
 });
}

function pathwayShell() {
 app.innerHTML=header()+`<main class="wrap"><div class="pathhero"><div><a class="back" href="/mh-liver-pathways/transplant/">← All pathways</a><p class="eyebrow">${e(active.route)}</p><h1>${e(active.name)}</h1><p class="lead">${e(active.entry)}</p></div><div class="herolinks">${active.roadmap?external(active.roadmap,`${active.code} treatment roadmap`,'btn secondary'):external(DATA.sources['E-consensus'].pdf,'HEHE treatment consensus','btn secondary')}<a href="#meeting" class="plain-link" data-view="meeting">Protocol & meeting documents ↓</a></div></div>
 <div class="viewbar" role="tablist" aria-label="Pathway sections"><button role="tab" id="tab-pathway" data-view="pathway">Decision pathway</button><button role="tab" id="tab-meeting" data-view="meeting">Meeting record <span>${active.issues.length}</span></button><button role="tab" id="tab-evidence" data-view="evidence">Evidence library <span>${allRefs(active).length}</span></button><span class="viewnote">Browse the pathway · no patient status is saved</span></div>
 <div id="view"></div></main>`+footer();
 renderView();
}

function renderView(){
 document.querySelectorAll('[role="tab"]').forEach(t=>t.setAttribute('aria-selected',t.dataset.view===view?'true':'false'));
 const out=document.getElementById('view');
 out.setAttribute('role','tabpanel');out.setAttribute('aria-labelledby','tab-'+view);
 if(view==='pathway')out.innerHTML=renderStep();
 if(view==='meeting')out.innerHTML=renderMeeting();
 if(view==='evidence')out.innerHTML=renderEvidence();
 const strip=out.querySelector('.stepstrip');const selected=out.querySelector('.step-tab.active');
 if(strip&&selected&&strip.scrollWidth>strip.clientWidth)strip.scrollLeft=selected.offsetLeft-strip.offsetLeft-(strip.clientWidth-selected.offsetWidth)/2;
}

function renderStep(){
 const s=active.steps[stepIndex];
 return `<nav class="stepstrip" aria-label="${e(active.code)} decision steps">${active.steps.map((s,i)=>`<button class="step-tab ${i===stepIndex?'active':''}" data-step="${s.id}" ${i===stepIndex?'aria-current="step"':''}><span>${String(i+1).padStart(2,'0')}</span><b>${e(s.title)}</b></button>`).join('')}</nav>
 <section class="decision" aria-labelledby="question"><div class="question-head"><div><p class="eyebrow">Decision ${stepIndex+1} of ${active.steps.length} <span> / ${e(s.title)}</span></p><h2 id="question" tabindex="-1">${e(s.question)}</h2></div><a class="permalink" href="#${s.id}" aria-label="Link to this decision">#</a></div><div class="contextline"><span><b>When</b> ${e(s.timing)}</span><span><b>Responsible team</b> ${e(s.owner)}</span></div>
 <div class="decision-grid"><section class="orders"><div class="section-head"><span class="number-dot">1</span><h3>Tests and information needed</h3></div>${s.orders.map(g=>`<div class="ordergroup"><h4>${e(g.label)}</h4>${bullets(g.items)}</div>`).join('')}</section>
 <section class="results"><div class="section-head"><span class="number-dot">2</span><h3>Review results and select the next step</h3></div><p class="logic-note">Within a branch, all listed conditions apply unless an <b>OR</b> is stated. These links support review; they do not determine a patient’s eligibility.</p>${s.branches.map(b=>`<article class="branch ${e(b.kind)}"><div class="branch-title"><span class="route-label">${b.kind==='advance'?'Proceed when':b.kind==='hold'?'Pause and clarify':b.kind==='redirect'?'Use another pathway':'Do not proceed on this pathway'}</span><h4>${e(b.title)}</h4></div>${bullets(b.criteria)}<div class="branch-action"><span class="action-arrow">→</span><p>${e(b.action)} ${refs(b.refs)}</p>${b.to?`<button class="route-button" data-step="${e(b.to)}">${e(active.steps.find(x=>x.id===b.to).title)} →</button>`:b.kind==='redirect'&&active.roadmap?external(active.roadmap,'Treatment roadmap','route-button'):''}</div></article>`).join('')}</section></div>
 <div class="safety-grid"><section class="stops"><div class="section-head"><span class="status-icon">!</span><h3>Findings that require stopping or reassessment</h3></div>${s.stops.length?bullets(s.stops):'<p class="muted">No additional stopping condition is listed here. Earlier exclusions and the full transplant evaluation still apply.</p>'}<p class="small stopnote">Check whether each finding requires a temporary pause, excludes this allocation route, or rules out transplantation clinically.</p></section>
 <section class="gray"><div class="section-head"><span class="status-icon">?</span><h3>Questions for multidisciplinary discussion</h3></div>${s.issues.map(id=>{const i=active.issues.find(x=>x.id===id);return `<a class="issue-link" href="/mh-liver-pathways/transplant/alignment/${active.slug}/#${i.id}"><span>${e(i.record)}</span><b>${e(i.question)}</b><span class="issue-arrow">Compare sources · proposed decision →</span></a>`;}).join('')}</section></div>
 <nav class="stepfooter" aria-label="Previous and next decision"><button ${stepIndex===0?'disabled':''} data-step="${active.steps[Math.max(0,stepIndex-1)].id}">← Previous decision</button><span>${stepIndex+1} / ${active.steps.length}</span><button ${stepIndex===active.steps.length-1?'disabled':''} data-step="${active.steps[Math.min(active.steps.length-1,stepIndex+1)].id}">Next decision →</button></nav></section>`;
}

function renderMeeting(){
 return `<section class="meetingintro"><div><p class="eyebrow">Source comparison + local decision record</p><h2>Questions to resolve together</h2><p>Each question below is linked from the relevant pathway step. Source wording and our proposed interpretation are separate. <b>No local proposal is marked approved.</b></p></div><div class="docbox"><b>Protocol & meeting documents</b><a href="${active.protocol}" download>Clinical protocol · Oct 16 V3 DOCX ↓</a>${active.docs.map(d=>`<a href="${d.url}" download>${e(d.label)} · Oct 16 DOCX ↓</a>`).join('')}<a href="/mh-liver-pathways/transplant/meeting-records/${active.slug}.html" target="_blank" rel="noopener">Current web alignment record · print / save ↓</a><small>Word downloads retain their October 16 wording; the website language was revised October 23. Reconcile agreed changes in the source documents before clinical activation.</small></div></section>
 <div class="versionnote"><b>Version clarity:</b> the web source-comparison addendum was reviewed October 17, with a plain-language revision October 23. The linked V3 Word documents retain their October 16/source wording. Record an agreed change there before clinical activation.</div>
 <nav class="issue-index" aria-label="Meeting questions">${active.issues.map((i,n)=>`<a href="#${i.id}" data-issue="${i.id}">${n+1}. ${e(i.question)}</a>`).join('')}</nav>
 <div class="issue-records">${active.issues.map((i,n)=>renderIssue(i,n)).join('')}</div>`;
}

function renderIssue(i,n){
 const linked=active.steps.filter(s=>s.issues.includes(i.id));
 return `<article class="issue-record" id="${i.id}"><div class="issue-heading"><span class="issue-num">${String(n+1).padStart(2,'0')}</span><div><p class="eyebrow">${e(i.record)}</p><h3>${e(i.question)}</h3></div><span class="pending">Pending approval</span></div><div class="backsteps">In the pathway: ${linked.map(s=>`<a href="/mh-liver-pathways/transplant/${active.slug}/#${s.id}">${e(s.title)} ↗</a>`).join(' · ')}</div>
 <div class="comparison-grid">${i.comparisons.map(c=>`<section class="comparison"><div class="source-kind">${e(DATA.sources[c.ref].kind)}</div><h4>${e(DATA.sources[c.ref].short)}</h4><p class="quotation ${c.quote?'exact':''}">${c.quote?'“':''}${e(c.text)}${c.quote?'”':''}</p><p class="small muted">${c.quote?'Short verbatim excerpt':'Source summary / scope'}${c.locator?' · '+e(c.locator):''}</p>${refs([c.ref])}</section>`).join('')}</div>
 <div class="proposal"><div><span class="route-label">Proposed local approach · discussion draft</span><p>${e(i.proposal)}</p></div><div><b>Why this matters</b><p>${e(i.rationale)}</p></div></div><div class="meeting-status"><span><b>Proposed responsible team:</b> ${e(i.owners)}</span><span><b>Decision:</b> pending meeting</span><span><b>Approval / date:</b> not recorded</span></div></article>`;
}

function renderEvidence(){
 return `<section class="evidenceintro"><p class="eyebrow">Evidence is also linked at the point of use</p><h2>Sources for ${e(active.code)}</h2><p>Policy, review guidance, clinical recommendations and study evidence have different roles. Open a source to see its locator and full text. Publisher access may require an institutional sign-in. A source link does not imply high-level or definitive evidence.</p></section><div class="evidencegrid">${allRefs(active).map(id=>{const r=DATA.sources[id];return `<article class="evidencecard"><span class="source-kind">${e(r.kind)}</span><h3>${e(r.title)}</h3><p>${e(r.locator)}</p><button class="btn secondary" data-ref="${id}">Source details & full text ↗</button></article>`;}).join('')}</div>`;
}

function showSource(id, trigger){
 const r=DATA.sources[id];
 if(!r)return;
 lastTrigger=trigger;
 const d=document.getElementById('source-dialog');
 d.innerHTML=`<button type="button" class="close-dialog" aria-label="Close evidence">×</button><p class="eyebrow">${e(r.kind)}</p><h2 id="source-title">${e(r.title)}</h2><p class="locator">${e(r.locator)}</p>${r.note?`<div class="source-note">${e(r.note)}</div>`:''}<div class="source-actions">${external(r.url,r.kind==='Allocation policy'||r.kind==='NLRB guidance'?'Open official source':'Publisher / full-text access','btn')}</div><p class="small muted">Access through the publisher or official source; institutional sign-in may be required. The linked source supports the adjacent statement. Guidance is not binding allocation policy; cohort results and local proposals are not universal eligibility rules.</p>`;
 d.showModal();
}

function setStep(id,push=true){
 const index=active.steps.findIndex(s=>s.id===id);if(index<0)return;
 stepIndex=index;view='pathway';if(push)history.pushState(null,'','#'+id);renderView();
 document.getElementById('question').focus({preventScroll:true});
 document.querySelector('.stepstrip').scrollIntoView({block:'start',behavior:'instant'});
}
function hashState(){
 const h=decodeURIComponent(location.hash.slice(1));
 const idx=active.steps.findIndex(s=>s.id===h);
 if(DATA.mode==='alignment'&&active.issues.some(i=>i.id===h))view='meeting';
 else if(idx>=0){view='pathway';stepIndex=idx;}
 else if(h==='evidence')view='evidence';
 else if(h==='meeting'||active.issues.some(i=>i.id===h)||DATA.mode==='alignment')view='meeting';
 else view='pathway';
 renderView();
 if(view==='meeting'&&active.issues.some(i=>i.id===h))requestAnimationFrame(()=>document.getElementById(h)?.scrollIntoView({block:'start'}));
}

document.addEventListener('click',ev=>{
 const cite=ev.target.closest('[data-ref]');if(cite){showSource(cite.dataset.ref,cite);return;}
 if(ev.target.closest('.close-dialog')){document.getElementById('source-dialog').close();return;}
 const step=ev.target.closest('[data-step]');if(step&&!step.disabled){setStep(step.dataset.step);return;}
 const tab=ev.target.closest('[data-view]');if(tab){ev.preventDefault();view=tab.dataset.view;history.pushState(null,'',view==='pathway'?'#'+active.steps[stepIndex].id:'#'+view);renderView();return;}
 const issue=ev.target.closest('[data-issue]');if(issue){ev.preventDefault();history.pushState(null,'','#'+issue.dataset.issue);document.getElementById(issue.dataset.issue).scrollIntoView({block:'start'});}
});
document.getElementById('source-dialog').addEventListener('click',ev=>{if(ev.target===ev.currentTarget){const r=ev.currentTarget.getBoundingClientRect();if(ev.clientX<r.left||ev.clientX>r.right||ev.clientY<r.top||ev.clientY>r.bottom)ev.currentTarget.close();}});
document.getElementById('source-dialog').addEventListener('close',()=>lastTrigger?.focus());
window.addEventListener('popstate',()=>active?hashState():null);
window.addEventListener('hashchange',()=>active?hashState():null);
document.addEventListener('keydown',ev=>{
 if(!ev.target.matches('[role="tab"]')||!['ArrowLeft','ArrowRight','Home','End'].includes(ev.key))return;
 ev.preventDefault();const tabs=[...document.querySelectorAll('[role="tab"]')];let n=tabs.indexOf(ev.target);
 n=ev.key==='Home'?0:ev.key==='End'?tabs.length-1:(n+(ev.key==='ArrowRight'?1:-1)+tabs.length)%tabs.length;
 tabs[n].click();tabs[n].focus();
});
if(active){pathwayShell();hashState();}else home();
