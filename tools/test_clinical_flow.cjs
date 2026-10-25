const fs=require('node:fs'),path=require('node:path'),vm=require('node:vm'),assert=require('node:assert/strict');
const root=path.resolve(__dirname,'..'),read=f=>fs.readFileSync(path.join(root,f),'utf8');
const src=read('transplant/assets/app.js'),data=JSON.parse(read('transplant/assets/content.json'));
for(const file of ['assets/clinical-flow.js','assets/portal-navigation.js','assets/contextual-info.js','assets/roadmap-flow.js','transplant/assets/app.js'])new vm.Script(read(file),{filename:file});
const helpers=src.slice(src.indexOf('// Navigation context is in memory only.'),src.indexOf('function renderStep()'));
const box={DATA:data,active:data.index.find(p=>p.slug==='hcc'),assistantSession:{answers:{},origins:{}},riskContext:{},careId:'local',view:'pathway',stepIndex:2,
 e:s=>String(s).replaceAll('&','&amp;').replaceAll('<','&lt;').replaceAll('>','&gt;').replaceAll('"','&quot;'),
 refs:ids=>ids.join('|'),renderActions:actions=>JSON.stringify(actions),renderView:()=>{},
 history:{pushState(){}},document:{getElementById:()=>({focus(){}}),querySelector:()=>({scrollIntoView(){}})}};
vm.createContext(box);vm.runInContext(helpers,box);
box.assistantSession.answers['hcc/allocation']={burden:'t2',afp:'no'};
box.riskContext['hcc/allocation']={b:'no',a:'yes'};
const before=box.careFingerprint('allocation');
box.assistantSession.answers['hcc/allocation']={afp:'no',burden:'t2'};
box.riskContext['hcc/allocation']={a:'yes',b:'no'};
assert.equal(box.careFingerprint('allocation'),before,'Answer insertion order must not mark a plan stale');
box.assistantSession.answers['hcc/allocation'].afp='yes';
assert.notEqual(box.careFingerprint('allocation'),before,'Changed finding must mark a plan stale');
vm.runInContext("captureCareOrigin=()=>({care:'local',step:'allocation',fingerprint:careFingerprint('allocation')});",box);
for(let i=0;i<40;i++)box.showCare({dataset:{care:'local'}});
assert.equal(vm.runInContext('careOrigins.size',box),24,'In-memory origin store is bounded');
assert(box.currentCareOrigin());box.clearCareOrigins();assert.equal(box.currentCareOrigin(),null);
assert(box.careOriginHTML().includes('Opened as a reference. No findings are attached'));
assert(src.includes('clearCareOrigins();'),'Choice clearing must remove origin data');
let plans=0,actions=0;
for(const p of data.index){box.active=p;for(const plan of data.care[p.slug]){
 const html=box.carePlanHTML(plan);assert(html.includes(box.e(plan.when)));
 for(const task of plan.tasks)assert(html.includes(box.e(task)));
 const reassess=plan.actions.filter(a=>a.step),other=plan.actions.filter(a=>!a.step);
 if(reassess.length)assert(html.includes(JSON.stringify(reassess)));
 if(other.length)assert(html.includes(JSON.stringify(other)));
 assert.equal(reassess.length+other.length,plan.actions.length);
 if(!reassess.length&&!plan.endpoint)assert(html.includes('Choose the next care plan'));
 if(plan.endpoint)assert(html.includes('Continuing care and review'));
 for(const id of plan.refs)assert(html.includes(box.e(data.sources[id].locator)));
 plans++;actions+=plan.actions.length;
}}
for(const asset of ['assets/clinical-flow.js','transplant/assets/app.js'])assert(!/localStorage|sessionStorage|document\.cookie|indexedDB/.test(read(asset)),'Findings must not persist');
const mirror=read('tools/decision_assistant_source/app.js').replaceAll('href="/','href="/mh-liver-pathways/transplant/').replace('The linked source supports the adjacent statement.','Access through the publisher or official source; institutional sign-in may be required. The linked source supports the adjacent statement.');
assert.equal(mirror,src,'Source mirror must reproduce the current public renderer');
const nav=read('assets/portal-navigation.js');for(const slug of Object.keys(JSON.parse(read('assets/roadmap-links.json'))))assert(nav.includes("'"+slug+"/'"),slug+' missing from navigation');
console.log(`PASS: ${plans} care plans and ${actions} actions preserved; canonical stale detection, clear/reference behavior, bounded origins, source mirror and all roadmap menu entries verified.`);
