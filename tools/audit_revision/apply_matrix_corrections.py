"""Apply the reconciled B09/B10 clinical corrections; preserve exact before/after records.

Source dossiers live in the frozen 2026-10-31 review package. This is a curated
revision, not an automatic application of all reviewer flags.
"""
import copy, json
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'tools/audit_revision'
register = []
original = {}

def read(name):
    original[name] = (ROOT / name).read_text()
    return json.loads(original[name])

def setv(obj, path, value, source, batch='B09'):
    parent = obj
    for key in path[:-1]: parent = parent[key]
    old = parent[path[-1]]
    if old == value: return
    parent[path[-1]] = value
    register.append(dict(batch=batch, path=path, old=old, new=value, source_locator=source))

x = read('lrt/matrix.json')
def l(path, value, source): setv(x, path, value, source)
def cell(key, field, value, source): l(['cells',key,field],value,source)
def role(key,n,field,value,source): l(['cells',key,'roles',n,field],value,source)
def ev(key,n,k,value,source): l(['cells',key,'roles',n,'ev',k,2],value,source)

l(['tiers','2','label'],'Curative-intent alternative — selection and evidence depend on tumor type and the reference treatment','B09 R11; avoid making ablation an alternative only when ablation is infeasible')
role('hcc|sbrt',0,'when','Single HCC ≤5 cm with suitable liver reserve; Xi randomized ablation-eligible recurrent HCC. Difficult ablation anatomy is a separate clinical reason to consider SBRT.','PMID 39693584 PDF p2, p5, Fig4; 26628466 retrospective anatomy/size comparison')
ev('hcc|sbrt',0,0,'Recurrent HCC: 2-y local PFS 92.7 vs 75.8%; OS HR 0.91 (0.37–2.22), not an equivalence result','PMID 39693584 p4, Fig2')
ev('hcc|sbrt',1,0,'ITT dropout 16.7%; nonrandomized comparison with TACE/RFA','PMID 28257902; B09 R2 cohort comparison')
ev('hcc|abl',3,0,'Nonrandomized bridge comparison; no significant dropout difference from TACE/SBRT','PMID 28257902; not an equivalence trial')
ev('hcc|sbrt',2,0,'Neoadjuvant 3D-CRT, not SBRT: HCC-death HR 0.47 (univariable ITT); 9/82 did not reach surgery','PMID 31283409 p3, Table A4 pp17–18')
ev('hcc|sbrt',2,1,'Conventional RT vs TACE: intrahepatic recurrence 20.8 vs 52.1%; extrahepatic 37.5 vs 14.6%; PFS/OS not significantly different','PMID 38488934 pp6–8, Table2; exploratory recurrence patterns')
role('hcc|sbrt',3,'when','Separate trial settings: salvage after incomplete TACE; first-line alternative to TACE; or vascular invasion with systemic treatment','PMIDs 36421345,37037359,39699905,29543938; populations must not be pooled')
ev('hcc|sbrt',3,1,'TACE-eligible small HCC: primary TTP not improved; local-control signal post hoc; n=28, closed early','PMID 37037359 p2 eligibility and results')
ev('hcc|sbrt',3,2,'SBRT→sorafenib vs sorafenib: OS 15.8 vs 12.3 mo; HR 0.77 (90% CI 0.59–1.01), primary P=.06','PMID 39699905 pp3–5, primary analysis')
l(['cells','hcc|sbrt','roles',3,'ev',3,0],'Yoon RCT','PMID 29543938; START is not the published trial name')
ev('hcc|sbrt',3,3,'Macrovascular invasion: TACE+EBRT vs sorafenib; 91% crossover from sorafenib','PMID 29543938; B09 R2')
ev('hcc|y90',1,0,'TTP >26 vs 6.8 mo vs cTACE; OS not significantly different; stopped at 45/124','PMID 27575820; B09 R3')
ev('hcc|y90',1,1,'OS 30.2 vs 15.6 mo vs DEB-TACE; phase II trial stopped early','PMID 35258371; B09 R3')
ev('hcc|y90',1,2,'No significant Y90–TACE difference in downstaging; observational, not equivalence evidence','PMID 34331914; B09 R3')
ev('hcc|y90',2,3,'Personalized vs standard Y90 dosimetry: ORR 71 vs 36%; not a Y90–sorafenib comparison','PMID 33166497; B09 R3')
role('hcc|tace',3,'when','Embolization-eligible HCC without macrovascular invasion; TACE–systemic combinations require separate selection and guideline review','PMIDs 39798579,39798578; BCLC2026 does not establish routine combination use')
ev('hcc|tace',3,2,'Durvalumab+bevacizumab+TACE: PFS 15.0 vs 8.2 mo; PFS benefit does not establish OS benefit; Child-Pugh A–B7','PMID 39798579 eligibility/results')
ev('hcc|tace',3,3,'Lenvatinib+pembrolizumab+TACE: PFS 14.6 vs 10.0 mo; OS not significant; grade ≥3 toxicity 71 vs 32%; Child-Pugh A','PMID 39798578 eligibility/results')
role('hcc|hai',0,'when','Large unresectable HCC: vascular-invasion eligibility differs by trial; Li 2021 excluded macrovascular invasion','PMIDs 34905388,31070690,34648352; B09 R4')
role('hcc|hai',2,'when','Adjuvant HAIC-FOLFOX after R0 resection for histological microvascular invasion, without macrovascular invasion','PMID 36525610 pp2–3')
role('icca|sbrt',0,'when','Localized unresectable iCCA; ablative dose subject to organ constraints. Tao compared BED >80.5 Gy with ≤80.5 Gy.','PMID 26503201 dose-group definition')
ev('icca|abl',0,1,'Retrospective matched cohort: no significant OS difference from repeat resection; not equivalence evidence','PMID 41528222; B09 R8')
cell('icca|y90','head','Selected chemo–Y90 control/conversion; substantial cirrhosis-related toxicity','PMID 31670746 pp3–4,7')
role('icca|y90',0,'when','Unresectable iCCA, predominantly hepatic; MISPHEC allowed limited extrahepatic disease. Avoid extrapolation to routine chemo–Y90 in cirrhosis.','PMID 31670746 p2 eligibility, p7 recommendation')
ev('icca|y90',0,0,'GemCis+Y90, single arm: median OS 22 mo; hepatic failure 9/12 with cirrhosis vs 5/29 without','PMID 31670746 pp3–4; no randomized comparison')
role('icca|hai',0,'when','Unresectable liver-confined iCCA ± selected resectable regional nodes; systemic-treatment plan required. Pump FUDR evidence is distinct from pCCA catheter GemCis plus I-125 stents.','B09 source/population distinction; punctuation repair')
ev('crlm|abl',0,0,'Early-stop trial: OS HR 1.05 (95% CI 0.69–1.58); CI crosses the 1.30 noninferiority margin; AEs 19 vs 46%','PMID 39848272 pp1–2; retain design and uncertainty')
role('crlm|sbrt',0,'when','Selected limited metastases when surgery/ablation is unsuitable; Rusthoven studied 1–3 lesions each <6 cm in a mixed-primary cohort','PMID 19255321 p2; 15/47 colorectal')
ev('crlm|sbrt',0,2,'Mixed-primary oligometastases: 5-y OS 42.3 vs 17.7%; not a CRLM-only estimate','PMID 32484754; B09 R5')
role('crlm|y90',0,'when','Previously treated liver-only disease in these trials; EPOCH excluded confirmed extrahepatic metastases','PMIDs 34541864,20567019 eligibility')
ev('crlm|y90',0,0,'PFS 8.0 vs 7.2, hepatic PFS 9.1 vs 7.2 mo; OS not significant; grade ≥3 AEs 68.4 vs 49.3%','PMID 34541864; B09 R5')
role('crlm|tace',0,'when','Selected salvage discussion; Fiorentini studied liver-only disease in a small historical trial','PMID 22493375; comparator/population limit')
role('crlm|hai',0,'when','Adjuvant after resection: expert-center discussion. Dutch PUMP did not establish PFS benefit in its low-risk population; pump FUDR is distinct from pCCA catheter therapy.','PMID 28426374; primary PUMP abstract reconciled by A on 1 Nov')
ev('crlm|hai',0,1,'Propensity-score quartile-adjusted OS HR 0.67; retrospective association, not matching or randomized benefit','PMID 28426374 pp2–4, Appendix A1')
cell('nelm|abl','tier',4,'PMIDs 17629995,21134563; reported cohorts support cytoreduction/control, not comparative cure')
cell('nelm|abl','head','Selected local control / cytoreduction; case-series evidence','PMIDs 17629995,21134563')
role('nelm|abl',0,'t',4,'B09 R9: treatment intent is cytoreduction/control')
role('nelm|abl',0,'when','Selected unresectable progressive or symptomatic NELM; cited laparoscopic RFA series included multifocal disease and did not test combined resection','PMIDs 17629995 p10–12;21134563 p2')
ev('nelm|abl',0,0,'Local recurrence 6.3% per lesion (11% per patient); median OS 3.9 y after RFA; hepatic progression elsewhere common','PMID 17629995 pp13–15')
role('nelm|abl',1,'t',4,'B09 R9; symptom control is not a bridge-to-surgery endpoint')
ev('nelm|tace',0,1,'NANETS 2025 abstract: hepatic PFS difference not significant, not equivalence; PMID links the protocol, not results','PMID 30016989 protocol; abstract not full paper. Remove unsupported abstract medians.')
ev('pcca|sbrt',0,0,'287-patient retrospective series; 5-y ITT OS 53% from presentation; post-LT recurrence-free survival 65%; 25% pre-LT dropout. No isolated RT effect.','PMID 22504095; B09 R10')
ev('pcca|sbrt',0,2,'26 recipients: 12 GemCis-only vs 14 RT-containing; recurrence 6/12 vs 3/14. No significant OS/RFS difference; no equivalence or ITT benefit established.','PMID 39936132; B09 R10')

