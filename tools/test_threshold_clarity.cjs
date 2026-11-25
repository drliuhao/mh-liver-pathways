const assert=require('node:assert/strict'),fs=require('node:fs'),cp=require('node:child_process');
const D=JSON.parse(fs.readFileSync('transplant/assets/content.json','utf8'));
const before=JSON.parse(cp.execFileSync('git',['show','4380022:transplant/assets/content.json'],{encoding:'utf8',maxBuffer:8e6}));
for(const [key,a] of Object.entries(D.assistants)){
 if(key!=='crlm/biology'){assert.deepEqual(a.rules,before.assistants[key].rules,key+' routing unchanged');assert.deepEqual(a.questions.map(q=>q.options.map(o=>o.value)),before.assistants[key].questions.map(q=>q.options.map(o=>o.value)),key+' categorical criteria unchanged');}
}
const q=D.assistants['crlm/biology'].questions.find(q=>q.id==='cea');
assert(q.help.includes('Initial NLRB request: CEA ≤80 µg/L. Extension: CEA <80 µg/L.'));
assert.deepEqual(q.options.map(o=>o.value),['low','high','unknown']);
assert(!D.assistants['crlm/biology'].rules.some(r=>r.when.cea==='boundary'));
assert(D.index.find(p=>p.slug==='crlm').issues.find(i=>i.id==='cea-progression').resolved);
assert(!D.index.find(p=>p.slug==='pcca').issues.find(i=>i.id==='threshold').question.includes('3 cm'));
assert(D.assistants['pcca/phenotype'].questions[0].options.some(o=>o.label==='Single mass <3 cm'));
assert(D.assistants['pcca/phenotype'].questions[0].help.includes('perpendicular'));
const stale=/Exactly 3(?:\.0)? cm|exactly ten is not|exact-20 boundary|Resolve exactly 80|exactly 80 satisfies|strict <80 harmonization/i;
assert(!stale.test(JSON.stringify(D)),'No redundant exact-threshold debate remains in active pathway data');
for(const file of ['lrt/matrix.json','lrt/comparisons.json','systemic/matrix.json'])assert.equal(fs.readFileSync(file,'utf8'),cp.execFileSync('git',['show','4380022:'+file],{encoding:'utf8',maxBuffer:8e6}),file+' therapy evidence preserved');
for(const file of ['documents/crlm/questions.json','transplant/assets/pathway-sections.json'])assert(fs.readFileSync(file,'utf8').includes('"resolved": true'));
console.log('PASS: 45 other assistant routes/options unchanged; CRLM CEA follows request stage; resolved references retained; all three therapy datasets unchanged.');
