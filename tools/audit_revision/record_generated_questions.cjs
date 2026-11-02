const fs=require('fs'),cp=require('child_process'),path=require('path');
const R=path.resolve(__dirname,'../..'),lib=require('../apply_clinical_revisions.cjs');
const revs=lib.revisions().filter(x=>x.id.startsWith('2026-11-02'));
const files=['assets/documents.json',...fs.readdirSync(path.join(R,'documents')).map(x=>`documents/${x}/questions.json`).filter(f=>fs.existsSync(path.join(R,f)))];
const edits=[];
for(const f of files){const base=cp.execFileSync('git',['show',`30039fe:${f}`],{cwd:R,encoding:'utf8',maxBuffer:20000000});const old=lib.applyText(f,base,revs),value=fs.readFileSync(path.join(R,f),'utf8');if(old!==value)edits.push({file:f,old,new:value});}
if(edits.length)fs.writeFileSync(path.join(R,'tools/clinical_revisions/2026-11-02-zzzzz-generated-questions.json'),JSON.stringify({id:'2026-11-02-zzzzz-generated-questions',reason:'Rebuild web discussion questions from the revised clinical sources; historical Word files remain versioned.',files:edits},null,2)+'\n');
console.log(`Recorded ${edits.length} regenerated clinical question files.`);
