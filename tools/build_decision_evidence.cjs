const fs=require('fs'),path=require('path'),assert=require('assert');
const root=path.resolve(__dirname,'..'),read=p=>JSON.parse(fs.readFileSync(path.join(root,p),'utf8'));
const data=read('tools/prognosis_cards.json');
for(const [id,c] of Object.entries(data.cards)){
 for(const field of ['title','population','n','context','endpoint','origin','horizon','source','caution','uncertainty','verified'])assert(c[field],id+' missing '+field);
 assert(data.sources[c.source],id+' source missing');assert(c.rows.length>0,id+' rows missing');
 c.rows.forEach(r=>assert(r.label&&r.value,id+' empty estimate'));
}
const topics=read('tools/decision_workspace_source.json'),protocol=read('transplant/assets/content.json');
for(const [key,ids] of Object.entries(data.placements)){
 const [type,disease,decision]=key.split('/');assert(type==='roadmap'?topics[disease]?.[decision]:protocol.assistants[disease+'/'+decision],key+' invalid placement');
 ids.forEach(id=>assert(data.cards[id],key+' card missing '+id));
}
for(const [d,ids] of Object.entries(data.libraries))ids.forEach(id=>assert(data.cards[id],d+' missing '+id));
for(const [id,s] of Object.entries(data.sources)){
 for(const field of ['author','journal','year','locator','url','verification'])assert(s[field],id+' source missing '+field);
 assert((s.pmid&&/^\d+$/.test(s.pmid)&&s.doi.startsWith('10.'))||id.startsWith('houston-'),id+' identifier missing');
}
const waiting=read('transplant/assets/houston-waiting.json');
for(const key of ['hcc','all']){
 const card=data.cards['houston-'+key],cohort=waiting.cohorts[key],point=cohort.points.find(p=>p.month===12);
 assert.equal(card.n,cohort.n);assert.equal(cohort.entry_start,'2021-01-01');assert.equal(cohort.entry_end,'2025-12-31');
 assert.equal(card.rows[0].value,(point.ddlt*100).toFixed(1)+'%');assert.equal(card.rows[1].value,(point.death_or_too_sick*100).toFixed(1)+'%');
}
const generated='/* Verified outcome context. Source: tools/prognosis_cards.json. No eligibility rules. */\nwindow.DecisionEvidenceData='+JSON.stringify(data)+';\n';
const target=path.join(root,'assets/decision-evidence-data.js');
if(process.argv.includes('--check'))assert.equal(fs.readFileSync(target,'utf8'),generated,'Generated evidence data is stale');else fs.writeFileSync(target,generated);
console.log(`${Object.keys(data.cards).length} evidence cards validated; ${Object.keys(data.placements).length} decision placements.`);
