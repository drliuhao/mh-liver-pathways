import json,re
from pathlib import Path
R=Path(__file__).resolve().parents[2]
oldkeys=['20261031-ui1','20261030-docs2','20261030-review1','20261029-docs1','20261029-nav1','20261026-tools1']
protected={f:(R/f).read_text() for f in ['hcc/index.html','lrt/index.html']}
changed=[]
for p in R.rglob('*'):
 if not p.is_file() or p.suffix not in ['.html','.js','.css','.py','.cjs']:continue
 rel=p.relative_to(R)
 if any(x in rel.parts for x in ['.git','audit_revision','clinical_revisions','__pycache__']):continue
 s=p.read_text();v=s
 for old in oldkeys:v=v.replace(old,'20261102-review1')
 if v!=s:p.write_text(v);changed.append(str(rel))
m=R/'tools/clinical_revisions/2026-11-02-zzzzzz-release.json'
f=[dict(file=n,old=s,new=(R/n).read_text()) for n,s in protected.items() if (R/n).read_text()!=s]
m.write_text(json.dumps(dict(id='2026-11-02-zzzzzz-release',reason='Refresh client assets after clinical reconciliation; no criterion changes.',files=f),ensure_ascii=False,indent=2)+'\n')
p=R/'changes/index.html';s=p.read_text();at=s.index('</header>')+len('</header>');entry='<h2>1 November 2026 · reconciled review edition</h2><ul><li>Applied supported findings from the completed review batches across the cancer roadmaps, transplant pathways and treatment matrices. Corrected trial populations, survival time origins, outcome numbers, diagnostic thresholds, source attribution and conditional next-step links. Nonbinding allocation guidance, standard clinical options and proposed high-risk routes remain distinct. Unresolved source-access and appraisal limitations remain explicit.</li><li>Released a separate sharing edition with the same clinical decisions, evidence summaries and literature-access links, without downloadable protocols, discussion documents or slide decks. Versioned Word and presentation files in the full edition retain their separately dated source wording.</li></ul>'
assert 'reconciled review edition' not in s
p.write_text(s[:at]+entry+s[at:])
(R/'.gitignore').write_text('__pycache__/\n*.py[cod]\n')
print('Cache updated in',len(changed),'files; release log added.')
