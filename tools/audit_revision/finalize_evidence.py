import json,re
from pathlib import Path
R=Path(__file__).resolve().parents[2]
manifest=R/'tools/clinical_revisions/2026-11-02-zzzz-evidence.json'
assert not manifest.exists()
changes=[]
def save(f,d,why):
 p=R/f;old=p.read_text();new=json.dumps(d,ensure_ascii=False,indent=2)+'\n'
 if old!=new:p.write_text(new);changes.append(dict(file=f,old=old,new=new,why=why))
for sl,pm,old,new in [('nelm','25014687','hazard ratio of 0.47 and 65% versus 33%','hazard ratio of 0.47 (95% CI 0.30–0.73) and 65.1% versus 33.0%'),('chcca','38092727','(76.4% vs 45.4% at 5 years),','(76.4% vs 45.4% at 5 years; HR 2.69, 95% CI 1.15–6.31),')]:
 f=f'{sl}/data/critique.json';d=json.loads((R/f).read_text());assert old in d[pm]['bottom_line'];d[pm]['bottom_line']=d[pm]['bottom_line'].replace(old,new);save(f,d,'Source-verified precision in the shared clinical summary: original trial/figure estimates')
f='hcc/data/critique.json';d=json.loads((R/f).read_text());d['39802807']={'kind':'rct','n':'236 treated patients with HCC ≤4 cm in the device-specific MWA versus single-needle RFA trial.','limitations':['Device-specific comparison, mostly small lesions; the lesion-level complete-case result is not a universal ablation superiority claim.'],'critique':['Lower local progression does not establish an overall-survival advantage or dedicated superiority for every 3–4 cm tumour.'],'bottom_line':'Sugimoto 2025: 2-year lesion-level local progression was 20/122 (16.4%) with MWA versus 38/125 (30.4%) with single-needle RFA; RR 0.54 (95% CI 0.33–0.87), P=.007. No overall-survival advantage was demonstrated.'};save(f,d,'A HB031 and B11-R13-CF01; original PDF5/printed4, device-specific trial')
src=json.loads((R/'tools/compact_evidence_source.json').read_text());s=src['studies']
s['41763363']['design']='Prospective cohort';s['41763363']['arms']='61 treated; 16 selected responders listed and transplanted'
s['37329889']['caution']='Initial PFS report; subsequent OS analysis did not show a survival gain; panitumumab arm stopped for futility'
s['32615109']['result']='5-y OS 77.5% vs 31.2% (published HR 0.32, 95% CI 0.11–0.92); tumor-event-free survival 76.8% vs 18.3%; 45 randomized responders'
s['32615109']['caution']='Selected responders; closed early; published abstract corrects a discrepant draft; final full text unavailable'
s['29064885']['result']='Recipient 5-y OS 64% LT vs 18% resection; restricted non-PSC, <3 cm, node-negative comparison 54% vs 29% (P=.03)'
s['29064885']['caution']='Observational selection; different ITT time origins; restricted comparison is not an adjusted treatment effect'
s['37820293']['result']='Nine paired samples: all ctDNA-positive before surgery, three remained positive. Recurrence association was after resection, not LT'
s['37820293']['caution']='Small mixed cohort; inconsistent recurrence denominators; no validated ctDNA-based transplant selection rule'
s['39802807']['quotes']=[d['39802807']['n'],d['39802807']['bottom_line']]
# Numeric and provenance guards use the same source-specific, already reviewed clinical text.
pool={}
def add(pm,*texts):pool.setdefault(str(pm),[]).extend(t for t in texts if isinstance(t,str) and t)
for p in R.glob('*/data/critique.json'):
 for pm,c in json.loads(p.read_text()).items():add(pm,c.get('n'),c.get('bottom_line'),*c.get('critique',[]))
def cited(node):
 if isinstance(node,dict):
  for pm in node.get('refs',[]):
   if re.fullmatch(r'\d{6,9}',str(pm)):add(pm,*(v for k,v in node.items() if k!='refs' and isinstance(v,str)))
  for v in node.values():cited(v)
 elif isinstance(node,list):
  for v in node:cited(v)
for p in R.glob('*/data/pathway.json'):cited(json.loads(p.read_text()).get('gates',[]))
for c in json.loads((R/'systemic/matrix.json').read_text())['cards']:
 for pm in c['refs']:add(pm,c['title'],c['evidence'])
for c in json.loads((R/'lrt/matrix.json').read_text())['cells'].values():
 for role in c['roles']:
  for ev in role['ev']:
   if len(ev)>2:add(ev[1],ev[0],ev[2],role['when'])
hr=json.loads((R/'transplant/assets/content.json').read_text())['high_risk']
for p in hr['pathways'].values():
 for r in p['reviews']:
  for st in r['evidence']['studies']:
   pm=hr['sources'].get(st['key'],{}).get('pmid')
   if pm:add(pm,st.get('design_population'),st.get('results'),st.get('limits'))
for pm in ['22290335','25014687','29064885','29433850','32615109','37820293','38092727','38488934','41763363','42223072','39802807']:
 s[pm]['quotes']=list(dict.fromkeys(pool[pm]))
s['42879142']['quotes']=[json.loads((R/'icca/data/critique.json').read_text())['34554208']['bottom_line']]
save('tools/compact_evidence_source.json',src,'Reconciled sources: corrected XXL published estimate, observational ImmunoXXL, ctDNA attribution and refreshed exact source passages')
manifest.write_text(json.dumps(dict(id='2026-11-02-zzzz-evidence',files=changes),ensure_ascii=False,indent=2)+'\n')
