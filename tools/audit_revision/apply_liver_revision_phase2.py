from pathlib import Path
exec((Path(__file__).with_name('apply_liver_revision.py')).read_text().split('# HCC: stage')[0])
def critfield(slug,pm,path,new,finding,source):
 d=json.loads(texts[f'{slug}/data/critique.json']);old=get(d[pm],path)
 replace(old,new,finding,source,slug)
def addref(slug,pm,value,finding,source):
 f=f'{slug}/data/pathway.json';d=data(slug)
 if pm not in d['refs']:updatejson(f,lambda d:d['refs'].update({pm:value}),finding,source)
# ClarIDHy 2026 correction: carry corrected uncertainty, not the obsolete significance claim.
src=A+'hepatobiliary/Source_Reviews/42879142.md and ClarIDHy_Audit_Summary.md; correction DOI10.1001/jamaoncol.2026.4298, current Fig2; HB040/HB049'
clar='ClarIDHy improved PFS in previously treated IDH1-mutant cholangiocarcinoma (2.7 versus 1.4 months; HR 0.37). Final ITT OS was 10.3 versus 7.5 months (HR 0.79, 95% CI 0.56–1.12; P=.09), with 70% crossover. The October 2026 correction retains the crossover-adjusted HR 0.49 but changes its bootstrap 95% CI to 0.25–1.24; adjusted OS is not statistically significant. Response was 2%, so large shrinkage is uncommon; surgical conversion was not established.'
field('icca','gates/1/standard/1/opts/1/avoid','Do not promise surgical conversion: objective response was only 2%, and the trial did not test a conversion or transplant strategy. A response may still warrant MDT reassessment. The final crossover-adjusted OS estimate is model-dependent and, after the October 2026 correction, is HR 0.49 (bootstrap 95% CI 0.25–1.24), not a significant randomized survival result.','HB040;HB049',src)
field('hilar','gates/5/alt/1/note',clar+' The final population was predominantly intrahepatic, with only six extrahepatic/perihilar cases; no pCCA-specific treatment effect is established. No randomized evidence establishes a sequence among all targeted options.','HB040;HB049',src) if False else None
# Locate the original ClarIDHy note regardless of option index.
d=data('hilar')
for gi,g in enumerate(d['gates']):
 for ci,op in enumerate(g.get('alt',[])):
  if 'ClarIDHy' in op.get('note',''):field('hilar',f'gates/{gi}/alt/{ci}/note',clar+' The final population was predominantly intrahepatic, with only six extrahepatic/perihilar cases; no pCCA-specific treatment effect is established. No randomized evidence establishes a sequence among all targeted options.','HB040;HB049',src)
