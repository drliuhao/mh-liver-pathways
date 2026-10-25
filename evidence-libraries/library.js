'use strict';
(async()=>{
 const e=s=>String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
 const out=document.getElementById('results'),select=document.getElementById('library'),search=document.getElementById('search');
 try{
  const response=await fetch('catalog.json');if(!response.ok)throw Error('Catalog unavailable');const data=await response.json();
  document.getElementById('census').textContent=`${data.libraries.length} libraries · ${data.unique_publications} unique publications · ${data.matched_publication_pdfs} matched publication PDFs. ${data.missing_publication_pdfs} PDFs remain unmatched; ${data.appraisals_pending} appraisals are pending.`;
  for(const lib of data.libraries){const option=document.createElement('option');option.value=lib.key;option.textContent=lib.title;select.append(option);}
  function render(){
   const key=decodeURIComponent(location.hash.slice(1));select.value=data.libraries.some(l=>l.key===key)?key:'';
   const lib=data.libraries.find(l=>l.key===select.value),q=search.value.trim().toLowerCase();
   if(!lib){
    const matches=data.libraries.filter(l=>(l.title+' '+l.papers.map(r=>{const p=data.publications[r.id];return p.title+' '+p.doi+' '+p.pmid;}).join(' ')).toLowerCase().includes(q));
    out.innerHTML=`<p class="count">${matches.length} libraries shown</p><div class="library-grid">${matches.map(l=>`<article class="library-card"><h2><a href="#${e(l.key)}">${e(l.title)}</a></h2><p>${l.publication_count} papers · ${l.matched_pdfs} matched PDFs</p><p>${l.slides} slides in its own PPT</p><p class="meta">${e(l.family.replace(/^\d+_/,'').replaceAll('_',' '))}</p></article>`).join('')}</div>`;return;
   }
   const matches=lib.papers.filter(r=>{const p=data.publications[r.id];return [p.title,p.doi,p.pmid,p.coverage].join(' ').toLowerCase().includes(q);});
   out.innerHTML=`<p><a href="#">← All evidence libraries</a></p><div class="library-heading"><h2>${e(lib.title)}</h2><p>${lib.publication_count} publications · ${lib.matched_pdfs} deposited PDFs · ${lib.slides} PPT slides</p><p><b>Matching PPT:</b> ${e(lib.ppt_filename)}</p><details><summary>Where to find the local files</summary><p>Synology → MHH work → Memorial Herman Transplant Oncology Protocols → <code>V15_complete_evidence_libraries_2026-10-25/${e(lib.local_folder)}/</code></p><p>The PPT, PDF_depot and searchable index are together.${lib.document?' The unchanged source document is included: '+e(lib.document)+'.':''}</p></details><p class="meta">These summaries retain their source review dates. Citation-only entries are explicitly marked; they are not completed full-text reviews.</p></div><p class="count">${matches.length} of ${lib.publication_count} publications shown</p><ul class="records">${matches.map(r=>{const p=data.publications[r.id];return `<li class="record"><h3>${e(p.title)}</h3><p class="meta">${e(p.year)} · PMID ${e(p.pmid||'not indexed')} · DOI ${e(p.doi||'not recorded')}</p><p><b>PPT slides ${r.slides.join(', ')}</b> · ${e(p.coverage)}</p><p class="${p.pdf_available?'meta':'gap'}">${p.pdf_available?'PDF deposited in this local library':'PDF not yet matched in the audited depots'}</p><div class="access"><a href="${e(p.url)}" target="_blank" rel="noopener">Publication / full text ↗</a><a href="${e(p.tmc)}" target="_blank" rel="noopener">TMC full-text access ↗</a></div><details><summary>Why this paper is included</summary><p>${e(r.inclusion.join('; '))}</p></details></li>`;}).join('')}</ul>${lib.policy_records.length?`<h3>Policy and guideline records</h3><p class="meta">Separate from publication counts.</p><ul>${lib.policy_records.map(p=>`<li>${e(p.title)} · PPT slides ${p.slides.join(', ')}${p.pdf_available?' · PDF in the local library':''}</li>`).join('')}</ul>`:''}`;
  }
  select.addEventListener('change',()=>{history.pushState(null,'','#'+select.value);search.value='';render();});search.addEventListener('input',render);window.addEventListener('hashchange',render);window.addEventListener('popstate',render);render();
 }catch(error){out.textContent='The evidence index could not load. Please reload this page.';console.error(error);}
})();
