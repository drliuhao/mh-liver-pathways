"""Normalize reconciled V7 proposals for the standard pathway renderer.

Only bibliographic metadata, authored summaries and access URLs are exported.
Article PDFs and local depot paths are never copied into the public site.
"""
from pathlib import Path
from urllib.parse import quote
import argparse, hashlib, json, shutil
from build_high_risk import GROUPS, TITLES, LABELS, plain

ROOT=Path(__file__).resolve().parents[1]
STEPS={
 'HCC-B1':['allocation','treatment'], 'HCC-B2':['curative-route'],
 'HCC-B3':['treatment','waitlist'], 'HCC-B4':['listing'],
 'pCCA-B1':['diagnosis','phenotype','staging'], 'pCCA-B2':['phenotype'], 'pCCA-B3':['neoadjuvant'],
 'iCCA-B1':['diagnosis','phenotype'], 'iCCA-B2':['therapy','stability'], 'iCCA-B3':['review'],
 'CRLM-B1':['unresectability'], 'CRLM-B2':['control','restaging'],
 'CRLM-B3':['biology','clocks'], 'CRLM-B4':['review'],
 'NET-B1':['options'], 'NET-B2':['biology','distribution','observation'], 'NET-B3':['review'],
 'HEHE-B1':['risk'], 'HEHE-B2':['stage'], 'HCA-B1':['exception-route'], 'HCA-B2':['standard-care'],
}
CONTEXT={
 'HCC-B1':'Consider this review when the original tumor burden exceeded UNOS downstaging entry criteria.',
 'HCC-B2':'A history of tumor invasion into the portal vein requires a separate assessment, even after a radiographic response.',
 'HCC-B3':'Review checkpoint-inhibitor exposure before treatment selection and again before transplantation.',
 'HCC-B4':'Prediction models may inform research; they do not currently determine access to a graft in this proposal.',
 'pCCA-B1':'Review exact radial size, the route of any primary-tumor biopsy, and the full nodal history. These proposed expansions remain closed.',
 'pCCA-B2':'If complete resection may be feasible, compare it with the transplant strategy before entering a transplant study.',
 'pCCA-B3':'Alternative neoadjuvant regimens require their own approval and cannot be substituted into the standard protocol automatically.',
 'iCCA-B1':'Confirm the actual lesion distribution and tumor grade before considering the proposed advanced-disease study.',
 'iCCA-B2':'Use the full treatment and progression history to decide whether further observation or another treatment is needed.',
 'iCCA-B3':'A potential living donor does not by itself establish recipient eligibility or make a proposed study ready to open.',
 'CRLM-B1':'Confirm persistent unresectability after reviewing all realistic approaches to complete tumor clearance.',
 'CRLM-B2':'No visible tumor after treatment is a reason to reassess the indication; presumed microscopic disease alone does not justify transplantation.',
 'CRLM-B3':'Review molecular markers, CEA, primary-tumor clearance, and any previous disease outside the liver.',
 'CRLM-B4':'Compare expected benefit with continued nontransplant treatment and discuss recurrence and future graft use.',
 'NET-B1':'Establish what additional benefit transplantation offers over available treatment or surveillance.',
 'NET-B2':'Confirm differentiation, primary site, prior spread and the duration of disease control.',
 'NET-B3':'Age and liver replacement require individual benefit assessment; proposed expanded groups remain unactivated.',
 'HEHE-B1':'Balance observation of disease behavior against liver failure or other reasons transplantation cannot safely wait.',
 'HEHE-B2':'Assess vascular invasion and any extrahepatic disease separately from the usual liver-only pathway.',
 'HCA-B1':'Review which NLRB recommendation applies, while separately establishing a clinical indication for transplantation.',
 'HCA-B2':'Use transplantation only when standard treatment is not feasible and a clear clinical benefit is established.',
}

def cleaned(v):
 if isinstance(v,str):return plain(v).replace('OPEN Analyst A position: ','').replace('OPEN — Analyst A proposal, not institutional approval','Proposed — institutional approval pending')
 if isinstance(v,list):return [cleaned(x) for x in v]
 if isinstance(v,dict):return {k:cleaned(x) for k,x in v.items()}
 return v

