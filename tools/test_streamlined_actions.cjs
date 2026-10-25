/* Regression: concise links must not remove distinct clinical treatment choices. */
const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict'),path=require('node:path');
const root=path.resolve(__dirname,'..');
const source=fs.readFileSync(path.join(root,'transplant/assets/app.js'),'utf8');
const begin=source.indexOf('function renderActions(actions){'),end=source.indexOf('\nfunction afpReviewHTML',begin);
assert(begin>=0&&end>begin);
const e=s=>String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const ctx=vm.createContext({e,highRiskAction:a=>`<a class="route-button" href="${e(a.url)}">${e(a.label)}</a>`});
vm.runInContext(source.slice(begin,end)+';this.renderActions=renderActions;',ctx);
const data=JSON.parse(fs.readFileSync(path.join(root,'transplant/assets/content.json'),'utf8'));
let groups=0,actions=0;
for(const next of Object.values(data.continuations))for(const group of [...Object.values(next.branches),...Object.values(next.rules),next.clarify]){
 const html=ctx.renderActions(group);groups++;
 for(const a of group){assert(html.includes(e(a.label.replace(/^Continue: /,''))),a.label);if(a.detail)assert(html.includes(e(a.detail)),a.detail);actions++;}
}
const afp=data.continuations['hcc/allocation'].rules['4'];
const html=ctx.renderActions(afp);
assert.equal((html.match(/class="next-action"/g)||[]).length,6);
assert(html.includes('Continue downstaging')&&html.includes('Change liver-directed modality'));
assert.equal((ctx.renderActions([afp[0],afp[0]]).match(/class="next-action"/g)||[]).length,1);
assert.equal((ctx.renderActions(afp.slice(0,2)).match(/data-care="local"/g)||[]).length,2);
assert(!ctx.renderActions([{label:'<script>x</script>',care:'local',detail:'<img>'}]).includes('<script>'));
const reviewBegin=source.indexOf('function canContinueIndividualReview(context){');
const reviewEnd=source.indexOf('\nfunction updateDecision()',reviewBegin);
assert(reviewBegin>=0&&reviewEnd>reviewBegin);
vm.runInContext(source.slice(reviewBegin,reviewEnd)+';this.canContinueIndividualReview=canContinueIndividualReview;this.isReadinessOnlyReview=isReadinessOnlyReview;',ctx);
const mayContinue=(options,guard=null)=>ctx.canContinueIndividualReview({options,guard});
for(const anchor of ['hcc-b1','hcc-b2','pcca-b1','pcca-b3','icca-b1','icca-b2','icca-b3','crlm-b2','crlm-b3','net-b2','hehe-b2','future-closed'])assert(!mayContinue([{anchor,mode:'closed'}]),anchor);
for(const anchor of ['pcca-b1','pcca-b3','icca-b1','icca-b2','icca-b3'])for(const mode of ['review','readiness','checklist'])assert(!mayContinue([{anchor,mode}]),anchor+mode);
assert(mayContinue([{anchor:'hcc-b1',mode:'review'}]));
assert(mayContinue([{anchor:'crlm-b3',mode:'notice'}]));
assert(mayContinue([]),'AFP individual clinical review has no closed local proposal');
assert(!mayContinue([],{why:'Earlier safety issue'}));
assert(ctx.isReadinessOnlyReview({options:[{anchor:'icca-b3',mode:'readiness'}],guard:null}));
assert(!ctx.isReadinessOnlyReview({options:[{anchor:'icca-b3',mode:'readiness'},{anchor:'icca-b1',mode:'review'}],guard:null}));
assert(!ctx.isReadinessOnlyReview({options:[{anchor:'icca-b3',mode:'readiness'}],guard:{why:'Earlier selection issue'}}));
assert(!ctx.isReadinessOnlyReview({options:[],guard:null}));
console.log(`PASS: ${groups} next-action groups / ${actions} actions retain every label and conditional detail; six AFP choices remain separate; exact duplicates removed; output escaped.`);
console.log('PASS: closed local and inactive study proposals have no forward protocol action; supported HCC/CRLM/AFP individual review remains; safety holds take priority.');
console.log('PASS: iCCA living-donor study interest alone does not replace standard assessment; actual advanced-study and safety findings still take priority.');
