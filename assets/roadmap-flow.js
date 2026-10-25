/* Shared roadmap navigation. Topic selection is not a patient classification. */
(() => {
 'use strict';
 const root=new URL('../',document.currentScript.src),esc=s=>String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
 let state=null,links=null,configLoaded=false;
 const configPromise=fetch(new URL('assets/roadmap-links.json?v=20261025',root)).then(r=>{if(!r.ok)throw Error('Navigation unavailable');return r.json();}).catch(()=>null);
 const title=s=>s.name.replace(/^\d+\s*·\s*/, '');
 function initial(stages,fallback){let id;try{id=decodeURIComponent(location.hash.replace(/^#decision-/,''));}catch{return fallback;}return location.hash.startsWith('#decision-')&&stages.some(s=>s.id===id)?id:fallback;}
 function setup({slug,stages,select,topic}){
  state={slug,stages,select,topic,current:null,initialSelection:null};document.body.classList.add('roadmap-streamlined');
  const legend=document.querySelector('.legend');
  if(legend&&!legend.closest('details')){const d=document.createElement('details');d.className='rf-legend';d.innerHTML='<summary>Recommendation labels, evidence grades and delivery requirements</summary>';legend.before(d);d.append(legend);}
  const entry=document.getElementById('entry');if(entry)entry.textContent='Select the clinical question to review. Some assessments can proceed together; urgent care and procedure-specific precautions take priority.';
  const buttons=document.getElementById('stageBtns');
  buttons.innerHTML=stages.map(s=>`<button class="rf-topic" type="button" data-roadmap-decision="${esc(s.id)}">${esc(s.name)}</button>`).join('');
  const overview=document.createElement('details');overview.className='rf-overview';overview.innerHTML='<summary>Browse all clinical decisions</summary>';buttons.before(overview);overview.append(buttons);
  const bar=document.createElement('nav');bar.className='rf-selector';bar.setAttribute('aria-label','Current roadmap decision');
  bar.innerHTML=`<label for="roadmap-decision">Review a clinical situation</label><select id="roadmap-decision">${stages.map(s=>`<option value="${esc(s.id)}">${esc(s.name)}</option>`).join('')}</select><a class="rf-permalink" href="#stage">Link to this decision</a><button type="button" data-rf-overview>All decisions</button>`;
  document.getElementById('answer').before(bar);
  bar.querySelector('select').addEventListener('change',e=>navigate(e.target.value,{replace:true,focus:false,scroll:false}));
  bar.querySelector('[data-rf-overview]').addEventListener('click',()=>{overview.open=true;overview.scrollIntoView({block:'start',behavior:'smooth'});});
  document.addEventListener('click',e=>{
   const b=e.target.closest('[data-roadmap-decision]');if(b){e.preventDefault();navigate(b.dataset.roadmapDecision);}
   const t=e.target.closest('[data-roadmap-topic]');if(t&&state.topic){e.preventDefault();state.topic(t.dataset.roadmapTopic);document.getElementById('topics')?.scrollIntoView({block:'start',behavior:'smooth'});}
  });
  window.addEventListener('hashchange',()=>{if(location.hash&&!location.hash.startsWith('#decision-'))return;const id=initial(stages,state.initialSelection||stages[0].id);if(id&&id!==state.current)state.select(id);});
  const header=document.querySelector('header.top');const offsets=()=>document.documentElement.style.setProperty('--roadmap-header',`${header&&getComputedStyle(header).position==='sticky'?header.getBoundingClientRect().height:0}px`);offsets();if(header&&window.ResizeObserver)new ResizeObserver(offsets).observe(header);
  configPromise.then(data=>{links=data;configLoaded=true;if(state.current)renderRelated(state.current);});
 }
 function navigate(id,{replace=false,focus=true,scroll=true}={}){
  if(!state.stages.some(s=>s.id===id))return;
  history[replace?'replaceState':'pushState'](null,'','#decision-'+encodeURIComponent(id));
  state.select(id);
  if(scroll)document.getElementById('answer').scrollIntoView({block:'start',behavior:'smooth'});
  if(focus)document.querySelector('#answer h3')?.focus({preventScroll:true});
 }
 function render(s,recHTML){
  state.current=s.id;
  document.querySelector('#roadmap-decision').value=s.id;
  document.querySelector('.rf-permalink').href='#decision-'+encodeURIComponent(s.id);
  document.querySelectorAll('[data-roadmap-decision]').forEach(b=>{if(b.classList.contains('rf-topic'))b.setAttribute('aria-current',b.dataset.roadmapDecision===s.id?'true':'false');});
  const group=(label,items,cls)=>items?.length?`<section class="rf-option-group ${cls}"><h4>${label}</h4>${items.map(recHTML).join('')}</section>`:'';
  return `<div class="ahead"><p class="rf-context">Showing this clinical topic</p><h3 tabindex="-1">${esc(s.name)}</h3>${s.ask?`<p class="ask">${esc(s.ask)}</p>`:''}<div class="rf-criteria"><h4 class="flow-section-heading"><span>1</span> Review the situation</h4><p>Topic selection does not establish treatment or transplant eligibility.</p><p>Conditions and checks described for this topic:</p><b>${s.req==='any'?'Any one of the following':'All of the following'}</b><ul>${s.crit.map(c=>`<li>${esc(c)}</li>`).join('')}</ul></div></div><div class="rf-recommendations"><h4 class="flow-section-heading"><span>2</span> Compare treatment options</h4><div class="rf-options">${group('Standard approach',s.standard,'rf-standard')}${group('Reasonable alternatives',s.alt,'rf-alternatives')}</div>${group('Avoid / cautions in this situation',s.avoid,'rf-cautions')}</div><section class="rf-related" aria-label="Related clinical decisions" data-related-for="${esc(s.id)}"></section><div class="rf-evidence-controls"><button class="xpand" type="button" id="xpandAll" data-open="0" aria-expanded="false">Expand criteria and evidence</button><span>These links open related assessments. Recheck the destination criteria; topic selections do not carry patient findings or establish eligibility.</span></div>`;
 }
 function update(s){
  renderRelated(s.id);
  if(!state.initialSelection){state.initialSelection=s.id;if(location.hash==='#decision-'+encodeURIComponent(s.id))requestAnimationFrame(()=>document.getElementById('answer').scrollIntoView({block:'start'}));}
 }
 function renderRelated(id){
  const panel=document.querySelector('[data-related-for]');if(!panel||panel.dataset.relatedFor!==id)return;
  if(!links){panel.innerHTML=configLoaded?'<p>Related-decision shortcuts are unavailable. Use the clinical decision selector above.</p>':'<p>Loading related assessments…</p>';return;}
  const records=links[state.slug]?.[id]||[];
  const items=records.map(r=>{
   const target=r.decision?state.stages.find(s=>s.id===r.decision):null;
   if(r.decision&&!target)return '';
   const label=r.label||(target?title(target):'Review related care');
   const href=r.decision?'#decision-'+encodeURIComponent(r.decision):r.topic?new URL('hcc/?topic='+encodeURIComponent(r.topic)+'#topics',root).href:new URL(r.url,root).href;
   return `<a class="rf-related-link" href="${esc(href)}" ${r.decision?`data-roadmap-decision="${esc(r.decision)}"`:''}><span><b class="flow-if">When</b> ${esc(r.when)}</span><strong>${esc(label)} →</strong></a>`;
  }).join('');
  panel.innerHTML=`<h4 class="flow-section-heading"><span>3</span> Next assessment or care</h4><p>Open the assessment when the stated situation applies. Several may be needed together. Supportive care can accompany treatment or be the main care plan.</p><div class="rf-related-grid">${items}</div>`;
 }
 window.RoadmapFlow={setup,render,update,initial,navigate};
})();
