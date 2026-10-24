/* Synthetic checks for serialization, validation and export integrity. */
const assert=require('node:assert/strict');const fs=require('node:fs');const path=require('node:path');
const root=path.resolve(__dirname,'..');const R=require(path.join(root,'transplant/recording-templates/templates.js'));
const folder=path.join(root,'transplant/recording-templates');
const files=fs.readdirSync(folder).filter(x=>x.includes('--')&&x.endsWith('.html'));
function schemaOf(name){const html=fs.readFileSync(path.join(folder,name),'utf8');return JSON.parse(html.match(/<script type="application\/json" id="form-schema">([\s\S]*?)<\/script>/)[1]);}
function blank(s){return {format:s.format,format_version:s.format_version,template_version:s.template_version,pathway_id:s.pathway_id,decision_id:s.decision_id,modules:Object.fromEntries(s.modules.map(g=>[g.id,[{instance_id:g.id+'-1',source:'',observed_date:'',values:Object.fromEntries(g.fields.map(f=>[f.id,{value:null,missing:'',notes:'',source:'',observed_date:'',precision:'day'}]))}]])),checklist:s.checklist.map(()=>({status:'',result:'',action:'',owner:'',due:''}))};}
for(const file of files){const s=schemaOf(file),d=blank(s);assert.deepEqual(R.errors(d,s),[],file);assert.equal(R.note(d,s).includes('Draft / not signed.'),true);}
const s=schemaOf('pcca--staging.html'),d=blank(s);const v=(id)=>d.modules[id.split('.')[0]][0].values[id];
v('record.record_id').value='SYNTHETIC-TEST';v('record.assessment_id').value='DEMO-ONLY';v('operative_stage.approach').value='laparoscopy';
v('staging_specimens.examined').value=4;v('staging_specimens.positive').value=0;v('biliary.mass').value=18.7;
v('operative_stage.date').value='2026-10';v('operative_stage.date').precision='month';
assert.deepEqual(R.errors(d,s),[]);assert(R.note(d,s).includes('Number of nodes positive, when applicable: 0'));
assert(R.note(d,s).includes('18.7 mm'));assert(R.note(d,s).includes('month precision'));
assert.equal(R.validDate('2026-02-29'),false);assert.equal(R.validDate('2028-02-29'),true);assert.equal(R.validDate('2026-13','month'),false);
let copy=JSON.parse(JSON.stringify(d));copy.modules.staging_specimens.push({...structuredClone(copy.modules.staging_specimens[0]),instance_id:'staging_specimens-2'});
assert.deepEqual(R.errors(copy,s),[]);assert(R.csv(copy,s).includes('staging_specimens-2'));
copy.modules.staging_specimens[1].instance_id='staging_specimens-1';assert(R.errors(copy,s).some(x=>x.includes('duplicate')));
v('staging_specimens.examined').value=1.5;assert(R.errors(d,s).some(x=>x.includes('whole number')));v('staging_specimens.examined').value=4;
v('biliary.mass').value=-1;assert(R.errors(d,s).length);v('biliary.mass').value=18.7;
v('operative_stage.approach').value='invented';assert(R.errors(d,s).length);
v('operative_stage.approach').value='other';assert(R.errors(d,s).some(x=>x.includes('Other')));v('operative_stage.approach').notes='Synthetic alternative';assert.deepEqual(R.errors(d,s),[]);
v('staging_specimens.positive').missing='unknown';assert(R.errors(d,s).some(x=>x.includes('clear the value')));v('staging_specimens.positive').missing='';
v('decision.review_status').value='reviewed';assert(R.errors(d,s).some(x=>x.includes('reviewer')));v('decision.signoff').value='Demo Reviewer';v('decision.signoff_date').value='2026-10-24';assert.deepEqual(R.errors(d,s),[]);
assert.equal(R.csvCell('=SUM(1,2)'), '"\'=SUM(1,2)"');assert.equal(R.csvCell(-2),'"-2"');assert.equal(R.csvCell('a,"b"\nc'),'"a,""b""\nc"');
copy=structuredClone(d);copy.template_version='old';assert(R.errors(copy,s).some(x=>x.includes('template version')));
copy=structuredClone(d);copy.pathway_id='hcc';assert(R.errors(copy,s).length);
copy=structuredClone(d);copy.checklist[0].unexpected='x';assert(R.errors(copy,s).length);
copy=structuredClone(d);copy.modules.record[0].values.unrecognized={value:'x'};assert(R.errors(copy,s).length);
const demoFolder=path.resolve(root,'../../Electronic_Assessments_2026-10-24');fs.mkdirSync(demoFolder,{recursive:true});
fs.writeFileSync(path.join(demoFolder,'synthetic-pcca-assessment.json'),JSON.stringify(d,null,2));fs.writeFileSync(path.join(demoFolder,'synthetic-export.csv'),R.csv(d,s));
console.log(`PASS: ${files.length} form schemas; numeric zero/decimals/integers; missing states; partial/leap dates; repeated entries; single sign-off; invalid import rejection; formula-safe CSV and JSON round-trip.`);
