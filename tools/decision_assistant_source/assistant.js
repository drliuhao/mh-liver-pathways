/* Deterministic navigation aid. No records, network calls, storage or eligibility score. */
(function(root){
 'use strict';
 const labelMap={
  'P-cohort':'Darwish Murad · Gastroenterology 2012',
  'I-cohort':'Sapisochin · Hepatology 2016',
  'C-transmet':'Adam · Lancet 2024 · TransMet',
  'NET-milan':'Mazzaferro · AJT 2016 · Milan-NET',
  'E-score':'Lai · Transplantation 2017',
  'A-molecular':'Nault · Gastroenterology 2017'
 };
 const esc=s=>String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
 function createSession(pathway,configs,examples=true){
  const answers={},origins={};
  pathway.steps.forEach(s=>{const key=`${pathway.slug}/${s.id}`;answers[key]=examples?{...configs[key].example}:{};origins[key]=examples?'example':'empty';});
  return {answers,origins};
 }
 function clearFrom(session,pathway,index){
  pathway.steps.slice(index).forEach(s=>{const key=`${pathway.slug}/${s.id}`;session.answers[key]={};session.origins[key]='empty';if(session.presets)delete session.presets[key];});
 }
 function changeAnswer(session,pathway,index,id,value){
  const key=`${pathway.slug}/${pathway.steps[index].id}`;
  if(session.answers[key][id]===value)return false;
  session.answers[key][id]=value;session.origins[key]='edited';
  clearFrom(session,pathway,index+1);
  return true;
 }
 // Entry examples never fill later decisions. Each newly revealed layer starts blank.
 function createStagedSession(pathway,configs,example=true){
  const session=createSession(pathway,configs,false);session.presets={};
  if(example){const key=pathway.slug+'/'+pathway.steps[0].id,q=configs[key].questions[0];session.answers[key][q.id]=configs[key].example[q.id];session.origins[key]='example';session.presets[key]={[q.id]:configs[key].example[q.id]};}
  return session;
 }
 function changeStagedAnswer(session,pathway,configs,index,id,value){
  const key=pathway.slug+'/'+pathway.steps[index].id,questions=configs[key].questions,n=questions.findIndex(q=>q.id===id);
  if(n<0||session.answers[key][id]===value)return false;
  changeAnswer(session,pathway,index,id,value);
  if(session.presets?.[key])delete session.presets[key][id];
  questions.slice(n+1).forEach(q=>delete session.answers[key][q.id]);
  return true;
 }
 function visibleQuestions(config,answers){
  const firstEmpty=config.questions.findIndex(q=>!answers[q.id]);
  return config.questions.slice(0,firstEmpty<0?config.questions.length:firstEmpty+1);
 }
 function evaluate(config, answers, branches){
  const known={};
  config.questions.forEach(q=>{if(q.options.some(o=>o.value===answers[q.id]))known[q.id]=answers[q.id];});
  for(const [ruleIndex,rule] of config.rules.entries()){
   const match=Object.entries(rule.when).every(([q,values])=>(Array.isArray(values)?values:[values]).includes(known[q]));
   if(!match)continue;
   const branch=rule.branch===null?null:branches[rule.branch];
   const kind=branch?.kind||rule.kind;
   // A proceed highlight requires every essential question to be resolved.
   if(kind==='advance'&&config.questions.some(q=>!known[q.id]||known[q.id]==='unknown'))continue;
   return {state:'matched',branch:rule.branch,ruleIndex,kind,title:branch?.title||rule.title,
    text:branch?.action||rule.text,refs:rule.refs};
  }
  const uncertain=config.questions.filter(q=>known[q.id]==='unknown');
  if(uncertain.length)return {state:'clarify',branch:null,kind:'hold',title:'Clarify before choosing the next step',
   text:uncertain.map(q=>q.label).join(' '),refs:[...new Set(uncertain.flatMap(q=>q.refs))]};
  const remaining=config.questions.filter(q=>!known[q.id]);
  return {state:'pending',branch:null,kind:'pending',title:remaining.length?'Choose the essential findings':'Review the combination with the team',
   text:remaining.length?`${remaining.length} ${remaining.length===1?'choice remains':'choices remain'}. The relevant next step will light up as the findings support it.`:
    'Review this combination with the treating team before choosing treatment or transplantation.',refs:[]};
 }
 function evidence(ids,sources){
  return `<span class="assistant-evidence">${[...new Set(ids)].map(id=>{
   const s=sources[id];if(!s)return '';
   const doi=s.url.match(/^https:\/\/(?:dx\.)?doi\.org\/(.+)$/)?.[1];
   const tmc=doi?`https://thslc-houston.primo.exlibrisgroup.com/discovery/search?vid=01TEXASHEALTH_HOUSTON%3ATMC_INST&query=any,contains,${encodeURIComponent(doi)}&lang=en`:null;
   return `<span><a href="${esc(s.url)}" target="_blank" rel="noopener" title="${esc(s.title+' · '+s.locator)}">${esc(labelMap[id]||s.short)} ↗</a>${tmc?` <a class="tmc-link" href="${esc(tmc)}" target="_blank" rel="noopener" aria-label="Find ${esc(labelMap[id]||s.short)} at TMC Library">TMC ↗</a>`:''}</span>`;
  }).join('')}</span>`;
 }
 function definitions(q,value,sources){
  const selected=q.options.find(o=>o.value===value);
  return (selected?`<p class="assistant-selected">Selected: ${esc(selected.label)}</p>`:'')+
   (selected?.details?.length?`<details class="assistant-criteria"><summary>Criteria for this selection</summary><ul>${selected.details.map(x=>`<li>${esc(x)}</li>`).join('')}</ul></details>`:'')+
   q.criteria.map(c=>`<details class="assistant-criteria" data-relevant="${!c.show_for.length||c.show_for.includes(value||'')}"><summary>${esc(c.title)}</summary><ul>${c.items.map(x=>`<li>${esc(x)}</li>`).join('')}</ul>${evidence(c.refs,sources)}</details>`).join('');
 }
 function render(config,sources,answers={},origin='empty'){
  return `<div class="decision-assistant"><p class="assistant-intro">${origin==='example'?'Example findings are preselected to show the path toward transplant. Change any choice to explore another result.':'Choose the findings that matter for this decision. The matching next step will be highlighted.'}</p>
   ${config.questions.map((q,n)=>`<div class="assistant-question"><label for="assistant-${esc(q.id)}"><span>${n+1}</span>${esc(q.label)}</label>
   ${q.help?(q.criteria.length?`<p class="assistant-help" id="assistant-help-${esc(q.id)}">${esc(q.help)}</p>`:`<details class="assistant-criteria assistant-help-criteria" data-relevant="true"><summary>Criteria for this finding</summary><p class="assistant-help" id="assistant-help-${esc(q.id)}">${esc(q.help)}</p>${evidence(q.refs,sources)}</details>`):''}
   <select id="assistant-${esc(q.id)}" data-assistant-question="${esc(q.id)}" ${q.help?`aria-describedby="assistant-help-${esc(q.id)}"`:''}><option value="">Choose a finding…</option>${q.options.map(o=>`<option value="${esc(o.value)}" ${answers[q.id]===o.value?'selected':''}>${esc(o.label)}</option>`).join('')}</select>
   <div class="assistant-definitions" data-definitions="${esc(q.id)}">${definitions(q,answers[q.id],sources)}</div>
   ${q.help&&!q.criteria.length?'':evidence(q.refs.filter(id=>!q.criteria.some(c=>c.refs.includes(id))),sources)}</div>`).join('')}
   <div class="assistant-actions"><button type="button" data-assistant-reset>Clear choices</button><button type="button" data-assistant-show>See next step ↓</button></div>
   <p class="assistant-footnote">For this decision only. Choices are not saved. The team must assess transplant suitability and MELD-exception eligibility separately.</p></div>`;
 }
 function update(container,config,answers,branches,sources,origin='empty'){
  const result=evaluate(config,answers,branches);
  const feedback=container.querySelector('.assistant-feedback');
  feedback.className='assistant-feedback sr-only '+result.kind;
  feedback.textContent=(origin==='example'?'Example result: ':'Result updated: ')+result.title+'. See Next step.';
  container.querySelectorAll('[data-branch-index]').forEach(card=>{
   const selected=result.state==='matched'&&result.branch===Number(card.dataset.branchIndex);
   card.classList.toggle('is-highlighted',selected);
   card.classList.toggle('is-muted',!selected);
   if(selected)card.setAttribute('aria-current','true');else card.removeAttribute('aria-current');
   const marker=card.querySelector('.branch-match');marker.hidden=!selected;
   marker.textContent=origin==='example'?'Matches the example':'Matches these choices';
  });
  const extra=container.querySelector('.assistant-other-result');
  const custom=result.branch===null&&result.kind!=='pending';
  extra.hidden=!custom;
  extra.className='assistant-other-result branch '+result.kind+' is-highlighted';
  extra.innerHTML=custom?`<span class="branch-match">${result.state==='matched'?'Review next actions':'Clarification needed'}</span><h4>${esc(result.title)}</h4><p>${esc(result.text)}</p>${evidence(result.refs,sources)}`:'';
  return result;
 }
 const API={evaluate,evidence,definitions,render,update,createSession,clearFrom,changeAnswer,createStagedSession,changeStagedAnswer,visibleQuestions};
 if(typeof module==='object'&&module.exports)module.exports=API;
 else root.DecisionAssistant=API;
})(typeof window==='undefined'?{}:window);
