/* Presentation only: filter, disclose and link to existing evidence. */
(() => {
 'use strict';
 const $=s=>document.querySelector(s), $$=s=>[...document.querySelectorAll(s)];
 const params=new URLSearchParams(location.search);
 const tumors=['all','hcc','pcca','icca','crlm','nelm','pdac','pnet','ampullary','chcca'];
 const views=['options','comparison','precautions','library'];
 let tumor=tumors.includes(params.get('tumor'))?params.get('tumor'):'hcc';
 let view=views.includes(params.get('view'))?params.get('view'):'options';
 const buttons=$$('[data-filter]'), tabs=$$('[data-view]'), cards=$$('.regimen-card');
 const papers=$$('.library-entry'), search=$('#therapy-search'), setting=$('#setting');
 const names=Object.fromEntries(buttons.map(b=>[b.dataset.filter,b.textContent]));
 const validSettings=[...setting.options].map(o=>o.value);
 if(validSettings.includes(params.get('setting')))setting.value=params.get('setting');
 function syncUrl(){
  const u=new URL(location.href);u.searchParams.set('tumor',tumor);
  if(view==='options')u.searchParams.delete('view');else u.searchParams.set('view',view);
  if(setting.value==='all')u.searchParams.delete('setting');else u.searchParams.set('setting',setting.value);
  history.replaceState(null,'',u);
 }
 function updatePapers(){
  const q=$('#paper-search').value.toLowerCase().trim(),pdf=$('#pdf-filter').value;let count=0;
  papers.forEach(p=>{
   p.hidden=!(tumor==='all'||p.dataset.tumors.split(' ').includes(tumor))
    ||!(pdf==='all'||p.dataset.pdf===pdf)||!p.textContent.toLowerCase().includes(q);
   if(!p.hidden)count++;
  });
  $('#paper-count').textContent=count+(count===1?' paper':' papers');
  $('#no-papers').hidden=count!==0;
 }
 function update(){
  buttons.forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.filter===tumor)));
  const q=search.value.toLowerCase().trim(),s=setting.value;let count=0;
  cards.forEach(c=>{
   c.hidden=!(tumor==='all'||c.dataset.tumors.split(' ').includes(tumor))
    ||!(s==='all'||c.dataset.setting===s)||!c.textContent.toLowerCase().includes(q);
   if(!c.hidden)count++;
  });
  $$('[data-setting-group]').forEach(g=>g.hidden=![...g.querySelectorAll('.regimen-card')].some(c=>!c.hidden));
  $('#result-count').textContent=count+(count===1?' option':' options');
  $('#no-results').hidden=count!==0;$('#expand-options').disabled=count===0;
  $$('.therapy-matrix [data-tumor]').forEach(c=>c.hidden=tumor!=='all'&&c.dataset.tumor!==tumor);
  $$('.therapy-matrix tbody tr').forEach(row=>{
   row.hidden=s!=='all'&&row.dataset.setting!==s;
   row.querySelectorAll('td>.matrix-option').forEach(p=>{
    const a=p.querySelector('a');if(a){const c=document.getElementById(a.hash.slice(1));p.hidden=Boolean(c?.hidden);}
   });
  });
  $('.therapy-matrix').style.minWidth=tumor==='all'?'950px':'0';
  tabs.forEach(t=>{
   const selected=t.dataset.view===view;t.setAttribute('aria-selected',String(selected));
   t.tabIndex=selected?0:-1;$('#view-'+t.dataset.view).hidden=!selected;
  });
  $('#treatment-controls').hidden=!['options','comparison'].includes(view);
  $('.tumor-tabs').hidden=view==='precautions';
  $('#selection-context').textContent=view==='precautions'?'Shared safety considerations across tumor types.'
   :names[tumor]+' · '+(view==='library'?'Evidence library':setting.selectedOptions[0].textContent);
  updatePapers();syncUrl();
 }
 function clearAnchor(){const u=new URL(location.href);u.hash='';history.replaceState(null,'',u);}
 function showView(next){view=next;clearAnchor();update();}
 buttons.forEach(b=>b.addEventListener('click',()=>{tumor=b.dataset.filter;clearAnchor();update();}));
 tabs.forEach((tab,i)=>{
  tab.addEventListener('click',()=>showView(tab.dataset.view));
  tab.addEventListener('keydown',e=>{
   let n;if(e.key==='ArrowRight')n=(i+1)%tabs.length;
   else if(e.key==='ArrowLeft')n=(i+tabs.length-1)%tabs.length;
   else if(e.key==='Home')n=0;else if(e.key==='End')n=tabs.length-1;else return;
   e.preventDefault();showView(tabs[n].dataset.view);tabs[n].focus();
  });
 });
 search.addEventListener('input',update);setting.addEventListener('change',()=>{clearAnchor();update();});
 $('#paper-search').addEventListener('input',updatePapers);$('#pdf-filter').addEventListener('change',updatePapers);
 $('#expand-options').addEventListener('click',()=>cards.filter(c=>!c.hidden).forEach(c=>c.querySelector('.regimen-disclosure').open=true));
 $('#collapse-options').addEventListener('click',()=>cards.forEach(c=>c.querySelectorAll('details').forEach(d=>d.open=false)));
 $('#compare-all').addEventListener('click',()=>{tumor='all';search.value='';setting.value='all';clearAnchor();update();});
 // Old section anchors, matrix cells and external regimen links all keep working.
 function openAnchor(hash, scroll=true){
  let id;try{id=decodeURIComponent(hash.replace(/^#/,''));}catch{return false;}
  const target=document.getElementById(id);if(!target)return false;
  const panel=target.closest('.matrix-panel');if(!panel)return false;
  view=panel.id.replace('view-','');const card=target.closest('.regimen-card');
  if(card){
   if(tumor!=='all'&&!card.dataset.tumors.split(' ').includes(tumor))tumor=card.dataset.tumors.split(' ')[0];
   if(setting.value!=='all'&&setting.value!==card.dataset.setting)setting.value='all';
   search.value='';card.querySelector('.regimen-disclosure').open=true;
  }
  for(let p=target;p&&p!==panel;p=p.parentElement)if(p.tagName==='DETAILS')p.open=true;
  update();
  if(scroll)requestAnimationFrame(()=>{
   const focus=target.matches('details')?target.querySelector('summary'):card?.querySelector('summary');
   if(focus)focus.focus({preventScroll:true});target.scrollIntoView({block:'start',behavior:'instant'});
  });
  return true;
 }
 document.addEventListener('click',e=>{
  const a=e.target.closest('a[href^="#"]');if(!a)return;
  const previous=location.href;
  if(openAnchor(a.hash)){
   e.preventDefault();const u=new URL(location.href);u.hash=a.hash;
   history.replaceState(null,'',previous);history.pushState(null,'',u);
  }
 });
 window.addEventListener('hashchange',()=>openAnchor(location.hash));
 window.addEventListener('popstate',()=>{
  const p=new URLSearchParams(location.search);
  tumor=tumors.includes(p.get('tumor'))?p.get('tumor'):'hcc';
  view=views.includes(p.get('view'))?p.get('view'):'options';
  setting.value=validSettings.includes(p.get('setting'))?p.get('setting'):'all';
  if(!openAnchor(location.hash))update();
 });
 const empty=document.createElement('p');empty.id='no-papers';empty.hidden=true;
 empty.textContent='No matching papers. Clear the search or select another tumor or PDF status.';
 $('.library-list').after(empty);
 let printState=[];
 window.addEventListener('beforeprint',()=>{printState=$$('details').map(d=>[d,d.open]);printState.forEach(([d])=>d.open=true);});
 window.addEventListener('afterprint',()=>{printState.forEach(([d,open])=>d.open=open);printState=[];});
 if(!openAnchor(location.hash))update();
})();
