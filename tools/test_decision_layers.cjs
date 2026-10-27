/* Staging is an interface constraint, not a new clinical matcher. */
const fs=require('node:fs'),assert=require('node:assert/strict'),cp=require('node:child_process'),path=require('node:path');
const root=path.resolve(__dirname,'..'),read=f=>fs.readFileSync(path.join(root,f),'utf8');
const A=require('../transplant/assets/assistant.js'),D=JSON.parse(read('transplant/assets/content.json'));
const old=cp.execFileSync('git',['show','5739274:transplant/assets/assistant.js'],{cwd:root,encoding:'utf8'}),now=read('transplant/assets/assistant.js');
const section=(s,start,end)=>s.slice(s.indexOf(start),s.indexOf(end,s.indexOf(start)));
assert.equal(section(now,' function evaluate(', ' function definitions('),section(old,' function evaluate(', ' function definitions('),'Clinical matcher and source links unchanged');
let questions=0,rollbacks=0;
for(const p of D.index){
 const seeded=A.createStagedSession(p,D.assistants),first=p.slug+'/'+p.steps[0].id;
 assert.equal(Object.values(seeded.answers).flatMap(a=>Object.values(a)).length,1,'Only one entry example');
 assert.equal(seeded.answers[first][D.assistants[first].questions[0].id],D.assistants[first].example[D.assistants[first].questions[0].id]);
 assert.equal(Object.keys(seeded.presets[first]).length,1,'Entry example remains explicitly labeled');
 const session=A.createStagedSession(p,D.assistants,false);
 for(const [index,step]of p.steps.entries()){
  const key=p.slug+'/'+step.id,c=D.assistants[key];
  for(const [n,q]of c.questions.entries()){
   assert.equal(A.visibleQuestions(c,session.answers[key]).length,n+1,'One new unanswered question');
   assert.equal(session.answers[key][q.id],undefined,'New layer is not seeded');
   A.changeStagedAnswer(session,p,D.assistants,index,q.id,c.example[q.id]);questions++;
  }
  assert.equal(A.evaluate(c,session.answers[key],step.branches).kind,'advance',key+' curated core example');
 }
 for(const [index,step]of p.steps.entries())for(const [n,q]of D.assistants[p.slug+'/'+step.id].questions.entries()){
  const s=A.createSession(p,D.assistants),key=p.slug+'/'+step.id,c=D.assistants[key];
  assert.equal(A.changeStagedAnswer(s,p,D.assistants,index,q.id,c.example[q.id]),false);
  const alternative=q.options.find(o=>o.value!==c.example[q.id]).value;
  A.changeStagedAnswer(s,p,D.assistants,index,q.id,alternative);
  assert.equal(s.answers[key][q.id],alternative);
  c.questions.slice(0,n).forEach(prior=>assert.equal(s.answers[key][prior.id],c.example[prior.id]));
  c.questions.slice(n+1).forEach(later=>assert.equal(s.answers[key][later.id],undefined,'Later questions in same decision clear'));
  p.steps.slice(index+1).forEach(later=>assert.deepEqual(s.answers[p.slug+'/'+later.id],{},'Later decisions clear'));
  rollbacks++;
 }
 for(const step of p.steps){const key=p.slug+'/'+step.id,c=D.assistants[key];for(const q of c.questions){
  const html=A.definitions(q,c.example[q.id],D.sources);
  const rendered=A.render(c,D.sources,{},'empty');if(q.help)assert(rendered.includes('<p class="assistant-help"'),'Help remains visible, not inside a closed disclosure');
  const relevant=q.criteria.filter(x=>!x.show_for.length||x.show_for.includes(c.example[q.id]));
  if(relevant.length||q.options.find(o=>o.value===c.example[q.id])?.details?.length)assert(/<details[^>]*\sopen(?:\s|>)/.test(html),'Relevant definitions start open');
  q.criteria.forEach(c=>{assert(html.includes(c.title));c.items.forEach(item=>assert(html.includes(item.replaceAll('&','&amp;').replaceAll('<','&lt;').replaceAll('>','&gt;').replaceAll('"','&quot;').replaceAll("'",'&#39;'))));});
 }}
}
assert(!read('assets/contextual-info.js').includes("'.branch-details, #answer details.more, .care-evidence'"),'Criteria cannot become floating explanations');
assert(read('assets/contextual-info.js').includes("node.closest('.rf-cautions')"),'Standalone Avoid recommendations stay visible; option cautions use the requested peer disclosures');
assert(!/localStorage|sessionStorage|indexedDB|document\.cookie/.test(now+read('transplant/assets/app.js')));
console.log(`PASS: 7 single-entry presets; ${questions} blank successive layers; ${rollbacks} same-decision and downstream rollbacks; unchanged clinical matcher and sources; criteria stay inline.`);

const vm=require('node:vm'),app=read('transplant/assets/app.js');
const box={window:{ContextualCopy:{}},active:{slug:'icca',steps:[{id:'phenotype'}]},e:s=>String(s)};vm.createContext(box);
vm.runInContext(section(app,'function layerQuestionRow(', 'function renderLayerStack('),box);
const step={id:'phenotype',title:'Criteria'},q={id:'focality',label:'Distribution',options:[{value:'multiple',label:'Multiple lesions'}]};
const core=box.layerQuestionRow(step,q,'multiple',1),risk=box.layerQuestionRow(step,q,'multiple',2,false,true);
const ids=[...((core+risk).matchAll(/ id="([^"]+)"/g))].map(m=>m[1]);assert.equal(new Set(ids).size,ids.length,'Core and supplemental fields must have unique IDs');
assert(core.includes('data-layer-question="focality"'));assert(risk.includes('data-layer-risk="focality"')&&risk.includes('data-risk-criteria'));
console.log('PASS: core and supplemental focality questions have distinct controls and criteria targets.');
assert(core.includes('data-record-finding=')&&core.includes('disabled'),'An explicit confirmation commits findings');
assert(core.includes('data-cancel-finding=')&&core.includes('layer-stage-status'),'Unapplied selections have a status and cancel control');
assert(app.includes("select.value=select.dataset.committed;select.dispatchEvent(new Event('change',{bubbles:true}))"),'Cancel updates every inline criteria observer, not just the dropdown');
assert(app.includes('Criteria behind recorded findings'),'Selected threshold definitions remain visible alongside the next question');
assert(app.includes('createStagedSession(active,DATA.assistants,false)'),'Ordinary entry is unanswered');
assert(!app.includes('layer-next-action')&&!app.includes('data-layer-action'),'No redundant action selector');
assert(read('assets/roadmap-flow.js').includes('data-open-topic'),'Topic navigation requires an explicit Open action');
assert(!read('assets/roadmap-flow.js').includes('id="roadmap-next"'),'Conditional navigation is not duplicated in a dropdown');
console.log('PASS: explicit finding and topic confirmation; blank entry; no single-option or condition-free navigation dropdowns.');
