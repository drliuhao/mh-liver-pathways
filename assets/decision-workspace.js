/* Three-column reading layout. Move original controls; never infer or change clinical findings. */
(()=>{
 'use strict';
 const data=window.DecisionWorkspaceData,ref=window.ClinicalReference;if(!data||!ref)return;
 const root=new URL('../',document.currentScript.src),slug=location.pathname.slice(root.pathname.length).split('/').filter(Boolean)[0];
 let protocol;try{protocol=JSON.parse(document.getElementById('protocol-data')?.textContent||'null');}catch{}
 if(!protocol?.pathway&&!document.getElementById('answer'))return;
 let queued=false,initialProtocolPositioned=false,selectedColumn='criteria';
 const phone=matchMedia('(max-width:760px)');
 const sections=[['inputs','Tests needed'],['criteria','Results & criteria'],['tools','Tools & resources']];
 const initialProtocolStep=protocol?.pathway?.steps.find(s=>'#'+s.id===location.hash)?.id;
 const make=(tag,cls,text)=>{const n=document.createElement(tag);if(cls)n.className=cls;if(text!==undefined)n.textContent=text;return n;};
 const plain=s=>String(s||'').replace(/\s+/g,' ').trim();
 const displayTeam=s=>s.split(' · ').map(x=>({
  'IR':'Interventional radiology','oncology':'Medical oncology','Oncology':'Medical oncology',
  'HPB surgery':'HPB surgery','transplant surgery':'Liver transplant surgery','Transplant surgery':'Liver transplant surgery',
  'transplant radiology':'Abdominal / transplant radiology','Transplant radiology':'Abdominal / transplant radiology',
  'radiology':'Abdominal radiology','Radiology':'Abdominal radiology','Advanced GI':'Advanced gastroenterology',
  'Medical/radiation oncology':'Medical oncology / Radiation oncology','HPB/transplant surgery':'HPB / Liver transplant surgery',
  'Transplant/HPB surgery':'Liver transplant / HPB surgery','Transplant MDT':'Transplant multidisciplinary team',
  'NET MDT':'NET multidisciplinary team','coordinator':'Transplant coordinator','Coordinator':'Transplant coordinator'
 }[x]||x.charAt(0).toUpperCase()+x.slice(1)));
 function column(cls,id,title,lead){
  const box=make('section','dw-column '+cls);box.id=id;box.setAttribute('aria-labelledby',id+'-title');
  const h=make('h3','dw-column-title',title);h.id=id+'-title';h.tabIndex=-1;box.append(h);
  if(lead)box.append(make('p','dw-column-lead',lead));return box;
 }
 function showColumn(value,focus=false){
  selectedColumn=value;
  const grid=document.querySelector('.decision.dw-ready .dw-grid,#answer.dw-ready .dw-grid');
  const nav=document.querySelector('.ct-strip>.dw-column-nav');if(!grid||!nav)return;
  nav.setAttribute('role',phone.matches?'tablist':'navigation');
  for(const [key] of sections){
   const button=nav.querySelector('[data-column="'+key+'"]'),panel=grid.querySelector('#dw-'+key);
   if(!button||!panel)continue;
   panel.hidden=phone.matches&&key!==value;
   button.classList.toggle('is-selected',key===value);
   button.setAttribute('role',phone.matches?'tab':'button');
   if(phone.matches){button.setAttribute('aria-selected',String(key===value));button.tabIndex=key===value?0:-1;panel.setAttribute('role','tabpanel');panel.setAttribute('aria-labelledby',button.id);}
   else{button.removeAttribute('aria-selected');button.removeAttribute('tabindex');panel.removeAttribute('role');panel.setAttribute('aria-labelledby',panel.id+'-title');}
  }
  if(focus){const panel=grid.querySelector('#dw-'+value);panel.scrollIntoView({block:'start',behavior:'instant'});panel.querySelector('h3').focus({preventScroll:true});}
 }
 function jumps(host,grid){
  const strip=document.querySelector('.ct-strip');if(!strip)return;
  let nav=strip.querySelector(':scope>.dw-column-nav');
  if(!nav){
   nav=make('nav','dw-column-nav');nav.setAttribute('aria-label','Decision sections');
   sections.forEach(([key,label])=>{const b=make('button','',label);b.type='button';b.id='dw-tab-'+key;b.dataset.column=key;b.setAttribute('aria-controls','dw-'+key);b.addEventListener('click',()=>showColumn(key,true));nav.append(b);});
   nav.addEventListener('keydown',ev=>{if(!phone.matches||!['ArrowLeft','ArrowRight','Home','End'].includes(ev.key))return;const buttons=[...nav.querySelectorAll('button')],n=buttons.indexOf(ev.target);if(n<0)return;ev.preventDefault();const i=ev.key==='Home'?0:ev.key==='End'?2:(n+(ev.key==='ArrowRight'?1:2))%3;showColumn(sections[i][0]);buttons[i].focus();});
   strip.append(nav);
  }
  showColumn(selectedColumn);
 }
 function toolsColumn(team,keys,text,isProtocol,evidenceAction=null){
  const right=column('dw-tools','dw-tools','Tools & resources');
  right.append(make('h4','dw-team-heading','Decision team'));
  const list=make('ul','dw-team-list');displayTeam(team).forEach(s=>list.append(make('li','',s)));right.append(list);
  right.append(make('h4','dw-tools-title','Calculators & references'));
  const group=make('div','dw-tool-list');
  const terms=[...new Set([...keys,...Object.keys(ref.terms).filter(k=>ref.terms[k].match.test(text)),...(/Class 5/.test(text)?['lr5']:[])])];
  if(terms.includes('meld')){const b=make('button','clinical-button dw-calculator','MELD 3.0 calculator');b.type='button';b.setAttribute('data-clinical-calculator','');group.append(b);}
  for(const key of terms){
   if(ref.terms[key]){
    const term=ref.terms[key],d=make('details','clinical-term');d.dataset.contextTitle=term.title;
    d.innerHTML='<summary>'+ref.esc({ecog:'ECOG scale',child:'Child-Pugh score',lr5:'LI-RADS / LR-5',meld:'MELD: what the score means'}[key])+'</summary>'+term.html;
    group.append(d);
   }else if(key==='lrt'||key==='systemic'){
    const a=make('a','clinical-button',key==='lrt'?'Liver-directed therapy matrix':'Systemic therapy matrix');a.href=new URL(key+'/',root);group.append(a);
   }
  }
  if(isProtocol){for(const [view,label] of [['meeting','Protocol & meeting documents'],['care','Treatment reference']]){const a=make('a','clinical-button',label);a.href='#'+view;a.dataset.view=view;group.append(a);}}
  const evidence=make(evidenceAction?'button':'a','clinical-button',evidenceAction?'Evidence & sources ↓':'Evidence library (all papers)');
  if(evidenceAction){evidence.type='button';evidence.addEventListener('click',evidenceAction);}else{evidence.href='#evidence';if(isProtocol)evidence.dataset.view='evidence';}group.append(evidence);
  right.append(group);
  return right;
 }
 function protocolLayout(decision){
  if(!protocol?.pathway||!decision.classList.contains('ct-workspace')||decision.classList.contains('dw-ready'))return;
  const id=decision.querySelector('.permalink')?.getAttribute('href')?.slice(1),step=protocol.pathway.steps.find(s=>s.id===id);
  const current=decision.querySelector('.layer-current'),orders=decision.querySelector('.orders'),result=decision.querySelector('#decision-results'),tests=orders?.querySelector('.full-tests');
  if(!step||!current||!orders||!result||!tests)return;
  decision.classList.add('dw-ready','dw-protocol');decision.dataset.workspaceKey=protocol.pathway.slug+'/'+id;
  const grid=decision.querySelector('.decision-grid');grid.classList.add('dw-grid');current.before(grid);
  const left=column('dw-inputs','dw-inputs','Tests needed');
  const config=protocol.assistants[protocol.pathway.slug+'/'+id];
  tests.open=true;left.append(tests);
  const middle=column('dw-criteria','dw-criteria','Results & criteria');middle.append(current,orders,result);
  if(protocol.pathway.slug==='hcc'&&['listing','waitlist'].includes(id)){const sub=make('nav','dw-wait-parts');sub.setAttribute('aria-label','Transplant waitlisted assessments');for(const [key,label] of [['listing','Before activation'],['waitlist','While waiting']]){const b=make('button','',label);b.type='button';b.dataset.dwBrowse='';b.dataset.step=key;if(key==='waitlist')b.setAttribute('aria-label','While waiting — reassess at each extension');if(key===id)b.setAttribute('aria-current','true');sub.append(b);}middle.querySelector('h3').after(sub);}
  const text=JSON.stringify([step,config]);
  const right=toolsColumn(step.owner,[],text,true);grid.append(left,middle,right);selectedColumn='criteria';jumps(decision,grid);
  const overview=document.querySelector('.journey-overview');
  if(overview){const controls=overview.querySelector('.example-controls');if(controls){const d=make('details','dw-session-controls');d.append(make('summary','','Example & clear choices'),controls);right.append(d);}overview.remove();}
  // Owner is now explicit above tools. Keep the timing and usage explanation above the grid.
  const owner=[...decision.querySelectorAll('.contextline>span,.contextline>.ci-unit')].find(n=>n.querySelector('b')?.textContent==='Responsible team'||n.querySelector('.ci-label')?.textContent==='Responsible team');if(owner)owner.remove();
  if(!initialProtocolPositioned&&initialProtocolStep===id){
   initialProtocolPositioned=true;
   requestAnimationFrame(()=>requestAnimationFrame(()=>{
    if(!decision.isConnected)return;
    const strip=document.querySelector('.dw-protocol-strip');if(strip)document.documentElement.style.setProperty('--pathway-nav-height',Math.ceil(strip.getBoundingClientRect().height)+'px');
    decision.scrollIntoView({block:'start',behavior:'instant'});
   }));
  }
 }
 function roadmapLayout(answer){
  if(answer.classList.contains('dw-ready')&&answer.querySelector('.dw-grid'))return;
  const ahead=answer.querySelector('.ahead'),criteria=ahead?.querySelector('.rf-criteria'),related=answer.querySelector('.rf-related');
  const meta=data.topics[slug+'/'+related?.dataset.relatedFor];if(!ahead||!criteria||!related||!meta)return;
  const actual=[...criteria.querySelectorAll(':scope>ul>li')].map(n=>plain(n.textContent));
  if(plain(ahead.querySelector('h3')?.textContent)!==plain(meta.title)||JSON.stringify(actual)!==JSON.stringify(meta.criteria.map(plain)))return;
  answer.classList.add('dw-ready','dw-roadmap');answer.dataset.workspaceKey=slug+'/'+related.dataset.relatedFor;
  ahead.prepend(make('p','dw-decision-kicker','Current decision'));
  const grid=make('div','dw-grid'),left=column('dw-inputs','dw-inputs','Tests needed');
  const inputs=make('ul','dw-input-list');meta.inputs.forEach(s=>inputs.append(make('li','',s)));left.append(inputs);
  const middle=column('dw-criteria','dw-criteria','Results & criteria');
  const recommendations=answer.querySelector('.rf-recommendations'),controls=answer.querySelector('.rf-evidence-controls');
  const recommendationHeading=recommendations.querySelector(':scope>.flow-section-heading');
  if(recommendationHeading)recommendationHeading.textContent='Recommendations within this decision';
  middle.append(criteria,related,recommendations,controls);
  const right=toolsColumn(meta.team,meta.tools,meta.criteria.join(' '),false);grid.append(left,middle,right);ahead.after(grid);selectedColumn='criteria';jumps(answer,grid);
 }
 function roadmapNavigation(){
  if(protocol?.pathway||!window.CompactTrailLabels)return;
  const strip=document.querySelector('.rf-selector .ct-strip'),buttons=document.getElementById('stageBtns');if(!strip||!buttons)return;
  let nav=strip.querySelector('.dw-major-decisions');
  if(!nav){
   const old=buttons.closest('.rf-overview');if(!old)return;
   nav=make('section','dw-major-decisions');nav.setAttribute('aria-labelledby','dw-major-title');
   const disease={hcc:'HCC',crlm:'CRLM',icca:'iCCA',hilar:'pCCA',nelm:'NELM',chcca:'cHCC–CCA',adenoma:'Hepatic adenoma',incidental:'Incidental liver lesions',pdac:'PDAC',pnet:'pNET',pcyst:'Pancreatic cysts',ampullary:'Ampullary cancer'}[slug]||slug.toUpperCase();
   const heading=make('div','dw-major-heading'),title=make('h2','',disease+' · Major decisions');title.id='dw-major-title';
   heading.append(title);nav.append(heading,buttons);
   old.remove();strip.prepend(nav);strip.classList.add('dw-major-strip');
   buttons.setAttribute('aria-label','Major clinical decisions');buttons.setAttribute('role','group');
   if(window.ResizeObserver)new ResizeObserver(()=>revealMajorDecision(buttons)).observe(buttons);
   if(location.hash.startsWith('#decision-'))requestAnimationFrame(()=>{
    document.documentElement.style.setProperty('--roadmap-trail-height',Math.ceil(strip.getBoundingClientRect().height)+'px');
    document.getElementById('answer')?.scrollIntoView({block:'start',behavior:'instant'});
   });
  }
  for(const b of buttons.querySelectorAll('.rf-topic')){
   if(b.dataset.majorReady)continue;
   const key=slug+'/'+b.dataset.roadmapDecision,meta=data.topics[key];if(!meta||plain(b.textContent)!==plain(meta.title))continue;
   const full=meta.title.replace(/^\d+\s*·\s*/,''),short=window.CompactTrailLabels.roadmaps[key];
   const label=short?.source===full?short.label:full;
   b.title=meta.title;b.setAttribute('aria-label','View '+meta.title);
   b.replaceChildren(make('span','dw-major-number',b.dataset.roadmapDecision),make('span','dw-major-label',label));b.dataset.majorReady='true';
  }
  const active=buttons.querySelector('[data-viewed]')||buttons.querySelector('[aria-current="true"],[aria-current="step"]');
  if(active&&nav.dataset.active!==active.dataset.roadmapDecision){
   nav.dataset.active=active.dataset.roadmapDecision;
   requestAnimationFrame(()=>revealMajorDecision(buttons));
  }
 }
 function protocolNavigation(){
  if(!protocol?.pathway)return;
  const strip=document.querySelector('.pathway-nav .ct-strip');if(!strip)return;
  let nav=strip.querySelector('.dw-protocol-nav');
  if(!nav){
   nav=make('section','dw-major-decisions dw-protocol-nav');nav.setAttribute('aria-labelledby','dw-protocol-nav-title');
   const heading=make('div','dw-major-heading'),title=make('h2','',protocol.pathway.code+' · Major decisions');title.id='dw-protocol-nav-title';
   heading.append(title);
   const choices=make('div','dw-protocol-decisions');choices.setAttribute('role','group');choices.setAttribute('aria-label','View pathway decisions');
   protocol.pathway.steps.forEach((step,i)=>{
    if(protocol.pathway.slug==='hcc'&&step.id==='waitlist')return;
    const short=data.protocolNavigation?.[protocol.pathway.slug+'/'+step.id],label=short?.source===step.title?short.label:step.title;
    const waitStep={hcc:'listing',pcca:'listing',icca:'review',crlm:'review',nelm:'review',hehe:'review',hca:'review'}[protocol.pathway.slug];
    const b=make('button','dw-protocol-topic',step.id===waitStep?'Transplant waitlisted':label);b.type='button';b.dataset.dwBrowse='';b.dataset.step=step.id;b.title=step.id===waitStep?'Listing and waiting':step.title;
    b.dataset.baseLabel=step.id===waitStep?'Transplant waitlisted: before activation and reassessment while waiting':step.title;b.setAttribute('aria-label','View '+b.dataset.baseLabel);choices.append(b);
   });
   nav.append(heading,choices);strip.prepend(nav);strip.classList.add('dw-protocol-strip');
   const menu=strip.querySelector('.ct-menu>summary');if(menu){menu.textContent='Findings';menu.setAttribute('aria-label','Recorded findings menu');}
   if(window.ResizeObserver)new ResizeObserver(()=>revealMajorDecision(choices)).observe(choices);
  }
  const id=document.querySelector('.decision .permalink')?.getAttribute('href')?.slice(1)||'';
  const actual=document.body.dataset.currentAssessment||id,signature=id+'/'+actual;
  if(nav.dataset.current!==signature){
   nav.dataset.current=signature;
   for(const b of nav.querySelectorAll('.dw-protocol-topic')){const viewed=b.dataset.step===id||(id==='waitlist'&&b.dataset.step==='listing'),current=b.dataset.step===actual||(actual==='waitlist'&&b.dataset.step==='listing');b.toggleAttribute('data-viewed',viewed);b.setAttribute('aria-pressed',String(viewed));if(current)b.setAttribute('aria-current','step');else b.removeAttribute('aria-current');b.toggleAttribute('data-current-assessment',current&&actual!==id);b.setAttribute('aria-label','View '+b.dataset.baseLabel+(current?' (current assessment)':'')+(viewed&&actual!==id?' (viewing)':''));}
   requestAnimationFrame(()=>revealMajorDecision(nav.querySelector('.dw-protocol-decisions')));
  }
 }
 function compactNavigation(){
  const strip=document.querySelector('.ct-strip');if(!strip)return;
  strip.classList.add('dw-two-row');
  if(protocol?.pathway){
   let record=document.querySelector('.dw-recorded');
   if(!record){record=make('details','dw-recorded');record.append(make('summary','','Recorded findings'));strip.after(record);}
   for(const n of [...strip.children])if(n.matches('.layer-heading,.layer-history,.ct-scroll-button'))record.append(n);
   const middle=document.querySelector('.decision.dw-ready .dw-criteria');if(middle&&!middle.contains(record))middle.querySelector('h3').after(record);
   const right=document.querySelector('.decision.dw-ready .dw-tools'),tools=strip.querySelector('.clinical-strip-tools');
   if(right&&tools)right.append(tools);
   record.querySelector('.layer-heading')?.remove();
   const count=record.querySelectorAll('button.ct-chip:not(.ct-next)').length,summary=record.querySelector(':scope>summary'),label='Recorded findings'+(count?' · '+count:'');if(summary.textContent!==label)summary.textContent=label;record.hidden=count===0;
  }else{
   const tools=strip.querySelector('.clinical-strip-tools');if(tools)document.querySelector('#answer .dw-tools')?.append(tools);
  }
 }
 function revealMajorDecision(buttons){
  const active=buttons.querySelector('[data-viewed]')||buttons.querySelector('[aria-current="true"],[aria-current="step"]');if(!active||buttons.scrollWidth<=buttons.clientWidth)return;
  const parent=buttons.getBoundingClientRect(),child=active.getBoundingClientRect();
  if(child.left<parent.left-1||child.right>parent.right+1)buttons.scrollLeft+=child.left-parent.left;
 }
 function allocationPlacement(decision){
  const right=decision.querySelector('.dw-tools'),card=decision.querySelector('.allocation-overview');if(!right||!card||right.contains(card))return;
  right.append(card);card.querySelector('[data-clinical-calculator]')?.remove();
 }
 function supplementalInputs(decision){
  if(!decision.classList.contains('dw-ready'))return;
  const labels=[...decision.querySelectorAll('#risk-question-panel .risk-question')].map(n=>{
   const source=plain(n.querySelector('label')?.textContent),id=n.querySelector('[data-risk-question]')?.dataset.riskQuestion,short=window.CompactTrailLabels?.riskById[id];
   return short?.source===source?short.label:source;
  }).filter(Boolean);
  let box=decision.querySelector('.dw-additional-findings');
  if(!labels.length){box?.remove();return;}
  const signature=JSON.stringify(labels);if(box?.dataset.signature===signature)return;
  if(!box){box=make('div','dw-required dw-additional-findings');decision.querySelector('.dw-inputs .full-tests').before(box);}
  const list=make('ul','dw-input-list');labels.forEach(s=>list.append(make('li','',s)));box.replaceChildren(make('h4','','Additional checks when relevant'),list);box.dataset.signature=signature;
 }
 function previewLayout(content){
  if(!protocol?.pathway||(content.classList.contains('dw-preview')&&content.querySelector('.dw-grid')))return;
  const step=protocol.pathway.steps.find(s=>s.title===content.querySelector('h3')?.textContent),checklist=content.querySelector('.clinical-preview-checklist'),sources=content.querySelector('.clinical-preview-sources');
  if(!step||!checklist||!sources)return;
  const key=protocol.pathway.slug+'/'+step.id,config=protocol.assistants[key],grid=make('div','dw-grid');
  content.classList.add('dw-ready','dw-preview');content.dataset.workspaceKey=key;
  const allocation=content.querySelector(':scope>.allocation-overview');
  const sections=[...content.querySelectorAll(':scope>section')].filter(n=>n!==checklist&&n!==sources&&n!==allocation);
  const left=column('dw-inputs','preview-dw-inputs','Tests needed'),middle=column('dw-criteria','preview-dw-criteria','Results & criteria');
  left.append(checklist);middle.append(...sections);
  const right=toolsColumn(step.owner,[],JSON.stringify([step,config]),false,()=>{sources.scrollIntoView({block:'start',behavior:'instant'});const h=sources.querySelector('h4');h.tabIndex=-1;h.focus({preventScroll:true});});right.id='preview-dw-tools';right.setAttribute('aria-labelledby','preview-dw-tools-title');right.querySelector('h3').id='preview-dw-tools-title';
  grid.append(left,middle,right);sources.before(grid);
  if(allocation)right.append(allocation);
 }
 function scan(){queued=false;
  protocolNavigation();
  document.querySelectorAll('.decision.ct-workspace').forEach(n=>{protocolLayout(n);allocationPlacement(n);supplementalInputs(n);});
  const answer=document.getElementById('answer');if(answer){roadmapNavigation();roadmapLayout(answer);}
  compactNavigation();
  const ready=document.querySelector('.decision.dw-ready,#answer.dw-ready');if(ready)jumps(ready,ready.querySelector('.dw-grid'));
  document.querySelectorAll('.clinical-preview-content').forEach(previewLayout);
 }
 phone.addEventListener('change',()=>showColumn(selectedColumn));
 new MutationObserver(records=>{if(!queued&&records.some(r=>r.type==='childList')){queued=true;requestAnimationFrame(scan);}}).observe(document.body,{childList:true,subtree:true});scan();
})();