def make_review(d,ev):
 k=d['id']
 keys=list(dict.fromkeys([x['key'] for x in d.get('evidence',[])]+d.get('supporting_refs',[])+[x['key'] for x in ev.get('studies',[]) if x.get('key')]))
 result={'id':k,'anchor':k.lower(),'title':TITLES[k],'status':LABELS.get(k,'Proposed operating requirement'),
  'steps':STEPS.get(k,[]),'context':CONTEXT.get(k,''),'stance':d['stance'],'rules':d['rules'],
  'tests':d['tests'],'allocation':d['allocation'],'references':keys,
  'evidence':{f:ev[f] for f in ['synthesis','counterevidence','certainty','threshold_basis','policy_context','studies'] if f in ev}}
 return cleaned(result)

def build(src,access,output):
 d=json.loads((src/'source/decision_records.json').read_text());v=json.loads((src/'source/evidence_reviews_combined.json').read_text());s=json.loads((src/'source/all_sources_used.json').read_text())
 links=json.loads(access.read_text());used=set();pathways={};docs=[]
 for group,slug,name,doc in GROUPS:
  reviews=[make_review(x,v[x['id']]) for x in d.values() if x['group']==group]
  files=[]
  for ext in ['pdf','docx']:
   name_doc=Path(doc).with_suffix('.'+ext).name
   source=next(src.rglob(name_doc));target=ROOT/'transplant/high-risk/docs'/name_doc
   target.parent.mkdir(exist_ok=True,parents=True);shutil.copyfile(source,target)
   info={'url':'/high-risk/docs/'+name_doc,'label':f'V7 high-risk {"boundary addendum" if slug in ["hehe","hca"] else "protocol"} · {ext.upper()}','format':ext,'sha256':hashlib.sha256(target.read_bytes()).hexdigest()}
   files.append(info);docs.append({'path':str(target.relative_to(ROOT)), 'sha256':info['sha256'],'kind':'Author-created protocol; not a journal article'})
  pathways[slug]={'name':name,'reviews':reviews,'documents':files}
  for r in reviews:used.update(r['references'])
 readiness=[make_review(x,v[x['id']]) for x in d.values() if x['group']=='ALLOC']
 for r in readiness:used.update(r['references'])
 sources={}
 for key in sorted(used):
  r=s[key];a=links.get(key,{});authors=r.get('authors') or a.get('authors') or []
  author=authors[0].split(',')[0] if authors else ''
  doi=r.get('doi','');pdfs=[]
  for link in sorted(a.get('links',[]),key=lambda x:('pmc.ncbi.nlm.nih.gov' not in x['url'], 'access may' in x['label'])):
   if link['url'] not in [x['url'] for x in pdfs]:pdfs.append({k:link[k] for k in ['url','label','method']})
  sources[key]={'key':key,'short':r.get('short') or r['title'],'title':r['title'],'author':author,
   'journal':r.get('journal') or a.get('journal',''),'year':r.get('year') or a.get('year',''),
   'pmid':r.get('pmid') or a.get('pmid',''),'doi':doi,'url':a.get('pmc_url') or r.get('primary_url') or r['url'],
   'pdf_links':pdfs[:2], 'tmc':('https://thslc-houston.primo.exlibrisgroup.com/discovery/search?vid=01TEXASHEALTH_HOUSTON%3ATMC_INST&query=any,contains,'+quote(doi,safe='')+'&lang=en') if doi else '',
   'review_depth':r.get('review_depth') or r.get('access','')}
 payload={'version':'2026-10-24-integrated-v7','review_date':'2026-10-24','pathways':pathways,'readiness':readiness,'sources':sources,
  'status':'Proposed high-risk protocols; not activated. Standard selection and allocation rules are unchanged.'}
 text=json.dumps(payload,ensure_ascii=False,indent=2)+'\n'
 assert '/Users/' not in text and 'file://' not in text and 'PDAC-' not in text
 output.parent.mkdir(exist_ok=True,parents=True);output.write_text(text)
 public=json.loads(text)
 for entry in public['pathways'].values():
  for doc in entry['documents']:doc['url']='/mh-liver-pathways/transplant'+doc['url']
 (ROOT/'transplant/high-risk/integrated-protocols.json').write_text(json.dumps(public,ensure_ascii=False,indent=2)+'\n')
 (ROOT/'transplant/high-risk/authored-documents.json').write_text(json.dumps(docs,indent=2)+'\n')
 print(f'Integrated {sum(len(x["reviews"]) for x in pathways.values())} reviews across {len(pathways)} protocols; {len(sources)} sources; {sum(bool(x["pdf_links"]) for x in sources.values())} sources with direct PDF links; seven authored protocol PDFs.')

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('source',type=Path);p.add_argument('access',type=Path);p.add_argument('output',type=Path);a=p.parse_args();build(a.source,a.access,a.output)
