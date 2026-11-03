/* Analyst A audit regressions. Expectations follow source rules and saved B08 reproductions. */
'use strict';
const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict'),vm=require('node:vm');
const root=path.resolve(__dirname,'..'),D=JSON.parse(fs.readFileSync(path.join(root,'transplant/assets/content.json'),'utf8'));
const A=require('../transplant/assets/assistant.js'),R=require('../transplant/assets/risk-routing.js');
global.window={ClinicalReference:require('../assets/clinical-reference.js')};const C=require('../assets/clinical-scores.js').calculators;
const purePost=new Set(['hcc/after-transplant','pcca/follow-up']);let inheritedStops=0,missing=0,phases=0;
for(const p of D.index)for(let i=0;i<p.steps.length;i++){
 const key=p.slug+'/'+p.steps[i].id,config=D.assistants[key];
 for(const rule of config.rules){
  const s=A.createSession(p,D.assistants);for(const [q,v] of Object.entries(rule.when))s.answers[key][q]=Array.isArray(v)?v[0]:v;
  const core=A.evaluate(config,s.answers[key],p.steps[i].branches);
  if(core.kind!=='stop')continue;
  for(let j=i+1;j<p.steps.length;j++){
   if(purePost.has(p.slug+'/'+p.steps[j].id))continue;
   assert(R.evaluate(p,j,s,{},D.assistants).guard,key+' stop disappears at '+p.steps[j].id);inheritedStops++;
  }
 }
 for(let j=i+1;j<p.steps.length;j++){
  if(purePost.has(p.slug+'/'+p.steps[j].id))continue;
  const s=A.createSession(p,D.assistants);s.answers[key]={};
  assert(R.evaluate(p,j,s,{},D.assistants).guard,key+' blank disappears at '+p.steps[j].id);missing++;
 }
}
for(const [slug,last,origin,bad] of [['icca','follow-up','phenotype',{spread:'no'}],['crlm','transplant','biology',{molecular:'outside'}],['nelm','follow-up','distribution',{spread:'solid'}],['hehe','follow-up','stage',{vascular:'no'}],['hca','follow-up','standard-care',{bleeding:'yes'}]]){
 const p=D.index.find(p=>p.slug===slug),i=p.steps.findIndex(s=>s.id===last),key=slug+'/'+last,s=A.createSession(p,D.assistants);
 Object.assign(s.answers[slug+'/'+origin],bad);assert(R.evaluate(p,i,s,{},D.assistants).guard);
 s.answers[key]={phase:'after',plan:'yes',concern:'none'};
 const r=R.evaluate(p,i,s,{},D.assistants);assert.equal(r.guard,null);assert.equal(r.route,null);assert.equal(r.postTransplant,true);
 const core=A.evaluate(D.assistants[key],s.answers[key],p.steps[i].branches);assert.equal(core.title,'Continue recipient follow-up');assert(!core.text.includes('Proceed to transplantation'));
 s.answers[key].concern='concern';const concern=A.evaluate(D.assistants[key],s.answers[key],p.steps[i].branches);
 assert.equal(D.continuations[key].rules[concern.ruleIndex][0].care,'post-transplant-recurrence');phases++;
}
// Decimal-representation error may not reject exact 8 cm; genuinely larger burden must fail.
function perms(a){if(a.length<2)return[a];return a.flatMap((x,i)=>perms(a.filter((_,j)=>i!==j)).map(r=>[x,...r]));}
for(const sizes of perms([3.2,2.3,2.5]))assert.equal(C.hccBurden({sizes,spread:false}).downstaging,true);
for(const sizes of [[3.2,2.3,2.5001],[3,2,2,1],[0.7,2,2]]){
 const r=C.hccBurden({sizes,spread:false});if(sizes[0]===0.7)assert.equal(r.ok,false);else assert.equal(r.downstaging,false);
}
assert.equal(C.metroticket({number:1,largest:0.9,afp:50}).ok,false);
// Canonical source snapshots must not regenerate the old clinical definitions or omit review code.
for(const name of ['app.js','risk-routing.js','assistant.js','high-risk.js'])assert.equal(fs.readFileSync(path.join(root,'tools/decision_assistant_source',name),'utf8'),fs.readFileSync(path.join(root,'transplant/assets',name),'utf8'));
assert.deepEqual(JSON.parse(fs.readFileSync(path.join(root,'tools/decision_assistant_source/high_risk_data.json'),'utf8')),D.high_risk);
assert.deepEqual(JSON.parse(fs.readFileSync(path.join(root,'tools/v12_content_snapshot.json'),'utf8')),D);
for(const p of D.index){const html=fs.readFileSync(path.join(root,'transplant',p.slug,'index.html'),'utf8'),embedded=JSON.parse(html.match(/<script[^>]+id="protocol-data"[^>]*>([\s\S]*?)<\/script>/)[1]);assert.deepEqual(embedded.assistants,D.assistants);assert.deepEqual(embedded.continuations,D.continuations);assert.deepEqual(embedded.care,D.care);assert.deepEqual(embedded.high_risk,D.high_risk);}
const revisions=require('./apply_clinical_revisions.cjs'),cp=require('node:child_process');
for(const file of ['transplant/assets/app.js','transplant/assets/risk-routing.js','assets/transplant-workspace.js','assets/clinical-scores.js','tools/decision_assistant_source/app.js','tools/decision_assistant_source/risk-routing.js','tools/decision_assistant_source/high-risk.js','tools/decision_assistant_source/high_risk_data.json','tools/decision_assistant_source/build.py']){
 const base=cp.execFileSync('git',['show','30039fe0cec15a29ac2f326e0ee316eaf6bfb48e:'+file],{cwd:root,encoding:'utf8',maxBuffer:8e6});
 assert.equal(fs.readFileSync(path.join(root,file),'utf8'),revisions.applyText(file,base,revisions.revisions().filter(r=>r.id >= '2026-11-02')),file+' exact reviewed-baseline replay');
}
console.log(`PASS: ${inheritedStops} upstream-stop carry checks, ${missing} skipped-decision holds, ${phases} explicit recipient contexts, exact decimal boundaries, source/runtime and all embedded payloads.`);
