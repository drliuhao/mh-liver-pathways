/* Display only: reuse source controls and their existing clinical/state handlers. */
(() => {
 'use strict';
 const labels=window.CompactTrailLabels, states=new WeakMap(),riskSources=new Map();
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
  }else if(select?.dataset.roadmapLayer!==undefined){
   const n=Number(select.dataset.roadmapLayer),trail=history.state?.roadmapTrail;
   let id=n===0?select.value:trail?.[n]?.id;
   if(!id&&row.closest('.layer-history'))id=decodeURIComponent(location.hash.replace(/^#decision-/,''));
   const original=nav.querySelector('#roadmap-decision')?.querySelector(`option[value="${CSS.escape(id||'')}"]`)?.textContent;
   const entry=labels.roadmaps[slug+'/'+id];
   if(entry&&plain(original)===entry.source){short=entry.label;full=entry.source;}
   if(row.closest('.layer-current')){short='Next step';full='Next assessment or care';}
  }
  return {select,label,short,full,action:!!select?.matches('[data-layer-action],#roadmap-next'),binary:[...(select?.options||[])].some(o=>/^(Yes|No)$/.test(plain(o.textContent))),number:plain(row.querySelector('.layer-number')?.textContent),value:select?.value||'',chosen:plain(select?.selectedOptions[0]?.textContent),example:/entry example/.test(label?.textContent||'')};
 }
 function closeEditor(state,focus=true){
  const prior=state.open;state.open=null;state.editors.hidden=true;state.current.hidden=false;
  state.editors.querySelectorAll('.layer-row').forEach(r=>r.hidden=true);
  state.editors.querySelectorAll('.ct-inline-criteria').forEach(p=>p.hidden=true);
  state.editors.querySelectorAll('[data-layer-criteria]').forEach(b=>b.setAttribute('aria-expanded','false'));
  state.history.querySelectorAll('.ct-chip').forEach(b=>{b.setAttribute('aria-expanded','false');b.classList.remove('is-editing');});
  if(focus&&prior)prior.focus({preventScroll:true});
 }
 function openEditor(state,button,row){
  if(state.open===button){closeEditor(state);return;}
  closeEditor(state,false);state.open=button;state.editors.hidden=false;row.hidden=false;state.current.hidden=true;
  button.setAttribute('aria-expanded','true');button.classList.add('is-editing');
  button.scrollIntoView({block:'nearest',inline:'nearest'});state.editors.scrollIntoView({block:'start',behavior:'instant'});
 }
 function bindInlineCriteria(row,info){
  const button=row.querySelector('[data-layer-criteria]');if(!button)return;
  const key=slug+'/'+info.select.dataset.layerStep,q=protocol?.assistants?.[key]?.questions.find(q=>q.id===info.select.dataset.layerQuestion);
  const risk=riskSources.get(key+'/'+info.select.dataset.layerRisk);
  if(!q&&!risk){button.disabled=true;button.setAttribute('aria-label','Criteria unavailable in this editor. Use All decisions to open the source decision.');return;}
  let panel;
  button.addEventListener('click',ev=>{
   ev.preventDefault();ev.stopPropagation();
   if(!panel){
    panel=el('div','ct-inline-criteria');panel.id='compact-criteria-'+info.select.id;
    panel.append(el('p','ct-original-question',q?.label||risk.source));
    if(q){
     if(q.help)panel.append(el('p','',q.help));
     const content=el('div');content.innerHTML=window.DecisionAssistant.definitions(q,info.select.value,protocol.sources)+window.DecisionAssistant.evidence(q.refs,protocol.sources);
     content.querySelectorAll('.assistant-selected').forEach(n=>n.remove());
     content.querySelectorAll('details[data-relevant="true"]').forEach(d=>d.open=true);panel.append(content);
    }else panel.append(el('p','',risk.help));
    row.after(panel);button.setAttribute('aria-controls',panel.id);panel.hidden=true;
   }
   panel.hidden=!panel.hidden;button.setAttribute('aria-expanded',String(!panel.hidden));
   if(!panel.hidden)row.closest('.ct-editors')?.scrollIntoView({block:'start',behavior:'instant'});
  });
 }
 function shortControl(row,info,editing=false){
  if(!info.label||row.dataset.compactPrepared)return;row.dataset.compactPrepared='true';
  const context=info.label.querySelector('small');
  if(context)context.classList.add('ct-context');
  // A bare Yes/No needs its complete question to keep the direction unambiguous.
  info.label.replaceChildren(el('span','ct-short-title',!editing&&info.binary?info.full:info.short));
  if(info.example)info.label.append(el('span','ct-example','Example'));
  info.select.setAttribute('aria-description',info.full);
  if(editing){
   const question=el('p','ct-original-question',info.full);info.label.after(question);
   if(context)row.querySelector('.layer-choice').prepend(context);
   const value=row.querySelector('.layer-value');if(value)value.classList.add('ct-exact-value');
   info.select.dataset.compactOriginal=info.value;
   bindInlineCriteria(row,info);
  }
 }
 function enhance(nav){
  const historyEl=nav.querySelector('.layer-history'),current=nav.querySelector('.layer-current');if(!historyEl||!current)return;
  let state=states.get(nav);
  if(!state){
   const strip=el('div','ct-strip'),heading=nav.querySelector('.layer-heading');nav.prepend(strip);strip.append(heading,historyEl);
   const menu=el('details','ct-menu'),summary=el('summary','',protocol?protocol.pathway.code:slug.toUpperCase()),items=el('div','ct-menu-items');
   summary.setAttribute('aria-label',(protocol?'Findings':'Topics viewed')+' menu');menu.append(summary,items);
   [...heading.querySelectorAll('button,a')].forEach(n=>items.append(n));heading.replaceChildren(menu);
   items.prepend(el('p','ct-menu-hint',protocol?'Select a finding to review. Swipe the strip on a phone.':'Topics viewed · navigation only. Swipe the strip on a phone.'));
   items.addEventListener('click',ev=>{if(ev.target.closest('button,a'))menu.open=false;});
   const editors=el('div','ct-editors');editors.hidden=true;current.before(editors);
   const entry=el('p','ct-entry-note');entry.hidden=true;editors.before(entry);
   const close=el('button','ct-close','Back to current question');close.type='button';close.addEventListener('click',()=>closeEditor(state));editors.append(close);
   state={nav,strip,items,entry,history:historyEl,current,editors,close,open:null};states.set(nav,state);nav.classList.add('compact-trail');
   const earlier=el('button','ct-scroll-button','‹'),later=el('button','ct-scroll-button','›');earlier.type=later.type='button';earlier.setAttribute('aria-label','Earlier findings');later.setAttribute('aria-label','Later findings');earlier.hidden=later.hidden=true;
   historyEl.before(earlier);historyEl.after(later);state.earlier=earlier;state.later=later;
   [earlier,later].forEach((button,i)=>button.addEventListener('click',()=>historyEl.scrollBy({left:(i?1:-1)*historyEl.clientWidth*.65,behavior:matchMedia('(prefers-reduced-motion:reduce)').matches?'instant':'smooth'})));
   historyEl.addEventListener('scroll',()=>scrollControls(state));
   historyEl.setAttribute('aria-label',protocol?'Chosen findings and next question':'Topics viewed and next step');
   historyEl.addEventListener('keydown',ev=>{
    if(!['ArrowLeft','ArrowRight','Home','End'].includes(ev.key)||!ev.target.matches('.ct-chip'))return;
    const buttons=[...historyEl.querySelectorAll('.ct-chip')],n=buttons.indexOf(ev.target),i=ev.key==='Home'?0:ev.key==='End'?buttons.length-1:Math.max(0,Math.min(buttons.length-1,n+(ev.key==='ArrowRight'?1:-1)));
    ev.preventDefault();buttons[i]?.focus({preventScroll:true});buttons[i]?.scrollIntoView({block:'nearest',inline:'nearest'});
   });
   nav.addEventListener('keydown',ev=>{if(ev.key==='Escape'&&state.open){ev.preventDefault();closeEditor(state);}});
   if(window.ResizeObserver)new ResizeObserver(()=>measure(state)).observe(strip);
  }
  const raw=[...historyEl.children].filter(r=>r.classList.contains('layer-row'));
  if(raw.length||(!historyEl.children.length&&state.editors.querySelector('.layer-row'))){
   closeEditor(state,false);state.editors.replaceChildren(state.close);
   const chips=[];
   for(const row of raw){
    const info=describe(row,nav);if(!info.select)continue;
    shortControl(row,info,true);row.id='compact-editor-'+info.select.id;row.hidden=true;state.editors.append(row);
    const button=el('button','ct-chip');button.type='button';button.setAttribute('aria-controls',row.id);button.setAttribute('aria-expanded','false');
    button.setAttribute('aria-label',protocol?`Finding ${info.number}: ${info.short}. ${info.full} ${info.example?'Example answer: ':'Answer: '}${info.chosen}. Review or edit.`:`Topic ${info.number}: ${info.short}. Viewed topic: ${info.chosen}. Review or change topic.`);
    button.classList.toggle('is-example',info.example);button.classList.toggle('is-unknown',info.value==='unknown');
    button.append(el('span','ct-number',info.number),el('span','ct-label',info.short),el('span','ct-state',info.example?'Example':info.value==='unknown'?'Uncertain / not assessed':protocol?'Chosen':'Viewed'));
    button.addEventListener('click',()=>openEditor(state,button,row));chips.push(button);
   }
   historyEl.replaceChildren(...chips);
   const completed=[...state.editors.querySelectorAll('.layer-row')];
   completed.slice(0,-1).forEach(row=>row.querySelector('.layer-choice').append(el('p','ct-clear-note',protocol?'Changing this clears later findings and next-step choices.':'Changing this replaces later topics.')));
  }
  const pending=current.querySelector('.layer-row');
  if(pending&&!pending.dataset.compactPrepared){
   // A fresh source render replaces the current question after a real choice.
   closeEditor(state,false);const info=describe(pending,nav);shortControl(pending,info);
   historyEl.querySelectorAll('.ct-current-chip').forEach(b=>b.remove());
   const button=el('button','ct-chip ct-current-chip');button.type='button';button.setAttribute('aria-current','step');
   button.setAttribute('aria-label',info.action?'Next steps: review options and their conditions below.':`Finding ${info.number}: ${info.short}. Choose below.`);
   button.append(el('span','ct-number',info.action?'→':info.number),el('span','ct-label',info.action?'Next steps':info.short),el('span','ct-state',info.action?'Options & criteria ↓':'Choose below ↓'));
   current.classList.toggle('ct-action-only',info.action);
   button.addEventListener('click',()=>{closeEditor(state,false);const target=info.action?document.querySelector(protocol?'#current-result':'.rf-related'):current;target?.scrollIntoView({block:'start',behavior:'instant'});if(!info.action)info.select?.focus({preventScroll:true});});historyEl.append(button);
   requestAnimationFrame(()=>{historyEl.scrollLeft=historyEl.scrollWidth;});
  }else if(!pending){historyEl.querySelectorAll('.ct-current-chip').forEach(b=>b.remove());current.classList.remove('ct-action-only');}
  if(protocol){
   const first=state.editors.querySelector('select[data-layer-step]')||current.querySelector('select[data-layer-step]');
   const start=protocol.pathway.steps.findIndex(s=>s.id===first?.dataset.layerStep);state.entry.hidden=start<=0;
   const text=start>0?'Starting here · earlier decisions are not shown in this trail.':'';if(state.entry.textContent!==text)state.entry.textContent=text;
  }
  nav.querySelectorAll(':scope>.ci-reading').forEach(n=>state.items.append(n));measure(state);
 }
 function scrollControls(state){const box=state.history,show=matchMedia('(min-width:761px)').matches&&box.scrollWidth>box.clientWidth+2;state.earlier.hidden=state.later.hidden=!show;state.earlier.disabled=box.scrollLeft<2;state.later.disabled=box.scrollLeft+box.clientWidth>=box.scrollWidth-2;}
 function measure(state){scrollControls(state);const h=Math.ceil(state.strip.getBoundingClientRect().height);document.documentElement.style.setProperty(protocol?'--pathway-nav-height':'--roadmap-trail-height',h+'px');}
 const announcement=el('p','sr-only');announcement.setAttribute('aria-live','polite');document.body.append(announcement);
 document.addEventListener('change',ev=>{if(ev.target.matches('.ct-editors select')&&ev.target.value!==ev.target.dataset.compactOriginal)requestAnimationFrame(()=>{announcement.textContent=protocol?'Choice changed. Later findings cleared; choose the next finding.':'Topic changed. Later topics replaced.';});},true);
 let queued=false;const scan=()=>{queued=false;document.querySelectorAll('.layer-nav,.rf-selector').forEach(enhance);};
 new MutationObserver(()=>{if(!queued){queued=true;queueMicrotask(scan);}}).observe(document.body,{childList:true,subtree:true});
 scan();
})();
