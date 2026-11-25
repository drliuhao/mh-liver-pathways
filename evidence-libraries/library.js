/* One clinical index in both editions; institutional artifacts remain full-edition only. */
'use strict';
(async()=>{
 const e=s=>String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
 const out=document.getElementById('results'),select=document.getElementById('library'),search=document.getElementById('search');
 const share=document.body.dataset.edition==='share'||document.documentElement.dataset.edition==='share'||location.pathname.includes('mh-liver-pathways-share');
 const links=p=>'<div class="access">'+(p.url?'<a href="'+e(p.url)+'" target="_blank" rel="noopener">Publication / full text ↗</a>':'')+(p.tmc?'<a href="'+e(p.tmc)+'" target="_blank" rel="noopener">TMC full text ↗</a>':'')+'</div>';
 const inclusion=r=>(r.inclusion||[]).map(e).join('; ');
 const slideNote=r=>!share&&r.slides?.length?'<p class="meta">Evidence PPT · slides '+r.slides.join(', ')+'</p>':'';
 try{
  const responses=await Promise.all([fetch('catalog.json?v=20261125-alignment1'),fetch('document-index.json?v=20261125-alignment1')]);
  if(responses.some(r=>!r.ok))throw Error('Catalog unavailable');
  const [base,supplement]=await Promise.all(responses.map(r=>r.json()));const data=LibraryDocumentIndex.merge(base,supplement);
  document.getElementById('census').textContent=data.libraries.length+' libraries · '+data.unique_publications+' distinct publications. Search includes policy and guidance records.';
  for(const lib of data.libraries){const o=document.createElement('option');o.value=lib.key;o.textContent=lib.title;select.append(o);}
  const paperSearch=(r,p)=>[p.title,p.author,p.journal,p.year,p.doi,p.pmid,...(r.inclusion||[])].join(' ').toLowerCase();
  const policySearch=r=>[r.title,...(r.inclusion||[])].join(' ').toLowerCase();
  const paper=r=>{const p=data.publications[r.id];return '<li class="record"><h3>'+e(p.title)+'</h3><p class="meta">'+[p.author,p.journal,p.year,p.pmid?'PMID '+p.pmid:'',p.doi?'DOI '+p.doi:''].filter(Boolean).map(e).join(' · ')+'</p>'+(p.publisher_citation?'<p class="meta">'+e(p.publisher_citation)+'</p>':'')+links(p)+(r.inclusion?.length?'<p class="library-clinical-summary"><b>Cited in:</b> '+inclusion(r)+'</p>':'')+slideNote(r)+(!share?'<p class="meta">'+(p.pdf_available===true?'PDF matched in the local reference depot':p.pdf_available===false?'PDF not yet matched':'Local PDF status not checked')+'</p>':'')+'</li>';};
  const policy=r=>'<li class="record"><h3>'+e(r.title)+'</h3>'+links(r)+(r.inclusion?.length?'<p class="library-clinical-summary"><b>Cited in:</b> '+inclusion(r)+'</p>':'')+slideNote(r)+'</li>';
  function render(){
   const key=decodeURIComponent(location.hash.slice(1));select.value=data.libraries.some(l=>l.key===key)?key:'';
   const lib=data.libraries.find(l=>l.key===select.value),q=search.value.trim().toLowerCase();
   if(!lib&&!q){out.innerHTML='<div class="library-grid">'+data.libraries.map(l=>'<article class="library-card"><h2><a href="#'+e(l.key)+'">'+e(l.title)+'</a></h2><p>'+l.publication_count+' publications · '+l.policy_records.length+' policy / guidance records</p></article>').join('')+'</div>';return;}
   const chosen=lib?[lib]:data.libraries;
   let count=0;const groups=chosen.map(l=>{const papers=l.papers.filter(r=>paperSearch(r,data.publications[r.id]).includes(q)),policies=l.policy_records.filter(r=>policySearch(r).includes(q));count+=papers.length+policies.length;
    if(!papers.length&&!policies.length)return '';
    return '<section class="library-global-hit"><h2><a href="#'+e(l.key)+'">'+e(l.title)+'</a></h2>'+(lib&&!share?'<details><summary>Local presentation and files</summary><p>'+e(l.ppt_filename||'')+'</p><p>'+e(l.local_folder||'')+'</p><p class="meta">Slide numbers describe the current presentation. A document citation alone does not establish completed full-text appraisal.</p></details>':'')+(papers.length?'<ul class="records">'+papers.map(paper).join('')+'</ul>':'')+(policies.length?'<h3>Policy & guidance</h3><ul class="records">'+policies.map(policy).join('')+'</ul>':'')+'</section>';}).join('');
   out.innerHTML=(lib?'<p><a href="#">← All libraries</a></p>':'')+'<p class="count">'+count+' matching records'+(!lib?' across libraries':'')+'</p>'+groups+(count?'':'<p>No included source matches this search. Clear the search or select another library.</p>');
  }
  select.addEventListener('change',()=>{history.pushState(null,'','#'+select.value);render();});search.addEventListener('input',render);window.addEventListener('hashchange',render);window.addEventListener('popstate',render);render();
 }catch(error){out.textContent='The evidence index could not load. Please reload this page.';console.error(error);}
})();
