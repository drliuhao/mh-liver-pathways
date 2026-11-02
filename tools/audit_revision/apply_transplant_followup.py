from pathlib import Path
import json,copy
ROOT=Path(__file__).resolve().parents[2]
rev={'id':'2026-11-02-transplant-followup','date':'2026-11-02','summary':'Complete source definitions, adverse-result action guards, clinical source corrections and builder synchronization.','edits':[],'files':[]}
regfile=ROOT/'tools/audit_revision/transplant_change_register.json'; reg=json.loads(regfile.read_text())
D=json.loads((ROOT/'transplant/assets/content.json').read_text());texts={}
def f(file,old,new,fid,loc):
 s=texts.get(file,(ROOT/file).read_text());assert s.count(old)==1,(file,old[:90],s.count(old));texts[file]=s.replace(old,new,1)
 rev['files'].append({'file':file,'old':old,'new':new});reg['changes'].append({'finding_id':fid,'source_locator':loc,'files':[file],'old':old,'new':new})
def v(path,new,fid,loc):
 h=D
 for k in path[:-1]:h=h[k]
 old=copy.deepcopy(h[path[-1]]);assert old!=new
 rev['edits'].append({'op':'replace_value','path':path,'old':old,'new':new});h[path[-1]]=copy.deepcopy(new)
 reg['changes'].append({'finding_id':fid,'source_locator':loc,'files':['transplant/assets/content.json','tools/v12_content_snapshot.json','transplant/*/index.html'],'content_path':path,'old':old,'new':new})
def walk(x,p=[]):
 if isinstance(x,dict):
  for k,z in x.items():yield from walk(z,p+[k])
 elif isinstance(x,list):
  for k,z in enumerate(x):yield from walk(z,p+[k])
 elif isinstance(x,str):yield p,x
def replace_text(old,new,fid,loc):
 n=0
 for p,t in list(walk(D)):
  if old in t:v(p,t.replace(old,new),fid,loc);n+=1
 print(fid,n)
