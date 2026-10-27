/* Build display metadata against the exact source topics. Clinical criteria are copied for guards only. */
const fs=require('node:fs'),path=require('node:path'),vm=require('node:vm'),assert=require('node:assert/strict');
const root=path.resolve(__dirname,'..'),read=f=>fs.readFileSync(path.join(root,f),'utf8');
const source=JSON.parse(read('tools/decision_workspace_source.json')),map=JSON.parse(read('assets/roadmap-links.json')),topics={};
for(const slug of Object.keys(map)){
 let stages;
 if(slug==='hcc'){const s=read('hcc/index.html'),a=s.indexOf('const STAGES = ['),b=s.indexOf('/* the quantifier',a);stages=JSON.parse(JSON.stringify(vm.runInNewContext(s.slice(a,b)+';STAGES')));}
 else stages=JSON.parse(read(slug+'/data/pathway.json')).gates;
 assert.deepEqual(Object.keys(source[slug]).sort(),stages.map(s=>s.id).sort(),slug+' display coverage');
 for(const s of stages){const [team,inputs,tools]=source[slug][s.id];topics[slug+'/'+s.id]={title:s.name,criteria:s.crit,team,inputs,tools};}
}
assert.equal(Object.keys(topics).length,103);
fs.writeFileSync(path.join(root,'assets/decision-workspace-data.js'),'/* Display summaries; original cutoffs, recommendations and evidence stay in the source topic. */\nwindow.DecisionWorkspaceData='+JSON.stringify({topics},null,2)+';\n');
console.log('Built source-guarded input/team/tool summaries for all 103 roadmap topics.');
