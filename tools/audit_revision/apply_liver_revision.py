"""Analyst A: bounded, source-supported liver roadmap corrections (2026-11-02)."""
from pathlib import Path
import json,difflib,re,hashlib
ROOT=Path(__file__).resolve().parents[2]
SLUGS=['hcc','hilar','icca','crlm','nelm','chcca']
DOCSLUG={'hilar':'pcca',**{s:s for s in SLUGS if s!='hilar'}}
files=[]
for s in SLUGS:
 files += [p for p in (ROOT/s).rglob('*') if p.suffix in ('.json','.html')]
 files += [ROOT/'tools/consensus_source'/f'roadmap_{s}.json',ROOT/'documents'/DOCSLUG[s]/'questions.json']
files=[p for p in files if p.exists()]
texts={str(p.relative_to(ROOT)):p.read_text() for p in files}
original=texts.copy(); edits=[]; register=[]; misses=[]
A='Full_Text_Review_2026-10-31/Analyst_A_Full_Reaudit_2026-11-01/reviews/'
B='Full_Text_Review_2026-10-31/Analyst_B/batches/'
def selected(slugs):
 if isinstance(slugs,str):slugs=[slugs]
 return [f for f in texts if any(f.startswith(s+'/') or f==f'tools/consensus_source/roadmap_{s}.json' or f==f'documents/{DOCSLUG[s]}/questions.json' for s in slugs)]
def change(file,new,finding,source):
 old=texts[file]
 if old==new:return
 # Reversible unique patches, applied from right to left, compatible with Revisions.applyText.
 oldlines=old.splitlines(keepends=True);newlines=new.splitlines(keepends=True)
 oldoff=[0];newoff=[0]
 for line in oldlines:oldoff.append(oldoff[-1]+len(line))
 for line in newlines:newoff.append(newoff[-1]+len(line))
 for tag,li,lj,lk,ll in reversed(list(difflib.SequenceMatcher(None,oldlines,newlines,autojunk=True).get_opcodes())):
  i,j,k,l=oldoff[li],oldoff[lj],newoff[lk],newoff[ll]
  if tag=='equal':continue
  lo=max(0,i-100);hi=min(len(old),j+100)
  while texts[file].count(old[lo:hi])!=1:
   lo=max(0,lo-100);hi=min(len(old),hi+100)
   if lo==0 and hi==len(old):break
  o=old[lo:hi];n=old[lo:i]+new[k:l]+old[j:hi]
  assert texts[file].count(o)==1,(file,finding)
  edits.append({'file':file,'old':o,'new':n,'why':finding+'; '+source})
  texts[file]=texts[file].replace(o,n,1)
 assert texts[file]==new,file
 register.append({'finding_id':finding,'source_locator':source,'file':file,'old':old,'new':new})
def replace(old,new,finding,source,slugs=SLUGS,required=True):
 found=0
 for f in selected(slugs):
  t=texts[f]
  variants=[(old,new)]
  enc=lambda s:json.dumps(s,ensure_ascii=False)[1:-1]
  if enc(old)!=old:variants.append((enc(old),enc(new)))
  for o,n in variants:
   if o in t:t=t.replace(o,n);found+=1
  if t!=texts[f]:change(f,t,finding,source)
 if not found and required:misses.append((finding,old[:130]))
def data(slug):return json.loads(texts[f'{slug}/data/pathway.json'])
def get(v,path):
 for k in path.split('/'):v=v[int(k)] if isinstance(v,list) else v[k]
 return v
def field(slug,path,new,finding,source):replace(get(data(slug),path),new,finding,source,slug)
def qfield(slug,qid,key,new,finding,source):
 d=json.loads(texts[f'tools/consensus_source/roadmap_{slug}.json']);old=next(q for q in d['questions'] if q['id']==qid)[key]
 if not isinstance(old,str):raise TypeError(key)
 replace(old,new,finding,source,slug)
