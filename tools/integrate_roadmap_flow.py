"""Reapply the shared roadmap layout after regenerating a legacy page."""
from pathlib import Path
import re
r=Path(__file__).resolve().parents[1]
for slug in 'hcc crlm icca hilar nelm chcca adenoma incidental pdac pnet pcyst ampullary'.split():
 p=r/slug/'index.html'; s=p.read_text()
 if 'RoadmapFlow.setup(' in s: continue
 s=s.replace('</style>','</style>\n<link rel="stylesheet" href="../assets/roadmap-flow.css?v=20261025">\n<script src="../assets/roadmap-flow.js?v=20261029-ehd2"></script>',1)
 name='Stage' if slug=='hcc' else 'Gate'; data='STAGES' if slug=='hcc' else 'P.gates'; key='"hcc.stage"' if slug=='hcc' else 'KEY+".gate"'
 pat=r'function render'+name+r'\(id\)\{.*?\n\}'
 body=f'''function render{name}(id){{
  const s = {data}.find(x=>x.id===id);
  if(!s) return;
  document.getElementById("answer").innerHTML = RoadmapFlow.render(s,recHTML);
  RoadmapFlow.update(s);
  try{{ localStorage.setItem({key}, id); }}catch(e){{}}
}}'''
 s,n=re.subn(pat,lambda m:body,s,count=1,flags=re.S);assert n==1
 if slug=='hcc':
  s=s.replace('if(b) selectStage(b.dataset.goto);','if(b) RoadmapFlow.navigate(b.dataset.goto);').replace('if(b) selectStage(b.dataset.stage);','if(b) RoadmapFlow.navigate(b.dataset.stage);')
  s=s.replace('let start = "A";',"RoadmapFlow.setup({slug:'hcc',stages:STAGES,select:renderStage,topic:renderTopic});\nlet start = \"A\";")
  s=s.replace('renderStage(start);','start = RoadmapFlow.initial(STAGES,start);\nrenderStage(start);')
 else:
  s=s.replace('  let startGate = P.gates[0].id;',"  RoadmapFlow.setup({slug:P.key,stages:P.gates,select:renderGate});\n  let startGate = P.gates[0].id;")
  s=s.replace('  renderGate(startGate);','  startGate = RoadmapFlow.initial(P.gates,startGate);\n  renderGate(startGate);')
 s=s.replace('b.textContent = open ? "Collapse all" : "Expand all";','b.textContent = open ? "Collapse criteria and evidence" : "Expand criteria and evidence";')
 s=s.replace('b.textContent = open ? "Collapse criteria and evidence" : "Expand criteria and evidence";', 'b.textContent = open ? "Collapse criteria and evidence" : "Expand criteria and evidence";\n    b.setAttribute("aria-expanded", String(open));')
 p.write_text(s)
