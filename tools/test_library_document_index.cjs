'use strict';
const assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path');
const root=path.resolve(__dirname,'..'),read=f=>JSON.parse(fs.readFileSync(path.join(root,f),'utf8'));
const {merge}=require('../evidence-libraries/document-index.js');
const base=read('evidence-libraries/catalog.json'),supplement=read('evidence-libraries/document-index.json');
const before=JSON.stringify(base),data=merge(base,supplement);
assert.equal(JSON.stringify(base),before,'preserve audited catalog');
assert.deepEqual(merge(data,supplement),data,'no duplicates when loaded again');
for(const lib of data.libraries){
 const original=base.libraries.find(l=>l.key===lib.key);
 assert.deepEqual(lib.papers.filter(r=>r.slides.length),original.papers,'preserve every original slide mapping');
 assert.equal(lib.publication_count,lib.papers.length);
 assert.equal(new Set(lib.papers.map(r=>r.id)).size,lib.papers.length,'deduplicate by publication');
 for(const r of lib.papers.filter(r=>!r.slides.length)){
  assert.equal(r.document_only,true);assert.ok(r.inclusion.length);assert.ok(data.publications[r.id]);
 }
}
for(const p of Object.values(supplement.publications)){assert.equal(p.pdf_available,null);assert.match(p.url,/^https:\/\//);}
const crlm=data.libraries.find(l=>l.key==='standard_crlm');
assert.ok(crlm.papers.length>base.libraries.find(l=>l.key==='standard_crlm').papers.length,'CRLM document references included');
assert.equal(data.matched_publication_pdfs,596,'no unverified PDF matches introduced');
assert.ok(data.no_slide_entries>0);
const app=fs.readFileSync(path.join(root,'transplant/assets/app.js'),'utf8');
assert.match(app,/<div class="viewbar"><div class="viewtabs" role="tablist"/);
assert.match(app,/<\/button><\/div><button type="button" class="viewjump"/);
const sourceApp=fs.readFileSync(path.join(root,'tools/decision_assistant_source/app.js'),'utf8');
assert.equal(app.split('\n').find(l=>l.includes('class="viewbar"')),sourceApp.split('\n').find(l=>l.includes('class="viewbar"')));
console.log('PASS: document-only index keeps original slide mappings and PDF audit; missing slides explicit, merge idempotent; evidence jump outside tablist; app sources match.');
