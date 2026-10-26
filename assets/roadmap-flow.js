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
  const overview=document.createElement('details');overview.className='rf-overview';overview.innerHTML='<summary>Browse all clinical decisions</summary>';buttons.before(overview);overview.append(buttons);
  const tree=document.getElementById('tree');
  if(tree){const children=[...tree.children].filter(n=>n!==overview&&n.tagName!=='H2');if(children.length){const reference=document.createElement('details');reference.className='rf-background-reference';const summary=document.createElement('summary');summary.textContent='Staging overview and reference definitions';reference.append(summary,...children);tree.prepend(reference);}}
  const bar=document.createElement('nav');bar.className='rf-selector';bar.setAttribute('aria-label','Current roadmap decision');
  bar.innerHTML='<div class="layer-heading"><b>Decision trail</b><a class="rf-permalink" href="#stage">Link</a><button type="button" data-rf-overview>All decisions</button></div><div class="layer-history"></div><div class="layer-current"></div>';
  document.getElementById('answer').before(bar);
  bar.addEventListener('change',ev=>{
   const row=ev.target.dataset.roadmapLayer;if(row===undefined||ev.target.value==='')return;
   const n=Number(row);
   if(n===0){state.trail=[];navigate(ev.target.value,{layer:0});return;}
   const previous=state.trail[n-1],r=links?.[state.slug]?.[previous.id]?.[Number(ev.target.value)];if(!r)return;
   if(r.decision)navigate(r.decision,{layer:n,via:Number(ev.target.value)});
   else {const anchor=document.createElement('a');anchor.href=recordHref(r);anchor.className='rf-related-link';anchor.textContent=recordLabel(r);document.body.append(anchor);anchor.click();anchor.remove();}
  });
  bar.addEventListener('click',ev=>{
   if(ev.target.closest('[data-rf-overview]')){overview.open=true;overview.scrollIntoView({block:'start',behavior:'smooth'});}
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
 }
 function recordLabel(r){return r.label||(r.decision?title(state.stages.find(s=>s.id===r.decision)):'Review related care');}
 function recordHref(r){return r.decision?'#decision-'+encodeURIComponent(r.decision):r.topic?new URL('hcc/?topic='+encodeURIComponent(r.topic)+'#topics',root).href:new URL(r.url,root).href;}
 function renderTrail(){
  const bar=document.querySelector('.rf-selector');if(!bar||!state.current)return;
  if(!state.trail.length||state.trail.at(-1).id!==state.current)state.trail=[{id:state.current,via:null}];
  const rootOptions=state.stages.map(s=>`<option value="${esc(s.id)}" ${s.id===state.trail[0].id?'selected':''}>${esc(title(s))}</option>`).join('');
  let rows=`<div class="layer-row is-chosen"><span class="layer-number">1</span><div class="layer-choice"><label for="roadmap-decision">Starting topic</label><select id="roadmap-decision" data-roadmap-layer="0">${rootOptions}</select></div></div>`;
  state.trail.slice(1).forEach((node,i)=>{const options=links?.[state.slug]?.[state.trail[i].id]||[],selected=options[node.via];rows+=`<div class="layer-row is-chosen"><span class="layer-number">${i+2}</span><div class="layer-choice"><label for="roadmap-layer-${i+1}">Next assessment or care</label><select id="roadmap-layer-${i+1}" data-roadmap-layer="${i+1}">${options.map((r,j)=>`<option value="${j}" ${j===node.via?'selected':''}>${esc(recordLabel(r))}</option>`).join('')}</select>${selected?`<span class="layer-value">${esc(selected.when)}</span>`:''}</div></div>`;});
  bar.querySelector('.layer-history').innerHTML=rows;
  const options=links?.[state.slug]?.[state.current]||[];
  bar.querySelector('.layer-current').innerHTML=`<div class="layer-row is-current"><span class="layer-number">${state.trail.length+1}</span><div class="layer-choice"><label for="roadmap-next">Next assessment or care</label><select id="roadmap-next" data-roadmap-layer="${state.trail.length}" ${!options.length?'disabled':''}><option value="">${options.length?'Choose the next step…':'Loading next options…'}</option>${options.map((r,i)=>`<option value="${i}">${esc(recordLabel(r))}</option>`).join('')}</select></div><button class="layer-criteria" data-roadmap-criteria="next">Options &amp; criteria</button></div>`;
  bar.querySelector('.rf-permalink').href='#decision-'+encodeURIComponent(state.current);
  const historyEl=bar.querySelector('.layer-history');
  const size=()=>document.documentElement.style.setProperty('--roadmap-trail-height',Math.ceil(bar.getBoundingClientRect().height)+'px');size();if(!bar.dataset.observed&&window.ResizeObserver){bar.dataset.observed='true';new ResizeObserver(size).observe(bar);}
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
  return `<div class="ahead"><p class="rf-context">Showing this clinical topic</p><h3 tabindex="-1">${esc(s.name)}</h3>${s.ask?`<p class="ask">${esc(s.ask)}</p>`:''}<details class="rf-criteria"><summary>Selection criteria · ${s.req==='any'?'any one':'all required'}</summary><p>Topic selection does not establish treatment or transplant eligibility.</p><p>Conditions and checks described for this topic:</p><b>${s.req==='any'?'Any one of the following':'All of the following'}</b><ul>${s.crit.map(c=>`<li>${esc(c)}</li>`).join('')}</ul></details></div><div class="rf-recommendations"><h4 class="flow-section-heading"><span>2</span> Compare treatment options</h4><div class="rf-options">${group('Standard approach',s.standard,'rf-standard')}${group('Reasonable alternatives',s.alt,'rf-alternatives')}</div>${group('Avoid / cautions in this situation',s.avoid,'rf-cautions')}</div><section class="rf-related" aria-label="Related clinical decisions" data-related-for="${esc(s.id)}"></section><div class="rf-evidence-controls"><button class="xpand" type="button" id="xpandAll" data-open="0" aria-expanded="false">Expand criteria and evidence</button><span>These links open related assessments. Recheck the destination criteria; topic selections do not carry patient findings or establish eligibility.</span></div>`;
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
