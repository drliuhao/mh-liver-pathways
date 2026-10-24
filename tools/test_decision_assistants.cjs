/* Clinical-route scenarios plus exhaustive categorical-state checks. No patient data. */
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const root=path.resolve(__dirname,'..');
const D=JSON.parse(fs.readFileSync(path.join(root,'transplant/assets/content.json'),'utf8'));
const R=require(path.join(root,'transplant/assets/assistant.js'));
const stepOf=key=>{const [p,s]=key.split('/');return D.index.find(pw=>pw.slug===p).steps.find(st=>st.id===s);};
const result=(key,answers)=>R.evaluate(D.assistants[key],answers,stepOf(key).branches);
const expect=(key,answers,branch,kind)=>{const r=result(key,answers);assert.equal(r.branch,branch,key+JSON.stringify(answers));if(kind)assert.equal(r.kind,kind,key);return r;};
const proceed={
 'hcc/diagnosis':{diagnosis:'hcc'},
 'hcc/curative-route':{spread:'clear',operation:'transplant'},
 'hcc/allocation':{burden:'t2',afp:'met',spread:'yes'},
 'hcc/treatment':{response:'controlled',afp:'yes',reserve:'yes'},
 'hcc/listing':{exception:'yes',fitness:'yes'},
 'hcc/waitlist':{control:'maintained',fitness:'yes'},
 'hcc/after-transplant':{plan:'yes',concern:'none'},
 'pcca/localize':{origin:'hilar',review:'yes'},
 'pcca/diagnosis':{diagnosis:'yes',biopsy:'no'},
 'pcca/phenotype':{size:'small',unresectable:'yes',spread:'clear',diagnosis:'yes'},
 'pcca/neoadjuvant':{protocol:'yes',status:'safe'},
 'pcca/staging':{stage:'negative',ready:'yes'},
 'pcca/listing':{evidence:'yes',ready:'ready'},
 'pcca/follow-up':{plan:'yes',concern:'none'},
 'icca/diagnosis':{histology:'icca',extent:'yes'},
 'icca/phenotype':{focality:'solitary',profile:'fits',spread:'yes',program:'yes'},
 'icca/therapy':{control:'controlled',safe:'yes'},
 'icca/stability':{duration:'met',disease:'stable'},
 'icca/review':{criteria:'met',reviews:'yes'},
 'icca/follow-up':{plan:'yes',concern:'none'},
 'crlm/map-disease':{primary:'yes',spread:'clear'},
 'crlm/biology':{molecular:'fits',cea:'low',size:'yes'},
 'crlm/unresectability':{clearance:'no'},
 'crlm/control':{response:'controlled',duration:'yes',unresectable:'yes'},
 'crlm/clocks':{primary:'yes',interval:'yes',synchronous:'na'},
 'crlm/restaging':{stage:'clear',timing:'yes',control:'yes'},
 'crlm/review':{criteria:'met',reviews:'yes'},
 'crlm/transplant':{plan:'yes',concern:'none'},
 'nelm/biology':{grade:'fits',primary:'yes'},
 'nelm/distribution':{primary:'yes',spread:'none'},
 'nelm/options':{strategy:'transplant'},
 'nelm/exposure':{safety:'acceptable'},
 'nelm/observation':{clearance:'met',imaging:'yes',control:'yes'},
 'nelm/review':{criteria:'met',reviews:'yes'},
 'nelm/follow-up':{plan:'yes',concern:'none'},
 'hehe/diagnosis':{pathology:'hehe'},
 'hehe/stage':{vascular:'yes',strategy:'transplant',extrahepatic:'none'},
 'hehe/risk':{criteria:'yes',benefit:'supported'},
 'hehe/review':{criteria:'met',reviews:'yes'},
 'hehe/follow-up':{plan:'yes',concern:'none'},
 'hca/characterize':{diagnosis:'hca'},
 'hca/standard-care':{bleeding:'no',management:'no'},
 'hca/exception-route':{route:'syndrome'},
 'hca/transformation':{diagnosis:'benign'},
 'hca/review':{criteria:'met',reviews:'yes'},
 'hca/follow-up':{plan:'yes',concern:'none'},
};
assert.equal(Object.keys(D.assistants).length,46);
assert.deepEqual(Object.keys(proceed).sort(),Object.keys(D.assistants).sort());
let combinations=0;
for(const [key,config] of Object.entries(D.assistants)){
 assert(config.questions.length>=1&&config.questions.length<=4,key);
 assert.equal(result(key,{}).state,'pending',key);
 const good=result(key,proceed[key]);assert.equal(good.kind,'advance',key);
 for(const q of config.questions){
  const partial={...proceed[key]};delete partial[q.id];assert.notEqual(result(key,partial).kind,'advance',key+' missing '+q.id);
  partial[q.id]='unknown';assert.notEqual(result(key,partial).kind,'advance',key+' uncertain '+q.id);
  partial[q.id]='INVALID';assert.notEqual(result(key,partial).kind,'advance',key+' invalid '+q.id);
 }
 const visit=(i,answers)=>{
  if(i<config.questions.length){const q=config.questions[i];for(const v of ['',...q.options.map(o=>o.value)])visit(i+1,{...answers,[q.id]:v});return;}
  combinations++;
  const r=result(key,answers);
  if(r.branch!==null)assert(stepOf(key).branches[r.branch],key);
  if(r.kind==='advance')assert(config.questions.every(q=>answers[q.id]&&answers[q.id]!=='unknown'),key);
  if(config.questions.every(q=>answers[q.id]&&answers[q.id]!=='unknown'))assert.notEqual(r.state,'pending',key+JSON.stringify(answers));
 };
 visit(0,{});
 const html=R.render(config,D.sources);
 assert.equal((html.match(/<select /g)||[]).length,config.questions.length,key);
 assert(!/<input|<textarea|type="date"|signature|Save \/ download JSON/.test(html),key);
 for(const q of config.questions)for(const id of [...q.refs,...q.criteria.flatMap(c=>c.refs)])assert(D.sources[id],id);
}
// High-impact distinctions and known exclusions override a proceed route.
expect('hcc/allocation',{burden:'ds',afp:'met',spread:'yes'},1,'advance');
expect('hcc/allocation',{burden:'t1',afp:'met',spread:'yes'},2,'hold');
expect('hcc/allocation',{burden:'beyond',afp:'met',spread:'yes'},3,'hold');
expect('hcc/allocation',{burden:'t2',afp:'not-met',spread:'yes'},null,'hold');
expect('hcc/allocation',{burden:'ds',afp:'met',spread:'no'},null,'stop');
expect('hcc/curative-route',{spread:'clear',operation:'resection'},0,'redirect');
expect('pcca/phenotype',{size:'large',unresectable:'yes',spread:'clear',diagnosis:'yes'},1,'hold');
expect('pcca/phenotype',{size:'none',unresectable:'yes',spread:'clear',diagnosis:'yes'},0,'advance');
expect('pcca/phenotype',{size:'small',unresectable:'yes',spread:'present',diagnosis:'yes'},null,'stop');
expect('pcca/diagnosis',{diagnosis:'yes',biopsy:'yes'},null,'stop');
expect('pcca/staging',{stage:'incomplete',ready:'yes'},1,'hold');
expect('pcca/staging',{stage:'positive',ready:'yes'},null,'stop');
expect('pcca/staging',{stage:'negative',ready:'no'},null,'hold');
expect('icca/phenotype',{focality:'multiple',profile:'fits',spread:'yes',program:'yes'},1,'redirect');
expect('icca/phenotype',{focality:'uncertain',profile:'fits',spread:'yes',program:'yes'},null,'hold');
expect('icca/stability',{duration:'short',disease:'stable'},1,'hold');
expect('icca/stability',{duration:'met',disease:'progression'},null,'stop');
expect('crlm/biology',{molecular:'fits',cea:'boundary',size:'yes'},null,'hold');
expect('crlm/biology',{molecular:'fits',cea:'high',size:'yes'},null,'stop');
expect('crlm/biology',{molecular:'outside',cea:'low',size:'yes'},1,'redirect');
expect('crlm/unresectability',{clearance:'yes'},0,'redirect');
expect('crlm/unresectability',{clearance:'uncertain'},2,'hold');
expect('crlm/clocks',{primary:'yes',interval:'yes',synchronous:'different'},1,'hold');
expect('crlm/clocks',{primary:'yes',interval:'yes',synchronous:'met'},0,'advance');
expect('nelm/distribution',{primary:'yes',spread:'cleared'},1,'hold');
expect('nelm/distribution',{primary:'yes',spread:'solid'},null,'stop');
expect('hehe/stage',{vascular:'yes',strategy:'transplant',extrahepatic:'limited'},2,'hold');
expect('hehe/stage',{vascular:'no',strategy:'transplant',extrahepatic:'none'},null,'stop');
for(const route of ['syndrome','beta','adenomatosis','complicated'])expect('hca/exception-route',{route},0,'advance');
expect('hca/exception-route',{route:'none'},1,'hold');
expect('hca/standard-care',{bleeding:'yes',management:'no'},null,'stop');
// Exact boundaries remain explicit in rendered source definitions.
const hcc=JSON.stringify(D.assistants['hcc/allocation']);
for(const term of ['4–5 Class 5 lesions: each <3 cm','1 to <2 cm','summed diameters ≤8 cm','2–5 cm','<500'])assert(hcc.includes(term),term);
assert(JSON.stringify(D.assistants['pcca/phenotype']).includes('Exactly 3 cm does not meet <3 cm'));
assert(R.evidence(['H-milan'],D.sources).includes('query=any,contains,10.1056%2FNEJM199603143341104'));
// No data submission, saved-record interface, or old kit remains in the live workflow.
for(const name of ['assistant.js','app.js']){
 const js=fs.readFileSync(path.join(root,'transplant/assets',name),'utf8');
 assert(!/localStorage|sessionStorage|indexedDB|\bfetch\s*\(|XMLHttpRequest|sendBeacon|\.submit\s*\(/.test(js),name);
 assert(!/Open electronic assessment|recording-kit|download JSON|Research data kit/.test(js),name);
}
const retired=path.join(root,'transplant/recording-templates');
assert(!fs.readdirSync(retired).some(f=>/\.(zip|js|css|md)$/.test(f)));
for(const key of Object.keys(D.assistants)){
 const [p,s]=key.split('/');const html=fs.readFileSync(path.join(retired,`${p}--${s}.html`),'utf8');
 assert(html.includes(`content="0;url=/mh-liver-pathways/transplant/${p}/#${s}"`),key);
 assert(!html.includes('<form'),key);
}
console.log(`PASS: all 46 decisions; ${combinations} categorical states; explicit clinical boundary/exclusion scenarios; unknown and missing findings cannot proceed; source links and redirects; no record collection/storage/export.`);
