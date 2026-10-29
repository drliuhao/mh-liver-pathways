/* Present the reconciled high-risk proposals within the standard protocol.
 * This module does not change eligibility rules, answers, or example presets. */
'use strict';
const HighRisk = (() => {
 const e=s=>String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
 const link=(url,label,cls='')=>`<a href="${e(url)}" class="${cls}" target="_blank" rel="noopener">${e(label)} ↗</a>`;
 const list=items=>`<ul>${items.map(x=>`<li>${e(x)}</li>`).join('')}</ul>`;
 const text=v=>Array.isArray(v)?list(v):`<p>${e(v)}</p>`;
 const pathway=(data,slug)=>data.pathways[slug];
 const reviews=(data,slug,step)=>pathway(data,slug).reviews.filter(r=>!step||r.steps.includes(step));
 const keys=(data,slug)=>[...new Set(reviews(data,slug).flatMap(r=>r.references))];
 const badge=()=>'<span class="high-risk-label">High-risk protocol</span>';
 // Presentation labels describe the review, never patient eligibility or activation.
 const states={
  'hcc-b1-1':['review','AFP-only review · OPEN'],
  'hcc-b1':['proposal','Proposed study · not active'],
  'hcc-b2':['mixed','Different limits by invasion level'],
  'hcc-b3':['proposal','Proposed safety approach'],
  'hcc-b4':['research','Research use only'],
  'pcca-b1':['closed','Expansion closed'],
  'pcca-b2':['review','Review the standard treatment'],
  'pcca-b3':['closed','Alternative regimens not activated'],
  'icca-b1':['proposal','Proposed study · not active'],
  'icca-b2':['proposal','Proposed response requirements'],
  'icca-b3':['research','Study development · no transplantation yet'],
  'crlm-b1':['review','Review the standard treatment'],
  'crlm-b2':['closed','No transplant for presumed microscopic disease'],
  'crlm-b3':['mixed','Initial selection and expansion limits'],
  'crlm-b4':['review','Review expected benefit'],
  'net-b1':['review','Review expected benefit'],
  'net-b2':['review','Review initial selection limits'],
  'net-b3':['mixed','Individual review · expansion not activated'],
  'hehe-b1':['review','Review timing and need for transplant'],
  'hehe-b2':['mixed','Initial selection and expansion limits'],
  'hca-b1':['review','Review allocation separately'],
  'hca-b2':['review','Review the clinical indication'],
  'hcc-b5':['closed','Closed · registry only'],
  'icca-b4':['closed','Closed'],
  'crlm-b5':['mixed','Closed · lung-only study proposed'],
  'net-b4':['mixed','Resected nodes only, after clearance']
 };
 const ruleLabels={
  'hcc-b1':['Entry criteria','Response and reassessment','History and exclusions'],
  'hcc-b2':['Invasion level','Response and observation','Review and exclusions'],
  'hcc-b3':['Interval after immunotherapy','Immune toxicity','Exceptional review','Consent and evidence limits'],
  'pcca-b1':['Radial tumor size','Primary-tumor biopsy','Previously malignant nodes','Distant or peritoneal disease'],
  'hcc-b5':['Meaning of “no extrahepatic disease”','Nodes and resolved findings','Registry','No combination'],
  'icca-b4':['Previous nodes or distant disease','Indeterminate nodes','Nodal staging before listing','Future research'],
  'crlm-b5':['Default','Proposed lung-only stratum','No other relaxation','Closed sites'],
  'net-b4':['Resected nodes','Non-surgical clearance','Solid-organ metastases','Progression and surgery'],
  'hehe-b2':['Opening boundary','Suspicious lesions and scores','Proposed extrahepatic stratum','Closed extrahepatic sites']
 };
 const cautions={
  'hcc-b1':'Transplant benefit in selected responders does not validate the proposed combination of expanded-entry limits and observation time.',
  'hcc-b2':'Small selected series do not establish benefit for each invasion level. Disease control does not remove recurrence risk.',
  'hcc-b3':'No washout interval guarantees immune safety. Prior toxicity, rejection and graft loss must be considered separately from tumor response.',
  'hcc-b4':'A prognostic model is not a validated treatment-benefit or allocation rule for these expanded populations.',
  'pcca-b1':'Size and biopsy associations do not establish causation. Evidence does not validate transplantation after clearance of previously malignant nodes.',
  'pcca-b2':'Selected recipient outcomes do not establish superiority over resection. Dropout and differences in selection affect comparisons.',
  'pcca-b3':'Feasibility with an alternative regimen does not establish equivalent survival or safety. Comparative evidence is very limited.',
  'icca-b1':'Small selected series do not validate a universal size or lesion-count limit, or establish comparative benefit in advanced iCCA.',
  'icca-b2':'Sustained control supports selection, but the optimal duration and permitted salvage treatment remain uncertain.',
  'icca-b3':'Selected recipient survival does not establish causal benefit from living-donor transplantation or resolve the healthy-donor risk tradeoff.',
  'crlm-b1':'Randomized benefit applies to a restricted population. It does not establish a universal unresectability threshold or require HAI for every candidate.',
  'crlm-b2':'Imaging can miss viable tumor. That diagnostic finding does not prove that transplantation benefits patients with no visible disease.',
  'crlm-b3':'Prognostic markers and outcomes in selected recipients do not validate benefit from broadening molecular or extrahepatic-disease criteria.',
  'crlm-b4':'Recurrence and meaningful survival benefit can coexist. Individual benefit estimates and broader graft-use strategies remain uncertain.',
  'net-b1':'Good predicted recipient survival alone does not establish additional benefit over available treatment or surveillance.',
  'net-b2':'Evidence for expanding grade, primary-site or extrahepatic-disease criteria is very limited; allocation guidance remains a separate assessment.',
  'net-b3':'Age and tumor burden inform review, but the proposed thresholds are not validated universal boundaries of transplant benefit.',
  'hehe-b1':'Selected post-transplant survival does not prove that a fixed observation period improves outcomes. Urgent clinical needs require separate assessment.',
  'hehe-b2':'Prognostic associations do not establish benefit from transplanting extrahepatic disease; explant findings cannot be assumed before transplantation.',
  'hca-b1':'Meeting an NLRB recommendation does not itself establish a clinical indication or comparative benefit from transplantation.',
  'hca-b2':'Favorable outcomes in selected recipients do not prove benefit over feasible nontransplant treatment.',
  'hcc-b5':'One case report cannot establish safety or benefit after metastatic HCC, even with a complete response to immunotherapy.',
  'icca-b4':'No study has tested transplantation after previously malignant nodes or treated distant disease in iCCA.',
  'crlm-b5':'Indolent lung recurrence after transplantation does not show benefit from transplanting after treated lung metastases; direct evidence is one patient.',
  'net-b4':'Accepting resected nodes rests on selected Milan practice; previous nodal disease still carries recurrence risk, and the solid-organ exclusion rests on guidance rather than outcome data.',
  'alloc-b1':'Clinical suitability, allocation access, donor clearance and research authorization answer separate questions.',
  'alloc-b2':'Acceptable recipient survival does not establish incremental benefit or account for the opportunity cost of graft use.',
  'alloc-b3':'Population donor-risk estimates do not predict an individual donor’s outcome or replace independent donor review.',
  'alloc-b4':'Small pilot survival estimates cannot establish efficacy or justify automatic expansion; the proposed stopping rules require independent review.'
 };
 const sourceKinds={consort_pilot:'Reporting guideline',optn:'OPTN policy',nlrb:'NLRB guidance',hhs_irb:'Research regulation',optn_ethics:'Ethics guidance',aasld:'Clinical guidance',acg_fll2024:'Clinical guideline',candidate2026:'Clinical guideline',dgvs_lt2024:'Clinical guideline',easl_benign:'Clinical guideline',ehe_consensus:'Consensus statement',enets:'Position statement',hcc_design:'Consensus statement',ihpba:'Consensus guideline',ilts:'Consensus recommendations',cirse:'Technical guidance',crlm_seca3:'Trial registration',crlm_fukumitsu:'Study protocol'};
 const sourceKind=r=>sourceKinds[r.key]||'Published research';
 const statusLabel=anchor=>states[anchor]?.[1]||'Local review · approval pending';
 const isResearch=r=>sourceKind(r)==='Published research';
 const typeLabel=r=>`<span class="hr-source-type">${e(sourceKind(r))}</span>`;
 function citation(r){return [r.author,r.journal,r.year].filter(Boolean).map(e).join(' · ');}
 function access(r){
  const buttons=r.pdf_links.map(x=>link(x.url,x.label,'hr-source-link hr-pdf'));
  buttons.push(link(r.url,'Article / official source','hr-source-link'));
  if(r.tmc)buttons.push(link(r.tmc,'TMC Library access','hr-source-link'));
  return `<div class="hr-source-actions">${buttons.join('')}</div>${r.pdf_links.length?'':'<p class="hr-access-note">No direct PDF link confirmed. Use the article or TMC Library link to access full text.</p>'}`;
 }
 function source(r,compact=false){
  return `<div class="hr-source ${compact?'hr-source-compact':''}" data-evidence-item data-source-key="${e(r.key)}">${typeLabel(r)}<p class="hr-citation">${citation(r)||e(r.short)}</p>${compact?'':`<h4>${e(r.title)}</h4>`}<p class="hr-identifiers">${r.pmid?link('https://pubmed.ncbi.nlm.nih.gov/'+r.pmid+'/','PMID '+r.pmid):''}${r.pmid&&r.doi?' · ':''}${r.doi?link('https://doi.org/'+r.doi,'DOI '+r.doi):''}</p>${r.review_depth?`<p class="hr-review-depth"><b>Review coverage:</b> ${e(r.review_depth)}</p>`:''}${access(r)}</div>`;
 }
 function downloads(data,slug){return `<div class="hr-documents">${pathway(data,slug).documents.map(d=>link(d.url,d.label,d.format==='pdf'?'hr-document hr-pdf':'hr-document')).join('')}</div>`;}
 function prompt(data,slug,step){
  const rs=reviews(data,slug,step);if(!rs.length)return '';
  return `<aside class="high-risk-prompt" aria-label="High-risk protocols related to this decision">${badge()}<div><p>Also review here when relevant:</p><div class="hr-jump-links">${rs.map(r=>`<a href="#high-risk-${r.anchor}" data-high-risk="${r.anchor}">${e(r.title)} ↓<small>${e(statusLabel(r.anchor))}</small></a>`).join('')}</div></div></aside>`;
 }
 function distribution(){return `<details class="hr-definition"><summary>iCCA: satellite nodules, multifocal disease and intrahepatic metastases</summary><dl><dt>One mass with adjacent satellite nodules</dt><dd>A dominant mass with nearby peritumoral nodules. Record their exact relationship and location; nearby nodules may still represent spread within the liver.</dd><dt>Multifocal disease</dt><dd>Separate tumor foci, including lesions in other liver segments. This describes the imaging pattern; it does not establish whether the tumors arose independently.</dd><dt>Intrahepatic metastases</dt><dd>Spread from the primary tumor to other locations in the liver. This is a biological interpretation based on imaging, pathology and the clinical course, rather than a synonym for every additional nodule.</dd></dl><p>The initial advanced-disease proposal permits one mass-forming focus with adjacent peritumoral satellites. It excludes separate multifocal tumors in different segments. Preserve the lesion map and any uncertainty; this is a proposed study limit, not a universal transplant rule.</p></details>`;}
 function study(data,s){
  const r=data.sources[s.key];
  return `<article class="hr-study" data-study-key="${e(s.key)}"><header class="hr-study-heading"><h5>${e(r?.short||s.key)}</h5>${r?typeLabel(r):''}</header>${r?.review_depth?`<p class="hr-review-depth"><b>Review coverage:</b> ${e(r.review_depth)}</p>`:''}<div class="hr-study-grid">${['design_population','selection','results','limits','limitations'].filter(k=>s[k]).map(k=>`<section class="hr-study-row hr-field-${k}"><h6>${({design_population:'Who was studied?',selection:'Selection and applicability',results:'Results · retain the stated population and time origin',limits:'Limitations and conflicting findings',limitations:'Limitations and conflicting findings'})[k]}</h6>${text(s[k])}</section>`).join('')}</div>${s.locator?`<p class="hr-locator">Source location: ${e(s.locator)}</p>`:''}${r?`<div class="hr-study-access" data-source-key="${e(s.key)}"><p class="hr-citation">${citation(r)}</p><p class="hr-identifiers">${r.pmid?link('https://pubmed.ncbi.nlm.nih.gov/'+r.pmid+'/','PMID '+r.pmid):''}${r.pmid&&r.doi?' · ':''}${r.doi?link('https://doi.org/'+r.doi,'DOI '+r.doi):''}</p>${access(r)}</div>`:''}</article>`;
 }
 function next(r,slug){
  if(r.anchor==='hcc-b1-1')return 'Confirm the AFP signal, complete staging and obtain individual clinical/allocation review. The proposed biochemical hold and release thresholds remain OPEN. A research expansion, if proposed, needs separate approval; ordinary case review does not itself enroll a study.';
  if(r.anchor==='hcc-b4')return 'Use the model for research and prospective validation only. Make listing, treatment and allocation decisions through the standard multidisciplinary assessment; do not use this model to award priority or determine eligibility.';
  if(r.anchor==='icca-b3')return 'Complete the proposed study, recipient-benefit and independent donor reviews before seeking activation. This proposal does not yet permit transplantation; continue appropriate nontransplant treatment and reassessment.';
  if(r.anchor==='pcca-b3')return 'Use the established center neoadjuvant protocol when clinically appropriate. Alternative regimens remain unactivated and require separate review; do not substitute them automatically.';
  if(slug==='hca')return 'Review the remaining nontransplant options with the liver team. If a clear transplant benefit is not established, agree treatment or surveillance through the standard adenoma pathway.';
  if(['pcca-b1','crlm-b2','hcc-b5','icca-b4'].includes(r.anchor))return 'These findings do not open a transplant route under this proposal. Clarify any uncertain finding, then choose another treatment or surveillance plan when transplantation remains unsuitable.';
  return 'Review the findings with the transplant multidisciplinary team. A proposed expanded route requires the relevant clinical, allocation, donor and study approvals before use. Continue appropriate treatment and reassess while that decision is pending.';
 }
 function card(data,slug,r,shared=false){
  const ev=r.evidence,papers=ev.studies||[],count=r.references.length;
  const [state,status]=states[r.anchor]||['proposal','Proposed operating requirement'];
  const additional=r.references.filter(k=>!papers.some(s=>s.key===k));
  return `<article class="hr-protocol hr-state-${state}" id="high-risk-${r.anchor}" aria-labelledby="title-${r.anchor}"><div class="hr-card-top"><span class="hr-status">${e(status)}</span>${badge()}<span class="hr-code">${e(r.id)}</span></div><h3 id="title-${r.anchor}" tabindex="-1">${e(r.title)}</h3><p class="hr-context"><b>When this applies:</b> ${e(r.context||r.stance)}</p><div class="hr-position"><span class="hr-source-type">Local review · institutional approval pending</span><p><b>Proposed position:</b> ${e(r.stance)}</p></div>
  ${r.anchor==='hcc-b1-1'?'<p><a href="/mh-liver-pathways/transplant/meeting-records/hcc-b1-1/">B1.1a–f: source comparisons and meeting decisions</a></p>':''}<div class="hr-next"><h4>Next step</h4><p>${e(next(r,slug))}</p><div class="hr-next-links">${r.steps.length?`<button data-step="${e(r.steps[0])}">Return to the standard decision →</button>`:''}${!shared?'<a href="#high-risk-readiness" data-high-risk="readiness">Approvals required before study use →</a>':''}<a href="#care-treatment" data-care="treatment">Treatment and continuing care →</a></div></div>
  <details class="hr-criteria" open><summary>Clinical criteria and limits <span>${r.rules.length} requirements · recorded status: ${e(r.status)}</span></summary><ol class="hr-rule-grid">${r.rules.map((rule,n)=>`<li><b>${e(ruleLabels[r.anchor]?.[n]||`Requirement ${n+1}`)}</b><p>${e(rule)}</p></li>`).join('')}</ol>${r.anchor==='icca-b1'?distribution():''}</details>
  <div class="hr-interpretation"><section class="hr-allocation"><h4>Allocation and donor considerations</h4>${text(r.allocation)}<div class="hr-authority-links"><span>Check current requirements separately:</span>${['optn','nlrb'].filter(k=>data.sources[k]).map(k=>link(data.sources[k].url,sourceKind(data.sources[k]))).join('')}</div></section><section class="hr-certainty"><h4>What remains uncertain?</h4><p>${e(cautions[r.anchor]||ev.certainty)}</p></section></div>
  <details class="hr-information"><summary>Tests and information needed</summary>${text(r.tests)}</details>
  <details class="hr-rationale"><summary>Why this position? Evidence and uncertainty</summary><div class="hr-evidence-pair">${['synthesis','counterevidence'].filter(k=>ev[k]).map(k=>`<section class="hr-evidence-summary"><h4>${k==='synthesis'?'What supports the position':'Findings that limit or challenge it'}</h4>${text(ev[k])}</section>`).join('')}</div>${['certainty','threshold_basis','policy_context'].filter(k=>ev[k]).map(k=>`<section class="hr-evidence-summary"><h4>${k==='certainty'?'Certainty by claim · informal assessment':k==='threshold_basis'?'Where the thresholds come from':'Allocation policy and review guidance'}</h4>${text(ev[k])}</section>`).join('')}<p class="hr-access-note">These are informal certainty assessments, not formal GRADE ratings.</p></details>
  <details class="hr-evidence"><summary>Studies and full-text access <span>${papers.length} study summaries · ${count} distinct sources</span></summary><div class="hr-evidence-body"><p class="hr-reading-note"><b>Read each result with its population and starting point.</b> Outcomes after transplantation, outcomes from treatment entry and comparative survival benefit answer different questions. Overlapping cohorts must not be counted as independent studies. Source type is not an evidence grade.</p><div class="hr-study-tools"><label for="find-${r.anchor}">Find a study or result</label><input id="find-${r.anchor}" type="search" data-study-search placeholder="Author, trial, outcome or limitation…"><span role="status" data-study-count>${papers.length} study summaries</span></div><div class="hr-study-list">${papers.map(s=>study(data,s)).join('')}</div>${additional.length?`<section class="hr-additional"><h4>Additional sources</h4><p>These ${additional.length} sources are not repeated in the study summaries above.</p>${additional.map(k=>source(data.sources[k])).join('')}</section>`:''}<p class="hr-access-note">PDF links open a paper or author manuscript; TMC Library may require UTHealth sign-in. PDF availability and the depth of the prior review are separate.</p></div></details></article>`;
 }
 function inline(data,slug,step){
  const rs=reviews(data,slug,step);if(!rs.length)return '';
  return `<section class="high-risk-section" aria-labelledby="hr-inline-title"><div class="hr-section-heading"><div><p class="hr-eyebrow">Within this transplant protocol</p><h2 id="hr-inline-title">High-risk protocols at this decision</h2><p>Review the proposed criteria, evidence and next steps below. Each option retains its stated limits and approval status.</p></div><a href="#high-risk" data-view="high-risk" class="hr-overview-link">All high-risk protocols for this tumor →</a></div>${rs.map(r=>card(data,slug,r)).join('')}${downloads(data,slug)}</section>`;
 }
 function overview(data,slug){
  const rs=reviews(data,slug);
  return `<section class="high-risk-view" aria-labelledby="high-risk-title"><div class="hr-section-heading"><div>${badge()}<h2 id="high-risk-title" tabindex="-1">High-risk protocols within the ${e(slug==='nelm'?'NELM':slug==='pcca'?'pCCA':slug==='icca'?'iCCA':slug.toUpperCase())} pathway</h2><p>Clinical reviews appear with matching next-step choices when the relevant findings are selected. Research-only models remain references. Orange identifies a proposed high-risk option; closed local expansions are explanatory notices. No proposal is activated by this website.</p></div></div>${downloads(data,slug)}<nav class="hr-index" aria-label="High-risk protocol decisions">${rs.map(r=>`<a href="#high-risk-${r.anchor}" data-high-risk="${r.anchor}">${e(r.title)} →<small>${e(statusLabel(r.anchor))}</small></a>`).join('')}<a href="#high-risk-readiness" data-high-risk="readiness">Shared approval requirements →</a></nav>${rs.map(r=>card(data,slug,r)).join('')}<section class="hr-readiness" id="high-risk-readiness"><h2 tabindex="-1">Before a proposed study can open</h2><p>Recipient selection, allocation, donor protection and institutional study approval are separate decisions.</p>${data.readiness.map(r=>card(data,slug,r,true)).join('')}</section></section>`;
 }
 function library(data,slug){
  const sources=keys(data,slug).map(k=>data.sources[k]);
  return `<section class="hr-library"><div class="hr-section-heading"><div>${badge()}<h2>Evidence for the high-risk protocols</h2><p>Start with the clinical question; open its study summaries for outcomes and limitations. Document types below describe authority, not evidence grades.</p></div><a href="#high-risk" data-view="high-risk">Open the high-risk protocols →</a></div>${downloads(data,slug)}${[['Policy, guidance and consensus',sources.filter(r=>!isResearch(r))],['Published research',sources.filter(isResearch)]].filter(([,rows])=>rows.length).map(([label,rows])=>`<section class="hr-library-group"><h3>${label}</h3><div class="hr-library-grid">${rows.map(r=>source(r)).join('')}</div></section>`).join('')}</section>`;
 }
 function destination(url){
  if(!url)return null;
  const m=url.match(/\/transplant\/high-risk\/(?:([a-z]+)\/)?(?:#([\w-]+))?$/);
  return m?{slug:m[1]||null,id:m[2]==='readiness'?'readiness':m[2]||''}:null;
 }
 return {reviews,keys,badge,prompt,inline,overview,library,downloads,destination,statusLabel,card};
})();
if(typeof module!=='undefined')module.exports=HighRisk;
