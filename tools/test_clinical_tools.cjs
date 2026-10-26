const assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path');
const root=path.resolve(__dirname,'..'),R=require('../assets/clinical-reference.js'),routing=require('../transplant/assets/risk-routing.js');
const read=f=>fs.readFileSync(path.join(root,f),'utf8');
const base={ageGroup:'adult',sex:'male',dialysis:'no',bilirubin:1,inr:1,creatinine:1,sodium:137,albumin:3.5};
assert.equal(R.calculateMeld(base).score,6);
assert.equal(R.calculateMeld({...base,sex:'female'}).score,7);
assert.equal(R.calculateMeld({...base,ageGroup:'registered-under18',sex:''}).score,7);
assert.equal(R.calculateMeld({...base,ageGroup:'under12'}).ok,false);
for(const key of Object.keys(base))assert.equal(R.calculateMeld({...base,[key]:''}).ok,false,'Required input: '+key);
for(const key of ['bilirubin','inr','creatinine','sodium','albumin'])for(const v of [-1,0,NaN,Infinity,'abc',null,undefined])assert.equal(R.calculateMeld({...base,[key]:v}).ok,false,'Invalid '+key+' '+v);
const mild={...base,bilirubin:2.5,inr:1.5,creatinine:1.2,sodium:132,albumin:2.8};
assert.equal(R.calculateMeld(mild).score,20);assert.equal(R.calculateMeld({...mild,sex:'female'}).score,21);
assert.equal(R.calculateMeld({...mild,sex:'female',dialysis:'yes'}).score,30);
assert.equal(R.calculateMeld({...mild,ageGroup:'registered-under18',sex:''}).score,21);
const bounded=R.calculateMeld({...base,bilirubin:0.2,inr:0.8,creatinine:0.4,sodium:150,albumin:4.5});
assert.deepEqual(bounded.inputs,{bilirubin:1,inr:1,creatinine:1,sodium:137,albumin:3.5});assert.equal(bounded.adjustments.length,5);
const low=R.calculateMeld({...base,creatinine:4,sodium:110,albumin:0.8});assert.deepEqual(low.inputs,{bilirubin:1,inr:1,creatinine:3,sodium:125,albumin:1.5});
assert.equal(R.calculateMeld({...mild,creatinine:3}).score,R.calculateMeld({...mild,dialysis:'yes',creatinine:''}).score);
assert.equal(R.calculateMeld({...base,bilirubin:50,inr:8,creatinine:4,sodium:120,albumin:1}).score,40);
for(const ageGroup of ['adult','registered-under18'])for(const sex of ['male','female'])for(const dialysis of ['yes','no'])for(const bilirubin of [.2,1,3,20])for(const sodium of [124,125,132,137,145]){
 const x=R.calculateMeld({...mild,ageGroup,sex,dialysis,bilirubin,sodium});assert(x.ok&&x.score>=6&&x.score<=40&&Number.isInteger(x.score));
}
let count=0,refs=0;
const data=JSON.parse(read('transplant/assets/content.json'));
for(const p of data.index){
 const d=JSON.parse(read('transplant/'+p.slug+'/index.html').match(/id="protocol-data"[^>]*>([\s\S]*?)<\/script>/)[1]);
 for(const step of d.pathway.steps){
  const config=d.assistants[p.slug+'/'+step.id],html=R.renderPreview(d,step.id);count++;
  assert(html.includes(R.esc(step.question)));assert(!/<(?:select|input)\b|data-(?:step|care|record-finding|assistant-question)=/.test(html),'Preview must be read-only');
  for(const q of config.questions){assert(html.includes(R.esc(q.label)));for(const o of q.options)assert(html.includes(R.esc(o.label)));for(const c of q.criteria)for(const x of c.items)assert(html.includes(R.esc(x)));}
  for(const id of R.collectRefs([step,config])){assert(d.sources[id],id);assert(html.includes(R.esc(d.sources[id].url)),p.slug+'/'+step.id+': '+id);refs++;}
  assert(html.includes('Full checklist and sources'));assert(html.includes('Source details'));assert(!/<details\b/.test(html),'Preview content must start open');
 }
}
assert.equal(count,46);
const ui=read('assets/clinical-tools.js');assert(ui.includes('ev.stopImmediatePropagation()'));assert(ui.includes("d.open=true"));assert(!/localStorage|sessionStorage|fetch\(|XMLHttpRequest|sendBeacon|changeStagedAnswer|recordRiskFinding/.test(ui));
assert(ui.includes("form.addEventListener('input',clearResult)"),'Stale score must clear when inputs change');
assert(ui.includes("dialog.replaceChildren()"),'Closing clears calculator inputs');
assert(ui.includes('sourceOrigin(origin)'),'Calculator closes any originating explanation');
console.log(`PASS: MELD required inputs, age/sex, dialysis, bounds, invalid values and 320 combinations; ${count} read-only previews with ${refs} source placements.`);
