/* Preserve unique AFP questions and stable anchors; show one addressed question at a time. */
(()=>{'use strict';const sections=[...document.querySelectorAll('main>section[id^="b1-1"]')],main=document.querySelector('main');if(!sections.length)return;
const nav=document.createElement('nav');nav.className='issue-index';nav.setAttribute('aria-label','AFP discussion questions');
for(const s of sections){const a=document.createElement('a');a.href='#'+s.id;a.textContent=s.querySelector('h2').textContent;nav.append(a);}sections[0].before(nav);
const back=document.createElement('a');back.href='#';back.textContent='← All AFP discussion questions';nav.before(back);
function render(){const id=decodeURIComponent(location.hash.slice(1)),chosen=sections.find(s=>s.id===id);for(const s of sections)s.hidden=!!chosen&&s!==chosen;nav.hidden=!!chosen;back.hidden=!chosen;if(chosen)requestAnimationFrame(()=>chosen.scrollIntoView({block:'start'}));}
window.addEventListener('hashchange',render);render();})();
