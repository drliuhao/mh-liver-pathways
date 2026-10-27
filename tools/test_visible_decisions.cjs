/* Regression coverage for visible decision maps and intact treatment-detail content. */
const fs=require('node:fs'),path=require('node:path'),vm=require('node:vm'),assert=require('node:assert/strict');
const root=path.resolve(__dirname,'..'),read=f=>fs.readFileSync(path.join(root,f),'utf8');
const data=JSON.parse(read('transplant/assets/content.json')),app=read('transplant/assets/app.js');
const render=app.slice(app.indexOf('function renderOverview()'),app.indexOf('function renderNavigation()'));
let total=0;
for(const active of data.index){
 const ctx={DATA:data,active,stepIndex:0,e:s=>String(s),exampleStatus:()=>['Status','Description']};vm.createContext(ctx);vm.runInContext(render,ctx);
 const html=ctx.renderOverview();assert(!html.includes('<details'),'Clinical overview cannot fold');
 for(const s of active.steps){assert.equal(html.split(`data-step="${s.id}"`).length-1,1,'Each decision has one overview entry');assert(html.includes(s.title));total++;}
 assert.equal((html.match(/aria-current="step"/g)||[]).length,1);
}
assert.equal(total,46);
assert(!read('assets/compact-trail.js').includes("querySelector('.journey-map')"),'Compact trail cannot fold the clinical overview');
const hcc=read('hcc/index.html');assert(hcc.includes('<div id="topicsBody">'));assert(!hcc.includes('data-fold="topicsBody"'));
const flow=read('assets/roadmap-flow.js');assert(!flow.includes('rf-background-reference'),'No hidden clinical chart wrapper');assert(!flow.includes("createElement('details');overview"));
const expected=[];
for(const slug of Object.keys(JSON.parse(read('assets/roadmap-links.json')))){
 let stages;
 if(slug==='hcc')stages=vm.runInNewContext(hcc.slice(hcc.indexOf('const STAGES = ['),hcc.indexOf('/* the quantifier'))+';STAGES');
 else stages=JSON.parse(read(slug+'/data/pathway.json')).gates;
 for(const s of stages){
  const records=[...s.standard,...s.alt,...s.avoid].flatMap(r=>r.opts||[r]);
  expected.push({slug,id:s.id,indications:records.filter(r=>r.pref).map(r=>r.pref),cautions:records.filter(r=>r.avoid).map(r=>r.avoid),refs:records.flatMap(r=>r.refs||[]).map(String),pairCount:records.filter(r=>r.pref||r.avoid).length});
 }
}
fs.writeFileSync('/tmp/visible-decision-expected.json',JSON.stringify(expected));
for(const f of ['assets/contextual-info.js','assets/roadmap-flow.js','transplant/assets/app.js'])new vm.Script(read(f),{filename:f});
console.log(`PASS: all ${total} transplant decision labels visible, HCC clinical sections cannot fold; exact treatment criteria and citation expectations generated for ${expected.length} roadmap topics.`);
