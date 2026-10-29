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
let assistantSession = active ? DecisionAssistant.createStagedSession(active,DATA.assistants,false) : null;
let decisionTrail=[];
let browseOrigin=null;
let focusedCriteria=null;
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
 return `<footer><b>Suitability for liver transplantation and eligibility for MELD-exception points are assessed separately.</b> This draft supports, but does not replace, specialist judgment and the center’s full transplant evaluation. Proposed local decisions are not institutional approvals.<br><span>Source review: October 17–25, 2026 · OPTN policies checked October 24, 2026 (effective October 1, 2026) · NLRB guidance: December 2025. Check current requirements when submitting an exception request.</span></footer>`;
}

function home() {
 app.innerHTML = header()+`<main class="wrap home"><div class="homehero"><div><p class="eyebrow">Diagnosis → selection → disease control → transplant</p><h1>Liver transplant assessment and treatment pathways</h1><p class="lead">Transplant oncology pathways with the information to collect, the findings that change treatment or transplant plans, and the evidence beside each decision.</p></div><div class="how"><b>How to use the pathways</b><ol><li>Choose the tumor and current decision.</li><li>Compare the possible results, selection criteria and next steps.</li><li>Expand the supporting evidence or open a linked discussion question.</li><li>Use Tools & resources for calculators or optional step-by-step findings.</li></ol></div></div>
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
   p.issues.forEach(i=>{if((i.question+' '+i.proposal).toLowerCase().includes(q))found.push(`<a class="search-result" href="/mh-liver-pathways/transplant/${p.slug}/#meeting-${i.id}"><span class="tag amber">${e(p.code)} · meeting question</span><b>${e(i.question)}</b><span>Compare sources →</span></a>`);});
  });
  document.getElementById('search-count').textContent=`${found.length} matching decisions or meeting questions`;
  results.innerHTML=found.length?found.join(''):'<p class="empty">No match. Try a tumor name or a shorter clinical term.</p>';
 });
}

function pathwayShell() {
 app.innerHTML=header()+`<main class="wrap"><div class="pathhero"><div><a class="back" href="/mh-liver-pathways/transplant/">← All pathways</a><p class="eyebrow">${e(active.route)}</p><h1>${e(active.name)}</h1><p class="lead">${e(active.entry)}</p></div><div class="herolinks">${active.roadmap?external(active.roadmap,`${active.code} treatment roadmap`,'btn secondary'):external(DATA.sources['E-consensus'].pdf,'HEHE treatment consensus','btn secondary')}</div></div>
 <div class="viewbar" role="tablist" aria-label="Pathway sections"><button role="tab" id="tab-pathway" data-view="pathway">Decision pathway</button><button role="tab" id="tab-meeting" data-view="meeting">Meeting record <span>${active.issues.length}</span></button><button role="tab" id="tab-care" data-view="care">Treatment reference</button><button role="tab" id="tab-high-risk" class="high-risk-tab" data-view="high-risk">High-risk protocols <span>${HighRisk.reviews(DATA.high_risk,active.slug).length}</span></button><button role="tab" id="tab-evidence" data-view="evidence">Evidence library</button><span class="viewnote">Compare choices · nothing is saved</span></div>
 <div id="view"></div></main>`+footer();
 renderView();
}

function decisionLabel(id){const step=active.steps.find(s=>s.id===id),key=active.slug+'/'+id;return ['listing','waitlist','review'].includes(id)?'Transplant waitlisted':window.DecisionWorkspaceData?.protocolNavigation?.[key]?.label||step?.title||id;}
function laterFindingSummary(index){const groups=active.steps.slice(index+1).map(s=>{const key=active.slug+'/'+s.id;return {label:decisionLabel(s.id),count:Object.values(assistantSession.answers[key]||{}).filter(Boolean).length+Object.values(riskContext[key]||{}).filter(Boolean).length};}).filter(x=>x.count);const count=groups.reduce((n,x)=>n+x.count,0);return count?count+' later finding'+(count===1?'':'s')+' in '+[...new Set(groups.map(x=>x.label))].join(', '):'';}
function announceAssessmentSwitch(from,cleared=''){if(!from&&!cleared)return;const note=document.createElement('p');note.className='sr-only';note.setAttribute('role','status');note.setAttribute('aria-live','polite');note.textContent=(from?'Current assessment changed to '+decisionLabel(active.steps[stepIndex].id)+'. ':'')+'Finding recorded.'+(cleared?' Cleared '+cleared+'.':'');document.querySelector('.decision')?.append(note);}
function renderView(){
 document.body.dataset.pathwayView=view;
 document.querySelectorAll('.viewbar [role="tab"]').forEach(t=>t.setAttribute('aria-selected',t.dataset.view===(view==='risk-reference'?'high-risk':view)?'true':'false'));
 const out=document.getElementById('view');
 out.setAttribute('role','tabpanel');out.setAttribute('aria-labelledby','tab-'+(view==='risk-reference'?'high-risk':view));
 const content=view==='pathway'?renderStep():view==='meeting'?renderMeeting():view==='evidence'?renderEvidence():view==='high-risk'?HighRisk.overview(DATA.high_risk,active.slug):view==='risk-reference'?renderRiskReference():renderCare();
 out.innerHTML=(view==='pathway'?renderOverview():'')+renderNavigation()+content;
 if(view==='pathway'){updateDecision();if(browseOrigin){const origin=active.steps.find(s=>s.id===browseOrigin);const note=document.createElement('p');note.className='dw-browse-note';note.innerHTML=`Viewing: <b>${e(decisionLabel(active.steps[stepIndex].id))}</b> · Current: ${e(decisionLabel(browseOrigin))}. <span>Use finding records your choice and makes this the current assessment.${laterFindingSummary(stepIndex)?' Recording here clears '+e(laterFindingSummary(stepIndex))+'.':''}</span> <button type="button" data-step="${e(browseOrigin)}" data-dw-browse>Return to ${e(decisionLabel(browseOrigin))}</button>`;document.querySelector('.question-head')?.after(note);}}else if(view==='care')renderLayerStack();
 navigationObserver?.disconnect();
 navigationObserver=new ResizeObserver(syncNavigationHeight);
 const nav=out.querySelector('.pathway-nav');if(nav)navigationObserver.observe(nav);if(!['pathway','care'].includes(view))renderLayerStack();
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
 if(Object.values(assistantSession.presets||{}).some(a=>Object.keys(a).length))return ['Entry example selected','Only the first finding is preselected toward transplant. Choose each later finding; changing an earlier choice clears later choices.'];
 if(origins.every(x=>x==='empty'))return ['Choose the first finding','Each new decision starts unanswered. Choices stay in this page only.'];
 return ['Your decision trail','Earlier choices stay above the current decision. Change an earlier finding to explore a different path.'];
}

function renderOverview(){
 const status=exampleStatus();
 return `<section class="journey-overview" aria-labelledby="journey-title"><div class="journey-heading"><div><p class="eyebrow">The whole pathway</p><h2 id="journey-title">From diagnosis to transplant and follow-up</h2></div><a href="#care-treatment" data-care="treatment" class="journey-alternative">Browse treatment options →</a></div>
 <div class="journey-map"><p class="journey-hint">Preview any decision without changing your findings.</p><nav class="journey-phases" aria-label="All clinical decisions">${DATA.journeys[active.slug].map(phase=>`<section class="journey-phase"><h3>${e(phase.title)}</h3><div class="journey-steps">${phase.steps.map(id=>{const n=active.steps.findIndex(s=>s.id===id),step=active.steps[n],current=n===stepIndex;return `<button type="button" data-step="${e(id)}" class="journey-step ${current?'current':''}" ${current?'aria-current="step"':''}><span class="phase-number">${n+1}</span><span>${e(step.title)}</span></button>`;}).join('')}</div></section>`).join('')}</nav></div>
 <div class="example-controls"><div><strong data-example-status aria-live="polite">${e(status[0])}</strong><p data-example-description>${e(status[1])}</p></div><div class="example-buttons"><button data-pathway-example>Show entry example</button><button data-pathway-clear>Clear all choices</button></div></div></section>`;
}

function renderNavigation(){
 return `<div class="pathway-nav layer-nav" aria-label="Decision trail"><div class="layer-heading"><b>${e(active.code)} · Decision trail</b><button data-pathway-overview>All decisions</button></div><div id="layer-history" class="layer-history"></div><div id="layer-current" class="layer-current"></div></div>`;
}
function layerQuestionRow(step,q,value,number,example=false,risk=false){
 const key=active.slug+'/'+step.id,short=window.ContextualCopy?.help?.[key+'/'+q.id]?.label||q.label;
 const selected=q.options.find(o=>o.value===value),id='layer-'+(risk?'risk-':'')+step.id+'-'+q.id;
 const decision=active.steps.findIndex(s=>s.id===step.id)+1;
 const help=window.ContextualCopy?.help?.[key+'/'+q.id]?.concise||q.help||'';
 return `<div class="layer-row ${value?'is-chosen':'is-current'}"><span class="layer-number" title="Decision ${decision}">${decision}</span><div class="layer-choice"><label for="${e(id)}"><small>Decision ${decision} · ${e(step.title)}${example?' · entry example':''}${risk?' · safety / individual review':''}</small>${e(short)}</label>${help?`<p class="layer-help" id="${e(id)}-help">${e(help)}</p>`:''}<select id="${e(id)}" ${help?`aria-describedby="${e(id)}-help"`:''} data-committed="${e(value)}" data-layer-step="${e(step.id)}" data-layer-${risk?'risk':'question'}="${e(q.id)}"><option value="">Choose a finding…</option>${q.options.map(o=>`<option value="${e(o.value)}" ${o.value===value?'selected':''}>${e(o.label)}</option>`).join('')}</select><span class="layer-stage-status" role="status" hidden></span>${selected?`<span class="layer-value">${e(selected.label)}</span>`:''}</div><div class="layer-controls"><button class="layer-apply" data-record-finding="${e(id)}" disabled>${value?'Apply change':'Use finding'}</button><button class="layer-cancel" data-cancel-finding="${e(id)}" hidden>Cancel</button><button class="layer-criteria" data-layer-criteria="${e(q.id)}" data-layer-step="${e(step.id)}" ${risk?'data-risk-criteria':''}>Criteria &amp; sources</button></div></div>`;
}
function stageFinding(select){
 const row=select.closest('.layer-row'),staged=select.value!==select.dataset.committed;
 row.classList.toggle('is-staged',staged);row.querySelector('[data-record-finding]').disabled=!staged;row.querySelector('[data-cancel-finding]').hidden=!staged;
 const status=row.querySelector('.layer-stage-status'),current=[...select.options].find(o=>o.value===select.dataset.committed)?.textContent;
 status.hidden=!staged;status.textContent=staged?'Not applied — current: '+(select.dataset.committed?current:'no finding recorded')+'.':'';
 const q=DATA.assistants[active.slug+'/'+select.dataset.layerStep]?.questions.find(q=>q.id===select.dataset.layerQuestion);
 const definitions=document.querySelector(`.assistant-question:not([hidden]) [data-definitions="${select.dataset.layerQuestion}"]`);
 if(q&&definitions)definitions.innerHTML=(staged?'<p class="layer-stage-status">Definitions for the unapplied selection; the result below still uses recorded findings.</p>':'')+DecisionAssistant.definitions(q,select.value,DATA.sources);
 syncNavigationHeight();
}
function renderLayerStack(){
 const historyEl=document.getElementById('layer-history'),currentEl=document.getElementById('layer-current');if(!historyEl)return;
 if(view==='care'&&!currentCareOrigin()){historyEl.innerHTML='';currentEl.innerHTML='<div class="layer-care"><b>Care reference · no findings attached</b><button data-view="pathway">Decision choices →</button></div>';return;}
 if(!['pathway','care'].includes(view)){historyEl.innerHTML='';currentEl.innerHTML='<button data-view="pathway">Return to decision choices →</button>';return;}
 const coreResult=view==='pathway'?DecisionAssistant.evaluate(assistantConfig(),assistantSession.answers[assistantKey()],active.steps[stepIndex].branches):null;
 const stopEarly=coreResult?.state==='matched'&&coreResult.kind==='stop';
 const current=active.steps[stepIndex],visited=[...new Set([...decisionTrail,...(browseOrigin?[browseOrigin]:[])])].filter(id=>id!==current.id).concat(current.id).sort((a,b)=>active.steps.findIndex(s=>s.id===a)-active.steps.findIndex(s=>s.id===b));let chosen='',pending='',n=0;
 for(const id of visited){const step=active.steps.find(s=>s.id===id);if(!step)continue;const key=active.slug+'/'+id,config=DATA.assistants[key],answers=assistantSession.answers[key];
  for(const q of (id===current.id&&stopEarly?config.questions.filter(q=>answers[q.id]):DecisionAssistant.visibleQuestions(config,answers))){
   const value=answers[q.id]||'';
   if(id!==current.id&&!value)continue;
   const row=layerQuestionRow(step,q,value,++n,assistantSession.presets?.[key]?.[q.id]===value);
   if(value)chosen+=row;else if(view==='pathway')pending=row;
  }
  if((id!==current.id||view==='care')&&riskContext[key]){
   const index=active.steps.findIndex(s=>s.id===id),extra=RiskRouting.evaluate(active,index,assistantSession,riskContext,DATA.assistants).questions;
   for(const question of extra){const value=riskContext[key][question.id];if(!value)continue;const q={...question,options:question.options.map(([value,label])=>({value,label}))};chosen+=layerQuestionRow(step,q,value,++n,false,true);}
  }
 }
 // Additional high-risk and safety findings join the same sequential trail.
 if(view==='pathway'){
  const coreDone=assistantConfig().questions.every(q=>!!assistantSession.answers[assistantKey()][q.id]);
  const riskRows=[...document.querySelectorAll('#risk-question-panel .risk-question')];let riskPending=false;
  riskRows.forEach(node=>{const select=node.querySelector('select'),id=select.dataset.riskQuestion,value=riskContext[assistantKey()]?.[id]||'';select.value=value;
   const allowed=coreDone&&!riskPending&&!stopEarly;node.hidden=!allowed;select.classList.add('layer-source-select');node.classList.add('layer-question-detail');
   if(stopEarly){node.hidden=false;select.classList.remove('layer-source-select');select.dataset.committed=value;const apply=document.createElement('button');apply.type='button';apply.className='layer-apply';apply.dataset.recordRisk=id;apply.textContent='Use finding';apply.disabled=true;node.append(apply);return;}
   if(!allowed)return;
   const q={id,label:node.querySelector('label').textContent,help:node.querySelector('p')?.textContent||'',options:[...select.options].slice(1).map(o=>({value:o.value,label:o.textContent}))};
   const row=layerQuestionRow(current,q,value,++n,false,true);
   if(value){chosen+=row;node.hidden=true;}else{pending=row;riskPending=true;}
  });
  const riskSection=document.querySelector('.risk-questions');if(riskSection)riskSection.hidden=!riskRows.some(n=>!n.hidden);
 }
 const historyOpen=historyEl.querySelector('details')?.open||false;
 const count=(chosen.match(/class="layer-row/g)||[]).length;
 historyEl.innerHTML=chosen?`<details class="layer-history-disclosure" ${historyOpen?'open':''}><summary>Selected findings (${count}) · review or change</summary><div class="layer-history-rows">${chosen}</div></details>`:'';
 if(view==='pathway'){
  const config=assistantConfig(),answers=assistantSession.answers[assistantKey()],visible=DecisionAssistant.visibleQuestions(config,answers),last=visible[visible.length-1];
  const riskPending=!!document.querySelector('#risk-question-panel .risk-question:not([hidden])');
  const display=focusedCriteria||(!riskPending?(stopEarly?config.questions.filter(q=>answers[q.id]).at(-1)?.id:last.id):null);
  document.querySelectorAll('.assistant-question').forEach(node=>{const id=node.querySelector('select').dataset.assistantQuestion;node.hidden=id!==display;node.classList.add('layer-question-detail');node.querySelector('select').classList.add('layer-source-select');});
  // Recorded threshold definitions remain visible while the next finding is answered.
  document.querySelector('.recorded-criteria')?.remove();
  const definitions=config.questions.filter(q=>answers[q.id]&&q.id!==display).map(q=>{
   const criteria=q.criteria.filter(c=>!c.show_for.length||c.show_for.includes(answers[q.id]));
   if(!criteria.length&&!q.options.find(o=>o.value===answers[q.id])?.details?.length)return '';
   return DecisionAssistant.definitions({...q,criteria},answers[q.id],DATA.sources);
  }).join('');
  if(definitions){const group=document.createElement('section');group.className='recorded-criteria';group.innerHTML='<h4>Criteria behind recorded findings</h4>'+definitions;document.querySelector('.assistant-intro').after(group);}
  const allAnswered=config.questions.every(q=>!!answers[q.id]);
  // Navigation is not another patient finding. Actions appear once, with their
  // conditions in the result below; never ask the reader to select a sole route.
  if((allAnswered&&!riskPending)||stopEarly)pending=`<div class="layer-complete"><span>Decision ${stepIndex+1} · findings recorded</span><button data-layer-options>View result &amp; next actions ↓</button></div>`;
 }else pending=`<div class="layer-care"><b>Care plan: ${e(DATA.care[active.slug].find(c=>c.id===careId)?.title||careId)}</b><button data-view="pathway">Review findings</button></div>`;
 if(view==='pathway'){
  const missingRisk=!stopEarly&&!!document.querySelector('#risk-question-panel .risk-question:not([hidden])');
  const result=document.getElementById('current-result');result.querySelector('.layer-missing-note')?.remove();
  if(missingRisk&&coreResult.kind==='advance'){const note=document.createElement('p');note.className='layer-missing-note';note.textContent='Choose the remaining finding above before continuing to the next assessment.';result.prepend(note);}
  result.querySelectorAll('.next-action button[data-step]').forEach(button=>{button.disabled=!!(missingRisk&&coreResult.kind==='advance'&&active.steps.findIndex(s=>s.id===button.dataset.step)>stepIndex);});
 }
 currentEl.innerHTML=pending;
 document.querySelector('.pathway-nav').classList.toggle('has-layer-history',!!chosen);

 syncNavigationHeight();
}
function editLayer(stepId,id,value){
 const index=active.steps.findIndex(s=>s.id===stepId);if(index<0)return;
 const cleared=laterFindingSummary(index);
 const changed=DecisionAssistant.changeStagedAnswer(assistantSession,active,DATA.assistants,index,id,value);if(!changed)return;
 const priorAssessment=browseOrigin;browseOrigin=null;
 if(priorAssessment&&active.steps.findIndex(s=>s.id===priorAssessment)<index&&!decisionTrail.includes(priorAssessment))decisionTrail.push(priorAssessment);
 const found=decisionTrail.indexOf(stepId);if(found>=0)decisionTrail=decisionTrail.slice(0,found);
 else decisionTrail=decisionTrail.filter(x=>active.steps.findIndex(s=>s.id===x)<index);
 stepIndex=index;view='pathway';focusedCriteria=null;RiskRouting.clearFrom(riskContext,active,index);
 history.replaceState(null,'','#'+stepId);renderView();announceAssessmentSwitch(priorAssessment,cleared);
 const next=document.querySelector('#layer-current select')||document.querySelector('#current-result h4');if(next){if(next.tagName!=='SELECT')next.setAttribute('tabindex','-1');next.focus({preventScroll:true});}
}
function recordRiskFinding(step,id,value){
 const priorAssessment=browseOrigin;browseOrigin=null;document.querySelector('.dw-browse-note')?.remove();
 const index=active.steps.findIndex(s=>s.id===step);if(index<0)return;
 const cleared=laterFindingSummary(index);
 if(priorAssessment&&active.steps.findIndex(s=>s.id===priorAssessment)<index&&!decisionTrail.includes(priorAssessment))decisionTrail.push(priorAssessment);
 if(index!==stepIndex){const found=decisionTrail.indexOf(step);decisionTrail=found>=0?decisionTrail.slice(0,found):[];stepIndex=index;view='pathway';history.replaceState(null,'','#'+step);renderView();}
 const key=assistantKey();riskContext[key]||={};
 const questions=[...document.querySelectorAll('#risk-question-panel [data-risk-question]')].map(n=>n.dataset.riskQuestion),position=questions.indexOf(id);
 questions.slice(position+1).forEach(q=>delete riskContext[key][q]);riskContext[key][id]=value;
 if(id==='ici')delete riskContext[key].ici_review;
 RiskRouting.clearFrom(riskContext,active,stepIndex+1);DecisionAssistant.clearFrom(assistantSession,active,stepIndex+1);assistantSession.origins[key]='edited';
 focusedCriteria=null;updateDecision();announceAssessmentSwitch(priorAssessment,cleared);document.querySelector('#layer-current select')?.focus({preventScroll:true});
}
function showLayerCriteria(stepId,id,riskQuestion=false){
 const index=active.steps.findIndex(s=>s.id===stepId);if(index<0)return;
 if(index!==stepIndex){const found=decisionTrail.indexOf(stepId);decisionTrail=found>=0?decisionTrail.slice(0,found):[];stepIndex=index;view='pathway';history.pushState(null,'','#'+stepId);}
 focusedCriteria=id;renderView();
 const risk=riskQuestion?document.getElementById('risk-'+id)?.closest('.risk-question'):null;if(risk){risk.hidden=false;risk.closest('.risk-questions').hidden=false;risk.scrollIntoView({block:'start',behavior:'instant'});return;}
 const node=document.querySelector(`[data-definitions="${id}"]`),details=node?.querySelector('details[data-relevant="true"]')||node?.querySelector('details');if(details)details.open=true;
 const target=details?node?.closest('.assistant-question'):document.querySelector('.assistant-question:not([hidden]) .assistant-help-criteria')||document.querySelector('.full-tests');if(target?.tagName==='DETAILS')target.open=true;target?.scrollIntoView({block:'start',behavior:'instant'});target?.querySelector('summary')?.focus({preventScroll:true});
}

function updateExampleLabels(){
 const status=exampleStatus();
 const title=document.querySelector('[data-example-status]'),description=document.querySelector('[data-example-description]');
 if(title)title.textContent=status[0];if(description)description.textContent=status[1];
 const origin=assistantSession.origins[assistantKey()];
 const label=document.querySelector('[data-selection-label]');
 if(label)label.textContent=origin==='example'?'Example choices':origin==='edited'?'Choices changed':'Choices needed';
 const intro=document.querySelector('.assistant-intro');
 if(intro)intro.textContent=origin==='example'?'The first finding is a transplant-oriented example. Each later finding needs a choice.':origin==='edited'&&stepIndex<active.steps.length-1?'Choose the next unanswered finding. Earlier choices remain above.':'Choose the findings that matter for this decision. The matching next step will be highlighted.';
}

function highRiskAction(a){
 const target=HighRisk.destination(a.url);
 if(!target||target.slug&&target.slug!==active.slug)return external(a.url,a.label,'route-button');
 return `<a class="route-button high-risk-route" href="#high-risk${target.id?'-'+e(target.id):''}" ${target.id?`data-high-risk="${e(target.id)}"`:'data-view="high-risk"'}><small>High-risk protocol · ${e(HighRisk.statusLabel(target.id))}</small>${e(a.label)} →</a>`;
}
function renderActions(actions){
 // Distinct clinical choices stay distinct even when they open the same care page.
 const seen=new Set();
 return `<div class="next-actions">${(actions||[]).filter(a=>{const key=JSON.stringify([a.step,a.care,a.url,a.label,a.detail]);if(seen.has(key))return false;seen.add(key);return true;}).map(a=>`<div class="next-action">${a.detail?`<p>${e(a.detail)}</p>`:''}${a.step?`<button class="route-button" data-step="${e(a.step)}">${e(a.label.replace(/^Continue: /,''))} →</button>`:a.care?`<a class="route-button" href="#care-${e(a.care)}" data-care="${e(a.care)}" data-action-label="${e(a.label)}" data-action-condition="${e(a.detail||'')}">${e(a.label)} →</a>`:highRiskAction(a)}</div>`).join('')}</div>`;
}

function afpReviewHTML(finding){
 if(!finding)return '';
 return `<details class="risk-next-option ${finding.deferred?'risk-neutral':'risk-proposed'}" data-afp-review><summary><span class="risk-next-status">High-risk HCC review · individual assessment</span><b>AFP criterion not met: review transplant options</b><span class="risk-trigger">${finding.carried?'From decision '+(active.steps.findIndex(s=>s.id===finding.origin)+1)+': ':''}${e(finding.why)}</span><span class="risk-open-label">Open the AFP review and supporting guidance ↓</span></summary><div class="risk-next-body"><p><b>Review remains an option.</b> An unmet AFP requirement prevents a standardized exception; it does not by itself end the transplant assessment. Review AFP history and trend, treatment response, staging, liver reserve and expected transplant benefit.</p><p>OPTN Policy 9.5.I.iv sends the specified AFP nonresponse cases to individual NLRB review. The transplant-oncology guidance says these cases are generally unfavorable for exception approval, but selected cases may be appropriate.</p><p><a href="#high-risk-hcc-b1-1" data-high-risk="hcc-b1-1">HCC B1.1: full-text evidence and OPEN proposed thresholds</a> · <a href="/mh-liver-pathways/transplant/meeting-records/hcc-b1-1/">B1.1a–f meeting decisions</a></p><p>This is an individual high-risk review route. The existing beyond-UNOS tumor-burden study has separate entry limits, including AFP &lt;100; it is not an AFP-only expansion protocol.</p><p>${external('https://www.hrsa.gov/sites/default/files/hrsa/optn/optn_policies.pdf#page=197','OPTN Policy 9.5.I.iv · PDF pp197–198')} · ${external('https://www.hrsa.gov/sites/default/files/hrsa/optn/adult-meld-exception-transplant-oncology-review-guidance.pdf#page=3','NLRB HCC guidance · PDF p3')}</p>${renderActions([{label:'High-risk HCC and individual allocation assessment',care:'exception'},{label:'Continue or change HCC treatment',care:'treatment'},{label:'Recheck the AFP requirement',step:finding.origin}])}</div></details>`;
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
  return `<details class="risk-next-option ${ordinary?'risk-neutral':'risk-proposed'}" data-risk-anchor="${e(o.anchor)}" data-risk-mode="${e(o.mode)}"><summary><span class="risk-next-status">${e(descriptions[o.mode])}</span><b>${e(record.title)}</b><span class="risk-trigger">${o.carried?'From decision '+(active.steps.findIndex(s=>s.id===o.origin)+1)+': ':'Selected finding: '}${e(o.reason)}</span>${o.anchor==='hehe-b2'?'<span class="risk-trigger">National guidance permits case-level review; this narrower local proposal is not approved.</span>':''}<span class="risk-open-label">${ordinary?'Read the relevant criteria and evidence':'Review this option, criteria and evidence'} ↓</span></summary><div class="risk-next-body"><button class="risk-change" data-step="${e(o.origin)}">Review the triggering finding →</button>${HighRisk.card(DATA.high_risk,active.slug,{...record,steps:[active.steps[stepIndex].id]})}</div></details>`;
 }).join('');
}
function canContinueIndividualReview(context){
 // A closed local option cannot supply the next protocol step. Inactive study
 // proposals also need approval even when their display mode is review/readiness.
 return !context.guard&&!context.options.some(o=>o.mode==='closed'||['pcca-b1','pcca-b3','icca-b1','icca-b2','icca-b3'].includes(o.anchor));
}
function isReadinessOnlyReview(context){
 return !context.guard&&context.options.length>0&&context.options.every(o=>o.anchor==='icca-b3'&&o.mode==='readiness');
}
function updateDecision(){
 document.body.dataset.currentAssessment=browseOrigin||active.steps[stepIndex].id;
 const out=document.getElementById('view');
 out.querySelectorAll('.risk-next-options').forEach(node=>node.remove());
 const result=DecisionAssistant.update(out,assistantConfig(),assistantSession.answers[assistantKey()],active.steps[stepIndex].branches,DATA.sources,assistantSession.origins[assistantKey()]);
 const evaluatedContext=RiskRouting.evaluate(active,stepIndex,assistantSession,riskContext,DATA.assistants);
 // Interest in a living-donor study does not remove an otherwise valid standard route.
 const context=isReadinessOnlyReview(evaluatedContext)?{...evaluatedContext,route:null}:evaluatedContext;
 out.querySelector('#risk-question-panel').innerHTML=RiskRouting.renderQuestions(context.questions,riskContext[assistantKey()]);
 // An unresolved upstream exclusion cannot be cleared by a later favorable example.
 const reviewContext=context.guard||context.route;
 const override=reviewContext&&result.kind==='advance';
 if(override){
  out.querySelectorAll('[data-branch-index]').forEach(card=>{card.classList.remove('is-highlighted');card.classList.add('is-muted');card.removeAttribute('aria-current');card.querySelector('.branch-match').hidden=true;});
  const feedback=out.querySelector('.assistant-feedback');feedback.className='assistant-feedback sr-only hold';feedback.textContent=(context.guard?'Further review needed. ':'Individual review route. ')+reviewContext.why;
 }
 updateExampleLabels();
 const onward=DATA.continuations[assistantKey()];
 out.querySelectorAll('[data-next-branch]').forEach(el=>{el.innerHTML=el.closest('.is-highlighted')?renderActions(onward.branches[el.dataset.nextBranch]):'';});
 const extra=out.querySelector('.assistant-other-result');
 if(override){
  extra.hidden=false;extra.className='assistant-other-result branch hold is-highlighted';
  const actions=[{label:'Review the triggering finding',step:reviewContext.origin},{label:'Review treatment and continuing care',care:'treatment'}];
  if(active.slug==='hcc')actions.push({label:'Review individual exception assessment and treatment options',care:'exception'});
  if(canContinueIndividualReview(context)&&active.steps[stepIndex+1])actions.push({label:'Next decision for individual review: '+active.steps[stepIndex+1].title,step:active.steps[stepIndex+1].id});
  extra.innerHTML=`<span class="branch-match">${context.guard?'Additional review required':'Individual review route'}</span><h4>${context.guard?'Resolve the selection or safety issue':'Continue case-specific assessment'}</h4><p>${e(reviewContext.why)}</p><h5 class="next-heading">Choose the next action</h5>${renderActions(actions)}`;
 }else if(!extra.hidden){
  const noAnswers=Object.values(assistantSession.answers[assistantKey()]).every(v=>!v);
  const actions=result.state==='matched'?onward.rules[String(result.ruleIndex)]:noAnswers?[]:onward.clarify;
  if(actions.length)extra.insertAdjacentHTML('beforeend',`<h5 class="next-heading">Choose the next action</h5>${renderActions(actions)}`);
 }
 if(result.state==='pending'&&extra.hidden){
  extra.hidden=false;extra.className='assistant-other-result branch pending is-highlighted';
  extra.innerHTML=`<span class="branch-match">Choices needed</span><h4>${e(result.title)}</h4><p>${e(result.text)}</p>${Object.values(assistantSession.answers[assistantKey()]).some(Boolean)?renderActions(onward.clarify):''}`;
 }
 const content=riskOptionsHTML({...context,showGuard:!override});
 if(content){
  let destination=(!extra.hidden?extra:out.querySelector('[data-branch-index].is-highlighted'));
  if(!destination){extra.hidden=false;extra.className='assistant-other-result branch hold is-highlighted';extra.innerHTML=`<h4>Clarify the selected findings</h4><h5 class="next-heading">Choose the next action</h5>${renderActions(onward.clarify)}`;destination=extra;}
  destination.insertAdjacentHTML('beforeend',`<div class="risk-next-options">${content}</div>`);
 }
 streamlineResult(out,result,context);
 renderLayerStack();
 return result;
}
function streamlineResult(out,result,context){
 const current=out.querySelector('#current-result'),other=out.querySelector('#other-result-list');
 const extra=out.querySelector('.assistant-other-result');
 const selected=!extra.hidden?extra:out.querySelector('[data-branch-index].is-highlighted');
 out.querySelectorAll('.selected-basis').forEach(el=>el.remove());
 out.querySelectorAll('[data-branch-index]').forEach(card=>{
  const matched=card===selected;
  (matched?current:other).append(card);
  card.querySelector('.branch-action').hidden=!matched;
  card.querySelector('[data-next-branch]').hidden=!matched;
  const branch=active.steps[stepIndex].branches[Number(card.dataset.branchIndex)];
  const kind=branch.kind;card.querySelector('h4').textContent=branch.title;
  const superseded=result.branch===Number(card.dataset.branchIndex)&&!matched;
  card.querySelector('.route-label').textContent=matched?({advance:'Continue assessment',hold:'Clarify before continuing',redirect:'Review another route',stop:'Review treatment options'}[kind]):superseded?'Matches these answers; another finding or safety review takes priority':'Reference · applies to different findings';
  if(!matched){card.classList.remove('is-highlighted');card.classList.add('is-muted');card.removeAttribute('aria-current');card.querySelector('.branch-match').hidden=true;}
 });
 if(selected===extra)current.append(extra);else current.prepend(extra);
 if(selected){
  const config=assistantConfig(),answers=assistantSession.answers[assistantKey()];
  const when=config.rules[result.ruleIndex]?.when;
  const ids=when?Object.keys(when):config.questions.filter(q=>answers[q.id]).map(q=>q.id);
  const facts=ids.map(id=>{const q=config.questions.find(q=>q.id===id);const label=q?.options.find(o=>o.value===answers[id])?.label;return label?q.label.replace(/\?$/,'')+': '+label:q?.label;}).filter(Boolean);
  context.questions.forEach(q=>{const value=riskContext[assistantKey()]?.[q.id];const label=q.options.find(o=>o[0]===value)?.[1];if(label)facts.push(q.label.replace(/\?$/,'')+': '+label);});
  if(facts.length&&result.kind!=='advance'&&Object.values(answers).some(Boolean))selected.insertAdjacentHTML('afterbegin',`<p class="selected-basis"><b>${assistantSession.origins[assistantKey()]==='example'?'Example findings':'Selected findings'}</b> ${[...new Set(facts)].map(e).join(' · ')}</p>`);
  // The grouped source title remains in the reference; show the actual selected reason here.
  if(assistantKey()==='icca/phenotype'&&result.branch===1&&selected!==extra)selected.querySelector('h4').textContent='Review the selected finding outside the standard criteria';
 }
 const disclosure=out.querySelector('.other-results');
 disclosure.hidden=!other.children.length;
 disclosure.querySelector('[data-other-count]').textContent=other.children.length;
 // Remove exact repeated actions only; different treatments may share a care page.
 const seen=new Map();
 current.querySelectorAll('.route-button').forEach(link=>{
  const key=link.dataset.step?'step:'+link.dataset.step:link.dataset.care?'care:'+link.dataset.care:link.getAttribute('href');
  if(!key)return;
  const actionKey=key+'|'+link.textContent.trim();
  if(seen.has(actionKey)){const box=link.closest('.next-action');if(box)box.remove();else link.remove();}else seen.set(actionKey,link);
 });
 // The nested AFP review repeats navigation, not distinct treatment choices.
 // Keep those choices in the main result and retain only new destinations here.
 const destination=link=>link.dataset.step?'step:'+link.dataset.step:link.dataset.care?'care:'+link.dataset.care:link.getAttribute('href');
 const mainDestinations=new Set([...current.querySelectorAll('.route-button')].filter(link=>!link.closest('[data-afp-review]')).map(destination));
 current.querySelectorAll('[data-afp-review] .route-button').forEach(link=>{if(mainDestinations.has(destination(link)))link.closest('.next-action').remove();});
 current.querySelectorAll('[data-afp-review] .next-actions:empty').forEach(el=>el.remove());
}

function renderRiskReference(){
 const records=HighRisk.reviews(DATA.high_risk,active.slug);
 const record=records.find(r=>r.anchor===riskReference);
 const content=record?HighRisk.card(DATA.high_risk,active.slug,record):riskReference==='readiness'?DATA.high_risk.readiness.map(r=>HighRisk.card(DATA.high_risk,active.slug,r,true)).join(''):'';
 return `<section class="risk-reference"><div class="risk-reference-note"><b>Reference view</b><p>Opening this reference does not match it to the selected findings. In the decision pathway, specific reviews appear with the relevant next-step choices.</p><button data-step="${e(active.steps[stepIndex].id)}">Return to the decision →</button></div>${content||HighRisk.overview(DATA.high_risk,active.slug)}</section>`;
}

// Navigation context is in memory only. URLs/history carry an opaque token, never findings.
let careOrigins=new Map(),careOriginToken=null,careSequence=0;
const canonicalChoices=value=>Object.fromEntries(Object.entries(value||{}).sort(([a],[b])=>a.localeCompare(b)));
function clearCareOrigins(){careOrigins.clear();careOriginToken=null;}
function careFingerprint(origin){
 const end=active.steps.findIndex(s=>s.id===origin);
 return JSON.stringify(active.steps.slice(0,end+1).map(s=>{const key=active.slug+'/'+s.id;return [canonicalChoices(assistantSession.answers[key]),assistantSession.origins[key],canonicalChoices(riskContext[key])];}));
}
function currentCareOrigin(){
 const origin=careOrigins.get(careOriginToken);
 return origin&&origin.care===careId?origin:null;
}
function captureCareOrigin(trigger){
 if(view!=='pathway'||!trigger.closest('#current-result'))return null;
 const action=trigger.closest('.next-action'),result=trigger.closest('.branch,.assistant-other-result');
 const step=active.steps[stepIndex],key=assistantKey(),answers=assistantSession.answers[key]||{};
 return {step:step.id,care:trigger.dataset.care,title:step.title,number:stepIndex+1,
  option:trigger.dataset.actionLabel||trigger.textContent.trim().replace(/\s*→$/,''),condition:trigger.dataset.actionCondition??action?.querySelector(':scope > p')?.textContent??'',
  kind:result?.classList.contains('hold')?'hold':result?.classList.contains('stop')?'stop':'review',
  result:result?.querySelector('.branch-title h4,h4')?.textContent||'',
  status:result?.querySelector('.route-label')?.textContent||(result?.classList.contains('hold')?'Hold at the originating decision':result?.classList.contains('stop')?'Stop and review at the originating decision':result?.querySelector('.branch-match')?.textContent||''),
  example:assistantSession.origins[key]==='example',fingerprint:careFingerprint(step.id),
  reviews:[...document.querySelectorAll('#current-result [data-risk-anchor],#current-result [data-afp-review]')].map(n=>({anchor:n.dataset.riskAnchor||'hcc-b1-1',title:n.querySelector('summary>b')?.textContent||'AFP criterion not met: review transplant options',status:n.querySelector('.risk-next-status')?.textContent||''})),
  choices:assistantConfig().questions.filter(q=>answers[q.id]).map(q=>({question:q.label,answer:q.options.find(o=>o.value===answers[q.id])?.label||answers[q.id]}))};
}
function showCare(trigger){
 const nextId=trigger.dataset.care;if(!DATA.care[active.slug].some(p=>p.id===nextId))return;
 const original=currentCareOrigin();
 let origin=captureCareOrigin(trigger);
 if(!origin&&view==='care'&&original&&original.fingerprint===careFingerprint(original.step)){
  origin={...original,care:nextId,via:careId,option:trigger.textContent.trim().replace(/\s*→$/,''),condition:trigger.closest('.next-action')?.querySelector(':scope > p')?.textContent||''};
 }
 careId=nextId;careOriginToken=origin?'care-'+(++careSequence):null;
 if(origin){careOrigins.set(careOriginToken,origin);while(careOrigins.size>24)careOrigins.delete(careOrigins.keys().next().value);}
 view='care';history.pushState({careToken:careOriginToken},'','#care-'+careId);renderView();
 document.getElementById('care-title').focus({preventScroll:true});document.querySelector('.care-view').scrollIntoView({block:'start',behavior:'instant'});
}
function careOriginHTML(){
 const o=currentCareOrigin();
 if(!o)return `<p class="care-reference-note">Opened as a reference. No findings are attached to this care plan. Check the conditions below, or open the decision pathway to compare options.</p>`;
 const stale=o.fingerprint!==careFingerprint(o.step);
 return `<section class="care-origin ${stale?'stale':''}" aria-label="Decision context"><div class="care-origin-heading"><h3>${stale?'Earlier choices changed':'Why this plan is open'}</h3><span class="care-origin-label">${o.example?'Example findings':'Choices in this session'} · not saved</span></div>${stale?'<p>This plan no longer represents the current choices. Return to the originating decision and review its result.</p>':`<span class="care-origin-status" data-kind="${e(o.kind)}">${e(o.status)}</span><p class="care-result">${e(o.result)}</p><p><b>${o.via?'Option opened from another care plan':'Option opened'}:</b> ${e(o.option)}</p>${o.condition?`<p><b>Condition for this option:</b> ${e(o.condition)}</p>`:''}<details class="care-origin-choices"><summary>Findings at decision ${o.number}</summary><dl>${o.choices.map(q=>`<dt>${e(q.question)}</dt><dd>${e(q.answer)}</dd>`).join('')}</dl></details>`}<button class="care-return" data-step="${e(o.step)}">← Return to decision ${o.number}: ${e(o.title)} (choices kept)</button></section>`;
}
function carePlanHTML(selected){
 const reassess=selected.actions.filter(a=>a.step),other=selected.actions.filter(a=>!a.step);
 return `<div class="care-plan"><section class="care-condition"><h3>Use this plan when</h3><p>${e(selected.when)}</p></section><section class="care-tasks"><h3>${selected.endpoint?'Care to arrange':'What to do'}</h3><ol>${selected.tasks.map(t=>`<li>${e(t)}</li>`).join('')}</ol></section><details class="care-evidence"><summary>Supporting guidance and sources</summary><div class="care-sources">${selected.refs.map(id=>`<div>${refs([id])}<p class="small muted">${e(DATA.sources[id].locator)}</p></div>`).join('')}</div></details><section class="care-following"><h3>${selected.endpoint?'Continuing care and review':reassess.length?'Next assessment and other options':'Choose the next care plan'}</h3>${reassess.length?`<div class="care-following-group"><h4>${selected.endpoint?'Return to the assessment when appropriate':'Continue or revisit an assessment'}</h4>${renderActions(reassess)}</div>`:''}${other.length?`<div class="care-following-group"><h4>${reassess.length?'Other treatment and care options':'Treatment and care options'}</h4>${renderActions(other)}</div>`:''}</section></div>`;
}
function renderCare(){
 const plans=DATA.care[active.slug],selected=plans.find(p=>p.id===careId)||plans[0],origin=currentCareOrigin();
 return `<section class="care-view ${active.slug==='hcc'&&selected.id==='exception'?'care-high-risk':''}" aria-labelledby="care-title"><nav class="care-breadcrumb" aria-label="Care plan location"><span>${e(active.code)} pathway</span><span aria-hidden="true">›</span>${origin?`<button data-step="${e(origin.step)}">Decision ${origin.number}: ${e(origin.title)}</button><span aria-hidden="true">›</span>`:''}<strong>${origin?'Care plan':'Treatment reference'}</strong></nav><p class="eyebrow">${e(active.code)} · ${active.slug==='hcc'&&selected.id==='exception'?'High-risk and individual review':origin?'Care plan':'Treatment reference'}</p><h2 id="care-title" tabindex="-1">${e(selected.title)}</h2>${careOriginHTML()}${carePlanHTML(selected)}${origin&&origin.fingerprint===careFingerprint(origin.step)&&origin.reviews?.length?`<section class="care-risk-references"><h3>High-risk reviews from decision ${origin.number}</h3><p>Reference links retain the original review status.</p>${origin.reviews.map(r=>`<a href="#high-risk-${e(r.anchor)}" data-high-risk="${e(r.anchor)}"><strong>${e(r.title)}</strong><span>${e(r.status)}</span></a>`).join('')}</section>`:''}<details class="care-alternatives"><summary>Browse all ${e(active.code)} care plans (${plans.length})</summary><div class="care-reference-nav"><label for="care-topic">Choose a care plan</label><select id="care-topic" data-care-select>${plans.map(p=>`<option value="${e(p.id)}" ${p.id===selected.id?'selected':''}>${e(p.title)}</option>`).join('')}</select><a href="#${e(origin?.step||active.steps[stepIndex].id)}" data-step="${e(origin?.step||active.steps[stepIndex].id)}">Open decision pathway →</a></div></details></section>`;
}

function renderStep(){
 const s=active.steps[stepIndex];
 return `<section class="decision" aria-labelledby="question"><div class="question-head"><div><p class="eyebrow">Decision ${stepIndex+1} of ${active.steps.length} <span> / ${e(s.title)}</span></p><h2 id="question" tabindex="-1">${e(s.question)}</h2></div><a class="permalink" href="#${s.id}" aria-label="Link to this decision">#</a></div><div class="contextline"><span><b>When</b> ${e(s.timing)}</span><span><b>Responsible team</b> ${e(s.owner)}</span></div>
 <div class="decision-grid"><section class="orders"><div class="section-head"><span class="number-dot">1</span><h3>Tests and information needed</h3></div>${DecisionAssistant.render(assistantConfig(),DATA.sources,assistantSession.answers[assistantKey()],assistantSession.origins[assistantKey()])}<div id="risk-question-panel"></div><details class="full-tests"><summary>Full test checklist and source details</summary>${s.orders.map(g=>`<div class="ordergroup"><h4>${e(g.label)}</h4>${bullets(g.items)}</div>`).join('')}</details></section>
 <section class="results" id="decision-results"><div class="section-head"><span class="number-dot">2</span><h3>Next step</h3></div><p class="logic-note">Based on the selected findings. Review clinical suitability and allocation separately.</p><div class="assistant-feedback sr-only" role="status" aria-live="polite" aria-atomic="true"></div><div id="current-result"><article class="assistant-other-result" hidden></article></div><details class="other-results"><summary>Other possible results (<span data-other-count></span>)</summary><p class="small muted">Reference only. These are not the current next step. They require different findings, or a safety or earlier finding takes priority.</p><div id="other-result-list">${s.branches.map((b,bi)=>`<article class="branch ${e(b.kind)} is-muted" data-branch-index="${bi}"><span class="branch-match" hidden>Matches these choices</span><div class="branch-title"><span class="route-label">${b.kind==='advance'?'Proceed when':b.kind==='hold'?'Pause and clarify':b.kind==='redirect'?'Use another pathway':'Do not proceed on this pathway'}</span><h4>${e(b.title)}</h4></div><details class="branch-details"><summary>Criteria and supporting sources</summary>${bullets(b.criteria)}</details><div class="branch-action"><span class="action-arrow">→</span><p>${e(b.action)} ${refs(b.refs)}</p></div><div data-next-branch="${bi}"></div></article>`).join('')}</div></details></section></div>
 <div class="safety-grid"><section class="stops"><div class="section-head"><span class="status-icon">!</span><h3>Findings that change the treatment or transplant plan</h3></div>${s.stops.length?bullets(s.stops):'<p class="muted">No additional exclusion is listed at this step. Apply the earlier disease-specific criteria and complete the full transplant assessment.</p>'}<p class="small stopnote">Each statement identifies what the finding affects: treatment, a MELD-exception request, or transplantation under this protocol.</p></section>
 <section class="gray"><div class="section-head"><span class="status-icon">?</span><h3>Questions for multidisciplinary discussion</h3></div>${s.issues.map(id=>{const i=active.issues.find(x=>x.id===id);return `<a class="issue-link" href="#meeting-${i.id}"><span>Discussion ${active.issues.indexOf(i)+1}</span><b>${e(i.question)}</b><span class="issue-arrow">Compare sources · proposed decision →</span></a>`;}).join('')}</section></div>
 <nav class="stepfooter" aria-label="Browse decisions, not clinical clearance"><button ${stepIndex===0?'disabled':''} data-step="${active.steps[Math.max(0,stepIndex-1)].id}">Browse previous</button><span>Browse decisions · ${stepIndex+1} / ${active.steps.length}</span><button ${stepIndex===active.steps.length-1?'disabled':''} data-step="${active.steps[Math.min(active.steps.length-1,stepIndex+1)].id}">Browse next</button></nav></section>`;
}

function renderMeeting(){
 return `<section class="meetingintro"><div><p class="eyebrow">Source comparison + local decision record</p><h2>Questions to resolve together</h2><p>Each question is linked from its pathway decision. Source wording and proposed local interpretation are separate. <b>No local proposal is marked approved.</b></p></div></section>
 <aside class="high-risk-doc-note">${HighRisk.badge()}<p>Individual reviews appear with the relevant findings and next-step choices.</p><a href="#high-risk" data-view="high-risk">High-risk protocols and evidence →</a></aside><nav class="issue-index" aria-label="Meeting questions">${active.issues.map((i,n)=>`<a href="#meeting-${i.id}" data-issue="${i.id}">${n+1}. ${e(i.question)}</a>`).join('')}</nav>
 <div class="issue-records">${active.issues.map((i,n)=>renderIssue(i,n)).join('')}</div>`;
}

function renderIssue(i,n){
 const linked=active.steps.filter(s=>s.issues.includes(i.id));
 return `<article class="issue-record" id="${i.id}"><div class="issue-heading"><span class="issue-num">${String(n+1).padStart(2,'0')}</span><div><p class="eyebrow">Source-document item: ${e(i.record)}</p><h3>${e(i.question)}</h3></div><span class="pending">Pending approval</span></div><div class="backsteps">In the pathway: ${linked.map(s=>`<a href="/mh-liver-pathways/transplant/${active.slug}/#${s.id}">${e(s.title)} ↗</a>`).join(' · ')}</div>
 <div class="comparison-grid">${i.comparisons.map(c=>`<section class="comparison"><div class="source-kind">${e(DATA.sources[c.ref].kind)}</div><h4>${e(DATA.sources[c.ref].short)}</h4><p class="quotation ${c.quote?'exact':''}">${c.quote?'“':''}${e(c.text)}${c.quote?'”':''}</p><p class="small muted">${c.quote?'Short verbatim excerpt':'Source summary / scope'}${c.locator?' · '+e(c.locator):''}</p>${refs([c.ref])}</section>`).join('')}</div>
 <div class="proposal"><div><span class="route-label">Proposed local approach · discussion draft</span><p>${e(i.proposal)}</p></div><div><b>Why this matters</b><p>${e(i.rationale)}</p></div></div><div class="meeting-status"><span><b>Proposed responsible team:</b> ${e(i.owners)}</span><span><b>Decision:</b> pending meeting</span><span><b>Approval / date:</b> not recorded</span></div></article>`;
}

function renderEvidence(){
 return `<section class="evidenceintro"><p class="eyebrow">Evidence is also linked at the point of use</p><h2>Sources for ${e(active.code)}</h2><p><a href="https://drliuhao.github.io/mh-liver-pathways/evidence-libraries/#standard_${e(active.slug)}">Standard-protocol library and PPT index →</a> · <a href="https://drliuhao.github.io/mh-liver-pathways/evidence-libraries/#high_risk_${e(active.slug)}">High-risk library and PPT index →</a></p><p>Policy, review guidance, clinical recommendations and study evidence have different roles. Open a source to see its locator and full text. Publisher access may require an institutional sign-in. A source link does not imply high-level or definitive evidence.</p></section><div class="evidence-search"><label for="evidence-search">Find a source across this pathway</label><input id="evidence-search" type="search" data-evidence-search placeholder="Author, trial, guideline, PMID or DOI…"><span role="status" data-evidence-count>All sources shown</span></div><h3 class="evidence-group-title">Sources linked to standard decisions</h3><div class="evidencegrid">${allRefs(active).map(id=>{const r=DATA.sources[id];return `<article class="evidencecard" data-evidence-item data-search-text="${e([r.short,r.title,r.locator,r.url,r.pmid,r.doi].filter(Boolean).join(' '))}"><span class="source-kind">${e(r.kind)}</span><h3>${e(r.title)}</h3><p>${e(r.locator)}</p><button class="btn secondary" data-ref="${id}">Source details & full text ↗</button></article>`;}).join('')}</div>${HighRisk.library(DATA.high_risk,active.slug)}`;
}

function showSource(id, trigger){
 const r=DATA.sources[id];
 if(!r)return;
 lastTrigger=window.ContextualInfo?.sourceOrigin(trigger)||trigger;
 const d=document.getElementById('source-dialog');
 d.innerHTML=`<button type="button" class="close-dialog" aria-label="Close evidence">×</button><p class="eyebrow">${e(r.kind)}</p><h2 id="source-title">${e(r.title)}</h2><p class="locator">${e(r.locator)}</p>${r.note?`<div class="source-note">${e(r.note)}</div>`:''}<div class="source-actions">${external(r.url,r.kind==='Allocation policy'||r.kind==='NLRB guidance'?'Open official source':'Publisher / full-text access','btn')}</div><p class="small muted">Access through the publisher or official source; institutional sign-in may be required. The linked source supports the adjacent statement. Guidance is not binding allocation policy; cohort results and local proposals are not universal eligibility rules.</p>`;
 d.showModal();
}

function setStep(id,push=true,fromAction=false,browse=false){
 const index=active.steps.findIndex(s=>s.id===id);if(index<0)return;
 const previous=active.steps[stepIndex].id,found=decisionTrail.indexOf(id);
 if(browse){browseOrigin=browseOrigin||previous;if(id===browseOrigin)browseOrigin=null;}
 else if(found>=0)decisionTrail=decisionTrail.slice(0,found);
 else if(fromAction&&id!==previous){if(!decisionTrail.includes(previous))decisionTrail.push(previous);}
 else if(id!==previous)decisionTrail=[];
 if(!browse)browseOrigin=null;
 focusedCriteria=null;stepIndex=index;view='pathway';if(push)history.pushState({decisionTrail:[...decisionTrail],browseOrigin},'','#'+id);renderView();
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
 browseOrigin=history.state?.browseOrigin||null;
 const h=decodeURIComponent(location.hash.slice(1));
 const idx=active.steps.findIndex(s=>s.id===h);
 // A meeting question is addressed as #meeting-<id>: several question ids are also decision ids (e.g. #diagnosis).
 const question=h.startsWith('meeting-')&&active.issues.some(i=>i.id===h.slice(8))?h.slice(8):active.issues.some(i=>i.id===h)?h:null;
 if(h.startsWith('high-risk-')){showHighRisk(h.slice(10),false);return;}
 if(h==='high-risk'){view='high-risk';renderView();return;}
 if(h.startsWith('care-')&&DATA.care[active.slug].some(p=>p.id===h.slice(5))){view='care';careId=h.slice(5);careOriginToken=history.state?.careToken||null;}
 else if(question&&(question!==h||DATA.mode==='alignment'))view='meeting';
 else if(idx>=0){view='pathway';if(idx!==stepIndex){const saved=history.state?.decisionTrail;const found=decisionTrail.indexOf(h);decisionTrail=Array.isArray(saved)?saved.filter(id=>{const key=active.slug+'/'+id;return id!==h&&DATA.assistants[key]?.questions.every(q=>!!assistantSession.answers[key]?.[q.id]);}):found>=0?decisionTrail.slice(0,found):[];focusedCriteria=null;}stepIndex=idx;}
 else if(h==='evidence')view='evidence';
 else if(h==='meeting'||active.issues.some(i=>i.id===h)||DATA.mode==='alignment')view='meeting';
 else view='pathway';
 renderView();
 if(view==='pathway'&&idx>=0)requestAnimationFrame(()=>document.querySelector('.decision')?.scrollIntoView({block:'start'}));
 if(view==='meeting'&&question)requestAnimationFrame(()=>document.getElementById(question)?.scrollIntoView({block:'start'}));
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
 if(ev.target.matches('[data-layer-question],[data-layer-risk]')){stageFinding(ev.target);return;}
 if(ev.target.matches('[data-care-select]')){careId=ev.target.value;careOriginToken=null;view='care';history.replaceState(null,'','#care-'+careId);renderView();document.querySelector('.care-alternatives').open=true;document.getElementById('care-topic').focus();return;}
 const riskId=ev.target.dataset.riskQuestion;
 if(riskId){const button=ev.target.closest('.risk-question').querySelector('[data-record-risk]');if(button)button.disabled=ev.target.value===ev.target.dataset.committed;return;}
 const id=ev.target.dataset.assistantQuestion;if(!id)return;
 const config=assistantConfig(),q=config.questions.find(q=>q.id===id);if(!q)return;
 editLayer(active.steps[stepIndex].id,id,ev.target.value);
});

document.addEventListener('click',ev=>{
 const cancel=ev.target.closest('[data-cancel-finding]');if(cancel){const select=document.getElementById(cancel.dataset.cancelFinding);select.value=select.dataset.committed;select.dispatchEvent(new Event('change',{bubbles:true}));select.focus();return;}
 const record=ev.target.closest('[data-record-finding]');if(record&&!record.disabled){const select=document.getElementById(record.dataset.recordFinding);if(select.dataset.layerRisk)recordRiskFinding(select.dataset.layerStep,select.dataset.layerRisk,select.value);else editLayer(select.dataset.layerStep,select.dataset.layerQuestion,select.value);return;}
 const recordRisk=ev.target.closest('[data-record-risk]');if(recordRisk&&!recordRisk.disabled){const select=document.getElementById('risk-'+recordRisk.dataset.recordRisk);recordRiskFinding(active.steps[stepIndex].id,recordRisk.dataset.recordRisk,select.value);return;}
 const criteria=ev.target.closest('[data-layer-criteria]');if(criteria){showLayerCriteria(criteria.dataset.layerStep,criteria.dataset.layerCriteria,criteria.hasAttribute('data-risk-criteria'));return;}
 if(ev.target.closest('[data-layer-options]')){const target=document.getElementById('current-result');target.querySelectorAll('.branch-details').forEach(d=>d.open=true);target.scrollIntoView({block:'start',behavior:'instant'});return;}
 const highRisk=ev.target.closest('[data-high-risk]');if(highRisk){ev.preventDefault();showHighRisk(highRisk.dataset.highRisk);return;}
 if(ev.target.closest('[data-pathway-overview]')){
  if(view!=='pathway'){view='pathway';history.pushState(null,'','#'+active.steps[stepIndex].id);renderView();}
  const title=document.getElementById('journey-title');title.setAttribute('tabindex','-1');title.focus({preventScroll:true});
  document.querySelector('.journey-overview').scrollIntoView({block:'start',behavior:'instant'});return;
 }
 if(ev.target.closest('[data-pathway-example],[data-pathway-clear]')){
  const examples=!!ev.target.closest('[data-pathway-example]');
  assistantSession=DecisionAssistant.createStagedSession(active,DATA.assistants,examples);riskContext={};clearCareOrigins();decisionTrail=[];browseOrigin=null;focusedCriteria=null;stepIndex=0;view='pathway';history.replaceState(null,'','#'+active.steps[0].id);
  renderView();document.querySelector(examples?'[data-pathway-example]':'[data-pathway-clear]').focus({preventScroll:true});return;
 }
 const care=ev.target.closest('[data-care]');if(care){ev.preventDefault();showCare(care);return;}
 if(ev.target.closest('[data-assistant-reset]')){
  focusedCriteria=null;clearCareOrigins();DecisionAssistant.clearFrom(assistantSession,active,stepIndex);RiskRouting.clearFrom(riskContext,active,stepIndex);renderView();document.querySelector('[data-assistant-reset]').focus({preventScroll:true});return;
 }
 if(ev.target.closest('[data-assistant-show]')){const target=document.querySelector('.results .branch.is-highlighted:not([hidden])')||document.getElementById('decision-results');target.scrollIntoView({block:'start',behavior:'instant'});return;}

 const cite=ev.target.closest('[data-ref]');if(cite){showSource(cite.dataset.ref,cite);return;}
 if(ev.target.closest('.close-dialog')){document.getElementById('source-dialog').close();return;}
 const step=ev.target.closest('[data-step]');if(step&&!step.disabled){ev.preventDefault();setStep(step.dataset.step,true,!!step.closest('.next-action'),step.hasAttribute('data-dw-browse'));return;}
 const tab=ev.target.closest('[data-view]');if(tab){ev.preventDefault();view=tab.dataset.view;if(view==='care')careOriginToken=null;history.pushState(null,'',view==='pathway'?'#'+active.steps[stepIndex].id:view==='care'?'#care-'+careId:'#'+view);renderView();return;}
 const issue=ev.target.closest('[data-issue]');if(issue){ev.preventDefault();history.pushState(null,'','#meeting-'+issue.dataset.issue);document.getElementById(issue.dataset.issue).scrollIntoView({block:'start'});}
});
document.getElementById('source-dialog').addEventListener('click',ev=>{if(ev.target===ev.currentTarget){const r=ev.currentTarget.getBoundingClientRect();if(ev.clientX<r.left||ev.clientX>r.right||ev.clientY<r.top||ev.clientY>r.bottom)ev.currentTarget.close();}});
document.getElementById('source-dialog').addEventListener('close',()=>lastTrigger?.focus());
window.addEventListener('popstate',()=>{if(window.ContextualInfo?.handleHistory())return;active?hashState():null;});
window.addEventListener('hashchange',()=>active?hashState():null);
document.addEventListener('keydown',ev=>{
 if(ev.key==='Escape'&&ev.target.matches('[data-layer-question],[data-layer-risk]')){ev.target.value=ev.target.dataset.committed;stageFinding(ev.target);return;}
 if(!ev.target.matches('.viewbar [role="tab"]')||!['ArrowLeft','ArrowRight','Home','End'].includes(ev.key))return;
 ev.preventDefault();const tabs=[...document.querySelectorAll('.viewbar [role="tab"]')];let n=tabs.indexOf(ev.target);
 n=ev.key==='Home'?0:ev.key==='End'?tabs.length-1:(n+(ev.key==='ArrowRight'?1:-1)+tabs.length)%tabs.length;
 tabs[n].click();tabs[n].focus();
});
if(active){pathwayShell();hashState();}else home();
