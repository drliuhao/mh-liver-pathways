/* A presentation edit must preserve V12 data, thresholds and clinical action logic. */
const fs=require('node:fs'),cp=require('node:child_process'),vm=require('node:vm'),assert=require('node:assert/strict'),path=require('node:path');
const root=path.resolve(__dirname,'..'),read=f=>fs.readFileSync(path.join(root,f),'utf8');
const original=f=>cp.execFileSync('git',['show','a787e08:'+f],{cwd:root,encoding:'utf8',maxBuffer:8e6});
for(const file of ['transplant/assets/content.json','tools/v12_content_snapshot.json','transplant/assets/assistant.js','transplant/assets/risk-routing.js','transplant/assets/high-risk.js','assets/roadmap-links.json'])assert.equal(read(file),original(file),file+' changed clinical content');
const src=read('assets/contextual-info.js');const start=src.indexOf(' const criticalHelp='),end=src.indexOf('\n function note(',start);
const map=vm.runInNewContext(src.slice(start,end)+';criticalHelp;');
const data=JSON.parse(read('transplant/assets/content.json'));let reviewed=0,flags=[];
for(const [key,suffix] of Object.entries(map)){
 const [slug,step,id]=key.split('/');const q=data.assistants[slug+'/'+step].questions.find(q=>q.id===id);
 assert(q?.help.endsWith(suffix),key+' does not match its exact source');reviewed++;
 if(/[\d≤≥<>]|must|only|not|never|exclude|contraindicat|hold|stop/i.test(suffix))flags.push(key);
}
assert.equal(reviewed,8);
for(const key of ['hcc/allocation/afp','hcc/treatment/afp','pcca/diagnosis/biopsy','pcca/phenotype/size','crlm/biology/cea','icca/phenotype/focality'])assert(!map[key],'Critical selection help moved: '+key);
assert(src.includes("if(!d.open)enhance(d)"),'Selected threshold definitions must remain visible');
const app=read('transplant/assets/app.js'),old=original('transplant/assets/app.js');
for(const [a,b] of [['function renderActions(', 'function renderRiskReference('],['function renderStep()', 'function renderMeeting()']]){
 const slice=s=>s.slice(s.indexOf(a),s.indexOf(b,s.indexOf(a)));assert.equal(slice(app),slice(old),'Changed clinical action renderer '+a);
}
const docs=Object.keys(JSON.parse(read('assets/roadmap-links.json'))).map(x=>x+'/index.html').concat(data.index.map(p=>'transplant/'+p.slug+'/index.html'));
for(const doc of docs)assert(read(doc).includes('portal-navigation.js?v=20261025-contextual'),doc+' missing display update');
console.log(`PASS: V12 data and clinical renderers unchanged; ${docs.length} active pages load shared UI; ${reviewed} exact explanatory suffixes verified.`);
console.log('Manually reviewed lint flags (allocation explanation, repeated review disclaimer, and explant context): '+flags.join(', '));
