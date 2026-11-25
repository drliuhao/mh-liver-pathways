/* Read-only outcome context; never records findings, scores patients or chooses treatment. */
(()=>{'use strict';
 const data=window.DecisionEvidenceData;if(!data)return;
 const root=new URL('../',document.currentScript.src),make=(tag,cls,text)=>{const n=document.createElement(tag);if(cls)n.className=cls;if(text!==undefined)n.textContent=text;return n;};
 let queued=false;
 const sourceLink=(url,text)=>{const a=make('a','',text);a.href=new URL(url,root);a.target='_blank';a.rel='noopener';return a;};
 function renderCard(id,host){
  const c=data.cards[id],s=data.sources[c.source];host.replaceChildren();host.dataset.evidenceCard=id;
  host.append(make('h4','oe-title',c.title),make('p','oe-population',c.population+' · n='+c.n),make('p','oe-context',c.context));
  const table=make('table','oe-table'),caption=make('caption','',c.endpoint+' · '+c.horizon+' · from '+c.origin);table.append(caption);
  const head=make('thead'),hr=make('tr');['Group / finding',c.horizon==='cohort frequency'?'Frequency':'Outcome'].forEach(x=>{const th=make('th','',x);th.scope='col';hr.append(th);});head.append(hr);table.append(head);
  const body=make('tbody');c.rows.forEach(r=>{const tr=make('tr'),label=make('th','',r.label);label.scope='row';tr.append(label,make('td','',r.value));body.append(tr);});table.append(body);host.append(table,make('p','oe-caution',c.caution));
  if(c.definitions.length){const defs=make('details','oe-definitions');defs.append(make('summary','','Definitions'));const list=make('ul');c.definitions.forEach(x=>list.append(make('li','',x)));defs.append(list);defs.dataset.contextTitle=c.title+' · definitions';host.append(defs);const info=window.ContextualInfo?.reference?.(defs);if(info)info.button.setAttribute('aria-label','Definitions: '+c.title);}
  const details=make('details','oe-source');details.append(make('summary','','Study details & source'));details.append(make('p','',c.uncertainty),make('p','',s.locator));
  const citation=make('p','oe-citation',`${s.author} · ${s.journal} · ${s.year}`);details.append(citation);
  const links=make('p','oe-links');if(s.pmid)links.append(sourceLink('https://pubmed.ncbi.nlm.nih.gov/'+s.pmid+'/','PMID '+s.pmid));
  if(s.doi){links.append(sourceLink('https://doi.org/'+s.doi,'DOI: '+s.doi),sourceLink('https://thslc-houston.primo.exlibrisgroup.com/discovery/search?vid=01TEXASHEALTH_HOUSTON%3ATMC_INST&query=any,contains,'+encodeURIComponent(s.doi)+'&lang=en','TMC Library'));}
  if(!s.pmid||!s.url.startsWith('https://pubmed.ncbi.nlm.nih.gov/'))links.append(sourceLink(s.url,s.pmid?'Full text':'Curves, policy & methods'));
  for(const extra of s.related||[])links.append(sourceLink(extra.url,extra.label));
  details.append(links);host.append(details);
 }
 function enhance(workspace){
  const key=workspace.dataset.workspaceKey;if(!key||workspace.classList.contains('dw-preview'))return;
  const protocol=workspace.classList.contains('dw-protocol'),slug=key.split('/')[0],fullKey=(protocol?'transplant/':'roadmap/')+key;
  const preferred=data.placements[fullKey]||[],all=[...new Set([...preferred,...(data.libraries[slug]||[])])];
  if(!all.length)return;
  const middle=workspace.querySelector('.dw-criteria'),right=workspace.querySelector('.dw-tools');if(!middle||!right)return;
  const host=preferred.length?middle:right;
  let box=host.querySelector('.outcome-evidence');
  if(!box){
   box=make('details','outcome-evidence');box.id='outcome-evidence';
   const summary=make('summary','',preferred.length?'Outcome evidence for this decision':'Outcome evidence library');box.append(summary);
   // The table is evidence context, separate from recorded findings and next-step rules.
   box.append(make('p','oe-note','Study populations, not an individual prediction.'));
   const label=make('label','oe-label','Evidence topic'),select=make('select');select.id='outcome-topic';label.htmlFor=select.id;
   all.forEach(id=>{const option=make('option','',data.cards[id].title);option.value=id;select.append(option);});
   const content=make('article','oe-card');box.append(label,select,content);select.addEventListener('change',()=>renderCard(select.value,content));renderCard(select.value,content);
   if(!preferred.length){right.querySelector('.dw-tool-documents')?.append(box);}
   else if(protocol){const alternatives=middle.querySelector('.other-results');if(alternatives)alternatives.after(box);else middle.append(box);}
   else middle.querySelector('.rf-related')?.after(box);
   const wait=preferred[0]?.startsWith('houston-'),recorded=!!workspace.querySelector('select[data-committed]:not([data-committed=""])');
   box.open=!!preferred.length&&(!protocol||recorded||wait);
  }
  if(protocol&&preferred.length&&!box.dataset.recordedShown){const decision=key.split('/')[1];const recorded=document.querySelector('.ct-editors select[data-layer-step="'+decision+'"][data-committed]:not([data-committed=""])')||workspace.querySelector('select[data-committed]:not([data-committed=""])');if(recorded){box.open=true;box.dataset.recordedShown='true';}}
  if(preferred.length&&!right.querySelector('[data-outcome-jump]')){const b=make('button','clinical-button','Outcome evidence for this decision');b.type='button';b.dataset.outcomeJump='';b.addEventListener('click',()=>{document.getElementById('dw-tab-criteria')?.click();box.open=true;box.scrollIntoView({block:'start',behavior:'instant'});box.querySelector('select').focus({preventScroll:true});});right.querySelector('.dw-tool-documents')?.append(b);}
  if(right.querySelector('.allocation-overview'))right.querySelector('[data-waiting-resource]')?.remove();
  if(protocol&&!right.querySelector('.allocation-overview')&&!right.querySelector('[data-waiting-resource]')){const a=make('a','clinical-button','Transplant waitlisted · policy & outcomes');a.dataset.waitingResource='';a.href=new URL('transplant/waiting/?disease='+slug,root);if(!right.querySelector('.allocation-overview'))right.querySelector('.dw-tool-documents')?.append(a);}
 }
 function scan(){queued=false;document.querySelectorAll('.dw-ready[data-workspace-key]').forEach(enhance);}
 new MutationObserver(records=>{if(!queued&&records.some(r=>r.type==='childList')){queued=true;requestAnimationFrame(scan);}}).observe(document.body,{childList:true,subtree:true});scan();
})();
