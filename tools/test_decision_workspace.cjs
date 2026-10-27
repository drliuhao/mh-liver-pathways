/* Presentation coverage and source preservation, not a new clinical rule engine. */
const fs=require('node:fs'),path=require('node:path'),vm=require('node:vm'),assert=require('node:assert/strict');
const root=path.resolve(__dirname,'..'),read=f=>fs.readFileSync(path.join(root,f),'utf8'),context={window:{}};
vm.runInNewContext(read('assets/decision-workspace-data.js'),context);
const metadata=JSON.parse(JSON.stringify(context.window.DecisionWorkspaceData.topics)),map=JSON.parse(read('assets/roadmap-links.json'));
let count=0;
for(const slug of Object.keys(map)){
 let stages;
 if(slug==='hcc'){const s=read('hcc/index.html'),a=s.indexOf('const STAGES = ['),b=s.indexOf('/* the quantifier',a);stages=JSON.parse(JSON.stringify(vm.runInNewContext(s.slice(a,b)+';STAGES')));}
 else stages=JSON.parse(read(slug+'/data/pathway.json')).gates;
 for(const s of stages){
  const m=metadata[slug+'/'+s.id];assert(m);assert.equal(m.title,s.name);assert.deepEqual(m.criteria,s.crit);
  assert(m.inputs.length>=2&&m.inputs.length<=4);assert(m.team.split(' · ').length>=2);
  assert(m.tools.every(k=>['lr5','ecog','child','meld','lrt','systemic'].includes(k)));
  count++;
 }
}
assert.equal(count,103);assert.equal(Object.keys(metadata).length,count);
const clinical=JSON.parse(read('transplant/assets/content.json'));let decisions=0;
for(const p of clinical.index)for(const s of p.steps){
 assert(s.owner&&s.orders.length);assert(clinical.assistants[p.slug+'/'+s.id].questions.length);decisions++;
}
assert.equal(decisions,46);
const ui=read('assets/decision-workspace.js');
assert(ui.includes('middle.append(current,orders,result)'),'Original controls and results stay together');
assert(ui.includes('left.append(requiredFindings(config,protocol.pathway.slug+\'/\'+id),tests)'),'Original full checklist stays in input column');
assert(ui.includes('toolsColumn(step.owner'),'Protocol team is source-derived');
assert(ui.includes('JSON.stringify(actual)!==JSON.stringify(meta.criteria.map(plain))'),'Roadmap metadata fails closed when criteria change');
assert(ui.includes('previewLayout(content)'),'Read-ahead previews share the layout');
assert(ui.includes('supplementalInputs(n)'),'Applicable safety checks appear in input column');
assert(!/localStorage|sessionStorage|fetch\(|XMLHttpRequest|changeStagedAnswer|recordRiskFinding|dispatchEvent/.test(ui),'Presentation must not mutate findings or send patient data');
assert(read('assets/compact-trail.js').includes("!state.workspace.classList.contains('dw-ready')"),'Source layout must not fight the column layout');
assert(read('assets/decision-workspace.css').includes('@media(max-width:1099px)'));
for(const name of ['assets/decision-workspace.js','assets/decision-workspace-data.js','assets/portal-navigation.js'])new vm.Script(read(name),{filename:name});
console.log('PASS: 103 roadmap topics, 46 source-owned transplant decisions, exact criterion guards, original control/checklist placement, conditional checks and read-only tools.');
