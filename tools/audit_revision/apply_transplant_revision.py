"""Create exact, replayable revisions; original audit/baseline files remain intact."""
from pathlib import Path
import json, copy, hashlib
ROOT=Path(__file__).resolve().parents[2]
rev={'id':'2026-11-02-transplant-audit','date':'2026-11-02','summary':'Source-adjudicated routing, calculator and transplant-context corrections; no protocol activation.','edits':[],'files':[]}
register=[]
texts={}
def edit(file,old,new,finding,source):
    p=ROOT/file
    s=texts.get(file,p.read_text())
    assert s.count(old)==1,(file,old[:100],s.count(old))
    texts[file]=s.replace(old,new,1)
    rev['files'].append({'file':file,'old':old,'new':new})
    register.append({'finding_id':finding,'source_locator':source,'files':[file],'old':old,'new':new})
def filechange(file,new,finding,source):
    old=(ROOT/file).read_text(); edit(file,old,new,finding,source)
D=json.loads((ROOT/'transplant/assets/content.json').read_text())
def value(path,new,finding,source):
    h=D
    for k in path[:-1]: h=h[k]
    old=copy.deepcopy(h[path[-1]])
    assert old!=new,path
    rev['edits'].append({'op':'replace_value','path':path,'old':old,'new':new})
    h[path[-1]]=copy.deepcopy(new)
    register.append({'finding_id':finding,'source_locator':source,'files':['transplant/assets/content.json','tools/v12_content_snapshot.json','transplant/*/index.html'],'content_path':path,'old':old,'new':new})
# Pinned scripts are edited through exact replacement records. Source copies are synchronized afterward.
f='transplant/assets/risk-routing.js'
s=(ROOT/f).read_text()
s=s.replace("const referenceOnly=['hcc-b4'];", "const referenceOnly=['hcc-b4'];\n// These findings remain in force until the originating assessment is updated. Browsing is always possible.\nconst matches=(r,a)=>Object.entries(r.when).every(([k,v])=>(Array.isArray(v)?v:[v]).includes(a[k]));")
s=s.replace("  if(step==='curative-route'", "  if(is(a.afp,'not-met','no')||(step==='listing'&&a.exception==='no'&&prior.extra?.exception_reason==='afp')||(step==='waitlist'&&a.control==='lost'&&is(prior.extra?.loss,'afp','burden-afp')))add('afp_history','Which AFP history requires review?',[['pretreatment','AFP >1000 before treatment; no post-LRT AFP ≥500 history'],['post-lrt','AFP ≥500 after LRT in the >1000-history pathway'],['unclear','History or timing is not established']], 'Policy 9.5.I.iv: distinguish a pretreatment elevation from post-LRT AFP ≥500 at any time; later shrinkage or a favorable answer does not erase that history.');\n  if(prior.afp&&['treatment','listing','waitlist'].includes(step))add('afp_resolution','What has resolved the earlier AFP finding?',[['pending','Review remains pending'],['pretreatment-resolved','Pretreatment-only >1000 has fallen below 500 after LRT and remained below 500; no post-LRT value ≥500'],['individual','Individual NLRB review and the case-specific plan are documented']], 'Only a documented pretreatment-only response can restore the standard AFP route. Post-LRT ≥500 history remains an individual allocation-review route.');\n  if(step==='curative-route'",1)
s=s.replace("  else if(recovered)finding=null;", "  if(failed)finding.history=x.afp_history||'unclear';\n  else if(recovered&&finding&&finding.history==='pretreatment'&&x.afp_resolution==='pretreatment-resolved')finding=null;\n  else if(finding&&x.afp_resolution==='individual')finding.why='Prior AFP failure remains an individual allocation-review history. The case-specific NLRB plan is marked documented; this does not establish automatic standardized eligibility.';")
s=s.replace(" const candidates=[],stops=[],unresolved=[];", " const candidates=[],stops=[],unresolved=[];\n const afp=afpReview(pathway,index,session,context);")
s=s.replace("if(i<index&&Object.keys(a).length&&(configs[k]?.questions||[]).some(q=>!a[q.id]||a[q.id]==='unknown'))", "if(i<index&&(configs[k]?.questions||[]).some(q=>!q.options.some(o=>o.value===a[q.id])||a[q.id]==='unknown'))")
s=s.replace("  const found=local(slug,s,a,x,history);", "  for(const q of questions(slug,s,a,{...history,extra:x}))if(x[q.id]==='unknown'||x[q.id]==='unclear')unresolved.push({origin:s,label:'An additional finding remains uncertain: '+q.label});\n  const found=local(slug,s,a,x,history);")
s=s.replace("  const stop=hardStop(slug,s,a,x);if(stop)stops.push(stop);", """  const stop=hardStop(slug,s,a,x);if(stop)stops.push(stop);
  // A local closed stratum is a hold under this pathway, not a national contraindication.
  for(const o of found.options)if(o.blocks)stops.push({origin:s,why:o.reason+' This local boundary has not been activated; individual clinical and allocation review remains separate.',clinical:true,local:true});
  const config=configs[k], rule=config?.rules.find(r=>matches(r,a));
  const branch=rule?.branch===null?rule:pathway.steps[i].branches[rule?.branch];
  const kind=branch?.kind;
  // Stop rules come from the authored assistant itself; no incomplete duplicate stop list.
  if(kind==='stop'&&!stop)stops.push({origin:s,why:(branch.text||branch.action)+' Reassess this finding at its originating decision before advancing under the pathway.',clinical:true});
  if(i<index&&is(kind,'hold','redirect')){
   const standardMixed=slug==='icca'&&s==='diagnosis'&&a.histology==='mixed'&&a.extent==='yes'&&session.answers['icca/phenotype']?.program==='yes'&&session.answers['icca/phenotype']?.profile==='fits'&&session.answers['icca/phenotype']?.focality==='solitary';
   const clearedNodes=slug==='nelm'&&s==='distribution'&&a.spread==='cleared'&&a.primary==='yes'&&session.answers['nelm/observation']?.clearance==='met';
   const benignReview=slug==='hca'&&s==='characterize'&&a.diagnosis==='malignant'&&session.answers['hca/transformation']?.diagnosis==='benign';
   const individual=(slug==='hcc'&&((s==='allocation'&&is(a.burden,'beyond','t1'))||(s==='curative-route'&&a.spread==='prior')))||(slug==='icca'&&s==='phenotype'&&(a.profile==='outside'||a.focality==='multiple'))||(slug==='hca'&&s==='exception-route'&&a.route==='none');
   const afpOnly=slug==='hcc'&&((s==='allocation'&&a.afp==='not-met'&&is(a.burden,'t2','ds')&&a.spread==='yes')||(s==='treatment'&&a.afp==='no'&&a.response==='controlled'&&a.reserve==='yes')||(s==='listing'&&a.exception==='no'&&a.fitness==='yes'&&x.exception_reason==='afp'));
   if(!standardMixed&&!clearedNodes&&!benignReview&&!individual&&!afpOnly)unresolved.push({origin:s,label:(branch.text||branch.action)+' Review and update the originating finding; a later favorable answer does not resolve it.'});
  }""")
