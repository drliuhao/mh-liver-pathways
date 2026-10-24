(()=>{
 'use strict';
 const params=new URLSearchParams(location.search),allowed=['all','hcc','pcca','icca','crlm','nelm'];
 let tumor=allowed.includes(params.get('tumor'))?params.get('tumor'):'all';
 const buttons=[...document.querySelectorAll('[data-filter]')],cards=[...document.querySelectorAll('.regimen-card')],papers=[...document.querySelectorAll('.library-entry')];
 const search=document.querySelector('#therapy-search'),setting=document.querySelector('#setting');
 function updatePapers(){
  const q=document.querySelector('#paper-search').value.toLowerCase().trim(),pdf=document.querySelector('#pdf-filter').value;let count=0;
  papers.forEach(p=>{p.hidden=!(tumor==='all'||p.dataset.tumors.split(' ').includes(tumor))||!(pdf==='all'||p.dataset.pdf===pdf)||!p.textContent.toLowerCase().includes(q);if(!p.hidden)count++;});
  document.querySelector('#paper-count').textContent=`${count} ${count===1?'paper':'papers'}`;
 }
 function update(){
  buttons.forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.filter===tumor)));
  const q=search.value.toLowerCase().trim(),s=setting.value;let count=0;
  cards.forEach(c=>{c.hidden=!(tumor==='all'||c.dataset.tumors.split(' ').includes(tumor))||!(s==='all'||c.dataset.setting===s)||!c.textContent.toLowerCase().includes(q);if(!c.hidden)count++;});
  document.querySelector('#result-count').textContent=`${count} ${count===1?'option':'options'}`;document.querySelector('#no-results').hidden=count!==0;
  document.querySelectorAll('.therapy-matrix [data-tumor]').forEach(c=>{c.hidden=tumor!=='all'&&c.dataset.tumor!==tumor;});
  document.querySelectorAll('.therapy-matrix tbody tr').forEach(row=>{row.hidden=s!=='all'&&row.dataset.setting!==s;row.querySelectorAll('td p').forEach(p=>{const a=p.querySelector('a');if(a){const c=document.getElementById(a.hash.slice(1));p.hidden=c.hidden;}});});
  document.querySelector('.therapy-matrix').style.minWidth=tumor==='all'?'950px':'0';updatePapers();
  const u=new URL(location.href);if(tumor==='all')u.searchParams.delete('tumor');else u.searchParams.set('tumor',tumor);history.replaceState(null,'',u);
 }
 buttons.forEach(b=>b.addEventListener('click',()=>{tumor=b.dataset.filter;update();}));search.addEventListener('input',update);setting.addEventListener('change',update);
 document.querySelector('#paper-search').addEventListener('input',updatePapers);document.querySelector('#pdf-filter').addEventListener('change',updatePapers);
 // Incoming option links should remain visible even when a stale filter is present.
 const anchor=document.getElementById(location.hash.slice(1));if(anchor?.classList.contains('regimen-card')&&tumor!=='all'&&!anchor.dataset.tumors.split(' ').includes(tumor))tumor=anchor.dataset.tumors.split(' ')[0];
 update();
})();
