"""Presentation index of existing reviewed comparisons; no new outcome estimates.

The 40 detailed records and older comparative trials already cited by the matrix
are shown once per tumour. Single-arm series are not comparative rows.
"""
from pathlib import Path
import json

R=Path(__file__).resolve().parents[1]
load=lambda name:json.loads((R/name).read_text())
matrix=load('lrt/matrix.json');full=load('tools/lrt_comparative_evidence.json')['studies'];compact=load('tools/compact_evidence_source.json')['studies']
refs={r['pmid']:r for r in matrix['refs']}
settings={'local':'Definitive local treatment','transplant':'Bridge / downstaging / transplant','control':'Unresectable disease / disease control','combined':'Combined treatment / conversion','perioperative':'Before or after surgery','technique':'Technique / dose / toxicity','symptoms':'Symptom relief'}
group={'Definitive local treatment':'local','Bridge to transplantation':'transplant','Downstaging':'transplant','Radiation options':'control','Arterial treatment':'control','Ablation with regional chemotherapy':'combined','Conversion and combined treatment':'combined','Advanced disease':'control','Unresectable disease':'control','Regional combination treatment':'combined','Conversion treatment':'combined','After complete local clearance':'perioperative','Multifocal disease':'control','Nontransplant disease control':'control','Arterial disease control':'control','Delayed hepatic toxicity':'technique'}

# Labels identify the actual arms; a combination is never relabelled monotherapy.
comparisons={
'33230652':'Y90 segmentectomy vs MWA','42434250':'Y90 segmentectomy vs MWA','27930089':'Y90 segmentectomy vs TACE + MWA','36100064':'Y90 vs DEB-TACE + ablation','42379392':'Y90 segmentectomy vs TACE + MWA','35346857':'Y90 segmentectomy vs resection','19552767':'Y90 vs TACE','34358718':'Y90 or ablation vs TACE','41056563':'Y90 vs TACE','41580092':'Y90 vs TACE','39808828':'Y90 vs TACE','28668402':'Y90 vs TACE','35619164':'Y90 vs TACE','28799575':'SBRT / TACE / RFA / Y90','27284477':'Y90 vs external-beam radiation','25443863':'Y90 vs TACE','25373796':'Y90 vs DEB-TACE','33687130':'HAIC + RFA vs RFA','35993224':'HAIC → ablation vs HAIC','29631810':'HAIC + sorafenib vs sorafenib','40709764':'Pump HAI vs Y90','29181682':'Pump HAI vs Y90','11843249':'Y90 + arterial FUDR vs arterial FUDR','31177151':'DEB-TACE vs Y90','41118066':'HAI + systemic vs systemic','39644535':'HAI + systemic vs systemic','42018958':'Arterial vs IV oxaliplatin','42829779':'MWA vs SBRT','33868997':'HAIC vs TACE','40216615':'HAIC vs cTACE / DEB-TACE','35544131':'Pump HAI vs resection','37814188':'Pump HAI ± systemic vs GemCis','30191056':'Y90 vs chemoembolization','31517072':'SBRT / chemoradiation / Y90','42433279':'Drainage + HAIC vs drainage + supportive care','29167951':'Y90 vs bland embolization','32032719':'Y90 vs TACE','28677067':'cTACE / DEB-TACE / Y90','33004146':'TACE vs Y90: delayed toxicity','42006283':'Y90 vs bland embolization'}