s=s.replace(" const afp=afpReview(pathway,index,session,context);\n const route=", " const route=")
s=s.replace("const route=nonstandard?{origin:nonstandard.origin,why:routeText[slug]}:afp;", "const t1=slug==='hcc'&&session.answers['hcc/allocation']?.burden==='t1'?{origin:'allocation',why:'The original assessment recorded T1 disease. Confirm qualifying burden and the applicable allocation route at that decision; later favorable answers do not create a standardized exception.'}:null;\n const route=nonstandard?{origin:nonstandard.origin,why:routeText[slug]}:afp||t1;")
s=s.replace("extra:context[key]||{}})", "extra:context[key]||{},afp})")
filechange(f,s,'A-01; B08-R7-01–10,13','R7_REPORT.md §§5–8; A Routing_Reproduction.md; OPTN 9.5.I.iv; NLRB pp7–11; existing disease-specific local boundaries')
# Make all six authored AFP actions available whenever an AFP failure is shown.
f='transplant/assets/app.js';s=(ROOT/f).read_text()
old="${renderActions([{label:'High-risk HCC and individual allocation assessment',care:'exception'},{label:'Continue or change HCC treatment',care:'treatment'},{label:'Recheck the AFP requirement',step:finding.origin}])}"
new="${renderActions([...(DATA.continuations['hcc/allocation'].rules['4']||[]),{label:'Recheck the AFP requirement and history',step:finding.origin}])}"
assert old in s;s=s.replace(old,new)
s=s.replace("const mainDestinations=new Set([...current.querySelectorAll('.route-button')].filter(link=>!link.closest('[data-afp-review]')).map(destination));", "const mainDestinations=new Set([...current.querySelectorAll('.route-button')].filter(link=>!link.closest('[data-afp-review]')).map(link=>destination(link)+'|'+link.textContent.trim()));")
s=s.replace("if(mainDestinations.has(destination(link)))", "if(mainDestinations.has(destination(link)+'|'+link.textContent.trim()))")
filechange(f,s,'A-01; AFP six-action preservation','Authored continuations hcc/allocation rule4; A Routing_Review.md; OPTN 9.5.I.iv')
# Every custom stop/hold appears alongside the authored branches in the default no-input view.
f='assets/transplant-workspace.js';s=(ROOT/f).read_text()
s=s.replace("function actionsFor(step, index) {", "function actionsFor(step, index, ruleIndex) {")
s=s.replace("const list = (data.continuations?.[slug + '/' + step.id]?.branches?.[index] || [])", "const route = data.continuations?.[slug + '/' + step.id];\n    const list = (ruleIndex === undefined ? route?.branches?.[index] || [] : route?.rules?.[ruleIndex] || [])")
s=s.replace("function optionCard(step, branch, index) {", "function optionCard(step, branch, index, ruleIndex) {")
s=s.replace("card.dataset.branchIndex = String(index);", "if (ruleIndex === undefined) card.dataset.branchIndex = String(index);\n    else card.dataset.customRuleIndex = String(ruleIndex);")
s=s.replace("const next = actionsFor(step, index);", "const next = actionsFor(step, index, ruleIndex);")
s=s.replace("    for (const [kind, title] of GROUPS) {\n      const branches = step.branches.map((b, i) => [b, i]).filter(([b]) => b.kind === kind);", """    const config = data.assistants[slug + '/' + step.id];
    const results = step.branches.map((b, i) => [b, i]);
    config.rules.forEach((r, ri) => {
      if (r.branch !== null) return;
      const criteria = Object.entries(r.when).map(([qid, values]) => {
        const q = config.questions.find(q => q.id === qid);
        const choices = (Array.isArray(values) ? values : [values]).map(v => q.options.find(o => o.value === v));
        return {text: q.label + ' ' + choices.map(o => o.label).join(' OR '), refs: q.refs || [], children: []};
      });
      results.push([{kind:r.kind,title:r.title,action:r.text,criteria,refs:r.refs},null,ri]);
    });
    for (const [kind, title] of GROUPS) {
      const branches = results.filter(([b]) => b.kind === kind);""")
