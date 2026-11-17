/* Count a paper once across libraries; the cited documents can add references beyond the slide catalogue. */
(function(root){
  'use strict';
  function merge(catalog, supplement){
    const data = JSON.parse(JSON.stringify(catalog));
    const fullEdition = Object.hasOwn(catalog, 'matched_publication_pdfs');
    const identities = new Map(), aliases = new Map(), publications = {}, slidePapers = new Set();
    function register(id, publication){
      const doi = String(publication.doi || '').trim().toLowerCase().replace(/^https?:\/\/(?:dx\.)?doi\.org\//, '');
      const pmid = String(publication.pmid || '').trim();
      const keys = [id, ...(doi ? ['doi:'+doi] : []), ...(pmid ? ['pmid:'+pmid] : [])];
      const canonical = keys.map(k=>identities.get(k)).find(Boolean) || id;
      keys.forEach(k=>identities.set(k,canonical));
      aliases.set(id,canonical);
      if(!publications[canonical]) publications[canonical] = {...publication};
      else{
        const existing = publications[canonical];
        for(const [field,value] of Object.entries(publication)){
          if(existing[field] == null || existing[field] === '') existing[field] = value;
        }
        if(publication.pdf_available === true) existing.pdf_available = true;
      }
    }
    Object.entries(catalog.publications).forEach(([id,p])=>register(id,p));
    Object.entries(supplement.publications).forEach(([id,p])=>register(id,p));
    data.publications = publications;
    let pending = 0;
    for(const lib of data.libraries){
      const extra = supplement.libraries[lib.key] || {papers:[],policy_records:[]};
      const papers = new Map();
      function addPaper(original, fromSlides){
        const id = aliases.get(original.id);
        if(!id) throw Error('Unknown publication '+original.id);
        if(fromSlides && !original.document_only && (!fullEdition || original.slides?.length)) slidePapers.add(id);
        const existing = papers.get(id);
        if(!existing){
          papers.set(id,{...original,id});
          return;
        }
        for(const field of ['slides','inclusion']){
          if(Array.isArray(original[field])) existing[field] = [...new Set([...(existing[field] || []), ...original[field]])];
        }
        if(existing.slides?.length) delete existing.document_only;
      }
      lib.papers.forEach(p=>addPaper(p,true));
      extra.papers.forEach(p=>addPaper(p,false));
      lib.papers = [...papers.values()];
      if(!/^(?:Ampullary|Pancreatic) cancer roadmap$/i.test(lib.title))
        lib.title = lib.title.replace(/ cancer roadmap$/i,' roadmap');
      lib.title = lib.title.replace(/standard protocol$/i,'standard transplant pathway').replace(/high-risk \/ boundary protocol$/i,'high-risk transplant pathway');
      const policyTitles = new Set(lib.policy_records.map(p=>p.title));
      for(const row of extra.policy_records){
        if(!policyTitles.has(row.title)){lib.policy_records.push(row);policyTitles.add(row.title);}
      }
      lib.publication_count = lib.papers.length;
      if(fullEdition){
        lib.matched_pdfs = lib.papers.filter(r=>publications[r.id].pdf_available === true).length;
        lib.no_slide_count = [...lib.papers,...lib.policy_records].filter(r=>!r.slides?.length).length;
        pending += lib.no_slide_count;
      }
    }
    data.unique_publications = Object.keys(publications).length;
    if(fullEdition){
      data.from_slide_libraries = slidePapers.size;
      data.additional_document_publications = data.unique_publications - slidePapers.size;
      data.matched_publication_pdfs = Object.values(publications).filter(p=>p.pdf_available===true).length;
      data.missing_publication_pdfs = Object.values(publications).filter(p=>p.pdf_available===false).length;
      data.unchecked_publication_pdfs = Object.values(publications).filter(p=>p.pdf_available==null).length;
      data.no_slide_entries = pending;
    }
    return data;
  }
  if(typeof module === 'object' && module.exports) module.exports={merge};
  else root.LibraryDocumentIndex={merge};
})(typeof window === 'undefined' ? globalThis : window);
