"""Publish the reconciled V7 review material without activating a clinical protocol."""
from pathlib import Path
from html import escape as esc
from urllib.parse import quote
import argparse,json,shutil

ROOT=Path(__file__).resolve().parents[1]
BASE='/mh-liver-pathways'
OUT=ROOT/'transplant/high-risk'
GROUPS=[('HCC','hcc','Hepatocellular carcinoma','01_HCC_High_Risk_Protocol_v7.docx'),
 ('pCCA','pcca','Perihilar cholangiocarcinoma','02_PCCA_High_Risk_Protocol_v7.docx'),
 ('iCCA','icca','Intrahepatic cholangiocarcinoma','03_ICCA_High_Risk_Protocol_v7.docx'),
 ('CRLM','crlm','Colorectal liver metastases','04_CRLM_High_Risk_Protocol_v7.docx'),
 ('NET','nelm','Neuroendocrine liver metastases','05_NELM_High_Risk_Protocol_v7.docx'),
 ('HEHE','hehe','Hepatic epithelioid hemangioendothelioma','06_HEHE_Clinical_Protocol_Boundary_Addendum_v7.docx'),
 ('HCA','hca','Hepatocellular adenoma','07_HCA_Clinical_Protocol_Boundary_Addendum_v7.docx')]
TITLES={
 'HCC-B1':'Tumor burden beyond UNOS downstaging criteria',
 'HCC-B2':'Previously treated portal-vein tumor invasion',
 'HCC-B3':'Previous checkpoint immunotherapy',
 'HCC-B4':'Survival-benefit prediction: research use only',
 'pCCA-B1':'Tumor size, biopsy history or previously malignant nodes',
 'pCCA-B2':'Resection remains a potentially curative option',
 'pCCA-B3':'Alternative treatment before transplantation',
 'iCCA-B1':'Advanced disease: tumor distribution and grade',
 'iCCA-B2':'Response, progression and the observation period',
 'iCCA-B3':'Living-donor transplantation: study readiness',
 'CRLM-B1':'Confirm that complete resection is not feasible',
 'CRLM-B2':'No tumor is visible after treatment',
 'CRLM-B3':'Molecular findings and previous extrahepatic disease',
 'CRLM-B4':'Expected benefit, recurrence and graft use',
 'NET-B1':'Does transplantation offer enough additional benefit?',
 'NET-B2':'Primary site, grade, spread and disease control',
 'NET-B3':'Age and liver tumor burden',
 'HEHE-B1':'Observation and the need for transplantation',
 'HEHE-B2':'Extrahepatic disease and vascular invasion',
 'HCA-B1':'Which NLRB recommendation applies?',
 'HCA-B2':'Is transplantation clinically justified?',
 'ALLOC-B1':'Separate clinical, allocation, donor and study approval',
 'ALLOC-B2':'Assess expected recipient benefit and organ use',
 'ALLOC-B3':'Protect the living donor',
 'ALLOC-B4':'Monitor all patients considered for the study',
}
LABELS={
 'HCC-B1':'Proposed study cohort', 'HCC-B2':'Proposed study cohort',
 'HCC-B3':'Proposed safety approach', 'HCC-B4':'Research use only',
 'pCCA-B1':'Expansion remains closed', 'pCCA-B2':'Resection assessment', 'pCCA-B3':'Separate proposals; not activated',
 'iCCA-B1':'Proposed study cohort', 'iCCA-B2':'Proposed response requirements','iCCA-B3':'Study development only',
 'CRLM-B1':'Confirm the treatment options','CRLM-B2':'No transplant for presumed microscopic disease','CRLM-B3':'Initial expansion limits','CRLM-B4':'Benefit and graft-use review',
 'NET-B1':'Benefit review','NET-B2':'Initial selection limits','NET-B3':'Individual review; expansion not activated',
 'HEHE-B1':'Clinical boundary review','HEHE-B2':'Clinical boundary review','HCA-B1':'Allocation and clinical review','HCA-B2':'Clinical benefit review',
}
def plain(text):
 text=str(text)
 for old,new in [('clinical timing gate','clinical timing requirement'),('six-domain readiness gate','assessment of the six readiness domains'),('Proposed readiness gate:','Proposed readiness requirements:'),('Proposed LT gate:','Proposed transplant requirements:'),('Proposed activation gate:','Before considering transplantation:'),('Proposed CEA gate:','Proposed CEA requirement:'),('Proposed gate:','Proposed requirements:'),('Activation cutoff:','Before this study can open:'),('immune-toxicity gate','assessment of immune toxicity'),('No initial stacking with the PVTT arm.','Do not combine this expansion with the portal-vein tumor invasion study.'),('Do not stack these adverse strata.','Do not combine these excluded categories in one expansion cohort.'),('shadow mode','research-only evaluation'),('LT activation','a final decision to proceed with transplantation')]:text=text.replace(old,new)
 return text