# Do not allow same-decision hold/redirect actions to bypass a clinical guard.
p='transplant/assets/app.js'
f(p,'function updateDecision(){',"function guardedActions(actions,context){\n return (actions||[]).filter(a=>!context.guard||!a.step||active.steps.findIndex(s=>s.id===a.step)<=stepIndex);\n}\nfunction updateDecision(){",'B08-R7-01–05,18','R7_REPORT §§4,8; source-authored closed boundaries')
f(p,'renderActions(onward.branches[el.dataset.nextBranch])','renderActions(guardedActions(onward.branches[el.dataset.nextBranch],context))','B08-R7-18','Same-decision guard applies to non-advance matches as well as advances')
f(p,"if(actions.length)extra.insertAdjacentHTML('beforeend',`<h5 class=\"next-heading\">Choose the next action</h5>${renderActions(actions)}`);", "if(actions.length)extra.insertAdjacentHTML('beforeend',`<h5 class=\"next-heading\">Choose the next action</h5>${renderActions(guardedActions(actions,context))}`);",'B08-R7-18','R7_REPORT §8; keep backward reassessment and treatment navigation')
p='transplant/assets/risk-routing.js'
f(p,'Transperitoneal biopsy of the primary tumor does not meet the defined standard pCCA protocol. Program review does not waive the OPTN policy requirement.', 'Prior transperitoneal primary-tumor biopsy requires program eligibility review and is outside the local opening protocol. OPTN requires avoiding this biopsy route; review does not imply a policy waiver or automatic eligibility.', 'B04-biopsy source distinction','OPTN 9.5.A(6); AASLD PSC/CCA guidance; B08 R7 §5 element17')
p='assets/clinical-scores.js'
f(p,"{id: 'bclc', name: 'BCLC stage', kind: 'Classification', pages: ['chcca', 'T:hcc']", "{id: 'bclc', name: 'BCLC stage', kind: 'Classification', pages: ['T:hcc']",'B08-R2-F06','BCLC is HCC-specific; R2_REPORT bclc placement audit')
f(p,"['icca', 'Intrahepatic cholangiocarcinoma ≤3 cm in cirrhosis', 'MMaT − 3', 'NLRB guidance']", "['icca', 'iCCA or mixed HCC–iCCA: solitary, biopsy-proven, unresectable, ≤3 cm in cirrhosis; ≥6 months stability after qualifying therapy; no extrahepatic disease', 'MMaT − 3', 'Nonbinding NLRB guidance; all selection and extension criteria apply']",'HB-001,HB091; B08-R4-CF13','NLRB transplant oncology guidance pp7–8; current official PDF checked 2 Nov2026')
f(p,"'OPTN Policy 9.5 · Table 9-10'", "'OPTN Policy 9.5 · Table 9-10; age ≥18 at registration; exception-score floor 15 under 9.4.E'",'C-tools-exception scope','OPTN Table9-10 and9.4.E')
f(p,"['crlm', 'Colorectal liver metastases', 'MMaT − 20; a result below 15 is set to 15', 'NLRB guidance']", "['crlm', 'Colorectal liver metastases', 'MMaT − 20; a result below 15 is set to 15', 'NLRB score recommendation; floor 15 is OPTN Policy 9.4.E. Extensions include CEA <80 ng/mL.']",'C-tools-exception scope; B08-R5','NLRB pp9–10; OPTN9.4.E')
f(p,"options: [['mgdl', 'mg/dL'], ['umol', 'µmol/L']]", "options: [['', 'Choose units'], ['mgdl', 'mg/dL'], ['umol', 'µmol/L']]",'B08-R1-unit safety','ALBI conversion inputs must be explicitly selected; existing formula already rejects missing units')
f(p,"options: [['gdl', 'g/dL'], ['gl', 'g/L']]", "options: [['', 'Choose units'], ['gdl', 'g/dL'], ['gl', 'g/L']]",'B08-R1-unit safety','ALBI conversion inputs must be explicitly selected')
old=next(line for line in (ROOT/p).read_text().splitlines() if 'These are Baveno VII (2022) statements.' in line)
new="      html: () => `<p><b>Reference standard:</b> HVPG ≥10 mmHg in viral and alcohol-related cirrhosis. CSPH raises decompensation risk after HCC resection.</p><p><b>Baveno VIII (2026), compensated advanced chronic liver disease:</b> LSM ≤15 kPa plus platelets ≥150 ×10⁹/L rules out CSPH. Diagnostic criteria, with their individual limitations, are ANTICIPATE/ANTICIPATE-NASH or NICER probability ≥75%; LSM ≥25 kPa for viral/alcohol-related disease or non-obese (BMI &lt;30) MASLD; or spleen stiffness &gt;55 kPa measured at 100 Hz. LSM refers to vibration-controlled transient elastography. Use ANTICIPATE-NASH for MASLD with obesity.</p><p>For indeterminate results, reassessment at 12 months may be preferred (weak recommendation; low-level evidence). <b>HCC limits:</b> noninvasive tests may not apply with macrovascular invasion. The LSM/platelet rule-out applies in BCLC 0–C; ANTICIPATE probability ≥75% is highly suggestive in BCLC 0–A without a right-lobe nodule &gt;5 cm. Apply the clinical and imaging context.</p>${src(pm('42624290', 'Baveno VIII 2026 · statements 1.14–1.17, 1.21–1.23'), pm('35120736', 'Baveno VII · HVPG and resection risk'))}`},"
f(p,old,new,'B08-R1-F01; A B-01','Baveno VIII accepted pre-proof PDF pp16–18 statements1.14–1.17,1.21–1.23; Baveno VII HVPG/resection risk retained')
# The legacy no-JS redirect fallback must not claim a protocol was activated.
for pth in sorted((ROOT/'transplant/high-risk').glob('*/index.html')):
 p=pth.relative_to(ROOT).as_posix();old='Now integrated into the standard protocol.'
 if old in pth.read_text():f(p,old,'High-risk proposals remain OPEN and are not activated.', 'B26-R3-F1/R4-F02/R9-F01','Existing V17/open high-risk status; canonical pathways retain orange labels')
