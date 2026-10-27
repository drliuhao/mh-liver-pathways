/* Shared roadmap navigation. Topic selection is not a patient classification. */
(() => {
 'use strict';
 const root=new URL('../',document.currentScript.src),esc=s=>String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
 let state=null,links=null,configLoaded=false;
 const configPromise=fetch(new URL('assets/roadmap-links.json?v=20261025',root)).then(r=>{if(!r.ok)throw Error('Navigation unavailable');return r.json();}).catch(()=>null);
 const title=s=>s.name.replace(/^\d+\s*·\s*/, '');
 function initial(stages,fallback){let id;try{id=decodeURIComponent(location.hash.replace(/^#decision-/,''));}catch{return fallback;}return location.hash.startsWith('#decision-')&&stages.some(s=>s.id===id)?id:(stages.some(s=>s.id==='A')?'A':stages[0].id);}
 function setup({slug,stages,select,topic}){
  state={slug,stages,select,topic,current:null,initialSelection:null,trail:[]};document.body.classList.add('roadmap-streamlined');
  const legend=document.querySelector('.legend');
  if(legend&&!legend.closest('details')){const d=document.createElement('details');d.className='rf-legend';d.innerHTML='<summary>Recommendation labels, evidence grades and delivery requirements</summary>';legend.before(d);d.append(legend);}
  const entry=document.getElementById('entry');if(entry)entry.textContent='Select the clinical question to review. Some assessments can proceed together; urgent care and procedure-specific precautions take priority.';
  const buttons=document.getElementById('stageBtns');
  buttons.innerHTML=stages.map(s=>`<button class="rf-topic" type="button" data-roadmap-decision="${esc(s.id)}">${esc(s.name)}</button>`).join('');
  const overview=document.createElement('section');overview.className='rf-overview';overview.setAttribute('aria-label','All clinical decisions');buttons.before(overview);overview.append(buttons);
  // Clinical charts and choices remain visible; only their reference definitions can fold.
  const bar=document.createElement('nav');bar.className='rf-selector';bar.setAttribute('aria-label','Current roadmap decision');
  bar.innerHTML='<div class="layer-heading"><b>Clinical topics</b><a class="rf-permalink" href="#stage">Link</a><button type="button" data-rf-overview>All decisions</button></div><div class="layer-history"></div><div class="layer-current"></div>';
  document.getElementById('answer').before(bar);
  bar.addEventListener('change',ev=>{
   if(ev.target.matches('[data-roadmap-current]'))stageTopic();
  });
  bar.addEventListener('keydown',ev=>{if(ev.key==='Escape'&&ev.target.matches('[data-roadmap-current]')){ev.target.value=state.current;stageTopic();}});
  bar.addEventListener('click',ev=>{
   if(ev.target.closest('[data-open-topic]')){navigate(bar.querySelector('[data-roadmap-current]').value);return;}
   if(ev.target.closest('[data-cancel-topic]')){bar.querySelector('[data-roadmap-current]').value=state.current;stageTopic();bar.querySelector('[data-roadmap-current]').focus();return;}
   const prior=ev.target.closest('[data-roadmap-trail]');if(prior){const n=Number(prior.dataset.roadmapTrail),node=state.trail[n];if(node)navigate(node.id,{layer:n,via:node.via});return;}
   if(ev.target.closest('[data-rf-overview]')){overview.scrollIntoView({block:'start',behavior:'smooth'});}
   const criteria=ev.target.closest('[data-roadmap-criteria]');if(criteria){const panel=document.querySelector(criteria.dataset.roadmapCriteria==='next'?'.rf-related':'.rf-criteria');if(panel?.tagName==='DETAILS')panel.open=true;panel?.scrollIntoView({block:'start',behavior:'instant'});panel?.querySelector('summary')?.focus({preventScroll:true});}
  });
  document.addEventListener('click',e=>{
   const b=e.target.closest('[data-roadmap-decision]');if(b){e.preventDefault();navigate(b.dataset.roadmapDecision,{layer:b.closest('.rf-related')?state.trail.length:0,via:b.dataset.relatedIndex===undefined?null:Number(b.dataset.relatedIndex)});}
   const t=e.target.closest('[data-roadmap-topic]');if(t&&state.topic){e.preventDefault();state.topic(t.dataset.roadmapTopic);document.getElementById('topics')?.scrollIntoView({block:'start',behavior:'smooth'});}
  });
  const restore=()=>{if(location.hash&&!location.hash.startsWith('#decision-'))return;const id=initial(stages,state.initialSelection||stages[0].id);if(id&&id!==state.current){const saved=history.state?.roadmapTrail;state.trail=Array.isArray(saved)&&saved.at(-1)?.id===id&&saved.every(x=>stages.some(s=>s.id===x.id))?saved:[{id,via:null}];state.select(id);}};
  window.addEventListener('hashchange',restore);window.addEventListener('popstate',restore);
  const header=document.querySelector('header.top');const offsets=()=>document.documentElement.style.setProperty('--roadmap-header',`${header&&getComputedStyle(header).position==='sticky'?header.getBoundingClientRect().height:0}px`);offsets();if(header&&window.ResizeObserver)new ResizeObserver(offsets).observe(header);
  configPromise.then(data=>{links=data;configLoaded=true;if(state.current){renderRelated(state.current);renderTrail();}});
  const revealAppraisal=()=>{let id;try{id=decodeURIComponent(location.hash.slice(1));}catch{return;}const node=document.getElementById(id);if(!node?.closest('.study-appraisals'))return;const body=document.getElementById('evBody');if(body)body.hidden=false;const toggle=document.querySelector('[data-fold="evBody"]');if(toggle){toggle.textContent='Hide';toggle.setAttribute('aria-expanded','true');}if(node.tagName==='DETAILS')node.open=true;requestAnimationFrame(()=>node.scrollIntoView({block:'start'}));};
  window.addEventListener('hashchange',revealAppraisal);requestAnimationFrame(revealAppraisal);
 }
 function recordLabel(r){return r.label||(r.decision?title(state.stages.find(s=>s.id===r.decision)):'Review related care');}
 function recordHref(r){return r.decision?'#decision-'+encodeURIComponent(r.decision):r.topic?new URL('hcc/?topic='+encodeURIComponent(r.topic)+'#topics',root).href:new URL(r.url,root).href;}
 function stageTopic(){
  const bar=document.querySelector('.rf-selector'),staged=bar.querySelector('[data-roadmap-current]').value!==state.current,status=bar.querySelector('.layer-stage-status');
  bar.querySelector('[data-open-topic]').disabled=!staged;bar.querySelector('[data-cancel-topic]').hidden=!staged;bar.querySelector('.layer-row').classList.toggle('is-staged',staged);
  status.hidden=!staged;status.textContent=staged?'Not opened — showing: '+title(state.stages.find(s=>s.id===state.current))+'.':'';
 }
 function renderTrail(){
  const bar=document.querySelector('.rf-selector');if(!bar||!state.current)return;
  if(!state.trail.length||state.trail.at(-1).id!==state.current)state.trail=[{id:state.current,via:null}];
  const historyEl=bar.querySelector('.layer-history'),historyOpen=historyEl.querySelector('details')?.open||false;
  const previous=state.trail.slice(0,-1);
  historyEl.innerHTML=previous.length?`<details class="layer-history-disclosure" ${historyOpen?'open':''}><summary>Previously viewed (${previous.length}) · revisit</summary><ol class="roadmap-history-list">${previous.map((node,i)=>{const selected=i?links?.[state.slug]?.[state.trail[i-1].id]?.[node.via]:null;return `<li><button type="button" data-roadmap-trail="${i}">${esc(title(state.stages.find(s=>s.id===node.id)))}</button>${selected?`<p>${esc(selected.when)}</p>`:''}</li>`;}).join('')}</ol><p class="layer-history-note">Navigation history only; no patient findings are recorded.</p></details>`:'';
  const options=state.stages.map(s=>`<option value="${esc(s.id)}" ${s.id===state.current?'selected':''}>${esc(title(s))}</option>`).join('');
  bar.querySelector('.layer-current').innerHTML=`<div class="layer-row is-current"><div class="layer-choice"><label for="roadmap-decision">Clinical topic</label><select id="roadmap-decision" data-roadmap-current>${options}</select><span class="layer-stage-status" role="status" hidden></span></div><div class="layer-controls"><button class="layer-apply" data-open-topic disabled>Open topic</button><button class="layer-cancel" data-cancel-topic hidden>Cancel</button><button class="layer-criteria" data-roadmap-criteria="next">Next assessments ↓</button></div></div>`;
  bar.querySelector('.rf-permalink').href='#decision-'+encodeURIComponent(state.current);
  const size=()=>document.documentElement.style.setProperty('--roadmap-trail-height',Math.ceil((bar.querySelector('.ct-strip')||bar).getBoundingClientRect().height)+'px');size();if(!bar.dataset.observed&&window.ResizeObserver){bar.dataset.observed='true';new ResizeObserver(size).observe(bar);}
 }
 function navigate(id,{replace=false,focus=true,scroll=true,layer=0,via=null}={}){
  if(!state.stages.some(s=>s.id===id))return;
  state.trail=state.trail.slice(0,layer);state.trail.push({id,via});
  history[replace?'replaceState':'pushState']({roadmapTrail:state.trail},'','#decision-'+encodeURIComponent(id));
  state.select(id);
  if(scroll)document.getElementById('answer').scrollIntoView({block:'start',behavior:'instant'});
  if(focus)document.querySelector('#answer .ahead h3')?.focus({preventScroll:true});
 }
 function render(s,recHTML){
  state.current=s.id;
  renderTrail();
  document.querySelectorAll('[data-roadmap-decision]').forEach(b=>{if(b.classList.contains('rf-topic'))b.setAttribute('aria-current',b.dataset.roadmapDecision===s.id?'true':'false');});
  const group=(label,items,cls)=>items?.length?`<section class="rf-option-group ${cls}"><h4>${label}</h4>${items.map(recHTML).join('')}</section>`:'';
  return `<div class="ahead"><p class="rf-context">Showing this clinical topic</p><h3 tabindex="-1">${esc(s.name)}</h3>${s.ask?`<p class="ask">${esc(s.ask)}</p>`:''}<p class="rf-eligibility-note">Topic selection does not establish treatment or transplant eligibility.</p><details class="rf-criteria" open><summary>Selection criteria · ${s.req==='any'?'any one':'all required'}</summary><p>Conditions and checks described for this topic:</p><b>${s.req==='any'?'Any one of the following':'All of the following'}</b><ul>${s.crit.map(c=>`<li>${esc(c)}</li>`).join('')}</ul></details></div><div class="rf-recommendations"><h4 class="flow-section-heading"><span>2</span> Compare treatment options</h4><div class="rf-options">${group('Standard approach',s.standard,'rf-standard')}${group('Reasonable alternatives',s.alt,'rf-alternatives')}</div>${group('Avoid / cautions in this situation',s.avoid,'rf-cautions')}</div><section class="rf-related" aria-label="Related clinical decisions" data-related-for="${esc(s.id)}"></section><div class="rf-evidence-controls"><button class="xpand" type="button" id="xpandAll" data-open="0" aria-expanded="false">Expand criteria and evidence</button><span>These links open related assessments. Recheck the destination criteria; topic selections do not carry patient findings or establish eligibility.</span></div>`;
 }
 function update(s){
  renderRelated(s.id);renderTrail();
  if(!state.initialSelection){state.initialSelection=s.id;if(location.hash==='#decision-'+encodeURIComponent(s.id))requestAnimationFrame(()=>document.getElementById('answer').scrollIntoView({block:'start'}));}
 }
 function renderRelated(id){
  const panel=document.querySelector('[data-related-for]');if(!panel||panel.dataset.relatedFor!==id)return;
  if(!links){panel.innerHTML=configLoaded?'<p>Related-decision shortcuts are unavailable. Use the clinical decision selector above.</p>':'<p>Loading related assessments…</p>';return;}
  const records=links[state.slug]?.[id]||[];
  const items=records.map((r,index)=>{
   const target=r.decision?state.stages.find(s=>s.id===r.decision):null;
   if(r.decision&&!target)return '';
   const label=r.label||(target?title(target):'Review related care');
   const href=r.decision?'#decision-'+encodeURIComponent(r.decision):r.topic?new URL('hcc/?topic='+encodeURIComponent(r.topic)+'#topics',root).href:new URL(r.url,root).href;
   return `<a class="rf-related-link" href="${esc(href)}" ${r.decision?`data-roadmap-decision="${esc(r.decision)}" data-related-index="${index}"`:''}><span><b class="flow-if">When</b> ${esc(r.when)}</span><strong>${esc(label)} →</strong></a>`;
  }).join('');
  panel.innerHTML=`<h4 class="flow-section-heading"><span>3</span> Next assessment or care</h4><p>Open the assessment when the stated situation applies. Several may be needed together. Supportive care can accompany treatment or be the main care plan.</p><div class="rf-related-grid">${items}</div>`;
 }
 window.RoadmapFlow={setup,render,update,initial,navigate};
})();