critfield('icca','34554208','bottom_line',clar,'HB040;HB049',src)
replace('HR 0.49 (95% CI 0.34-0.70)','HR 0.49 (corrected bootstrap 95% CI 0.25–1.24; October 2026 correction, PMID 42879142)','HB040',src,['icca','hilar'],required=False)
replace('HR 0.49 (0.34–0.70)','HR 0.49 (corrected bootstrap 95% CI 0.25–1.24; PMID 42879142)','HB040',src,['icca','hilar'],required=False)
replace('the frequently quoted 0.49 comes from a crossover-adjustment model that assumes the drug\'s effect is identical whenever given.','the crossover-adjusted HR is 0.49 with a corrected bootstrap 95% CI of 0.25–1.24 (October 2026; PMID 42879142), so adjusted OS is also not statistically significant.','HB040',src,'icca')
addref('icca','42879142',['ClarIDHy 2026 correction','Corrections','Correction: final overall survival efficacy results of ivosidenib for advanced cholangiocarcinoma. JAMA Oncol. 2026. doi:10.1001/jamaoncol.2026.4298. PMID:42879142.'],'HB040',src)
addref('hilar','42879142',['ClarIDHy 2026 correction','Corrections','Correction: final overall survival efficacy results of ivosidenib for advanced cholangiocarcinoma. JAMA Oncol. 2026. doi:10.1001/jamaoncol.2026.4298. PMID:42879142.'],'HB040',src)
# FIGHT-302 is reported; do not change first-line policy on this partial review.
src=A+'hepatobiliary/Source_Reviews/42223137_FIGHT302_partial.md; main Results/Fig2/Fig3; HB080/HB081'
fight='FIGHT-302 has reported (PMID 42223137): 167 randomized patients, PFS 8.3 versus 6.8 months with pemigatinib versus GemCis (HR 0.58, 95% CI 0.39–0.87; nominal P=.0078), without demonstrated OS benefit (24.4 versus 25.0 months). The trial closed early, permitted substantial crossover and did not compare against chemo-immunotherapy; it does not by itself establish a new first-line policy.'
replace('the first-line question is still open in FIGHT-302',fight,'HB081',src,'icca')
replace('Only one of them comes from a randomised trial, and that trial was negative on intention-to-treat overall survival.','ClarIDHy and the subsequently reported first-line FIGHT-302 are randomized trials; neither demonstrated an ITT OS advantage. FIGHT-302 used GemCis rather than a modern chemo-immunotherapy comparator.','HB081',src,'icca')
replace('Pemigatinib, futibatinib, zanidatamab and dabrafenib–trametinib are single-arm, all approved on single-arm data, and none has been compared with second-line chemotherapy;','The initial pemigatinib, futibatinib, zanidatamab and dabrafenib–trametinib approvals rested on single-arm data, and none of those registration studies compared against second-line chemotherapy; first-line FIGHT-302 is a separate randomized update.','HB081',src,'icca')
addref('icca','42223137',['FIGHT-302','Systemic therapy','Bekaii-Saab TS, et al. Pemigatinib versus gemcitabine and cisplatin in FGFR2-rearranged advanced cholangiocarcinoma (FIGHT-302). J Clin Oncol. 2026;44:2187–2197. doi:10.1200/JCO-26-00788. PMID:42223137.'],'HB081',src)
# Remove categorical no-conversion wording where a source shows actual resections.
for f in selected('icca'):
 t=texts[f]
 # Keep review of response conditional; no transplant-eligibility inference.
 for old in ['No targeted agent has shown it can convert unresectable disease to resectable.','No targeted agent has shown conversion to resection.']:
  if old in t:change(f,t.replace(old,'Targeted therapy does not establish a conversion or transplant protocol. FIGHT-202 reported one resection and FIGHT-302 five after pemigatinib; response should prompt selected MDT reassessment without promising cure.'),'HB080',src)