for key in ['hcc|htx','crlm|htx']:
    if key=='hcc|htx': role(key,0,'when','Up to 3 treated tumors <3 cm with an adequate acoustic window; trial / registry assessment','PMID 39225612; treated targets, not total lesion count')
l(['contra','abl','items',0],'Selection depends on tumor type, size, number and achievable margin; strongest small-tumor evidence is generally ≤3 cm. MWA ≤5 cm is not a universal curative threshold.','PMID 32382856 Tables1–2, pp3–4')
l(['contra','abl','items',2],'Central bile duct proximity: thermal-injury risk; specialized duct protection may change feasibility','PMID 32382856 Table3; duct-cooling exception')
l(['contra','abl','items',6],'Uncorrectable bleeding risk, ascites along the needle path or poor liver reserve: assess individually with IR; use procedure- and liver-disease-specific thresholds','PMID 32382856; remove unsupported universal INR/platelet/Child cutoffs')
l(['contra','sbrt','items',0],'Insufficient uninvolved liver to meet the dose/fractionation plan; baseline liver dysfunction increases risk. A bare 700-mL volume is not a universal validated cutoff.','PMID 29482870 p9; HyTEC could not validate 700-cm3 rule')
l(['contra','sbrt','items',4],'Large or multifocal targets: feasibility depends on normal-liver and adjacent-organ dose constraints','PMID 29482870; no universal 6–8cm prohibition')
l(['contra','y90','items',0],'Excess lung shunting: calculate absorbed lung dose and apply the selected device instructions and cumulative exposure limits','PMID 36114872; numerical device limits not in this source')
l(['contra','y90','items',2],'Decompensated liver disease, elevated bilirubin or poor performance: assess reserve, treatment volume and device-specific selection','PMID 36114872; HCC/glass guidance is not a universal all-tumor cutoff')
l(['contra','y90','items',5],'PVTT is not automatically prohibitive; extent, targeting, portal flow and liver reserve determine feasibility','PMID 36114872 Tables4,7')
l(['contra','y90','items'],x['contra']['y90']['items']+['GemCis with Y90 in cirrhotic iCCA: MISPHEC reported hepatic failure in 9/12; avoid routine extrapolation (PMID 31670746).'],'PMID 31670746 pp3–4,7')
l(['contra','tace','items',0],'Portal-vein obstruction or hepatofugal flow requires IR review. CIRSE lists neoplastic PVT as an absolute contraindication; selected alternative practice needs an explicit rationale.','PMID 34694454 contraindications; do not silently turn source attribution into new local blanket rule')
l(['contra','tace','items',1],'Decompensated cirrhosis, ascites or encephalopathy; CIRSE lists Child-Pugh ≥B8 and ECOG ≥2 as absolute contraindications','PMID 34694454 Table of contraindications')
l(['contra','tace','items',2],'Extensive liver replacement or marginal reserve: thresholds are tumor- and protocol-specific; >50% is not a universal contraindication','B09 R7; NCCN NET burden differs; retain individualized IR selection')
l(['contra','tace','items',5],'DEB-TACE in NELM: biliary injury/biloma concern (Bhagat, PMID 22722717); not attributed to CIRSE alone','PMID 22722717; B09 R7')
l(['contra','hai','items',2],'Unrelieved biliary obstruction, active infection or inability to tolerate pump surgery: clinical safety review','B09 R7; reasonable clinical safeguards, not quoted toolkit requirements')
l(['contra','hai','items',4],'Prior liver-directed radiation: expert review of hepatic reserve, perfusion and sequencing; prior TARE is a program-selection consideration','PMID 39962001; remove unspecified NCCN restriction')
l(['contra','htx','items',3],'Outside pivotal evidence: more than 3 treated targets or target size ≥3 cm; total liver lesion count is a separate assessment','PMID 39225612; treated target eligibility')
l(['contra','htx','items'],x['contra']['htx']['items']+['Biliary instrumentation or limited liver reserve: individualized safety assessment; the pivotal study does not establish safety in these groups.'],'PMID 39225612; B09 R7')
l(['notes',1],'Cell color and number describe clinical role, not evidence grade. Chips include other roles and cautions; numbers beside studies are PubMed IDs.','B09 R11 role vs evidence hierarchy')
l(['notes',4],'Dutch adjuvant PUMP (ASCO LBA3506), EA2222 (unresectable CRLM) and iCCA PUMP-2 are distinct trials. PUMP is an abstract with OS immature; do not extrapolate its low-risk resectable population to conversion treatment. HAI does not establish MELD exception or transplant eligibility.','A PUMP_and_ClarIDHy_Verification.md; rejected conflicting secondary report')
l(['notes',5],'pCCA is assessed separately from iCCA. No standalone local modality has established curative equivalence to resection or protocol transplantation for primary pCCA.','User removed biliary-directed panel; retain disease-specific distinction')