def bullets(items):return '<ul>'+''.join('<li>'+esc(plain(x))+'</li>' for x in items)+'</ul>'
def paragraph(text):return '<p>'+esc(plain(text))+'</p>'
def tmc(r):return 'https://thslc-houston.primo.exlibrisgroup.com/discovery/search?vid=01TEXASHEALTH_HOUSTON%3ATMC_INST&query=any,contains,'+quote(r.get('doi') or r['title'],safe='')+'&lang=en'
def source_link(key,sources):
 access=json.loads((OUT/'integrated-protocols.json').read_text())['sources'].get(key,{}) if (OUT/'integrated-protocols.json').exists() else {}
 pdfs=''.join(f'<a class="download" href="{esc(x["url"])}">{esc(x["label"])}</a> ' for x in access.get('pdf_links',[]))
 r=sources[key];author=(r.get('authors') or [''])[0].split(',')[0]
 citation=' · '.join(str(x) for x in [author,r.get('journal'),r.get('year')] if x)
 pm=r.get('pmid','');doi=r.get('doi','');url=r.get('primary_url') or r['url']
 return f'<li><a href="{esc(url)}" target="_blank" rel="noopener">{esc(r.get("short") or r["title"])}</a><span class="citation">{esc(citation)}</span><span class="source-access">'+(f'PMID <a href="https://pubmed.ncbi.nlm.nih.gov/{pm}/">{pm}</a> · ' if pm else '')+(f'DOI <a href="https://doi.org/{esc(doi)}">{esc(doi)}</a> · <a href="{esc(tmc(r))}">TMC Library</a>' if doi else '')+f'</span>{pdfs}<small>{esc(r.get("review_depth") or r.get("access",""))}</small></li>'