# Explicit selection of older comparative evidence, with its clinical setting.
# Result and limitation strings come from the current published sources unchanged.
older={
'hcc':[
('35949295','local','Resection vs RFA',['surgery','abl']),('40554738','local','Resection vs RFA',['surgery','abl']),('16495695','local','Ablation vs resection',['abl','surgery']),('29091283','local','Resection vs RFA',['surgery','abl']),('29503247','local','MWA vs RFA',['abl']),('31774468','local','Repeat resection vs RFA',['surgery','abl']),('23269991','combined','TACE + RFA vs RFA',['tace','abl']),('28257902','transplant','SBRT / TACE / RFA',['sbrt','tace','abl']),('39693584','local','SBRT vs RFA',['sbrt','abl']),('26628466','local','SBRT vs RFA',['sbrt','abl']),('31283409','perioperative','RT → resection vs resection',['sbrt','surgery']),('38488934','perioperative','Postoperative RT vs TACE',['sbrt','tace']),('36421345','control','SBRT vs repeat embolization',['sbrt','tace']),('37037359','control','SBRT vs DEB-TACE',['sbrt','tace']),('39699905','combined','SBRT + sorafenib vs sorafenib',['sbrt','systemic']),('29543938','combined','TACE + EBRT vs sorafenib',['tace','sbrt','systemic']),('39245060','symptoms','RT vs supportive care',['sbrt','supportive']),('27575820','control','Y90 vs cTACE',['y90','tace']),('35258371','control','Y90 vs DEB-TACE',['y90','tace']),('34331914','transplant','Y90 vs TACE',['y90','tace']),('29107679','control','Y90 vs sorafenib',['y90','systemic']),('29498924','control','Y90 vs sorafenib',['y90','systemic']),('31421157','combined','Y90 + sorafenib vs sorafenib',['y90','systemic']),('33166497','technique','Personalized vs standard Y90 dosimetry',['y90']),('37328589','perioperative','Embolization → resection vs emergency resection',['tace','surgery']),('29420221','perioperative','Adjuvant TACE vs observation',['tace','surgery']),('32615109','transplant','LT vs non-transplant care after downstaging',['surgery']),('12049862','control','TAE / TACE / supportive care',['tace','supportive']),('11981766','control','TACE vs supportive care',['tace','supportive']),('39798579','combined','TACE + durvalumab / bevacizumab vs TACE',['tace','systemic']),('39798578','combined','TACE + lenvatinib / pembrolizumab vs TACE',['tace','systemic']),('34905388','control','HAIC-FOLFOX vs sorafenib',['hai','systemic']),('31070690','combined','HAIC + sorafenib vs sorafenib',['hai','systemic']),('34648352','control','HAIC-FOLFOX vs cTACE',['hai','tace']),('36525610','perioperative','Adjuvant HAIC vs observation',['hai','surgery'])],
'icca':[('38261915','local','MWA vs resection',['abl','surgery']),('41528222','local','MWA vs repeat resection',['abl','surgery']),('26503201','technique','Higher vs lower radiation dose',['sbrt']),('26695839','control','HAI + systemic vs systemic',['hai','systemic'])],
'pcca':[('39936132','transplant','GemCis-only vs RT-containing neoadjuvant therapy',['sbrt','systemic']),('37032423','transplant','Neoadjuvant chemoradiation vs none before LT',['sbrt','surgery']),('39311927','technique','Radioactive vs conventional stents; both with HAIC',['hai'])],
'crlm':[('39848272','local','Thermal ablation vs resection',['abl','surgery']),('28376151','combined','RFA ± resection + systemic vs systemic',['abl','surgery','systemic']),('30982687','local','SABR + standard care vs standard care',['sbrt']),('32484754','local','SABR + standard care vs standard care',['sbrt']),('34541864','combined','Y90 + second-line systemic vs systemic',['y90','systemic']),('20567019','combined','Y90 + fluorouracil vs fluorouracil',['y90','systemic']),('28781171','combined','Y90 + FOLFOX vs FOLFOX',['y90','systemic']),('22493375','control','DEBIRI vs FOLFIRI',['tace','systemic']),('10615075','perioperative','HAI + systemic vs systemic',['hai','systemic']),('28426374','perioperative','Perioperative HAI vs no HAI',['hai','surgery']),('16505413','control','HAI vs systemic fluorouracil / leucovorin',['hai','systemic'])],
'nelm':[('16134179','control','Bland vs chemoembolization',['tace'])]}

occurrences={}
for key,cell in matrix['cells'].items():
 tumor=key.split('|')[0]
 for role in cell['roles']:
  if role.get('comparative'):continue
  for ev in role['ev']:
   occurrences.setdefault((tumor,ev[1]),[]).append((role,ev))

def citation(pid):
 r=refs.get(pid,{})
 return {'pmid':pid,'year':str(r.get('y','')),'journal':r.get('j',''),'author':r.get('au',''),'doi':r.get('doi',''),'pubmed':f'https://pubmed.ncbi.nlm.nih.gov/{pid}/','tmc':f'https://libkey.io/libraries/480/pmid/{pid}'}