p='tools/build_high_risk.py';f(p,'Now integrated into the standard protocol.','High-risk proposals remain OPEN and are not activated.','B26-status','Preserve status on future legacy-page rebuilds')
# HEHE limited EHD stays closed locally while national case-level review remains visible.
path=['continuations','hehe/stage','branches','2'];x=copy.deepcopy(D['continuations']['hehe/stage']['branches']['2'])
x=[a for a in x if not a.get('step')];x.append({'label':'Review the proposed HEHE extrahepatic-disease boundary','detail':'The local stratum is not activated. NLRB case-level review is a separate question.','step':None,'care':None,'url':'/mh-liver-pathways/transplant/hehe/#high-risk-hehe-b2'})
v(path,x,'B08-R7-04,18','HEHE-B2 local status; NLRB p11 EHD not absolute contraindication; Stacchiotti2021 LT not proposed with EHD')
# Use a source that actually supports post-LT ICI precautions in the separate recurrence resource.
for slug,plans in D['care'].items():
 i=next(i for i,x in enumerate(plans) if x['id']=='post-transplant-recurrence');refs=list(dict.fromkeys(plans[i]['refs']+['H-aasld']))
 if refs!=plans[i]['refs']:v(['care',slug,i,'refs'],refs,'A2-SH-005; B03 ICI-after-LT','AASLD2023 HCC guidance statement49; retain disease-specific follow-up refs')
# Paper summaries: apply only verified, source-specific corrections, preserving each cohort context.
replace_text('KRAS mutation alone was allowed in TransMet (17/47 assigned LT), so a blanket KRAS ban would exceed evidence', 'RAS-mutant disease (including KRAS) was allowed in TransMet (17/47 assigned LT), so a blanket RAS ban would exceed evidence','S5e1bf05cc2; S1e39b45a3f','TransMet2024 Table1; B01/R1/39306468.md')
replace_text('nine had progression-related exclusion/dropout. The control arm included seven subsequent resections and two LT crossovers.', 'nine were not transplanted (five progressed while waiting, three had extrahepatic disease at laparotomy, one had prostate cancer). The control arm included seven resections and two transplants outside protocol; crossover was not allowed.','Sc867c0ab5e','TransMet2024 PDF pp4,7; B01/R1/39306468.md')
replace_text('Median per-protocol PFS was 17.4 versus 6.4 months,', 'Median per-protocol PFS was 17.4 versus 6.4 months (recurrence after LT versus RECIST progression on chemotherapy; PET surveillance differed by arm),','Sc867c0ab5e','TransMet2024 PDF pp4,8; per-protocol, different event definitions')
replace_text("TransMet's nine progression dropouts and three retransplants", "TransMet's nine non-transplanted LT-arm patients (eight progression/extrahepatic disease and one prostate cancer) and three retransplants",'S8a57c05341','TransMet2024 p7, Fig1 vs text; preserve discrepancy rather than reclassifying prostate cancer')
replace_text('Six months: international expert-guidance default, not US policy or a proven biological cliff.', 'Six months: proposed local default informed by German DGVS/DGAV S2k guidance, not US policy, the international EHE consensus, or a proven biological cliff.','Sc3447a32c1','B07-R2/R3; DGVS national guidance; international Stacchiotti2021 gives no six-month interval')
r=D['high_risk']['pathways']['hcc']['reviews'][3];i=next(i for i,x in enumerate(r['evidence']['studies']) if x['key']=='immunoxxl');p=['high_risk','pathways','hcc','reviews',3,'evidence','studies',i]
x=copy.deepcopy(r['evidence']['studies'][i]);x.update(design_population='Prospective single-centre observational cohort: 61 potentially eligible patients treated with atezolizumab–bevacizumab; 16 selected responders were enrolled, listed and transplanted.',selection='Among 45 not included, 25 discontinued treatment (15 progression, four adverse events, six decompensation) and 20 failed downstaging criteria. Eight of 16 had baseline portal-vein tumor thrombosis (six Vp2, one Vp3, one Vp4); 15 had prior locoregional treatment. These were selected research recipients, not proof of standard eligibility after vascular invasion.',results='Median washout 57.5 days (IQR 29–87), median follow-up 16 months. Four biopsy-confirmed acute rejections (25%); three irAEs. Ninety-day morbidity 10/16 and mortality 1/16; two retransplants. Explants: ten complete and six partial responses; one recurrence. Reported two-year OS 94% (95% CI 67–100) and recurrence-free estimate 90% (62–98) in the 16 recipients; Methods start both clocks at listing and censor death for recurrence, so the latter is not conventional recurrence-or-death RFS.',limits='Selected-16 outcomes, not efficacy among all 61 treated patients. Small, observational cohort with short follow-up. A shorter median washout does not establish safety. The fatal course included graft dysfunction, rejection, sepsis and retransplantation; graft loss should not all be attributed to rejection. Supplement and mechanistic analyses were not fully reviewed.',locator='J Hepatol2026;85:117–129. PMID41763363. PDF pp3–5 selection, flow and endpoint definitions; Figures1–3; p8 safety; Table2. Targeted main clinical read; supplement not reviewed.')
v(p,x,'A2-SH-043; S7b3291f222; S09d32f3f7d; S8c137ba9ca','A shared Source_Reviews/41763363_ImmunoXXL_Clinical_Continuation.md; original PDF pp3–5,7–8,Table2')
# Keep the exact source and runtime script copies identical; the old source drift cannot recur.
for name in ['app.js','risk-routing.js','assistant.js','high-risk.js']:
 src='tools/decision_assistant_source/'+name;live='transplant/assets/'+name
 old=(ROOT/src).read_text();new=texts.get(live,(ROOT/live).read_text())
 if old!=new:f(src,old,new,'B08-R7-11','Published reviewed runtime synchronized to source snapshot; retain exact revision record')
