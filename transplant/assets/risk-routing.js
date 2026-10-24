/* Contextual links to existing reviews. This is not an eligibility calculator. */
(function(root){
'use strict';
const esc=s=>String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const is=(v,...xs)=>xs.includes(v), known=v=>!!v&&v!=='unknown';
const post=new Set(['hcc/after-transplant','pcca/follow-up']);
const referenceOnly=['hcc-b4'];
const coverage={
 'hcc-b1':['allocation','treatment','listing','waitlist'], 'hcc-b2':['curative-route','allocation','treatment','listing','waitlist'], 'hcc-b3':['treatment','listing','waitlist'], 'hcc-b4':[],
 'pcca-b1':['diagnosis','phenotype','neoadjuvant','staging','listing'], 'pcca-b2':['phenotype'], 'pcca-b3':['neoadjuvant','staging','listing'],
 'icca-b1':['phenotype','therapy','stability','review'], 'icca-b2':['therapy','stability','review'], 'icca-b3':['review'],
 'crlm-b1':['unresectability','control','restaging','review'], 'crlm-b2':['unresectability','control','restaging','review'], 'crlm-b3':['map-disease','biology','control','clocks','restaging','review'], 'crlm-b4':['review'],
 'net-b1':['options','review'], 'net-b2':['biology','distribution','observation','review'], 'net-b3':['options','review'],
 'hehe-b1':['risk','review'], 'hehe-b2':['stage','risk','review'], 'hca-b1':['exception-route','review'], 'hca-b2':['standard-care','exception-route','review']
};
// These final decisions include pre-transplant acceptance as well as follow-up.
for(const [anchor,steps] of Object.entries(coverage)){
 if(anchor.startsWith('crlm-'))steps.push('transplant');
 if(['icca-','net-','hehe-','hca-'].some(prefix=>anchor.startsWith(prefix)))steps.push('follow-up');
}
function questions(slug,step,a,prior={}){
 const q=[];const add=(id,label,options,help='')=>q.push({id,label,options:[...options,['unknown','Uncertain / not yet assessed']],help});
 if(slug==='hcc'){
  if(step==='curative-route'&&a.spread==='prior')add('history','Which previously treated finding is present?',[['vp12','Portal-vein invasion: Vp1–2'],['vp3','Portal-vein invasion: Vp3'],['vp4','Main/contralateral portal vein or hepatic-vein invasion'],['rupture','Tumor rupture'],['both','Rupture and vascular invasion']], 'The local invasion proposal has different limits from individual allocation review.');
  if(['treatment','listing','waitlist'].includes(step))add('ici','Immune checkpoint inhibitor exposure or plan',[['none','No exposure and none planned'],['planned','Being considered or planned'],['current','Currently receiving treatment'],['prior','Previously received']], 'Select the actual exposure or plan to display the transplant-safety review. No washout interval guarantees safety.');
  if(['treatment','listing','waitlist'].includes(step)&&prior.ici)add('ici_review','Has the transplant team completed the safety and sequencing review?',[['pending','Review or treatment plan remains pending'],['complete','Review completed and a case-specific plan agreed']], 'This selection does not approve transplantation or establish a safe washout interval. Reassess after changes in exposure or planned timing; document the team conclusion in the clinical record.');
  if(step==='treatment'&&a.response!=='spread'&&!prior.knownBurden)add('burden_history','Original tumor burden before treatment',[['standard','Within standard T2 / UNOS downstaging limits'],['beyond','Beyond UNOS downstaging limits']], 'Current tumor shrinkage does not erase the pretreatment burden. If recorded at decision 3, revise it there.');
  if(step==='waitlist'&&a.control==='lost')add('loss','Which requirement is no longer met?',[['burden','Tumor burden / AFP, without new invasion or extrahepatic spread'],['spread','New macrovascular invasion or extrahepatic spread']], 'New spread requires oncologic reassessment; an expanded-burden proposal does not waive this exclusion.');
 }
 if(slug==='pcca'){
  if(step==='phenotype'&&a.size==='large')add('mass_pattern','Which mass finding is present?',[['single-large','One mass with radial diameter ≥3 cm'],['multiple','Multiple separate masses']], 'Radial diameter is different from longitudinal duct involvement. Multiple masses are not a size-only expansion.');
  if(step==='neoadjuvant'&&a.protocol==='no')add('regimen','Why is the established neoadjuvant protocol not complete?',[['alternative','An alternative regimen is being considered or was used'],['incomplete','Established regimen is still underway / delivery needs review']], 'A temporary interruption or complication alone does not justify an alternative transplant regimen.');
  if(['phenotype','staging'].includes(step))add('nodes','Regional-node history',[['negative','No proven malignant nodes'],['positive','Previously proven malignant nodes, including after apparent clearance'],['suspicious','Suspicious / indeterminate nodes without proof']], 'Node sampling is different from a transperitoneal biopsy of the primary tumor.');
 }
 if(slug==='icca'){
  if(step==='phenotype'&&a.profile==='outside')add('outside','Which finding is outside the small-cirrhotic pathway?',[['larger','>3 cm, and no safe complete resection'],['noncirrhotic','Noncirrhotic liver, and no safe complete resection'],['both','>3 cm and noncirrhotic, with no safe complete resection'],['resectable','Safe complete resection is feasible']], 'Resectable disease should return to surgical treatment review.');
  if(step==='phenotype'&&a.focality==='multiple')add('focality','How are the additional malignant nodules distributed?',[['satellites','One dominant focus with adjacent peritumoral satellites'],['separate','Separate multifocal deposits across distinct segments']], 'This describes distribution. Satellites may represent intrahepatic spread; the label alone does not establish study eligibility or resectability.');
  if(step==='phenotype'&&(a.profile==='outside'||a.focality==='multiple')&&prior.extra?.outside!=='resectable')add('grade','Confirmed histology and grade for advanced-disease review',[['g12','Pure iCCA, G1–2'],['g3','Pure iCCA, G3 / poorly differentiated'],['mixed','Mixed HCC–iCCA']], 'The advanced proposal excludes mixed histology; this does not remove the separate small-cirrhotic guidance route.');
  if((step==='therapy'&&a.control==='progression')||(step==='stability'&&a.disease==='progression')){
   if(!prior.advanced)add('study_context','Which treatment pathway is being reassessed?',[['standard','Small-cirrhotic / NLRB guidance pathway'],['advanced','Advanced-iCCA study proposal']], 'The advanced-study salvage proposal does not replace the small-cirrhotic pathway or its observation requirements.');
   add('progression','What changed on reassessment?',[['first-liver','First confirmed liver-only progression'],['repeat-liver','Further progression after a salvage strategy'],['spread','Proven malignant nodes / extrahepatic spread'],['unclear','Finding remains indeterminate']], 'Only the defined advanced-study liver-only salvage scenario has a proposed re-entry review; no immediate transplant clearance follows.');
  }
  if(step==='review')add('donor','Is living-donor transplantation being considered?',[['no','No living-donor proposal'],['yes','Yes — a living-donor study is being considered']], 'Donor availability does not relax recipient selection or activate a study.');
 }
 if(slug==='crlm'){
  if((step==='unresectability'&&a.clearance==='uncertain')||['control','restaging'].includes(step))add('visible','What is the current interpretation of the treated liver lesions?',[['residual','Convincing residual disease remains'],['ned','No convincing visible disease on complete staging'],['uncertain','Scars / lesions remain indeterminate'],['failure','Irreversible treatment-related liver failure is the proposed indication']], 'PET negativity or a disappearing lesion alone does not establish no evidence of disease.');
  if(step==='biology'&&a.molecular==='outside')add('molecular','Which molecular result is outside the stated selection criteria?',[['braf','BRAF mutation'],['msi','MSI-H / dMMR'],['both','Both']], 'The local opening cohort keeps these separate research questions; use the relevant systemic-treatment pathway.');
 }
 if(slug==='nelm'){
  if(step==='biology'&&a.grade==='outside')add('grade_detail','Which pathology finding is established?',[['g3','Confirmed well-differentiated G3'],['nec','Confirmed poorly differentiated NEC'],['discordant','Borderline or discordant grading requires expert review']], 'Discordant tests require pathology review; they are not automatically a confirmed G3 or NEC diagnosis.');
  if(step==='options'&&a.strategy==='transplant')add('benefit','What requires additional transplant-benefit review?',[['symptoms','Refractory functioning syndrome'],['function','Liver-related functional compromise'],['threat','Credible threat to durable hepatic control despite reasonable alternatives'],['stable','Stable low-burden disease with reasonable durable alternatives'],['complete','Benefit comparison has been completed']], 'Favorable predicted survival alone does not establish additional benefit over available care.');
  if(['options','review'].includes(step)){
   add('age','Age at this review',[['younger','Under 60 years'],['older','60 years or older']], 'Age ≥60 calls for individual physiological-reserve and benefit review; it is not an absolute age exclusion.');
   add('burden','Estimated liver tumor involvement',[['low','Below 25%'],['reference','25% to <50%'],['expansion','50% through 70%'],['above','Above 70%']], 'These are local proposed review strata, not national age or burden limits.');
  }
 }
 if(slug==='hehe'&&step==='risk')add('tempo','Is observation sufficient, or is an earlier decision needed?',[['stable','Stable biology over the proposed observation period'],['short','Observation period is shorter / benefit remains uncertain'],['urgent','Threatening liver failure or significant progressive symptoms']], 'The proposed six-month default must not automatically delay urgent multidisciplinary review.');
 if(['crlm','nelm','hehe','hca'].includes(slug)&&step==='review'&&(a.reviews==='no'||is(a.criteria,'pending','lost')))add('review_reason','Which issue needs further review?',[['benefit','Expected benefit / treatment alternatives'],['selection','Disease-specific selection or allocation criteria'],['other','Incomplete tests, general fitness or another issue']], 'Show the review relevant to the actual unresolved issue; incomplete paperwork alone is not a high-risk phenotype.');
 for(const item of q)if(item.id==='ici_review')item.default=prior.iciStatus||'';
 return q;
}
function local(slug,step,a,x,history={}){
 const options=[],clarify=[];
 const add=(anchor,reason,mode='review',carry=false,blocks=false)=>options.push({anchor,reason,mode,carry,blocks,origin:step});
 const ask=(id,label)=>{if(!known(x[id])){clarify.push({id,label});return true;}return false;};
 if(slug==='hcc'){
  if(step==='allocation'&&a.burden==='beyond'){
   if(a.spread==='no')add('hcc-b1','The selected invasion/spread finding is outside this expanded-burden proposal.','closed',true,true);
   else if(a.spread!=='yes')clarify.push({label:'Confirm the absence of macrovascular invasion and extrahepatic disease before a beyond-UNOS study review.'});
   else add('hcc-b1',a.afp==='not-met'?'Original burden exceeds UNOS limits and the AFP requirement is not met. Continue treatment and reassessment; this is not clearance for the expanded cohort.':'Original pretreatment tumor burden exceeds UNOS downstaging limits.',a.afp==='not-met'?'notice':'review',true);
  }
  if(step==='curative-route'&&a.spread==='prior'&&!ask('history','Clarify prior portal-vein invasion versus rupture and the original invasion level.')){
   const excluded=x.history!=='vp12';add('hcc-b2',excluded?'The selected history is outside the initial Vp1–2 pilot; individual allocation review is a separate question.':'Previously treated Vp1–2 invasion needs the specific response, observation and selection review.',excluded?'closed':'review',true,excluded);
  }
  if(['treatment','listing','waitlist'].includes(step)&&is(x.ici,'planned','current','prior'))add('hcc-b3',x.ici==='planned'?'Immunotherapy is planned: coordinate treatment sequence and possible transplantation before exposure.':'Checkpoint immunotherapy exposure requires a transplant-safety assessment.','safety',true);
  if(['treatment','listing','waitlist'].includes(step)&&x.ici==='unknown')clarify.push({label:'Confirm checkpoint-inhibitor exposure before concluding that transplant-safety review is complete.'});
  if(step==='treatment'&&x.burden_history==='beyond'&&a.response!=='spread')add('hcc-b1','The original burden was beyond UNOS downstaging limits, even if the current response is favorable.','review',true);
  if(step==='waitlist'&&a.control==='lost')ask('loss','Clarify tumor-burden / AFP change versus new invasion or extrahepatic spread.');
 }
 if(slug==='pcca'){
  if(step==='diagnosis'&&a.biopsy==='yes')add('pcca-b1','Prior transperitoneal biopsy of the primary tumor was selected. This expansion remains closed.','closed',true,true);
  if(step==='phenotype'){
   if(a.size==='large'&&!ask('mass_pattern','Clarify a single oversized mass versus multiple masses.')&&x.mass_pattern==='single-large')add('pcca-b1','One mass has radial diameter ≥3 cm. Confirm the pretreatment measurement; this size expansion remains closed.','closed',true,true);
   if(a.unresectable==='no'&&a.spread!=='present')add('pcca-b2','Unresectability is not established: reassess safe complete resection and remnant optimization.','checklist');
  }
  if(step==='neoadjuvant'&&a.protocol==='no'&&a.status!=='spread'&&!ask('regimen','Clarify whether an alternative regimen is intended or the established regimen is simply incomplete.')&&x.regimen==='alternative')add('pcca-b3','An alternative neoadjuvant regimen is proposed or was used. These alternatives are not activated by this document.','closed',true,true);
  if(['phenotype','staging'].includes(step)){
   if(x.nodes==='positive')add('pcca-b1','Previously proven malignant nodes remain outside the initial proposal, even after apparent clearance.','closed',true,true);
   else if(x.nodes==='suspicious'||x.nodes==='unknown')clarify.push({label:'Resolve the nodal history; suspicion and proven malignant nodes are different findings.'});
  }
 }
 if(slug==='icca'){
  if(step==='phenotype'&&(a.profile==='outside'||a.focality==='multiple')){
   const unresolved=[];
   if(a.profile==='outside'&&!known(x.outside))unresolved.push('whether the finding is size, liver background or feasible resection');
   if(a.focality==='multiple'&&!known(x.focality))unresolved.push('adjacent satellites versus separate deposits');
   if(!known(x.grade))unresolved.push('histology and grade');
   if(a.spread!=='yes'&&a.spread!=='no')unresolved.push('nodal/extrahepatic status');
   if(x.outside==='resectable'){ /* Standard resection review remains the next action. */ }
   else if(a.spread==='no'||x.focality==='separate'||is(x.grade,'g3','mixed'))add('icca-b1','A selected finding is outside the initial advanced-iCCA pilot: separate multifocal deposits, G3/mixed histology, or nodal/extrahepatic disease.','closed',true,true);
   else if(unresolved.length)clarify.push({label:'Clarify '+unresolved.join('; ')+' before selecting the advanced-study review.'});
   else if(a.focality==='uncertain')clarify.push({label:'Characterize the additional nodule before an advanced-study review.'});
   else add('icca-b1','The selected unresectable larger/noncirrhotic or adjacent-satellite pattern needs the advanced-iCCA study review.','review',true);
  }
  if((step==='therapy'&&a.control==='progression')||(step==='stability'&&a.disease==='progression')){
   if(!history.advanced&&!known(x.study_context))clarify.push({label:'Clarify whether this is the small-cirrhotic pathway or the separate advanced-iCCA study proposal.'});
   if(!ask('progression','Distinguish first liver-only progression from repeat progression or proven nodal/extrahepatic spread.')){
    if(x.progression==='unclear')clarify.push({label:'Confirm whether progression is real and where it occurred before discussing salvage re-entry.'});
    else if(history.advanced||x.study_context==='advanced')add('icca-b2',x.progression==='first-liver'?'First liver-only progression in the advanced-study proposal: review salvage and renewed observation requirements. Transplantation cannot proceed during progression.':'Repeat progression or nodal/extrahepatic spread is outside the initial salvage re-entry proposal.',x.progression==='first-liver'?'notice':'closed',true,x.progression!=='first-liver');
   }
  }
  if(step==='stability'&&a.duration==='short'&&a.disease==='stable'&&history.advanced)add('icca-b2','The advanced-study observation interval is incomplete or its starting point is unresolved. This does not shorten the small-cirrhotic / NLRB pathway interval.','checklist');
  if(step==='review'&&x.donor==='yes')add('icca-b3','Living-donor study development was selected. This is a readiness review; donor availability does not permit protocol-directed transplantation.','readiness',true);
 }
 if(slug==='crlm'){
  if(step==='unresectability'&&a.clearance==='no')add('crlm-b1','Unresectability was selected. Confirm independent surgical review and the absence of a reasonable complete-clearance strategy.','checklist');
  if(step==='control'&&a.unresectable==='no')add('crlm-b1','Complete nontransplant clearance may now be possible. Reassess resection and ablation before further transplant planning.','checklist');
  if(step==='biology'){
   if(a.molecular==='outside'&&!ask('molecular','Clarify BRAF mutation versus MSI-H/dMMR before the molecular selection review.'))add('crlm-b3',x.molecular==='braf'?'BRAF mutation is outside the local opening cohort.':x.molecular==='msi'?'MSI-H/dMMR is outside the local opening cohort; review the appropriate systemic treatment.':'Both selected molecular findings are outside the local opening cohort.','closed',true,true);
   if(is(a.cea,'high','boundary'))add('crlm-b3','CEA is at or above the local proposed <80 boundary; repeat and review the trend. Local selection and NLRB guidance must be assessed separately.','notice',true);
   if(a.size==='no')add('crlm-b3','The pretreatment lesion-size criterion is not met; the initial proposal does not activate that expansion.','closed',true,true);
  }
  if(step==='map-disease'&&a.spread==='present')add('crlm-b3','Extrahepatic disease after primary resection or local relapse was selected. This does not open an expanded transplant route.','closed',true,true);
  if(step==='unresectability'&&a.clearance==='uncertain'&&!known(x.visible))clarify.push({label:'Clarify residual disease, no visible disease, or indeterminate treatment changes before a transplant review.'});
  if(['unresectability','control','restaging'].includes(step)&&known(x.visible)){
   if(x.visible==='residual'&&step==='unresectability')add('crlm-b1','Residual disease is suspected but complete nontransplant clearance remains disputed. Obtain the independent resectability review.','checklist');
   if(x.visible==='ned')add('crlm-b2','No convincing visible disease was selected. Transplantation solely for presumed microscopic disease is not offered by this proposal.','closed',true,true);
   if(x.visible==='uncertain'){clarify.push({label:'Resolve the treated-lesion interpretation; indeterminate scars are not automatically NED or unresectable viable disease.'});add('crlm-b2','Current residual disease is uncertain; review the diagnostic distinction before assigning a treatment route.','notice');}
   if(x.visible==='failure')add('crlm-b2','Assess a separate treatment-related liver-failure indication; do not relabel it active unresectable cancer.','notice',true);
  }
  if(step==='control'&&a.response==='progression')add('crlm-b3','Progression requires reassessment and renewed disease control; the proposal does not waive the control interval.','notice',true);
  if(step==='clocks'&&(a.interval==='no'||a.synchronous==='different'))add('crlm-b3','A required interval or treatment sequence is not met. Review the actual starting points; the proposal does not waive them.','checklist');
  if(step==='review'&&(a.criteria==='met'||x.review_reason==='benefit'))add('crlm-b4','Complete the individual benefit, recurrence-treatment and graft-use review before a transplant decision.','checklist');
 }
 if(slug==='nelm'){
  if(step==='biology'){
   if(a.grade==='outside'&&!ask('grade_detail','Resolve the grade and differentiation with expert pathology review.')){
    if(x.grade_detail==='discordant')clarify.push({label:'Resolve discordant pathology before assigning a grade-based transplant exclusion.'});
    else add('net-b2','Confirmed G3 or poorly differentiated NEC is outside the current opening pathway.','closed',true,true);
   }
   if(a.primary==='no')add('net-b2','The stated primary-site criterion is not met. Clarify the exact site before further transplant consideration.','notice',true);
  }
  if(step==='distribution'){
   if(is(a.spread,'active','solid'))add('net-b2','Active extrahepatic disease or prior lung/bone metastases is outside the current opening pathway.','closed',true,true);
   if(a.spread==='cleared')add('net-b2','Previously cleared extrahepatic disease requires review of the site, proof of clearance and disease-free interval.','checklist',true);
  }
  if(step==='observation'){
   if(a.clearance==='recurrence')add('net-b2','Extrahepatic recurrence or excluded lung/bone history does not open a transplant expansion.','closed',true,true);
   else if(a.clearance==='short'||a.control==='no')add('net-b2','Clearance or stable hepatic control has not met the required observation conditions.','checklist');
  }
  if(step==='options'){
   if(a.strategy==='other')add('net-b1','A feasible lower-risk treatment or durable disease-control option was preferred. Confirm the benefit comparison; do not automatically escalate to transplantation.','checklist');
   else if(a.strategy==='transplant'&&is(x.benefit,'symptoms','function','threat','stable'))add('net-b1',x.benefit==='stable'?'Stable low-burden disease with durable alternatives requires a convincing additional-benefit case before transplantation.':'A symptom, functional or durable-control concern calls for the specific benefit comparison.','checklist',true);
  }
  if(['options','review'].includes(step)){
   if(x.age==='older'||is(x.burden,'low','expansion','above'))add('net-b3',x.burden==='above'?'Liver involvement >70% is outside the local opening proposal, not a national declaration of futility.':x.burden==='expansion'?'Liver involvement of 50–70% belongs to a separate, unactivated expansion stratum.':x.burden==='low'?'Low liver burden calls for the benefit review; it does not by itself justify transplantation.':'Age ≥60 calls for individual reserve and benefit assessment, not an absolute age cutoff.',is(x.burden,'expansion','above')?'closed':'checklist',true,is(x.burden,'expansion','above'));
   if(x.review_reason==='benefit'||x.burden==='low')add('net-b1','Expected benefit over available nontransplant care needs review.','checklist');
   if(x.review_reason==='selection')add('net-b2','Clarify the disease-specific selection or clearance requirement that is not met.','checklist');
  }
 }
 if(slug==='hehe'){
  if(step==='stage'){
   if(a.vascular==='no'||a.extrahepatic==='limited')add('hehe-b2','Macrovascular invasion or limited extrahepatic disease needs the specific local-boundary review. The initial proposal is narrower than national case-level review.','closed',true,true);
   if(a.extrahepatic==='other')add('hehe-b2','Characterize the extrahepatic finding and disease behavior before selection.','notice',true);
  }
  if(step==='risk'&&(a.benefit==='uncertain'||is(x.tempo,'short','urgent')))add('hehe-b1',x.tempo==='urgent'?'Threatening liver failure or progressive symptoms require urgent multidisciplinary review; do not delay solely to complete six months.':'Observation, disease tempo or incremental benefit needs review. Stability alone does not mandate transplantation.','checklist',true);
  if(step==='review'&&x.review_reason==='benefit')add('hehe-b1','The expected benefit or observation plan remains unresolved.','checklist');
 }
 if(slug==='hca'){
  if(step==='standard-care'&&a.bleeding==='no'&&a.management==='no')add('hca-b2','No suitable conventional approach was selected; establish the clinical benefit and alternatives before considering transplantation.','checklist',true);
  if(step==='exception-route'&&a.route==='none')add('hca-b1','No listed NLRB guidance route was identified; multiplicity alone does not establish exception eligibility or transplant benefit.','notice',true);
  if(step==='review'&&x.review_reason==='benefit')add('hca-b2','Clinical benefit and feasible nontransplant alternatives still require review.','checklist');
  if(step==='review'&&x.review_reason==='selection')add('hca-b1','Identify the applicable guidance route separately from the clinical indication.','checklist');
 }
 return {options,clarify};
}
function hardStop(slug,step,a,x){
 const yes=(why)=>({origin:step,why,clinical:true});
 if(slug==='hcc'&&step==='diagnosis'&&a.diagnosis==='other')return yes('Establish the appropriate tumor-specific pathway before an HCC transplant review.');
 if(slug==='hcc'&&((step==='curative-route'&&a.spread==='excluded')||(step==='allocation'&&a.spread==='no')||(step==='treatment'&&a.response==='spread')))return yes('Selected active invasion, spread or rupture requires treatment and transplant reassessment before any expanded route.');
 if(slug==='hcc'&&step==='waitlist'&&x.loss==='spread')return yes('New invasion or extrahepatic spread requires oncologic reassessment; an expanded-burden proposal does not waive this finding.');
 if(slug==='hcc'&&step==='curative-route'&&a.spread==='prior'&&x.history==='vp4')return yes('Prior main/contralateral portal-vein or hepatic-vein tumor invasion is outside the defined invasion proposal. Continue oncologic and individual transplant review; do not infer a standard route.');
 if(slug==='pcca'&&step==='diagnosis'&&a.biopsy==='yes')return yes('Transperitoneal biopsy of the primary tumor does not meet the defined standard pCCA protocol. Program review does not waive the OPTN policy requirement.');
 if(slug==='pcca'&&step==='phenotype'&&a.size==='large')return yes('The selected original mass size or multiplicity does not meet the standard pCCA mass criterion. Review treatment and the applicable transplant protocol separately.');
 if(slug==='pcca'&&((step==='phenotype'&&a.spread==='present')||(step==='neoadjuvant'&&a.status==='spread')||(step==='staging'&&a.stage==='positive')||(step==='listing'&&a.ready==='spread')))return yes('Selected metastatic disease does not meet this pCCA transplant protocol.');
 if(slug==='icca'&&step==='phenotype'&&a.spread==='no')return yes('The selected nodal/extrahepatic finding does not meet this iCCA transplant proposal.');
 if(slug==='icca'&&step==='phenotype'&&a.profile==='outside'&&x.outside==='resectable')return yes('Safe complete resection was selected. Review resection before considering an advanced transplant study.');
 if(slug==='icca'&&step==='phenotype'&&(x.focality==='separate'||is(x.grade,'g3','mixed')))return yes('The selected focality or histology does not meet the advanced-iCCA proposal. Do not substitute the small-cirrhotic pathway for that review.');
 if(slug==='icca'&&['therapy','stability'].includes(step)&&x.progression==='spread')return yes('Proven nodal or extrahepatic spread does not meet the advanced-iCCA salvage proposal.');
 if(slug==='crlm'&&((step==='map-disease'&&a.spread==='present')||(step==='restaging'&&a.stage==='spread')))return yes('Selected extrahepatic disease or local relapse does not meet this CRLM pathway.');
 if(slug==='crlm'&&step==='biology'&&(a.molecular==='outside'||a.size==='no'))return yes('The selected molecular or pretreatment size finding does not meet the defined CRLM selection route. A later favorable response does not waive it.');
 if(slug==='crlm'&&x.visible==='ned')return yes('No convincing visible disease was selected. This proposal does not offer transplantation solely for presumed microscopic disease.');
 if(slug==='nelm'&&step==='biology'&&((a.grade==='outside'&&is(x.grade_detail,'g3','nec'))||a.primary==='no'))return yes('The selected grade or primary-site finding requires resolution before proceeding under this NET pathway.');
 if(slug==='nelm'&&((step==='distribution'&&is(a.spread,'active','solid'))||(step==='observation'&&a.clearance==='recurrence')))return yes('The selected extrahepatic finding does not meet the current NET opening pathway.');
 if(slug==='hca'&&((step==='characterize'&&a.diagnosis==='bleeding')||(step==='standard-care'&&a.bleeding==='yes')))return yes('Treat unstable hemorrhage before elective transplant assessment.');
 if(slug==='hehe'&&step==='diagnosis'&&a.pathology==='angiosarcoma')return yes('Angiosarcoma is not the HEHE transplant pathway; return to diagnosis-specific treatment.');
 if(slug==='hehe'&&step==='stage'&&a.vascular==='no')return yes('Macrovascular invasion does not meet the stated HEHE exception-guidance criterion. Review clinical suitability and any individual allocation request separately before continuing.');
 return null;
}
function evaluate(pathway,index,session,context={},configs={}){
 const slug=pathway.slug,step=pathway.steps[index].id,key=slug+'/'+step;
 if(post.has(key))return {options:[],clarify:[],questions:[],guard:null,route:null};
 const candidates=[],stops=[],unresolved=[];let current,priorAdvanced=false;const history={advanced:false,iciStatus:null};
 for(let i=0;i<=index;i++){
  const s=pathway.steps[i].id,k=slug+'/'+s,a=session.answers[k]||{},x=context[k]||{};
  if(i===index)priorAdvanced=history.advanced;
  if(is(x.ici,'planned','current','prior'))history.iciStatus=x.ici_review||'pending';
  else if(x.ici_review)history.iciStatus=x.ici_review;
  if(i<index&&Object.keys(a).length&&(configs[k]?.questions||[]).some(q=>!a[q.id]||a[q.id]==='unknown'))unresolved.push({origin:s,label:'An earlier essential finding is unresolved. Review that decision before choosing a proposed transplant review.'});
  const found=local(slug,s,a,x,history);if(i===index)current=found;else for(const question of found.clarify)unresolved.push({...question,origin:s});
  if(found.options.some(o=>o.anchor==='icca-b1'&&o.mode==='review')||x.study_context==='advanced')history.advanced=true;
  for(const option of found.options)if(i===index||(option.carry&&coverage[option.anchor]?.includes(step)))candidates.push({...option,carried:i!==index});
  const stop=hardStop(slug,s,a,x);if(stop)stops.push(stop);
 }
 const mixed=session.answers['icca/diagnosis']?.histology==='mixed';
 const originalBurden=session.answers['hcc/allocation']?.burden;
 const knownBurden=is(originalBurden,'t2','t1','ds','beyond');
 const repeatedBurden=context['hcc/treatment']?.burden_history;
 if(slug==='hcc'&&knownBurden&&known(repeatedBurden)&&((originalBurden==='beyond')!==(repeatedBurden==='beyond')))unresolved.push({origin:'allocation',label:'Pretreatment burden has conflicting selections. Correct the original burden at decision 3 before continuing.'});
 if(slug==='icca'&&mixed&&candidates.some(o=>o.anchor==='icca-b1'&&o.mode==='review'))stops.push({origin:'diagnosis',why:'Mixed histology is not included in the advanced-iCCA pilot; assess the separate small-cirrhotic route when applicable.'});
 const combined=slug==='hcc'&&candidates.some(o=>o.anchor==='hcc-b1')&&candidates.some(o=>o.anchor==='hcc-b2');
 if(combined){
  stops.push({origin:'curative-route',why:'The expanded-burden and prior-invasion proposals cannot be combined. Review the original burden and vascular history together; individual NLRB consideration and treatment options remain separate.'});
  candidates.filter(o=>is(o.anchor,'hcc-b1','hcc-b2')).forEach(o=>{o.mode='notice';o.reason+=' The two local expansion proposals cannot be combined.';});
 }
 const hard=[...stops].reverse().find(s=>s.clinical)||stops[stops.length-1];
 const out=[];
 for(const option of candidates){
  if(hard&&is(option.mode,'review','readiness'))continue;
  if(!out.some(x=>x.anchor===option.anchor))out.push(option);
  else {const old=out.find(x=>x.anchor===option.anchor);if(option.mode==='closed')Object.assign(old,option);}
 }
 const blocked=out.find(o=>o.blocks);
 const a=session.answers[key]||{};
 const beyond=out.some(o=>o.anchor==='hcc-b1'&&o.carried);
 const ici=out.find(o=>o.anchor==='hcc-b3');
 const iciComplete=ici&&history.iciStatus==='complete';
 if(iciComplete){ici.mode='safety-note';ici.reason+=' The transplant team review is marked complete for this scenario; follow the agreed plan. This does not guarantee safety or approve transplantation.';}
 const finalReview=ici&&!iciComplete&&['listing','waitlist'].includes(step)?{origin:step,why:'The known immunotherapy exposure or plan still needs a transplant-team safety and sequencing review.'}:null;
 const nonstandard=out.find(o=>is(o.anchor,'hcc-b1','hcc-b2','pcca-b1','pcca-b3','icca-b1','icca-b2','icca-b3','hca-b1'))||out.find(o=>o.anchor==='crlm-b3'&&o.reason.startsWith('CEA'))||out.find(o=>o.anchor==='hehe-b2'&&session.answers['hehe/stage']?.vascular==='no');
 const routeText={
  hcc:'Continue case-specific transplant and allocation review. The original burden or invasion history is not erased by a current T2 response; standardized exception eligibility must not be assumed.',
  pcca:'Continue case-specific protocol review with the earlier finding visible. Neither an alternative regimen nor apparent clearance of previously malignant nodes activates a closed local expansion or establishes standardized exception eligibility.',
  icca:'Continue the separate iCCA study assessment. The small-cirrhotic exception pathway does not establish eligibility for an advanced or living-donor study proposal; approvals and its own selection requirements remain necessary.',
  crlm:'Continue individual CRLM review with the earlier CEA finding visible. A later favorable staging result does not resolve the CEA requirement.',
  hehe:'Macrovascular invasion does not meet the stated HEHE exception-guidance criterion. Clinical suitability and any individual allocation request require separate expert review.',
  hca:'No listed HCA exception-guidance route was identified earlier. Assess the clinical indication and any individual allocation request separately; do not infer exception eligibility from a favorable later review.'
 };
 const route=nonstandard?{origin:nonstandard.origin,why:routeText[slug]}:null;
 const unknown=unresolved[0]?{origin:unresolved[0].origin,why:unresolved[0].label}:null;
 const clarify=[...(current?.clarify||[]),...unresolved];
 const incomplete=(configs[key]?.questions||Object.keys(a).map(id=>({id}))).some(q=>!a[q.id]||a[q.id]==='unknown');
 // Review navigation is conditional; it never fills in missing clinical facts.
 const deferred=!!(incomplete||clarify.length||hard||blocked);
 if(deferred&&out.some(o=>is(o.mode,'review','readiness'))&&!hard&&!blocked)clarify.push({label:'Complete or clarify the essential findings before choosing proposed study options. Known safety findings are shown separately.'});
 const visible=deferred?out.filter(o=>!is(o.mode,'review','readiness')).map(o=>o.mode==='safety'?{...o,mode:'safety-note',reason:o.reason+' Keep this safety issue visible while the other findings are clarified; it does not establish transplant eligibility.'}:o):out;
 const currentUnknown=clarify.length?{origin:step,why:clarify[0].label}:null;
 return {options:visible,clarify,questions:questions(slug,step,a,{beyond,knownBurden,advanced:priorAdvanced,ici:!!ici,iciStatus:history.iciStatus,extra:context[key]||{}}),guard:hard||unknown||currentUnknown||finalReview,route};
}
function renderQuestions(qs,values={}){
 if(!qs.length)return '';
 return `<section class="risk-questions" aria-label="Findings that select a specific review"><h4>Additional findings that may change the next step</h4>${qs.map(q=>`<div class="risk-question"><label for="risk-${esc(q.id)}">${esc(q.label)}</label><select id="risk-${esc(q.id)}" data-risk-question="${esc(q.id)}"><option value="">Choose if applicable…</option>${q.options.map(([v,label])=>`<option value="${esc(v)}" ${(values[q.id]??q.default)===v?'selected':''}>${esc(label)}</option>`).join('')}</select><p>${esc(q.help)}</p></div>`).join('')}</section>`;
}
function clearFrom(context,pathway,index){pathway.steps.slice(index).forEach(s=>delete context[pathway.slug+'/'+s.id]);}
const API={questions,local,evaluate,renderQuestions,clearFrom,coverage,referenceOnly};
if(typeof module==='object'&&module.exports)module.exports=API;else root.RiskRouting=API;
})(typeof window==='undefined'?{}:window);
