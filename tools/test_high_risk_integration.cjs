/* Integration invariants: every V7 review is reachable in its standard pathway,
   sources stay attached, and additions do not masquerade as eligibility results. */
const assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path');
const root=path.resolve(__dirname,'..');
const data=JSON.parse(fs.readFileSync(path.join(root,'transplant/assets/content.json'),'utf8'));
const HR=require(path.join(root,'transplant/assets/high-risk.js'));
const h=data.high_risk;
assert.equal(Object.keys(h.pathways).length,7);
let count=0, placements=0;
const escapeHTML=s=>String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
let sourceSlots=0,studySummaries=0;
function checkEvidenceCard(slug,r){
 const card=HR.card(h,slug,r,r.id.startsWith('ALLOC-'));
 assert(card.indexOf('class="hr-next"')<card.indexOf('class="hr-criteria"'),r.id+' next action is buried');
 assert(card.includes('class="hr-criteria" open'),r.id+' criteria hidden by default');
 assert(card.includes(escapeHTML(r.stance)),r.id+' position missing');
 for(const rule of r.rules)assert(card.includes(escapeHTML(rule)),r.id+' rule lost');
 for(const key of ['synthesis','counterevidence','certainty','threshold_basis','policy_context']){
  const value=r.evidence[key];
  for(const item of Array.isArray(value)?value:[value].filter(Boolean))assert(card.includes(escapeHTML(item)),r.id+' evidence lost: '+key);
 }
 const sourceKeys=[...card.matchAll(/data-source-key="([^"]+)"/g)].map(x=>x[1]);
 assert.deepEqual(sourceKeys.slice().sort(),r.references.slice().sort(),r.id+' duplicate or missing access records');
 sourceSlots+=sourceKeys.length;
 for(const s of r.evidence.studies||[]){
  studySummaries++;
  for(const k of ['design_population','selection','results','limits','limitations','locator'])if(s[k])assert(card.includes(escapeHTML(s[k])),r.id+' study field lost: '+s.key+'/'+k);
  assert(card.includes(escapeHTML(h.sources[s.key].review_depth)),r.id+' review depth lost');
 }
 assert(!card.includes('<details class="hr-study"'),r.id+' nested study disclosure');
 assert(card.includes('not formal GRADE'),r.id+' certainty limitation missing');
}
for(const p of data.index){
 const rr=HR.reviews(h,p.slug);count+=rr.length;
 const full=HR.overview(h,p.slug);
 assert(full.includes('High-risk protocol'));
 for(const r of rr){
  checkEvidenceCard(p.slug,r);
  assert(r.steps.length>0,r.id);
  for(const id of r.steps){
   assert(p.steps.some(x=>x.id===id),r.id+': '+id);
   const rendered=HR.inline(h,p.slug,id);
   assert(rendered.includes('id="high-risk-'+r.anchor+'"'),r.id);
   assert(rendered.includes('Studies and full-text access'),r.id);
   assert(rendered.includes('institutional approval pending'),r.id);
   assert(rendered.includes('Treatment and continuing care'),r.id);
   placements++;
  }
  for(const key of r.references)assert(h.sources[key],r.id+': '+key);
  for(const study of r.evidence.studies||[])assert(r.references.includes(study.key),r.id+': missing study reference');
 }
 const docs=h.pathways[p.slug].documents;
 assert.equal(docs.filter(x=>x.format==='docx').length,1);
 if(['hcc','pcca','icca','crlm'].includes(p.slug))assert(docs.some(x=>x.url.endsWith('_v12.docx')),'Current V12 source document missing');
 else assert.equal(docs.filter(x=>x.format==='pdf').length,1);
 assert(!full.includes('data-branch-index'), 'High-risk content must not become a standard selection branch');
 assert(!full.includes('/Users/')&&!full.includes('file://'));
 const ids=[...full.matchAll(/ id="([^"]+)"/g)].map(x=>x[1]);
 assert.equal(new Set(ids).size,ids.length,p.slug+' duplicate IDs');
}
assert.equal(count,26);assert.equal(h.readiness.length,4);assert.equal(Object.keys(h.sources).length,135);
for(const r of h.readiness)checkEvidenceCard('hcc',r);
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
assert.equal(onward,0,"Unconditional high-risk links on broad branches must be removed");
console.log(`PASS: ${count} reviews in ${placements} reference-catalog placements; ${h.readiness.length} shared readiness reviews; 135 attached sources; ${pdfCount} direct PDF sources; four current V12 DOCX protocols plus three V7 protocol packages with preserved content; broad branch links removed in favor of separately tested contextual routing.`);
console.log(`PASS: ${studySummaries} study summaries and ${sourceSlots} unique-per-review source records preserve every criterion, synthesis, result, limitation and review-depth statement; no nested study disclosures.`);
