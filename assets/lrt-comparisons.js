/* Explicit treatment-pair matrix. Clinical source records remain unchanged. */
(() => {
  'use strict';
  const url=new URL('../lrt/comparisons.json?v=20261104-grid1',document.currentScript.src);
  const names={hcc:'HCC',icca:'iCCA',pcca:'pCCA / hCCA',crlm:'CRLM',nelm:'NELM'};
  const core=['abl','sbrt','y90','tace','hai','htx'];
  const esc=x=>String(x??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  let pending;
  const load=()=>pending||(pending=fetch(url).then(r=>{if(!r.ok)throw Error('Unavailable');return r.json();}).catch(e=>{pending=null;throw e;}));
  const link=(href,label)=>href?`<a href="${esc(href)}" target="_blank" rel="noopener">${esc(label)} ↗</a>`:'';
  const links=r=>[
    link(r.tmc,r.label==='RETNET RCT'?'TMC protocol':'TMC full text'),
    link(r.pubmed,'PMID '+r.pmid+(r.label==='RETNET RCT'?' · protocol':'')),
    link(r.doi?'https://doi.org/'+r.doi:'','DOI / article')
  ].filter(Boolean).join('');
  function study(p,r,data){
    return `<article class="lcm-study" data-study="${esc(r.id)}" data-pair="${esc(p.id)}">
      <h4>${esc(r.label)}</h4><p class="lcm-context">${esc(data.settings[r.setting])}</p>
      <p class="lcm-arms">${esc(p.arms)}</p><p class="lcm-result">${esc(p.brief)}</p>
      <p class="lcm-caution">${esc(p.note)}</p><div class="lcm-links">${links(r)}</div>
      <details class="lcm-details"><summary>Study details</summary><div>
        <p class="lcm-citation">${esc([r.author,r.journal,r.year].filter(Boolean).join(' · '))}</p>
        <p><b>Design:</b> ${esc(r.design)}</p><p><b>Population:</b> ${esc(r.population)}</p>
        <p><b>Result:</b> ${esc(r.result)}</p><p><b>Interpretation:</b> ${esc(r.caution)}</p>
      </div></details></article>`;
  }
  const key=(a,b)=>[a,b].sort().join('|');
  const ordered=(items,data)=>Object.keys(data.arms).filter(k=>items.includes(k));
  function table(host,data,rows,pairs,filters){
    const refs=Object.fromEntries(rows.map(r=>[r.id,r]));
    const direct=filters.mode==='direct';
    const available=ordered([...new Set(pairs.flatMap(p=>[p.a,p.b]))],data);
    const axes=available;
    const selected=filters.treatment;
    let rowAxes,cols,visible=pairs;
    if(direct){
      if(selected&&!available.includes(selected))return '<p class="lcm-empty">No comparative study is included for this treatment and setting. Single-arm evidence remains in the treatment cards above.</p>';
      rowAxes=selected?[selected]:axes.slice(0,-1);cols=selected?axes.filter(a=>a!==selected):axes.slice(1);
    }
    else{
      if(selected)visible=pairs.filter(p=>p.a===selected||p.b===selected);
      rowAxes=ordered([...new Set(visible.map(p=>p.a))],data);cols=ordered([...new Set(visible.map(p=>p.b))],data);
    }
    if(!cols.length||!rowAxes.length)return '<p class="lcm-empty">No comparative study is included for this selection. Single-arm evidence remains in the treatment cards above.</p>';
    const grouped={};visible.forEach(p=>(grouped[direct?key(p.a,p.b):p.a+'|'+p.b]??=[]).push(p));
    const cellId=(a,b)=>host.id+'-cell-'+a+'-'+b;
    function cell(a,b){
      if(direct&&a===b)return '<td class="lcm-diagonal" aria-label="Same treatment">·</td>';
      const entries=grouped[direct?key(a,b):a+'|'+b]||[];
      const reverse=direct&&!selected&&axes.indexOf(a)>axes.indexOf(b);
      if(!entries.length)return '<td class="lcm-gap"><span aria-label="No comparative study included">—</span></td>';
      if(reverse)return `<td class="lcm-mirror"><button type="button" data-jump="${esc(cellId(b,a))}" aria-label="See ${esc(data.arms[a])} versus ${esc(data.arms[b])}">${entries.length} ${entries.length===1?'study':'studies'} ↗</button></td>`;
      const rank=r=>/randomized|randomised|\bRCT\b/i.test(r.design)?0:/prospective/i.test(r.design)?1:2;
      entries.sort((a,b)=>rank(refs[a.study])-rank(refs[b.study])||Number(refs[b.study].year)-Number(refs[a.study].year));
      const content=entries.map(p=>study(p,refs[p.study],data));
      return `<td class="lcm-pair" id="${cellId(a,b)}" data-row-arm="${a}" data-col-arm="${b}" tabindex="-1"><div class="lcm-cell-title"><span>${entries.length} ${entries.length===1?'report':'reports'}</span></div>
        ${content.slice(0,2).join('')}${content.length>2?`<details class="lcm-more"><summary>${content.length-2} more ${content.length===3?'study':'studies'}</summary>${content.slice(2).join('')}</details>`:''}</td>`;
    }
    return `<div class="lcm-scroll-hint">Scroll across for more treatments →</div><div class="lcm-table-wrap" tabindex="0" role="region" aria-label="${esc(names[host.dataset.tumor])} treatment comparison matrix, scroll horizontally and vertically">
      <table class="lcm-grid"><caption class="lcm-sr">${esc(data.modes[filters.mode])}. Row and column labels name the compared treatments. Study numbers follow their printed arm order.</caption>
      <colgroup><col class="lcm-row-col">${cols.map(()=>'<col class="lcm-data-col">').join('')}</colgroup>
      <thead><tr><th scope="col" class="lcm-corner">Treatment ↓<br>Compared with →</th>${cols.map(a=>`<th scope="col">${esc(data.arms[a])}</th>`).join('')}</tr></thead>
      <tbody>${rowAxes.map(a=>`<tr><th scope="row">${esc(data.arms[a])}</th>${cols.map(b=>cell(a,b)).join('')}</tr>`).join('')}</tbody></table></div>`;
  }
  function draw(host,data,tumor,f){
    const all=data.rows.filter(r=>r.tumor===tumor), byId=Object.fromEntries(all.map(r=>[r.id,r]));
    const allPairs=data.pairs.filter(p=>byId[p.study]);
    const eligible=allPairs.filter(p=>!f.setting||byId[p.study].setting===f.setting);
    const count=m=>new Set(eligible.filter(p=>p.mode===m).map(p=>p.study)).size;
    if(!count(f.mode))f.mode=Object.keys(data.modes).find(m=>count(m))||'direct';
    const pairs=eligible.filter(p=>p.mode===f.mode);
    const armKeys=ordered([...new Set(pairs.flatMap(p=>[p.a,p.b]).concat(f.mode==='direct'?core:[]))],data);
    if(f.treatment&&!armKeys.includes(f.treatment))f.treatment='';
    const shown=pairs.filter(p=>!f.treatment||p.a===f.treatment||p.b===f.treatment);
    const n=new Set(shown.map(p=>p.study)).size;
    host.id=host.id||'lrt-comparisons-'+tumor;host.classList.add('lcm');host.dataset.tumor=tumor;
    const options=(items,v,label)=>`<option value="">${label}</option>`+items.map(([k,l])=>`<option value="${esc(k)}"${v===k?' selected':''}>${esc(l)}</option>`).join('');
    host.innerHTML=`<div class="lcm-heading"><h2 id="${host.id}-heading">${esc(names[tumor])} · Treatment comparison matrix</h2>
      <p>Choose a row and column. Each cell shows the studies comparing those treatments; numbers follow the arm order printed with each study.</p></div>
      <div class="lcm-modes" role="group" aria-label="Comparison type">${Object.entries(data.modes).map(([m,l])=>`<button type="button" data-mode="${m}" aria-pressed="${f.mode===m}"${!count(m)?' disabled':''}>${esc(l)} <span>${count(m)}</span></button>`).join('')}</div>
      <div class="lcm-controls"><label>Clinical setting<select data-filter="setting">${options(Object.entries(data.settings).filter(([k])=>all.some(r=>r.setting===k)),f.setting,'All settings')}</select></label>
      <label>Focus on one treatment<select data-filter="treatment">${options(armKeys.map(k=>[k,data.arms[k]]),f.treatment,'All treatments')}</select></label>
      <button type="button" class="lcm-reset"${!f.setting&&!f.treatment?' hidden':''}>Reset filters</button>
      <p class="lcm-count" role="status" aria-live="polite">${n} study reports · ${all.length} across all views</p></div>
      ${table(host,data,all,pairs,f)}
      <p class="lcm-legend">— No comparative study included. ↗ The same comparison appears across the diagonal. Combination trials retain their actual regimens; separate studies do not establish a treatment ranking.</p>
      <details class="lcm-key"><summary>Abbreviations & source access</summary><p>OS: overall survival · PFS: progression-free survival · RFS: recurrence-free survival · DFS: disease-free survival · TTP: time to progression · HR: hazard ratio · sHR: subdistribution hazard ratio · CI: confidence interval · ITT: intention-to-treat · IPTW: inverse probability of treatment weighting · NS: not statistically significant (does not establish equivalence) · RCT: randomized controlled trial · MWA: microwave ablation · RFA: radiofrequency ablation · TACE: chemoembolization · TAE: bland embolization · HAI / HAIC: hepatic arterial infusion chemotherapy · RT: radiotherapy · SBRT / SABR: stereotactic radiotherapy · LT: liver transplantation · CR: complete response · QoL: quality of life · AE: adverse event. TMC opens institutional full-text access; DOI opens the original article. Study details retain the full population, result and limitations.</p></details>`;
    host.querySelectorAll('[data-filter]').forEach(select=>select.addEventListener('change',()=>{
      const k=select.dataset.filter;f[k]=select.value;draw(host,data,tumor,f);host.querySelector(`[data-filter="${k}"]`).focus({preventScroll:true});
    }));
    host.querySelectorAll('[data-mode]').forEach(button=>button.addEventListener('click',()=>{f.mode=button.dataset.mode;f.treatment='';draw(host,data,tumor,f);host.querySelector(`[data-mode="${f.mode}"]`).focus({preventScroll:true});}));
    host.querySelector('.lcm-reset').onclick=()=>{f.setting='';f.treatment='';draw(host,data,tumor,f);host.querySelector('[data-filter]').focus({preventScroll:true});};
    host.querySelectorAll('[data-jump]').forEach(button=>button.addEventListener('click',()=>{
      const target=document.getElementById(button.dataset.jump), wrap=host.querySelector('.lcm-table-wrap');
      const r=target.getBoundingClientRect(),w=wrap.getBoundingClientRect();
      const corner=host.querySelector('.lcm-corner').getBoundingClientRect();
      wrap.scrollTo({left:wrap.scrollLeft+r.left-w.left-corner.width-2,top:wrap.scrollTop+r.top-w.top-corner.height-2,behavior:'smooth'});target.focus({preventScroll:true});
    }));
  }
  async function mount(host,tumor){
    if(!host||!names[tumor])return;const token=(host._lcmToken||0)+1;host._lcmToken=token;
    host.innerHTML='<p class="lcm-loading" role="status">Loading treatment comparisons…</p>';
    try{const data=await load();if(host._lcmToken!==token)return;host._lcmFilters??={};const f=host._lcmFilters[tumor]??={setting:'',treatment:'',mode:'direct'};draw(host,data,tumor,f);}
    catch(e){if(host._lcmToken!==token)return;host.innerHTML='<p class="lcm-empty">The comparison matrix could not load. <button type="button">Try again</button></p>';host.querySelector('button').onclick=()=>mount(host,tumor);}
  }
  window.LrtComparisons={mount};
  const init=()=>{
    const detail=document.getElementById('lrtDetail'),slug=location.pathname.split('/').filter(Boolean).find(p=>['hcc','crlm','icca','nelm'].includes(p));
    if(detail&&slug&&!document.querySelector('[data-lrt-tumor]')){const host=document.createElement('section');host.dataset.lrtTumor=slug;detail.after(host);}
    document.querySelectorAll('[data-lrt-tumor]').forEach(host=>mount(host,host.dataset.lrtTumor));
  };
  if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',init,{once:true});else init();
})();
