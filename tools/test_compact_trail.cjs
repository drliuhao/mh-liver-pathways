/* Display aliases must cover the current source exactly; no clinical criteria are shortened. */
const fs=require('node:fs'),path=require('node:path'),vm=require('node:vm'),assert=require('node:assert/strict');
const root=path.resolve(__dirname,'..'),read=f=>fs.readFileSync(path.join(root,f),'utf8'),context={window:{}};
vm.runInNewContext(read('assets/compact-trail-labels.js'),context);const labels=context.window.CompactTrailLabels;
const data=JSON.parse(read('transplant/assets/content.json'));let count=0;
for(const [key,c] of Object.entries(data.assistants))for(const q of c.questions){
 const entry=labels.core[key+'/'+q.id];assert(entry,key+'/'+q.id);assert.equal(entry.source,q.label);assert(entry.label.length<=44);count++;
}
assert.equal(count,96);assert.equal(Object.keys(labels.core).length,count);
assert.equal(labels.core['hcc/allocation/burden'].label,'Tumor burden');
assert.equal(labels.core['hcc/allocation/afp'].label,'AFP');
assert.equal(labels.core['hcc/treatment/response'].label,'Tumor response');
assert.equal(labels.core['hcc/treatment/afp'].label,'AFP response');
assert.notEqual(labels.core['icca/phenotype/focality'].label,labels.riskById.focality.label,'Count and distribution remain distinct');
let risk=read('transplant/assets/risk-routing.js');risk=risk.slice(risk.indexOf('function questions('),risk.indexOf('function local('));
for(const [,id,source] of risk.matchAll(/add\('([^']+)','([^']+)'/g))assert.equal(labels.riskById[id].source,source,id);
let topics=0;
for(const slug of Object.keys(JSON.parse(read('assets/roadmap-links.json')))){
 let stages;
 if(slug==='hcc'){const s=read('hcc/index.html'),a=s.indexOf('const STAGES = ['),b=s.indexOf('/* the quantifier',a);stages=vm.runInNewContext(s.slice(a,b)+';STAGES');}
 else stages=JSON.parse(read(slug+'/data/pathway.json')).gates;
 for(const s of stages){const entry=labels.roadmaps[slug+'/'+s.id];assert(entry);assert.equal(entry.source,s.name.replace(/^\d+\s*·\s*/,''));assert(entry.label.length<=44);topics++;}
}
assert.equal(topics,103);
for(const f of ['assets/compact-trail.js','assets/compact-trail-labels.js','assets/portal-navigation.js'])new vm.Script(read(f),{filename:f});
console.log(`PASS: ${count} core labels, 23 supplemental labels, ${topics} topic labels match exact source questions; baseline and response remain distinct; shared scripts parse.`);
// A missing supplemental source must fail closed instead of invoking old navigation.
const js=read('assets/compact-trail.js'),fn=js.slice(js.indexOf(' function bindInlineCriteria('),js.indexOf(' function shortControl('));
const criteriaContext={slug:'hcc',protocol:{assistants:{}},riskSources:new Map()};vm.createContext(criteriaContext);vm.runInContext(fn,criteriaContext);
let disabledButton={disabled:false,attrs:{},setAttribute(k,v){this.attrs[k]=v;}};
criteriaContext.bindInlineCriteria({querySelector:()=>disabledButton},{select:{dataset:{layerStep:'allocation',layerRisk:'missing'}}});
assert.equal(disabledButton.disabled,true);assert(disabledButton.attrs['aria-label'].includes('All decisions'));
for(const [key,label]of Object.entries({'icca/5':'Unresectable, liver-confined','hilar/5':'Unresectable, outside protocol','crlm/5':'Disease control'}))assert.equal(labels.roadmaps[key].label,label);
assert.equal(labels.core['pcca/phenotype/diagnosis'].label,'Diagnosis / biopsy history');
assert.equal(labels.riskById.visible.label,'Treated-lesion interpretation');
assert.equal(labels.riskById.molecular.label,'Molecular result outside criteria');
console.log('PASS: missing editor criteria cannot fall through to navigation; reviewed qualifiers and non-verdict labels retained.');
assert(js.includes("historyEl.querySelectorAll('.layer-row')"),'Nested fallback history remains compatible');
assert(js.includes("select.value=select.dataset.committed;select.dispatchEvent"),'Closing an editor discards its unapplied draft');
assert(js.includes('Unapplied choice. Use Apply change'),'No false announcement that staging cleared findings');
assert(!js.includes('Choice changed. Later findings cleared'),'Staging is not clinical commitment');
assert(js.includes("location.hash.startsWith('#decision-')")&&js.includes(':select.value'),'Initial topic chip resolves without a hash');
assert(read('assets/compact-trail.css').includes('.compact-trail .layer-help{display:block'),'Active thresholds are not hidden by compact mode');
const closer=js.slice(js.indexOf(' function closeEditor('),js.indexOf(' function openEditor('));
let changed=0,focused=0;
const draft={value:'unapplied',dataset:{committed:'recorded'},dispatchEvent(){changed++;}};
const state={open:{focus(){focused++;}},editors:{hidden:false,querySelectorAll(s){return s==='select[data-committed]'?[draft]:[];}},current:{hidden:true},history:{querySelectorAll(){return [];}}};
const closeContext={Event:class Event{},state};vm.createContext(closeContext);vm.runInContext(closer+';closeEditor(state);',closeContext);
assert.equal(draft.value,'recorded');assert.equal(changed,1);assert.equal(focused,1);assert(state.editors.hidden&&!state.current.hidden);
console.log('PASS: compact integration retains explicit confirmation, cancel-on-close, visible threshold help and source topic labels.');
