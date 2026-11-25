/* Read-only decision previews and clinical references. Calculators never write pathway answers. */
(() => {
 'use strict';
 const ref=window.ClinicalReference;if(!ref)return;
 let data;try{data=JSON.parse(document.getElementById('protocol-data')?.textContent||'null');}catch{}
 const pathway=data?.pathway,roadmap=document.getElementById('answer');if(!pathway&&!roadmap&&!document.querySelector('[data-allocation-page]'))return;
 const {esc,link}=ref,root=new URL('../',document.currentScript.src),supplementCache=new Map();
 let queued=false,dialog=null,dialogOrigin=null;
 const node=(tag,cls,text)=>{const n=document.createElement(tag);if(cls)n.className=cls;if(text!==undefined)n.textContent=text;return n;};
 function button(text,attr){const b=node('button','clinical-button',text);b.type='button';b.setAttribute(attr,'');return b;}
 function termLink(key){
  const term=ref.terms[key],d=node('details','clinical-term');d.dataset.contextTitle=term.title;
  d.innerHTML=`<summary>${esc(term.label)}</summary>${term.html}`;
  return d;
 }
 function enhanceTerms(scope){
  scope.querySelectorAll('details.clinical-term:not([data-context-ready])').forEach(d=>{
   const item=window.ContextualInfo?.reference?.(d);
   if(item){item.wrapper.classList.add('clinical-term-unit');item.button.setAttribute('aria-label','Explain '+d.querySelector('summary').textContent);}
  });
 }
 function termRow(host,text){
  if(host.querySelector(':scope > .clinical-term-links'))return;
  const keys=Object.keys(ref.terms).filter(k=>ref.terms[k].match.test(text));if(!keys.length)return;
  const row=node('div','clinical-term-links');row.setAttribute('aria-label','Terms explained');keys.forEach(k=>row.append(termLink(k)));host.append(row);enhanceTerms(row);
 }
 function openDialog(title,wide,origin){
  dialogOrigin=window.ContextualInfo?.sourceOrigin(origin)||origin;
  if(!dialog){
   dialog=node('dialog','clinical-dialog');dialog.setAttribute('aria-labelledby','clinical-dialog-title');document.body.append(dialog);
   dialog.addEventListener('click',ev=>{if(ev.target===dialog){const r=dialog.getBoundingClientRect();if(ev.clientX<r.left||ev.clientX>r.right||ev.clientY<r.top||ev.clientY>r.bottom)dialog.close();}});
   dialog.addEventListener('close',()=>{dialog.replaceChildren();document.body.classList.remove('clinical-dialog-open');if(dialogOrigin?.isConnected)dialogOrigin.focus({preventScroll:true});});
  }
  dialog.classList.toggle('clinical-dialog-wide',wide);
  dialog.innerHTML=`<header class="clinical-dialog-head"><h2 id="clinical-dialog-title">${esc(title)}</h2><button type="button" class="clinical-dialog-close" aria-label="Close ${esc(title)}">Close ×</button></header><div class="clinical-dialog-body"></div>`;
  dialog.querySelector('.clinical-dialog-close').addEventListener('click',()=>dialog.close());
  document.body.classList.add('clinical-dialog-open');if(!dialog.open)dialog.showModal();return dialog.querySelector('.clinical-dialog-body');
 }
 function supplemental(step){
  if(supplementCache.has(step.id))return supplementCache.get(step.id);
  const engine=window.RiskRouting;if(!engine)return [];
  const config=data.assistants[pathway.slug+'/'+step.id];let combinations=[{}];
  for(const q of config.questions)combinations=combinations.flatMap(a=>q.options.map(o=>({...a,[q.id]:o.value})));
  const found=new Map();
  for(const answers of combinations)for(const prior of [{},{knownBurden:true,beyond:true,advanced:true,ici:true,iciStatus:'prior',extra:{}}])for(const q of engine.questions(pathway.slug,step.id,answers,prior))found.set(q.id,{...q,options:q.options.map(([value,label])=>({value,label})),refs:[],criteria:[]});
  const result=[...found.values()];supplementCache.set(step.id,result);return result;
 }
 function preview(id,origin){
  const selected=pathway.steps.find(s=>s.id===id)||pathway.steps[0];
  const body=openDialog(pathway.code+' · preview decisions',true,origin);
  body.innerHTML='<p class="clinical-preview-note"><b>Read ahead at any time.</b> Previewing leaves your findings and current step unchanged.</p><div class="clinical-preview-layout"><nav class="clinical-preview-nav" aria-label="Preview any decision"></nav><div class="clinical-preview-content"></div></div>';
  const nav=body.querySelector('nav'),content=body.querySelector('.clinical-preview-content');
  const show=(step,focus=true)=>{
   nav.querySelectorAll('button').forEach(b=>{const active=b.dataset.previewStep===step.id;b.classList.toggle('is-selected',active);if(active)b.setAttribute('aria-current','true');else b.removeAttribute('aria-current');});
   content.innerHTML=ref.renderPreview(data,step.id,supplemental(step));
   if(window.AllocationReference?.diseases[pathway.slug]?.steps.includes(step.id))content.insertAdjacentHTML('afterbegin',window.AllocationReference.overview(pathway.slug));
   const reviews=data.high_risk.pathways[pathway.slug]?.reviews.filter(r=>(window.RiskRouting.coverage[r.anchor]||[]).includes(step.id))||[];
   if(reviews.length){const risk=node('section','clinical-preview-risk');risk.innerHTML='<h4>High-risk reviews · only when relevant</h4><p>Each review retains its own eligibility limits and approval status. Reading it does not select a protocol.</p>'+reviews.map(r=>`<p>${link(new URL('transplant/'+pathway.slug+'/#high-risk-'+r.anchor,root),r.title||r.anchor)}</p>`).join('');content.querySelector('.clinical-preview-sources').before(risk);}
   termRow(content.querySelector('.clinical-preview-checklist'),content.textContent);
   content.scrollTop=0;
   if(focus)content.querySelector('h3').focus({preventScroll:true});
  };
  pathway.steps.forEach((s,i)=>{const b=button('', 'data-preview-step');b.dataset.previewStep=s.id;b.innerHTML=`<span>${i+1}</span><span>${esc(s.title)}</span>`;b.addEventListener('click',()=>show(s));nav.append(b);});
  show(selected,false);nav.querySelector('[aria-current]')?.focus({preventScroll:true});
 }
 function calculator(origin){
  const body=openDialog('MELD 3.0 calculator',false,origin);
  const field=(id,label,unit)=>`<label for="clinical-meld-${id}">${label}<span class="clinical-unit">${unit}</span><input id="clinical-meld-${id}" name="${id}" type="number" step="any" min="0.000001" inputmode="decimal" required autocomplete="off"></label>`;
  body.innerHTML=`<p class="clinical-score-note"><b>Laboratory MELD only.</b> Cancer exception points and transplant suitability are assessed separately.</p>
   <form class="clinical-meld-form" novalidate autocomplete="off"><div class="clinical-meld-grid">
    <label for="clinical-meld-ageGroup">Age group<select id="clinical-meld-ageGroup" name="ageGroup" required><option value="">Choose…</option><option value="adult">Age 18 or older at registration</option><option value="registered-under18">Registered before 18; currently 12 or older</option><option value="under12">Currently under 12 · use PELD</option></select></label>
    <label for="clinical-meld-sex">Sex for OPTN adult MELD<select id="clinical-meld-sex" name="sex" required><option value="">Choose…</option><option value="female">Female</option><option value="male">Male</option></select><span class="clinical-field-help">Use the value documented for the OPTN calculation.</span></label>
    ${field('bilirubin','Total bilirubin','mg/dL')}${field('inr','INR','unitless')}${field('creatinine','Serum creatinine','mg/dL')}${field('sodium','Serum sodium','mmol/L (equivalent to mEq/L)')}${field('albumin','Serum albumin','g/dL')}
    <label for="clinical-meld-dialysis">Qualifying dialysis<select id="clinical-meld-dialysis" name="dialysis" required><option value="">Choose…</option><option value="no">No</option><option value="yes">Yes</option></select><span class="clinical-field-help">≥2 dialysis treatments or ≥24 hours of CVVHD in the 7 days before the creatinine test.</span></label>
   </div><div class="clinical-form-actions"><button type="submit" class="clinical-button clinical-primary">Calculate MELD</button><button type="reset" class="clinical-button">Clear</button></div><div class="clinical-meld-result" role="status" aria-live="polite"><p>Enter the required values to calculate.</p></div></form>
   <p class="clinical-private">Calculated in this tab; values are not saved, sent, or applied to pathway choices. Closing the calculator clears its inputs.</p>
   <details class="clinical-formula"><summary>Formula, limits and sources</summary><p>ln = natural logarithm. Adult formula:</p><p class="clinical-equation">6 + 1.33 (if female) + 4.56 ln(bilirubin) + 0.82 (137 − sodium) − 0.24 (137 − sodium) ln(bilirubin) + 9.09 ln(INR) + 11.14 ln(creatinine) + 1.85 (3.5 − albumin) − 1.83 (3.5 − albumin) ln(creatinine).</p><p>For registration before age 18 and current age ≥12, use 7.33 in place of 6 + the sex term.</p><ul><li>Bilirubin and INR: minimum 1. Creatinine: 1–3 mg/dL; qualifying dialysis sets it to 3.</li><li>Sodium: 125–137 mmol/L. Albumin: 1.5–3.5 g/dL.</li><li>Round to the nearest whole number and limit to 6–40.</li></ul><p>OPTN policy 9.1.D, effective October 1, 2026; checked October 26, 2026. Confirm the official score when submitting allocation data.</p><p>${link(ref.sources.optn,'Policy · PDF p.183')} · ${link(ref.sources.meld,'Official OPTN calculator')} · ${link('https://www.hrsa.gov/optn/data-calculators/allocation-calculators/peld-calculator','PELD calculator')}</p></details>`;
  const form=body.querySelector('form'),result=form.querySelector('.clinical-meld-result'),input=name=>form.elements.namedItem(name);
  const clearResult=()=>{result.classList.remove('has-score','has-error');result.innerHTML='<p>Enter the required values to calculate.</p>';};
  const sync=()=>{const adult=input('ageGroup').value==='adult';input('sex').disabled=!adult;input('sex').required=adult;const dialysis=input('dialysis').value==='yes';input('creatinine').disabled=dialysis;input('creatinine').required=!dialysis;};
  form.addEventListener('input',clearResult);form.addEventListener('change',()=>{sync();clearResult();});
  form.addEventListener('reset',()=>requestAnimationFrame(()=>{sync();clearResult();input('ageGroup').focus();}));
  form.addEventListener('submit',ev=>{ev.preventDefault();const values=Object.fromEntries(['ageGroup','sex','dialysis','bilirubin','inr','creatinine','sodium','albumin'].map(key=>[key,input(key).value]));const score=ref.calculateMeld(values);clearResult();
   if(!score.ok){result.classList.add('has-error');result.innerHTML=`<p>${esc(score.message)}</p>${values.ageGroup==='under12'?link('https://www.hrsa.gov/optn/data-calculators/allocation-calculators/peld-calculator','Open official PELD calculator'):''}`;}
   else{result.classList.add('has-score');result.innerHTML=`<span>Laboratory MELD 3.0</span><strong>${score.score}</strong><p>Rounded score · range 6–40</p>${score.adjustments.length?`<p><b>Policy adjustments applied</b></p><ul>${score.adjustments.map(x=>`<li>${esc(x)}</li>`).join('')}</ul>`:''}`;}
  });sync();input('ageGroup').focus({preventScroll:true});
 }
 function enhance(){
  queued=false;
  const host=pathway?document.querySelector('.pathhero'):document.querySelector('.rf-selector');
  if(host&&!document.querySelector('.clinical-tool-bar')){
   const bar=node('div','clinical-tool-bar');bar.setAttribute('aria-label','Decision previews and clinical tools');
   if(pathway)bar.append(button('Preview decisions','data-clinical-preview'));
   bar.append(button('MELD calculator','data-clinical-calculator'));Object.keys(ref.terms).forEach(k=>bar.append(termLink(k)));
   if(pathway)host.after(bar);else host.before(bar);enhanceTerms(bar);
  }
  document.querySelectorAll('.ct-strip:not([data-clinical-shortcuts])').forEach(strip=>{
   strip.dataset.clinicalShortcuts='true';const tools=node('div','clinical-strip-tools');
   if(pathway)tools.append(button('Preview','data-clinical-preview'));
   const calc=button('MELD','data-clinical-calculator');calc.setAttribute('aria-label','Open MELD calculator');tools.append(calc);strip.append(tools);
  });
  document.querySelectorAll('.full-tests:not([data-clinical-opened])').forEach(d=>{d.dataset.clinicalOpened='true';d.open=true;});
  document.querySelectorAll('.layer-current .layer-choice,.full-tests .ordergroup,.assistant-criteria,.rf-criteria').forEach(n=>{
   if(n.closest('.clinical-dialog,.ci-panel,.clinical-term-links'))return;
   const text=n.textContent;termRow(n,text);
  });
  enhanceTerms(document);
 }
 // Preview controls intentionally do not dispatch data-step or mutate the decision trail.
 document.addEventListener('click',ev=>{
  const previewControl=ev.target.closest('[data-clinical-preview],[data-pathway-overview],.journey-phases [data-step]');
  if(pathway&&previewControl){ev.preventDefault();ev.stopImmediatePropagation();const map=previewControl.closest('.ct-menu');if(map)map.open=false;preview(previewControl.dataset.step||location.hash.slice(1),previewControl);return;}
  const calc=ev.target.closest('[data-clinical-calculator]');if(calc){ev.preventDefault();ev.stopImmediatePropagation();calculator(calc);}
 },true);
 new MutationObserver(records=>{if(records.some(r=>r.type==='childList')&&!queued){queued=true;requestAnimationFrame(enhance);}}).observe(document.body,{childList:true,subtree:true});
 enhance();
})();
