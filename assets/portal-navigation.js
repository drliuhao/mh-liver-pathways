/* Navigation only. No changes to clinical content or pathway state. */
(() => {
  const root=new URL('../',document.currentScript.src);
  // Shared, progressive presentation layer for roadmaps and decision protocols.
  const infoCSS=document.createElement('link');infoCSS.rel='stylesheet';infoCSS.href=new URL('assets/contextual-info.css?v=20261026-tools1',root);document.head.append(infoCSS);
  const flowCSS=document.createElement('link');flowCSS.rel='stylesheet';flowCSS.href=new URL('assets/clinical-flow.css?v=20261025-1',root);document.head.append(flowCSS);
  const layerCSS=document.createElement('link');layerCSS.rel='stylesheet';layerCSS.href=new URL('assets/decision-layers.css?v=20261026-tools1',root);document.head.append(layerCSS);
  const compactCSS=document.createElement('link');compactCSS.rel='stylesheet';compactCSS.href=new URL('assets/compact-trail.css?v=20261026-tools1',root);document.head.append(compactCSS);
  for(const file of ['contextual-copy.js','contextual-info.js','clinical-flow.js','compact-trail-labels.js','compact-trail.js','clinical-reference.js','clinical-tools.js']){const script=document.createElement('script');script.async=false;script.src=new URL('assets/'+file+'?v=20261026-tools1',root);document.head.append(script);}
  const toolsCSS=document.createElement('link');toolsCSS.rel='stylesheet';toolsCSS.href=new URL('assets/clinical-tools.css?v=20261026-tools1',root);document.head.append(toolsCSS);
  const path=location.pathname.slice(root.pathname.length).split('/').filter(Boolean);
  const transplant=path[0]==='transplant';
  const highRisk=transplant&&path[1]==='high-risk';
  const key=highRisk?path[2]:(transplant?path[1]:path[0]);
  const pairs={hcc:'hcc',pcca:'hilar',icca:'icca',crlm:'crlm',nelm:'nelm',hca:'adenoma'};
  const inverse=Object.fromEntries(Object.entries(pairs).map(([a,b])=>[b,a]));
  const match=transplant?pairs[key]:(key==='chcca'?'icca':inverse[key]);
  const nav=document.createElement('nav');nav.className='shared-portal-nav';nav.setAttribute('aria-label','Shared oncology portal');
  const add=(url,label,current=false)=>{const a=document.createElement('a');a.href=new URL(url,root);a.textContent=label;if(current)a.setAttribute('aria-current','true');nav.append(a);};
  add('','HPB oncology');nav.lastElementChild.className='portal-home';
  const menu=(title,items)=>{const d=document.createElement('details'),summary=document.createElement('summary'),list=document.createElement('div');summary.textContent=title;list.className='portal-menu';d.append(summary,list);items.forEach(([url,label,current,group])=>{if(group){const heading=document.createElement('span');heading.className='portal-menu-group';heading.textContent=group;list.append(heading);}const a=document.createElement('a');a.href=new URL(url,root);a.textContent=label;if(current)a.setAttribute('aria-current','page');list.append(a);});nav.append(d);d.addEventListener('toggle',()=>{if(d.open)nav.querySelectorAll('details').forEach(other=>{if(other!==d)other.open=false;});});};
  menu('Roadmaps', [['#hpb-roadmaps','All cancer roadmaps',false],['hcc/','HCC',key==='hcc'&&!transplant,'Liver'],['hilar/','Perihilar CCA',key==='hilar'],['icca/','Intrahepatic CCA',key==='icca'&&!transplant],['crlm/','Colorectal liver metastases',key==='crlm'&&!transplant],['nelm/','Neuroendocrine liver metastases',key==='nelm'&&!transplant],['chcca/','Combined HCC–CCA',key==='chcca'],['adenoma/','Hepatic adenoma',key==='adenoma'],['incidental/','Incidental liver mass',key==='incidental'],['pdac/','Pancreatic adenocarcinoma',key==='pdac','Pancreas and ampulla'],['pnet/','Pancreatic neuroendocrine tumor',key==='pnet'],['pcyst/','Pancreatic cysts',key==='pcyst'],['ampullary/','Ampullary tumors',key==='ampullary'],['lrt/','Liver-directed therapy matrix',key==='lrt','Treatment matrices'],['systemic/','Systemic therapy matrix',key==='systemic']]);
  menu('Transplant pathways', [['transplant/','All transplant pathways',transplant&&!key],...Object.entries({hcc:'HCC',pcca:'Perihilar CCA',icca:'Intrahepatic CCA',crlm:'Colorectal liver metastases',nelm:'Neuroendocrine liver metastases',hehe:'HEHE',hca:'Hepatic adenoma'}).map(([slug,name])=>['transplant/'+slug+'/',name,transplant&&!highRisk&&key===slug]),['transplant/high-risk/','High-risk protocol index',highRisk]]);
  if(match){add(transplant?match+'/':'transplant/'+match+'/',transplant?'Treatment roadmap →':key==='chcca'?'iCCA / mixed HCC-iCCA transplant criteria →':'Transplant assessment →');nav.lastElementChild.className='portal-pair';}
  document.addEventListener('click',ev=>{if(!nav.contains(ev.target))nav.querySelectorAll('details[open]').forEach(d=>d.open=false);});
  nav.addEventListener('keydown',ev=>{if(ev.key==='Escape'){const d=ev.target.closest('details');if(d){d.open=false;d.querySelector('summary').focus();}}});
  document.body.prepend(nav);
  const footer=document.createElement('footer');footer.className='portal-change-log';
  const log=document.createElement('a');log.href=new URL('changes/',root);log.textContent='Change log';
  const library=document.createElement('a');library.href=new URL('evidence-libraries/',root);library.textContent='Evidence libraries and PPT index';
  footer.append(log,document.createTextNode(' · '),library);document.body.append(footer);
  // A source deep link should reveal its appraisal, not stop at a closed title.
  if(path[0]==='evidence'){
    const revealStudy=()=>{let id;try{id=decodeURIComponent(location.hash.slice(1));}catch{return;}const target=document.getElementById(id);if(!target?.matches('details.study-appraisal'))return;target.open=true;target.style.scrollMarginTop='16px';requestAnimationFrame(()=>target.scrollIntoView({block:'start'}));};
    window.addEventListener('hashchange',revealStudy);requestAnimationFrame(revealStudy);
  }
})();
