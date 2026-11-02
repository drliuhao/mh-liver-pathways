from pathlib import Path
exec((Path(__file__).with_name('apply_liver_revision.py')).read_text().split('# HCC: stage')[0])
def cfield(slug,pm,path,new,finding,source):
 old=get(json.loads(texts[f'{slug}/data/critique.json'])[pm],path);replace(old,new,finding,source,slug)

# Resolve duplicate clinical statements identified during integration.
src=A+'metastatic_benign/Clinical_Continuation/Adjudications.csv CC07; CLARINET Figure2; A/C final reconciliation'
cfield('nelm','25014687','critique/2','CLARINET subgroup estimates are exploratory: the pancreatic subgroup HR was 0.58 (95% CI 0.32–1.04), hepatic tumour volume >25% HR 0.45 (0.23–0.88), and grade 2 HR 0.45 (0.22–0.91). These are different strata. The estimates do not establish a predictive primary-site, grade or liver-volume cutoff.','MB086',src)
src=A+'hepatobiliary/Source_Reviews/42223137_FIGHT302_partial.md; main Results/Fig2–3; ClarIDHy_Audit_Summary.md'
field('icca','gates/1/standard/1/order','Match treatment to the actionable alteration and prior therapy; this order does not establish a sequence. ClarIDHy provides randomized second-line IDH1 evidence and FIGHT-302 provides a separate first-line FGFR2 comparison against GemCis without immunotherapy. Both demonstrated PFS benefit without a demonstrated ITT OS advantage. The other registration studies listed here are principally single-arm response studies; cross-trial results do not establish comparative survival.','HB081;HB049',src)
replace('first-line policy..','first-line policy.','HB081',src,'icca')
replace('Ivosidenib is the only randomised option and it met progression-free survival, not intention-to-treat overall survival.','ClarIDHy provides randomized second-line IDH1 evidence and met PFS, not ITT OS. The later FIGHT-302 randomized first-line pemigatinib against GemCis without immunotherapy; it does not establish a second-line sequence.','HB081;HB049',src,'icca')
replace('the pemigatinib investigators explicitly warn','The pemigatinib investigators explicitly warn','HB081',src,'icca')
replace('Do not treat the single-arm figures as comparative survival data, and do not expect a response-driven surgical opportunity from ivosidenib (response 2%) or from any of these agents. There is no randomised evidence establishing a sequence among the targeted options.','Single-arm outcomes do not establish comparative survival or a conversion strategy. Ivosidenib has a low objective response rate (2%), while other targeted agents have different response profiles; reassess any major response with MDT rather than applying a categorical bar to surgery. No randomized evidence establishes a sequence among these options.','HB049',src,'icca')
f='icca/data/pathway.json'
def add_fight_ref(d):
 refs=d['gates'][1]['standard'][1]['opts'][0]['refs']
 if '42223137' not in refs: refs.append('42223137')
updatejson(f,add_fight_ref,'HB081',src)
cfield('icca','33798493','bottom_line','ABC-06 provides randomized phase 3 evidence for FOLFOX after cisplatin–gemcitabine: adjusted OS HR 0.69 (95% CI 0.50–0.97), with 12-month survival 25.9% versus 11.4% and a median gain of 0.9 months. Grade 3–5 events occurred in 69% of the chemotherapy arm, including three treatment-related deaths. The response rate was 5%. NIFTY and NALIRICC subsequently provided conflicting randomized phase 2 irinotecan-regimen results; these studies do not establish a cross-trial ranking or an iCCA-specific survival estimate.','B13-R12-F01',src+'; ABC-06 primary report; NIFTY/NALIRICC source records')

