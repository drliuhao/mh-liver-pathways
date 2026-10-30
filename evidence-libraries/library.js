'use strict';
(async()=>{
 const e=s=>String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
 const out=document.getElementById('results'),select=document.getElementById('library'),search=document.getElementById('search');
 const slides=r=>r.slides.length?'PPT slides '+r.slides.join(', '):'No slide yet';
 const pdf=p=>p.pdf_available===true?'PDF matched in the audited depots':p.pdf_available===false?'PDF not yet matched in the audited depots':'PDF status not yet checked for this index entry';
 const links=p=>'<div class="access">'+(p.url?'<a href="'+e(p.url)+'" target="_blank" rel="noopener">Publication / full text ↗</a>':'')+(p.tmc?'<a href="'+e(p.tmc)+'" target="_blank" rel="noopener">TMC full-text access ↗</a>':'')+'</div>';
 const title=l=>l.title.replace(/\bprotocol\b/gi,'pathway').replace(/ cancer roadmap$/i,' roadmap');
 const pending=l=>l.no_slide_count?' · '+l.no_slide_count+(l.no_slide_count===1?' reference has':' references have')+' no slide yet':'';
 try{
  const responses=await Promise.all([fetch('catalog.json?v=20261030-review1'),fetch('document-index.json?v=20261030-review1')]);
  if(responses.some(r=>!r.ok))throw Error('Catalog unavailable');
  const [base,supplement]=await Promise.all(responses.map(r=>r.json()));
  const data=LibraryDocumentIndex.merge(base,supplement);
  document.getElementById('census').textContent=data.libraries.length+' libraries · '+data.unique_publications+' unique publications · '+data.matched_publication_pdfs+' matched PDFs · '+data.missing_publication_pdfs+' PDFs unmatched · '+data.unchecked_publication_pdfs+' PDF statuses not yet checked. '+data.no_slide_entries+' library entries have no slide yet.';
  for(const lib of data.libraries){const option=document.createElement('option');option.value=lib.key;option.textContent=title(lib);select.append(option);}
  const paperSearch=(r,p)=>[p.title,p.doi,p.pmid,p.coverage,slides(r),...r.inclusion].join(' ').toLowerCase();
  const policySearch=r=>[r.title,slides(r),...(r.inclusion||[])].join(' ').toLowerCase();
  function render(){
   const key=decodeURIComponent(location.hash.slice(1));select.value=data.libraries.some(l=>l.key===key)?key:'';
   const lib=data.libraries.find(l=>l.key===select.value),q=search.value.trim().toLowerCase();
   if(!lib){
    const matches=data.libraries.filter(l=>title(l).toLowerCase().includes(q)||l.papers.some(r=>paperSearch(r,data.publications[r.id]).includes(q))||l.policy_records.some(r=>policySearch(r).includes(q)));
    out.innerHTML='<p class="count">'+matches.length+' libraries shown</p><div class="library-grid">'+matches.map(l=>'<article class="library-card"><h2><a href="#'+e(l.key)+'">'+e(title(l))+'</a></h2><p>'+l.publication_count+' papers · '+l.matched_pdfs+' matched PDFs</p><p>'+l.slides+' slides in its PPT'+pending(l)+'</p><p class="meta">'+e(l.family.replace(/^\d+_/,'').replaceAll('_',' '))+'</p></article>').join('')+'</div>';return;
   }
   const matches=lib.papers.filter(r=>paperSearch(r,data.publications[r.id]).includes(q));
   const policies=lib.policy_records.filter(r=>policySearch(r).includes(q));
   out.innerHTML='<p><a href="#">← All evidence libraries</a></p><div class="library-heading"><h2>'+e(title(lib))+'</h2><p>'+lib.publication_count+' publications · '+lib.matched_pdfs+' matched PDFs · '+lib.slides+' PPT slides'+pending(lib)+'</p><p><b>Matching PPT:</b> '+e(lib.ppt_filename)+'</p><details><summary>Where to find the local files</summary><p>Synology → MHH work → Memorial Herman Transplant Oncology Protocols → <code>V15_complete_evidence_libraries_2026-10-25/'+e(lib.local_folder)+'/</code></p><p>The PPT, PDF_depot and searchable index are together. References marked “No slide yet” are cited in the newer documents and have not been added to this PPT.</p></details><p class="meta">Slide numbers describe the existing PPT. A document citation alone does not establish a completed full-text appraisal or a deposited PDF.</p></div><p class="count">'+matches.length+' of '+lib.publication_count+' publications shown</p><ul class="records">'+matches.map(r=>{
    const p=data.publications[r.id];
    return '<li class="record"><h3>'+e(p.title)+'</h3><p class="meta">'+(p.year?e(p.year)+' · ':'')+'PMID '+e(p.pmid||'not indexed')+' · DOI '+e(p.doi||'not recorded')+'</p><p><b>'+e(slides(r))+'</b>'+(r.document_only?' · Document reference':' · '+e(p.coverage))+'</p><p class="'+(p.pdf_available===false?'gap':'meta')+'">'+pdf(p)+'</p>'+links(p)+'<details><summary>Why this paper is included</summary><p>'+e(r.inclusion.join('; '))+'</p></details></li>';
   }).join('')+'</ul>'+(policies.length?'<h3>Policy, guidance and document records</h3><p class="meta">Separate from publication counts.</p><ul class="records">'+policies.map(p=>'<li class="record"><h3>'+e(p.title)+'</h3><p><b>'+e(slides(p))+'</b></p><p class="meta">'+pdf(p)+'</p>'+links(p)+(p.inclusion?.length?'<p class="meta">'+e(p.inclusion.join('; '))+'</p>':'')+'</li>').join('')+'</ul>':'');
  }
  select.addEventListener('change',()=>{history.pushState(null,'','#'+select.value);search.value='';render();});search.addEventListener('input',render);window.addEventListener('hashchange',render);window.addEventListener('popstate',render);render();
 }catch(error){out.textContent='The evidence index could not load. Please reload this page.';console.error(error);}
})();
