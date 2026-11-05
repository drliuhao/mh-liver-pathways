"""Comparison rows retain source values, actual regimens and every reviewed report."""
import json,subprocess,hashlib
from pathlib import Path
R=Path(__file__).resolve().parents[1]
read=lambda f:json.loads((R/f).read_text())
data=read('lrt/comparisons.json');source=read('tools/lrt_comparative_evidence.json')['studies'];matrix=read('lrt/matrix.json');compact=read('tools/compact_evidence_source.json')['studies']
rows=data['rows'];assert len(rows)==97 and len({r['id'] for r in rows})==97
for study in source:
 r=next(r for r in rows if r['tumor']==study['tumor'] and r.get('pmid')==study['pmid'])
 for key in ['design','population','result','caution']:assert r[key]==study[key],(r['id'],key)
 assert r['summary']==compact[r['pmid']]['result'] and r['shortCaution']==compact[r['pmid']]['caution']
for r in rows:
 assert r['setting'] in data['settings'] and all(m in data['treatments'] for m in r['treatments'])
 assert r['comparison'] and r['summary'] and r['caution']
 if r['origin']=='compact-evidence':
  c=compact[r['pmid']]
  for a,b in [('population','arms'),('result','result'),('caution','caution')]:assert r[a]==c[b]
 if r['origin'].startswith('matrix'):
  entries=[e for k,c in matrix['cells'].items() if k.startswith(r['tumor']+'|') for role in c['roles'] for e in role['ev']]
  assert any(e[2]==r['result'] for e in entries),r['id']
 assert r['pubmed'] or r['doi'],r['id']
# A postoperative HAI trial is not a head-to-head ablation trial.
assert 'abl' not in next(r for r in rows if r.get('pmid')=='42018958')['treatments']
for pid in ['29091283','40554738','27575820','35258371','39848272','39311927','16134179']:
 assert any(r.get('pmid')==pid for r in rows),pid
for pid in ['33739462','35617978','39225612','31670746']:
 assert not any(r.get('pmid')==pid for r in rows),('Single-arm study used as comparison',pid)
# A layout-only change leaves the source clinical data identical to V20.
for f in ['lrt/matrix.json','tools/compact_evidence_source.json','tools/lrt_comparative_evidence.json','transplant/assets/content.json']:
 baseline=subprocess.check_output(['git','show','90d7afb:'+f],cwd=R)
 assert baseline==(R/f).read_bytes(),f
print('PASS: 97 unique tumour-study rows; all 40 detailed comparisons preserved, older trials included, single-arm evidence excluded; clinical sources unchanged.')
