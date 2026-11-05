/* One comparison table per tumour, using reviewed source text without ranking trials. */
(() => {
  'use strict';
  const script = document.currentScript;
  const url = new URL('../lrt/comparisons.json?v=20261104-compare1', script.src);
  const labels = {hcc:'HCC',icca:'iCCA',pcca:'pCCA / hCCA',crlm:'CRLM',nelm:'NELM'};
  const esc = value => String(value ?? '').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  let promise;
  const load = () => promise || (promise = fetch(url).then(r => {if(!r.ok)throw Error('Comparison table unavailable');return r.json();}).catch(e=>{promise=null;throw e;}));
  const link = (href,text) => href ? `<a href="${esc(href)}" target="_blank" rel="noopener">${esc(text)} ↗</a>` : '';
  const sourceLinks = r => [link(r.pubmed,'PMID '+r.pmid),link(r.doi ? 'https://doi.org/'+r.doi : '', 'DOI'),link(r.tmc,'TMC full text')].filter(Boolean).join(' · ');

  function row(r,setting) {
    const citation=[r.author,r.journal,r.year].filter(Boolean).join(' · ');
    return `<tr data-study="${esc(r.id)}">
      <th scope="row"><span class="lcm-comparison">${esc(r.comparison)}</span><span class="lcm-setting">${esc(setting)}</span></th>
      <td class="lcm-study" data-label="Study"><strong>${esc(r.label)}</strong><span class="lcm-design">${esc(r.design)}</span>
        ${r.pmid ? link(r.pubmed,'PMID '+r.pmid) : link('https://doi.org/'+r.doi,'Abstract / DOI')}
        <p class="lcm-population">${esc(r.population)}</p>
        <details class="lcm-details"><summary>Details & sources</summary><div>
        <p class="lcm-citation">${esc(citation)}</p><p class="lcm-links">${sourceLinks(r)}</p>
        ${r.result!==r.summary ? `<p><b>Full result:</b> ${esc(r.result)}</p>` : ''}
        ${r.caution!==r.shortCaution ? `<p><b>Interpretation:</b> ${esc(r.caution)}</p>` : ''}</div></details></td>
      <td class="lcm-result" data-label="Results">${esc(r.summary)}</td>
      <td class="lcm-limit" data-label="Interpretation">${esc(r.shortCaution)}</td>
    </tr>`;
  }

  function draw(host,data,tumor,filters) {
    const all=data.rows.filter(r=>r.tumor===tumor);
    const rows=all.filter(r=>(!filters.setting||r.setting===filters.setting)&&(!filters.treatment||r.treatments.includes(filters.treatment)));
    const settings=Object.entries(data.settings).filter(([key])=>all.some(r=>r.setting===key));
    const treatments=Object.entries(data.treatments);
    const id=host.id || (host.id='lrt-comparisons-'+tumor);
    const options=(items,value,allLabel)=>`<option value="">${allLabel}</option>`+items.map(([key,label])=>`<option value="${esc(key)}"${key===value?' selected':''}>${esc(label)}</option>`).join('');
    host.classList.add('lcm');host.dataset.tumor=tumor;
    host.innerHTML=`<div class="lcm-heading"><h2 id="${id}-heading">${esc(labels[tumor])} · Treatment comparisons</h2>
      <p>Compare the treatments within each study. Different patient groups and endpoints limit comparisons between studies.</p></div>
      <div class="lcm-controls"><label>Clinical setting<select data-filter="setting">${options(settings,filters.setting,'All settings')}</select></label>
      <label>Treatment in comparison<select data-filter="treatment">${options(treatments,filters.treatment,'All treatments')}</select></label>
      <button type="button" class="lcm-reset"${!filters.setting&&!filters.treatment?' hidden':''}>Show all</button>
      <p class="lcm-count" role="status" aria-live="polite">${rows.length} of ${all.length} study reports</p></div>
      ${rows.length ? `<div class="lcm-table-wrap"><table aria-labelledby="${id}-heading"><colgroup><col class="lcm-col-compare"><col class="lcm-col-study"><col class="lcm-col-result"><col class="lcm-col-limit"></colgroup><thead><tr><th scope="col">Treatment comparison</th><th scope="col">Study & population</th><th scope="col">Results</th><th scope="col">Interpretation</th></tr></thead><tbody>${rows.map(r=>row(r,data.settings[r.setting])).join('')}</tbody></table></div>` : '<p class="lcm-empty">No comparative study is included for this selection. Available single-arm evidence remains in the treatment cards above.</p>'}
      <details class="lcm-key"><summary>Abbreviations</summary><p>OS: overall survival · PFS: progression-free survival · RFS: recurrence-free survival · DFS: disease-free survival · LC: local control · TTP: time to progression · HR: hazard ratio · sHR: subdistribution hazard ratio · CI: confidence interval · RCT: randomized controlled trial · NS: not statistically significant · ITT: intention-to-treat · RFA: radiofrequency ablation · MWA: microwave ablation · RT: radiotherapy · TARE / SIRT: Y90 radioembolization · TACE: chemoembolization · TAE: bland embolization · HAI / HAIC: hepatic arterial infusion chemotherapy · LT: liver transplantation. Regimens and trial-specific qualifications are shown with each study.</p></details>`;
    host.querySelectorAll('[data-filter]').forEach(select=>select.addEventListener('change',()=>{
      const key=select.dataset.filter;filters[key]=select.value;draw(host,data,tumor,filters);host.querySelector(`[data-filter="${key}"]`).focus({preventScroll:true});
    }));
    host.querySelector('.lcm-reset').addEventListener('click',()=>{filters.setting='';filters.treatment='';draw(host,data,tumor,filters);host.querySelector('[data-filter]').focus({preventScroll:true});});
  }

  async function mount(host,tumor) {
    if(!host||!labels[tumor])return;
    const token=(host._lcmToken||0)+1;host._lcmToken=token;
    host.innerHTML='<p class="lcm-loading" role="status">Loading treatment comparisons…</p>';
    try {
      const data=await load();if(host._lcmToken!==token)return;
      host._lcmFilters=host._lcmFilters||{};
      const filters=host._lcmFilters[tumor]||(host._lcmFilters[tumor]={setting:'',treatment:''});
      draw(host,data,tumor,filters);
    }
    catch(e){if(host._lcmToken!==token)return;host.innerHTML='<p class="lcm-empty">The comparison table could not load. <button type="button">Try again</button></p>';host.querySelector('button').onclick=()=>mount(host,tumor);}
  }
  window.LrtComparisons={mount};
  const init=()=>{
    const detail=document.getElementById('lrtDetail');
    const slug=location.pathname.split('/').filter(Boolean).find(part=>['hcc','crlm','icca','nelm'].includes(part));
    if(detail&&slug&&!document.querySelector('[data-lrt-tumor]')){
      const host=document.createElement('section');host.dataset.lrtTumor=slug;detail.after(host);
    }
    document.querySelectorAll('[data-lrt-tumor]').forEach(host=>mount(host,host.dataset.lrtTumor));
  };
  if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',init,{once:true});else init();
})();
