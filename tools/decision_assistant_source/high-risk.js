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
 function citation(r){return [r.author,r.journal,r.year].filter(Boolean).map(e).join(' · ');}
 function access(r){
  const buttons=r.pdf_links.map(x=>link(x.url,x.label,'hr-source-link hr-pdf'));
  buttons.push(link(r.url,'Article / official source','hr-source-link'));
  if(r.tmc)buttons.push(link(r.tmc,'TMC Library access','hr-source-link'));
  return `<div class="hr-source-actions">${buttons.join('')}</div>${r.pdf_links.length?'':'<p class="hr-access-note">No direct PDF link confirmed. Use the article or TMC Library link to access full text.</p>'}`;
 }
 function source(r,compact=false){
  return `<div class="hr-source ${compact?'hr-source-compact':''}"><p class="hr-citation">${citation(r)}</p>${compact?'':`<h4>${e(r.title)}</h4>`}<p class="hr-identifiers">${r.pmid?link('https://pubmed.ncbi.nlm.nih.gov/'+r.pmid+'/','PMID '+r.pmid):''}${r.pmid&&r.doi?' · ':''}${r.doi?link('https://doi.org/'+r.doi,'DOI '+r.doi):''}</p>${access(r)}</div>`;
 }
 function downloads(data,slug){return `<div class="hr-documents">${pathway(data,slug).documents.map(d=>link(d.url,d.label,d.format==='pdf'?'hr-document hr-pdf':'hr-document')).join('')}</div>`;}
 function prompt(data,slug,step){
  const rs=reviews(data,slug,step);if(!rs.length)return '';
  return `<aside class="high-risk-prompt" aria-label="High-risk protocols related to this decision">${badge()}<div><p>Also review here when relevant:</p><div class="hr-jump-links">${rs.map(r=>`<a href="#high-risk-${r.anchor}" data-high-risk="${r.anchor}">${e(r.title)} ↓</a>`).join('')}</div></div></aside>`;
 }
 function distribution(){return `<details class="hr-definition"><summary>iCCA: satellite nodules, multifocal disease and intrahepatic metastases</summary><dl><dt>One mass with adjacent satellite nodules</dt><dd>A dominant mass with nearby peritumoral nodules. Record their exact relationship and location; nearby nodules may still represent spread within the liver.</dd><dt>Multifocal disease</dt><dd>Separate tumor foci, including lesions in other liver segments. This describes the imaging pattern; it does not establish whether the tumors arose independently.</dd><dt>Intrahepatic metastases</dt><dd>Spread from the primary tumor to other locations in the liver. This is a biological interpretation based on imaging, pathology and the clinical course, rather than a synonym for every additional nodule.</dd></dl><p>The initial advanced-disease proposal permits one mass-forming focus with adjacent peritumoral satellites. It excludes separate multifocal tumors in different segments. Preserve the lesion map and any uncertainty; this is a proposed study limit, not a universal transplant rule.</p></details>`;}
 function study(data,s){
  const r=data.sources[s.key];
  return `<details class="hr-study"><summary>${e(r?.short||s.key)}</summary>${r?source(r,true):''}${['design_population','selection','results','limits','limitations'].filter(k=>s[k]).map(k=>`<div class="hr-study-row"><b>${({design_population:'Design and population',selection:'Selection',results:'Results',limits:'Limitations',limitations:'Limitations'})[k]}</b>${text(s[k])}</div>`).join('')}${s.locator?`<p class="hr-locator">Source location: ${e(s.locator)}</p>`:''}</details>`;
 }
 function next(r,slug){
  if(slug==='hca')return 'Review the remaining nontransplant options with the liver team. If a clear transplant benefit is not established, agree treatment or surveillance through the standard adenoma pathway.';
  if(['pcca-b1','crlm-b2'].includes(r.anchor))return 'These findings do not open a transplant route under this proposal. Clarify any uncertain finding, then choose another treatment or surveillance plan when transplantation remains unsuitable.';
  return 'Review the findings with the transplant multidisciplinary team. A proposed expanded route requires the relevant clinical, allocation, donor and study approvals before use. Continue appropriate treatment and reassess while that decision is pending.';
 }
 function card(data,slug,r,shared=false){
  const ev=r.evidence;const papers=(ev.studies||[]);const count=r.references.length;
  return `<article class="hr-protocol" id="high-risk-${r.anchor}" aria-labelledby="title-${r.anchor}"><div class="hr-card-top">${badge()}<span class="hr-status">${e(r.status)}</span><span class="hr-code">${e(r.id)}</span></div><h3 id="title-${r.anchor}" tabindex="-1">${e(r.title)}</h3><p class="hr-context">${e(r.context||r.stance)}</p><p class="hr-approval">Proposed protocol / boundary review · institutional approval pending</p>
  <details class="hr-criteria" open><summary>Proposed criteria and clinical approach</summary>${list(r.rules)}${r.anchor==='icca-b1'?distribution():''}</details>
  <details class="hr-information"><summary>Tests and information needed for this review</summary>${text(r.tests)}</details>
  <div class="hr-allocation"><h4>Allocation and donor considerations</h4>${text(r.allocation)}</div>
  <details class="hr-evidence"><summary>High-risk evidence and full-text access <span>${papers.length} study summaries · ${count} sources</span></summary><div class="hr-evidence-body">${['synthesis','counterevidence','certainty','threshold_basis','policy_context'].filter(k=>ev[k]).map(k=>`<div class="hr-evidence-summary"><h4>${({synthesis:'What the evidence supports',counterevidence:'Reasons for caution',certainty:'How certain is the evidence?',threshold_basis:'Where the proposed thresholds come from',policy_context:'Allocation context'})[k]}</h4>${text(ev[k])}</div>`).join('')}<h4 class="hr-subheading">Study results and limitations</h4>${papers.map(s=>study(data,s)).join('')}<details class="hr-all-sources"><summary>All ${count} supporting sources and access links</summary>${r.references.map(k=>source(data.sources[k])).join('')}</details><p class="hr-access-note">PDF buttons open the full paper or an author manuscript. TMC Library access may require UTHealth sign-in. An article available only at abstract level in the V7 review remains identified as such in its limitations.</p></div></details>
  <div class="hr-next"><h4>Next step</h4><p>${e(next(r,slug))}</p><div class="hr-next-links">${r.steps.length?`<button data-step="${e(r.steps[0])}">Return to the standard decision →</button>`:''}${!shared?'<a href="#high-risk-readiness" data-high-risk="readiness">Review requirements before opening a study →</a>':''}<a href="#care-treatment" data-care="treatment">Treatment and continuing care →</a></div></div></article>`;
 }
 function inline(data,slug,step){
  const rs=reviews(data,slug,step);if(!rs.length)return '';
  return `<section class="high-risk-section" aria-labelledby="hr-inline-title"><div class="hr-section-heading"><div><p class="hr-eyebrow">Within this transplant protocol</p><h2 id="hr-inline-title">High-risk protocols at this decision</h2><p>Review the proposed criteria, evidence and next steps below. Each option retains its stated limits and approval status.</p></div><a href="#high-risk" data-view="high-risk" class="hr-overview-link">All high-risk protocols for this tumor →</a></div>${rs.map(r=>card(data,slug,r)).join('')}${downloads(data,slug)}</section>`;
 }
 function overview(data,slug){
  const rs=reviews(data,slug);
  return `<section class="high-risk-view" aria-labelledby="high-risk-title"><div class="hr-section-heading"><div>${badge()}<h2 id="high-risk-title" tabindex="-1">High-risk protocols within the ${e(slug==='nelm'?'NELM':slug==='pcca'?'pCCA':slug==='icca'?'iCCA':slug.toUpperCase())} pathway</h2><p>Each review also appears at the relevant standard decision. Orange identifies a high-risk protocol or boundary review; it does not mean the proposal is approved or that every expansion is open.</p></div></div>${downloads(data,slug)}<nav class="hr-index" aria-label="High-risk protocol decisions">${rs.map(r=>`<a href="#high-risk-${r.anchor}" data-high-risk="${r.anchor}">${e(r.title)} →</a>`).join('')}<a href="#high-risk-readiness" data-high-risk="readiness">Shared approval requirements →</a></nav>${rs.map(r=>card(data,slug,r)).join('')}<section class="hr-readiness" id="high-risk-readiness"><h2 tabindex="-1">Before a proposed study can open</h2><p>Recipient selection, allocation, donor protection and institutional study approval are separate decisions.</p>${data.readiness.map(r=>card(data,slug,r,true)).join('')}</section></section>`;
 }
 function library(data,slug){
  return `<section class="hr-library"><div class="hr-section-heading"><div>${badge()}<h2>Evidence for the high-risk protocols</h2><p>Results, limitations and the reason for each proposed threshold are presented beside the relevant decision.</p></div><a href="#high-risk" data-view="high-risk">Open the high-risk protocols →</a></div>${downloads(data,slug)}<div class="hr-library-grid">${keys(data,slug).map(k=>source(data.sources[k])).join('')}</div></section>`;
 }
 function destination(url){
  if(!url)return null;
  const m=url.match(/\/transplant\/high-risk\/(?:([a-z]+)\/)?(?:#([\w-]+))?$/);
  return m?{slug:m[1]||null,id:m[2]==='readiness'?'readiness':m[2]||''}:null;
 }
 return {reviews,keys,badge,prompt,inline,overview,library,downloads,destination};
})();
if(typeof module!=='undefined')module.exports=HighRisk;