def updatejson(f,func,finding,source):
 d=json.loads(texts[f]);func(d);change(f,json.dumps(d,ensure_ascii=False,indent=2)+'\n',finding,source)
# HCC: stage is separate from treatment selection and portal pressure.
src=A+'hepatobiliary/Source_Reviews/41151697.md; BCLC 2026 staging figure p9; B11/R13 CF04'
replace('crit:["Single lesion ≤2 cm","ECOG 0","Child-Pugh A","No clinically significant portal hypertension"]','crit:["Single lesion ≤2 cm","ECOG 0","Preserved liver function"]','B11-R13-CF04',src,'hcc')
replace('Macrovascular invasion or extrahepatic spread?</div>','Macrovascular invasion, extrahepatic spread, or cancer-related ECOG 1–2?</div>','B11-R12-F01',src,'hcc')
replace('What is the tumour burden on the staging scan?</div>','With ECOG 0 and preserved liver function, what is the tumour burden?</div>','B11-R12-F01',src,'hcc')
replace('<div class="stages" id="stageBtns"></div>','<p class="small muted">Assess liver function before assigning stages 0–B. Child-Pugh B or decompensation needs individualized hepatology and transplant assessment; tumour burden alone does not establish an early stage or treatment eligibility.</p>\n    <div class="stages" id="stageBtns"></div>','B11-R12-F01',src,'hcc')
src='B11/R12 F02; '+A+'metastatic_benign/Source_Reviews/LIRADS_CORE_2018.md; ACR CT/MRI LI-RADS v2018 diagnostic table'
replace('<tr><th style="width:38%">Additional major features</th><th>Any size</th></tr></thead><tbody>\n          <tr><td>0</td><td>LR-3</td></tr>\n          <tr><td>≥1</td><td>LR-4</td></tr>','<tr><th style="width:38%">Additional major features</th><th>&lt;20 mm</th><th>≥20 mm</th></tr></thead><tbody>\n          <tr><td>0</td><td>LR-3</td><td>LR-3</td></tr>\n          <tr><td>1</td><td>LR-3</td><td>LR-4</td></tr>\n          <tr><td>≥2</td><td>LR-4</td><td>LR-4</td></tr>','B11-R12-F02',src,'hcc')
src='B11/R11 R11-F01; Baveno VIII PDF p55 statement 8.44 (PSVD), p16 1.16c, p17 1.19; roadmap distinction retained'
replace('Medium or large oesophageal varices; gastric varices; spontaneous portosystemic collaterals; spleen stiffness &gt;40 kPa absent myeloproliferative neoplasm.','Oesophageal or gastric varices; spontaneous portosystemic collaterals.','B11-R11-R11-F01',src,'hcc')
replace('Baveno VIII lists these as specific signs of portal hypertension in its PSVD/NCPF diagnostic score (statement 8.44) — note that spleen stiffness &gt;40 kPa is <b>not</b> one of its cACLD CSPH criteria — and names varices or portosystemic collaterals as generally signs of CSPH (statement 3.2d). A shunt reported on staging CT is a staging finding, not an incidental one.','Baveno VIII identifies varices and portosystemic collaterals as generally indicating CSPH (statement 3.2d), with the exceptions below. The PSVD diagnostic score is a separate assessment; its spleen-stiffness &gt;40 kPa item must not be used to rule in cirrhotic CSPH.','B11-R11-R11-F01',src,'hcc')
replace('Overt ascites; small oesophageal varices; platelets &lt;150 × 10⁹/L; splenomegaly.</td><td>Supportive but not sufficient alone. Absence does not exclude CSPH.','Platelets &lt;150 × 10⁹/L; splenomegaly.</td><td>Supportive findings do not establish CSPH alone. Ascites requires evaluation for hepatic decompensation and its cause. Absence of these findings does not exclude CSPH.','B11-R11-R11-F01',src,'hcc')
# Microwave evidence: local control, not universal survival superiority.
src=A+'hepatobiliary/Source_Reviews/39802807.md; Sugimoto 2025 PDF5/printed4, Fig2/Table3; HB031; B11-R13-CF01'
mwa='MWA and RFA are both options. Sugimoto 2025 found lower two-year lesion-level local progression with MWA than single-needle RFA (20/122, 16.4%, versus 38/125, 30.4%; RR 0.54, 95% CI 0.33–0.87; P=.007), without a demonstrated overall-survival advantage. Most lesions were small; this does not establish superiority over every RFA system or a specific 3–4 cm subgroup.'
replace('No randomised trial separates them — Vietti Violi was a negative superiority trial at a mean lesion size of 18 mm — but BCLC 2026 now prefers microwave up to 3–4 cm.','BCLC 2026 prefers microwave up to 3–4 cm on local-control evidence. Sugimoto 2025 found two-year lesion progression of 16.4% with MWA versus 30.4% with single-needle RFA, without a demonstrated survival advantage; earlier trials did not show a significant difference.','HB031',src,'hcc')
replace('BCLC 2026 prefers microwave up to 3–4 cm; no randomised trial has shown a difference, so below that the choice is operational.','BCLC 2026 prefers microwave up to 3–4 cm on local-control evidence; the positive trial used single-needle RFA and did not demonstrate a survival advantage.','HB031',src,'hcc')
replace('<b>Microwave versus radiofrequency: no demonstrated superiority.</b> The randomised comparison in HCC up to 4 cm was a superiority trial: it did not show superiority of microwave over radiofrequency ablation, did not test non-inferiority, and found no significant difference in two-year local tumour progression (6% versus 12%, RR 1.62, 95% CI 0.66–3.94). v0.2 said microwave is “often favoured operationally”, which is accurate — but that is a workflow preference, not an outcome-based one. {{29503247}}','<b>Microwave versus radiofrequency.</b> '+mwa+' The earlier Vietti Violi superiority trial did not show a significant local-progression difference and did not test equivalence. {{29503247|39802807}}','HB031',src,'hcc')
replace('The BCLC 2026 preference for microwave up to 3 to 4 cm is a change of guideline position, not a trial result.','The later Sugimoto trial supports a device-specific local-control advantage for MWA, without a demonstrated survival advantage (PMID 39802807).','HB031',src,'hcc')
replace('No randomised superiority. The one randomised comparison was a superiority trial','The earlier Vietti Violi comparison was a superiority trial','HB031',src,'hcc')
qfield('hcc','HCC-D9','question','Decide whether to adopt the BCLC 2026 microwave preference, distinguishing a device-specific local-control advantage from an unproven survival advantage.','HB031',src)
qfield('hcc','HCC-D9','proposal','Microwave or radiofrequency according to anatomy, achievable margin and expertise. BCLC 2026 prefers microwave up to 3–4 cm on local-control evidence; adopting that preference locally remains an OPEN decision.','HB031',src)
qfield('hcc','HCC-D9','rationale',mwa+' Earlier randomized comparisons did not show significant superiority; nonsignificance does not establish equivalence.','HB031',src)
qfield('hcc','HCC-D9','divergence','BCLC 2026 prefers microwave on local-control evidence. EASL 2025 does not recommend one thermal technique over the other; neither position establishes survival equivalence or universal device superiority.','HB031',src)
replace('Prefers microwave over radiofrequency ablation up to 3-4 cm; the roadmap calls this a change of guideline position, not a trial result.','Prefers microwave up to 3–4 cm on local-control evidence, including Sugimoto 2025 (PMID 39802807); a survival advantage was not demonstrated.','HB031',src,'hcc')
replace('Treats radiofrequency and microwave ablation as equivalent.','Does not recommend one thermal technique over the other; this is not proof of equivalence.','HB031',src,'hcc')
# New source uses existing reference hierarchy; parent supplies shared compact study row.
ref=' "39802807":["Sugimoto 2025","Thermal ablation","Sugimoto K, et al. Microwave ablation versus radiofrequency ablation for hepatocellular carcinoma: a randomized controlled trial. JHEP Rep. 2025;7:101269. doi:10.1016/j.jhepr.2024.101269. PMID:39802807."],\n'
f='hcc/index.html';anchor=' "29503247":'
if anchor in texts[f]:change(f,texts[f].replace(anchor,ref+anchor,1),'HB031',src)
# Systemic combinations remain trial-only under BCLC.
src=A+'hepatobiliary/Source_Reviews/41151697.md; BCLC2026 TACE/systemic section; HB030'
replace('Phase 3 trials have since overtaken the position and the 2026 BCLC update incorporates them, so a reader using this document now is advised against a treatment that has become standard.','Subsequent phase 3 trials reported PFS benefits, but BCLC 2026 still advises against routine TACE–systemic combinations outside trials; these data have not established a new BCLC standard.','HB030',src,'hcc')
# AFP boundaries apply to exception priority; preserve stricter OPEN proposals.
src=A+'hepatobiliary/Source_Reviews/OPTN-2026-10-01.md; Policy 9.5.I.ii/iv pp197–198; B11-R12-F05'
replace('An AFP at or above 1,000 ng/mL blocks the standard exception','An AFP above 1,000 ng/mL blocks the standard exception','B11-R12-F05',src,'hcc')
replace('An AFP of 1,000 ng/mL or more blocks the standard exception','An AFP above 1,000 ng/mL blocks the standard exception','B11-R12-F05',src,'hcc')
replace('allow listing once an AFP of 1,000 ng/mL or more falls below 500','allow a standardized exception once an AFP above 1,000 ng/mL falls below 500 after treatment','B11-R12-F05',src,'hcc')
replace('allows listing once an AFP of 1,000 or more falls below 500 ng/mL','supports the standardized exception after an AFP above 1,000 falls below 500 ng/mL following treatment','B11-R12-F05',src,'hcc')
replace('allow listing once an AFP of 1,000 or more falls below 500 ng/mL','allow the standardized exception after an AFP above 1,000 falls below 500 ng/mL following treatment','B11-R12-F05',src,'hcc')
replace('requiring three months at or below 1,000','requiring AFP below 1,000 for at least three months after downstaging','B11-R12-F05',src+'; EASL 2025 p29','hcc')
replace('requires 1,000 or less for 3 months before listing','requires AFP below 1,000 for at least 3 months after downstaging','B11-R12-F05',src+'; EASL 2025 p29','hcc')
replace('1,000 or less must be sustained for three months before listing','AFP below 1,000 must be sustained for at least three months after downstaging','B11-R12-F05',src+'; EASL 2025 p29','hcc')
# Adjuvant statement is all systemic therapy, not only atezolizumab-bevacizumab.
src=A+'hepatobiliary/Source_Reviews/39992051.md; AASLD critical update statement32 PDF2; B11-R13-CF03'
replace('<b>Adjuvant atezolizumab–bevacizumab is not recommended.</b>','<b>AASLD advises against routine neoadjuvant or adjuvant systemic therapy for resection or local ablation; use clinical trials.</b>','B11-R13-CF03',src,'hcc')
qfield('hcc','HCC-D14','question','Decide whether any adjuvant locoregional therapy is offered after high-risk resection, recognizing that AASLD advises against neoadjuvant/adjuvant systemic therapy and EASL 2025 advises against any adjuvant treatment.','B11-R13-CF03',src+'; EASL 2025 pp25–26,45')
qfield('hcc','HCC-D14','rationale','AASLD statement 32 advises against neoadjuvant and adjuvant systemic therapy after resection or ablation. EASL 2025 advises against any adjuvant treatment. Chinese trials and broader meta-analyses report locoregional benefit signals, but generalizability and the local treatment policy require explicit review.','B11-R13-CF03',src+'; EASL 2025 pp25–26,45')
qfield('hcc','HCC-D14','divergence','AASLD advises against neoadjuvant/adjuvant systemic therapy and EASL against any adjuvant treatment. Adjuvant TACE/HAI signals from predominantly Eastern populations do not create an approved local treatment policy.','B11-R13-CF03',src)
replace('Advises against adjuvant and neoadjuvant systemic therapy after resection or ablation because IMbrave050\'s benefit did not hold; roadmap: it concerns atezolizumab-bevacizumab, rests on an interim analysis, and extends to neoadjuvant therapy without a cited trial.','Advises against neoadjuvant and adjuvant systemic therapy after resection or local ablation (statement 32, Level 1, strong). Small neoadjuvant studies do not establish a survival benefit over immediate surgery.','B11-R13-CF03',src,'hcc')
# pCCA: regional nodes concern prognosis and LT exclusion, not automatic resection exclusion.
src=B+'B12_hilar_roadmap/reviews/R12/R12_REPORT.md; Milan Rec9 p74; AASLD PSC/CCA p27; B12-R12-F01'
field('hilar','gates/3/crit/3','No intrahepatic, extrahepatic, distant (non-regional) nodal or peritoneal metastases on the staging package; regional nodal disease requires prognostic assessment and does not by itself exclude resection.','B12-R12-F01',src)
field('hilar','gates/5/crit/0','Regional nodal disease or a radial mass of 3 cm or more excludes the standardized transplant exception. If otherwise resectable, return to resection assessment; these findings alone do not establish unresectability. Confirm borderline measurements with the transplant team.','B12-R12-F01',src)
replace('0 · Assess the need for biliary drainage','0 · Assess drainage after staging imaging, unless urgent','B12-R11-F01',B+'B12_hilar_roadmap/reviews/R11/R11_REPORT.md; ESGE 2025 p8; DRAINAGE p9','hilar')
# Accurate guideline attribution without silently approving a new local capecitabine label.
src=B+'B12_hilar_roadmap/reviews/R12/R12_REPORT.md; Milan Rec54 p79; ESMO2023 p7; AASLD PSC/CCA p27'
replace('Records that the adjuvant trials showed no benefit in the perihilar subgroup.','Recommends six months of adjuvant capecitabine or S-1 after pCCA resection (strong recommendation, level 2); the trials were not powered for the perihilar subgroup.','B12-R12-F03',src,'hilar')
qfield('hilar','pCCA-D5','divergence','Milan, ESMO, AASLD and NCCN support adjuvant capecitabine after resection. The roadmap’s more cautious Reasonable/grade C label is an OPEN local divergence; a nonsignificant pCCA subgroup does not establish absence of benefit.','B12-R12-F03',src)
# iCCA small cirrhotic exception: six-month observation belongs directly to NLRB guidance.
src=A+'hepatobiliary/Findings.csv HB-001/HB091; NLRB oncology guidance pp7–8; Clinical_Continuation.md'
field('icca','gates/9/alt/0/opts/1/when','The nonbinding NLRB guidance supports consideration of MMaT-3 for biopsy-proven, unresectable, solitary iCCA or mixed HCC-iCCA ≤3 cm in cirrhosis, after treatment and six months of documented stability. The six-month interval is specified directly in this guidance; it is not proof of an optimal biological observation period.','HB-001;HB091',src)
field('icca','honest/12/why','NLRB guidance itself specifies six months of stability for the solitary ≤3 cm cirrhotic iCCA/mixed-tumour exception route. ILTS–ILCA gives no duration for its small cirrhotic phenotype. Incidental explant series did not select on stability, while the prospective Houston programme selected locally advanced disease after at least six months of response or stability. These different populations do not establish that six months is the optimal biological interval.','HB-001;HB091',src)
field('icca','ops/approvals/10/why','The NLRB small-cirrhotic exception guidance directly specifies six months of stability. This administrative recommendation is separate from ILTS–ILCA’s observation wording and from the Houston locally advanced protocol; neither establishes the optimal biological interval. Early referral may occur while treatment and observation continue.','HB-001;HB091',src)
replace('Attaches no duration to the cirrhotic 3 cm recommendation, only an observed period of stability; its six-month requirement belongs to the weakly graded non-cirrhotic investigational route.','Attaches no duration to its cirrhotic ≤3 cm recommendation. The NLRB guidance separately specifies six months for its small-cirrhotic exception route; do not attribute that interval only to advanced-disease protocols.','HB-001;HB091',src,'icca')
qfield('icca','iCCA-D11','divergence','NLRB guidance directly specifies six months for its small-cirrhotic exception route; ILTS–ILCA does not specify a duration for the corresponding cirrhotic phenotype. Explant and locally advanced protocol cohorts address different populations.','HB-001;HB091',src)
qfield('icca','iCCA-D11','question','Define how treatment response and the six-month NLRB stability interval are documented; permit early transplant referral while that assessment continues.','HB-001;HB091',src)
# Second-line and conversion assertions must distinguish randomized and single-arm evidence.
src=A+'hepatobiliary/Source_Reviews/ClarIDHy_Audit_Summary.md; 42223137_FIGHT302_partial.md; HB049/HB080/HB081; B13-R12-F01'
field('icca','gates/5/alt/0/order','Choose by molecular target, previous treatment, fitness and treatment goal. ABC-06 provides randomized FOLFOX evidence; ClarIDHy provides randomized IDH1-targeted evidence. NIFTY and NALIRICC provide conflicting randomized phase 2 irinotecan-regimen results. FIGHT-302 compared first-line pemigatinib with GemCis, not the modern chemo-immunotherapy backbone. Cross-trial medians do not establish a sequence.','B13-R12-F01;HB081',src)
field('icca','gates/8/alt/0/pref','ABC-06 compared FOLFOX with active symptom control after cisplatin–gemcitabine: median OS 6.2 versus 5.3 months, adjusted HR 0.69 (95% CI 0.50–0.97), with 12-month survival 25.9% versus 11.4%. ClarIDHy also provides randomized evidence in IDH1-mutant disease; NIFTY and NALIRICC have conflicting phase 2 results. These populations and comparators do not permit ranking by cross-trial survival.','B13-R12-F01',src)
qfield('icca','iCCA-D5','rationale','Evidence includes retrospective incidental-explant series and small prospective protocols for known locally advanced disease, with substantial selection and limited waitlist denominators. The later Houston update included 18 transplanted patients. These data support protocol discussion, not routine transplantation or proof that a particular selection rule is optimal.','B13-R12-F02',A+'hepatobiliary/Source_Reviews/34856069.md; McMillan2022 Results; B13-R11-F01')
# CRLM: initial exception, extensions, local proposal and primary regional nodes are distinct.
src=A+'metastatic_benign/Findings.csv MB024; '+B+'B14_crlm_roadmap/reviews/R12/R12_REPORT.md; NLRB pp9–10'
field('crlm','gates/3/crit/1','Liver-only metastatic disease on CT/MRI and PET/CT for the NLRB exception route, with no extrahepatic disease after primary resection, including nodes outside the primary regional resection field or peritoneal metastases. A history of regional nodes removed with the primary is distinct. Broader clinical/LDLT review requires its own protocol.','MB024;B14-R12-F10',src)
replace('CEA at or below 80 µg/L','CEA below 80 µg/L, with an exact value of 80 requiring explicit review because initial and extension guidance differ','B14-R12-F03',src,'crlm')
replace('a 10% increase in diameter','more than a 10% increase in diameter','B-002',src+'; footnotes20–21','crlm')
# NELM pathology adequacy and selective receptor imaging.
src=A+'metastatic_benign/Clinical_Continuation/Adjudications.csv CC03–05; MB084–085; original pathology/imaging locators retained'
field('nelm','gates/0/crit/0','Biopsy reporting differentiation and a representative Ki-67 index; include a mitotic count when evaluable. Document tissue adequacy and resolve discordance with expert pathology review.','MB084',src)
field('nelm','gates/0/standard/0/t','Obtain expert pathology reporting differentiation and representative Ki-67, with mitoses when evaluable. An adequate small biopsy may be graded with Ki-67 when mitoses cannot be assessed; inadequate or discordant tissue needs review and further sampling if it would change treatment.','MB084',src)
replace('Biopsy with Ki-67 and mitotic count is required before a pathway is assigned','Expert biopsy review with representative Ki-67 and mitoses when evaluable is required before a pathway is assigned; an adequate small biopsy need not be rejected solely because mitoses cannot be counted','MB084',src,'nelm')
replace('All patients at staging and at restaging: it is the gateway to both the analogue and the PRRT decisions, and the EANM consensus judged it necessary at staging of all NET as complementary to conventional imaging.','Use SSTR imaging for staging and when it will change management, including PRRT assessment or discordant progression. Use CT/MRI for routine response surveillance and repeat receptor imaging selectively.','MB085',src,'nelm')
# PRRT evidence and medication instructions.
src=A+'metastatic_benign/Clinical_Continuation/Adjudications.csv CC08; MB087; completed NETTER-2/OCLURANDOM/COMPETE source reports'
replace('The label is wider than the trial: only midgut primaries were enrolled, so the foregut and hindgut indications rest on retrospective and registry data, which is also why EANM declined to recommend PRRT second line for pancreatic NET and why ESMO places it in pancreatic NET only after failure of approved therapies [III, A].','NETTER-1 enrolled progressive midgut NET after SSA. Later randomized studies include selected pancreatic/GI populations (NETTER-2, OCLURANDOM and COMPETE), with different grade, prior-treatment, receptor and product criteria. They do not establish a universal PRRT sequence.','MB087',src,'nelm')
replace('Everything outside midgut rests on retrospective and registry series — which is why EANM declined to recommend PRRT second line for pancreatic NET at all, why ESMO places it in pancreatic NET only after failure of approved therapies [III, A], and why NANETS/SNMMI scores pancreatic use 8 rather than 9.','Later randomized evidence includes selected pancreatic/GI populations in NETTER-2, OCLURANDOM and COMPETE. Apply each trial’s grade, prior-treatment and product criteria; COMPETE excluded functioning GI NET/carcinoid syndrome, which is a trial limitation rather than a universal PRRT contraindication.','MB087;MB088',src,'nelm')
src=A+'metastatic_benign/Findings.csv MB044; current LUTATHERA label §2.3 PDF4; article conflicting24/48-hour instructions'
replace('Octreotide within 48 hours, or octreotide LAR within 28 days, of 177Lu-dotatate can competitively block tumour uptake and reduce efficacy','The LUTATHERA label calls for withholding short-acting octreotide for at least 24 hours and long-acting SSA for at least 4 weeks before each dose; individualized crisis prophylaxis requires a coordinated nuclear-medicine plan','MB044',src,'nelm')
# SSA subgroup numbers and inference.
src=A+'metastatic_benign/Clinical_Continuation/Adjudications.csv CC07; PROMID Tables1–2; CLARINET Figure2'
replace('61% having 10% or less liver involvement','64/85 (75%) having 10% or less liver involvement, including those without liver disease','MB086',src,'nelm')
replace('hazard ratio 0.45 (0.22–0.91) above 25%','hazard ratio 0.45 (0.23–0.88) above 25%','MB086',src,'nelm')
replace("PROMID's effect was concentrated where there was least liver to treat","PROMID's exploratory burden subgroups had imprecise estimates and did not establish a predictive liver-volume threshold",'MB086',src,'nelm')
# Mixed histology: exception size and reclassification kappa.
src=A+'hepatobiliary/Clinical_Continuation.md HB090; NLRB p8; local mixed CPG p2'
replace('a solitary 3 to 5 cm tumour treated with TACE alone and stable for six months','a solitary 3.0 cm tumour treated with TACE alone and stable for six months','HB090',src,'chcca')
replace('requires only locoregional or systemic therapy with six months of stability and sets no such restriction','supports consideration after locoregional or systemic therapy with six months of stability, but only for a solitary tumour ≤3 cm in cirrhosis','HB090',src,'chcca')
replace('requires only locoregional or systemic therapy with six months of stability and imposes neither restriction','supports consideration after locoregional or systemic therapy with six months of stability for a solitary tumour ≤3 cm in cirrhosis; a tumour above 3 cm already falls outside that route','HB090',src,'chcca')
src=B+'B16_chcca_roadmap/reviews/R4/38092727.md; Calderaro2023 pp3–4; B16-R9-001/002'
replace('pathologist agreement with the reference cHCC-CCA diagnosis was kappa 0.19, with inter-observer agreement kappa 0.37, across 405 cases','agreement between the model and pathologist dominant-component reclassification was kappa 0.19, and between two pathologists was kappa 0.37, across 405 already-diagnosed cHCC-CCA cases','B16-R9-001',src,'chcca')
replace('Pathologist agreement with the reference cHCC-CCA diagnosis kappa 0.19, inter-observer agreement kappa 0.37, across 405 cases','Dominant-component reclassification: model versus pathologist kappa 0.19; pathologist versus pathologist kappa 0.37, in 405 cHCC-CCA cases','B16-R9-001',src,'chcca')
replace('Pathologist agreement with the reference cHCC-CCA diagnosis was kappa 0.19 across 405 cases, with inter-observer agreement kappa 0.37.','In 405 cHCC-CCA cases, dominant-component reclassification agreement was kappa 0.19 for model versus pathologist and 0.37 between pathologists; these are not diagnostic-agreement estimates for cHCC-CCA.','B16-R9-002',src,'chcca')
replace('given that the diagnosis is reproduced at kappa 0.19 to 0.37','given sampling limitations and imperfect agreement on dominant-component reclassification','B16-R9-002',src,'chcca')
replace('pathologists agree on the cHCC-CCA diagnosis at kappa 0.19 to 0.37','dominant-component reclassification has kappa 0.19 for model versus pathologist and 0.37 between pathologists','B16-R9-001',src,'chcca')
replace('in an entity where pathologist agreement is kappa 0.19 to 0.37','in an entity with difficult diagnosis and sampling limitations; the reported kappa values concern dominant-component reclassification, not diagnostic agreement','B16-R9-001',src,'chcca')
replace('having been validated against a reference standard the same paper shows to be unreliable at kappa 0.19 to 0.37','with no ground truth for reclassification; model–pathologist kappa was 0.19 and inter-pathologist dominant-component kappa 0.37','B16-R9-001',src,'chcca')
# Save only after all transformations are prepared.
if __name__=='__main__':
 for f,t in texts.items():
  if t!=original[f]:(ROOT/f).write_text(t)
 # Record concise changes as exact manifests, with full old/new pieces rather than whole-file copies.
 out={'id':'2026-11-02-liver-roadmap-audit','requested_by':'Hao Liu: implement verified full-text audit corrections in a new version; Analyst A implementation','status':'Source-supported factual and clinical-scope corrections; OPEN policy decisions remain OPEN. No deployment.','sources':[],'edits':[],'files':edits}
 (ROOT/'tools/clinical_revisions/2026-11-02-liver-roadmap-audit.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
 regs=[]
 for i,e in enumerate(edits):regs.append({'change_id':f'LIVER-{i+1:03d}','finding_id':e['why'].split('; ')[0],'source_locator':e['why'],'file':e['file'],'old':e['old'],'new':e['new']})
 (ROOT/'tools/audit_revision/liver_change_register.json').write_text(json.dumps(regs,ensure_ascii=False,indent=2)+'\n')
 (ROOT/'tools/audit_revision/liver_misses.json').write_text(json.dumps(misses,ensure_ascii=False,indent=2)+'\n')
 print(json.dumps({'patches':len(edits),'files':len({e['file'] for e in edits}),'misses':misses},ensure_ascii=False))
