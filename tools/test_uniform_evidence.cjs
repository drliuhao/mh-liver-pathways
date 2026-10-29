/* Evidence identity, search coverage and unchanged clinical content. */
const fs = require('fs'), vm = require('vm'), assert = require('assert'), cp = require('child_process');
const root = require('path').resolve(__dirname, '..');
const slugs = ['hcc','hilar','icca','crlm','nelm','chcca','pdac','pnet','ampullary','pcyst','adenoma','incidental'];
const baseline = '0773285';
const read = p => fs.readFileSync(root + '/' + p, 'utf8');
// Recorded clinical revisions (tools/clinical_revisions/) are replayed on the baseline: the only permitted change.
const old = p => require('./apply_clinical_revisions.cjs').applyText(p,cp.execFileSync('git',['show',baseline + ':' + p],{cwd:root,encoding:'utf8',maxBuffer:8e6}));
const htmlText = s => s.replace(/<[^>]*>/g,'').replace(/&amp;/g,'&').replace(/&lt;/g,'<').replace(/&gt;/g,'>').replace(/&#13;/g,'\r').replace(/\s+/g,' ').trim();
let appraisals = 0, aliases = 0;
for (const slug of slugs) {
  const page = read(slug + '/index.html');
  assert(page.includes('RoadmapEvidence.row(r, CRIT)'),slug);
  assert(!page.includes('class="study-appraisals"'),slug);
  assert(!page.includes('Batch 09 HAI update'),slug);
  for (const [,code] of page.matchAll(/<script(?:\s[^>]*)?>([\s\S]*?)<\/script>/g)) {
    if (code.trim().startsWith('{')) continue;
    new vm.Script(code,{filename:slug + '/index.html'});
  }
  const payload = page.match(/<script[^>]*id="roadmap-evidence-data"[^>]*>([\s\S]*?)<\/script>/)?.[1] || '{"papers":[]}';
  const data = JSON.parse(payload);
  let refs, nonpm;
  if (slug === 'hcc') {
    const start = page.indexOf('const REF ='), end = page.indexOf('\nfunction ',start);
    const ctx = {}; vm.createContext(ctx);
    // Restrict evaluation to the two static reference maps.
    const maps = page.slice(start).match(/const REF = ([\s\S]*?\n});\s*const NONPM = ([\s\S]*?\n});/);
    assert(maps,'HCC reference maps');
    vm.runInContext('refs = ' + maps[1] + '; nonpm = ' + maps[2],ctx);
    refs = ctx.refs; nonpm = ctx.nonpm;
  } else {
    const cur = JSON.parse(read(slug + '/data/pathway.json'));
    const prev = JSON.parse(old(slug + '/data/pathway.json').replaceAll('stlocal approval','stratification'));
    for (const key of ['gates','honest','ops','lead','matrix','provenance']) assert.deepStrictEqual(cur[key],prev[key],slug + ' clinical ' + key);
    for (const key of ['refs','nonpm']) {
      assert.deepStrictEqual(Object.keys(cur[key]),Object.keys(prev[key]),slug + ' source IDs');
      for (const id of Object.keys(cur[key])) {
        assert.deepStrictEqual(cur[key][id].slice(2),prev[key][id].slice(2),slug + ' citation ' + id);
        assert(!/^HAI (evidence|library access|randomized)/.test(cur[key][id][1]));
      }
    }
    refs = cur.refs; nonpm = cur.nonpm;
  }
  const rows = Object.entries(refs).map(([id,v])=>({id,pmid:id,tag:v[0],group:v[1],cit:v[2]})).concat(Object.entries(nonpm).map(([id,v])=>({id,tag:v[0],group:v[1],cit:v[2],url:v[3]})));
  const win = {addEventListener(){}}, document = {getElementById:()=>({textContent:payload})};
  const ctx = {window:win,document}; vm.createContext(ctx);
  vm.runInContext(read('assets/roadmap-evidence.js'),ctx);
  const api = win.RoadmapEvidence;
  api.merge(rows);
  const first = JSON.stringify(rows); api.merge(rows); assert.strictEqual(JSON.stringify(rows),first,slug + ' idempotent');
  assert.equal(new Set(rows.map(r=>r.id)).size,rows.length);
  for (const [id,v] of Object.entries(nonpm).filter(([id])=>id.startsWith('tmc'))) {
    const row = rows.find(r=>(r.aliases||[]).includes(id));
    assert(row,slug + ' TMC alias ' + id); assert(api.row(row,{}).includes(v[3].replace(/&/g,'&amp;'))); aliases++;
  }
  for (const paper of data.papers) {
    const matches = rows.filter(r=>r.pmid===paper.pmid); assert.equal(matches.length,1,slug + ' merged PMID');
    const row = matches[0], rendered = api.row(row,{}), searched = api.text(row,{});
    assert(rendered.includes('class="ev"')); assert(rendered.includes('class="evcrit"'));
    assert(rendered.includes(`id="${paper.id}"`));
    for (const val of Object.values(paper.appraisal)) {
      assert(searched.includes(val),slug + ' appraisal searchable');
      assert(htmlText(rendered).includes(htmlText(val)),slug + ' appraisal rendered');
    }
    const prior = old(slug + '/index.html').match(new RegExp('<details id="'+paper.id+'" class="study-appraisal">([\\s\\S]*?)</details>'));
    assert(prior,slug + ' original appraisal');
    const originalParagraphs = [...prior[1].matchAll(/<p>([\s\S]*?)<\/p>/g)].map(m=>htmlText(m[1]));
    for (const value of originalParagraphs.filter(v=>!v.includes('TMC full-text access'))) {
      assert(htmlText(rendered).includes(value),slug + ' original appraisal text retained: '+value.slice(0,55));
    }
    assert(old(slug + '/index.html').includes('id="'+paper.id+'"'),slug + ' stable original anchor');
    appraisals++;
  }
  const queries = ['no-such-publication-xyz', ...data.papers.map(p=>p.id), 'HAI'];
  for (const query of queries) {
    const matches = rows.filter(r=>(r.tag+' '+r.cit+' '+r.group+' '+r.id+' '+api.text(r,{})).toLowerCase().includes(query.toLowerCase()));
    if (query==='no-such-publication-xyz')assert.equal(matches.length,0);
    if (data.papers.some(p=>p.id===query))assert(matches.length>0,slug + ' former appraisal now in search');
  }
  console.log(slug + ': ' + rows.length + ' source cards before matrix merge; ' + data.papers.length + ' integrated appraisals');
}
assert.equal(appraisals,17);
assert.equal(aliases,13);
console.log(`PASS: 12 original evidence libraries; ${appraisals} appraisals searchable in ordinary cards; ${aliases} duplicate access records consolidated; clinical content and source identities retained.`);
