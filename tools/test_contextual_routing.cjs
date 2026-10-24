/* Clinical routing regressions: proposed reviews, closed limits, context and reset. */
const assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path');
const root=path.resolve(__dirname,'..');
const D=JSON.parse(fs.readFileSync(path.join(root,'transplant/assets/content.json'),'utf8'));
const R=require(path.join(root,'transplant/assets/risk-routing.js'));
const A=require(path.join(root,'transplant/assets/assistant.js'));
const actionable=o=>['review','safety','readiness'].includes(o.mode);
let cases=0;const seen=new Set();
function fixture(key,answers={},extra={},previous={},priorExtra={}){
 const [slug,step]=key.split('/'),p=D.index.find(p=>p.slug===slug),i=p.steps.findIndex(s=>s.id===step);
 const session=A.createSession(p,D.assistants);
 Object.assign(session.answers[key],answers);
 for(const [k,v] of Object.entries(previous))Object.assign(session.answers[slug+'/'+k],v);
 const context={[key]:extra};for(const [k,v] of Object.entries(priorExtra))context[slug+'/'+k]=v;
 return {p,i,session,context,result:R.evaluate(p,i,session,context,D.assistants)};
}
function has(f,anchor,mode){cases++;const o=f.result.options.find(o=>o.anchor===anchor);assert(o,anchor+': '+JSON.stringify(f.result));if(mode)assert.equal(o.mode,mode,anchor);seen.add(anchor);return f;}
function noAction(f){cases++;assert(!f.result.options.some(actionable),JSON.stringify(f.result));return f;}
function absent(f,anchor){cases++;assert(!f.result.options.some(o=>o.anchor===anchor),anchor);return f;}
const hb=has(fixture('hcc/allocation',{burden:'beyond'}),'hcc-b1','review');
noAction(fixture('hcc/allocation',{burden:'beyond',spread:'unknown'}));
noAction(fixture('hcc/allocation',{burden:'beyond',spread:'no'}));
noAction(fixture('hcc/allocation',{burden:'beyond',afp:'not-met'}));
absent(fixture('hcc/allocation',{afp:'not-met'}),'hcc-b1');
has(fixture('hcc/curative-route',{spread:'prior'},{history:'vp12'}),'hcc-b2','review');
for(const history of ['vp3','vp4','rupture','both'])noAction(has(fixture('hcc/curative-route',{spread:'prior'},{history}),'hcc-b2','closed'));
for(const ici of ['planned','current','prior'])has(fixture('hcc/treatment',{}, {ici}),'hcc-b3','safety');
noAction(fixture('hcc/treatment',{response:'spread'},{ici:'prior'}));
noAction(fixture('hcc/treatment',{}, {ici:'unknown'}));
noAction(fixture('hcc/waitlist',{control:'lost'},{loss:'spread',ici:'prior'}));
const combined=fixture('hcc/allocation',{burden:'beyond'},{},{'curative-route':{spread:'prior'}},{'curative-route':{history:'vp12'}});
noAction(combined);assert(combined.result.guard.why.includes('cannot be combined'));
const excludedCombined=fixture('hcc/allocation',{burden:'beyond',spread:'no'},{},{'curative-route':{spread:'prior'}},{'curative-route':{history:'vp12'}});
assert(excludedCombined.result.guard.why.includes('active invasion'),'Clinical exclusion must precede study-combination note');
const carried=has(fixture('hcc/treatment',{}, {},{allocation:{burden:'beyond'}}),'hcc-b1','review');
assert(carried.result.options[0].carried&&carried.result.route);
noAction(has(fixture('hcc/treatment',{}, {ici:'prior'},{allocation:{spread:'unknown'}}),'hcc-b3','safety-note'));
noAction(fixture('hcc/listing',{}, {ici:'prior'},{'curative-route':{spread:'excluded'}}));
// Current and previous pCCA findings never activate closed expansions.
has(fixture('pcca/diagnosis',{biopsy:'yes'}),'pcca-b1','closed');
has(fixture('pcca/phenotype',{size:'large'},{mass_pattern:'single-large'}),'pcca-b1','closed');
absent(fixture('pcca/phenotype',{size:'large'},{mass_pattern:'multiple'}),'pcca-b1');
has(fixture('pcca/phenotype',{unresectable:'no'}),'pcca-b2','checklist');
has(fixture('pcca/neoadjuvant',{protocol:'no'},{regimen:'alternative'}),'pcca-b3','closed');
absent(fixture('pcca/neoadjuvant',{protocol:'no',status:'complication'},{regimen:'incomplete'}),'pcca-b3');
has(fixture('pcca/staging',{}, {nodes:'positive'}),'pcca-b1','closed');
noAction(fixture('pcca/staging',{}, {nodes:'suspicious'}));
assert(fixture('pcca/listing',{}, {},{diagnosis:{biopsy:'yes'}}).result.guard);
// Resectability, focality, histology and metastatic spread are distinct.
const ip={profile:'outside'},ix={outside:'larger',grade:'g12'};
has(fixture('icca/phenotype',ip,ix),'icca-b1','review');
absent(fixture('icca/phenotype',ip,{outside:'resectable',grade:'g12'}),'icca-b1');
has(fixture('icca/phenotype',{focality:'multiple'},{focality:'satellites',grade:'g12'}),'icca-b1','review');
noAction(fixture('icca/phenotype',{focality:'multiple'},{focality:'separate',grade:'g12'}));
noAction(fixture('icca/phenotype',{...ip,spread:'no'},ix));
noAction(fixture('icca/phenotype',ip,ix,{diagnosis:{histology:'mixed'}}));
assert.equal(fixture('icca/phenotype',{}, {},{diagnosis:{histology:'mixed'}}).result.guard,null,'Mixed small-cirrhotic route must remain');
noAction(fixture('icca/phenotype',ip,{outside:'larger',grade:'unknown'}));
has(fixture('icca/therapy',{control:'progression'},{study_context:'advanced',progression:'first-liver'}),'icca-b2','notice');
absent(fixture('icca/therapy',{control:'progression'},{study_context:'standard',progression:'first-liver'}),'icca-b2');
noAction(fixture('icca/therapy',{control:'progression'},{study_context:'advanced',progression:'spread'}));
noAction(fixture('icca/therapy',{control:'progression'},{study_context:'advanced',progression:'repeat-liver'}));
absent(fixture('icca/stability',{duration:'short'}),'icca-b2');
has(fixture('icca/stability',{duration:'short'}, {},{phenotype:ip},{phenotype:ix}),'icca-b2','checklist');
has(fixture('icca/review',{}, {donor:'yes'}),'icca-b3','readiness');
noAction(fixture('icca/review',{}, {donor:'yes'},{phenotype:{focality:'multiple'}},{phenotype:{focality:'separate',grade:'g12'}}));
noAction(fixture('icca/review',{}, {donor:'yes'},{phenotype:ip},{phenotype:{outside:'resectable',grade:'g12'}}));
// CRLM distinguishes viable disease, scars, NED and liver failure.
has(fixture('crlm/unresectability'),'crlm-b1','checklist');
has(fixture('crlm/unresectability',{clearance:'uncertain'},{visible:'residual'}),'crlm-b1','checklist');
has(fixture('crlm/unresectability',{clearance:'uncertain'},{visible:'ned'}),'crlm-b2','closed');
const scars=has(fixture('crlm/restaging',{}, {visible:'uncertain'}),'crlm-b2','notice');assert(scars.result.clarify.length);
has(fixture('crlm/control',{}, {visible:'failure'}),'crlm-b2','notice');
for(const molecular of ['braf','msi','both'])has(fixture('crlm/biology',{molecular:'outside'},{molecular}),'crlm-b3','closed');
has(fixture('crlm/clocks',{interval:'no'}),'crlm-b3','checklist');
has(fixture('crlm/review'),'crlm-b4','checklist');
absent(fixture('crlm/transplant',{plan:'no'}),'crlm-b4');
// NET benefit, grade uncertainty, cleared versus excluded sites, age and burden.
has(fixture('nelm/options',{}, {benefit:'symptoms'}),'net-b1','checklist');
has(fixture('nelm/distribution',{spread:'cleared'}),'net-b2','checklist');
has(fixture('nelm/biology',{grade:'outside'},{grade_detail:'g3'}),'net-b2','closed');
const discordant=fixture('nelm/biology',{grade:'outside'},{grade_detail:'discordant'});noAction(discordant);assert(discordant.result.clarify.length);assert(!discordant.result.options.some(o=>o.mode==='closed'));
has(fixture('nelm/observation',{clearance:'short'}),'net-b2','checklist');
has(fixture('nelm/options',{}, {age:'older',burden:'reference'}),'net-b3','checklist');
has(fixture('nelm/review',{}, {burden:'expansion'}),'net-b3','closed');
has(fixture('nelm/review',{}, {burden:'above'}),'net-b3','closed');
// HEHE-specific interpretation and HCA clinical benefit remain distinct.
has(fixture('hehe/risk',{}, {tempo:'urgent'}),'hehe-b1','checklist');
has(fixture('hehe/stage',{extrahepatic:'limited'}),'hehe-b2','closed');
assert.equal(fixture('hehe/stage',{extrahepatic:'limited'}).result.guard,null,'Local EHD exclusion must not become a universal clinical block');
has(fixture('hca/exception-route',{route:'none'}),'hca-b1','notice');
has(fixture('hca/standard-care'),'hca-b2','checklist');
noAction(fixture('hca/standard-care',{bleeding:'yes'}));
// Reconciliation regressions: final acceptance, individual routes and completed safety review.
assert(fixture('crlm/transplant',{}, {},{biology:{molecular:'outside'}},{biology:{molecular:'braf'}}).result.guard);
assert(fixture('icca/follow-up',{}, {},{phenotype:ip},{phenotype:ix}).result.route);
assert(fixture('hcc/allocation',{}, {},{'curative-route':{spread:'prior'}},{'curative-route':{history:'vp12'}}).result.route);
assert(fixture('icca/therapy',{}, {},{phenotype:ip},{phenotype:ix}).result.route);
assert(fixture('hcc/treatment',{}, {burden_history:'beyond'}).result.route);
assert.equal(fixture('nelm/review',{}, {burden:'expansion'}).result.guard,null);
assert.equal(fixture('hehe/review',{}, {},{stage:{extrahepatic:'limited'}}).result.guard,null);
assert(fixture('hcc/listing',{}, {},{'curative-route':{spread:'prior'}},{'curative-route':{history:'rupture'}}).result.route);
const safetyDone=fixture('hcc/listing',{}, {ici:'prior',ici_review:'complete'});
assert.equal(safetyDone.result.guard,null);has(safetyDone,'hcc-b3','safety-note');
assert.equal(fixture('hcc/waitlist',{}, {},{},{listing:{ici:'prior',ici_review:'complete'}}).result.guard,null);
assert(fixture('crlm/review',{}, {},{biology:{cea:'high'}}).result.route);
assert(fixture('crlm/transplant',{}, {},{biology:{cea:'high'}}).result.route);
assert(fixture('hehe/review',{}, {},{stage:{vascular:'no'}}).result.guard);
assert(fixture('hca/follow-up',{}, {},{'exception-route':{route:'none'}}).result.route);
assert(fixture('icca/follow-up',{}, {},{therapy:{control:'progression'}},{therapy:{study_context:'advanced',progression:'repeat-liver'}}).result.route);
assert(fixture('hcc/treatment',{}, {burden_history:'beyond'}).result.guard.why.includes('conflicting'));
// All 46 example paths and categorical states, including missing/unknown values.
let states=0;
for(const p of D.index)for(const [i,s] of p.steps.entries()){
 const key=p.slug+'/'+s.id,f=fixture(key);noAction(f);
 const config=D.assistants[key];
 function visit(n,a){
  if(n<config.questions.length){const q=config.questions[n];for(const value of ['',...q.options.map(o=>o.value)])visit(n+1,{...a,[q.id]:value});return;}
  states++;const f=fixture(key,a),r=f.result;
  for(const o of r.options){assert(D.high_risk.pathways[p.slug].reviews.some(v=>v.anchor===o.anchor),key);assert(R.coverage[o.anchor].includes(s.id),key);}
  if(config.questions.some(q=>!a[q.id]||a[q.id]==='unknown'))assert(!r.options.some(actionable),key+JSON.stringify(a));
  assert(!r.options.some(o=>o.anchor==='hcc-b4'));
 }
 visit(0,{});
}
const all=new Set(Object.values(D.high_risk.pathways).flatMap(p=>p.reviews.map(r=>r.anchor)));
assert.deepEqual(new Set([...seen,...R.referenceOnly]),all,'Every review must have a tested clinical trigger or explicit research-only status');
// Upstream edits invalidate later facts and additional context; navigation does not refill.
const reset=fixture('hcc/treatment',{}, {ici:'prior'},{allocation:{burden:'beyond'}});
A.changeAnswer(reset.session,reset.p,reset.p.steps.findIndex(s=>s.id==='allocation'),'burden','t2');
R.clearFrom(reset.context,reset.p,reset.p.steps.findIndex(s=>s.id==='allocation'));
assert.deepEqual(reset.context,{});
assert.deepEqual(reset.session.answers['hcc/treatment'],{});
assert(!R.evaluate(reset.p,reset.i,reset.session,reset.context,D.assistants).options.some(actionable));
const js=fs.readFileSync(path.join(root,'transplant/assets/app.js'),'utf8');
assert(!js.includes('HighRisk.inline(')&&!js.includes('HighRisk.prompt('),'Unconditional inserts must stay removed');
assert(js.includes('risk-next-options')&&js.includes('renderActions(onward.clarify)'));
assert(!/localStorage|sessionStorage|indexedDB|\bfetch\s*\(/.test(fs.readFileSync(path.join(root,'transplant/assets/risk-routing.js'),'utf8')));
console.log(`PASS: ${cases} targeted assertions; ${states} categorical states across all 46 decisions; 20 clinical review triggers and HCC-B4 reference-only; unknown/excluded/composite findings, prior context and reset.`);
