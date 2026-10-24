/* Electronic documentation: in-memory only; explicit local file/copy exports. */
'use strict';
const Recording = (() => {
 const present = v => v !== null && v !== undefined && v !== '';
 const human = v => String(v ?? '').replaceAll('_',' ');
 const statuses = ['', 'pending','not_done','not_applicable','unknown','not_documented'];
 const text = v => typeof v === 'string' && v.length <= 10000;
 function validDate(value, precision='day') {
  if (!present(value)) return true;
  if(typeof value !== 'string') return false;
  const pattern={day:/^\d{4}-\d{2}-\d{2}$/,month:/^\d{4}-\d{2}$/,year:/^\d{4}$/}[precision];
  if(!pattern?.test(value)) return false;
  const parts=value.split('-').map(Number), [y,m=1,d=1]=parts;
  return y>=1000 && y<=9999 && m>=1 && m<=12 && d>=1 && d<=new Date(Date.UTC(y,m,0)).getUTCDate();
 }
 function errors(data,schema) {
  const out=[];
  if(!data || typeof data!=='object' || Array.isArray(data)) return ['This is not an assessment file.'];
  for(const key of ['format','format_version','template_version','pathway_id','decision_id']) {
   if(data[key]!==schema[key]) out.push(`File ${key.replaceAll('_',' ')} does not match this form. Open its original decision and template version.`);
  }
  if(out.length)return out;
  if(!data.modules || typeof data.modules!=='object' || Array.isArray(data.modules)) return ['Missing assessment sections.'];
  const moduleKeys=schema.modules.map(g=>g.id);
  if(Object.keys(data.modules).some(k=>!moduleKeys.includes(k)))out.push('The file contains an unrecognized section.');
  for(const g of schema.modules) {
   const entries=data.modules[g.id];
   if(!Array.isArray(entries)||entries.length<1||entries.length>100||(!g.repeat && entries.length!==1)){out.push(`${g.title}: invalid number of entries.`);continue;}
   const seen=new Set();
   for(const row of entries) {
    if(!row || typeof row!=='object'){out.push(`${g.title}: invalid entry.`);continue;}
    if(typeof row.instance_id!=='string'||!new RegExp('^'+g.id+'-[1-9][0-9]*$').test(row.instance_id)||seen.has(row.instance_id))out.push(`${g.title}: invalid or duplicate entry ID.`);
    seen.add(row.instance_id);
    if(!text(row.source)||!validDate(row.observed_date))out.push(`${g.title}: invalid source or observation date.`);
    if(!row.values || typeof row.values!=='object' || Array.isArray(row.values)){out.push(`${g.title}: missing fields.`);continue;}
    const keys=g.fields.map(f=>f.id);
    if(Object.keys(row.values).some(k=>!keys.includes(k)))out.push(`${g.title}: unrecognized field.`);
    for(const f of g.fields) {
     const v=row.values[f.id];
     if(!v || typeof v!=='object'){out.push(`${f.label}: missing field record.`);continue;}
     if(!statuses.includes(v.missing)||!text(v.notes)||!text(v.source)||!validDate(v.observed_date))out.push(`${f.label}: invalid notes, status, source or date.`);
     if(!['day','month','year'].includes(v.precision))out.push(`${f.label}: invalid date precision.`);
     if(present(v.value)){
      if(v.missing)out.push(`${f.label}: clear the value or clear its missing-value status.`);
      if(f.type==='choice'&&!f.choices.includes(v.value))out.push(`${f.label}: choose an available option.`);
      if(f.type==='date'&&!validDate(v.value,v.precision))out.push(`${f.label}: enter a valid date at the selected precision.`);
      if(f.type==='text'&&!text(v.value))out.push(`${f.label}: invalid text.`);
      if(['number','integer'].includes(f.type)){
       if(typeof v.value!=='number'||!Number.isFinite(v.value)||(f.type==='integer'&&!Number.isInteger(v.value)))out.push(`${f.label}: enter ${f.type==='integer'?'a whole number':'a number'}.`);
       else if((f.min!==undefined&&v.value<f.min)||(f.max!==undefined&&v.value>f.max))out.push(`${f.label}: value is outside the field's allowed numeric range.`);
      }
      if(v.value==='other'&&!v.notes?.trim())out.push(`${f.label}: describe “Other” in Notes / missing value.`);
     }
    }
   }
  }
  if(!Array.isArray(data.checklist)||data.checklist.length!==schema.checklist.length)out.push('The information checklist does not match this decision.');
  else data.checklist.forEach((r,i)=>{
   if(!r||Object.keys(r).some(k=>!['status','result','action','owner','due'].includes(k))||!['','documented','pending','not_done','not_applicable','unknown'].includes(r.status)||!['result','action','owner'].every(k=>text(r[k]))||!validDate(r.due))out.push(`Checklist item ${i+1}: invalid data.`);
  });
  const sign=data.modules.decision?.[0]?.values;
  if(sign?.['decision.review_status']?.value==='reviewed'){
   if(!sign['decision.signoff']?.value?.trim()||!sign['decision.signoff_date']?.value||sign['decision.signoff_date']?.precision!=='day')out.push('Reviewed assessments need a reviewer name and an exact sign-off date. Otherwise choose Draft.');
  }
  return [...new Set(out)];
 }
 function valueText(v){return present(v.value)?human(v.value):v.missing?human(v.missing):'Not entered';}
 function note(data,schema) {
  const out=[`# ${schema.title}`,schema.question,`Template ${schema.template_version}`];
  const checklist=data.checklist.map((r,i)=>[r,i]).filter(([r])=>Object.values(r).some(present));
  if(checklist.length){out.push('## Information checklist');for(const [r,i] of checklist)out.push(`${i+1}. ${schema.checklist[i].text}\nStatus: ${human(r.status)||'Not entered'}${r.result?'\nResult: '+r.result:''}${r.action?'\nNext action: '+r.action:''}${r.owner?'\nResponsible clinician: '+r.owner:''}${r.due?'\nDue: '+r.due:''}`);}
  const signoff=[];
  for(const g of schema.modules){
   for(const row of data.modules[g.id]){
    const lines=[];
    for(const f of g.fields){
     const v=row.values[f.id];if(!present(v.value)&&!v.missing&&!v.notes)continue;
     const line=`- ${f.label}: ${valueText(v)}${present(v.value)&&f.unit?' '+f.unit:''}${f.type==='date'&&v.precision!=='day'?' ('+v.precision+' precision)':''}${v.notes?'\n  Notes: '+v.notes:''}${v.source?'\n  Source: '+v.source:''}${v.observed_date?'\n  Observed: '+v.observed_date:''}`;
     if(f.signoff)signoff.push(line);else lines.push(line);
    }
    if(lines.length||row.source||row.observed_date){out.push(`## ${g.title.replace(' and sign-off','')}${g.repeat?' · '+row.instance_id:''}`);if(row.source)out.push('Section source: '+row.source);if(row.observed_date)out.push('Observation date: '+row.observed_date);out.push(...lines);}
   }
  }
  out.push('## Assessment sign-off',...(signoff.length?signoff:['Draft / not signed.']));
  return out.join('\n\n')+'\n';
 }
 function csvCell(v){
  let s=String(v??'');
  if(typeof v!=='number'&&/^[\s]*[=+@-]/.test(s))s="'"+s;
  return '"'+s.replaceAll('"','""')+'"';
 }
 const headers=['record_id','assessment_id','pathway_id','decision_id','module_id','repeat_instance','field_id','label','value','unit','value_status','value_date_precision','observed_date','source_document','notes','reviewer','review_status','signoff_date','template_version'];
 function csv(data,schema){
  const rec=data.modules.record[0].values,sign=data.modules.decision[0].values;
  const prefix=[rec['record.record_id'].value,rec['record.assessment_id'].value,schema.pathway_id,schema.decision_id];
  const suffix=[sign['decision.signoff'].value,sign['decision.review_status'].value,sign['decision.signoff_date'].value,schema.template_version];
  const rows=[headers];
  for(const g of schema.modules)for(const row of data.modules[g.id])for(const f of g.fields){
   const v=row.values[f.id];
   rows.push([...prefix,g.id,row.instance_id,f.id,f.label,v.value,f.unit,present(v.value)?'recorded':v.missing||'not_documented',f.type==='date'?v.precision:'',v.observed_date||row.observed_date,v.source||row.source,v.notes,...suffix]);
  }
  data.checklist.forEach((r,i)=>Object.entries(r).forEach(([k,v])=>rows.push([...prefix,'information_checklist',String(i+1),'checklist.'+(i+1)+'.'+k,schema.checklist[i].text,v,'',present(v)?'recorded':'not_documented','','','', '',...suffix])));
  return rows.map(r=>r.map(csvCell).join(',')).join('\r\n')+'\r\n';
 }
 return {present,human,validDate,errors,note,csv,csvCell,headers};
})();
if(typeof module!=='undefined'&&module.exports)module.exports=Recording;
if(typeof document!=='undefined')(() => {
 const schema=JSON.parse(document.getElementById('form-schema').textContent);
 const form=document.getElementById('assessment');
 const msg=document.getElementById('message'),errorsEl=document.getElementById('errors');
 const counters=Object.fromEntries(schema.modules.map(g=>[g.id,1]));
 let dirty=false;
 const say=s=>{msg.textContent=s;};
 const fieldElement=(container,f)=>f.signoff?document.querySelector(`#signoff [data-field="${f.id}"]`):container.querySelector(`[data-field="${f.id}"]`);
 const read=(field,selector)=>field.querySelector(selector)?.value||'';
 function dateType(field,precision,value=''){
  const input=field.querySelector('[data-value]');
  input.type={day:'date',month:'month',year:'number'}[precision];
  input.removeAttribute('min');input.removeAttribute('max');input.removeAttribute('step');
  if(precision==='year'){input.min='1000';input.max='9999';input.step='1';}
  input.value=value;
 }
 function collect(){
  const data={format:schema.format,format_version:schema.format_version,template_version:schema.template_version,pathway_id:schema.pathway_id,decision_id:schema.decision_id,saved_at:new Date().toISOString(),modules:{},checklist:[]};
  for(const g of schema.modules){
   data.modules[g.id]=[...document.querySelector(`[data-module="${g.id}"] .instances`).children].map(el=>{
    const values={};
    for(const f of g.fields){
     const field=fieldElement(el,f);const raw=read(field,'[data-value]');
     values[f.id]={value:raw===''?null:['number','integer'].includes(f.type)?Number(raw):raw,missing:read(field,'[data-missing]'),notes:read(field,'[data-notes]'),source:read(field,'[data-source]'),observed_date:read(field,'[data-observed]'),precision:read(field,'[data-precision]')||'day'};
    }
    return {instance_id:el.dataset.instance,source:read(el,'[data-module-source]'),observed_date:read(el,'[data-module-date]'),values};
   });
  }
  data.checklist=[...form.querySelectorAll('[data-checklist]')].map(el=>Object.fromEntries(['status','result','action','owner','due'].map(k=>[k,read(el,`[data-check="${k}"]`)])));
  return data;
 }
 function validate(data){
  const problems=Recording.errors(data,schema);
  form.querySelectorAll('[data-value]').forEach(el=>{if(el.validity.badInput||el.validity.stepMismatch)problems.push(el.closest('.field').querySelector('label').textContent+': enter a valid number.');});
  errorsEl.replaceChildren();errorsEl.hidden=!problems.length;
  if(problems.length){const p=document.createElement('p');p.textContent='Please check these entries before exporting:';const ul=document.createElement('ul');for(const text of problems){const li=document.createElement('li');li.textContent=text;ul.append(li);}errorsEl.append(p,ul);errorsEl.scrollIntoView({block:'center'});}
  return !problems.length;
 }
 function updateCounts(){
  let total=0;
  form.querySelectorAll('[data-module]').forEach(section=>{
   const n=[...section.querySelectorAll('[data-value]')].filter(el=>el.value!=='').length;total+=n;
   section.querySelector('.section-count').textContent=n?n+' entered':'';
   const rows=section.querySelectorAll('.module-instance');rows.forEach((row,i)=>{const num=row.querySelector('[data-instance-number]');if(num)num.textContent=String(i+1);const remove=row.querySelector('[data-remove]');if(remove)remove.disabled=rows.length===1;});
  });
  document.getElementById('completion').textContent=total+' clinical fields entered';
 }
 function changed(target){
  dirty=true;document.getElementById('save-status').textContent='Unsaved changes · download JSON to keep them';
  if(!target?.closest('#signoff')){
   const review=form.querySelector('[data-field="decision.review_status"] [data-value]');
   if(review.value==='reviewed'){review.value='draft';say('Clinical fields changed. Review status returned to Draft; review again before signing.');}
  }
  updateCounts();
 }
 function instance(g,id){
  const node=document.getElementById('repeat-'+g.id).content.firstElementChild.cloneNode(true);
  node.dataset.instance=id;
  node.querySelectorAll('[id]').forEach(el=>{const before=el.id;const after=before.replace(g.id+'-1-',id+'-');el.id=after;node.querySelectorAll('[for],[aria-describedby]').forEach(label=>{for(const a of ['for','aria-describedby'])if(label.getAttribute(a)===before)label.setAttribute(a,after);});});
  return node;
 }
 function apply(data){
  form.reset();
  for(const g of schema.modules){
   const parent=form.querySelector(`[data-module="${g.id}"] .instances`);parent.replaceChildren();
   for(const row of data.modules[g.id]){
    const el=instance(g,row.instance_id);parent.append(el);counters[g.id]=Math.max(counters[g.id],Number(row.instance_id.split('-').pop()));
    el.querySelector('[data-module-source]').value=row.source;el.querySelector('[data-module-date]').value=row.observed_date;
    for(const f of g.fields){
     const field=fieldElement(el,f),v=row.values[f.id];
     if(f.type==='date'){field.querySelector('[data-precision]').value=v.precision;dateType(field,v.precision,v.value??'');}else field.querySelector('[data-value]').value=v.value??'';
     for(const [sel,key] of [['data-missing','missing'],['data-notes','notes'],['data-source','source'],['data-observed','observed_date']]){const input=field.querySelector('['+sel+']');if(input)input.value=v[key];}
     if(v.notes||v.missing)field.querySelector('details')?.setAttribute('open','');
    }
   }
  }
  data.checklist.forEach((row,i)=>Object.entries(row).forEach(([k,v])=>{form.querySelector(`[data-checklist="${i}"] [data-check="${k}"]`).value=v;}));
  errorsEl.hidden=true;dirty=false;updateCounts();
 }
 function download(body,extension,type){
  const url=URL.createObjectURL(new Blob([body],{type}));const a=document.createElement('a');a.href=url;a.download=schema.pathway_id+'-'+schema.decision_id+'-'+new Date().toISOString().replace(/[:.]/g,'-')+'.'+extension;document.body.append(a);a.click();a.remove();setTimeout(()=>URL.revokeObjectURL(url),30000);
 }
 form.addEventListener('submit',ev=>ev.preventDefault());
 form.addEventListener('input',ev=>{changed(ev.target);});
 form.addEventListener('change',ev=>{
  if(ev.target.matches('[data-precision]')){
   const field=ev.target.closest('.field'),value=read(field,'[data-value]'),precision=ev.target.value;
   const desired={day:10,month:7,year:4}[precision];dateType(field,precision,value.length>=desired?value.slice(0,desired):'');
  }
  if(ev.target.matches('[data-value]')&&ev.target.value==='other'){const details=ev.target.closest('.field').querySelector('details');if(details){details.open=true;details.querySelector('[data-notes]').focus();}}
  changed(ev.target);
 });
 form.addEventListener('click',ev=>{
  const add=ev.target.closest('[data-add]'),remove=ev.target.closest('[data-remove]');
  if(add){const g=schema.modules.find(g=>g.id===add.dataset.add);const list=form.querySelector(`[data-module="${g.id}"] .instances`);if(list.children.length>=100){say('This section supports up to 100 entries in one assessment.');return;}const row=instance(g,g.id+'-'+(++counters[g.id]));list.append(row);changed(add);row.querySelector('[data-value]').focus();}
  if(remove){const row=remove.closest('.module-instance');if(row.parentElement.children.length===1)return;const filled=[...row.querySelectorAll('input,textarea,select')].some(el=>el.value&&!el.matches('[data-precision]'));if(!filled||window.confirm('Remove this entry from the current assessment? Saved files are unchanged.')){row.remove();changed(remove);}}
 });
 document.querySelector('[data-save]').addEventListener('click',()=>{const data=collect();if(!validate(data))return;download(JSON.stringify(data,null,2),'json','application/json');dirty=false;document.getElementById('save-status').textContent='JSON download prepared · keep the file in an approved location';say('Use Reopen saved JSON to continue this assessment later.');});
 document.querySelector('[data-load]').addEventListener('click',()=>document.querySelector('[data-import]').click());
 document.querySelector('[data-import]').addEventListener('change',async ev=>{
  const file=ev.target.files[0];if(!file)return;
  try{
   if(file.size>5*1024*1024)throw new Error('The JSON file must be smaller than 5 MB.');
   const data=JSON.parse(await file.text());const problems=Recording.errors(data,schema);if(problems.length)throw new Error(problems.slice(0,4).join(' '));
   if(dirty&&!window.confirm('Replace the unsaved assessment with this saved file?'))return;
   apply(data);document.getElementById('save-status').textContent='Saved assessment reopened · local to this tab';say('All entries, repeated records and the assessment sign-off have been restored.');
  }catch(error){say('Could not reopen file. '+error.message+' The current assessment was kept.');}
  finally{ev.target.value='';}
 });
 document.querySelector('[data-csv]').addEventListener('click',()=>{const data=collect();if(validate(data)){download('\uFEFF'+Recording.csv(data,schema),'csv','text/csv;charset=utf-8');say('Structured CSV prepared, including repeated entries, units, missing-value status and the single assessment sign-off.');}});
 document.querySelector('[data-md]').addEventListener('click',()=>{const data=collect();if(validate(data))download(Recording.note(data,schema),'md','text/markdown;charset=utf-8');});
 document.querySelector('[data-copy]').addEventListener('click',async()=>{const data=collect();if(!validate(data))return;const note=Recording.note(data,schema);try{await navigator.clipboard.writeText(note);say('Completed assessment copied. Paste into the approved clinical record.');}catch{const pre=document.getElementById('copy-fallback');pre.textContent=note;pre.hidden=false;const range=document.createRange();range.selectNodeContents(pre);const selection=window.getSelection();selection.removeAllRanges();selection.addRange(range);pre.focus();say('Select and copy the completed note below, or use Download note.');}});
 function printNote(){const el=document.getElementById('print-note');el.replaceChildren();const h=document.createElement('h1');h.textContent=schema.title;const pre=document.createElement('pre');pre.textContent=Recording.note(collect(),schema);el.append(h,pre);}
 window.addEventListener('beforeprint',printNote);
 document.querySelector('[data-print]').addEventListener('click',()=>{const data=collect();if(validate(data)){printNote();window.print();}});
 document.querySelector('[data-expand]').addEventListener('click',()=>form.querySelectorAll('.form-section').forEach(d=>d.open=true));
 document.querySelector('[data-collapse]').addEventListener('click',()=>form.querySelectorAll('.form-section').forEach(d=>d.open=false));
 const blank=collect();
 document.querySelector('[data-new]').addEventListener('click',()=>{if(dirty&&!window.confirm('Clear this unsaved assessment? Download JSON first to retain it.'))return;apply(blank);document.getElementById('save-status').textContent='New assessment · not saved';say('A new blank assessment is ready.');});
 window.addEventListener('beforeunload',ev=>{if(dirty){ev.preventDefault();ev.returnValue='';}});
 updateCounts();
})();
