import json,re
from pathlib import Path
R=Path(__file__).resolve().parents[2]
p=R/'tools/compact_evidence_source.json'; old=p.read_text(); s=json.loads(old)
remaps=json.loads((R/'tools/audit_revision/compact_option_remap_proposals.json').read_text())['remaps']
for r in remaps:
 for field in ['options','reference_links']:
  if r['old_key'] in s[field]:
   assert r['new_key'] not in s[field]
   s[field][r['new_key']]=s[field].pop(r['old_key'])
 if r['new_key'] in s['options']:s['options'][r['new_key']]['lead']=r['new_lead'][:80]
rows=s['options']['hilar:mmyiw4']['rows']
rows[0]['caution']='Single-arm study; no randomized survival comparison or anatomical-subsite estimate'
rows[1]['result']='Ivosidenib: PFS HR 0.37; ITT OS 10.3 vs 7.5 mo, HR 0.79 (95% CI 0.56–1.12), P=.09'
rows[1]['caution']='Corrected crossover-adjusted HR 0.49 (95% CI 0.25–1.24); neither OS analysis significant'
s['options']['adenoma:1ex2fsl']['rows'][0]['caution']='Major complications 6 of 59 (10%); nonrandomized, non-pregnant cohort'
s['options']['adenoma:2xyicd']['rows'][0]['caution']="Elective complications not reported separately; 'surgery avoided' is a process endpoint"
s['options']['chcca:1c4n2h1']['rows']=[x for x in s['options']['chcca:1c4n2h1']['rows'] if x['pmid']!='38319896']
r=s['options']['pcyst:1qkomof']['rows']
for x in r:
 if x['pmid']=='36209796':x['caution']='Small surgically verified subgroup; negative testing cannot exclude serous cystadenoma'
r[:]=[x for x in r if x['pmid']!='38182527']
r.append(dict(pmid='37230894',result='Pooled VHL testing: sensitivity 56% (95% CI 33–78%), specificity 99% (99–100%); 1,140 cysts',caution='Assay and verification differences; negative VHL does not exclude serous cystadenoma'))
s['options']['icca:16jk2se']['rows']=[dict(pmid='34856069',result='32 listed, 18 transplanted: 5-year OS 49% in the listed cohort and 57% among recipients, both from listing',caution='Selected, nonrandomized cohort; overlaps the earlier six-recipient report')]
# The incidental-lesion option no longer makes a lesion-size imaging comparison.
# Keep its current cited primary-study line, rather than a stale option-specific override.
s['options']['incidental:1u00rqv']['rows']=[x for x in s['options']['incidental:1u00rqv']['rows'] if x['pmid']!='20829538']
pd=json.loads((R/'pdac/data/pathway.json').read_text()); qs=[]
def walk(v):
 if isinstance(v,dict):
  if isinstance(v.get('refs'),list) and '42456089' in v['refs']:qs.extend(v.get(k,'') for k in ['t','pref','avoid','note'])
  for z in v.values():walk(z)
 elif isinstance(v,list):
  for z in v:walk(z)
walk(pd)
s['studies']['42456089']=dict(label='RTOG 0848 final',design='RCT',arms='Adjuvant chemoradiation vs no RT after chemotherapy; 354 patients',result='OS HR 0.96 (90% CI 0.79–1.18); DFS HR 0.82 (95% CI 0.65–1.03), P=.089; grade-3 toxicity 38% vs 19%',caution='Overall negative; selected node-negative discussion; no FOLFIRINOX backbone or SBRT validation',quotes=qs)
new=json.dumps(s,ensure_ascii=False,indent=2)+'\n';p.write_text(new)
m=R/'tools/clinical_revisions/2026-11-02-zzzz-evidence.json';d=json.loads(m.read_text());d['files'].append(dict(file=str(p.relative_to(R)),old=old,new=new));m.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
print('Updated30optionkeys; corrected8stale evidence overrides; added RTOG0848.')
