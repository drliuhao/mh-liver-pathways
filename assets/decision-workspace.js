/* Three-column reading layout. Move original controls; never infer or change clinical findings. */
(()=>{
 'use strict';
 const data=window.DecisionWorkspaceData,ref=window.ClinicalReference;if(!data||!ref)return;
 const root=new URL('../',document.currentScript.src),slug=location.pathname.slice(root.pathname.length).split('/').filter(Boolean)[0];
 let protocol;try{protocol=JSON.parse(document.getElementById('protocol-data')?.textContent||'null');}catch{}
 if(!protocol?.pathway&&!document.getElementById('answer'))return;
 let queued=false;
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
 function jumps(host,grid){
  const nav=make('nav','dw-column-nav');nav.setAttribute('aria-label','Decision sections');
  [['dw-inputs','Tests & data'],['dw-criteria','Criteria & options'],['dw-tools','Team & tools']].forEach(([id,label])=>{
   const b=make('button','',label);b.type='button';b.addEventListener('click',()=>{const target=grid.querySelector('#'+id);target.scrollIntoView({block:'start',behavior:'instant'});target.querySelector('h3').focus({preventScroll:true});});nav.append(b);
  });host.insertBefore(nav,grid);
 }
 function toolsColumn(team,keys,text,isProtocol,evidenceAction=null){
  const right=column('dw-tools','dw-tools','Decision team');
  const list=make('ul','dw-team-list');displayTeam(team).forEach(s=>list.append(make('li','',s)));right.append(list);
  right.append(make('h4','dw-tools-title','Tools & references'));
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
  const evidence=make(evidenceAction?'button':'a','clinical-button',evidenceAction?'Evidence & sources ↓':'Evidence library');
  if(evidenceAction){evidence.type='button';evidence.addEventListener('click',evidenceAction);}else{evidence.href='#evidence';if(isProtocol)evidence.dataset.view='evidence';}group.append(evidence);
  right.append(group);
  return right;
 }
 function requiredFindings(config,key){
  const box=make('div','dw-required'),h=make('h4','','Required findings'),list=make('ul','dw-input-list');
  for(const q of config.questions){const short=window.CompactTrailLabels?.core[key+'/'+q.id];list.append(make('li','',short?.source===q.label?short.label:q.label));}
  box.append(h,list);return box;
 }
 function protocolLayout(decision){
  if(!protocol?.pathway||!decision.classList.contains('ct-workspace')||decision.classList.contains('dw-ready'))return;
  const id=decision.querySelector('.permalink')?.getAttribute('href')?.slice(1),step=protocol.pathway.steps.find(s=>s.id===id);
  const current=decision.querySelector('.layer-current'),orders=decision.querySelector('.orders'),result=decision.querySelector('#decision-results'),tests=orders?.querySelector('.full-tests');
  if(!step||!current||!orders||!result||!tests)return;
  decision.classList.add('dw-ready','dw-protocol');decision.dataset.workspaceKey=protocol.pathway.slug+'/'+id;
  const grid=decision.querySelector('.decision-grid');grid.classList.add('dw-grid');current.before(grid);
  const left=column('dw-inputs','dw-inputs','Tests & data','Have these results available.');
  const config=protocol.assistants[protocol.pathway.slug+'/'+id];
  tests.open=true;left.append(requiredFindings(config,protocol.pathway.slug+'/'+id),tests);
  const middle=column('dw-criteria','dw-criteria','Criteria & next options');middle.append(current,orders,result);
  const text=JSON.stringify([step,config]);
  const right=toolsColumn(step.owner,[],text,true);grid.append(left,middle,right);jumps(decision,grid);
  // Owner is now explicit above tools. Keep the timing and usage explanation above the grid.
  const owner=[...decision.querySelectorAll('.contextline>span,.contextline>.ci-unit')].find(n=>n.querySelector('b')?.textContent==='Responsible team'||n.querySelector('.ci-label')?.textContent==='Responsible team');if(owner)owner.remove();
 }
 function roadmapLayout(answer){
  if(answer.classList.contains('dw-ready')&&answer.querySelector('.dw-grid'))return;
  const ahead=answer.querySelector('.ahead'),criteria=ahead?.querySelector('.rf-criteria'),related=answer.querySelector('.rf-related');
  const meta=data.topics[slug+'/'+related?.dataset.relatedFor];if(!ahead||!criteria||!related||!meta)return;
  const actual=[...criteria.querySelectorAll(':scope>ul>li')].map(n=>plain(n.textContent));
  if(plain(ahead.querySelector('h3')?.textContent)!==plain(meta.title)||JSON.stringify(actual)!==JSON.stringify(meta.criteria.map(plain)))return;
  answer.classList.add('dw-ready','dw-roadmap');answer.dataset.workspaceKey=slug+'/'+related.dataset.relatedFor;
  ahead.prepend(make('p','dw-decision-kicker','Current decision'));
  const grid=make('div','dw-grid'),left=column('dw-inputs','dw-inputs','Tests & data','Information to review for this topic.');
  const inputs=make('ul','dw-input-list');meta.inputs.forEach(s=>inputs.append(make('li','',s)));left.append(inputs);
  const middle=column('dw-criteria','dw-criteria','Criteria & next options');
  const recommendations=answer.querySelector('.rf-recommendations'),controls=answer.querySelector('.rf-evidence-controls');
  const recommendationHeading=recommendations.querySelector(':scope>.flow-section-heading');
  if(recommendationHeading)recommendationHeading.textContent='Recommendations within this decision';
  middle.append(criteria,related,recommendations,controls);
  const right=toolsColumn(meta.team,meta.tools,meta.criteria.join(' '),false);grid.append(left,middle,right);ahead.after(grid);jumps(answer,grid);
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
   heading.append(title,make('p','','Choose a clinical question.'));nav.append(heading,buttons);
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
   b.title=meta.title;b.setAttribute('aria-label','Review '+meta.title);
   b.replaceChildren(make('span','dw-major-number',b.dataset.roadmapDecision),make('span','dw-major-label',label));b.dataset.majorReady='true';
  }
  const active=buttons.querySelector('[aria-current="true"]');
  if(active&&nav.dataset.active!==active.dataset.roadmapDecision){
   nav.dataset.active=active.dataset.roadmapDecision;
   requestAnimationFrame(()=>revealMajorDecision(buttons));
  }
 }
 function revealMajorDecision(buttons){
  const active=buttons.querySelector('[aria-current="true"]');if(!active||buttons.scrollWidth<=buttons.clientWidth)return;
  const parent=buttons.getBoundingClientRect(),child=active.getBoundingClientRect();
  if(child.left<parent.left-1||child.right>parent.right+1)buttons.scrollLeft+=child.left-parent.left;
 }
 function allocationPlacement(decision){
  const right=decision.querySelector('.dw-tools'),card=decision.querySelector('.allocation-overview');if(!right||!card||right.contains(card))return;
  // Keep the required pre-follow-up allocation overview visible, beside the decision.
  right.append(card);
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
  const left=column('dw-inputs','preview-dw-inputs','Tests & data'),middle=column('dw-criteria','preview-dw-criteria','Criteria & next options');
  left.append(requiredFindings(config,key),checklist);middle.append(...sections);
  const right=toolsColumn(step.owner,[],JSON.stringify([step,config]),false,()=>{sources.scrollIntoView({block:'start',behavior:'instant'});const h=sources.querySelector('h4');h.tabIndex=-1;h.focus({preventScroll:true});});right.id='preview-dw-tools';right.setAttribute('aria-labelledby','preview-dw-tools-title');right.querySelector('h3').id='preview-dw-tools-title';
  grid.append(left,middle,right);sources.before(grid);
  if(allocation)right.append(allocation);
 }
 function scan(){queued=false;
  document.querySelectorAll('.decision.ct-workspace').forEach(n=>{protocolLayout(n);allocationPlacement(n);supplementalInputs(n);});
  const answer=document.getElementById('answer');if(answer){roadmapNavigation();roadmapLayout(answer);}
  document.querySelectorAll('.clinical-preview-content').forEach(previewLayout);
 }
 new MutationObserver(records=>{if(!queued&&records.some(r=>r.type==='childList')){queued=true;requestAnimationFrame(scan);}}).observe(document.body,{childList:true,subtree:true});scan();
})();
