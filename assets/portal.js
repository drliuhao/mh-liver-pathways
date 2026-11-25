'use strict';
const search=document.getElementById('portal-search');
search.addEventListener('input',()=>{
  const q=search.value.trim().toLowerCase();
  let total=0;
  document.querySelectorAll('.portal-lane').forEach(lane=>{
    let found=0;
    lane.querySelectorAll('.portal-card').forEach(card=>{card.hidden=!card.dataset.search.includes(q);if(!card.hidden){found++;total++;}});
    lane.querySelectorAll('.portal-group').forEach(group=>{group.hidden=![...group.querySelectorAll('.portal-card')].some(card=>!card.hidden);});
    lane.querySelector('.portal-empty').hidden=found!==0;
  });
  document.getElementById('portal-count').textContent=q?`${total} matching entries`:'12 roadmaps · 2 therapy matrices · standard & high-risk transplant reviews';
});
