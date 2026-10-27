/* Display only: reuse source controls and their existing clinical/state handlers. */
(() => {
 'use strict';
 const labels=window.CompactTrailLabels, states=new WeakMap(),riskSources=new Map();
 let followCurrent=null;
 if(!labels)return;
 let protocol;try{protocol=JSON.parse(document.getElementById('protocol-data')?.textContent||'null');}catch{}
 const root=new URL('../',document.currentScript.src),parts=location.pathname.slice(root.pathname.length).split('/').filter(Boolean);
 const slug=protocol?.pathway?.slug||parts[0], plain=s=>String(s||'').replace(/\s+/g,' ').trim();
 const el=(tag,cls,text)=>{const n=document.createElement(tag);if(cls)n.className=cls;if(text!==undefined)n.textContent=text;return n;};
 function describe(row,nav){
  const select=row.querySelector('select'),label=row.querySelector('label'),copy=label?.cloneNode(true);copy?.querySelectorAll('small').forEach(n=>n.remove());
  const fallback=plain(copy?.textContent)||'Next step';let short=fallback,full=fallback;
  if(select?.dataset.layerQuestion){
   const key=slug+'/'+select.dataset.layerStep+'/'+select.dataset.layerQuestion,entry=labels.core[key];
   const source=protocol?.assistants?.[slug+'/'+select.dataset.layerStep]?.questions.find(q=>q.id===select.dataset.layerQuestion)?.label;
   if(entry&&entry.source===source){short=matchMedia('(max-width:760px)').matches&&entry.mobile?entry.mobile:entry.label;full=entry.source;}
  }else if(select?.dataset.layerRisk){
   const entry=labels.riskById[select.dataset.layerRisk];
   const key=slug+'/'+select.dataset.layerStep+'/'+select.dataset.layerRisk,node=document.getElementById('risk-'+select.dataset.layerRisk)?.closest('.risk-question');
   if(entry&&plain(node?.querySelector('label')?.textContent)===entry.source)riskSources.set(key,{source:entry.source,help:node?.querySelector('p')?.textContent||''});
   if(entry&&riskSources.get(key)?.source===entry.source){short=matchMedia('(max-width:760px)').matches&&entry.mobile?entry.mobile:entry.label;full=entry.source;}
  }else if(select?.hasAttribute('data-roadmap-current')){
   const id=location.hash.startsWith('#decision-')?decodeURIComponent(location.hash.slice(10)):select.value,entry=labels.roadmaps[slug+'/'+id];
   const original=[...select.options].find(o=>o.value===id)?.textContent;
   if(entry&&plain(original)===entry.source){short=entry.label;full=entry.source;}
  }
  return {select,label,short,full,action:!!select?.matches('[data-layer-action],#roadmap-next'),binary:[...(select?.options||[])].some(o=>/^(Yes|No)$/.test(plain(o.textContent))),number:plain(row.querySelector('.layer-number')?.textContent),value:select?.value||'',chosen:plain(select?.selectedOptions[0]?.textContent),example:/entry example/.test(label?.textContent||'')};
 }
 function closeEditor(state,focus=true){
  const prior=state.open;state.open=null;state.editors.hidden=true;state.current.hidden=false;if(state.workspace)state.workspace.hidden=false;
  // Closing an editor never commits its draft or leaves it silently staged.
  state.editors.querySelectorAll('select[data-committed]').forEach(select=>{
   if(select.value!==select.dataset.committed){select.value=select.dataset.committed;select.dispatchEvent(new Event('change',{bubbles:true}));}
  });
  state.editors.querySelectorAll('.layer-row').forEach(r=>r.hidden=true);
  state.editors.querySelectorAll('.ct-inline-criteria').forEach(p=>p.hidden=true);
  state.editors.querySelectorAll('[data-layer-criteria]').forEach(b=>b.setAttribute('aria-expanded','false'));
  state.history.querySelectorAll('.ct-chip').forEach(b=>{b.setAttribute('aria-expanded','false');b.classList.remove('is-editing');});
  if(focus&&prior)prior.focus({preventScroll:true});
 }
 function openEditor(state,button,row){
  if(state.open===button){closeEditor(state);return;}
  closeEditor(state,false);state.open=button;state.editors.hidden=false;row.hidden=false;state.current.hidden=true;if(state.workspace)state.workspace.hidden=true;
  button.setAttribute('aria-expanded','true');button.classList.add('is-editing');
  button.scrollIntoView({block:'nearest',inline:'nearest'});state.editors.scrollIntoView({block:'start',behavior:'instant'});
 }
 function bindInlineCriteria(row,info){
  const button=row.querySelector('[data-layer-criteria]');if(!button)return;
  const key=slug+'/'+info.select.dataset.layerStep,q=protocol?.assistants?.[key]?.questions.find(q=>q.id===info.select.dataset.layerQuestion);
  const risk=riskSources.get(key+'/'+info.select.dataset.layerRisk);
  if(!q&&!risk){button.disabled=true;button.setAttribute('aria-label','Criteria unavailable in this editor. Use All decisions to open the source decision.');return;}
  let panel;
  const refresh=()=>{
   if(!panel)return;
   panel.replaceChildren(el('p','ct-original-question',q?.label||risk.source));
   if(q){
    if(q.help)panel.append(el('p','',q.help));
    if(info.select.value!==info.select.dataset.committed)panel.append(el('p','layer-stage-status','Definitions for the unapplied selection. Recorded findings and the result have not changed.'));
    const content=el('div');content.innerHTML=window.DecisionAssistant.definitions(q,info.select.value,protocol.sources)+window.DecisionAssistant.evidence(q.refs,protocol.sources);
    content.querySelectorAll('.assistant-selected').forEach(n=>n.remove());
    content.querySelectorAll('details[data-relevant="true"]').forEach(d=>d.open=true);panel.append(content);
   }else panel.append(el('p','',risk.help));
  };
  info.select.addEventListener('change',refresh);
  button.addEventListener('click',ev=>{
   ev.preventDefault();ev.stopPropagation();
   if(!panel){
    panel=el('div','ct-inline-criteria');panel.id='compact-criteria-'+info.select.id;
    row.after(panel);button.setAttribute('aria-controls',panel.id);panel.hidden=true;
   }
   refresh();
   panel.hidden=!panel.hidden;button.setAttribute('aria-expanded',String(!panel.hidden));
   if(!panel.hidden)row.closest('.ct-editors,.layer-current')?.scrollIntoView({block:'start',behavior:'instant'});
  });
 }
 function shortControl(row,info,editing=false){
  if(!info.label||row.dataset.compactPrepared)return;row.dataset.compactPrepared='true';
  const context=info.label.querySelector('small');
  if(context)context.classList.add('ct-context');
  // A bare Yes/No needs its complete question to keep the direction unambiguous.
  info.label.replaceChildren(el('span','ct-short-title',!protocol?'Clinical topic':!editing&&info.binary?info.full:info.short));
  if(info.example)info.label.append(el('span','ct-example','Example'));
  info.select.setAttribute('aria-description',info.full);
  if(!editing&&protocol)bindInlineCriteria(row,info);
  if(editing){
   const question=el('p','ct-original-question',info.full);info.label.after(question);
   if(context)row.querySelector('.layer-choice').prepend(context);
   const value=row.querySelector('.layer-value');if(value)value.classList.add('ct-exact-value');
   info.select.dataset.compactOriginal=info.value;
   bindInlineCriteria(row,info);
  }
 }
 function arrangeWorkspace(state){
  if(!protocol||state.workspace)return;
  const decision=document.querySelector('.decision'),head=decision?.querySelector('.question-head'),result=decision?.querySelector('#decision-results');
  if(!head||!result)return;
  const workspace=decision;workspace.classList.add('ct-workspace');state.current.before(workspace);
  const context=decision.querySelector('.contextline');
  const instruction=el('p','ct-workflow-hint','Choose a finding → Use finding → choose a next step.');(context||head).after(instruction,state.current,result);
  // Move the original controls and result together. Their clinical handlers,
  // conditions, evidence, high-risk reviews and care-context capture stay intact.
  state.workspace=workspace;state.result=result;state.orders=decision.querySelector('.orders');document.body.classList.add('single-decision-workspace');
  const eyebrow=head.querySelector('.eyebrow');if(eyebrow?.firstChild?.nodeType===3)eyebrow.firstChild.textContent='Current assessment ';
 }
 function followWorkspace(state){
  if(!followCurrent||!state.workspace)return;
  const kind=followCurrent;followCurrent=null;
  requestAnimationFrame(()=>requestAnimationFrame(()=>{
   if(!state.workspace.isConnected)return;
   const pending=state.current.querySelector('select:not([data-layer-action])');
   const target=kind==='step'?state.workspace:pending?state.current:state.result;
   target?.scrollIntoView({block:'start',behavior:'instant'});
   const focus=kind==='step'?state.workspace.querySelector('#question'):pending||state.result?.querySelector('h3');
   if(focus){if(!focus.matches('select'))focus.setAttribute('tabindex','-1');focus.focus({preventScroll:true});}
  }));
 }
 function enhance(nav){
  const historyEl=nav.querySelector('.layer-history'),current=nav.querySelector('.layer-current');if(!historyEl||!current)return;
  let state=states.get(nav);
  if(!state){
   const strip=el('div','ct-strip'),heading=nav.querySelector('.layer-heading');nav.prepend(strip);strip.append(heading,historyEl);
   const menu=el('details','ct-menu'),summary=el('summary','',protocol?protocol.pathway.code:slug.toUpperCase()),items=el('div','ct-menu-items');
   summary.setAttribute('aria-label',(protocol?'Findings':'Topics viewed')+' menu');menu.append(summary,items);
   [...heading.querySelectorAll('button,a')].forEach(n=>{if(n.matches('[data-pathway-overview],[data-rf-overview]'))n.textContent='Browse all decisions';items.append(n);});heading.replaceChildren(menu);
   items.prepend(el('p','ct-menu-hint',protocol?'Review recorded findings here. Confirm findings and choose next steps below.':'Revisit earlier topics above, or browse another topic here. Use the conditional next-step links to continue.'));
   items.addEventListener('click',ev=>{if(ev.target.closest('button,a'))menu.open=false;});
   const editors=el('div','ct-editors');editors.hidden=true;current.before(editors);
   const entry=el('p','ct-entry-note');entry.hidden=true;editors.before(entry);
   const close=el('button','ct-close',protocol?'Back to current step':'Back to current topic');close.type='button';close.addEventListener('click',()=>closeEditor(state));editors.append(close);
   state={nav,strip,items,entry,history:historyEl,current,editors,close,open:null};states.set(nav,state);nav.classList.add('compact-trail');
   const earlier=el('button','ct-scroll-button','‹'),later=el('button','ct-scroll-button','›');earlier.type=later.type='button';earlier.setAttribute('aria-label','Earlier findings');later.setAttribute('aria-label','Later findings');earlier.hidden=later.hidden=true;
   historyEl.before(earlier);historyEl.after(later);state.earlier=earlier;state.later=later;
   [earlier,later].forEach((button,i)=>button.addEventListener('click',()=>historyEl.scrollBy({left:(i?1:-1)*historyEl.clientWidth*.65,behavior:matchMedia('(prefers-reduced-motion:reduce)').matches?'instant':'smooth'})));
   historyEl.addEventListener('scroll',()=>scrollControls(state));
   historyEl.setAttribute('aria-label',protocol?'Earlier findings — review or edit':'Topic navigation history');
   historyEl.addEventListener('keydown',ev=>{
    if(!['ArrowLeft','ArrowRight','Home','End'].includes(ev.key)||!ev.target.matches('.ct-chip'))return;
    const buttons=[...historyEl.querySelectorAll('button.ct-chip')],n=buttons.indexOf(ev.target),i=ev.key==='Home'?0:ev.key==='End'?buttons.length-1:Math.max(0,Math.min(buttons.length-1,n+(ev.key==='ArrowRight'?1:-1)));
    ev.preventDefault();buttons[i]?.focus({preventScroll:true});buttons[i]?.scrollIntoView({block:'nearest',inline:'nearest'});
   });
   nav.addEventListener('keydown',ev=>{if(ev.key==='Escape'&&state.open){ev.preventDefault();ev.stopPropagation();closeEditor(state);}});
   if(window.ResizeObserver)new ResizeObserver(()=>measure(state)).observe(strip);
  }
  arrangeWorkspace(state);
  if(!protocol&&!state.current.closest('.ct-menu-items'))state.items.append(state.current);
  const raw=[...historyEl.querySelectorAll('.layer-row')];
  if(protocol&&(raw.length||(!historyEl.children.length&&state.editors.querySelector('.layer-row')))){
   closeEditor(state,false);state.editors.replaceChildren(state.close);
   const chips=[];
   for(const [index,row] of raw.entries()){
    const number=row.querySelector('.layer-number');if(number){number.textContent=index+1;number.title='Finding '+(index+1);}
    const info=describe(row,nav);if(!info.select)continue;
    shortControl(row,info,true);row.id='compact-editor-'+info.select.id;row.hidden=true;state.editors.append(row);
    const button=el('button','ct-chip');button.type='button';button.setAttribute('aria-controls',row.id);button.setAttribute('aria-expanded','false');
    button.setAttribute('aria-label',`Finding ${info.number}, ${info.short}. ${info.full} ${info.example?'Example answer: ':'Recorded answer: '}${info.chosen}. Review or edit.`);
    button.classList.toggle('is-example',info.example);button.classList.toggle('is-unknown',info.value==='unknown');
    button.append(el('span','ct-number',info.number),el('span','ct-label',info.short),el('span','ct-state',info.example?'Example':info.value==='unknown'?'Uncertain / not assessed':'Recorded'));
    const editIcon=el('span','ct-edit-icon','✎');editIcon.setAttribute('aria-hidden','true');button.append(editIcon);
    button.addEventListener('click',()=>openEditor(state,button,row));chips.push(button);
   }
   historyEl.replaceChildren(...chips);
   const completed=[...state.editors.querySelectorAll('.layer-row')];
   completed.forEach(row=>row.querySelector('.layer-choice').append(el('p','ct-clear-note','Applying a changed finding clears later dependent findings. Selecting or reviewing alone does not change the pathway.')));
  }
  if(!protocol&&historyEl.querySelector('.layer-history-disclosure')){
   const chips=[...historyEl.querySelectorAll('[data-roadmap-trail]')].map(button=>{
    const n=Number(button.dataset.roadmapTrail),id=history.state?.roadmapTrail?.[n]?.id,full=plain(button.textContent),entry=labels.roadmaps[slug+'/'+id];
    const short=entry&&entry.source===full?entry.label:full;
    const condition=button.closest('li')?.querySelector('p')?.textContent;
    button.className='ct-chip';button.setAttribute('aria-label','Previously viewed topic: '+full+'. Navigation only.');
    if(condition)button.setAttribute('aria-description',condition);
    button.replaceChildren(el('span','ct-number','↶'),el('span','ct-label',short),el('span','ct-state','Viewed'));
    return button;
   });
   historyEl.replaceChildren(...chips);
  }
  const pending=current.querySelector('.layer-row');
  if(pending&&!pending.dataset.compactPrepared){
   // A fresh source render replaces the current question after a real choice.
   closeEditor(state,false);const number=pending.querySelector('.layer-number');if(protocol&&number){const ordinal=state.editors.querySelectorAll('.layer-row').length+1;number.textContent=ordinal;number.title='Finding '+ordinal;}const info=describe(pending,nav);shortControl(pending,info);
   historyEl.querySelectorAll('.ct-current-chip').forEach(b=>b.remove());
   const button=el('span','ct-chip ct-current-chip');button.setAttribute('aria-current','step');
   button.setAttribute('aria-label',protocol?`Current finding ${info.number}, ${info.short}. Choose and confirm below.`:`Current topic: ${info.full}. Navigation only.`);
   button.append(el('span','ct-number',protocol?info.number:'↗'),el('span','ct-label',info.short),el('span','ct-state',protocol?'Current':'Current topic'));
   current.classList.toggle('ct-action-only',info.action);
   historyEl.append(button);
   requestAnimationFrame(()=>{historyEl.scrollLeft=historyEl.scrollWidth;});
  }else if(!pending&&!current.querySelector('.layer-complete')){historyEl.querySelectorAll('.ct-current-chip').forEach(b=>b.remove());current.classList.remove('ct-action-only');}
  if(state.workspace){
   const complete=!!current.querySelector('.layer-complete');current.classList.toggle('ct-action-only',complete);
   const heading=state.result.querySelector('.section-head h3'),text=complete?'Choose next step':'Next-step options';if(heading&&heading.textContent!==text)heading.textContent=text;
   if(complete&&!historyEl.querySelector('.ct-current-chip')){const marker=el('span','ct-chip ct-current-chip');marker.setAttribute('aria-current','step');marker.append(el('span','ct-number','→'),el('span','ct-label','Next step'),el('span','ct-state','Current'));historyEl.append(marker);}
   // Keep the original current and recorded definitions visible with the finding.
   if(state.orders&&!state.workspace.classList.contains('dw-ready')){const anchor=complete?state.result:current;if(anchor.nextElementSibling!==state.orders)anchor.after(state.orders);}
   state.workspace.classList.toggle('ct-has-visible-help',!!current.querySelector('.layer-help'));
  }
  if(protocol){
   const first=state.editors.querySelector('select[data-layer-step]')||current.querySelector('select[data-layer-step]');
   const start=protocol.pathway.steps.findIndex(s=>s.id===first?.dataset.layerStep);state.entry.hidden=start<=0;
   const text=start>0?'View earlier decisions from the top row.':'';if(state.entry.textContent!==text)state.entry.textContent=text;
  }
  nav.querySelectorAll(':scope>.ci-reading').forEach(n=>state.items.append(n));measure(state);followWorkspace(state);
 }
 function scrollControls(state){const box=state.history,show=matchMedia('(min-width:761px)').matches&&box.scrollWidth>box.clientWidth+2;state.earlier.hidden=state.later.hidden=!show;state.earlier.disabled=box.scrollLeft<2;state.later.disabled=box.scrollLeft+box.clientWidth>=box.scrollWidth-2;}
 function measure(state){scrollControls(state);const h=Math.ceil(state.strip.getBoundingClientRect().height);document.documentElement.style.setProperty(protocol?'--pathway-nav-height':'--roadmap-trail-height',h+'px');}
 const announcement=el('p','sr-only');announcement.setAttribute('aria-live','polite');document.body.append(announcement);
 document.addEventListener('change',ev=>{if(ev.target.matches('.ct-editors select'))requestAnimationFrame(()=>{announcement.textContent=ev.target.isConnected&&ev.target.value!==ev.target.dataset.committed?'Unapplied choice. Use Apply change to record it, or Cancel to keep the recorded finding.':'';});},true);
 document.addEventListener('click',ev=>{if(ev.target.closest('[data-record-finding],[data-record-risk],[data-cancel-finding],.ct-close,[data-dw-browse]'))announcement.textContent='';},true);
 document.addEventListener('click',ev=>{if(ev.target.closest('[data-record-finding]:not(:disabled),[data-record-risk]:not(:disabled)'))followCurrent='finding';else if(ev.target.closest('.next-action [data-step],[data-dw-browse],[data-pathway-clear],[data-pathway-example]'))followCurrent='step';},true);
 let queued=false;const scan=()=>{queued=false;document.querySelectorAll('.layer-nav,.rf-selector').forEach(enhance);};
 new MutationObserver(()=>{if(!queued){queued=true;queueMicrotask(scan);}}).observe(document.body,{childList:true,subtree:true});
 scan();
})();
