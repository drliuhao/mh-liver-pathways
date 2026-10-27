const assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path');
const root=path.resolve(__dirname,'..'),A=require('../assets/allocation-reference.js'),read=f=>fs.readFileSync(path.join(root,f),'utf8');
assert.equal(Object.keys(A.diseases).length,7);
for(const [slug,d]of Object.entries(A.diseases)){
 const data=JSON.parse(read(`transplant/${slug}/index.html`).match(/id="protocol-data"[^>]*>([\s\S]*?)<\/script>/)[1]);
 assert(d.steps.includes(data.pathway.steps.at(-1).id),'Final follow-up must include overview: '+slug);
 for(const id of d.steps)assert(data.pathway.steps.some(s=>s.id===id));
 const html=A.overview(slug);assert(html.includes(d.source));assert(html.includes('Houston waiting analysis'));
 assert(!/data-(?:step|care|record-finding|assistant-question)=/.test(html));assert(!/<(?:input|select)\b/.test(html));
}
assert(A.diseases.hcc.lead.includes('initial HCC request and first extension'));
assert(A.diseases.pcca.lead.includes('six-month exception delay does not apply'));
for(const slug of ['icca','crlm','nelm','hehe','hca'])assert.equal(A.diseases[slug].route,'Individual NLRB review');
assert(A.diseases.crlm.score.includes('20')&&A.diseases.crlm.score.includes('15'));
const data=JSON.parse(read('transplant/assets/houston-waiting.json'));
for(const [key,c]of Object.entries(data.cohorts)){
 assert(c.n>=30);assert.equal(c.points.length,25);assert.equal(c.origin,key==='hcc'?'First recorded HCC exception application':'First national liver listing');
 let dd=-1,drop=-1,risk=c.n;
 for(const p of c.points){assert(p.ddlt>=dd&&p.death_or_too_sick>=drop);assert(p.ddlt+p.death_or_too_sick<=1);assert(p.ddlt_low<=p.ddlt&&p.ddlt<=p.ddlt_high);assert(p.dropout_low<=p.death_or_too_sick&&p.death_or_too_sick<=p.dropout_high);assert(p.at_risk<=risk);dd=p.ddlt;drop=p.death_or_too_sick;risk=p.at_risk;}
 assert(c.points[12].ddlt+c.points[12].death_or_too_sick+c.other_12m+c.still_listed_12m<1.000002);
}
assert.equal(data.cohorts.hcc.n,463);assert.equal(data.cohorts.all.n,2890);
for(const c of Object.values(data.cohorts)){
 assert.equal(c.entry_start,'2021-01-01');assert.equal(c.entry_end,'2025-12-31');assert.equal(c.followup_end,'2025-12-31');
 assert(c.entered_2025>0&&c.entered_2025<c.n);assert(c.censored_before_12m>0&&c.censored_before_12m<c.n);
}
assert(read('transplant/waiting/index.html').includes('2021–2025 entrants only'));
assert(read('assets/waiting-analysis.js').includes('2025 entrants have shorter follow-up'));
assert(!/No one was administratively censored|One-year estimates also match direct endpoint proportions|4 February 2020–31 December 2024/.test(read('transplant/waiting/methods.md')));
const serialized=JSON.stringify(data);for(const k of ['PT_CODE','WL_ID_CODE','TRR_ID_CODE','/Users/','23839','02418','06510'])assert(!serialized.includes(k),'No patient data or encrypted mapping in public aggregates');
assert(read('assets/portal-navigation.js').includes('allocation-overview.js'));
assert(read('assets/clinical-tools.js').includes('AllocationReference.overview'));
assert(read('assets/allocation-overview.js').includes("const waitStep={hcc:'listing',pcca:'listing',icca:'review',crlm:'review',nelm:'review',hehe:'review',hca:'review'}"));
assert(read('assets/allocation-overview.js').includes("p.slug==='hcc'?['waitlist']:[]"));
assert(!/10,000 LDLT|10000 LDLT|dynamic HCC project/i.test(read('transplant/waiting/index.html')+read('transplant/waiting/methods.md')));
assert(!/localStorage|sessionStorage|fetch\(|assistantSession|dispatchEvent/.test(read('assets/allocation-overview.js')));
console.log('PASS: seven disease summaries, Transplant waitlisted placement, read-only controls, distinct clocks, score routes, aggregate bounds/intervals and public-data safeguards.');
