/* One-screen overview. Study-level colors never rank whole modalities. */
(() => {
  'use strict';
  const url=new URL('../lrt/comparisons.json?v=20261105-compact1',document.currentScript.src);
  const names={hcc:'HCC',icca:'iCCA',pcca:'pCCA / hCCA',crlm:'CRLM',nelm:'NELM'};
  const core=['abl','sbrt','y90','tace','hai','htx'];
  const esc=x=>String(x??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  let pending;
  const load=()=>pending||(pending=fetch(url).then(r=>{if(!r.ok)throw Error('Unavailable');return r.json();}).catch(e=>{pending=null;throw e;}));
  const link=(href,label)=>href?`<a href="${esc(href)}" target="_blank" rel="noopener">${esc(label)} ↗</a>`:'';
  const links=r=>[link(r.tmc,r.label==='RETNET RCT'?'TMC protocol':'TMC full text'),link(r.pubmed,'PMID '+r.pmid+(r.label==='RETNET RCT'?' · protocol':'')),link(r.doi?'https://doi.org/'+r.doi:'','DOI / original article')].filter(Boolean).join('');
  const key=(a,b)=>[a,b].sort().join('|');
  const ordered=(items,data)=>Object.keys(data.arms).filter(k=>items.includes(k));
  const rank=r=>!/non[- ]?random/i.test(r.design)&&/randomized|randomised|\bRCT\b/i.test(r.design)?0:/prospective/i.test(r.design)?1:2;
  const shortWinner={'Transplant':'LT','HAIC-FOLFOX':'HAIC','HAIC + sorafenib':'HAIC+sys','TACE + EBRT':'TACE+RT','TACE + RFA':'TACE+RFA','TACE + durvalumab/bevacizumab':'Add-on','TACE + lenvatinib/pembrolizumab':'Add-on','Adjuvant HAIC':'Adj. HAIC','Adjuvant TACE':'Adj. TACE','Personalized Y90 dose':'Personalized','Whole-liver RT':'RT','Radioactive stent + HAIC':'Rad. stent','Y90 + fluorouracil':'Y90+FU','Y90 + second-line chemotherapy':'Y90+chemo','HAI oxaliplatin + IV LV5FU2':'HAI-ox','HAI + systemic':'HAI+sys'};
  const sortPairs=(pairs,refs)=>pairs.sort((a,b)=>rank(refs[a.study])-rank(refs[b.study])||Number(refs[b.study].year)-Number(refs[a.study].year));
  const badge=(p,data)=>`<span class="lcm-badge v-${p.screen.verdict}" title="${esc(data.verdicts[p.screen.verdict].description)}">${esc(data.verdicts[p.screen.verdict].symbol)} ${esc(data.verdicts[p.screen.verdict].label)}</span>`;

  function study(p,r,data,first){
    return `<details class="lcm-study" data-study="${esc(r.id)}" data-pair="${esc(p.id)}"${first?' open':''}>
      <summary><span><strong>${esc(p.screen.label)}</strong> ${badge(p,data)}<span class="lcm-study-mini">${esc(p.screen.result)}</span></span></summary>
      <div class="lcm-study-body"><p class="lcm-arms"><b>Comparison:</b> ${esc(p.arms)}</p>
        <p><b>What the label means:</b> ${esc(p.screen.favored?p.screen.favored+' · '+p.screen.endpoint+'. ':'')}${esc(data.verdicts[p.screen.verdict].description)} ${esc(p.screen.rationale)}</p>
        <dl class="lcm-study-info"><div><dt>Design / setting</dt><dd>${esc(r.design)} · ${esc(data.settings[r.setting])}</dd></div><div><dt>Population / applicability</dt><dd>${esc(r.population)}</dd></div><div><dt>Results</dt><dd>${esc(r.result)}</dd></div><div><dt>Limitations / generalizability</dt><dd>${esc(r.caution)}</dd></div></dl>
        <details class="lcm-sources"><summary>Sources & full text</summary><p>${esc([r.author,r.journal,r.year].filter(Boolean).join(' · '))}</p><div class="lcm-links">${links(r)}</div></details>
      </div></details>`;
  }
  function openCell(host,entries,a,b,data,refs){
    const dialog=document.createElement('dialog');dialog.className='lcm-dialog';dialog.setAttribute('aria-label',data.arms[a]+' versus '+data.arms[b]);
    dialog.innerHTML=`<header><div><span class="lcm-dialog-kicker">${esc(names[host.dataset.tumor])} · ${entries.length} ${entries.length===1?'study report':'study reports'}</span><h3>${esc(data.arms[a])} <span>vs</span> ${esc(data.arms[b])}</h3></div><button type="button" class="lcm-close" aria-label="Close study details">×</button></header>
      <div class="lcm-dialog-body"><p class="lcm-dialog-note">Labels describe each study’s stated endpoint and population. Results from different settings are not a combined treatment ranking.</p>${entries.map((p,i)=>study(p,refs[p.study],data,i===0)).join('')}</div>`;
    document.body.append(dialog);dialog.querySelector('.lcm-close').onclick=()=>dialog.close();dialog.addEventListener('click',e=>{if(e.target===dialog){const r=dialog.getBoundingClientRect();if(e.clientX<r.left||e.clientX>r.right||e.clientY<r.top||e.clientY>r.bottom)dialog.close();}});dialog.addEventListener('close',()=>dialog.remove(),{once:true});dialog.showModal();
  }
  function legend(host,data){
    const d=document.createElement('dialog');d.className='lcm-dialog lcm-legend-dialog';d.setAttribute('aria-label','How to read comparison colors');
    d.innerHTML=`<header><h3>How to read the colors</h3><button class="lcm-close" aria-label="Close color key">×</button></header><div class="lcm-dialog-body">${Object.entries(data.verdicts).map(([k,v])=>`<p><span class="lcm-badge v-${k}">${esc(v.symbol)} ${esc(v.label)}</span><br>${esc(v.description)}</p>`).join('')}<p>One report is previewed per cell, with randomized studies first. Click a cell for every included report, its actual treatment arms, population, endpoints, limitations and source links. A blank cell means no included comparison.</p><p><b>Abbreviations:</b> OS overall survival; PFS progression-free survival; RFS recurrence-free survival; DFS disease-free survival; TTP time to progression; FFLP freedom from local progression; CR complete response; DCR disease-control rate; QoL quality of life; HR hazard ratio; sHR subdistribution hazard ratio; CI confidence interval; NS not statistically significant; NI non-inferiority. Mo/months, y/years. Colors are study findings, not recommendation grades.</p></div>`;
    document.body.append(d);d.querySelector('.lcm-close').onclick=()=>d.close();d.addEventListener('close',()=>d.remove(),{once:true});d.showModal();
  }
  function focusView(host,redraw){
    if(host._focusDialog){host._focusDialog.close();return;}
    const marker=document.createComment('comparison matrix position');host.before(marker);
    const dialog=document.createElement('dialog');dialog.className='lcm-screen-dialog';dialog.setAttribute('aria-label','Comparison matrix screen view');document.body.append(dialog);dialog.append(host);host._focusDialog=dialog;
    dialog.addEventListener('close',()=>{marker.replaceWith(host);host._focusDialog=null;dialog.remove();redraw();host.querySelector('.lcm-screen').focus({preventScroll:true});},{once:true});redraw();dialog.showModal();
  }
  function table(host,data,rows,pairs,f){
    const refs=Object.fromEntries(rows.map(r=>[r.id,r])),direct=f.mode==='direct';
    const axes=ordered([...new Set(pairs.flatMap(p=>[p.a,p.b]))],data),selected=f.treatment;
    let rowAxes,cols,visible=pairs;
    if(direct){
      if(selected&&!axes.includes(selected))return '<p class="lcm-empty">No comparative study is included for this treatment and setting.</p>';
      rowAxes=selected?[selected]:axes.slice(0,-1);cols=selected?axes.filter(a=>a!==selected):axes.slice(1);
    }else{if(selected)visible=pairs.filter(p=>p.a===selected||p.b===selected);rowAxes=ordered([...new Set(visible.map(p=>p.a))],data);cols=ordered([...new Set(visible.map(p=>p.b))],data);}
    if(!cols.length||!rowAxes.length)return '<p class="lcm-empty">No comparative study is included for this selection.</p>';
    const grouped={};visible.forEach(p=>(grouped[direct?key(p.a,p.b):p.a+'|'+p.b]??=[]).push(p));
    host._lcmCells={};
    function cell(a,b){
      if(direct&&a===b)return '<td class="lcm-diagonal" aria-label="Same treatment">·</td>';
      const entries=sortPairs(grouped[direct?key(a,b):a+'|'+b]||[],refs);
      if(!entries.length)return '<td class="lcm-gap"><span aria-label="No comparative study included">—</span></td>';
      const id=a+'|'+b;host._lcmCells[id]={entries,a,b,refs};
      const reverse=direct&&!selected&&axes.indexOf(a)>axes.indexOf(b);
      if(reverse)return `<td class="lcm-mirror"><button type="button" data-cell="${id}" aria-label="Open ${esc(data.arms[a])} versus ${esc(data.arms[b])}">${entries.length} ↗</button></td>`;
      const p=entries[0],v=data.verdicts[p.screen.verdict];
      return `<td class="lcm-pair" data-row-arm="${a}" data-col-arm="${b}" data-pairs="${entries.map(p=>p.id).join(' ')}"><button type="button" class="lcm-preview v-${p.screen.verdict}" data-cell="${id}" data-preview="${p.id}" aria-label="${esc(data.arms[a]+' versus '+data.arms[b]+'. '+p.screen.label+'. '+v.label+'. '+p.screen.result+'. Open all '+entries.length+' reports and sources.')}">
       <span class="lcm-preview-top"><strong>${esc(p.screen.label)}</strong><span class="lcm-preview-symbol" title="${esc(v.label+(p.screen.favored?': '+p.screen.favored+' · '+p.screen.endpoint:''))}">${esc(v.symbol)}${p.screen.verdict==='superior'?' '+esc(shortWinner[p.screen.favored]||p.screen.favored):''}</span>${entries.length>1?`<span class="lcm-report-count" title="${entries.length} reports">+${entries.length-1}</span>`:''}</span>
       <span class="lcm-preview-result">${esc(p.screen.result)}</span></button></td>`;
    }
    return `<div class="lcm-table-wrap" tabindex="0" role="region" aria-label="${esc(names[host.dataset.tumor])} comparison matrix"><table class="lcm-grid" style="--lcm-cols:${cols.length};--lcm-rows:${rowAxes.length}"><caption class="lcm-sr">Treatment by treatment. Click a cell for all studies and source links. Each color applies to the previewed study only.</caption><colgroup><col class="lcm-row-col">${cols.map(()=>'<col>').join('')}</colgroup>
      <thead><tr><th scope="col" class="lcm-corner">Treatment ↓<br>Compared with →</th>${cols.map(a=>`<th scope="col">${esc(data.arms[a])}</th>`).join('')}</tr></thead>
      <tbody>${rowAxes.map(a=>`<tr><th scope="row">${esc(data.arms[a])}</th>${cols.map(b=>cell(a,b)).join('')}</tr>`).join('')}</tbody></table></div>`;
  }
  function draw(host,data,tumor,f){
    const all=data.rows.filter(r=>r.tumor===tumor),byId=Object.fromEntries(all.map(r=>[r.id,r]));
    const allPairs=data.pairs.filter(p=>byId[p.study]),eligible=allPairs.filter(p=>!f.setting||byId[p.study].setting===f.setting);
    const count=m=>new Set(eligible.filter(p=>p.mode===m).map(p=>p.study)).size;
    if(!count(f.mode))f.mode=Object.keys(data.modes).find(m=>count(m))||'direct';
    const pairs=eligible.filter(p=>p.mode===f.mode),armKeys=ordered([...new Set(pairs.flatMap(p=>[p.a,p.b]).concat(f.mode==='direct'?core:[]))],data);
    if(f.treatment&&!armKeys.includes(f.treatment))f.treatment='';
    const n=new Set(pairs.filter(p=>!f.treatment||p.a===f.treatment||p.b===f.treatment).map(p=>p.study)).size;
    host.id=host.id||'lrt-comparisons-'+tumor;host.classList.add('lcm');host.dataset.tumor=tumor;
    const options=(items,v,label)=>`<option value="">${label}</option>`+items.map(([k,l])=>`<option value="${esc(k)}"${v===k?' selected':''}>${esc(l)}</option>`).join('');
    const tumorPicker=host._focusDialog&&host.id==='comparison-matrix'?`<select class="lcm-tumor-picker" aria-label="Tumor type">${Object.entries(names).map(([k,l])=>`<option value="${k}"${tumor===k?' selected':''}>${l}</option>`).join('')}</select>`:'';
    host.innerHTML=`<div class="lcm-heading">${tumorPicker}<h2>${tumorPicker?'Treatment comparisons':esc(names[tumor])+' · Treatment comparisons'}</h2><span class="lcm-count" role="status">${n} reports</span><button type="button" class="lcm-screen">${host._focusDialog?'Return to page':'Screen view ↗'}</button></div>
     <div class="lcm-toolbar"><div class="lcm-modes" role="group" aria-label="Comparison type">${Object.entries(data.modes).map(([m,l])=>`<button type="button" data-mode="${m}" aria-pressed="${f.mode===m}"${!count(m)?' disabled':''}>${esc(m==='direct'?'Treatments':m==='combined'?'Combinations':'Technique / dose')}</button>`).join('')}</div>
     <label><span class="lcm-sr">Clinical setting</span><select data-filter="setting" aria-label="Clinical setting">${options(Object.entries(data.settings).filter(([k])=>all.some(r=>r.setting===k)),f.setting,'All settings')}</select></label>
     <label><span class="lcm-sr">Focus treatment</span><select data-filter="treatment" aria-label="Focus treatment">${options(armKeys.map(k=>[k,data.arms[k]]),f.treatment,'All treatments')}</select></label><button type="button" class="lcm-reset"${!f.setting&&!f.treatment?' hidden':''}>Reset</button></div>
     <div class="lcm-legend"><span class="v-superior">▲ Superiority</span><span class="v-noninferior">≈ Non-inferiority</span><span class="v-signal">↗ Signal only</span><span class="v-uncertain">? Uncertain / not shown</span><button class="lcm-key-button" type="button" aria-label="Explain colors and abbreviations">ⓘ</button><span class="lcm-legend-note">Study endpoint only · ≈? NI unresolved</span></div>
     ${table(host,data,all,pairs,f)}
     <p class="lcm-foot">One study preview per cell · Click for all studies, limitations & links · +n = additional reports · — = no included comparison</p>`;
    const redraw=()=>draw(host,data,tumor,f);
    host.querySelectorAll('[data-filter]').forEach(s=>s.addEventListener('change',()=>{const k=s.dataset.filter;f[k]=s.value;redraw();host.querySelector(`[data-filter="${k}"]`).focus({preventScroll:true});}));
    host.querySelectorAll('[data-mode]').forEach(b=>b.onclick=()=>{f.mode=b.dataset.mode;f.treatment='';redraw();host.querySelector(`[data-mode="${f.mode}"]`).focus({preventScroll:true});});
    host.querySelector('.lcm-reset').onclick=()=>{f.setting='';f.treatment='';redraw();};
    host.querySelector('.lcm-screen').onclick=()=>focusView(host,redraw);
    const picker=host.querySelector('.lcm-tumor-picker');if(picker)picker.onchange=()=>document.querySelector('#tumtabs [data-t="'+picker.value+'"]').click();
    host.querySelector('.lcm-key-button').onclick=()=>legend(host,data);
    host.querySelectorAll('[data-cell]').forEach(b=>b.onclick=()=>{const c=host._lcmCells[b.dataset.cell];openCell(host,c.entries,c.a,c.b,data,c.refs);});
  }
  async function mount(host,tumor){
    if(!host||!names[tumor])return;const token=(host._lcmToken||0)+1;host._lcmToken=token;
    host.innerHTML='<p class="lcm-loading" role="status">Loading treatment comparisons…</p>';
    try{const data=await load();if(host._lcmToken!==token)return;host._lcmFilters??={};const f=host._lcmFilters[tumor]??={setting:'',treatment:'',mode:'direct'};draw(host,data,tumor,f);if(host.id==='comparison-matrix'&&new URLSearchParams(location.search).get('compare')==='1'&&!host._autoFocusApplied){host._autoFocusApplied=true;host.querySelector('.lcm-screen').click();}}
    catch(e){if(host._lcmToken!==token)return;host.innerHTML='<p class="lcm-empty">The comparison matrix could not load. <button type="button">Try again</button></p>';host.querySelector('button').onclick=()=>mount(host,tumor);}
  }
  window.LrtComparisons={mount};
  const init=()=>{const detail=document.getElementById('lrtDetail'),slug=location.pathname.split('/').filter(Boolean).find(p=>['hcc','crlm','icca','nelm'].includes(p));if(detail&&slug&&!document.querySelector('[data-lrt-tumor]')){const h=document.createElement('section');h.dataset.lrtTumor=slug;detail.after(h);}document.querySelectorAll('[data-lrt-tumor]').forEach(h=>mount(h,h.dataset.lrtTumor));};
  if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',init,{once:true});else init();
})();