y=read('systemic/matrix.json'); cards={c['id']:c for c in y['cards']}
def s(cid,field,value,source): setv(y,['cards',y['cards'].index(cards[cid]),field],value,source,'B10')
s('hcc-single-ici','limits','Guideline options and US indications differ: durvalumab monotherapy is not the labelled HCC regimen; the HCC label specifies combination treatment. KEYNOTE-240/394 are later-line studies, not first-line superiority evidence.','B26 drug-label finding; B10 R1/R2; durvalumab indication')
s('hcc-tki','evidence','REFLECT: lenvatinib vs sorafenib OS 13.6 vs 12.3 months; noninferiority design. SHARP: sorafenib vs placebo OS 10.7 vs 7.9 months, HR 0.69 (0.55–0.87); radiologic time to progression 5.5 vs 2.8 months, not PFS.','PMIDs 29433850,18650514; B10 R1/R2')
s('hcc-tki','limits','REFLECT enrolled Child-Pugh A, ECOG 0–1 and excluded main portal-vein invasion, ≥50% liver occupation and obvious bile-duct invasion. SHARP reported grade 3 diarrhea and hand–foot reaction of 8% each with sorafenib; these are not lenvatinib toxicity rates. Little evidence supports use in decompensated cirrhosis.','PMID 29433850 eligibility;18650514 safety')
s('hcc-adjuvant','who','No residual HCC after resection or ablation; IMbrave050 enrolled patients at high recurrence risk.','PMIDs 37871608,41580093 trial eligibility')
s('hcc-adjuvant','evidence',cards['hcc-adjuvant']['evidence']+' Updated OS HR 1.26; immature survival data do not establish benefit or harm.','PMID 41580093 update; B10 R1')
s('hcc-tace-combination','who','TACE-eligible unresectable HCC: eligibility differs by regimen. LEAP-012 and EMERALD-3 mainly required Child-Pugh A; EMERALD-1 allowed B7. Evaluate current guideline position and competing curative options.','PMIDs 39798579,39798578,42636832')
s('hcc-tace-combination','limits','PFS benefit is not proof of OS benefit or a transplant bridge. LEAP-012 grade ≥3 treatment-related toxicity was 71% vs 32%; EMERALD-3 grade 3–4 treatment-related toxicity was 63% vs 19%. EMERALD-1 durvalumab without bevacizumab did not improve PFS.','PMIDs 39798578,42636832 Table3,39798579')
s('crlm-conversion','who','For fit patients when shrinkage may enable complete local treatment; CAIRO5 triplet evidence applies to right-sided or RAS/BRAF-mutant disease. Reassess resectability with the liver multidisciplinary team.','PMID 37329889 eligibility')
s('crlm-conversion','evidence',cards['crlm-conversion']['evidence']+' TRICE did not meet its primary endpoint; grade ≥3 neutropenia increased. CAIRO5 long-term OS was not significantly improved (HR 0.90).','PMIDs 38728364,39570583; long-term report')
s('crlm-msi','evidence','KEYNOTE-177: pembrolizumab PFS 16.5 vs 8.2 months with chemotherapy; final OS superiority was not statistically established. CheckMate 8HW: first-line nivolumab–ipilimumab improved PFS vs chemotherapy; the separate PFS HR 0.62 comparison vs nivolumab pools treatment lines.','PMIDs 33264544,39602630,39874977 pp4,8–10')
s('crlm-other-targets','evidence','MOUNTAINEER final: tucatinib–trastuzumab ORR 39.3%, median response duration 15.2 months in HER2-positive, RAS-wild-type CRC. CodeBreaK 300, corrected 2025: sotorasib 960 mg–panitumumab PFS 5.6 vs 2.0 months, HR 0.48 (0.30–0.78), vs trifluridine–tipiracil or regorafenib. KRYSTAL-1: adagrasib–cetuximab ORR 34% in 94 patients.','PMIDs 41526345 p3,37870968 corrected Table2,38587856; erratum39938112')
s('crlm-other-targets','limits','MOUNTAINEER randomized combination vs tucatinib alone in cohorts B/C, with crossover, but had no powered standard-care survival comparison and excluded prior HER2 therapy. KRYSTAL-1 was single-arm. CodeBreaK 300 improved PFS; OS superiority was not established. Do not rank these different molecular populations by response or survival.','PMID41526345 p8;37870968 p13;40215429 OS')
s('crlm-refractory','evidence','SUNLIGHT: trifluridine–tipiracil+bevacizumab vs trifluridine–tipiracil OS 10.8 vs 7.5 months, HR 0.61; PFS 5.6 vs 2.4 months. FRESCO-2: fruquintinib vs placebo/supportive care OS 7.4 vs 4.8 months, HR 0.66; PFS 3.7 vs 1.8 months. CORRECT: regorafenib improved OS vs placebo in its separate refractory population.','PMIDs37133585 pp5–7,37331369,23177514; remove duplicated/unlabelled SUNLIGHT data')
s('crlm-refractory','limits','Separate trials do not rank these options. SUNLIGHT grade ≥3 adverse events were 72.4% vs 69.5%, including grade 3–4 neutropenia 43.1% vs 32.1%. FRESCO-2 grade ≥3 adverse events were 63% vs 50%. These are refractory-treatment studies, not preferred conversion or transplant regimens.','PMIDs37133585 Table2,37331369')
s('net-prrt-first','position','Newly diagnosed well-differentiated GEP-NET; Ki-67 10–55%; SSTR-positive','PMID38851203; avoid extending trial to all G2')
s('net-prrt','limits',cards['net-prrt']['limits']+' NETTER-1 enrolled midgut NET; its numerical results are not pancreatic-NET-specific estimates.','PMIDs28076709,34793718')
s('net-emerging','who','OCLURANDOM: pretreated progressive SSTR-positive pancreatic NET. COMPETE: progressive SSTR-positive G1/G2 GEP-NET; functioning GI NET and prior PRRT/mTOR therapy were excluded.','PMIDs42225102,42392118 eligibility; A focused continuation')
s('v12-pdac-daraxonrasib-current-us-option','setting','later','B10 R9; trial previously treated, retain broader FDA indication in eligibility text')
s('v12-pdac-daraxonrasib-current-us-option','position','Subsequent treatment; broader label includes patients unfit for multiagent therapy','FDA26Aug2026; A Current_FDA_and_eCFR_2026-11-01.md')
for cid in cards:
    for field in ['transplant']:
        if 'initial V7' in cards[cid][field]: s(cid,field,cards[cid][field].replace('initial V7','proposed local opening'),'B25/B26 obsolete version label; no policy change')
