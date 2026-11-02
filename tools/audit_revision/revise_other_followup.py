#!/usr/bin/env python3
"""One-time, bounded follow-up to revise_other.py; appends exact replay chunks."""
from pathlib import Path

helper = Path(__file__).with_name('revise_other.py').read_text()
exec(helper.split('# Pancreatic cyst fluid and high-risk interpretation.')[0])

src=B+'B20_pnet_roadmap/reviews/R7/36434154.md; Chan 2023 pp552–554, Tables2–4 and limitations'
setp('pnet','gates.1.alt.0.avoid','Do not use NETPET alone to decide an operation on a localized primary. The cohorts involved metastatic or unresectable disease, with only 39% and 36% pancreatic primaries and no pancreas-specific analysis. The validation centres had published earlier series, but patient overlap with those series is unquantified. Treatment was not adjusted for. SSTR-positive disease across P1–P4 may be eligible for PRRT; FDG positivity does not by itself exclude it, so treatment access cannot be attributed only to P1. These data support prognosis, not a validated treatment threshold or a localized-primary resection rule.',['S48707d8896','S90f214117b','Sc3960d6e75'],src)
setp('pnet','honest.14.why','NETPET and histological grade were independently prognostic in the 319-patient metastatic GEP-NEN validation cohort. This does not establish superiority over pathology or determine treatment for a small localized primary. The study did not adjust for treatment; PRRT eligibility can extend to SSTR-positive P1–P4 disease rather than requiring FDG negativity. Centres had earlier published series, but patient overlap is unquantified. Dual-tracer imaging may help identify a higher-risk biopsy target in selected patients; document how the result would change care.',['S48707d8896','S90f214117b','Sc3960d6e75'],src)
setp('pnet','ops.approvals.14.why','The dual-tracer score is prognostic in metastatic or unresectable GEP-NEN, with only about a third pancreatic primaries and no validated threshold for treating a localized primary. Treatment was not adjusted for; SSTR-positive P1–P4 patients may receive PRRT. Define the selected clinical question, biopsy implications and intended management change before adding FDG imaging.',['Sc3960d6e75'],src)
sub('319 patients: score independently predicted survival alongside grade. Roadmap critique: metastatic or unresectable disease, about a third pancreatic, partly the derivation centres, treatment not modelled, no treatment threshold.','319 metastatic GEP-NEN patients: score independently predicted survival alongside grade. About a third had pancreatic primaries; earlier-series overlap is unquantified, treatment was not adjusted for, and no localized-primary treatment threshold was established.',['S48707d8896'],src,['pnet'])
setp('pnet','28435454.critique.3','Treatment was not adjusted for. PRRT eligibility depends on adequate SSTR expression and clinical selection and may include FDG-positive disease; it is not restricted to SSTR-positive/FDG-negative P1. Treatment access may therefore confound prognosis across receptor-positive categories.',['S90f214117b'],src,kind='critique')
setp('pnet','36434154.critique.0','The centres had published earlier series and re-queried their databases. Patient overlap with the original derivation and other earlier cohorts is unquantified; do not assert that two centres supplied the original derivation patients or that a known proportion is a re-analysis.',['S48707d8896'],src,kind='critique')
setp('pnet','36434154.bottom_line','In 319 patients with metastatic GEP-NEN, NETPET and histological grade independently predicted overall survival and time to progression. Treatment was not adjusted for, earlier-series overlap is unquantified and only about a third had pancreatic primaries. The study does not validate a treatment threshold for localized pNET.',['S48707d8896','S90f214117b'],src,kind='critique')