def page(title,body):
 return f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="robots" content="noindex"><title>{esc(title)} | Memorial Hermann HPB Oncology</title><link rel="stylesheet" href="{BASE}/assets/evidence-tools.css?v=20261024-integrated-high-risk"><link rel="stylesheet" href="{BASE}/assets/portal-navigation.css"><script src="{BASE}/assets/portal-navigation.js?v=20261029-tools2" defer></script></head><body><main class="evidence-wrap">{body}<footer class="evidence-footer">V7 source review · 24 October 2026 · Proposals remain open for multidisciplinary and institutional review. Analyst A synthesis; no institutional approval or external-analyst consensus is implied.</footer></main></body></html>'''
def render_decision(d,e,sources,slug):
 k=d['id'];status=LABELS.get(k,'Proposed operating requirement')
 # Keep source rules verbatim; do not turn a proposal into an active recommendation.
 rule_html=bullets(d['rules'])
 study_html=''
 for s in e.get('studies',[]):
  key=s.get('key');r=sources.get(key,{})
  title=r.get('short') or r.get('title') or key or 'Supporting study'
  rows=''.join(f'<p><strong>{label}.</strong> {esc(str(s[field]))}</p>' for field,label in [('design_population','Design and population'),('selection','Selection'),('results','Results'),('limits','Limits'),('limitations','Limits')] if s.get(field))
  study_html+=f'<article class="study"><h4>{esc(title)}</h4>{rows}</article>'
 keys=list(dict.fromkeys([x['key'] for x in d.get('evidence',[])]+d.get('supporting_refs',[])+[x['key'] for x in e.get('studies',[]) if x.get('key')]))
 refs='<ul class="sources">'+''.join(source_link(x,sources) for x in keys if x in sources)+'</ul>'
 summaries=''
 for field,label in [('synthesis','Evidence summary'),('counterevidence','Evidence against expansion'),('certainty','Certainty'),('threshold_basis','Basis for proposed thresholds')]:
  if e.get(field):summaries+=f'<h4>{label}</h4>'+(bullets(e[field]) if isinstance(e[field],list) else paragraph(e[field]))
 clinical_route=f'{BASE}/transplant/{slug}/' if slug else f'{BASE}/transplant/'
 next_step=('These findings do not open a transplant route under this proposal. Review the standard criteria, clarify any uncertain finding, and select another cancer treatment when transplantation remains unsuitable.' if k in ['pCCA-B1','CRLM-B2'] else 'Bring the findings and source comparison to the transplant multidisciplinary team. A proposed study route requires its own approval; continue appropriate cancer treatment and reassess while that decision is pending.')
 if slug=='hca':next_step='Review the remaining nontransplant options with the liver team and establish whether transplantation offers a clear clinical benefit. If that benefit is not established, agree treatment or surveillance through the standard adenoma pathway.'
 treatment_links=(f'<a href="{BASE}/systemic/?tumor={slug}">Systemic treatment options</a><a href="{BASE}/lrt/">Liver-directed treatment options</a>' if slug in ['hcc','pcca','icca','crlm','nelm'] else (f'<a href="{clinical_route}#care-treatment">Treatment and continuing care</a>' if slug else ''))
 return f'''<section class="review-decision" id="{k.lower()}"><div class="section-top"><span class="eyebrow">{esc(k)}</span><span class="badge">High-risk protocol · {esc(status)}</span></div><h2>{esc(TITLES[k])}</h2><p class="proposed-label">Proposed position for discussion — not an activated protocol</p>{rule_html}<details><summary>Tests and information to review</summary>{paragraph(d['tests'])}</details><div class="allocation-note"><h3>Allocation and donor route</h3>{paragraph(d['allocation'])}</div><details><summary>Evidence, limitations and supporting papers</summary>{summaries}{study_html}{refs}</details><div class="next-step"><h3>Next step</h3>{paragraph(next_step)}<div class="button-row"><a href="{clinical_route}">Standard transplant pathway</a>{treatment_links}<a href="{BASE}/transplant/high-risk/#readiness">Approval requirements</a></div></div></section>'''

def build(src):
 decisions=json.loads((src/'source/decision_records.json').read_text());reviews=json.loads((src/'source/evidence_reviews_combined.json').read_text());sources=json.loads((src/'source/all_sources_used.json').read_text())
 OUT.mkdir(parents=True,exist_ok=True);(OUT/'docs').mkdir(exist_ok=True)
 cards=[];published=[];used=set()
 for group,slug,name,doc in GROUPS:
  ds=[d for d in decisions.values() if d['group']==group]
  title=f'{name}: '+('clinical boundary review' if group in ('HEHE','HCA') else 'high-risk transplant review')
  nav='<nav class="tool-tabs" aria-label="Review questions">'+''.join(f'<a href="#{d["id"].lower()}">{i+1}. {esc(TITLES[d["id"]])}</a>' for i,d in enumerate(ds))+'</nav>'
  source_file=next(src.rglob(doc));shutil.copyfile(source_file,OUT/'docs'/doc)
  body=f'<a class="back" href="../">← All high-risk and boundary reviews</a><header class="tool-hero"><p class="eyebrow">Transplant oncology · V7</p><h1>{esc(title)}</h1><p>Use this review when a finding falls outside the standard pathway or needs a separate assessment of benefit, safety or study eligibility.</p></header><div class="review-notice"><strong>Discussion material. These proposals have not been activated.</strong> A link from the standard pathway invites review; it does not establish transplant eligibility, MELD-exception approval or permission to enroll. Some expansions remain closed.</div>{nav}'
  if slug=='icca':
   body+='<aside class="definition"><h2>Describe the distribution before considering an expanded route</h2><dl><dt>One mass with adjacent satellite nodules</dt><dd>A dominant mass with nearby peritumoral nodules. Record their relationship and exact distribution; nearby nodules may still represent spread within the liver.</dd><dt>Multifocal disease</dt><dd>Separate tumor foci, including lesions in other liver segments. This describes the imaging pattern; it does not prove whether they arose independently.</dd><dt>Intrahepatic metastases</dt><dd>Spread from the primary tumor to other locations in the liver. This is a biological interpretation, supported by the full imaging, pathology and clinical picture, rather than a synonym for every additional nodule.</dd></dl><p>The initial advanced-disease proposal permits a single mass-forming focus with adjacent peritumoral satellites; it excludes separate multifocal tumors in different segments. This is a proposed study boundary, not a validated universal transplant rule. Preserve the actual lesion map and uncertainty.</p></aside>'
  body=f'<div class="review-notice"><strong>Now integrated into the standard protocol.</strong> <a href="{BASE}/transplant/{slug}/#high-risk">Open the orange-labeled high-risk protocols, evidence and PDFs →</a></div>'+body
  body+=''.join(render_decision(d,reviews[d['id']],sources,slug) for d in ds)
  body+=f'<p><a class="download" href="../docs/{Path(doc).with_suffix(".pdf").name}">Full V7 protocol PDF</a></p>'
  body+=f'<p><a class="download" href="../docs/{doc}">Download the V7 discussion document (.docx)</a></p>'
  (OUT/slug).mkdir(exist_ok=True);(OUT/slug/'index.html').write_text(page(title,body).replace('</head>',f'<script>location.replace("{BASE}/transplant/{slug}/#high-risk"+(location.hash?"-"+location.hash.slice(1):""));</script></head>'))
  label='High-risk boundary review' if group in ('HEHE','HCA') else 'High-risk protocol'
  summary=' · '.join(TITLES[d['id']] for d in ds)
  cards.append(f'<a class="review-card" href="{BASE}/transplant/{slug}/#high-risk"><span class="eyebrow">{esc(group if group!="NET" else "NELM")} · {label}</span><h2>{esc(name)}</h2><p>{esc(summary)}</p><span>Open {len(ds)} integrated reviews →</span></a>')
  published.extend(d['id'] for d in ds)
  for d in ds:
   used.update(d.get('supporting_refs',[]));used.update(x['key'] for x in d.get('evidence',[]));used.update(x['key'] for x in reviews[d['id']].get('studies',[]) if x.get('key'))
 governance=''.join(render_decision(d,reviews[d['id']],sources,None) for d in decisions.values() if d['group']=='ALLOC')
 body='<header class="tool-hero"><p class="eyebrow">Transplant oncology · beyond the standard pathway</p><h1>High-risk protocols</h1><p>These reviews are integrated into the standard disease pathways. Choose a tumor below to see orange-labeled protocols at the relevant decision, with proposed criteria, study results and full-text PDF access.</p></header><div class="review-notice"><strong>Referral for review is not approval for transplantation.</strong> All V7 proposals remain open. Standard allocation rules still apply, living-donor access does not remove selection requirements, and several expansions remain closed.</div><ol class="journey-strip"><li><b>1</b> Identify the unmet standard criterion</li><li><b>2</b> Review disease-specific limits</li><li><b>3</b> Assess benefit and donor route</li><li><b>4</b> Obtain required approvals or select other care</li></ol><div class="review-grid">'+''.join(cards)+'</div><section id="readiness"><h2>Before any proposed study can open</h2><p>Clinical selection, allocation review, donor protection and research approval are separate decisions. These shared requirements must be resolved before a proposed cohort is activated.</p>'+governance+'</section>'
 (OUT/'index.html').write_text(page('High-risk transplant review',body))
 (OUT/'publication-manifest.json').write_text(json.dumps({'source':'V7_high_risk_evidence_review_2026-10-24','review_date':'2026-10-24','high_risk_pathways':5,'boundary_addenda':2,'disease_questions':published,'shared_readiness_questions':4,'activation_status':'All proposals remain OPEN; publication is not institutional approval.','licensed_pdfs_published':0,'authored_protocol_pdfs':7,'integrated_into_standard_pathways':True,'selection_rules_changed':False},indent=2))
 print(f'Published {len(GROUPS)} review pages, {len(published)} disease questions and four shared readiness questions.')

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('source',type=Path);build(p.parse_args().source)
