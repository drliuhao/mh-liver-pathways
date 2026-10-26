/* Allocation reference placed before final follow-up, and available throughout assessment. */
(()=>{'use strict';const api=window.AllocationReference;if(!api)return;let data;try{data=JSON.parse(document.getElementById('protocol-data')?.textContent||'null');}catch{}
 const p=data?.pathway;if(!p||!api.diseases[p.slug])return;let scheduled=false;
 function enhance(){scheduled=false;
  const bar=document.querySelector('.clinical-tool-bar');if(bar&&!bar.querySelector('[data-allocation-link]')){const a=document.createElement('a');a.className='clinical-button';a.dataset.allocationLink='true';a.textContent='Exception & wait';a.href=`/mh-liver-pathways/transplant/waiting/?disease=${p.slug}`;bar.append(a);}
  const decision=document.querySelector('.decision');if(!decision)return;
  const step=decision.querySelector('.permalink')?.getAttribute('href')?.slice(1);
  if(!api.diseases[p.slug].steps.includes(step)||decision.querySelector('.allocation-overview'))return;
  const wrap=document.createElement('div');wrap.innerHTML=api.overview(p.slug);const card=wrap.firstElementChild;
  // Final follow-up always starts with the allocation overview; earlier steps keep their question first.
  if(step===p.steps[p.steps.length-1].id)decision.prepend(card);else decision.querySelector('.contextline')?.after(card);
 }
 new MutationObserver(records=>{if(records.some(r=>r.type==='childList')&&!scheduled){scheduled=true;requestAnimationFrame(enhance);}}).observe(document.body,{childList:true,subtree:true});enhance();
})();
