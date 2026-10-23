/* Navigation only. No changes to clinical content or pathway state. */
(() => {
  const root=new URL('../',document.currentScript.src);
  const path=location.pathname.slice(root.pathname.length).split('/').filter(Boolean);
  const transplant=path[0]==='transplant';
  const key=transplant?path[1]:path[0];
  const pairs={hcc:'hcc',pcca:'hilar',icca:'icca',crlm:'crlm',nelm:'nelm',hca:'adenoma'};
  const inverse=Object.fromEntries(Object.entries(pairs).map(([a,b])=>[b,a]));
  const match=transplant?pairs[key]:inverse[key];
  const nav=document.createElement('nav');nav.className='shared-portal-nav';nav.setAttribute('aria-label','Shared oncology portal');
  const add=(url,label,current=false)=>{const a=document.createElement('a');a.href=new URL(url,root);a.textContent=label;if(current)a.setAttribute('aria-current','true');nav.append(a);};
  add('','← Shared home');add('#hpb-roadmaps','HPB oncology roadmaps',!transplant);add('transplant/','Standard-risk transplant protocols',transplant);
  if(match)add(transplant?match+'/':'transplant/'+match+'/',transplant?'This tumor’s treatment roadmap →':'This tumor’s transplant pathway →');
  document.body.prepend(nav);
})();
