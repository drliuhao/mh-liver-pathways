/* Allocation overview inside Transplant waitlisted; linked from other decisions. */
(()=>{'use strict';const api=window.AllocationReference;if(!api)return;let data;try{data=JSON.parse(document.getElementById('protocol-data')?.textContent||'null');}catch{}
 const p=data?.pathway;if(!p||!api.diseases[p.slug])return;let scheduled=false;
 function enhance(){scheduled=false;
  const decision=document.querySelector('.decision');if(!decision)return;
  const step=decision.querySelector('.permalink')?.getAttribute('href')?.slice(1);
  const waitStep={hcc:'listing',pcca:'listing',icca:'review',crlm:'review',nelm:'review',hehe:'review',hca:'review'}[p.slug];
  if(![waitStep,...(p.slug==='hcc'?['waitlist']:[])].includes(step)||decision.querySelector('.allocation-overview'))return;
  const wrap=document.createElement('div');wrap.innerHTML=api.overview(p.slug);const card=wrap.firstElementChild;
  decision.querySelector('.contextline')?.after(card);
 }
 new MutationObserver(records=>{if(records.some(r=>r.type==='childList')&&!scheduled){scheduled=true;requestAnimationFrame(enhance);}}).observe(document.body,{childList:true,subtree:true});enhance();
})();
