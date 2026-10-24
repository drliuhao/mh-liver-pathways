/* Integration invariants: every V7 review is reachable in its standard pathway,
   sources stay attached, and additions do not masquerade as eligibility results. */
const assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path');
const root=path.resolve(__dirname,'..');
const data=JSON.parse(fs.readFileSync(path.join(root,'transplant/assets/content.json'),'utf8'));
const HR=require(path.join(root,'transplant/assets/high-risk.js'));
const h=data.high_risk;
assert.equal(Object.keys(h.pathways).length,7);
let count=0, placements=0;
for(const p of data.index){
 const rr=HR.reviews(h,p.slug);count+=rr.length;
 const full=HR.overview(h,p.slug);
 assert(full.includes('High-risk protocol'));
 for(const r of rr){
  assert(r.steps.length>0,r.id);
  for(const id of r.steps){
   assert(p.steps.some(x=>x.id===id),r.id+': '+id);
   const rendered=HR.inline(h,p.slug,id);
   assert(rendered.includes('id="high-risk-'+r.anchor+'"'),r.id);
   assert(rendered.includes('High-risk evidence and full-text access'),r.id);
   assert(rendered.includes('institutional approval pending'),r.id);
   assert(rendered.includes('Treatment and continuing care'),r.id);
   placements++;
  }
  for(const key of r.references)assert(h.sources[key],r.id+': '+key);
  for(const study of r.evidence.studies||[])assert(r.references.includes(study.key),r.id+': missing study reference');
 }
 assert.equal(h.pathways[p.slug].documents.filter(x=>x.format==='pdf').length,1);
 assert(!full.includes('data-branch-index'), 'High-risk content must not become a standard selection branch');
 assert(!full.includes('/Users/')&&!full.includes('file://'));
 const ids=[...full.matchAll(/ id="([^"]+)"/g)].map(x=>x[1]);
 assert.equal(new Set(ids).size,ids.length,p.slug+' duplicate IDs');
}
assert.equal(count,21);assert.equal(h.readiness.length,4);assert.equal(Object.keys(h.sources).length,105);
for(const r of Object.values(h.sources)){
 if(r.doi){assert(r.author&&r.journal&&r.year&&r.pmid,r.key);assert(decodeURIComponent(r.tmc).includes(r.doi),r.key);}
 for(const pdf of r.pdf_links){assert(/^https?:\/\//.test(pdf.url),r.key);assert(pdf.method,r.key);}
}
const pdfCount=Object.values(h.sources).filter(r=>r.pdf_links.length).length;
assert(pdfCount>=57);
assert(HR.inline(h,'pcca','phenotype').includes('Expansion remains closed'));
assert(HR.inline(h,'icca','phenotype').includes('Intrahepatic metastases'));
assert(!JSON.stringify(h).includes('PDAC-'));
let onward=0;
for(const c of Object.values(data.continuations))for(const kind of ['branches','rules'])for(const actions of Object.values(c[kind]))for(const a of actions){
 const dest=HR.destination(a.url);if(dest){onward++;assert(h.pathways[dest.slug]);if(dest.id)assert(h.pathways[dest.slug].reviews.some(x=>x.anchor===dest.id));}
}
assert.equal(onward,20);
console.log(`PASS: ${count} reviews in ${placements} decision placements; ${h.readiness.length} shared readiness reviews; 105 attached sources; ${pdfCount} direct PDF sources; seven protocol PDFs; 20 branch links resolve within the standard protocol.`);
