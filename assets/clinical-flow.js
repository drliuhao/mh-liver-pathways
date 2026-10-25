/* Link purpose and reading order only; no patient matching or new clinical rules. */
(() => {
 'use strict';
 const root=new URL('../',document.currentScript.src);let queued=false;
 const protocol=JSON.parse(document.getElementById('protocol-data')?.textContent||'{}');
 if(location.pathname.includes('/transplant/high-risk/')||location.pathname.includes('/transplant/meeting-records/hcc-b1-1/'))document.body.classList.add('high-risk-document-page');
 const tumors={hcc:'HCC',hilar:'pCCA',pcca:'pCCA',icca:'iCCA',crlm:'CRLM',nelm:'NELM',hehe:'HEHE',hca:'Hepatic adenoma',adenoma:'Hepatic adenoma',chcca:'Combined HCC–CCA',incidental:'Incidental liver mass',pdac:'PDAC',pnet:'pNET',pcyst:'Pancreatic cyst',ampullary:'Ampullary'};
 function navigationOrigin(){
  const raw=new URL(location.href).searchParams.get('via');if(!raw)return;
  const m=raw.match(/^(transplant\/)?([a-z]+)\/(#[a-z0-9-]+)?$/);if(!m)return;
  if(!tumors[m[2]]&&!['lrt','systemic'].includes(m[2]))return;
  const label=m[1]?tumors[m[2]]+' transplant pathway':m[2]==='lrt'?'Liver-directed therapy matrix':m[2]==='systemic'?'Systemic therapy matrix':tumors[m[2]]+' roadmap';
  const banner=document.createElement('aside');banner.className='flow-return';banner.setAttribute('aria-label','Navigation origin');
  const a=document.createElement('a');a.href=new URL(raw,root);a.textContent='← Return to '+label;const note=document.createElement('span');note.textContent='Navigation only. Findings are not carried between pages; check the conditions here.';banner.append(a,note);
  (document.querySelector('main,.wrap,.container')||document.body).prepend(banner);
 }
 document.addEventListener('click',ev=>{
  const a=ev.target.closest('.next-action a[href],.rf-related-link[href],.herolinks a[href]');if(!a)return;
  let u;try{u=new URL(a.href);}catch{return;}
  if(![location.origin,'https://drliuhao.github.io'].includes(u.origin)||!u.pathname.startsWith(root.pathname)||u.pathname===location.pathname||!u.pathname.endsWith('/'))return;
  const rel=location.pathname.slice(root.pathname.length);if(!/^(transplant\/)?[a-z]+\/$/.test(rel))return;
  u.searchParams.set('via',rel+location.hash);a.href=u.href;
 },true);
 navigationOrigin();
 const matrixHero=document.querySelector('.tool-hero');
 if(location.pathname.includes('/systemic/')&&matrixHero){
  const guide=document.createElement('p');guide.className='flow-reading-guide';guide.textContent='1 Choose the tumor and treatment setting · 2 Compare options · 3 Open evidence and precautions';matrixHero.append(guide);
 }

 function enhance(){queued=false;
  document.querySelectorAll('.next-action:not([data-flow-label])').forEach(box=>{
   const a=box.querySelector(':scope > .route-button');if(!a)return;
   let label='Reference';
   if(a.dataset.care){label=protocol.pathway?.slug==='hcc'&&a.dataset.care==='exception'?'High-risk review · care plan':'Care plan';if(label.startsWith('High-risk'))box.classList.add('flow-risk-action');}
   else if(a.dataset.step){const n=protocol.pathway?.steps.findIndex(s=>s.id===a.dataset.step);label=Number.isInteger(n)&&n>=0?'Decision '+(n+1):'Pathway decision';}
   else if(a.classList.contains('high-risk-route'))label='High-risk review';
   else {try{const u=new URL(a.href,location.href);if(u.pathname.includes('/lrt/')||u.pathname.includes('/systemic/'))label='Treatment matrix';else if(u.origin===location.origin&&u.pathname.startsWith(root.pathname))label='Related roadmap or assessment';}catch{}}
   const type=document.createElement('span');type.className='flow-action-type';type.textContent=label;box.prepend(type);box.dataset.flowLabel='true';
  });
 }
 new MutationObserver(records=>{if(!queued&&records.some(r=>r.type==='childList')){queued=true;requestAnimationFrame(enhance);}}).observe(document.body,{childList:true,subtree:true});enhance();
})();