s=s.replace("for (const [b, i] of branches) group.append(optionCard(step, b, i));", "for (const [b, i, ri] of branches) group.append(optionCard(step, b, i, ri));")
filechange(f,s,'A default-view omission; B08-R7 custom-result inventory','172 authored rules / 46 decisions in reviewed content.json; custom branch:null rules and their existing continuations')
# Calculators: preserve exact inputs; do not round a genuine >8 total into eligibility.
f='assets/clinical-scores.js';s=(ROOT/f).read_text()
s=s.replace("    const n = sizes.length, max = Math.max(...sizes), sum = sizes.reduce((a, b) => a + b, 0), spread = positive(v.spread);", """    if (sizes.some(x => x < 1)) return fail('Enter only qualifying HCC lesions at least 1 cm. Review subcentimeter observations separately; they are not OPTN Class 5 lesions.');
    // Compensated summation plus representation-scale tolerance; retain arbitrarily precise inputs.
    let sum = 0, correction = 0;
    for (const size of sizes) { const y = size - correction, t = sum + y; correction = (t - sum) - y; sum = t; }
    const withinSum = sum <= 8 || sum - 8 <= Number.EPSILON * Math.max(8, sum) * sizes.length;
    const n = sizes.length, max = Math.max(...sizes), spread = positive(v.spread);""")
