/* Browser inventory and clinical rendering regressions; no clinical records or real patient data. */
'use strict';
const fs=require('node:fs'),path=require('node:path'),http=require('node:http'),assert=require('node:assert/strict');
const {chromium}=require('playwright'),root=path.resolve(__dirname,'..');
const D=JSON.parse(fs.readFileSync(path.join(root,'transplant/assets/content.json'),'utf8'));
const python=fs.readFileSync(path.join(root,'tools/test_transplant_workspace_browser.py'),'utf8');
const VIEW=python.match(/VIEW = """([\s\S]*?)"""/)[1];
const mime={'.html':'text/html','.js':'text/javascript','.json':'application/json','.css':'text/css','.svg':'image/svg+xml','.png':'image/png'};
const server=http.createServer((req,res)=>{try{const pathname=decodeURIComponent(new URL(req.url,'http://local').pathname).replace(/^\/mh-liver-pathways\//,'/');let file=path.resolve(root,'.'+pathname);if(!file.startsWith(root+path.sep)&&file!==root){res.writeHead(403);return res.end();}if(fs.statSync(file).isDirectory())file=path.join(file,'index.html');res.writeHead(200,{'content-type':mime[path.extname(file)]||'application/octet-stream'});fs.createReadStream(file).pipe(res);}catch(e){res.writeHead(404);res.end('Not found');}});
(async()=>{await new Promise(r=>server.listen(0,'127.0.0.1',r));const base=process.argv[2]||'http://127.0.0.1:'+server.address().port+'/mh-liver-pathways/';const edition=base.includes('share')?'share':'full';let browser;
try{browser=await chromium.launch({headless:true,...(process.env.PLAYWRIGHT_EXECUTABLE?{executablePath:process.env.PLAYWRIGHT_EXECUTABLE}:{})});const page=await browser.newPage({viewport:{width:1280,height:900}});const errors=[];page.on('pageerror',e=>errors.push(e.message));let decisions=0,options=0,phone=0,widgetChecks=0,documentChecks=0;
async function noOutcomeWidget(p,label){
 const state=await p.evaluate(()=>({nodes:document.querySelectorAll('#outcome-evidence,.outcome-evidence,[data-outcome-jump]').length,
  scripts:[...document.scripts].filter(s=>/\/decision-evidence(?:-data)?\.js(?:\?|$)/.test(s.src)).length,
  labels:[...document.querySelectorAll('button,summary')].filter(n=>/^Outcome evidence (for this decision|library)/.test(n.textContent.trim())).length}));
 assert.deepEqual(state,{nodes:0,scripts:0,labels:0},label+' latent outcome widget');widgetChecks++;
 if(edition==='share'){
  const docs=await p.evaluate(()=>{
   const forbidden=[...document.querySelectorAll('a[href],area[href]')].filter(a=>{let u;try{u=new URL(a.href,location.href)}catch(e){return false}
    const local=u.origin===location.origin||/\/mh-liver-pathways(?:-share)?\//.test(u.pathname)&&u.hostname==='drliuhao.github.io';
    return local&&/\.(?:docx?|pdf|xlsx?|csv|tsv|pptx?|zip|json)$/i.test(decodeURIComponent(u.pathname));
   }).map(a=>({label:a.textContent.trim(),href:a.href}));
   return {edition:document.documentElement.dataset.edition,controls:document.querySelectorAll('.doc-corner,[data-doc],[download]').length,targets:forbidden};
  });
  assert.deepEqual(docs,{edition:'share',controls:0,targets:[]},label+' local downloadable documents');documentChecks++;
 }
}
await page.goto(base+'transplant/',{waitUntil:'networkidle'});await noOutcomeWidget(page,'transplant home');
for(const p of D.index){
 await page.goto(base+'transplant/'+p.slug+'/',{waitUntil:'networkidle'});
 for(const s of p.steps){
  await page.evaluate(id=>{location.hash='#'+id},s.id);
  // Hash navigation and the compact workspace render in separate animation frames.
  // Wait for this decision's completed UI, not a fixed delay that can inspect its predecessor.
  await page.waitForFunction(id=>{
   const d=document.querySelector('.decision.dw-protocol.tw-decision'),o=d?.querySelector('.tw-options');
   return d?.querySelector('.permalink')?.getAttribute('href')==='#'+id&&!!o?.getClientRects().length;
  },s.id,{timeout:5000});
  await noOutcomeWidget(page,p.slug+'/'+s.id);const r=await page.evaluate('('+VIEW+')()');assert(!r.missing&&r.card&&r.shown&&r.hiddenOld,p.slug+'/'+s.id);
  const tuples=(a,b,c,d)=>a.map((x,i)=>[x,b[i],c[i],d[i]]).sort((x,y)=>JSON.stringify(x).localeCompare(JSON.stringify(y)));
  assert.deepEqual(tuples(r.kinds,r.titles,r.actions,r.evidence),tuples(r.wantKinds,r.want,r.wantActions,r.wantEvidence),p.slug+'/'+s.id+' authored options');
  // Share transforms must preserve clinical semantics, including branch:null. Comparing only to
  // the page's own transformed data could falsely validate a stripped clinical outcome.
  const config=D.assistants[p.slug+'/'+s.id];
  const canonical=s.branches.concat(config.rules.filter(rule=>rule.branch===null).map(rule=>({title:rule.title,action:rule.text,kind:rule.kind})));
  assert.deepEqual(tuples(r.kinds,r.titles,r.actions,r.kinds.map(()=>0)),tuples(canonical.map(x=>x.kind),canonical.map(x=>x.title),canonical.map(x=>x.action||''),canonical.map(()=>0)),p.slug+'/'+s.id+' full clinical inventory preserved in '+edition);

  assert.equal(r.stops,r.wantStops);assert.equal(r.risk,r.wantRisk);decisions++;options+=r.titles.length;
 }
 for(const hash of ['meeting','high-risk','care-follow-up']){await page.evaluate(h=>{location.hash='#'+h},hash);await page.waitForTimeout(130);await noOutcomeWidget(page,p.slug+'#'+hash);}
}
// The default view must display each of the six original AFP alternatives, including choices that share destinations.
await page.goto(base+'transplant/hcc/#allocation',{waitUntil:'networkidle'});await page.waitForTimeout(250);
const afpLabels=D.continuations['hcc/allocation'].rules['4'].map(a=>a.label.replace(/^Continue: /,''));
const afpCard=await page.locator('[data-custom-rule-index="4"]').innerText();for(const label of afpLabels)assert(afpCard.includes(label),label);
// The browser executes the current matcher and guard on a recipient with a known prior pre-LT exclusion.
const phase=await page.evaluate(()=>{const d=JSON.parse(document.getElementById('protocol-data').textContent),p=d.index.find(x=>x.slug==='icca'),i=p.steps.length-1,s=DecisionAssistant.createSession(p,d.assistants);s.answers['icca/phenotype'].spread='no';s.answers['icca/follow-up']={phase:'after',plan:'yes',concern:'none'};return {guard:RiskRouting.evaluate(p,i,s,{},d.assistants).guard,result:DecisionAssistant.evaluate(d.assistants['icca/follow-up'],s.answers['icca/follow-up'],p.steps[i].branches)};});
assert.equal(phase.guard,null);assert.equal(phase.result.title,'Continue recipient follow-up');
const small=await browser.newPage({viewport:{width:390,height:844}});small.on('pageerror',e=>errors.push(e.message));
for(const p of D.index){await small.goto(base+'transplant/'+p.slug+'/',{waitUntil:'networkidle'});await small.waitForTimeout(130);await noOutcomeWidget(small,p.slug+' phone');assert.equal(await small.evaluate(()=>document.documentElement.scrollWidth-innerWidth),0,p.slug+' phone overflow');phone++;}
await page.screenshot({path:path.join(root,'tools/audit_revision/transplant_afp_browser_'+edition+'.png'),fullPage:true});
assert.deepEqual(errors,[]);const report={pass:true,baseURL:base,edition,widgetChecks,documentChecks,decisions,ordinaryAndCustomOptions:options,phonePages:phone,afpDistinctAlternatives:afpLabels.length,pageErrors:errors};fs.writeFileSync(path.join(root,'tools/audit_revision/transplant_browser_results_'+edition+'.json'),JSON.stringify(report,null,2)+'\n');console.log('PASS:',JSON.stringify(report));
}finally{if(browser)await browser.close();await new Promise(r=>server.close(r));}})().catch(e=>{console.error(e);process.exitCode=1});
