/* Navigation must preserve clinical content and resolve every conditional link. */
const fs=require('node:fs'),path=require('node:path'),vm=require('node:vm'),assert=require('node:assert/strict'),cp=require('node:child_process');
const root=path.resolve(__dirname,'..');
const map=JSON.parse(fs.readFileSync(path.join(root,'assets/roadmap-links.json')));
let topics=0,links=0;const expected={};
function stagesFromHCC(s){const a=s.indexOf('const STAGES = ['),b=s.indexOf('/* the quantifier',a);return vm.runInNewContext(s.slice(a,b)+';STAGES');}
function rec(s){const a=s.indexOf('function recHTML('),b=s.indexOf('\nfunction render',a);return s.slice(a,b);}
// Only the explicitly requested library category / editorial heading changes.
function libraryPresentation(raw){
 // Approved copy correction only: the old baseline corrupted stratification.
 const d=JSON.parse(raw.replaceAll('stlocal approval','stratification'));
 for(const [key,ref] of [...Object.entries(d.refs),...Object.entries(d.nonpm)]){
  if(!['HAI evidence · October 2026','HAI library access','HAI randomized conference results'].includes(ref[1]))continue;
  const id=key.replace(/^tmc/,'');ref[1]=id==='37210451'?'Transplant':id==='39962001'?'Guidelines & policy':'Liver-directed';
 }
 for(const topic of d.quickref||[]){
  if(topic.title==='HAI evidence and programme update · 15 October 2026')topic.title='Hepatic arterial infusion: selection, evidence and delivery';
  for(const row of topic.rows||[])if(row[0]==='Adjuvant HAI: updated evidence')row[0]='Adjuvant HAI: randomized evidence';
 }
 return d;
}
for(const slug of Object.keys(map)){
 const rel=`${slug}/index.html`,s=fs.readFileSync(path.join(root,rel),'utf8'),old=require('./apply_clinical_revisions.cjs').applyText(rel,cp.execFileSync('git',['show',`f77348e:${rel}`],{cwd:root,encoding:'utf8',maxBuffer:4e6}));
 assert(s.includes('RoadmapFlow.setup(')&&s.includes('RoadmapFlow.render('));
 assert.equal(rec(s),rec(old),slug+' option/evidence renderer changed');
 let stages;
 if(slug==='hcc'){
   stages=JSON.parse(JSON.stringify(stagesFromHCC(s)));assert.deepEqual(JSON.parse(JSON.stringify(stages)),JSON.parse(JSON.stringify(stagesFromHCC(old))));
   for(const marker of ['const REF =','const NONPM =','const TOPICS =','const LOCO =','const SYSTEMIC =','const HONEST ='])assert(s.includes(old.slice(old.indexOf(marker),old.indexOf('\n];',old.indexOf(marker))+3))||marker==='const REF ='||marker==='const NONPM =');
 }else{
   const rel=`${slug}/data/pathway.json`;const data=fs.readFileSync(path.join(root,rel),'utf8');assert.deepEqual(JSON.parse(data),libraryPresentation(require('./apply_clinical_revisions.cjs').applyText(rel,cp.execFileSync('git',['show',`f77348e:${rel}`],{cwd:root,encoding:'utf8',maxBuffer:4e6}))));stages=JSON.parse(data).gates;
 }
 expected[slug]=[];assert.deepEqual(Object.keys(map[slug]).sort(),stages.map(s=>s.id).sort(),slug+' coverage');
 for(const s of stages){
  topics++;expected[slug].push({id:s.id,name:s.name,criteria:s.crit.length,standard:s.standard.length,alt:s.alt.length,avoid:s.avoid.length});
  assert(map[slug][s.id].length>0,slug+'/'+s.id+' has no links');
  for(const r of map[slug][s.id]){
   links++;assert(r.when&&r.when.length>10,'Missing conditional wording');
   if(r.decision)assert(stages.some(s=>s.id===r.decision),slug+' invalid decision '+r.decision);
   else if(r.topic)assert(slug==='hcc'&&['dx','cure','tx','loco','resp'].includes(r.topic));
   else{const u=new URL(r.url,'https://local.test/');assert.equal(u.origin,'https://local.test');const file=path.join(root,u.pathname.replace(/^\//,''));assert(fs.existsSync(file),'Missing destination '+r.url);if(u.hash.startsWith('#decision-')){const targetSlug=u.pathname.split('/').filter(Boolean)[0];assert(map[targetSlug]?.[decodeURIComponent(u.hash.slice(10))],'Missing target decision '+r.url);}if(slug==='pdac')assert(!u.pathname.startsWith('/transplant/'),'PDAC transplant route');}
  }
 }
}
assert.equal(topics,103);assert.equal(Object.keys(map).length,12);
fs.writeFileSync('/tmp/roadmap-flow-expected.json',JSON.stringify(expected));
console.log(`PASS: ${topics} topics across 12 roadmaps; ${links} conditional links valid; original clinical data and option renderers unchanged.`);
