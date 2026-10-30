/* Keep the audited slide catalog intact; add document citations with explicit missing-slide status. */
(function(root){
  'use strict';
  function merge(catalog, supplement){
    const data=JSON.parse(JSON.stringify(catalog));
    Object.assign(data.publications,supplement.publications);
    let pending=0;
    for(const lib of data.libraries){
      const extra=supplement.libraries[lib.key]||{papers:[],policy_records:[]};
      const ids=new Set(lib.papers.map(r=>r.id));
      for(const row of extra.papers){if(!ids.has(row.id)){lib.papers.push(row);ids.add(row.id);}}
      const policyTitles=new Set(lib.policy_records.map(p=>p.title));
      for(const row of extra.policy_records){if(!policyTitles.has(row.title)){lib.policy_records.push(row);policyTitles.add(row.title);}}
      lib.publication_count=lib.papers.length;
      lib.matched_pdfs=lib.papers.filter(r=>data.publications[r.id].pdf_available===true).length;
      lib.no_slide_count=lib.papers.filter(r=>!r.slides.length).length+lib.policy_records.filter(r=>!r.slides.length).length;
      pending+=lib.no_slide_count;
    }
    data.unique_publications=Object.keys(data.publications).length;
    data.matched_publication_pdfs=Object.values(data.publications).filter(p=>p.pdf_available===true).length;
    data.missing_publication_pdfs=Object.values(data.publications).filter(p=>p.pdf_available===false).length;
    data.unchecked_publication_pdfs=Object.values(data.publications).filter(p=>p.pdf_available==null).length;
    data.no_slide_entries=pending;
    return data;
  }
  if(typeof module==='object'&&module.exports)module.exports={merge};
  else root.LibraryDocumentIndex={merge};
})(typeof window==='undefined'?globalThis:window);