rows=[]
for r in full:
 pid=r['pmid'];c=compact[pid]
 row={'id':r['tumor']+'-'+pid,'tumor':r['tumor'],'setting':group[r['setting']],'comparison':comparisons[pid],
 'treatments':r['modalities'],'label':c['label'],'design':r['design'],'population':r['population'],'result':r['result'],'caution':r['caution'],
 'summary':c['result'],'shortCaution':c['caution'],'origin':'comparative-record',**citation(pid)}
 extras={'35346857':['surgery'],'29631810':['systemic'],'41118066':['systemic'],'39644535':['systemic'],'42018958':['systemic'],'35544131':['surgery'],'37814188':['systemic'],'42433279':['supportive']}
 row['treatments']=list(dict.fromkeys(row['treatments']+extras.get(pid,[])))
 if pid=='42018958':row['treatments']=['hai','systemic']
 rows.append(row)

# Keep the primary matrix wording where a compact source gives a different
# analysis or an over-broad interpretation. This is a layout-only release.
matrix_result={'26628466','31283409','34331914','39311927'}
for tumor,items in older.items():
 for pid,setting,label,treatments in items:
  assert (tumor,pid) in occurrences,(tumor,pid)
  role,ev=occurrences[(tumor,pid)][0]
  c=compact.get(pid)
  if not c:
   assert pid=='39311927'
   c={'design':'Randomized trial','arms':role['when'],'result':ev[2],'caution':role['when']}
  result=ev[2] if pid in matrix_result else c['result']
  rows.append({'id':tumor+'-'+pid,'tumor':tumor,'setting':setting,'comparison':label,'treatments':treatments,'label':ev[0],
   'design':c['design'],'population':c['arms'],'result':result,'summary':result,'caution':c['caution'],'shortCaution':c['caution'],
   'origin':'matrix' if pid in matrix_result else 'compact-evidence',**citation(pid)})

# Conference results retain their explicit publication-status limitations.
for tumor,name,setting,label,treatments,doi in [
 ('pcca','ABC-07 randomized phase II','control','GemCis → SBRT vs continued GemCis',['sbrt','systemic'],'10.1200/JCO.2024.42.16_suppl.4006'),
 ('crlm','Dutch PUMP, ASCO 2026 LBA3506','perioperative','Adjuvant pump HAI vs no pump HAI',['hai','surgery'],'10.1200/JCO.2026.44.17_suppl.LBA3506'),
 ('nelm','RETNET RCT','control','Bland embolization vs cTACE',['tace'],'')]:
 candidates=[(role,ev) for (t,p),items in occurrences.items() if t==tumor for role,ev in items if ev[0]==name]
 assert candidates,name
 role,ev=candidates[0];pid=ev[1]
 rows.append({'id':tumor+'-'+('abstract-'+name.split(',')[0].replace(' ','-')),'tumor':tumor,'setting':setting,'comparison':label,'treatments':treatments,
  'label':name,'design':'Conference results','population':role['when'],'result':ev[2],'summary':ev[2],
  'caution':'Conference abstract; interpret within the reported trial population.' if not pid else 'Results are from the conference abstract. The PMID opens the trial protocol, not the results.',
  'shortCaution':'Conference results; primary report status is shown with the source.','origin':'matrix-conference','pmid':pid,'doi':doi,
  'year':'2025' if tumor=='nelm' else ('2024' if tumor=='pcca' else '2026'),'journal':'Conference abstract','author':'',
  'pubmed':f'https://pubmed.ncbi.nlm.nih.gov/{pid}/' if pid else '',
  'tmc':f'https://libkey.io/libraries/480/pmid/{pid}' if pid else 'https://thslc-houston.primo.exlibrisgroup.com/discovery/search?vid=01TEXASHEALTH_HOUSTON%3ATMC_INST&query=any,contains,'+doi})

assert len({r['id'] for r in rows})==len(rows)
order={k:i for i,k in enumerate(settings)}
rows.sort(key=lambda r:(r['tumor'],order[r['setting']],r['comparison'],r['year'],r['id']))
out={'version':'20261104-compare1','settings':settings,'treatments':dict((m[0],m[1]) for m in matrix['modalities'])|{'surgery':'Resection / transplant','systemic':'Systemic therapy','supportive':'Supportive care'},'rows':rows}
(R/'lrt/comparisons.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
print('Built comparison tables:',{t:sum(r['tumor']==t for r in rows) for t,_,_ in matrix['tumours']})
