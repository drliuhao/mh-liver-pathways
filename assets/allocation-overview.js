/* Allocation overview inside Transplant waitlisted; linked from other decisions. */
(()=>{'use strict';const api=window.AllocationReference;if(!api)return;let data;try{data=JSON.parse(document.getElementById('protocol-data')?.textContent||'null');}catch{}
 const p=data?.pathway;if(!p||!api.diseases[p.slug])return;let scheduled=false;
 const root=new URL('../',document.currentScript.src);
 function enhance(){scheduled=false;
  const decision=document.querySelector('.decision');if(!decision)return;
  const step=decision.querySelector('.permalink')?.getAttribute('href')?.slice(1);
  const waitStep={hcc:'listing',pcca:'listing',icca:'review',crlm:'review',nelm:'review',hehe:'review',hca:'review'}[p.slug];
  const isWaiting=[waitStep,...(p.slug==='hcc'?['waitlist']:[])].includes(step);
  const resources=decision.querySelector('.dw-tool-documents');
  if(isWaiting)resources?.querySelector('[data-waiting-resource]')?.remove();
  else if(resources&&!resources.querySelector('[data-waiting-resource]')){
   const a=document.createElement('a');a.className='clinical-button';a.dataset.waitingResource='';
   a.textContent='Transplant waitlisted · policy & outcomes';a.href=new URL('transplant/waiting/?disease='+p.slug,root);resources.append(a);
  }
  if(![waitStep,...(p.slug==='hcc'?['waitlist']:[])].includes(step)||decision.querySelector('.allocation-overview'))return;
  const wrap=document.createElement('div');wrap.innerHTML=api.overview(p.slug);const card=wrap.firstElementChild;
  decision.querySelector('.contextline')?.after(card);
 }
 new MutationObserver(records=>{if(records.some(r=>r.type==='childList')&&!scheduled){scheduled=true;requestAnimationFrame(enhance);}}).observe(document.body,{childList:true,subtree:true});enhance();
})();