# Use the reviewed snapshot when the archived source builder is invoked in this checkout.
p='tools/decision_assistant_source/build.py'
old="HIGH_RISK=json.loads((Path(__file__).parent/'high_risk_data.json').read_text())"
new=old+"\n# The checkout's reviewed content is canonical; legacy Python literals remain as provenance.\nREVIEWED=Path(__file__).resolve().parents[1]/'v12_content_snapshot.json'\nREVIEWED_DATA=json.loads(REVIEWED.read_text()) if REVIEWED.exists() else None\nif REVIEWED_DATA:\n    PATHWAYS[:]=REVIEWED_DATA['index']; SOURCES.clear(); SOURCES.update(REVIEWED_DATA['sources'])\n    ASSISTANTS.clear(); ASSISTANTS.update(REVIEWED_DATA['assistants'])\n    CARE.clear(); CARE.update(REVIEWED_DATA['care'])\n    HIGH_RISK=REVIEWED_DATA['high_risk']\n"
f(p,old,new,'B08-R7-11','Builder reads the versioned reviewed snapshot; legacy source is not silently restored')
old="              care=CARE,continuations=build_continuations(PATHWAYS,ASSISTANTS))"
f(p,old,old+"\n    if REVIEWED_DATA: base=REVIEWED_DATA",'B08-R7-11','Rebuild uses reviewed continuations and clinical revisions')
old='    continuations=build_continuations(PATHWAYS,ASSISTANTS)'
f(p,old,"    continuations=REVIEWED_DATA['continuations'] if REVIEWED_DATA else build_continuations(PATHWAYS,ASSISTANTS)",'B08-R7-11','Validation uses the same reviewed data as the builder')
(ROOT/'tools/clinical_revisions'/f"{rev['id']}.json").write_text(json.dumps(rev,ensure_ascii=False,indent=2)+'\n');reg['revision_ids']=[reg['revision_id'],rev['id']];regfile.write_text(json.dumps(reg,ensure_ascii=False,indent=2)+'\n')
print('Prepared',len(rev['files']),'script records',len(rev['edits']),'content edits')
