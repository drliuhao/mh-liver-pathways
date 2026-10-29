/* Content ownership and invariants: presentation must not alter clinical rules. */
const fs=require('node:fs'),assert=require('node:assert/strict'),vm=require('node:vm'),cp=require('node:child_process');
const read=f=>fs.readFileSync(f,'utf8'),manifest=JSON.parse(read('tools/content_hierarchy.json')),navigation=JSON.parse(read('assets/roadmap-links.json'));
const generated={window:{}};vm.runInNewContext(read('assets/content-hierarchy-data.js'),generated);
assert.deepEqual(JSON.parse(JSON.stringify(generated.window.ContentHierarchyData)),manifest);
let count=0;
for(const [slug,refs] of Object.entries(manifest.references)){
 const source=slug==='hcc'?['Child-Pugh','ECOG performance status','LI-RADS, in full']:JSON.parse(read(slug+'/data/pathway.json')).quickref.map(q=>q.title);
 assert.deepEqual(refs.map(r=>r.source),source,slug+' must account for every reference exactly once');
 assert.equal(new Set(refs.map(r=>r.source)).size,refs.length);
 for(const r of refs){assert(['tool','criteria','guide','evidence'].includes(r.kind));assert(r.label&&r.decisions.length);assert(r.decisions.every(id=>navigation[slug][id]),slug+': invalid owning decision');count++;}
 if(slug!=='hcc')assert.equal(read(slug+'/data/pathway.json'),require('./apply_clinical_revisions.cjs').applyText(slug+'/data/pathway.json',cp.execFileSync('git',['show','dfda24c:'+slug+'/data/pathway.json'],{encoding:'utf8',maxBuffer:4e6}).replaceAll('stlocal approval','stratification')),'Clinical source content changed beyond recorded revisions');
}
assert.equal(count,49);assert.equal(Object.keys(manifest.references).length,12);
const bilcap=manifest.references.icca.find(r=>r.source==='BILCAP, as published');assert.equal(bilcap.kind,'evidence');assert.deepEqual(bilcap.decisions,['8']);
const crisis=manifest.references.nelm.find(r=>r.source==='Carcinoid crisis precautions');assert.deepEqual(crisis.decisions,['5','6','7','8']);
assert.equal(crisis.visibleCaution.text,JSON.parse(read('nelm/data/pathway.json')).quickref[3].rows[0][1],'Visible procedural caution must retain its exact source wording');
// Recorded clinical revisions (tools/clinical_revisions/) are the only permitted change to these sources.
const Revisions=require('./apply_clinical_revisions.cjs');
const pinned=file=>{const text=cp.execFileSync('git',['show','dfda24c:'+file],{encoding:'utf8',maxBuffer:8e6});return file.endsWith('content.json')?JSON.stringify(Revisions.applyContent(JSON.parse(text)),null,2):Revisions.applyText(file,text);};
for(const file of ['transplant/assets/content.json','transplant/assets/assistant.js','transplant/assets/risk-routing.js','assets/roadmap-links.json']){
 assert.equal(read(file),pinned(file),file+' clinical matching/source changed');
}
const layout=read('assets/decision-workspace.js');assert(layout.includes('middle.append(criteria,recommendations,related,controls)'),'Clinical recommendations must precede subsequent routes');
const presentation=read('assets/portal-navigation.js');
assert(!/decision-evidence(?:-data)?\.(?:js|css)/.test(presentation),'Standalone outcome panels are retired from the shared interface');
assert(presentation.includes('compact-evidence-data.js')&&presentation.includes('compact-treatment.js'),'Individual option evidence must remain available');
assert(read('assets/allocation-overview.js').includes('data-waiting-resource'),'Waiting resources must remain independent of retired outcome panels');
const hierarchy=read('assets/content-hierarchy.js');assert(hierarchy.includes("node.dataset.disclosureSorted='true'"),'Reference tables must not be deleted by recommendation restructuring');
assert(hierarchy.includes('grid.dataset.hierarchyReferences'),'Reference placement must reset when the workspace grid is replaced');
assert(!hierarchy.includes('||workspace.dataset.hierarchyReferences)return'),'A reused answer container must not suppress reference placement after switching topics');
assert(!/fetch\(|localStorage|sessionStorage|recordRiskFinding|changeStagedAnswer|dispatchEvent/.test(hierarchy),'Hierarchy layer must be read-only with respect to clinical findings');
for(const f of ['assets/content-hierarchy.js','assets/content-hierarchy-data.js','assets/decision-workspace.js','assets/decision-evidence.js','assets/portal-navigation.js'])new vm.Script(read(f),{filename:f});
console.log('PASS: 49 references assigned to clinical decisions; BILCAP only in adjuvant evidence; clinical data and branching unchanged; recommendations before evidence and secondary navigation.');