setv(y,['safety',1,2],'Bevacizumab: withhold at least 28 days before elective surgery and for at least 28 days after major surgery, until adequate healing. Review perforation, fistula, arterial thrombosis and bleeding risks. Other VEGF agents have different intervals.',['Bevacizumab prescribing information sections2.1,5.1–5.5'],'B10')
setv(y,['safety',3,1],y['safety'][3][1].replace('Correct active infection and major organ dysfunction before treatment.','Stabilize active infection and assess organ dysfunction; dose adjustment or a different regimen may be needed rather than normalization of every test.'),'A focused targeted-label review; avoid blanket requirement','B10')
setv(y,['safety',5,2],'Review cumulative marrow and radiation exposure with nuclear medicine when sequencing PRRT and alkylators; NETTER-1 did not establish an optimal or universally safe sequence.','B10 PRRT source attribution','B10')

for name,data in [('lrt/matrix.json',x),('systemic/matrix.json',y)]:
    (ROOT/name).write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
    for entry in register:
        entry.setdefault('file',name if (entry['batch']=='B09')==(name.startswith('lrt')) else '')

# Produce text-replay entries for source guards. Preserve prior whitespace in the
# canonical file; exact JSON string/object replacements avoid ambiguous short tokens.
files=[]
for name,data in [('lrt/matrix.json',x),('systemic/matrix.json',y)]:
    new=(ROOT/name).read_text()
    files.append(dict(file=name,old=original[name],new=new,why='Curated B09/B10 corrections with per-field source locators in tools/audit_revision/matrix_change_register.json'))
(ROOT/'tools/clinical_revisions/2026-11-02-matrices.json').write_text(json.dumps(dict(id='2026-11-02-matrices',requested_by='Hao Liu: implement reconciled audit and publish two editions',sources=[],edits=[],files=files),ensure_ascii=False,indent=2)+'\n')
for r in register:r['file']='lrt/matrix.json' if r['batch']=='B09' else 'systemic/matrix.json'
(OUT/'matrix_change_register.json').write_text(json.dumps(register,ensure_ascii=False,indent=2)+'\n')
print(f'{len(register)} reconciled matrix field corrections')
