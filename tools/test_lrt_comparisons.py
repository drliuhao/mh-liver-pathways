"""Comparison rows retain source values, actual regimens and every reviewed report."""
import json,subprocess,hashlib
from pathlib import Path
R=Path(__file__).resolve().parents[1]
read=lambda f:json.loads((R/f).read_text())
data=read('lrt/comparisons.json');source=read('tools/lrt_comparative_evidence.json')['studies'];matrix=read('lrt/matrix.json');compact=read('tools/compact_evidence_source.json')['studies']
rows=data['rows'];assert len(rows)==101 and len({r['id'] for r in rows})==101
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
for pid in ['33739462','35617978','39225612','31670746','32749512']:
 assert not any(r.get('pmid')==pid for r in rows),('Single-arm study used as comparison',pid)
# Retain the V20 source baseline, replaying only recorded subsequent clinical edits.
later=[json.loads(p.read_text()) for p in sorted((R/'tools/clinical_revisions').glob('*.json')) if p.name>'2026-11-05']
for f in ['lrt/matrix.json','tools/compact_evidence_source.json','tools/lrt_comparative_evidence.json','transplant/assets/content.json']:
 baseline=subprocess.check_output(['git','show','90d7afb:'+f],cwd=R).decode()
 for rev in later:
  for e in rev.get('files',[]):
   if e['file']==f:
    assert baseline.count(e['old'])==1,(rev['id'],f)
    baseline=baseline.replace(e['old'],e['new'])
 if f=='transplant/assets/content.json':
  baseline=json.loads(baseline)
  for rev in later:
   for e in rev.get('edits',[]):
    assert e['op']=='replace_value',e['op']
    holder=baseline
    for k in e['path'][:-1]:holder=holder[k]
    k=e['path'][-1];assert holder[k]==e['old'],e['path'];holder[k]=e['new']
  assert baseline==read(f),f
 else:assert baseline==(R/f).read_text(),f
pairs=data['pairs']
assert {p['study'] for p in pairs}=={r['id'] for r in rows}
assert len({p['id'] for p in pairs})==len(pairs)
for p in pairs:
 assert p['a'] in data['arms'] and p['b'] in data['arms'] and p['a']!=p['b']
 assert p['mode'] in data['modes'] and p['arms'] and p['brief'] and p['note']
 assert len(p['brief'])<=180 and len(p['note'])<=110,(p['id'],'not concise')
def at(pid):return [p for p in pairs if p['study'].endswith('-'+pid)]
assert {(p['a'],p['b']) for p in at('34358718')}=={('y90','tace'),('abl','tace')}
for pid,a,b in [('27930089','y90','tace_abl'),('36100064','y90','tace_abl'),('11843249','y90_hai','hai'),('42018958','hai_sys','systemic'),('33687130','hai_abl','abl'),('35993224','hai_abl','hai')]:
 assert [(p['mode'],p['a'],p['b']) for p in at(pid)]==[('combined',a,b)],pid
assert at('39311927')[0]['mode']=='technique' and 'Both arms received HAIC' in at('39311927')[0]['note']
assert all('Recipient' in p['note'] or 'recipient' in p['note'] for pid in ['28799575','28668402','35619164','42379392'] for p in at(pid))
assert at('32615109')[0]['a']=='lt' and at('32615109')[0]['b']=='nonlt'
assert not any('htx' in [p['a'],p['b']] for p in pairs),'No comparative histotripsy trial in this source set'
assert [(p['a'],p['b']) for p in at('abstract-RETNET-RCT')]==[('tae','ctace')]
print(f'PASS: 101 source records and {len(pairs)} explicit treatment pairs; combination arms and effect order retained; clinical changes match recorded revisions.')

# Screen colors are per endpoint, and null trials never become non-inferiority.
for p in pairs:
 s=p['screen'];assert s['verdict'] in data['verdicts'] and len(s['result'])<=64
 assert s['label'] and s['rationale']
 if s['verdict']=='superior':
  r=next(r for r in rows if r['id']==p['study']);design=r['design'].lower()
  assert ('randomized' in design or 'rct' in design) and 'nonrandom' not in design,p['id']
  assert s['favored'] and s['endpoint']
assert at('39848272')[0]['screen']['verdict']=='ni_uncertain'
for pid in ['40554738','35949295','42829779','33687130','39699905','39644535','29107679','29498924']:
 assert all(p['screen']['verdict']=='uncertain' for p in at(pid)),pid
for pid in ['34358718','41580092','41056563','26695839','42433279','28677067']:
 assert all(p['screen']['verdict']=='signal' for p in at(pid)),pid
assert at('35258371')[0]['screen']['endpoint']=='TTP'
assert at('27575820')[0]['screen']['endpoint']=='TTP'
assert not any(p['screen']['verdict']=='noninferior' for p in pairs),'Current review has no unqualified confirmed-NI label'
print('PASS: compact results and explicit endpoint-specific color labels; negative/observational trials are not promoted to superiority or NI.')