src=B+'B14_crlm_roadmap/reviews/R12/R12_REPORT.md F02; Hill37210451 PDF2 Results, PDF3 Table1'
replace('Hill et al. reported seven transplants, five for biliary complications and two for residual tumour, with difficult dissection and frequent atypical arterial reconstruction (PMID 37210451).','Hill et al. reported seven transplants across mixed diagnoses; only three patients had CRLM, two transplanted for HAI cholangiopathy and one for residual tumour. Difficult dissection and arterial reconstruction support early technical planning, not a seven-patient CRLM oncologic efficacy estimate (PMID 37210451).','B14-R12-F02',src,'crlm')
replace('Hill (PMID 37210451) describes seven transplants after HAI: five for biliary complications and two for residual tumour, with difficult dissection and arterial reconstruction.','Hill (PMID 37210451) describes seven transplants across mixed diagnoses, of which three were CRLM: two for HAI cholangiopathy and one for residual tumour. Difficult dissection and arterial reconstruction require advance planning.','B14-R12-F02',src,'crlm')

src=A+'metastatic_benign/Findings.csv MB048; ENETS2023 NEC36924180 distinction of differentiation and proliferation; B15 completed source report'
field('nelm','quickref/0/rows/5/1','A proliferation stratum, not a diagnostic boundary between well-differentiated NET G3 and poorly differentiated NEC. Establish differentiation by morphology, expert pathology review and supportive immunohistochemistry. The cited receptor-positive high-grade PRRT cohort had PFS 4 months and OS 7 months above 55%; this selected retrospective result does not classify the tumour.','MB048',src)

src=A+'metastatic_benign/Source_Reviews/RETNET_2025_POSTER.md; MB067; conference abstractC12 DOI10.1530/endoabs.116.C12; MB071'
field('nelm','gates/6/avoid/0/note','The precautionary recommendation rests on small safety series and the early closure of RETNET’s DEB arm. The 13-patient phase 2 series reported bilomas in 54%; technique, bead size, tumour burden and the small denominator limit attribution to the whole device class. Serious hepatobiliary injury may be permanent. The 2018 RETNET paper is a protocol, whereas separate NANETS 2025 conference results report 151 TAE/cTACE patients and hepatic-PFS HR 1.40 (95% CI 0.80–2.46; P=.234). Those results do not establish equivalence or remove the DEB safety signal.','MB067;MB071',src)
field('nelm','honest/15/why','The DEB recommendation is precautionary. A small interrupted phase 2 series and RETNET’s early DEB-arm closure support concern about serious hepatobiliary harm, but they do not quantify a uniform device-class effect; particle size, technique and population matter. Injury may be permanent, but not every injury is irreversible. RETNET’s 2025 randomized TAE-versus-cTACE results remain conference evidence and did not establish equivalence.','MB067;MB071',src)
src=A+'metastatic_benign/Source_Reviews/36260828.md; E2211 final analysis; MB046'
cfield('nelm','36260828','bottom_line','E2211 randomized patients with progressive low- or intermediate-grade pancreatic NET to temozolomide alone or capecitabine–temozolomide. The interim primary PFS analysis was positive (22.7 versus 14.4 months for CAPTEM versus temozolomide); the final PFS HR was 0.71 (95% CI 0.46–1.07). Final median OS was 58.7 versus 53.8 months for CAPTEM versus temozolomide (P=.42). Responses occurred in 39.7% versus 33.8% (P=.59), so a response advantage from adding capecitabine was not demonstrated, while grade 3–4 toxicity increased. CAPTEM can still be chosen when tumour shrinkage is a goal; the trial neither compares it with all other treatments nor directly establishes its efficacy in NET G3.','MB046',src)

for f,t in texts.items():
 if t!=original[f]:(ROOT/f).write_text(t)
p=ROOT/'tools/clinical_revisions/2026-11-02-liver-roadmap-audit.json';out=json.loads(p.read_text());out['files']+=edits;p.write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
p=ROOT/'tools/audit_revision/liver_change_register.json';regs=json.loads(p.read_text());n=len(regs)
for i,e in enumerate(edits):regs.append({'change_id':f'LIVER-{n+i+1:03d}','finding_id':e['why'].split('; ')[0],'source_locator':e['why'],'file':e['file'],'old':e['old'],'new':e['new']})
p.write_text(json.dumps(regs,ensure_ascii=False,indent=2)+'\n')
(ROOT/'tools/audit_revision/liver_phase4_misses.json').write_text(json.dumps(misses,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'patches':len(edits),'files':len({e['file'] for e in edits}),'misses':misses},ensure_ascii=False))
