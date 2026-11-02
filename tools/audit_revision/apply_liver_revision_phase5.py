from pathlib import Path
exec((Path(__file__).with_name('apply_liver_revision.py')).read_text().split('# HCC: stage')[0])
def cfield(slug,pm,path,new,finding,source):
 old=get(json.loads(texts[f'{slug}/data/critique.json'])[pm],path);replace(old,new,finding,source,slug)
src=B+'B14_crlm_roadmap/reviews/R12/R12_REPORT.md F02/F04; Hill37210451 PDF2–3/Table1; ASCO/ESMO peritoneal recommendations'
replace('Of seven patients transplanted after HAI, five were for biliary complications and two for residual tumour, and dissection and arterial reconstruction were difficult; this supports early technical planning, not a validated HAI-to-transplant schedule.','Seven patients with mixed diagnoses underwent LT after HAI; only three had CRLM, two for cholangiopathy and one for residual tumour. Difficult dissection and arterial reconstruction support early technical planning, not an established CRLM HAI-to-LT schedule.','B14-R12-F02',src,'crlm')
replace('limited peritoneal disease belongs to expert CRS/HIPEC centres.','limited peritoneal disease requires specialist peritoneal-surface review. Combined liver/peritoneal clearance is an individualized OPEN proposal; routine oxaliplatin HIPEC is not recommended.','B14-R12-F04',src,'crlm')
replace('Peritoneum: limited peritoneal disease with liver metastases only in a peritoneal-surface-malignancy centre (CRS/HIPEC plus limited liver resection).','Peritoneum: discuss limited peritoneal plus liver disease with a specialist peritoneal-surface team after systemic assessment. Combined complete clearance is case-specific and remains an OPEN proposal; do not prescribe routine oxaliplatin HIPEC. Peritoneal-only cytoreduction guidance does not directly establish benefit in combined disease.','B14-R12-F04',src,'crlm')

src=A+'metastatic_benign/Source_Reviews/36924180.md; ENETS2023 PDF7–8/Table2; MB048'
replace('Almost every therapeutic recommendation in that paper is 4B or weaker and no randomised trial underpins either first- or second-line therapy.','ENETS cites randomized first- and second-line chemotherapy evidence and grades the corresponding regimen recommendations 2bB; its generally-against metastatic surgery/PRRT recommendation is separately grade 5D.','MB048',src,'nelm')
replace('almost every therapeutic recommendation in that paper is 4B or weaker and no randomised trial underpins either first- or second-line therapy.','ENETS cites randomized first- and second-line chemotherapy evidence, with regimen recommendations graded 2bB.','MB048',src,'nelm')
cfield('nelm','36924180','limitations/0','Evidence quality varies by question. ENETS cites randomized first- and second-line systemic-therapy studies, including TOPIC-NEC, Zhang, BEVANEC and NET-02; metastatic surgery and PRRT evidence remains sparse and selected.','MB048',src)
cfield('nelm','36924180','limitations/5','First- and second-line chemotherapy recommendations are grade 2bB. Localized surgery/chemoradiation and adjuvant chemotherapy are grade 4B; metastatic MiNEN and the generally-against metastatic surgery/PRRT recommendations are grade 5D.','MB048',src)
cfield('nelm','36924180','critique/6','Adjuvant platinum–etoposide after radical surgery is offered at grade 4B. ENETS discusses observational treated-versus-untreated comparisons with conflicting results and confounding; no randomized adjuvant trial or reliable absolute treatment benefit is established.','MB048',src)
replace('Somatostatin analogue for antiproliferative intent, PRRT, hepatic debulking for cytoreduction and transplantation are all inappropriate.','Do not use SSA for antiproliferative intent in NEC. Metastatic surgery and PRRT are generally not recommended; rare selected exceptions require specialist review and do not establish a transplant indication.','MB048',src,'nelm')

src=A+'metastatic_benign/Source_Reviews/22722717.md; original Table3 and pp451–455; MB068/MB069; NCCN NET PDF115'
cfield('nelm','22722717','critique/2','Table 3 reports two later deaths after prolonged hospitalization and infection following biliary injury. There were no deaths within 30 days. Dates and formal causal adjudication of the later deaths are not supplied, so retain the serious safety signal without describing a measured treatment-related 90-day mortality.','MB069',src)
cfield('nelm','22722717','critique/3','Table 2 does not provide the claimed grade 3–4 biloma count. It prints one liver abscess as 15%, inconsistent with a 13-patient denominator; Table 3 and the narrative supply the cumulative seven bilomas and four drainages. Keep all-grade biliary injury separate from severe-event grading.','MB069',src)
field('nelm','gates/6/avoid/0/pref','NCCN NET directly advises against drug-eluting embolics. Retain avoidance using the small primary safety series and RETNET DEB-arm closure; assess liver burden, reserve and prior biliary intervention separately rather than assuming every injury is irreversible or that a safe DEB subgroup is established.','MB068',src)

for f,t in texts.items():
 if t!=original[f]:(ROOT/f).write_text(t)
p=ROOT/'tools/clinical_revisions/2026-11-02-liver-roadmap-audit.json';out=json.loads(p.read_text());out['files']+=edits
# Correct provenance-only identifiers from phase4 and earlier safety prose; patch content is unchanged.
for e in out['files']:
 why=e['why']
 if 'MB048; '+A+'metastatic_benign/Findings.csv MB048; ENETS2023 NEC36924180 distinction' in why:
  e['why']=why.replace('MB048','MB049')
 if 'metastatic_benign/Source_Reviews/36260828.md; E2211 final analysis; MB046' in why:
  e['why']='MB042;MB051; '+A+'pancreatic_ampullary/Source_Reviews/PMID_36260828.md; E2211 final analysis and Table3'
 if 'MB071' in why and ('injury' in e['new'].lower() or 'irreversible' in e['old'].lower()) and ('MB067' in why or 'NCCN NET safety' in why):
  e['why']=e['why'].replace('MB071','MB068')
p.write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
regs=[{'change_id':f'LIVER-{i+1:03d}','finding_id':e['why'].split('; ')[0],'source_locator':e['why'],'file':e['file'],'old':e['old'],'new':e['new']} for i,e in enumerate(out['files'])]
(ROOT/'tools/audit_revision/liver_change_register.json').write_text(json.dumps(regs,ensure_ascii=False,indent=2)+'\n')
(ROOT/'tools/audit_revision/liver_phase5_misses.json').write_text(json.dumps(misses,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'patches':len(edits),'files':len({e['file'] for e in edits}),'misses':misses},ensure_ascii=False))
