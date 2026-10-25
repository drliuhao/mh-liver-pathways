/* Presentation only: source text and clinical decision state are never rewritten. */
(() => {
 'use strict';
 const supported=typeof HTMLElement.prototype.showPopover==='function';
 if(!supported||(!document.getElementById('protocol-data')&&!document.getElementById('answer')))return; // Native details remain usable in older browsers.
 let printDetails=[],pendingEvidence=null;
 let counter=0,current=null,expanded=false,queued=false,printing=false,scrollLock='',mobileHistory=false,ignoreBack=false;
 const items=new Set(),touch=()=>matchMedia('(max-width:760px)').matches;
 const criticalHelp={
  // Exact, individually reviewed explanatory suffixes; the clinical prefix stays visible.
  'hcc/listing/exception':'Adults retain calculated MELD initially and at first extension; later eligible extensions use MMaT−3.',
  'hcc/after-transplant/plan':'Surveillance intervals are individualized.',
  'icca/review/reviews':'Record the transplant team\'s decision on clinical suitability separately from the decision on MELD-exception points. The highlighted text does not approve either decision.',
  'crlm/review/reviews':'Record the transplant team\'s decision on clinical suitability separately from the decision on MELD-exception points. The highlighted text does not approve either decision.',
  'nelm/review/reviews':'Record the transplant team\'s decision on clinical suitability separately from the decision on MELD-exception points. The highlighted text does not approve either decision.',
  'hehe/review/reviews':'Record the transplant team\'s decision on clinical suitability separately from the decision on MELD-exception points. The highlighted text does not approve either decision.',
  'hca/review/reviews':'Record the transplant team\'s decision on clinical suitability separately from the decision on MELD-exception points. The highlighted text does not approve either decision.',
  'hehe/risk/benefit':'Some prognostic features are known only on explant.'
 };
 function note(node,label){
  if(!node||node.closest('.ci-unit,.ci-prose,.ci-panel'))return;
  const d=document.createElement('details');d.className='ci-prose';
  const s=document.createElement('summary');s.textContent=label;d.append(s);node.before(d);d.append(node);enhance(d);
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
   item.modal=true;item.panel.removeAttribute('popover');item.panel.classList.add('ci-sheet');scrollLock=document.body.style.overflow;document.body.style.overflow='hidden';const host=document.createElement('dialog');host.className='ci-modal-shell';host.setAttribute('aria-labelledby',item.panel.id+'-title');item.modalHost=host;host.append(item.panel);document.body.append(host);host.addEventListener('cancel',ev=>{ev.preventDefault();close({focus:true});});host.addEventListener('click',ev=>{if(ev.target===host)close({focus:true});});host.showModal();
   history.pushState({...history.state,contextualExplanation:true},'',location.href);mobileHistory=true;
  }else{item.panel.setAttribute('popover','manual');item.panel.showPopover();position(item);if(keyboard)item.closeButton.focus();}
 }
 function inline(item,on){
  resetPanel(item);item.inline=on;item.details.classList.toggle('ci-inline',on);item.details.open=on;
  item.button.setAttribute('aria-expanded',String(on));item.panel.removeAttribute('popover');item.panel.setAttribute('role','region');item.panel.classList.toggle('ci-inline-panel',on);
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
  const title=document.createElement('strong');title.id=panel.id+'-title';title.textContent=label;
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
 }
 function toggleAll(on){close();expanded=on;for(const item of items)if(item.button.isConnected)inline(item,on);document.querySelectorAll('[data-context-reading]').forEach(b=>{b.setAttribute('aria-pressed',String(on));b.textContent=on?'Hide explanations':'Show explanations';});}
 function toolbar(){
  const host=document.querySelector('.decision .contextline')||document.querySelector('.rf-selector');if(!host||host.querySelector('[data-context-reading]'))return;
  const button=document.createElement('button');button.type='button';button.className='ci-reading';button.dataset.contextReading='';button.setAttribute('aria-pressed',String(expanded));button.textContent=expanded?'Hide explanations':'Show explanations';button.addEventListener('click',()=>toggleAll(!expanded));host.append(button);
 }
 function enhancePage(){
  queued=false;
  for(const item of items)if(!item.button.isConnected){if(current===item)close();items.delete(item);}
  // Team attribution is contextual; all order-setting timing remains on the page.
  document.querySelectorAll('.contextline > span:nth-child(2)').forEach(n=>note(n,'Responsible team'));
  document.querySelectorAll('.assistant-footnote').forEach(n=>note(n,'How to use these choices'));
  document.querySelectorAll('.example-controls [data-example-description]').forEach(n=>note(n,'Using the example'));
  document.querySelectorAll('.stopnote').forEach(n=>note(n,'How to read these cautions'));
  document.querySelectorAll('.rf-evidence-controls > span').forEach(n=>note(n,'Using related decisions'));
  document.querySelectorAll('.rf-related > p').forEach(n=>note(n,'How these decisions connect'));
  const slug=location.pathname.split('/').filter(Boolean).pop(),step=document.querySelector('.permalink')?.getAttribute('href')?.slice(1);
  document.querySelectorAll('.assistant-help:not([data-context-checked])').forEach(n=>{
   n.dataset.contextChecked='true';const q=n.closest('.assistant-question')?.querySelector('select')?.dataset.assistantQuestion;
   const suffix=criticalHelp[slug+'/'+step+'/'+q];if(!suffix||!n.textContent.endsWith(suffix))return;
   const prefix=n.textContent.slice(0,-suffix.length).trim(),copy=document.createElement('p');copy.textContent=suffix;
   if(prefix){n.textContent=prefix;n.after(copy);note(copy,q==='exception'?'How exception points are assigned':q==='reviews'?'Selection and allocation review':q==='plan'?'Surveillance planning':'Information available before transplant');}
   else note(n,q==='reviews'?'Selection and allocation review':'Additional context');
  });
  // Keep selected quantitative/clinical definitions inline. Other reference definitions are contextual.
  document.querySelectorAll('.assistant-criteria:not([data-context-ready])').forEach(d=>{if(!d.open)enhance(d);});
  document.querySelectorAll('.branch-details, #answer details.more').forEach(enhance);
  document.querySelectorAll('.gray').forEach(section=>{
   if(section.querySelector('.ci-discussions'))return;
   const links=[...section.querySelectorAll(':scope > .issue-link')];if(!links.length)return;
   const d=document.createElement('details');d.className='ci-discussions';const s=document.createElement('summary');s.textContent=`Open discussion questions (${links.length})`;d.append(s,...links);section.append(d);
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
 const beforePrint=()=>{if(printing)return;close();printing=true;printDetails=[...document.querySelectorAll('.full-tests,.ci-discussions,.assistant-criteria:not(.ci-source)')].map(d=>[d,d.open]);printDetails.forEach(([d])=>d.open=true);for(const item of items)if(item.button.isConnected){item.beforePrint=item.inline;inline(item,true);}};
 const afterPrint=()=>{if(!printing)return;printing=false;printDetails.forEach(([d,open])=>d.open=open);printDetails=[];for(const item of items)if(item.button.isConnected)inline(item,!!item.beforePrint);};
 window.addEventListener('beforeprint',beforePrint);window.addEventListener('afterprint',afterPrint);
 const media=matchMedia('print');media.addEventListener('change',ev=>ev.matches?beforePrint():afterPrint());
 new MutationObserver(records=>{if(records.some(r=>r.type==='childList')&&!queued){queued=true;requestAnimationFrame(enhancePage);}}).observe(document.body,{childList:true,subtree:true});
 document.documentElement.classList.add('contextual-explanations');enhancePage();
})();
