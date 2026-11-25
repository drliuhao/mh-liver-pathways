/* Source-backed reference content and pure calculations. No clinical state or storage. */
(function(root){
 'use strict';
 const sources={
  optn:'https://www.hrsa.gov/sites/default/files/hrsa/optn/optn_policies.pdf#page=183',
  meld:'https://www.hrsa.gov/optn/data-calculators/allocation-calculators/meld-calculator',
  lirads:'https://www.acr.org/-/media/ACR/Files/RADS/LI-RADS/LI-RADS-2018-Core.pdf',
  applicability:'https://radssupport.acr.org/support/solutions/articles/11000079463-application',
  ecog:'https://ecog-acrin.org/resources/ecog-performance-status/',
  child:'https://www.hepatitisc.uw.edu/page/clinical-calculators/ctp',
  childClass:'https://sps.nhs.uk/articles/calculating-and-using-the-child-pugh-score/'
 };
 const esc=s=>String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
 const link=(url,label)=>`<a href="${esc(url)}" target="_blank" rel="noopener">${esc(label)} ↗</a>`;
 const table=(head,rows)=>`<div class="clinical-table-wrap"><table><thead><tr>${head.map(x=>`<th scope="col">${x}</th>`).join('')}</tr></thead><tbody>${rows.map(r=>`<tr>${r.map((x,i)=>i?`<td>${x}</td>`:`<th scope="row">${x}</th>`).join('')}</tr>`).join('')}</tbody></table></div>`;
 const terms={
  lr5:{label:'LR-5',title:'LR-5 · imaging diagnosis of HCC',match:/\b(?:LR[ -]?5|LI[ -]RADS)\b/i,html:`<p><b>LR-5 means definite HCC on eligible multiphase CT or MRI.</b> LI-RADS applies to adults at risk: cirrhosis, chronic hepatitis B, or current/prior HCC. Exclusions include cirrhosis from vascular disorders and congenital hepatic fibrosis.</p><p>The radiologist assesses lesion size, nonrim arterial enhancement, nonperipheral washout, capsule and threshold growth. A lesion under 10 mm cannot be LR-5. Use the complete ACR algorithm.</p><p>LR-3 is intermediate probability; LR-4 is probable HCC; LR-M suggests malignancy without being specific for HCC. LR-5 alone does not establish MELD-exception eligibility: tumor burden, AFP and spread also matter.</p><p>${link(sources.lirads,'ACR diagnostic algorithm') } · ${link(sources.applicability,'Who LI-RADS applies to')} · ${link('https://www.hrsa.gov/sites/default/files/hrsa/optn/optn_policies.pdf','OPTN policy 9.5.I')}</p>`},
  ecog:{label:'ECOG',title:'ECOG Performance Status Scale',match:/\bECOG\b/i,html:`<p>Describes daily activity, mobility and ability to care for oneself.</p>${table(['Grade','Functional status'],[['0','Fully active without activity restrictions.'],['1','Walking and able to do light work; strenuous activity is limited.'],['2','Independent in self-care, unable to work; out of bed/chair more than half of waking hours.'],['3','Limited self-care; in bed/chair more than half of waking hours.'],['4','Unable to perform self-care; entirely confined to bed/chair.'],['5','Death.']])}<p>Interpret the score with the reason for impairment and the treatment-specific criteria.</p><p>Scale developed by the Eastern Cooperative Oncology Group, now ECOG-ACRIN. Oken et al. <i>Am J Clin Oncol</i>, 1982. ${link('https://pubmed.ncbi.nlm.nih.gov/7165009/','PMID 7165009')} · ${link(sources.ecog,'Official ECOG scale')}</p>`},
  child:{label:'Child-Pugh',title:'Child-Pugh · cirrhosis severity',match:/\b(?:Child(?:[– -](?:Turcotte[– -])?Pugh|\s+(?:class|score|[ABC]))|CTP)\b/i,html:`<p>Add five component scores. <b>A = 5–6; B = 7–9; C = 10–15.</b> A higher total indicates more severe liver dysfunction.</p>${table(['Component','1 point','2 points','3 points'],[['Bilirubin (mg/dL)','&lt;2','2–3','&gt;3'],['Albumin (g/dL)','&gt;3.5','2.8–3.5','&lt;2.8'],['INR','&lt;1.7','1.7–2.3','&gt;2.3'],['Ascites','None','Mild/moderate; responds to diuretics','Severe; refractory to diuretics'],['Encephalopathy','None','Grade I–II','Grade III–IV']])}<p>This is the standard cirrhosis table. Cholestatic disease may require disease-specific interpretation. Ascites and encephalopathy need clinical assessment. The class does not by itself determine transplant suitability or drug dosing.</p><p>${link(sources.child,'UW score calculator and table')} · ${link(sources.childClass,'NHS interpretation')}</p>`},
  meld:{label:'MELD',title:'MELD 3.0 · laboratory score',match:/\bMELD(?:[ -]Na|\s*3\.0)?\b/i,html:`<p><b>Model for End-Stage Liver Disease:</b> estimates medical urgency from bilirubin, INR, creatinine, sodium, albumin and the applicable age/sex formula. Higher scores indicate greater urgency; laboratory MELD ranges from 6 to 40.</p><p><b>Cancer exception points are assessed separately.</b> Laboratory MELD does not establish HCC exception eligibility, transplant suitability, or the final allocation score. Older studies may report original MELD or MELD-Na; these differ from MELD 3.0.</p><p>The calculator follows OPTN policy 9.1.D, with age at registration and dialysis rules. Candidates currently under 12 use PELD.</p><p>${link(sources.optn,'OPTN policy 9.1.D · PDF p.183')} · ${link(sources.meld,'Official OPTN calculator')}</p><button type="button" class="clinical-button" data-clinical-calculator>Open MELD calculator</button>`}
 };
 function calculateMeld(input){
  const invalid=message=>({ok:false,message});
  if(input.ageGroup==='under12')return invalid('For a candidate currently under 12, use the official PELD calculator.');
  if(!['adult','registered-under18'].includes(input.ageGroup))return invalid('Choose the age-at-registration group.');
  if(input.ageGroup==='adult'&&!['female','male'].includes(input.sex))return invalid('Choose the sex used for the OPTN adult MELD calculation.');
  if(!['yes','no'].includes(input.dialysis))return invalid('Choose whether the qualifying dialysis criterion is met.');
  const names={bilirubin:'Bilirubin',inr:'INR',creatinine:'Creatinine',sodium:'Sodium',albumin:'Albumin'},values={};
  for(const [key,name] of Object.entries(names)){
   if(key==='creatinine'&&input.dialysis==='yes'){values[key]=3;continue;}
   const x=input[key];if(x===undefined||x===null||String(x).trim()===''||!Number.isFinite(Number(x))||Number(x)<=0)return invalid('Enter a positive numeric value for '+name.toLowerCase()+', using the displayed units.');
   values[key]=Number(x);
  }
  const bounded={bilirubin:Math.max(1,values.bilirubin),inr:Math.max(1,values.inr),creatinine:Math.min(3,Math.max(1,values.creatinine)),sodium:Math.min(137,Math.max(125,values.sodium)),albumin:Math.min(3.5,Math.max(1.5,values.albumin))};
  const b=Math.log(bounded.bilirubin),c=Math.log(bounded.creatinine),n=137-bounded.sodium,a=3.5-bounded.albumin;
  const raw=4.56*b+0.82*n-0.24*n*b+9.09*Math.log(bounded.inr)+11.14*c+1.85*a-1.83*a*c+(input.ageGroup==='registered-under18'?7.33:6+(input.sex==='female'?1.33:0));
  const adjustments=Object.keys(names).filter(k=>bounded[k]!==values[k]).map(k=>`${names[k]}: ${values[k]} → ${bounded[k]}`);
  if(input.dialysis==='yes')adjustments.unshift('Qualifying dialysis: creatinine set to 3 mg/dL.');
  return {ok:true,score:Math.min(40,Math.max(6,Math.round(raw))),raw,inputs:bounded,adjustments};
 }
 function sourceLinks(ids,sources){return [...new Set(ids||[])].map(id=>{const s=sources[id];return s?link(s.url,s.short):'';}).join(' · ');}
 function listItems(items,sources){return `<ul>${(items||[]).map(x=>`<li>${esc(x.text)} ${sourceLinks(x.refs,sources)}${x.children?listItems(x.children,sources):''}</li>`).join('')}</ul>`;}
 function collectRefs(value,out=new Set()){
  if(Array.isArray(value)){value.forEach(x=>collectRefs(x,out));return out;}
  if(value&&typeof value==='object')for(const [k,v] of Object.entries(value)){if(k==='refs')v.forEach(id=>out.add(id));else collectRefs(v,out);}
  return out;
 }
 function renderPreview(data,id,supplemental=[]){
  const step=data.pathway.steps.find(s=>s.id===id);if(!step)return '';
  const config=data.assistants[data.pathway.slug+'/'+id],sources=data.sources;
  const question=q=>`<section class="clinical-preview-question"><h4>${esc(q.label)}</h4>${q.help?`<p>${esc(q.help)}</p>`:''}${(q.criteria||[]).map(c=>`<section><h5>${esc(c.title)}</h5><ul>${c.items.map(x=>`<li>${esc(x)}</li>`).join('')}</ul><p>${sourceLinks(c.refs,sources)}</p></section>`).join('')}<h5>Possible findings</h5><ul>${q.options.map(o=>`<li>${esc(o.label)}${o.details?.length?`<ul>${o.details.map(x=>`<li>${esc(x)}</li>`).join('')}</ul>`:''}</li>`).join('')}</ul><p>${sourceLinks(q.refs,sources)}</p></section>`;
  const all=collectRefs([step,config]);
  return `<h3 id="clinical-preview-heading" tabindex="-1">${esc(step.title)}</h3><p class="clinical-preview-question-title">${esc(step.question)}</p><p><b>When:</b> ${esc(step.timing)}</p><section class="clinical-preview-checklist"><h4>Full checklist and sources</h4>${step.orders.map(g=>`<h5>${esc(g.label)}</h5>${listItems(g.items,sources)}`).join('')}</section><section><h4>Findings and criteria</h4>${config.questions.map(question).join('')}${supplemental.length?`<h4>Additional findings · when applicable</h4>${supplemental.map(question).join('')}`:''}</section><section><h4>Possible results and next actions</h4>${step.branches.map(b=>`<article class="clinical-preview-result"><h5>${esc(b.title)}</h5>${listItems(b.criteria,sources)}<p><b>Next:</b> ${esc(b.action)}</p><p>${sourceLinks(b.refs,sources)}</p></article>`).join('')}${config.rules.filter(r=>r.branch===null&&r.title).map(r=>`<article class="clinical-preview-result"><h5>${esc(r.title)}</h5><p>${Object.entries(r.when).map(([key,v])=>{const q=config.questions.find(x=>x.id===key);return esc(q.label)+': '+(Array.isArray(v)?v:[v]).map(x=>esc(q.options.find(o=>o.value===x)?.label||x)).join(' / ');}).join('; ')}</p><p>${esc(r.text)}</p><p>${sourceLinks(r.refs,sources)}</p></article>`).join('')}</section>${step.stops.length?`<section class="clinical-preview-cautions"><h4>Reasons to reassess</h4>${listItems(step.stops,sources)}</section>`:''}<section class="clinical-preview-sources"><h4>Source details</h4>${[...all].map(id=>{const s=sources[id];if(!s)return '';const doi=s.url.match(/^https:\/\/(?:dx\.)?doi\.org\/(.+)$/)?.[1];return `<article><h5>${esc(s.short)}</h5><p>${esc(s.title)}</p><p>${esc(s.kind)} · ${esc(s.locator)}</p>${s.note?`<p>${esc(s.note)}</p>`:''}<p>${link(s.url,'Source')}${s.pdf?' · '+link(s.pdf,'Full text / PDF'):''}${doi?' · '+link('https://thslc-houston.primo.exlibrisgroup.com/discovery/search?vid=01TEXASHEALTH_HOUSTON%3ATMC_INST&query=any,contains,'+encodeURIComponent(doi)+'&lang=en','TMC Library'):''}</p></article>`;}).join('')}</section>`;
 }
 const API={sources,terms,calculateMeld,renderPreview,collectRefs,esc,link};
 if(typeof module==='object'&&module.exports)module.exports=API;else root.ClinicalReference=API;
})(typeof window==='undefined'?{}:window);
