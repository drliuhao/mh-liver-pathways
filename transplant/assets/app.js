/* Shared renderer and local decision choices; no records, scoring or persistent storage. */
'use strict';
const DATA = JSON.parse(document.getElementById('protocol-data').textContent);
// One navigation map serves conditional options and reference return links.
for(const p of Object.values(DATA.high_risk.pathways))for(const review of p.reviews)review.steps=RiskRouting.coverage[review.anchor]||[];
const app = document.getElementById('app');
const escapeHTML = s => String(s ?? '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const e = escapeHTML;
let active = DATA.pathway || null;
let view = DATA.mode === 'alignment' ? 'meeting' : 'pathway';
let stepIndex = 0;
let careId = 'treatment';
let lastTrigger = null;
let assistantSession = active ? DecisionAssistant.createSession(active,DATA.assistants) : null;
let navigationObserver = null;
let riskContext = {};
let riskReference = null;
const assistantKey = () => `${active.slug}/${active.steps[stepIndex].id}`;
const assistantConfig = () => DATA.assistants[assistantKey()];
const refs = ids => (ids || []).map(id => `<button type="button" class="cite" data-ref="${e(id)}" aria-label="Evidence: ${e(DATA.sources[id].short)}">${e(DATA.sources[id].short)} ↗</button>`).join(' ');
const bullets = items => `<ul>${items.map(x=>`<li>${x.children?`<b>${e(x.text)}</b>`:e(x.text)} ${x.children?bullets(x.children):`<span class="citations">${refs(x.refs)}</span>`}</li>`).join('')}</ul>`;
const external = (url,label,cls='') => `<a class="${cls}" href="${e(url)}" target="_blank" rel="noopener">${e(label)} ↗</a>`;
const allRefs = p => {
  const ids = new Set();
  p.steps.forEach(s=>{s.orders.forEach(g=>g.items.forEach(x=>x.refs.forEach(r=>ids.add(r))));s.branches.forEach(b=>{b.criteria.forEach(x=>x.refs.forEach(r=>ids.add(r)));b.refs.forEach(r=>ids.add(r));});s.stops.forEach(x=>x.refs.forEach(r=>ids.add(r)));});
  p.issues.forEach(i=>i.comparisons.forEach(c=>ids.add(c.ref)));
  DATA.care[p.slug].forEach(c=>c.refs.forEach(r=>ids.add(r)));
  p.steps.forEach(s=>{const a=DATA.assistants[`${p.slug}/${s.id}`];a.questions.forEach(q=>{q.refs.forEach(r=>ids.add(r));q.criteria.forEach(c=>c.refs.forEach(r=>ids.add(r)));});a.rules.forEach(r=>r.refs.forEach(id=>ids.add(id)));});
  return [...ids];
};

function header() {
 return `<div class="draftbar">Clinical review draft <span>Not approved institutional policy · Not an automated eligibility tool.</span></div>
 <header class="top"><a class="brand" href="/mh-liver-pathways/transplant/">Memorial Hermann<span>Transplant oncology pathways</span></a>
 <nav aria-label="Tumor pathways">${DATA.index.map(p=>`<a href="/mh-liver-pathways/transplant/${p.slug}/" ${active?.slug===p.slug?'aria-current="page"':''}>${e(p.code)}</a>`).join('')}</nav>
 <a class="cancer-link" href="https://drliuhao.github.io/mh-liver-pathways/" target="_blank" rel="noopener">Cancer roadmaps ↗</a></header>`;
}

function footer() {
 return `<footer><b>Suitability for liver transplantation and eligibility for MELD-exception points are assessed separately.</b> This draft supports, but does not replace, specialist judgment and the center’s full transplant evaluation. Proposed local decisions are not institutional approvals.<br><span>Language and next actions revised October 24, 2026; pathway source review October 17, 2026 · OPTN policies checked October 24, 2026 (effective October 1, 2026) · NLRB guidance: December 2025. Check current requirements when submitting an exception request.</span></footer>`;
}

function home() {
 app.innerHTML = header()+`<main class="wrap home"><div class="homehero"><div><p class="eyebrow">Diagnosis → selection → disease control → transplant</p><h1>Liver transplant assessment and treatment pathways</h1><p class="lead">Transplant oncology pathways with the information to collect, the findings that change treatment or transplant plans, and the evidence beside each decision.</p></div><div class="how"><b>How to use the pathways</b><ol><li>Choose the tumor and current decision.</li><li>Start with the preselected transplant example, or clear all choices.</li><li>Change findings and follow the highlighted next step; read the criteria and key papers beside each choice.</li><li>Open evidence or an unresolved meeting question in context.</li></ol></div></div>
 <div class="searchbar"><label for="search">Find a pathway or clinical question</label><input id="search" type="search" placeholder="Try “LR-4”, “biopsy”, “CEA”, “nodes” or “unresectability”…" autocomplete="off"><p id="search-count" class="muted small" aria-live="polite">Seven disease-specific pathways · different step counts, one shared decision structure.</p></div>
 <section id="pathway-grid" class="pathway-grid" aria-label="Choose a pathway">${DATA.index.map(p=>`<article class="pathway-tile" data-slug="${p.slug}"><div class="tiletop"><span class="code">${e(p.code)}</span><span class="small muted">${p.steps.length} decisions</span></div><h2><a href="/mh-liver-pathways/transplant/${p.slug}/">${e(p.name)}</a></h2><span class="authority">${e(p.route)}</span><p>${e(p.entry)}</p><div class="tileflow">${e(p.steps[0].title)} <span>→</span> ${e(p.steps[p.steps.length-1].title)}</div><a class="tilego" href="/mh-liver-pathways/transplant/${p.slug}/">Open pathway <span>→</span></a></article>`).join('')}</section><section id="search-results" hidden aria-label="Matching decisions"></section>
 <section class="key"><div><span class="keyline go"></span><b>Proceed</b><p>The findings support reviewing the next decision.</p></div><div><span class="keyline hold"></span><b>Pause and clarify</b><p>Assign a clinician to resolve missing or uncertain information.</p></div><div><span class="keyline stop"></span><b>Stop and review</b><p>Read which decision is affected, then follow the stated assessment, treatment or continuing-care action.</p></div><div><span class="keyline discuss"></span><b>Meeting question</b><p>Compare sources and see the proposed local approach.</p></div></section></main>`+footer();
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
 <div class="viewbar" role="tablist" aria-label="Pathway sections"><button role="tab" id="tab-pathway" data-view="pathway">Decision pathway</button><button role="tab" id="tab-meeting" data-view="meeting">Meeting record <span>${active.issues.length}</span></button><button role="tab" id="tab-care" data-view="care">Treatment & continuing care</button><button role="tab" id="tab-high-risk" class="high-risk-tab" data-view="high-risk">High-risk protocols <span>${HighRisk.reviews(DATA.high_risk,active.slug).length}</span></button><button role="tab" id="tab-evidence" data-view="evidence">Evidence library</button><span class="viewnote">Compare choices · nothing is saved</span></div>
 <div id="view"></div></main>`+footer();
 renderView();
}

function renderView(){
 document.querySelectorAll('[role="tab"]').forEach(t=>t.setAttribute('aria-selected',t.dataset.view===(view==='risk-reference'?'high-risk':view)?'true':'false'));
 const out=document.getElementById('view');
 out.setAttribute('role','tabpanel');out.setAttribute('aria-labelledby','tab-'+(view==='risk-reference'?'high-risk':view));
 const content=view==='pathway'?renderStep():view==='meeting'?renderMeeting():view==='evidence'?renderEvidence():view==='high-risk'?HighRisk.overview(DATA.high_risk,active.slug):view==='risk-reference'?renderRiskReference():renderCare();
 out.innerHTML=(view==='pathway'?renderOverview():'')+renderNavigation()+content;
 if(view==='pathway')updateDecision();
 navigationObserver?.disconnect();
 navigationObserver=new ResizeObserver(syncNavigationHeight);
 navigationObserver.observe(out.querySelector('.pathway-nav'));
 syncNavigationHeight();
}

function syncNavigationHeight(){
 const height=document.querySelector('.pathway-nav')?.getBoundingClientRect().height||0;
 document.documentElement.style.setProperty('--pathway-nav-height',`${Math.ceil(height)}px`);
 const strip=document.querySelector('.stepstrip'),selected=strip?.querySelector('.step-tab.active');
 if(strip&&selected&&strip.scrollWidth>strip.clientWidth)strip.scrollLeft=selected.offsetLeft-strip.offsetLeft-(strip.clientWidth-selected.offsetWidth)/2;
}

function exampleStatus(){
 const origins=active.steps.map(s=>assistantSession.origins[`${active.slug}/${s.id}`]);
 if(origins.every(x=>x==='example'))return ['Preselected transplant example','Choices show one path toward transplant. Change findings to explore other options.'];
 if(origins.every(x=>x==='empty'))return ['All choices cleared','Choose findings at each decision. No results are assumed.'];
 return ['Exploring different findings','Changing a finding clears later choices. Review those decisions again, or restore the full example.'];
}

function renderOverview(){
 const status=exampleStatus();
 return `<section class="journey-overview" aria-labelledby="journey-title"><div class="journey-heading"><div><p class="eyebrow">The whole pathway</p><h2 id="journey-title">From diagnosis to transplant and follow-up</h2></div><a href="#care-treatment" data-care="treatment" class="journey-alternative">Treatment and care alternatives →</a></div>
 <nav class="journey-phases" aria-label="Pathway overview">${DATA.journeys[active.slug].map((phase,n)=>{const first=active.steps.findIndex(s=>s.id===phase.steps[0])+1;const last=first+phase.steps.length-1;const current=phase.steps.includes(active.steps[stepIndex].id);return `<button data-step="${e(phase.steps[0])}" class="journey-phase ${current?'current':''}" ${current?'aria-current="true"':''}><span class="phase-number">${n+1}</span><span><b>${e(phase.title)}</b><small>Decision${first===last?'':'s'} ${first}${first===last?'':'–'+last}</small></span><span class="phase-arrow" aria-hidden="true">→</span></button>`;}).join('')}</nav>
 <div class="example-controls"><div aria-live="polite"><strong data-example-status>${e(status[0])}</strong><p data-example-description>${e(status[1])}</p></div><div class="example-buttons"><button data-pathway-example>Restore transplant example</button><button data-pathway-clear>Clear all choices</button></div></div></section>`;
}

function renderNavigation(){
 const s=active.steps[stepIndex];
 const origin=assistantSession.origins[assistantKey()];
 const label=origin==='example'?'Example choices':origin==='edited'?'Choices changed':'Choices needed';
 return `<div class="pathway-nav"><div class="pathway-location"><span><b>${e(active.code)}</b> <span class="location-count">Decision ${stepIndex+1} of ${active.steps.length}</span><span class="location-title">${e(s.title)}</span></span><div class="location-tools"><span class="selection-label" data-selection-label>${label}</span><button data-pathway-overview>Overview ↑</button></div></div>
 <nav class="stepstrip" aria-label="${e(active.code)} decision steps">${active.steps.map((s,i)=>`<button class="step-tab ${i===stepIndex?'active':''}" data-step="${s.id}" ${i===stepIndex?'aria-current="step"':''}><span>${String(i+1).padStart(2,'0')}</span><b>${e(s.title)}</b></button>`).join('')}</nav></div>`;
}

function updateExampleLabels(){
 const status=exampleStatus();
 const title=document.querySelector('[data-example-status]'),description=document.querySelector('[data-example-description]');
 if(title)title.textContent=status[0];if(description)description.textContent=status[1];
 const origin=assistantSession.origins[assistantKey()];
 const label=document.querySelector('[data-selection-label]');
 if(label)label.textContent=origin==='example'?'Example choices':origin==='edited'?'Choices changed':'Choices needed';
 const intro=document.querySelector('.assistant-intro');
 if(intro)intro.textContent=origin==='example'?'Example findings are preselected to show the path toward transplant. Change any choice to explore another result.':origin==='edited'&&stepIndex<active.steps.length-1?'Findings changed. Later decisions have been cleared; review them again before continuing.':'Choose the findings that matter for this decision. The matching next step will be highlighted.';
}

function highRiskAction(a){
 const target=HighRisk.destination(a.url);
 if(!target||target.slug&&target.slug!==active.slug)return external(a.url,a.label,'route-button');
 return `<a class="route-button high-risk-route" href="#high-risk${target.id?'-'+e(target.id):''}" ${target.id?`data-high-risk="${e(target.id)}"`:'data-view="high-risk"'}><small>High-risk protocol · ${e(HighRisk.statusLabel(target.id))}</small>${e(a.label)} →</a>`;
}
function renderActions(actions){
 return `<div class="next-actions">${actions.map(a=>`<div class="next-action">${a.detail?`<p>${e(a.detail)}</p>`:''}${a.step?`<button class="route-button" data-step="${e(a.step)}">${e(a.label)} →</button>`:a.care?`<a class="route-button" href="#care-${e(a.care)}" data-care="${e(a.care)}">${e(a.label)} →</a>`:highRiskAction(a)}</div>`).join('')}</div>`;
}

function afpReviewHTML(finding){
 if(!finding)return '';
 return `<details class="risk-next-option ${finding.deferred?'risk-neutral':'risk-proposed'}" data-afp-review><summary><span class="risk-next-status">High-risk HCC review · individual assessment</span><b>AFP criterion not met: review transplant options</b><span class="risk-trigger">${finding.carried?'From decision '+(active.steps.findIndex(s=>s.id===finding.origin)+1)+': ':''}${e(finding.why)}</span><span class="risk-open-label">Open the AFP review and supporting guidance ↓</span></summary><div class="risk-next-body"><p><b>Review remains an option.</b> An unmet AFP requirement prevents a standardized exception; it does not by itself end the transplant assessment. Review AFP history and trend, treatment response, staging, liver reserve and expected transplant benefit.</p><p>OPTN Policy 9.5.I.iv sends the specified AFP nonresponse cases to individual NLRB review. The transplant-oncology guidance says these cases are generally unfavorable for exception approval, but selected cases may be appropriate.</p><p>This is an individual high-risk review route. The existing beyond-UNOS tumor-burden study has separate entry limits, including AFP &lt;100; it is not an AFP-only expansion protocol.</p><p>${external('https://www.hrsa.gov/sites/default/files/hrsa/optn/optn_policies.pdf#page=197','OPTN Policy 9.5.I.iv · PDF pp197–198')} · ${external('https://www.hrsa.gov/sites/default/files/hrsa/optn/adult-meld-exception-transplant-oncology-review-guidance.pdf#page=3','NLRB HCC guidance · PDF p3')}</p>${renderActions([{label:'High-risk HCC and individual allocation assessment',care:'exception'},{label:'Continue or change HCC treatment',care:'treatment'},{label:'Recheck the AFP requirement',step:finding.origin}])}</div></details>`;
}
function riskOptionsHTML(context){
 const descriptions={review:'Proposed high-risk review · not active',safety:'Immunotherapy safety review · proposed local approach','safety-note':'Immunotherapy safety context · proposed local approach',closed:'Local proposal: expansion remains closed',notice:'Selection / allocation clarification',checklist:'Proposed local review · approval pending',readiness:'Study development · no protocol-directed transplant'};
 const notes=context.clarify.length?`<div class="risk-clarify"><b>Clarify the finding before choosing a specific review</b><ul>${context.clarify.map(q=>`<li>${e(q.label)}${q.origin?` <button data-step="${e(q.origin)}">Review earlier finding →</button>`:''}</li>`).join('')}</ul></div>`:'';
 const note=context.guard||(context.route?.origin!==active.steps[stepIndex].id?context.route:null);
 const duplicate=note&&(context.clarify.some(q=>q.label===note.why)||context.options.some(o=>o.reason===note.why));
 const guardNote=context.showGuard&&note&&!duplicate?`<div class="risk-clarify"><b>Why further review is needed</b><p>${e(note.why)}</p><button data-step="${e(note.origin)}">Review the triggering finding →</button></div>`:'';
 return guardNote+notes+afpReviewHTML(context.afpReview)+context.options.map(o=>{
  const record=HighRisk.reviews(DATA.high_risk,active.slug).find(r=>r.anchor===o.anchor);if(!record)return '';
  const ordinary=['closed','notice','checklist','safety-note'].includes(o.mode);
  return `<details class="risk-next-option ${ordinary?'risk-neutral':'risk-proposed'}" data-risk-anchor="${e(o.anchor)}" data-risk-mode="${e(o.mode)}"><summary><span class="risk-next-status">${e(descriptions[o.mode])}</span><b>${e(record.title)}</b><span class="risk-trigger">${o.carried?'From decision '+(active.steps.findIndex(s=>s.id===o.origin)+1)+': ':'Selected finding: '}${e(o.reason)}</span><span class="risk-open-label">${ordinary?'Read the relevant criteria and evidence':'Review this option, criteria and evidence'} ↓</span></summary><div class="risk-next-body"><button class="risk-change" data-step="${e(o.origin)}">Review the triggering finding →</button>${HighRisk.card(DATA.high_risk,active.slug,{...record,steps:[active.steps[stepIndex].id]})}</div></details>`;
 }).join('');
}
function updateDecision(){
 const out=document.getElementById('view');
 out.querySelectorAll('.risk-next-options').forEach(node=>node.remove());
 const result=DecisionAssistant.update(out,assistantConfig(),assistantSession.answers[assistantKey()],active.steps[stepIndex].branches,DATA.sources,assistantSession.origins[assistantKey()]);
 const context=RiskRouting.evaluate(active,stepIndex,assistantSession,riskContext,DATA.assistants);
 out.querySelector('#risk-question-panel').innerHTML=RiskRouting.renderQuestions(context.questions,riskContext[assistantKey()]);
 // An unresolved upstream exclusion cannot be cleared by a later favorable example.
 const reviewContext=context.guard||context.route;
 const override=reviewContext&&result.kind==='advance';
 if(override){
  out.querySelectorAll('[data-branch-index]').forEach(card=>{card.classList.remove('is-highlighted');card.classList.add('is-muted');card.removeAttribute('aria-current');card.querySelector('.branch-match').hidden=true;});
  const feedback=out.querySelector('.assistant-feedback');feedback.className='assistant-feedback hold';feedback.innerHTML=`<strong>${context.guard?'Review the selected finding before proceeding':'Continue case-specific review'}</strong><p>${e(reviewContext.why)}</p>`;
 }
 updateExampleLabels();
 const onward=DATA.continuations[assistantKey()];
 out.querySelectorAll('[data-next-branch]').forEach(el=>{el.innerHTML=renderActions(onward.branches[el.dataset.nextBranch]);});
 const extra=out.querySelector('.assistant-other-result');
 if(override){
  extra.hidden=false;extra.className='assistant-other-result branch hold is-highlighted';
  const actions=[{label:'Review the triggering finding',step:reviewContext.origin},{label:'Review treatment and continuing care',care:'treatment'}];
  if(active.slug==='hcc')actions.push({label:'Review individual exception assessment and treatment options',care:'exception'});
  if(!context.guard&&active.steps[stepIndex+1])actions.push({label:'Continue case-specific review: '+active.steps[stepIndex+1].title,step:active.steps[stepIndex+1].id});
  extra.innerHTML=`<span class="branch-match">${context.guard?'Additional review required':'Individual review route'}</span><h4>${context.guard?'Resolve the selection or safety issue':'Continue case-specific assessment'}</h4><p>${e(reviewContext.why)}</p><h5 class="next-heading">Choose the next action</h5>${renderActions(actions)}`;
 }else if(!extra.hidden){
  const actions=result.state==='matched'?onward.rules[String(result.ruleIndex)]:onward.clarify;
  extra.insertAdjacentHTML('beforeend',`<h5 class="next-heading">Choose the next action</h5>${renderActions(actions)}`);
 }
 const content=riskOptionsHTML({...context,showGuard:!override});
 if(content){
  let destination=(!extra.hidden?extra:out.querySelector('[data-branch-index].is-highlighted'));
  if(!destination){extra.hidden=false;extra.className='assistant-other-result branch hold is-highlighted';extra.innerHTML=`<h4>Clarify the selected findings</h4><h5 class="next-heading">Choose the next action</h5>${renderActions(onward.clarify)}`;destination=extra;}
  destination.insertAdjacentHTML('beforeend',`<div class="risk-next-options">${content}</div>`);
 }
 return result;
}
function renderRiskReference(){
 const records=HighRisk.reviews(DATA.high_risk,active.slug);
 const record=records.find(r=>r.anchor===riskReference);
 const content=record?HighRisk.card(DATA.high_risk,active.slug,record):riskReference==='readiness'?DATA.high_risk.readiness.map(r=>HighRisk.card(DATA.high_risk,active.slug,r,true)).join(''):'';
 return `<section class="risk-reference"><div class="risk-reference-note"><b>Reference view</b><p>Opening this reference does not match it to the selected findings. In the decision pathway, specific reviews appear with the relevant next-step choices.</p><button data-step="${e(active.steps[stepIndex].id)}">Return to the decision →</button></div>${content||HighRisk.overview(DATA.high_risk,active.slug)}</section>`;
}

function renderCare(){
 const plans=DATA.care[active.slug];
 const selected=plans.find(p=>p.id===careId)||plans[0];
 return `<section class="care-view" aria-labelledby="care-title"><a class="back" href="#${e(active.steps[stepIndex].id)}" data-step="${e(active.steps[stepIndex].id)}">← Back to the decision</a><p class="eyebrow">${e(active.code)} · Treatment and continuing care</p><h2 id="care-title" tabindex="-1">${e(selected.title)}</h2><p class="lead">${e(selected.when)}</p><details class="care-alternatives"><summary>Other treatment and care options</summary><nav class="care-index" aria-label="Care options">${plans.map(p=>`<a href="#care-${e(p.id)}" data-care="${e(p.id)}" ${p.id===selected.id?'aria-current="page"':''}>${e(p.title)}</a>`).join('')}</nav></details><article class="care-plan"><h3>${selected.endpoint?'Care to arrange':'Clinical actions'}</h3><ol>${selected.tasks.map(t=>`<li>${e(t)}</li>`).join('')}</ol><div class="care-sources"><h4>Supporting sources</h4>${selected.refs.map(id=>`<div>${refs([id])}<p class="small muted">${e(DATA.sources[id].locator)}</p></div>`).join('')}</div><h3>${selected.endpoint?'Reassess when circumstances change':'What follows this decision'}</h3>${renderActions(selected.actions)}</article></section>`;
}

function renderStep(){
 const s=active.steps[stepIndex];
 return `<section class="decision" aria-labelledby="question"><div class="question-head"><div><p class="eyebrow">Decision ${stepIndex+1} of ${active.steps.length} <span> / ${e(s.title)}</span></p><h2 id="question" tabindex="-1">${e(s.question)}</h2></div><a class="permalink" href="#${s.id}" aria-label="Link to this decision">#</a></div><div class="contextline"><span><b>When</b> ${e(s.timing)}</span><span><b>Responsible team</b> ${e(s.owner)}</span></div>
 <div class="decision-grid"><section class="orders"><div class="section-head"><span class="number-dot">1</span><h3>Tests and information needed</h3></div>${DecisionAssistant.render(assistantConfig(),DATA.sources,assistantSession.answers[assistantKey()],assistantSession.origins[assistantKey()])}<div id="risk-question-panel"></div><details class="full-tests"><summary>Full test checklist and source details</summary>${s.orders.map(g=>`<div class="ordergroup"><h4>${e(g.label)}</h4>${bullets(g.items)}</div>`).join('')}</details></section>
 <section class="results" id="decision-results"><div class="section-head"><span class="number-dot">2</span><h3>Review results and select the next step</h3></div><p class="logic-note">Your choices highlight the relevant recommendation and next actions. Review each option with the treating team.</p><article class="assistant-other-result" hidden></article>${s.branches.map((b,bi)=>`<article class="branch ${e(b.kind)} is-muted" data-branch-index="${bi}"><span class="branch-match" hidden>Matches these choices</span><div class="branch-title"><span class="route-label">${b.kind==='advance'?'Proceed when':b.kind==='hold'?'Pause and clarify':b.kind==='redirect'?'Use another pathway':'Do not proceed on this pathway'}</span><h4>${e(b.title)}</h4></div><details class="branch-details"><summary>Criteria and supporting sources</summary>${bullets(b.criteria)}</details><div class="branch-action"><span class="action-arrow">→</span><p>${e(b.action)} ${refs(b.refs)}</p></div><div data-next-branch="${bi}"></div></article>`).join('')}</section></div>
 <div class="safety-grid"><section class="stops"><div class="section-head"><span class="status-icon">!</span><h3>Findings that change the treatment or transplant plan</h3></div>${s.stops.length?bullets(s.stops):'<p class="muted">No additional exclusion is listed at this step. Apply the earlier disease-specific criteria and complete the full transplant assessment.</p>'}<p class="small stopnote">Each statement identifies what the finding affects: treatment, a MELD-exception request, or transplantation under this protocol.</p></section>
 <section class="gray"><div class="section-head"><span class="status-icon">?</span><h3>Questions for multidisciplinary discussion</h3></div>${s.issues.map(id=>{const i=active.issues.find(x=>x.id===id);return `<a class="issue-link" href="/mh-liver-pathways/transplant/alignment/${active.slug}/#${i.id}"><span>Discussion ${active.issues.indexOf(i)+1}</span><b>${e(i.question)}</b><span class="issue-arrow">Compare sources · proposed decision →</span></a>`;}).join('')}</section></div>
 <nav class="stepfooter" aria-label="Previous and next decision"><button ${stepIndex===0?'disabled':''} data-step="${active.steps[Math.max(0,stepIndex-1)].id}">← Previous decision</button><span>${stepIndex+1} / ${active.steps.length}</span><button ${stepIndex===active.steps.length-1?'disabled':''} data-step="${active.steps[Math.min(active.steps.length-1,stepIndex+1)].id}">Next decision →</button></nav></section>`;
}

function renderMeeting(){
 return `<section class="meetingintro"><div><p class="eyebrow">Source comparison + local decision record</p><h2>Questions to resolve together</h2><p>Each question below is linked from the relevant pathway step. Source wording and our proposed interpretation are separate. <b>No local proposal is marked approved.</b></p></div><div class="docbox"><b>Protocol & meeting documents</b><a href="${active.protocol}" download>Clinical protocol · Oct 16 V3 DOCX ↓</a>${active.docs.map(d=>`<a href="${d.url}" download>${e(d.label)} · Oct 16 DOCX ↓</a>`).join('')}<a href="/mh-liver-pathways/transplant/meeting-records/${active.slug}.html" target="_blank" rel="noopener">Current web alignment record · print / save ↓</a><small>Word downloads retain their October 16 wording; the website language was revised October 24. Reconcile agreed changes in the source documents before clinical activation.</small></div></section>
 <div class="versionnote"><b>Version clarity:</b> the web source-comparison addendum was reviewed October 17, with language and next-action revisions October 24. The linked V3 Word documents retain their October 16/source wording. Record an agreed change there before clinical activation.</div>
 <aside class="high-risk-doc-note">${HighRisk.badge()}<p>Specific V7 reviews appear with matching next-step choices. The reference index retains all proposed criteria, study results and full-text access.</p><a href="#high-risk" data-view="high-risk">Open the integrated high-risk protocols →</a>${HighRisk.downloads(DATA.high_risk,active.slug)}</aside><nav class="issue-index" aria-label="Meeting questions">${active.issues.map((i,n)=>`<a href="#${i.id}" data-issue="${i.id}">${n+1}. ${e(i.question)}</a>`).join('')}</nav>
 <div class="issue-records">${active.issues.map((i,n)=>renderIssue(i,n)).join('')}</div>`;
}

function renderIssue(i,n){
 const linked=active.steps.filter(s=>s.issues.includes(i.id));
 return `<article class="issue-record" id="${i.id}"><div class="issue-heading"><span class="issue-num">${String(n+1).padStart(2,'0')}</span><div><p class="eyebrow">Source-document item: ${e(i.record)}</p><h3>${e(i.question)}</h3></div><span class="pending">Pending approval</span></div><div class="backsteps">In the pathway: ${linked.map(s=>`<a href="/mh-liver-pathways/transplant/${active.slug}/#${s.id}">${e(s.title)} ↗</a>`).join(' · ')}</div>
 <div class="comparison-grid">${i.comparisons.map(c=>`<section class="comparison"><div class="source-kind">${e(DATA.sources[c.ref].kind)}</div><h4>${e(DATA.sources[c.ref].short)}</h4><p class="quotation ${c.quote?'exact':''}">${c.quote?'“':''}${e(c.text)}${c.quote?'”':''}</p><p class="small muted">${c.quote?'Short verbatim excerpt':'Source summary / scope'}${c.locator?' · '+e(c.locator):''}</p>${refs([c.ref])}</section>`).join('')}</div>
 <div class="proposal"><div><span class="route-label">Proposed local approach · discussion draft</span><p>${e(i.proposal)}</p></div><div><b>Why this matters</b><p>${e(i.rationale)}</p></div></div><div class="meeting-status"><span><b>Proposed responsible team:</b> ${e(i.owners)}</span><span><b>Decision:</b> pending meeting</span><span><b>Approval / date:</b> not recorded</span></div></article>`;
}

function renderEvidence(){
 return `<section class="evidenceintro"><p class="eyebrow">Evidence is also linked at the point of use</p><h2>Sources for ${e(active.code)}</h2><p>Policy, review guidance, clinical recommendations and study evidence have different roles. Open a source to see its locator and full text. Publisher access may require an institutional sign-in. A source link does not imply high-level or definitive evidence.</p></section><div class="evidence-search"><label for="evidence-search">Find a source across this pathway</label><input id="evidence-search" type="search" data-evidence-search placeholder="Author, trial, guideline, PMID or DOI…"><span role="status" data-evidence-count>All sources shown</span></div><h3 class="evidence-group-title">Sources linked to standard decisions</h3><div class="evidencegrid">${allRefs(active).map(id=>{const r=DATA.sources[id];return `<article class="evidencecard" data-evidence-item data-search-text="${e([r.short,r.title,r.locator,r.url,r.pmid,r.doi].filter(Boolean).join(' '))}"><span class="source-kind">${e(r.kind)}</span><h3>${e(r.title)}</h3><p>${e(r.locator)}</p><button class="btn secondary" data-ref="${id}">Source details & full text ↗</button></article>`;}).join('')}</div>${HighRisk.library(DATA.high_risk,active.slug)}`;
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
 document.querySelector('.decision').scrollIntoView({block:'start',behavior:'instant'});
}
function showHighRisk(id,push=true){
 riskReference=id;view='risk-reference';
 if(push)history.pushState(null,'','#high-risk-'+id);
 renderView();
 const target=document.querySelector('.risk-reference');
 target?.scrollIntoView({block:'start',behavior:'instant'});
}

function hashState(){
 const h=decodeURIComponent(location.hash.slice(1));
 const idx=active.steps.findIndex(s=>s.id===h);
 if(h.startsWith('high-risk-')){showHighRisk(h.slice(10),false);return;}
 if(h==='high-risk'){view='high-risk';renderView();return;}
 if(h.startsWith('care-')&&DATA.care[active.slug].some(p=>p.id===h.slice(5))){view='care';careId=h.slice(5);}
 else if(DATA.mode==='alignment'&&active.issues.some(i=>i.id===h))view='meeting';
 else if(idx>=0){view='pathway';stepIndex=idx;}
 else if(h==='evidence')view='evidence';
 else if(h==='meeting'||active.issues.some(i=>i.id===h)||DATA.mode==='alignment')view='meeting';
 else view='pathway';
 renderView();
 if(view==='meeting'&&active.issues.some(i=>i.id===h))requestAnimationFrame(()=>document.getElementById(h)?.scrollIntoView({block:'start'}));
}

document.addEventListener('input',ev=>{
 if(ev.target.matches('[data-study-search]')){
  const box=ev.target.closest('.hr-evidence'),q=ev.target.value.trim().toLowerCase();
  const studies=[...box.querySelectorAll('.hr-study')];
  studies.forEach(el=>el.hidden=!!q&&!el.textContent.toLowerCase().includes(q));
  box.querySelector('[data-study-count]').textContent=`${studies.filter(el=>!el.hidden).length} of ${studies.length} study summaries shown`;
 }
 if(ev.target.matches('[data-evidence-search]')){
  const q=ev.target.value.trim().toLowerCase(),items=[...document.querySelectorAll('[data-evidence-item]')];
  items.forEach(el=>el.hidden=!!q&&!`${el.textContent} ${el.dataset.searchText||''}`.toLowerCase().includes(q));
  document.querySelector('[data-evidence-count]').textContent=`${items.filter(el=>!el.hidden).length} of ${items.length} source records shown`;
 }
});

document.addEventListener('change',ev=>{
 if(!active)return;
 const riskId=ev.target.dataset.riskQuestion;
 if(riskId){
  const key=assistantKey();riskContext[key]||={};riskContext[key][riskId]=ev.target.value;
  if(riskId==='ici')delete riskContext[key].ici_review;
  RiskRouting.clearFrom(riskContext,active,stepIndex+1);DecisionAssistant.clearFrom(assistantSession,active,stepIndex+1);assistantSession.origins[key]='edited';
  updateDecision();document.getElementById('risk-'+riskId)?.focus({preventScroll:true});return;
 }
 const id=ev.target.dataset.assistantQuestion;if(!id)return;
 const config=assistantConfig(),q=config.questions.find(q=>q.id===id);if(!q)return;
 DecisionAssistant.changeAnswer(assistantSession,active,stepIndex,id,ev.target.value);
 RiskRouting.clearFrom(riskContext,active,stepIndex);
 const answers=assistantSession.answers[assistantKey()];
 document.querySelector(`[data-definitions="${id}"]`).innerHTML=DecisionAssistant.definitions(q,answers[id],DATA.sources);
 updateDecision();
});

document.addEventListener('click',ev=>{
 const highRisk=ev.target.closest('[data-high-risk]');if(highRisk){ev.preventDefault();showHighRisk(highRisk.dataset.highRisk);return;}
 if(ev.target.closest('[data-pathway-overview]')){
  if(view!=='pathway'){view='pathway';history.pushState(null,'','#'+active.steps[stepIndex].id);renderView();}
  const title=document.getElementById('journey-title');title.setAttribute('tabindex','-1');title.focus({preventScroll:true});
  document.querySelector('.journey-overview').scrollIntoView({block:'start',behavior:'instant'});return;
 }
 if(ev.target.closest('[data-pathway-example],[data-pathway-clear]')){
  const examples=!!ev.target.closest('[data-pathway-example]');
  assistantSession=DecisionAssistant.createSession(active,DATA.assistants,examples);riskContext={};
  renderView();document.querySelector(examples?'[data-pathway-example]':'[data-pathway-clear]').focus({preventScroll:true});return;
 }
 const care=ev.target.closest('[data-care]');if(care){ev.preventDefault();careId=care.dataset.care;view='care';history.pushState(null,'','#care-'+careId);renderView();document.getElementById('care-title').focus({preventScroll:true});document.querySelector('.care-view').scrollIntoView({block:'start',behavior:'instant'});return;}
 if(ev.target.closest('[data-assistant-reset]')){
  DecisionAssistant.clearFrom(assistantSession,active,stepIndex);RiskRouting.clearFrom(riskContext,active,stepIndex);renderView();document.querySelector('[data-assistant-reset]').focus({preventScroll:true});return;
 }
 if(ev.target.closest('[data-assistant-show]')){const target=document.querySelector('.results .branch.is-highlighted:not([hidden])')||document.getElementById('decision-results');target.scrollIntoView({block:'start',behavior:'instant'});return;}

 const cite=ev.target.closest('[data-ref]');if(cite){showSource(cite.dataset.ref,cite);return;}
 if(ev.target.closest('.close-dialog')){document.getElementById('source-dialog').close();return;}
 const step=ev.target.closest('[data-step]');if(step&&!step.disabled){ev.preventDefault();setStep(step.dataset.step);return;}
 const tab=ev.target.closest('[data-view]');if(tab){ev.preventDefault();view=tab.dataset.view;history.pushState(null,'',view==='pathway'?'#'+active.steps[stepIndex].id:view==='care'?'#care-'+careId:'#'+view);renderView();return;}
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