src='Full_Text_Review_2026-10-31/Analyst_A_Continuation_2026-11-01/batches/B26_residual_sources/42456089.md; original PMC13374715 author-manuscript Methods, Results, Tables1–2 and Discussion'
setp('pdac','gates.6.alt.1.t','Consider adjuvant chemoradiation after chemotherapy in selected node-negative patients through multidisciplinary discussion; the overall RTOG 0848 result was negative.',['A-B26-RTOG0848','C-APACT-miscitation'],src)
setp('pdac','gates.6.alt.1.pref','RTOG 0848 randomized 354 patients without recurrence after five chemotherapy cycles. From this randomization, overall survival was not significantly improved (HR 0.96, 90% CI 0.79–1.18), nor was final-report disease-free survival (HR 0.82, 95% CI 0.65–1.03; two-sided P=.089). Significant nodal-status interactions and favorable node-negative results support an individualized discussion, not routine treatment of every resected patient.',['A-B26-RTOG0848'],src)
setp('pdac','gates.6.alt.1.avoid','None of the patients received FOLFIRINOX: 67% received gemcitabine alone, 28% gemcitabine/erlotinib and 5% other gemcitabine combinations. Benefit after modern chemotherapy is unestablished. Only ten patients were both node-negative and margin-positive, so margin-specific inference is inadequate. SBRT substitution is unestablished.',['A-B26-RTOG0848'],src)
setp('pdac','gates.6.alt.1.note','The final primary report is now available. Grade-3 toxicity was greater with chemoradiation (38% versus 19%); grade-4/5 toxicity did not significantly differ. The main clinical text, tables and figure captions were reviewed in the continuation; figure pixels, the separate supplement and protocol were not. The earlier abstract’s one-sided DFS formulation should not replace the final nonsignificant two-sided result.',['A-B26-RTOG0848'],src)
setp('pdac','gates.6.alt.1.g','C',['A-B26-RTOG0848'],src,propagate=False)
f='pdac/data/pathway.json';p=('gates',6,'alt',1,'refs');old=data[f]['gates'][6]['alt'][1].get('refs');new=['42456089'];data[f]['gates'][6]['alt'][1]['refs']=new;log(f,p,old,new,['C-APACT-miscitation'],src)
setp('pdac','gates.6.avoid.1.t','Do not present RTOG 0848 as establishing routine adjuvant chemoradiation benefit in node-positive disease.',['A-B26-RTOG0848'],src)
setp('pdac','gates.6.avoid.1.pref','Individualize radiation decisions with oncology and radiation oncology review, considering the systemic regimen, margins, nodal status, recovery, toxicity and patient preferences.',['A-B26-RTOG0848'],src)
setp('pdac','gates.6.avoid.1.avoid','The overall primary result was negative and the node-positive subgroup did not show benefit. A subgroup result does not establish a universal prohibition for every clinical context. The node-negative signal also requires caution after modern chemotherapy.',['A-B26-RTOG0848'],src)
setp('pdac','nonpm.rtog0848.2','Resolved to the primary NRG Oncology/RTOG 0848 report, PMID42456089, DOI10.1200/JCO-25-02520. Among 354 patients randomized after five recurrence-free chemotherapy cycles, added chemoradiation did not significantly improve overall OS or final-report DFS. Node-negative subgroup results support individual discussion, with unestablished transfer to modern chemotherapy.',['A-B26-RTOG0848'],src)
addref('pdac','42456089',['RTOG 0848 final report','Neoadjuvant & adjuvant trials','Abrams RA, et al. Adjuvant chemotherapy +/− chemoradiotherapy for adenocarcinoma of the pancreatic head: results of the radiotherapy randomization of NRG Oncology/RTOG 0848. J Clin Oncol. 2026;44(24):2316–2328. doi:10.1200/JCO-25-02520. PMID:42456089.'],['A-B26-RTOG0848'],src)
setp('pdac','honest.23.t','Source availability and read extent differ; the continuation resolved some earlier gaps.',['A-B26-RTOG0848'],src)
setp('pdac','honest.23.why','RTOG 0848 now has a reviewed final primary report and is summarized above. Other statements may depend on targeted original-guideline checks, abstracts, or reports with unread supplements. Consult the preserved source-level audit records rather than treating an old retrieval list or a passing website test as full verification.',['A-B26-RTOG0848'],src)
setp('pdac','ops.approvals.12.why','Assign ownership of the residual source-review list, record the actual source version and read extent, and propagate verified corrections. RTOG 0848 is resolved to PMID42456089; do not continue to label it an unavailable primary report.',['A-B26-RTOG0848'],src)
sub('No owner is proposed. The roadmap lists what still needs primary reports (the full ISGPS consensus; PAXG, RTOG 0848, ESPAC-3 completion, CONKO-004 and maintenance rucaparib; EUS staging, re-imaging and margin-clearance figures), asks that PAXG be read before the regimen is used, and tracks source currency on the dashboard.','Name an owner for residual source verification and keep actual read extent visible. The continuation has resolved some earlier gaps, including the final RTOG 0848 report; use the preserved source dossiers to maintain the remaining list.',['A-B26-RTOG0848'],src,['pdac'])
f='documents/pdac/questions.json';old=data[f]['sources'].pop('hr-cluster');log(f,('sources','hr-cluster'),old,None,['USER-remove-PDAC-transplant-concepts'],'Explicit prior user request; PDAC-B1/B2 removed; this historical reference is now orphaned.')

# Write only changed owned files, appending sequential unique protected replacements.
manifest_path=ROOT/'tools/clinical_revisions/2026-11-02-other-roadmaps.json'
manifest=json.loads(manifest_path.read_text())
chunks=[]
for f,obj in data.items():
    before=original[f]
    after=json.dumps(obj,ensure_ascii=False,separators=(',',':')) if '/critique.json' in f else json.dumps(obj,ensure_ascii=False,indent=1)+'\n'
    if before==after:continue
    a,b=before.splitlines(keepends=True),after.splitlines(keepends=True)
    for group in difflib.SequenceMatcher(None,a,b,autojunk=False).get_grouped_opcodes(3):
        old=''.join(a[group[0][1]:group[-1][2]])
        new=''.join(b[group[0][3]:group[-1][4]])
        assert before.count(old)==1,f
        chunks.append({'file':f,'old':old,'new':new,'why':'Bounded NETPET/RTOG and orphan-question-source follow-up; field/source details in other_change_register.json.'})
    replay=before
    for e in [e for e in chunks if e['file']==f]:
        assert replay.count(e['old'])==1,f
        replay=replay.replace(e['old'],e['new'],1)
    assert replay==after,f
    (ROOT/f).write_text(after)
manifest['files']+=chunks
manifest_path.write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
p=ROOT/'tools/audit_revision/other_change_register.json';register=json.loads(p.read_text());register['changes']+=changes
for row in register['changes']:
    row['source_locator']=row['source_locator'].replace('reviews/metastatic_benign/Source_Reviews/Priority_Clinical_Corrections.md','reviews/metastatic_benign/Priority_Clinical_Corrections.md')
p.write_text(json.dumps(register,ensure_ascii=False,indent=2)+'\n')
p=ROOT/'tools/audit_revision/other_shared_proposals.json';proposals=json.loads(p.read_text());proposals+=shared;p.write_text(json.dumps(proposals,ensure_ascii=False,indent=2)+'\n')
print(f"Final: {len(register['changes'])} field changes; {len(manifest['files'])} exact chunks; {len(proposals)} shared proposals")