# Houston update; source-correct listing clock and overlapping cohorts.
src=A+'hepatobiliary/Source_Reviews/34856069.md; McMillan2022 PDF3–8/Fig2, OS from listing; B13-R11-F01'
field('icca','gates/9/alt/0/opts/2/when','The Houston update analyzed 32 listed patients, of whom 18 underwent transplantation after at least six months of stability or response; 5-year OS was 49% for the analyzed listed cohort and 57% among eventual recipients, both measured from listing. Recipient 1- and 3-year OS were 100% and 71%. The earlier six-recipient report (83.3% at 3 and 5 years) overlaps and is not an independent cohort.','B13-R11-F01',src)
field('icca','gates/9/alt/0/opts/2/pref','This prospective centre protocol supplies selected locally advanced iCCA experience, with substantial selection and no randomized comparator. NLRB guidance independently specifies six months for its different small-cirrhotic exception phenotype. Stable disease may satisfy protocol biology assessment; major shrinkage is not universally required.','B13-R11-F01;HB-001',src)
replace('OPTN 2025 guidance and ILTS-ILCA 2024 both describe a route for cirrhotic, unresectable, biopsy-proven tumours of 3 cm or less after six months of stability','OPTN guidance describes six months of stability for its cirrhotic, unresectable, biopsy-proven solitary ≤3 cm route; ILTS–ILCA supports consideration after observation but sets no duration for that phenotype','HB-001',src,'icca')
addref('icca','34856069',['McMillan 2022','Transplant','McMillan RR, et al. Survival following liver transplantation for locally advanced, unresectable intrahepatic cholangiocarcinoma. Am J Transplant. 2022;22:823–832. doi:10.1111/ajt.16906. PMID:34856069.'],'B13-R11-F01',src)
# NET: response versus proven superiority; arms and grade-specific extrapolation.
src=A+'metastatic_benign/Findings.csv MB042/MB043; E2211 Table3/p8; sunitinib Table2/p7'
replace('the response rate did not differ from temozolomide alone (39.7% versus 33.8%, P=0.59), so this is not the agent to choose when shrinkage is the object','CAPTEM produced objective responses in 39.7% versus 33.8% with temozolomide (P=.59); response superiority was not established, but this does not exclude use when shrinkage is an important goal','MB042',src,'nelm')
replace('A 9.3% response rate means it stabilises rather than shrinks — it will not convert unresectable hepatic disease.','Objective responses occurred in 8/86 (9.3%), including two complete responses. Response is uncommon and conversion benefit was not tested; do not promise conversion or infer it is impossible.','MB043',src,'nelm')
replace('A 9.3% response rate with 2 complete and 6 partial responses in 83 patients means the drug stabilises rather than shrinks disease, so nothing here supports sunitinib as a way of converting unresectable hepatic disease to resectable.','Objective responses occurred in 8/86 (9.3%), including two complete and six partial responses. The trial did not test conversion to resection; modest response frequency does not prove conversion impossible.','MB043',src,'nelm')
replace('so this is a drug for delaying progression and not for converting hepatic disease.','so the established benefit is delayed progression; a conversion-to-resection strategy remains unproven.','MB043',src,'nelm')
replace('53.8 versus 58.7 months','58.7 months with CAPTEM versus 53.8 months with temozolomide','B15-R9-F01',src,'nelm')
replace('E2211 (n=133, pancreatic, progression within 12 months)','E2211 (n=133 evaluable, low/intermediate-grade pancreatic NET, progression within 12 months; G3 use is extrapolation)','MB042',src,'nelm')
# NEC is defined by differentiation; a Ki-67 cutpoint does not determine the route.
src=A+'metastatic_benign/Source_Reviews/36924180.md; ENETS2023 PDF4,7–8; MB049'
replace('The Ki-67 55% figure that ENETS 2023 calls the best discriminator between carcinoma and well-differentiated G3 is drawn from a single report, and the same paper concedes morphology can be ambiguous, particularly for large-cell carcinoma.','ENETS 2023 explicitly states that Ki-67 alone cannot distinguish NET G3 from NEC. Use differentiation, morphology and appropriate immunohistochemistry; 55% is not a diagnostic boundary.','MB049',src,'nelm')
replace('The Ki-67 55% discriminator between carcinoma and well-differentiated G3 comes from a single report, and the same ENETS paper concedes morphology can be ambiguous, particularly for large-cell carcinoma.','Ki-67 alone, including a 55% cutoff, cannot distinguish well-differentiated NET G3 from poorly differentiated NEC; expert morphology and immunohistochemistry resolve ambiguous cases.','MB049',src,'nelm')
critfield('nelm','36924180','critique/1','Ki-67 alone cannot distinguish NET G3 from NEC. ENETS recommends morphology and appropriate immunohistochemistry; the cited 55% observation is not a stand-alone diagnostic or treatment-route cutoff.','MB049',src)
critfield('nelm','36924180','critique/2','ENETS addresses poorly differentiated NEC separately from well-differentiated NET G3. An ambiguous high-grade biopsy requires expert pathology review; Ki-67 20–55% is not an unassigned diagnostic category.','MB049',src)
critfield('nelm','36924180','bottom_line','ENETS 2023 provides guidance for poorly differentiated digestive NEC, including randomized chemotherapy evidence. It favors platinum–etoposide first line and generally does not recommend metastasectomy or PRRT, while acknowledging rare selected exceptions. NET G3 is a separate diagnosis; differentiation, rather than Ki-67 alone, determines which guidance applies.','MB049',src)
# Correct CLARINET subgroup identity, while avoiding predictive cutoffs.
src='Full_Text_Review_2026-10-31/Analyst_A_Continuation_2026-11-01/reconciliation/C_Final_Addendum_Assessment.md; '+A+'metastatic_benign/Clinical_Continuation/Adjudications.csv CC07; CLARINET Figure2'
critfield('nelm','25014687','critique/1','CLARINET’s grade 2 subgroup HR was 0.45 (95% CI 0.22–0.91). The HR 0.58 (0.32–1.04) belongs to the pancreatic-primary subgroup. Subgroup estimates do not establish differential benefit by grade or primary site.','MB086;B15-CLARINET',src)
replace('and the grade 2 subgroup confidence interval crosses 1.','and subgroup estimates do not establish a predictive grade threshold; grade 2 HR was 0.45 (95% CI 0.22–0.91).','MB086;B15-CLARINET',src,'nelm')
replace('overall survival and quality of life were identical','no statistically significant difference in overall survival or quality of life was demonstrated','MB086;B15-CLARINET',src,'nelm')
# RETNET: conference results exist, but the protocol is not the results paper.
src=A+'metastatic_benign/Source_Reviews/RETNET_2025_POSTER.md; official NANETS2025 abstract C12 DOI10.1530/endoabs.116.C12; MB067'
ret='RETNET results were presented at NANETS 2025 (conference evidence): 151 patients were randomized to bland embolization (78) or conventional TACE (73); hepatic PFS HR 1.40 (95% CI 0.80–2.46; P=.234), with no significant difference. This does not establish equivalence. The DEB arm had closed after an early safety signal. The 2018 protocol does not contain these results; peer-reviewed full reporting remains needed.'
field('nelm','honest/14/why',ret,'MB067',src)
replace('The only randomised comparison in the literature is 26 patients and underpowered, and the three-way prospective trial that would answer it is still running.','The small Maire trial was underpowered. RETNET has now reported randomized TAE-versus-cTACE results as NANETS 2025 conference evidence, without a significant hepatic-PFS difference; that does not prove equivalence.','MB067',src,'nelm')
replace('RETNET is still enrolling','RETNET reported conference results at NANETS 2025; the full journal results report remains pending','MB067',src,'nelm',required=False)
replace('RETNET is still running','RETNET reported conference results at NANETS 2025; the full journal results report remains pending','MB067',src,'nelm',required=False)
# Local protocol status must be visible beside mixed-tumour assessment.
src=B+'B16_chcca_roadmap/reviews/R9/R9_REPORT.md; NLRB pp7–8; D1/D14 OPEN; B16-R9-003'
field('chcca','gates/5/crit/3','Record differentiation, vascular invasion and nodal status for individualized clinical selection. These are not additional explicit NLRB small-cirrhotic eligibility bullets; any stricter local exclusions require a stated programme decision.','B16-R9-003',src)
field('chcca','gates/5/crit/4','An approved written programme pathway and registry are required locally; decision D1 on opening this route remains OPEN. Meeting NLRB guidance alone does not activate a local transplant protocol.','B16-R10-F01',src)
# KEYNOTE-966 explicitly included mixed tumours; no histology-specific effect estimate.
src='Full_Text_Review_2026-10-31/Analyst_A_Continuation_2026-11-01/batches/B16_chcca_roadmap/41781152.md; KEYNOTE966 Methods/Table1; B16/R8/37075781.md'
keynote='KEYNOTE-966 enrolled 13 mixed HCC–CCA patients (8 pembrolizumab, 5 placebo), but reported no separate treatment effect for them. The overall BTC result (OS 12.7 versus 10.9 months; HR 0.83, 95% CI 0.72–0.95) cannot be presented as a cHCC–CCA-specific effect. HCC and other BTC regimens remain individualized extrapolations in this histology.'
field('chcca','gates/7/avoid/1/pref',keynote,'B16-KEYNOTE966',src)
field('chcca','gates/7/avoid/1/avoid','Name the source population, comparator and the absence of a powered mixed-histology analysis. Thirteen enrolled mixed cases do not establish a histology-specific benefit or a preferred regimen; retain multidisciplinary review and clinical trials.','B16-KEYNOTE966',src)
field('chcca','honest/1/why',keynote+' TOPAZ-1 and the HCC trials do not supply a validated cHCC–CCA subgroup effect.','B16-KEYNOTE966',src)
replace('patients with this histology were excluded from the landmark trials in both hepatocellular carcinoma and biliary tract cancer — by name in the case of KEYNOTE-966 —','most landmark studies do not establish a mixed-histology treatment effect; KEYNOTE-966 included 13 mixed cases without a separate effect estimate,','B16-KEYNOTE966',src,'chcca')
# Auer is interventional iCCA review, not systemic cHCC-CCA consensus.
src='Full_Text_Review_2026-10-31/Analyst_A_Continuation_2026-11-01/batches/B16_chcca_roadmap/41781152.md; Auer37174120 targeted PDF1–3,13'
critfield('chcca','37174120','bottom_line','A narrative review of interventional treatment for iCCA with an outlook for mixed tumours. It supplies no cHCC–CCA-specific comparative systemic-treatment estimate and cannot establish a gemcitabine–platinum/checkpoint standard for this histology.','B16-R9-007',src)
critfield('chcca','37174120','critique/3','The review’s principal scope is interventional iCCA treatment; mixed-tumour systemic choices require separately identified primary or review sources and explicit extrapolation.','B16-R9-007',src)
# Residual kappa shorthand in critiques.
src=B+'B16_chcca_roadmap/reviews/R4/38092727.md; primary pp3–4'
replace('pathologists agree on cHCC-CCA at kappa 0.19-0.37','dominant-component reclassification agreement is kappa 0.19 for model versus pathologist and 0.37 between pathologists','B16-R9-001',src,'chcca')
replace('while also showing pathologists agree on the diagnosis at kappa 0.19 — so the entity\'s pooled survival figures are averages of two diseases.','with model–pathologist dominant-component reclassification agreement of kappa 0.19. This retrospective classification is not a validated prospective diagnostic or transplant-selection tool.','B16-R9-001',src,'chcca')
# CRLM source scope and older randomized DEBIRI survival signal.
src=B+'B14_crlm_roadmap/reviews/R12/R12_REPORT.md; Hill37210451 Results PDF2/Table1 PDF3'
for f in selected('crlm'):
 t=texts[f]
 t=t.replace('HAI-to-transplant evidence is seven cases','HAI-to-transplant evidence is a seven-patient mixed-indication series, including three CRLM cases (two transplanted for cholangiopathy and one for tumour)')
 if t!=texts[f]:change(f,t,'B14-R12-F02',src)