s=s.replace('max <= 5 && sum <= 8','max <= 5 && withinSum').replace('max < 3 && sum <= 8','max < 3 && withinSum').replace('max <= 4.5 && sum <= 8','max <= 4.5 && withinSum')
s=s.replace("pages: ['hcc', 'chcca', 'T:hcc']", "pages: ['hcc', 'T:hcc']",1)
s=s.replace("{id: 'bclc', name: 'BCLC stage', kind: 'Classification', pages: ['hcc', 'chcca', 'T:hcc']", "{id: 'bclc', name: 'BCLC stage', kind: 'Classification', pages: ['hcc', 'T:hcc']")
s=s.replace('UNOS downstaging (pretreatment): ${r.milan ? \'not needed (within Milan)\'', 'UNOS downstaging (pretreatment): ${r.t2 === \'met\' ? \'not needed (within T2)\'')
s=s.replace("yes('dfi', 'Under 12 months from primary resection to liver metastasis diagnosis')", "yes('dfi', 'Synchronous liver metastases, or diagnosed under 12 months after primary resection')")
s=s.replace('node-positive primary; under 12 months from primary resection to liver metastasis diagnosis;', 'node-positive primary; synchronous liver metastases or diagnosis under 12 months after primary resection;')
s=s.replace('// Metroticket 2.0 (Mazzaferro 2018): number of viable tumors + largest viable diameter (cm)', '// Metroticket 2.0 (Mazzaferro 2018): active nodules ≥1 cm + whole largest active-nodule diameter (including necrosis)')
s=s.replace("return fail('Enter the number of viable tumors (0 after a complete response).')", "return fail('Enter the number of active nodules at least 1 cm (0 after a complete response).')")
s=s.replace("if (n > 0 && (d === null || d <= 0)) return fail('Enter the largest viable tumor diameter (cm).');", "if (n > 0 && (d === null || d < 1)) return fail('Enter the largest active nodule diameter including necrotic areas (at least 1 cm).');")
s=s.replace("if (n === 0 && d !== null && d > 0) return fail('With no viable tumor the size is 0. Check the entries.');", "if (d !== null && d < 0) return fail('Diameter cannot be negative.');\n    if (n === 0 && d !== null && d > 0) return fail('With no active qualifying nodule the size is 0. Check the entries.');")
s=s.replace("return {ok: true, sum: round(sum, 1), limit, within: limit !== null && sum <= limit, sharedBoundary: afp === 400};", "return {ok: true, sum, limit, within: limit !== null && sum <= limit, sharedBoundary: afp === 400};")
s=s.replace("{id: 'number', label: 'Number of viable tumors', type: 'number', step: '1'},\n      {id: 'largest', label: 'Largest viable tumor diameter', unit: 'cm', type: 'number', step: '0.1'}", "{id: 'number', label: 'Number of active nodules at least 1 cm', type: 'number', step: '1'},\n      {id: 'largest', label: 'Largest active nodule, whole diameter including necrosis', unit: 'cm', type: 'number', step: '0.1'}")
s=s.replace('Sum = number of viable tumors + largest viable diameter (cm)', 'Sum = active nodules ≥1 cm + whole largest active-nodule diameter including necrosis (cm)')
s=s.replace('Sum of the number of viable tumors and the largest viable diameter (cm)', 'Sum of the number of active nodules at least 1 cm and the whole largest active-nodule diameter including necrotic areas (cm)')
s=s.replace("{id: 'largest', label: 'Largest tumor diameter', unit: 'cm', type: 'number', step: '0.1'},\n      {id: 'number', label: 'Number of tumors', type: 'number', step: '1'},\n      {id: 'afp', label: 'AFP'", "{id: 'largest', label: 'Largest current active nodule, whole diameter', unit: 'cm', type: 'number', step: '0.1'},\n      {id: 'number', label: 'Current active typical nodules over 1 cm', type: 'number', step: '1'},\n      {id: 'afp', label: 'AFP at this assessment'")
s=s.replace('A selection model used in France; separate from OPTN exception rules.</p>', 'French operational guidance uses current assessment AFP and active typical nodules over 1 cm after treatment, measuring the maximum whole nodule rather than an enhancing rim. Record the assessment date and preserve pretreatment burden separately for allocation. AFEF 2025 Table 3 specifies ≥4 for the high count band; these operational definitions are separate from the original model validation.</p><p>A selection model used in France; separate from OPTN exception rules.</p>')
s=s.replace("${src(pm('22750200', 'Duvoux 2012'))}", "${src(pm('22750200', 'Duvoux 2012'), web('https://www.agence-biomedecine.fr/IMG/pdf/guide_score_foie_v4.pdf#page=20', 'ABM Score Foie 2024 · pp19–22'), web('https://afef.asso.fr/wp-content/uploads/2025/03/Recommandations-Afef-2025-CHC.pdf#page=65', 'AFEF 2025 · Table 3'))}")
s=s.replace('Derived in recipients within Milan on imaging; an external cohort found weaker discrimination when the explant was beyond Milan.', 'Derived in recipients within Milan on imaging; patients downstaged from beyond Milan were excluded. The external validation advises against using RETREAT beyond Milan on explant; it is not a pretransplant eligibility test.')
s=s.replace('When the two indices disagree, assign the higher grade.</p>', 'When the two indices disagree, assign the higher grade. On a small biopsy, use representative Ki-67 and differentiation when mitoses are not evaluable; expert review or additional tissue may be needed. WHO G2 includes Ki-67 exactly 20%, but the NLRB NET exception guidance uses a separate strict &lt;20% limit; this grade does not establish allocation eligibility.</p>')
s=s.replace('<b>T2 with AFP 1000 ng/mL or less:</b> eligible for the standardized exception.', '<b>T2 with AFP 1000 ng/mL or less:</b> satisfies this AFP condition only if the relevant prior AFP history and all other policy conditions are met.')
s=s.replace('or if AFP rises to 500 or more after having fallen below 500.</p>', 'or if AFP rises to 500 or more after having fallen below 500. Automatic extension also stops after resection since the preceding request or when the requested score differs from Table 9-10.</p>')
s=s.replace("waitlist: ['mrecist', 'lfi']", "waitlist: ['mrecist', 'afpexc', 'lfi']")
s=s.replace("chcca: {3: SURGERY, 5: ['lfi']", "chcca: {3: SURGERY, 5: ['lfi', 'meldexc']")
filechange(f,s,'B08-R2 F01–04,F07; R3-F01; A HB089; A-01; C tool reconciliation','OPTN 9.5.I pp196–199; Mazzaferro2018 PDF pp4–5; Fong1999 p312; AFEF2025 pp64–65; ABM2024 pp19–22; vanHooff2022 Discussion')
# Correct HCA benign detour: return to standard care/exception assessment after pathology clarification.
x=copy.deepcopy(D['continuations']['hca/transformation']['branches']['0'])
x[0]['label']='Return to standard-care and exception-route assessment';x[0]['step']='standard-care'
value(['continuations','hca/transformation','branches','0'],x,'B08-R7-08','NLRB p11 adenoma alternative criteria; R7_REPORT §5 element35')
# A separate post-LT disease-review destination preserves graft safety and does not re-enter candidacy.
for p in D['index']:
 slug=p['slug'];plans=copy.deepcopy(D['care'][slug]);follow=next(x for x in plans if x['id']=='follow-up')
 for a in follow['actions']:
  if a.get('care')=='treatment': a['care']='post-transplant-recurrence';a['label']='Review new disease after transplantation'
 plans.append({'id':'post-transplant-recurrence','title':'New or recurrent disease after transplantation','when':'A liver transplant recipient has suspected or confirmed new or recurrent tumor.','tasks':['Confirm the diagnosis and extent with the tumor and transplant teams, including the graft and extrahepatic sites.','Review graft function, immunosuppression, drug interactions and organ-specific treatment risks before choosing local or systemic therapy.','Review disease-specific treatment options with transplant specialists. An immune checkpoint inhibitor carries rejection and graft-loss risks after liver transplantation; for HCC, AASLD advises against routine post-transplant ICI.','Agree symptom management, a follow-up plan and a contact for worsening symptoms. This review does not authorize retransplantation.'],'refs':follow['refs'],'endpoint':False,'actions':[{'label':'Return to the transplant follow-up plan','detail':'Preserve graft and immunosuppression context.','step':None,'care':'follow-up','url':None},{'label':'Supportive care alongside tumor treatment','detail':'When symptom support is needed or tumor-directed treatment is unsuitable.','step':None,'care':'supportive','url':None}]})
 value(['care',slug],plans,'A2-SH-005','A shared/Routing_Review.md; existing follow-up safety references; AASLD HCC2023 guidance statement49')
# Preserve the existing reviewed original counts; no baseline clinical element is removed.
(ROOT/'tools/clinical_revisions'/f"{rev['id']}.json").write_text(json.dumps(rev,ensure_ascii=False,indent=2)+'\n')
(ROOT/'tools/audit_revision/transplant_change_register.json').write_text(json.dumps({'baseline':'30039fe0cec15a29ac2f326e0ee316eaf6bfb48e','analyst':'A (Codex)','revision_id':rev['id'],'changes':register},ensure_ascii=False,indent=2)+'\n')
print('Prepared',len(rev['files']),'exact script replacements and',len(rev['edits']),'data replacements')
