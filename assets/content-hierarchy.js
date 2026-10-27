/* Presentation ownership: clinical decisions first; references belong to their decision. */
(()=>{
 'use strict';
 const root=new URL('../',document.currentScript.src),slug=location.pathname.slice(root.pathname.length).split('/')[0];
 const map=window.ContentHierarchyData?.references[slug];
 const make=(tag,cls,text)=>{const n=document.createElement(tag);if(cls)n.className=cls;if(text!==undefined)n.textContent=text;return n;};
 const plain=s=>String(s||'').replace(/\s+/g,' ').trim();
 let queued=false,stored=null,legend=null;
 function capture(){
  if(stored||!map)return;
  const strip=document.querySelector('#quickref,.tree>.refstrip');
  const nodes=strip?[...strip.querySelectorAll(':scope>details')]:[];
  // Fail visibly if source content changes; never silently lose an unmapped reference.
  if(nodes.length!==map.length||nodes.some((n,i)=>plain(n.querySelector('summary')?.textContent)!==plain(map[i].source)))return;
  stored=nodes.map((node,i)=>{
   const entry=map[i];node.classList.remove('more');node.classList.add('ch-reference');node.dataset.disclosureSorted='true';
   node.dataset.referenceSource=entry.source;node.dataset.referenceKind=entry.kind;node.querySelector('summary').textContent=entry.label;
   node.open=false;
   const ids=[...new Set((node.textContent.match(/\b\d{8}\b/g)||[]))];
   if(ids.length){const links=make('div','ch-reference-sources');for(const id of ids){const a=make('a','','PMID '+id);a.href='https://pubmed.ncbi.nlm.nih.gov/'+id+'/';a.target='_blank';a.rel='noopener';links.append(a);}node.append(links);}
   return {entry,node};
  });
  // An earlier revision added this explanation globally. Keep it with its definition.
  if(slug==='icca'){
   const card=strip.previousElementSibling;
   if(card?.matches('.card')&&card.querySelector('h3')?.textContent==='Describe multiple liver tumors clearly'){
    const nav=card.querySelector('p:last-child');if(nav?.textContent.startsWith('Open the first quick reference'))nav.remove();
    card.classList.add('ch-definition-note');stored[0].node.querySelector('.moreinner')?.prepend(card);
   }
  }
  strip.remove();
 }
 function group(host,cls,label){
  let g=host.querySelector(':scope>.'+cls);
  if(!g){g=make('section',cls);g.append(make('h4','ch-reference-heading',label));host.append(g);}return g;
 }
 function placeReferences(workspace){
  const grid=workspace.querySelector('.dw-grid');
  if(!stored||!grid||grid.dataset.hierarchyReferences)return;
  const decision=workspace.dataset.workspaceKey?.split('/')[1],right=workspace.querySelector('.dw-tools'),middle=workspace.querySelector('.dw-criteria');if(!decision||!right||!middle)return;
  grid.dataset.hierarchyReferences='true';workspace.dataset.hierarchyReferences=decision;
  const refs=stored.filter(x=>x.entry.decisions.includes(decision)),tools=right.querySelector('.dw-tool-list');
  for(const {entry,node} of refs){
   node.open=false;
   let target;
   if(entry.kind==='evidence')target=group(middle,'ch-study-references','Supporting studies');
   else if(entry.kind==='tool')target=group(tools,'dw-tool-calculators','Calculators & scores');
   else if(entry.kind==='guide')target=group(tools,'dw-tool-treatments','Treatment resources');
   else target=group(tools,'ch-decision-references','Decision references');
   target.append(node);
   if(entry.visibleCaution){
    const caution=make('aside','ch-procedure-caution');
    caution.append(make('strong','',entry.visibleCaution.title),make('p','',entry.visibleCaution.text));
    const button=make('button','','Open crisis precautions');button.type='button';
    button.addEventListener('click',()=>{document.getElementById('dw-tab-tools')?.click();node.open=true;node.scrollIntoView({block:'start',behavior:'instant'});node.querySelector('summary').focus({preventScroll:true});});
    caution.append(button);(middle.querySelector('.rf-cautions')||middle.querySelector('.rf-recommendations')).append(caution);
   }
  }
  for(const cls of ['dw-tool-calculators','ch-decision-references','dw-tool-treatments','dw-tool-documents']){const g=tools.querySelector('.'+cls);if(g)tools.append(g);}
  if(slug==='hcc'){
   // Use the original working calculator and full definitions, without duplicate shortcuts.
   for(const key of ['child','ecog','lr5']){
    const title=window.ClinicalReference?.terms[key]?.title;if(!title)continue;
    const d=[...right.querySelectorAll('.clinical-term')].find(n=>n.dataset.contextTitle===title);
    if(d)(d.closest('.ci-unit')||d).remove();
   }
   const empty=right.querySelector('.dw-tool-calculators');if(empty&&empty.children.length===1)empty.remove();
  }
  if(!legend)legend=document.querySelector('.rf-legend');
  if(legend)right.querySelector('.dw-tool-documents')?.append(legend);
  const controls=middle.querySelector('.rf-evidence-controls');if(controls)middle.append(controls);
 }
 function evidenceOnlyRecommendation(workspace){
  const grid=workspace.querySelector('.dw-grid');
  if(workspace.dataset.workspaceKey!=='icca/10'||!grid||grid.dataset.evidenceRoleReady)return;
  const source=window.ContextualCopy?.recommendations['icca/10/standard/2'];if(!source)return;
  const rec=[...workspace.querySelectorAll('.rf-standard>.rec')].find(n=>[...n.querySelectorAll('div,p')].some(x=>x.textContent===source.source||x.textContent===source.concise));
  if(!rec)return;grid.dataset.evidenceRoleReady='true';
  const middle=workspace.querySelector('.dw-criteria'),holder=group(middle,'ch-study-references','Supporting studies');
  const detail=make('details','ch-reference ch-study-interpretation');detail.append(make('summary','','Incidental iCCA at transplant: evidence and limits'));
  // Preserve the original recommendation and its citations, but identify its role as evidence.
  rec.querySelector('.recmeta .pill')?.remove();detail.append(rec);holder.append(detail);
  const caution=make('p','ch-evidence-caution','Incidental explant outcomes do not establish eligibility for transplantation of known iCCA.');
  workspace.querySelector('.rf-standard').append(caution);
  const controls=middle.querySelector('.rf-evidence-controls');if(controls)middle.append(controls);
 }
 function resourceActions(){
  // A matrix or source link helps a decision; it is not a competing clinical action.
  document.querySelectorAll('.next-actions').forEach(list=>{
   const resources=[...list.querySelectorAll(':scope>.next-action[data-flow-label]')].filter(n=>['Reference','Treatment matrix'].includes(n.querySelector('.flow-action-type')?.textContent));
   if(!resources.length)return;
   let section=list.querySelector(':scope>.ch-action-resources');
   if(!section){section=make('section','ch-action-resources');section.append(make('h5','','Supporting resources'));list.append(section);}
   resources.forEach(n=>{n.classList.add('ch-resource-action');section.append(n);});
  });
 }
 function secondarySections(){
  const nav=document.querySelector('.roadmap-streamlined header.top nav.sec');
  if(nav&&!nav.dataset.hierarchyRole){
   nav.dataset.hierarchyRole='page-navigation';
   const links=[...nav.querySelectorAll(':scope>a')],clinical=links.find(a=>a.getAttribute('href')==='#tree');
   if(clinical){clinical.textContent='Clinical decisions';
    const menu=make('details','ch-page-resources'),summary=make('summary','','References & documents'),items=make('div','ch-page-resources-list');menu.append(summary,items);
    for(const link of links){if(link===clinical)continue;const href=link.getAttribute('href');if(href==='#stage'||href==='../'){link.remove();continue;}items.append(link);}
    nav.append(menu);
    menu.addEventListener('click',ev=>{if(ev.target.closest('a'))menu.open=false;});
    document.addEventListener('click',ev=>{if(!menu.contains(ev.target))menu.open=false;});
    menu.addEventListener('keydown',ev=>{if(ev.key==='Escape'){menu.open=false;summary.focus();}});
   }
  }
  document.querySelectorAll('.roadmap-streamlined #lrt,.roadmap-streamlined #topics').forEach(section=>{
   if(section.dataset.hierarchyRole)return;section.dataset.hierarchyRole='treatment-reference';
   const h=section.querySelector(':scope>.sechead>h2');if(h){h.before(make('p','ch-section-role','Treatment reference'));}
  });
  if(slug==='hcc'){
   const entry=document.querySelector('#tree .entry');
   if(entry&&!entry.querySelector('[data-roadmap-topic]')){
    const link=make('a','ch-before-stage','Before staging: diagnosis and work-up →');link.href='#topics';link.dataset.roadmapTopic='dx';entry.append(link);
   }
  }
  document.querySelectorAll('.roadmap-streamlined #honest,.roadmap-streamlined #ops,.roadmap-streamlined #evidence').forEach(section=>{
   if(section.dataset.hierarchyRole)return;section.dataset.hierarchyRole='background';
   const h=section.querySelector(':scope>.sechead>h2');if(h){const sub=make('h3','ch-background-title',h.textContent);h.replaceWith(sub);}
  });
  // Subquestions and study interpretation are subordinate to the treatment they inform.
  document.querySelectorAll('#panel h3').forEach(h=>{
   if(!['Establishing clinically significant portal hypertension','Does CSPH bar resection? The randomised evidence cuts both ways'].includes(h.textContent))return;
   const n=make('h4','ch-treatment-detail-heading',h.textContent);h.replaceWith(n);
  });
 }
 function protocolSafety(){
  document.querySelectorAll('.decision.dw-ready').forEach(workspace=>{
   const middle=workspace.querySelector('.dw-criteria'),stops=workspace.querySelector('.safety-grid .stops'),result=middle?.querySelector('#decision-results');
   if(stops&&result){stops.classList.add('ch-current-safety');result.before(stops);}
  });
 }
 function scan(){queued=false;capture();document.querySelectorAll('#answer.dw-ready').forEach(n=>{placeReferences(n);evidenceOnlyRecommendation(n);});resourceActions();secondarySections();protocolSafety();}
 new MutationObserver(records=>{if(!queued&&records.some(r=>r.type==='childList')){queued=true;requestAnimationFrame(scan);}}).observe(document.body,{childList:true,subtree:true});scan();
})();
