/* Approved 24 November presentation ownership: existing clinical rules remain authoritative. */
const fs=require('node:fs'),path=require('node:path'),vm=require('node:vm'),assert=require('node:assert/strict');
const R=path.resolve(__dirname,'..'),read=p=>fs.readFileSync(path.join(R,p),'utf8');
const box={window:{}};vm.runInNewContext(read('assets/clarity-presentation.js'),box);const P=box.window.ClarityPresentation;
const D=JSON.parse(read('transplant/assets/content.json')),Risk=require('../transplant/assets/risk-routing.js');
const anchors=new Set();let placements=0;
for(const [key,links] of Object.entries(P.riskLinks)){
 const [slug,step,branch]=key.split('/'),p=D.index.find(p=>p.slug===slug),s=p.steps.find(s=>s.id===step),config=D.assistants[slug+'/'+step];assert(s,key);
 if(branch[0]==='b')assert(s.branches[+branch.slice(1)],key);else assert.equal(config.rules[+branch.slice(1)].branch,null,key);
 for(const anchor of links){assert(D.high_risk.pathways[slug].reviews.some(r=>r.anchor===anchor),key+anchor);assert(Risk.coverage[anchor].includes(step),key+anchor);anchors.add(anchor);placements++;}
}
assert.equal(anchors.size,25);assert(!anchors.has('hcc-b4'),'Research model must not become a clinical next step');
const tw=read('assets/transplant-workspace.js');assert(!tw.includes('function highRiskGroup('),'No generic repeated risk stack');assert(tw.includes('Sources for these criteria'));assert(!tw.includes('Evidence & sources for this decision'));assert(tw.includes("config.questions.some(q=>q.id==='phase')"));assert(tw.includes("ruleIndex===3) list=[{step:'diagnosis'"));assert(tw.includes("decision.dataset.workspaceKey==='hcc/listing'"));
const app=read('transplant/assets/app.js');assert(app.includes("history.pushState({riskOrigin:origin}"));assert(app.includes('if(chosen)return'));assert(app.includes("view='meeting';renderView();document.getElementById(issue.dataset.issue)"));
const libraries=read('evidence-libraries/library.js');assert(libraries.includes('policy_records.filter'));assert(libraries.includes('Cited in:'));assert(libraries.includes('share'));assert(!read('tools/build_share_site.py').includes("if f == 'evidence-libraries/library.js': s=share_library_script()"));
for(const [key,entries] of Object.entries(P.recommendationRoles)){
 const [slug,id]=key.split('/'),g=JSON.parse(read(slug+'/data/pathway.json')).gates.find(g=>g.id===id);for(const e of Object.keys(entries)){const [group,n]=e.split('/');assert(g[group][+n],key+'/'+e);}
}
console.log(`PASS: ${placements} condition-linked review placements; 25 clinical reviews plus a separate research reference; preserved outcome identities; focused question links; one clinical evidence renderer.`);