src=A+'metastatic_benign/Source_Reviews/22493375.md; DEBIRI main PDF1,4–7; MB035'
# Replace exact order paragraph, preserving option order as a clinical judgement.
d=data('crlm')
for gi,g in enumerate(d['gates']):
 for ai,op in enumerate(g.get('alt',[])):
  if 'neither' in op.get('order','').lower() and ('survival' in op.get('order','').lower()):
   field('crlm',f'gates/{gi}/alt/{ai}/order','Choose liver-directed treatment by disease distribution, liver reserve, prior therapy and goals. EPOCH did not demonstrate OS benefit; the small historical DEBIRI trial reported OS 22 versus 15 months (P=.031), with substantial reporting and obsolete-comparator limitations. These trials do not establish a hierarchy against current systemic therapy.','MB035',src)
# Append new exact patches to the single liver manifest, never touching other agents' files.
for f,t in texts.items():
 if t!=original[f]:(ROOT/f).write_text(t)
p=ROOT/'tools/clinical_revisions/2026-11-02-liver-roadmap-audit.json';out=json.loads(p.read_text());out['files']+=edits;p.write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
p=ROOT/'tools/audit_revision/liver_change_register.json';regs=json.loads(p.read_text());n=len(regs)
for i,e in enumerate(edits):regs.append({'change_id':f'LIVER-{n+i+1:03d}','finding_id':e['why'].split('; ')[0],'source_locator':e['why'],'file':e['file'],'old':e['old'],'new':e['new']})
p.write_text(json.dumps(regs,ensure_ascii=False,indent=2)+'\n')
(ROOT/'tools/audit_revision/liver_phase2_misses.json').write_text(json.dumps(misses,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'patches':len(edits),'files':len({e['file'] for e in edits}),'misses':misses},ensure_ascii=False))
