/* A presentation edit must preserve V12 data, thresholds and clinical action logic. */
const fs=require('node:fs'),cp=require('node:child_process'),vm=require('node:vm'),assert=require('node:assert/strict'),path=require('node:path');
const root=path.resolve(__dirname,'..'),read=f=>fs.readFileSync(path.join(root,f),'utf8');
const orangeFiles=JSON.parse(read('tools/orange_document_hashes.json'));
const clarityFiles=JSON.parse(read('tools/clarity_document_hashes.json'));
for(const item of [...orangeFiles,...clarityFiles])assert.equal(require('node:crypto').createHash('sha256').update(fs.readFileSync(path.join(root,item.path))).digest('hex'),clarityFiles.find(x=>x.path===item.path)?.after||item.after,item.path+' document checksum');
// The only content-payload change is the checksum of these ten recolored author-created files.
const original=f=>orangeFiles.reduce((text,item)=>text.replaceAll(item.before,item.after),cp.execFileSync('git',['show','a787e08:'+f],{cwd:root,encoding:'utf8',maxBuffer:8e6}));
function neutralPresentation(raw){
 const d=JSON.parse(raw);
 const label=s=>{s=s.replace(/^V\d+\s+/,'').replace(' · DOCX',' · Word');return s[0].toUpperCase()+s.slice(1);};
 for(const p of d.index){p.docs=p.docs.filter(x=>x.url!==p.protocol);for(const x of p.docs)x.label=label(x.label);}
 for(const p of Object.values(d.high_risk.pathways))for(const x of p.documents||[])x.label=label(x.label);
 const designs={AFP_RESPONSE:'Retrospective cohort',AFP_500:'Retrospective cohort',AFP_SLOPE:'Retrospective cohort',AFP_NYCA:'Retrospective validation cohort',AFP_OCCULT:'Retrospective cohort',SHARP:'Randomized phase III trial',ASCO_BTC:'Clinical guidance',NALIRICC:'Randomized phase II trial',MOUNTAINEER:'Noncomparative phase II study',SUNLIGHT:'Randomized phase III trial',FRESCO2:'Randomized phase III trial',CASSANDRA:'Randomized phase III trial',NAPOLI1:'Randomized phase III trial',MIXED_PRIMARY:'Retrospective cohort'};
 for(const [k,v] of Object.entries(designs))d.sources['V12-'+k].kind=v;
 for(const plans of Object.values(d.care))for(const p of plans)p.actions=p.actions.filter(a=>a.label!=='V12 full-text appraisals');
 return d;
}
// Approved clinical revisions are recorded in tools/clinical_revisions/ and applied to the pinned original; nothing else may change.
const Revisions=require('./apply_clinical_revisions.cjs');
for(const file of ['transplant/assets/content.json','tools/v12_content_snapshot.json'])assert.deepEqual(JSON.parse(read(file)),Revisions.applyContent(neutralPresentation(original(file))),file+' changed clinical content beyond approved labels, release-index navigation and recorded clinical revisions');
for(const file of ['transplant/assets/risk-routing.js','transplant/assets/high-risk.js','assets/roadmap-links.json'])assert.equal(read(file),Revisions.applyText(file,original(file)),file+' changed clinical content');
const src=read('assets/contextual-info.js'),context={window:{}};vm.runInNewContext(read('assets/contextual-copy.js'),context);const copy=context.window.ContextualCopy;
const data=JSON.parse(read('transplant/assets/content.json'));let reviewed=0;
for(const [key,entry] of Object.entries(copy.help)){
 const [slug,step,id]=key.split('/');const q=data.assistants[slug+'/'+step].questions.find(q=>q.id===id);
 assert.equal(entry.source,q.help,key+' exact source');assert.equal(entry.title,q.label,key+' original prompt');assert(entry.concise&&entry.label);reviewed++;
}
assert.equal(reviewed,63);assert.equal(Object.keys(copy.headings).length,46);
for(const p of data.index)for(const s of p.steps)assert.equal(copy.headings[p.slug+'/'+s.id].source,s.question);
for(const key of ['hcc/allocation/afp','hcc/treatment/afp'])assert.equal(copy.help[key].concise,copy.help[key].source,'AFP rule must remain complete');
assert(copy.help['pcca/phenotype/size'].concise.includes('Exactly 3 cm fails <3 cm'));
assert(copy.help['crlm/biology/cea'].concise.includes('Initial request excludes >80; extensions require <80. Exactly 80'));
assert(copy.help['icca/phenotype/focality'].concise.includes('≥2 separate nodules'));
assert(copy.help['icca/phenotype/focality'].concise.includes('no universal distance cutoff'));
assert(copy.help['pcca/diagnosis/biopsy'].concise.includes('EUS, percutaneous or operative'));
assert(copy.help['pcca/diagnosis/biopsy'].concise.includes('without traversing the primary is a different procedure'));
assert(src.includes('node.textContent!==entry.source'),'Stale help must fall back to original');
assert(src.includes("node.closest('.rf-cautions')"),'Standalone Avoid recommendations must stay fully visible');
assert.equal(Object.keys(copy.recommendations).length,46);
for(const [key,entry]of Object.entries(copy.recommendations)){
 const [slug,id,group,index]=key.split('/');let stages;
 if(slug==='hcc'){const s=read('hcc/index.html');stages=vm.runInNewContext(s.slice(s.indexOf('const STAGES = ['),s.indexOf('/* the quantifier'))+';STAGES');}
 else stages=JSON.parse(read(slug+'/data/pathway.json')).gates;
 assert.equal(entry.source,stages.find(s=>s.id===id)[group][index].t,key+' exact source');
}
assert(!src.includes("if(!d.open)enhance(d)"),'Criteria must remain native inline expansions');
const app=read('transplant/assets/app.js'),old=original('transplant/assets/app.js');
for(const [a,b] of [['function renderActions(', 'function renderRiskReference('],['function renderStep()', 'function renderMeeting()']]){
 const slice=s=>s.slice(s.indexOf(a),s.indexOf(b,s.indexOf(a)));const metadata=' data-action-label="${e(a.label)}" data-action-condition="${e(a.detail||\'\')}"';assert.equal(slice(app).replaceAll(metadata,'').replace(' renderLayerStack();\n','').replace(' document.body.dataset.currentAssessment=browseOrigin||active.steps[stepIndex].id;\n','').replace('config.questions.filter(q=>answers[q.id]).map(q=>q.id)',"config.questions.filter(q=>!answers[q.id]||answers[q.id]==='unknown').map(q=>q.id)").replace('href="#meeting-${i.id}"','href="/mh-liver-pathways/transplant/alignment/${active.slug}/#${i.id}"'),slice(old),'Changed clinical action renderer '+a);
}
const docs=Object.keys(JSON.parse(read('assets/roadmap-links.json'))).map(x=>x+'/index.html').concat(data.index.map(p=>'transplant/'+p.slug+'/index.html'));
for(const doc of docs)assert(read(doc).includes('portal-navigation.js?v=20261030-review1'),doc+' missing display update');
console.log(`PASS: V12 data and clinical renderers unchanged; ${docs.length} pages; 46 headings, ${reviewed} help summaries and 46 recommendation guards verified; all Avoid wording retained.`);
