/* Presentation only: full source text is retained; clinical decision state is unchanged. */
(() => {
 'use strict';
 const supported=typeof HTMLElement.prototype.showPopover==='function';
 if(!supported||(!document.getElementById('protocol-data')&&!document.getElementById('answer')))return; // Native details remain usable in older browsers.
 let printDetails=[],pendingEvidence=null;
 let counter=0,current=null,expanded=false,queued=false,printing=false,scrollLock='',mobileHistory=false,ignoreBack=false;
 const items=new Set(),touch=()=>matchMedia('(max-width:760px)').matches;
 const copy=window.ContextualCopy||{headings:{},help:{},recommendations:{}};
 const recommendationCopy=new Map(Object.values(copy.recommendations).map(c=>[c.source,c]));
 const sources=JSON.parse(document.getElementById('protocol-data')?.textContent||'{}').sources||{};
 function authority(node){
  const records=[...node.querySelectorAll('[data-ref],a[href]')].map(n=>sources[n.dataset.ref]||Object.values(sources).find(s=>s.url===n.getAttribute('href'))).filter(Boolean);
  const labels={'Allocation policy':'OPTN policy','NLRB guidance':'NLRB guidance','Clinical guidance':'Guideline','Cohort evidence':'Cohort evidence','Prospective cohort evidence':'Prospective cohort','Randomized trial':'Randomized trial','Expert consensus':'Consensus','Full-text clinical evidence':'Clinical study','Pathology reporting standard':'Pathology standard','Supportive-care reference':'Supportive care'};
  return [...new Set(records.map(s=>labels[s.kind]||s.kind))].join(' · ');
 }
 function note(node,label){
  if(!node||node.closest('.ci-unit,.ci-prose,.ci-panel'))return;
  const d=document.createElement('details');d.className='ci-prose';
  const s=document.createElement('summary');s.textContent=label;d.append(s);node.before(d);d.append(node);return enhance(d);
 }
 function evidenceLabel(node){const count=node.matches('.assistant-evidence')?node.children.length:node.querySelectorAll('.cite,.refchip').length;return authority(node)||'Evidence'+(count?' ('+count+')':'');}
 function compactHelp(node,entry){
  if(!entry||node.textContent!==entry.source||node.closest('.ci-unit,.assistant-criteria'))return;
  const question=node.closest('.assistant-question'),d=document.createElement('details'),s=document.createElement('summary');
  d.className='ci-prose';d.dataset.contextTitle=entry.title;s.textContent=entry.concise;d.append(s);node.before(d);
  const id=node.id;node.removeAttribute('id');d.append(node);
  const evidence=question.querySelector(':scope > .assistant-evidence');if(evidence?.children.length)d.append(evidence);
  const item=enhance(d);item.wrapper.classList.add('ci-summary');item.button.id=id;
  item.wrapper.dataset.copySource=entry.source;
  const label=question.querySelector('label'),text=label?.lastChild;if(text?.nodeType===Node.TEXT_NODE&&text.textContent===entry.title)text.textContent=entry.label||entry.title;
  const types=authority(d);if(types){const small=document.createElement('small');small.className='ci-authority';small.textContent=types;item.button.append(small);}
 }
 function compactHeading(node,entry){
  if(!node||!entry||node.textContent!==entry.source||node.dataset.contextCopy)return;
  node.dataset.contextCopy='true';node.textContent=entry.concise;
  if(entry.concise===entry.source)return;
  const full=document.createElement('p');full.textContent=entry.source;node.after(full);const item=note(full,'Full decision question');
  item.wrapper.classList.add('ci-heading-info');item.button.setAttribute('aria-label','Read the full decision question');
  item.heading=node;item.displayCopy=entry;
  if(expanded)inline(item,true);
 }
 function compactRecommendations(){
  document.querySelectorAll('#answer .rec > div:not(.recmeta):not(.opts):not(.ci-unit)').forEach(node=>{
   const entry=recommendationCopy.get(node.textContent);if(!entry||node.dataset.contextCopy||node.closest('.rf-cautions'))return;
   node.dataset.contextCopy='true';node.textContent=entry.concise;
   const details=document.createElement('details');details.className='ci-prose';const summary=document.createElement('summary');summary.textContent='Full explanation';details.append(summary);node.after(details);
   const original=document.createElement('p');original.className='ci-original';original.textContent=entry.source;
   details.querySelector('summary').after(original);details.dataset.contextTitle='Recommendation: full explanation and evidence';
   const item=enhance(details);item.copyTarget=node;if(expanded)inline(item,true);
  });
 }
 function compactChrome(){
  const section=document.querySelector('.decision');if(!section||section.dataset.contextChrome)return;
  section.dataset.contextChrome='true';
  const heading=(selector,text)=>{const n=section.querySelector(selector);if(n)n.textContent=text;};
  heading('.orders .section-head h3','Findings');heading('.stops .section-head h3','Reasons to reassess');
  heading('.full-tests > summary','Full checklist and sources');
  const usage=document.createElement('div'),logic=section.querySelector('.logic-note');
  if(logic){const original=logic.cloneNode(true);original.removeAttribute('class');usage.append(original);logic.textContent='Transplant suitability and exception eligibility are separate decisions.';}
  section.querySelectorAll('.assistant-footnote,.stopnote').forEach(n=>usage.append(n));
  section.querySelector('.contextline').append(usage);note(usage,'Using this page');
 }
 function position(item){
  if(!item||item.modal||item.inline)return;
  const p=item.panel,r=item.button.getBoundingClientRect(),vw=document.documentElement.clientWidth,vh=innerHeight;
  const width=Math.min(480,vw-24);p.style.width=width+'px';p.style.maxHeight=Math.floor(vh*.7)+'px';
  const height=p.getBoundingClientRect().height,below=vh-r.bottom-12,above=r.top-12;
  const top=below>=height||below>=above?Math.min(r.bottom+6,vh-height-12):Math.max(12,r.top-height-6);
  p.style.left=Math.min(Math.max(12,r.left),vw-width-12)+'px';p.style.top=Math.max(12,top)+'px';
 }
 function resetPanel(item){
  item.panel.classList.remove('ci-sheet');item.panel.style.cssText='';
  if(item.panel.matches(':popover-open'))item.panel.hidePopover();
  if(item.modalHost){item.modalHost.close();item.details.append(item.panel);item.modalHost.remove();item.modalHost=null;}
  item.panel.classList.remove('ci-inline-panel');
 }
 function close({focus=false,fromBack=false}={}){
  if(!current)return;
  const item=current;current=null;clearTimeout(item.leave);clearTimeout(item.enter);resetPanel(item);
  item.details.open=false;item.button.setAttribute('aria-expanded','false');item.pinned=false;
  if(item.modal){document.body.style.overflow=scrollLock;item.modal=false;if(mobileHistory&&!fromBack){ignoreBack=true;history.back();}mobileHistory=false;}
  if(focus&&item.button.isConnected)item.button.focus({preventScroll:true});
 }
 function show(item,pin=false,keyboard=false){
  if(expanded||printing)return;
  clearTimeout(item.leave);
  if(current===item){if(pin)item.pinned=true;return;}
  close();current=item;item.pinned=pin;item.inline=false;item.details.classList.remove('ci-inline');item.details.open=true;
  item.button.setAttribute('aria-expanded','true');item.panel.setAttribute('role','dialog');
  if(touch()){
   item.modal=true;item.panel.removeAttribute('popover');item.panel.removeAttribute('role');item.panel.classList.add('ci-sheet');scrollLock=document.body.style.overflow;document.body.style.overflow='hidden';const host=document.createElement('dialog');host.className='ci-modal-shell';host.setAttribute('aria-labelledby',item.panel.id+'-title');item.modalHost=host;host.append(item.panel);document.body.append(host);host.addEventListener('cancel',ev=>{ev.preventDefault();close({focus:true});});host.addEventListener('click',ev=>{if(ev.target===host)close({focus:true});});host.showModal();
   history.pushState({...history.state,contextualExplanation:true},'',location.href);mobileHistory=true;
  }else{item.panel.setAttribute('popover','manual');item.panel.showPopover();position(item);if(keyboard)item.closeButton.focus();}
 }
 function inline(item,on){
  resetPanel(item);item.inline=on;item.details.classList.toggle('ci-inline',on);item.details.open=on;
  item.button.setAttribute('aria-expanded',String(on));item.panel.removeAttribute('popover');item.panel.setAttribute('role','region');item.panel.classList.toggle('ci-inline-panel',on);
  if(item.copyTarget)item.copyTarget.hidden=on;
  if(item.heading)item.heading.textContent=on?item.displayCopy.source:item.displayCopy.concise;
 }
 function enhance(details){
  if(details.dataset.contextReady||details.closest('.ci-panel'))return;
  const summary=details.querySelector(':scope > summary');if(!summary)return;
  details.dataset.contextReady='true';
  const wrapper=document.createElement('div');wrapper.className='ci-unit';details.before(wrapper);
  const button=document.createElement('button');button.type='button';button.className='ci-trigger';
  const label=summary.textContent.trim();button.innerHTML='<span class="ci-label"></span><span class="ci-icon" aria-hidden="true">i</span>';button.querySelector('.ci-label').textContent=label;
  const panel=document.createElement('div');panel.className='ci-panel';panel.id='context-info-'+(++counter);panel.setAttribute('aria-labelledby',panel.id+'-title');
  const header=document.createElement('div');header.className='ci-panel-head';
  const title=document.createElement('strong');title.id=panel.id+'-title';title.textContent=details.dataset.contextTitle||label;
  const closeButton=document.createElement('button');closeButton.type='button';closeButton.className='ci-close';closeButton.setAttribute('aria-label','Close '+label);closeButton.textContent='×';
  header.append(title,closeButton);const body=document.createElement('div');body.className='ci-body';
  [...details.childNodes].filter(n=>n!==summary).forEach(n=>body.append(n));panel.append(header,body);details.append(panel);summary.hidden=true;details.classList.add('ci-source');details.open=false;
  button.setAttribute('aria-haspopup','dialog');button.setAttribute('aria-controls',panel.id);button.setAttribute('aria-expanded','false');wrapper.append(button,details);
  const item={details,button,panel,closeButton,wrapper,inline:false,modal:false,pinned:false};items.add(item);
  const leave=()=>{clearTimeout(item.enter);if(!item.pinned)item.leave=setTimeout(()=>{if(current===item&&!panel.matches(':hover')&&!button.matches(':hover')&&!panel.contains(document.activeElement))close();},250);};
  button.addEventListener('pointerenter',ev=>{if(ev.pointerType==='mouse'&&!touch()){clearTimeout(item.leave);item.enter=setTimeout(()=>{if(!current?.pinned||current===item)show(item);},300);}});
  button.addEventListener('pointerleave',leave);panel.addEventListener('pointerenter',()=>clearTimeout(item.leave));panel.addEventListener('pointerleave',leave);
  let hold,start,ignoreClickUntil=0;
  button.addEventListener('pointerdown',ev=>{if(ev.pointerType!=='touch')return;start={x:ev.clientX,y:ev.clientY};hold=setTimeout(()=>{ignoreClickUntil=Date.now()+900;show(item,true);},550);});
  button.addEventListener('pointermove',ev=>{if(start&&Math.hypot(ev.clientX-start.x,ev.clientY-start.y)>10)clearTimeout(hold);});
  for(const event of ['pointerup','pointercancel','pointerleave'])button.addEventListener(event,()=>clearTimeout(hold));
  button.addEventListener('contextmenu',ev=>{ev.preventDefault();});
  button.addEventListener('click',ev=>{ev.preventDefault();if(Date.now()<ignoreClickUntil)return;if(expanded){inline(item,!item.inline);return;}if(current===item&&item.pinned)close({focus:true});else show(item,true,ev.detail===0);});
  closeButton.addEventListener('click',()=>close({focus:true}));
  panel.addEventListener('cancel',ev=>{ev.preventDefault();close({focus:true});});
  panel.addEventListener('click',ev=>{if(ev.target===panel){const r=panel.getBoundingClientRect();if(ev.clientX<r.left||ev.clientX>r.right||ev.clientY<r.top||ev.clientY>r.bottom)close({focus:true});}});
  // Existing expand-all controls and browser find-in-page can open the native details.
  details.addEventListener('toggle',()=>{if(details.open&&current!==item&&!item.inline)inline(item,true);else if(!details.open&&item.inline)inline(item,false);});
  if(expanded)inline(item,true);
  return item;
 }
 function toggleAll(on){close();expanded=on;for(const item of items)if(item.button.isConnected)inline(item,on);document.querySelectorAll('[data-context-reading]').forEach(b=>{b.setAttribute('aria-pressed',String(on));b.textContent=on?'Hide explanations':'Show explanations';});}
 function toolbar(){
  const host=document.querySelector('.decision .contextline')||document.querySelector('.rf-selector');if(!host||host.querySelector('[data-context-reading]'))return;
  const button=document.createElement('button');button.type='button';button.className='ci-reading';button.dataset.contextReading='';button.setAttribute('aria-pressed',String(expanded));button.textContent=expanded?'Hide explanations':'Show explanations';button.addEventListener('click',()=>toggleAll(!expanded));host.append(button);
 }
 function enhancePage(){
  queued=false;
  for(const item of items)if(!item.button.isConnected){if(current===item)close();items.delete(item);}
  compactChrome();
  // Team attribution is contextual; all order-setting timing remains on the page.
  document.querySelectorAll('.contextline > span:nth-child(2)').forEach(n=>note(n,'Responsible team'));
  document.querySelectorAll('.assistant-footnote').forEach(n=>note(n,'How to use these choices'));
  document.querySelectorAll('.example-controls [data-example-description]').forEach(n=>note(n,'Using the example'));
  document.querySelectorAll('.stopnote').forEach(n=>note(n,'How to read these cautions'));
  document.querySelectorAll('.rf-evidence-controls > span').forEach(n=>note(n,'Using related decisions'));
  document.querySelectorAll('.rf-related > p').forEach(n=>note(n,'How these decisions connect'));
  const slug=location.pathname.split('/').filter(Boolean).pop(),step=document.querySelector('.permalink')?.getAttribute('href')?.slice(1);
  compactHeading(document.querySelector('.question-head h2'),copy.headings[slug+'/'+step]);
  document.querySelectorAll('.assistant-help:not([data-context-checked])').forEach(n=>{
   n.dataset.contextChecked='true';const q=n.closest('.assistant-question')?.querySelector('select')?.dataset.assistantQuestion;
   compactHelp(n,copy.help[slug+'/'+step+'/'+q]);
  });
  // Citation lists become contextual. Selected definition bullets and all next actions stay visible.
  document.querySelectorAll('.assistant-evidence,.stops .citations').forEach(n=>{if(n.children.length&&!n.closest('.ci-panel,.assistant-criteria,.branch-details'))note(n,evidenceLabel(n));});
  document.querySelectorAll('.branch-action > p').forEach(p=>{
   const sources=[...p.querySelectorAll(':scope > .cite')];if(!sources.length)return;
   const group=document.createElement('div');p.after(group);group.append(...sources);note(group,evidenceLabel(group));
  });
  document.querySelectorAll('.rf-criteria:not([data-context-copy])').forEach(n=>{
   n.dataset.contextCopy='true';const paragraphs=[...n.querySelectorAll(':scope > p')];if(!paragraphs.length)return;
   const group=document.createElement('div');paragraphs[0].before(group);group.append(...paragraphs);note(group,'Using these criteria');
  });
  compactRecommendations();
  // Next-step criteria are native inline disclosures. Warnings are immediate;
  // explanatory notes and citations alone use floating information panels.
  document.querySelectorAll('#answer details.more:not([data-disclosure-sorted])').forEach(d=>{
   d.dataset.disclosureSorted='true';
   const warning=d.querySelector('.optline.bad');if(warning)d.before(warning);
   const approval=d.querySelector('.callout.amber');if(approval)d.before(approval);
   const noteText=d.querySelector('.recnote');
   if(noteText){const holder=document.createElement('div');d.after(holder);holder.append(noteText);const info=note(holder,'Explanation and evidence');const refs=d.querySelector('.refchip')?.parentElement;if(refs)info.panel.querySelector('.ci-body').append(refs);}
   const criteria=d.querySelector('.optline,.orderrule');
   if(criteria){d.querySelector('summary').textContent=criteria.classList.contains('orderrule')?'How to choose among these options':'Selection criteria';}
   else if(d.querySelector('.refchip'))enhance(d);
   else d.remove();
  });
  document.querySelectorAll('.care-evidence').forEach(enhance);
  document.querySelectorAll('.gray').forEach(section=>{
   if(section.querySelector('.ci-discussions'))return;
   const links=[...section.querySelectorAll(':scope > .issue-link')];if(!links.length)return;
   const d=document.createElement('details');d.className='ci-discussions';const s=document.createElement('summary');s.textContent=`Discussion questions (${links.length})`;d.append(s,...links);section.append(d);
  });
  document.querySelectorAll('.assistant-selected').forEach(n=>n.classList.toggle('ci-long-selection',n.textContent.length>45));
  toolbar();
 }
 function revealEvidence(id){requestAnimationFrame(()=>requestAnimationFrame(()=>{const target=document.getElementById('ev-'+id);if(target){target.setAttribute('tabindex','-1');target.style.scrollMarginTop=((document.querySelector('.rf-selector')?.getBoundingClientRect().bottom||0)+16)+'px';target.scrollIntoView({block:'start',behavior:'instant'});target.focus({preventScroll:true});}}));}
 document.addEventListener('click',ev=>{const ref=ev.target.closest('.refchip');if(current&&ref&&current.panel.contains(ref)){const id=ref.dataset.ref,afterHistory=current.modal&&mobileHistory;if(afterHistory)pendingEvidence=id;close();if(!afterHistory)revealEvidence(id);}},true);
 document.addEventListener('click',ev=>{if(current&&!current.modal&&!current.panel.contains(ev.target)&&!current.button.contains(ev.target))close();});
 document.addEventListener('keydown',ev=>{if(ev.key==='Escape'&&current){ev.preventDefault();ev.stopImmediatePropagation();close({focus:true});}},true);
 document.addEventListener('focusin',ev=>{if(current&&!current.modal&&!current.panel.contains(ev.target)&&ev.target!==current.button&&!ev.target.closest('#source-dialog'))close();});
 window.addEventListener('resize',()=>{if(current)close();});
 window.addEventListener('scroll',()=>{if(current&&!current.modal)position(current);},true);
 function handleHistory(){if(ignoreBack){ignoreBack=false;if(pendingEvidence){const id=pendingEvidence;pendingEvidence=null;revealEvidence(id);}return true;}if(current?.modal&&mobileHistory){close({focus:true,fromBack:true});return true;}return false;}
 window.ContextualInfo={handleHistory,sourceOrigin(trigger){if(current?.panel.contains(trigger)){const origin=current.button;close();return origin;}return trigger;}};
 window.addEventListener('popstate',()=>{if(!document.getElementById('protocol-data'))handleHistory();});
 const beforePrint=()=>{if(printing)return;close();printing=true;printDetails=[...document.querySelectorAll('.full-tests,.ci-discussions,.assistant-criteria:not(.ci-source),.branch-details,.rf-criteria,#answer details.more:not(.ci-source)')].map(d=>[d,d.open]);printDetails.forEach(([d])=>d.open=true);for(const item of items)if(item.button.isConnected){item.beforePrint=item.inline;inline(item,true);}};
 const afterPrint=()=>{if(!printing)return;printing=false;printDetails.forEach(([d,open])=>d.open=open);printDetails=[];for(const item of items)if(item.button.isConnected)inline(item,!!item.beforePrint);};
 window.addEventListener('beforeprint',beforePrint);window.addEventListener('afterprint',afterPrint);
 const media=matchMedia('print');media.addEventListener('change',ev=>ev.matches?beforePrint():afterPrint());
 new MutationObserver(records=>{if(records.some(r=>r.type==='childList')&&!queued){queued=true;requestAnimationFrame(enhancePage);}}).observe(document.body,{childList:true,subtree:true});
 document.documentElement.classList.add('contextual-explanations');enhancePage();
})();
