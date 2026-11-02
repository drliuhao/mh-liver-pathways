"""Apply the source-checked, bounded Analyst A roadmap corrections.

The generated manifest is the exact replay record used by source-preservation
tests. This helper changes only the six assigned roadmap families.
"""
import copy, difflib, json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SLUGS = ['adenoma', 'incidental', 'pdac', 'pnet', 'pcyst', 'ampullary']
DOC_SLUG = {'adenoma':'hca'}
FILES = [f'{s}/data/{n}.json' for s in SLUGS for n in ['pathway', 'critique']]
FILES += [f'tools/consensus_source/roadmap_{s}.json' for s in SLUGS]
FILES += [f'documents/{DOC_SLUG.get(s,s)}/questions.json' for s in SLUGS]
original = {f:(ROOT/f).read_text() for f in FILES}
data = {f:json.loads(s) for f,s in original.items()}
changes=[]
shared=[]

def walk(obj, path=()):
    if isinstance(obj, dict):
        for k,v in list(obj.items()):
            yield from walk(v, path+(k,))
    elif isinstance(obj, list):
        for i,v in enumerate(obj):
            yield from walk(v, path+(i,))
    else:
        yield path,obj

def put(obj, path, value):
    for k in path[:-1]: obj=obj[k]
    obj[path[-1]]=value

def get(obj, path):
    for k in path: obj=obj[k]
    return obj

def log(file,path,old,new,ids,source):
    changes.append({'file':file,'path':'/'+ '/'.join(map(str,path)), 'finding_ids':ids, 'source_locator':source, 'old':old,'new':new})

def sub(old,new,ids,source,slugs=None,required=True):
    n=0
    for f,obj in data.items():
        if slugs and not any(f.startswith(s+'/') or f==f'tools/consensus_source/roadmap_{s}.json' or f.startswith(f'documents/{DOC_SLUG.get(s,s)}/') for s in slugs):continue
        for path,v in walk(obj):
            if isinstance(v,str) and old in v:
                nv=v.replace(old,new);put(obj,path,nv);log(f,path,v,nv,ids,source);n+=1
    if required and not n: raise ValueError('No match: '+old)
    return n

def setp(slug,path,new,ids,source,kind='pathway',propagate=True):
    f=f'{slug}/data/{kind}.json'
    holder=data[f];parts=[]
    for k in path.split('.'):
        k=int(k) if isinstance(holder,list) else k;parts.append(k);holder=holder[k]
    path=tuple(parts)
    old=get(data[f],path)
    if old==new:return
    # Exact matching duplicate strings are always updated together.
    if isinstance(old,str) and propagate: sub(old,new,ids,source,slugs=[slug])
    else:put(data[f],path,new);log(f,path,old,new,ids,source)

def append(slug,path,new,ids,source):
    f=f'{slug}/data/pathway.json';path=tuple(int(k) if k.isdigit() else k for k in path.split('.'))
    old=get(data[f],path);nv=copy.deepcopy(old)+[new];put(data[f],path,nv);log(f,path,old,nv,ids,source)

def addref(slug,pmid,record,ids,source):
    refs=data[f'{slug}/data/pathway.json']['refs']
    if pmid not in refs:
        refs[pmid]=record;log(f'{slug}/data/pathway.json',('refs',pmid),None,record,ids,source)
        shared.append({'type':'source_summary','slug':slug,'pmid':pmid,'source_locator':source,'requested':'Add/verify compact evidence line or source summary for this reference in the shared evidence library.'})

PA='Full_Text_Review_2026-10-31/Analyst_A_Full_Reaudit_2026-11-01/reviews/pancreatic_ampullary/Source_Reviews/'
MB='Full_Text_Review_2026-10-31/Analyst_A_Full_Reaudit_2026-11-01/reviews/metastatic_benign/Source_Reviews/'
B='Full_Text_Review_2026-10-31/Analyst_B/batches/'

# Pancreatic cyst fluid and high-risk interpretation.
src=PA+'PMID_16111956.md; van der Waaij 2005, PDF pp2–5, Tables 2 and 4; European 2018 §1.1'
sub('Amylase under 250 U/L — rules in a collection','Amylase under 250 U/L — makes a pseudocyst unlikely',['PA-001','S4d6221d133'],src,['pcyst'])
sub('amylase rules in a collection','low amylase makes a pseudocyst unlikely; high amylase alone is nonspecific',['PA-001'],src,['pcyst'])
sub('Amylase below 250 U/L effectively excludes it (sensitivity 44%, specificity 98%).','Amylase below 250 U/L makes a pseudocyst unlikely. In the pooled study, low amylase identified non-pseudocyst lesions with 44% sensitivity and 98% specificity; high amylase alone does not establish a pseudocyst.',['PA-001'],src,['pcyst'])
sub('a cyst fluid amylase above 250 U/L and no epithelium','compatible cyst-fluid findings and no epithelium; an amylase above 250 U/L is nonspecific',['PA-001'],src,['pcyst'])
sub('Treat on symptoms; amylase under 250 U/L rules it out','Treat on symptoms; amylase under 250 U/L makes pseudocyst unlikely',['PA-001'],src,['pcyst'])
setp('pcyst','quickref.2.rows.3.1','Low amylase identifies non-pseudocyst lesions: sensitivity 44%, specificity 98% (155 patients with amylase data in a 12-study pooled analysis excluding IPMN). High amylase alone is nonspecific.',['PA-001'],src)
src=PA+'PMID_37230894.md; Pflüger 2023, PDF p4 and Figure 5/p7; PMID_38182527.md, Kyoto PDF p9'
setp('pcyst','gates.4.standard.0.opts.3.pref','Confident imaging diagnosis, with fluid testing when uncertainty would change management. In the multi-institutional PancreaSeq study, VHL alterations alone had 71% sensitivity and 100% specificity for serous cystadenoma in the small surgically verified subgroup. The commissioned biomarker meta-analysis reported pooled VHL sensitivity 56% (95% CI 33–78%) and specificity 99% (99–100%) across four studies and 1,140 cysts. Kyoto transposes the latter metric: a negative VHL result does not exclude a serous cystadenoma.',['PA-015','S1a6cff6f43'],src)
addref('pcyst','37230894',['Cyst-fluid biomarkers meta-analysis','Pflüger 2023','Pflüger MJ, et al. Predictive ability of pancreatic cyst fluid biomarkers: a systematic review and meta-analysis. Pancreatology. 2023;23:868–877. doi:10.1016/j.pan.2023.05.005. PMID:37230894.'],['PA-015'],src)
g=data['pcyst/data/pathway.json']['gates'][4]['standard'][0]['opts'][3]
setp('pcyst','gates.4.standard.0.opts.3.refs',list(dict.fromkeys(g.get('refs',[])+['37230894'])),['PA-015'],src,propagate=False)
src=PA+'PMID_38182527.md; Kyoto original PDF p6 §5.2 and p7 Figure 3'
setp('pcyst','gates.1.standard.0.t','Obtain surgical assessment for a high-risk stigma: obstructive jaundice with a head cyst, an enhancing mural nodule ≥5 mm or solid component, main pancreatic duct ≥10 mm, or cytology suspicious or positive for high-grade dysplasia or carcinoma. Consider resection when clinically appropriate after assessing fitness, comorbidity, life expectancy and preference.',['PA-016'],src)
sub('an absolute surgical indication','a high-risk stigma for clinically appropriate surgical assessment',['PA-016'],src,['pcyst'],False)
setp('pcyst','gates.7.alt.1.avoid','Kyoto 2024 Figure 3 includes young, surgically fit patients among those in whom surgery may be considered. This is an individualized discussion, not a mandate to resect solely for age or cyst size. No randomized comparison establishes that early resection is better than continued surveillance in young patients; weigh cumulative cancer risk, operative harm and long-term pancreatic function.',['B21-Kyoto-young-fit'],src)

# PDAC: essential staging information, conditional preparation, and parallel testing.
src=PA+'PMID_NCCN-PDAC-v3.2026.md; original PDF pp10–11,29–32,37,89,95 (targeted original-guideline review)'
setp('pdac','gates.0.crit.0','High-quality pancreas-protocol contrast CT (preferred) or contrast MRI adequate to assess the primary, vessels and liver',['PA-022','PA-023'],src)
setp('pdac','gates.0.crit.1','Chest imaging and appropriate abdomen/pelvis assessment to complete staging',['PA-023'],src)
setp('pdac','gates.0.crit.2','Liver tests and CA 19-9 interpreted with bilirubin; when drainage is indicated, reassess CA 19-9 after decompression',['PA-023'],src)
setp('pdac','gates.0.crit.3','Germline testing offered for confirmed pancreatic cancer in parallel with care; an unfinished result does not prevent initial review',['PA-023'],src)
setp('pdac','gates.0.crit.4','Before planned surgery, review whether imaging remains current; acquisition within four weeks is preferred, not an absolute prerequisite for initial assessment',['PA-023'],src)
setp('pdac','gates.0.standard.0.t','Obtain adequate pancreas-protocol cross-sectional imaging when the referral study cannot stage the tumour: contrast CT is preferred, and high-quality contrast MRI is an accepted alternative.',['PA-022'],src)
sub('NCCN sets an outer limit of 4 weeks between the staging CT and the operation.','NCCN prefers imaging within four weeks of surgery; reassess timing in context rather than using it as an absolute initial-review exclusion.',['PA-023'],src,['pdac'])
setp('pdac','gates.0.alt.0.t','Use high-quality pancreas-protocol contrast MRI as an alternative to CT when appropriate, and as a problem-solving study for indeterminate findings.',['PA-022'],src)
setp('pdac','gates.0.alt.0.avoid','Ensure the MRI adequately assesses arterial and venous relationships and distant disease. If both iodinated and gadolinium contrast are contraindicated, individualize noncontrast imaging and supplementary assessment with radiology.',['PA-022'],src)
setp('pdac','gates.0.standard.3.pref','Measure baseline CA 19-9 with the bilirubin recorded. If drainage is indicated, prefer reassessment after adequate decompression and improvement in bilirubin. A predrainage value may still be obtained, with its limited interpretation documented. Use serial values alongside imaging and clinical response.',['PA-023'],src)
setp('pdac','gates.2.standard.2.t','When a jaundiced patient needs both tissue sampling and biliary drainage, consider EUS biopsy and ERCP during the same anaesthesia session.',['PA-023'],src)
setp('pdac','gates.2.avoid.0.t','Do not interpret a CA 19-9 measured during obstructive jaundice as an unconfounded tumour baseline.',['PA-023'],src)
sub('CA 19-9 and liver function drawn after biliary decompression, not before','Liver tests and CA 19-9 interpreted with bilirubin; drainage is conditional and does not precede all laboratory testing',['PA-023'],src,['pdac'],False)

# Public speculative PDAC transplant questions: removal requested by the user.
for f,obj in data.items():
    if 'pdac' not in f:continue
    def remove_questions(o,path=()):
        if isinstance(o,dict):
            for k,v in list(o.items()):
                if isinstance(v,list) and any(isinstance(x,dict) and x.get('id') in ['PDAC-B1','PDAC-B2'] for x in v):
                    nv=[x for x in v if not(isinstance(x,dict) and x.get('id') in ['PDAC-B1','PDAC-B2'])]
                    log(f,path+(k,),v,nv,['PA-024'],'User scope; A review PA-024; public PDAC questions 14–15');o[k]=nv
                else:remove_questions(v,path+(k,))
        elif isinstance(o,list):
            for i,v in enumerate(o):remove_questions(v,path+(i,))
    remove_questions(obj)

# PRODIGE-24: preserve study effects, correct subgroup and relapse denominators.
src=PA+'PMID_30575490.md; PMID_36048453.md; 2018 PDF p6; 2022 Figure 2 and Supplement 2 eTable 4'
sub('with no disease-free survival benefit in the 101 patients aged 70 or over (hazard ratio 0.86, 95% CI 0.53–1.39)','with an imprecise disease-free survival estimate in the 101 patients aged 70 or over (HR 0.86, 95% CI 0.53–1.39), which does not establish absence of benefit',['PA099'],src,['pdac','ampullary'],False)
sub('with no disease-free survival benefit in the 101 patients aged 70 or over (hazard ratio 0.86, 0.53–1.39)','with an imprecise disease-free survival estimate in the 101 patients aged 70 or over (HR 0.86, 0.53–1.39), which does not establish absence of benefit',['PA099'],src,['pdac','ampullary'],False)
sub('showed no disease-free survival benefit in the fifth of patients aged 70 or over (hazard ratio 0.86, 0.53–1.39)','gave an imprecise disease-free survival estimate in patients aged 70 or over (HR 0.86, 0.53–1.39), without establishing absence of benefit',['PA099'],src,['pdac','ampullary'],False)
sub('with no disease-free survival benefit in those aged 70 or over','with uncertainty about the magnitude of benefit in those aged 70 or over; nonsignificance does not establish no benefit',['PA099'],src,['pdac','ampullary'],False)
sub('the disease-free survival benefit did not reach significance (HR 0.86, 95% CI 0.53–1.39).','the disease-free survival estimate was imprecise (HR 0.86, 95% CI 0.53–1.39). The mature overall-survival HR was 0.90 (0.56–1.46), with interaction P=.32; this does not demonstrate loss of benefit with age. Assess fitness and tolerance individually.',['PA099'],src,['pdac','ampullary'],False)
sub('chemotherapy at relapse reaching 66.9% against 83.0% of relapsing control patients, 74.2% of whom received FOLFIRINOX','first-relapse chemotherapy given to 107/160 (66.9%) versus 151/182 (83.0%) relapsers. Among the 151 control-arm patients receiving chemotherapy, 112 (74.2%) received FOLFIRINOX; that is 61.5% of all 182 control-arm relapsers',['PA100'],src,['pdac','ampullary'],False)
sub('a postoperative CA 19-9 below 180 U/mL','a postoperative CA 19-9 of 180 U/mL or less',['PA102'],src,['pdac','ampullary'],False)
sub('no coronary disease','no symptomatic heart failure or coronary artery disease',['PA102'],src,['pdac','ampullary'],False)
sub('which is why its medians sit below PRODIGE-24\'s and CONKO-001\'s.','These selection differences prevent ranking regimens by cross-trial survival medians.',['PA101','B19-S25484c86d5'],src,['pdac'],False)
sub('a 2.4-fold disease-free survival difference','a 2.0-fold difference in median disease-free survival',['B19-S98e1f2e416'],B+'B19_pdac_roadmap/reviews/R2/24104372.md; CONKO-001 abstract and Figure 2',['pdac'],False)

# pNET: specimen adequacy, functional and hereditary branches, and follow-up.
src=PA+'NCCN_NET_v1_2026_targeted.md; original PDF pp88–91, NE-E1–4'
setp('pnet','gates.0.crit.1','Exact Ki-67 index and mitotic rate per 2 mm² when assessable; document tissue adequacy and use Ki-67 when a small biopsy cannot support a reliable mitotic count',['PA090'],src)
setp('pnet','gates.0.standard.0.t','Report differentiation, exact Ki-67 and mitotic rate per 2 mm² when assessable. Record specimen adequacy; a reliable Ki-67-based grade can be used when mitotic counting is not possible.',['PA090'],src)
sub('An exact Ki-67 proliferative index reported as a number, not a range, with the mitotic count per 2 mm²','Exact Ki-67 and mitotic count per 2 mm² when assessable, with specimen adequacy recorded; use the higher grade when both are available',['PA090'],src,['pnet'],False)
src=PA+'37877341_ENETS_NF.md; original PDF pp2–3 and pp5–6; NANETS surgical guidance PMID31856076'
setp('pnet','gates.0.alt.0.t','For a small incidental suspected nonfunctioning pNET, discuss whether tissue confirmation will change observation or treatment; ENETS recommends confirmation where possible.',['B20-biopsy-scope'],src)
setp('pnet','gates.3.standard.0.t','Observation is an option for an asymptomatic, low-grade, nonfunctioning tumour ≤1 cm without main pancreatic duct dilation; consider tissue confirmation where possible and document diagnostic confidence.',['B20-biopsy-scope'],src)
setp('pnet','gates.3.standard.1.t','Explain that observation evidence is nonrandomized: prospective cohorts have short follow-up, and Sadot provides a retrospective size-matched observation-versus-resection comparison.',['B20-R9-F14'],B+'B20_pnet_roadmap/reviews/R9/R9_REPORT.md; Sadot 2016; ASPEN/PANDORA reports')
append('pnet','gates.3.alt',{'t':'For a nonfunctioning tumour >1 to ≤2 cm, choose observation or resection individually with the multidisciplinary team.','l':'Reasonable','g':'C','refs':['37877341','31856076'],'pref':'Consider grade and diagnostic confidence, symptoms, interval growth, main-duct dilation, imaging evidence of invasion or nodes, hereditary context, patient fitness and preference, and the pancreatic operation required. Document a surveillance schedule when observing.','avoid':'Main-duct dilation, concerning growth, higher grade, invasion, nodal disease or symptoms should prompt reassessment for treatment; 2 cm is not a guarantee of benign behavior.'},['B20-R9-F01'],src)
setp('pnet','gates.3.standard.2.avoid','Routine surveillance uses CT or MRI. SSTR PET and FDG PET are reserved for defined clinical questions. Reassess for growth, duct dilation, symptoms or other progression; not every operation in the observation cohorts was triggered by growth.',['B20-ASPEN-growth'],src)
src=PA+'37578384_ENETS_functioning.md; original PDF pp3–7 and pp9–14; NCCN_NET_v1_2026_targeted.md original PDF pp35–38'
setp('pnet','gates.2.crit.0','Insulinoma — documented hypoglycaemia with inappropriately nonsuppressed insulin, proinsulin and C-peptide, interpreted with the simultaneous glucose and evaluation of mimics',['PA095'],src)
setp('pnet','gates.2.standard.0.t','For appropriate sporadic, localized functioning tumours, the hormonal syndrome can justify resection irrespective of size. MEN1-associated gastrinoma requires individualized hereditary and endocrine assessment.',['PA094'],src)
setp('pnet','gates.2.standard.1.t','Confirm and stabilize the hormonal syndrome; interpret gastrin with PPI exposure and maintain acid suppression when withdrawal would be unsafe.',['PA093'],src)
setp('pnet','gates.2.standard.1.avoid','Do not diagnose gastrinoma from hypergastrinaemia on a PPI alone. If acid suppression cannot safely be withdrawn, specialist assessment may use the clinical syndrome, imaging and appropriate tissue sampling while excluding other causes. Assess hereditary features and arrange genetic evaluation when indicated; do not delay necessary acid suppression.',['PA093'],src)
setp('pnet','gates.2.standard.2.t','For insulinoma, choose the operation by tumour location and main-duct proximity: enucleation for suitable superficial lesions, spleen-preserving distal resection for appropriate deep distal lesions, and a head-specific operation for deep head lesions.',['PA092'],src)
setp('pnet','gates.2.alt.1.avoid','Nonrandomized comparative evidence exists. ERASING matched 89 EUS-RFA and 89 surgical patients: symptom control was 95.5% versus 100%, with repeat ablation counted as success and shorter RFA follow-up (23 versus 37 months). This does not establish durable oncologic equivalence. Reserve ablation for appropriately selected patients after expert multidisciplinary review. [EXPERTISE]',['PA098'],PA+'36871765_ERASING.md; original PDF pp2–9, Tables 1–2 and Figure 2')
addref('pnet','36871765',['ERASING insulinoma comparison','Crinò 2023','Crinò SF, et al. Endoscopic ultrasound-guided radiofrequency ablation versus surgical resection for treatment of pancreatic insulinoma. Clin Gastroenterol Hepatol. 2023;21:2834–2843.e2. doi:10.1016/j.cgh.2023.02.022. PMID:36871765.'],['PA098'],PA+'36871765_ERASING.md')
setp('pnet','gates.2.alt.1.refs',['31856076','37578384','36871765'],['PA098'],PA+'36871765_ERASING.md',propagate=False)
setp('pnet','gates.2.avoid.0.t','Avoid an unmonitored start of a somatostatin analogue for insulinoma: hypoglycaemia can worsen.',['B20-ENETS-functioning'],src)
setp('pnet','gates.2.avoid.0.pref','Stabilize with diet and appropriate medical therapy. ENETS supports a monitored short-acting octreotide trial before long-acting treatment; NCCN emphasizes receptor-positive disease. Specialist review should reconcile receptor findings and the clinical response.',['B20-ENETS-functioning'],src)
setp('pnet','gates.2.avoid.0.avoid','Suppression of counterregulatory hormones may worsen hypoglycaemia even when an antitumour effect is possible. Monitor glucose and symptoms closely during a short-acting trial; do not infer safe long-acting treatment from receptor imaging alone.',['B20-ENETS-functioning'],src)
append('pnet','gates.2.standard',{'t':'Stabilize the hormonal syndrome while localization and definitive treatment are planned.','l':'Standard','g':'D','refs':['37578384'],'pref':'Coordinate endocrinology and the treating team: prevent and treat insulinoma hypoglycaemia; maintain acid suppression for gastrinoma; replace fluids and electrolytes in VIPoma; address syndrome-specific metabolic and thrombotic risks.','avoid':'Severe hypoglycaemia, dehydration, electrolyte disturbance, bleeding or other acute complications require urgent clinical care rather than waiting for the tumour board.'},['B20-R9-gate3-symptom-control'],src)
sub('In MEN1, resect a functional tumour whatever its size, observe a nonfunctional tumour under 1 cm, and resect above 2 cm or on significant growth — accepting that surgery will not clear the gland.','In MEN1, individualize treatment by functional syndrome and hereditary context. Symptomatic insulinoma generally requires treatment; MEN1 gastrinoma timing and extent remain controversial. Nonfunctioning lesions may be observed when small, with resection considered for size, growth and other concerning features. Surgery will not clear the inherited risk.',['PA094'],src,['pnet'])
append('pnet','gates.4.crit','Differentiation/grade and hereditary or multifocal disease assessed before choosing the operation; refer to decisions 7 and 8 when relevant',['B20-R9-F02'],PA+'NCCN_NET_v1_2026_targeted.md; 37578384_ENETS_functioning.md; 37877341_ENETS_NF.md')
src=PA+'31856076_NANETS_surgical.md; 26482044_Tang.md; original ENETS NEC guidance PMID36924180 PDF pp5–8 (shared source application)'
setp('pnet','gates.7.standard.1.t','For poorly differentiated pancreatic NEC, prioritize multidisciplinary systemic-treatment assessment; selected localized disease may still warrant consideration of R0 surgery.',['PA070','PA075'],src)
setp('pnet','gates.7.standard.1.pref','NANETS 2020 generally advises against resection of pancreatic NEC. ENETS 2023 permits selected localized disease to be considered for surgery after thorough staging, with perioperative treatment discussed. Differentiation informs care but is not the sole determinant: integrate stage, anatomy, fitness and expected benefit. Metastatic NEC generally follows a systemic-therapy pathway.',['PA070','PA075'],src)
setp('pnet','gates.7.standard.1.note','Molecular profiling can identify treatment-relevant alterations. Biomarker-unselected immunotherapy has limited activity. Keep poorly differentiated NEC separate from well-differentiated NET G3 and do not use a Ki-67 threshold alone to choose between them.',['PA070','B20-ENETS-NEC'],src)
setp('pnet','gates.7.avoid.1.t','For resected well-differentiated NET G3, adjuvant systemic therapy is not established; assess clinical-trial eligibility.',['PA075'],src)
setp('pnet','gates.7.avoid.1.pref','Do not generalize this NET statement to poorly differentiated NEC. For selected resected localized NEC, ENETS allows discussion of adjuvant platinum-based therapy within multidisciplinary care.',['PA075'],src)
src=B+'B20_pnet_roadmap/reviews/R2/key_rm_pnet_nct05040360.md; NCT05040360/SWOG S2104 eligibility; R9 F13'
setp('pnet','gates.8.standard.0.pref','For resected well-differentiated pNET, no routine adjuvant systemic treatment is established. Consider trials after checking current eligibility and an accessible site. SWOG S2104 (NCT05040360) tests CAPTEM versus observation in a selected higher-risk population, including 14–120 days after resection, Ki-67 3–55% and Zaidi recurrence-risk score ≥3; it is not available to every resected patient.',['B20-R9-F13'],src)
src=PA+'37877341_ENETS_NF.md; original PDF pp11–12 §4.1.1; NCCN_NET_v1_2026_targeted.md PDF43'
sub('every 12 to 24 months to 10 years','every 12 to 24 months for 10 years after the first five years (the ENETS wording)',['PA079'],src,['pnet'],False)
sub('ENETS 2023 starts at 3 to 6 months with a somatostatin-receptor PET','ENETS 2023 starts at 3 to 6 months; SSTR PET is considered if no pretherapeutic scan was obtained or when clinically indicated, alongside morphological imaging',['PA079'],src,['pnet'],False)
sub('at level 5 evidence graded B - an inversion the GRADE framework it claims to follow would not permit','at level 5 evidence graded B in the guidance\'s own framework',['PA079'],src,['pnet'],False)
src=PA+'NCCN_NET_v1_2026_targeted.md; original NCCN PDF title/version page'
setp('pnet','nonpm.nccn.2','National Comprehensive Cancer Network. Neuroendocrine and Adrenal Tumors. Version 1.2026, 21 April 2026. Targeted original-PDF checks support the cited pathology, functional-tumour, imaging, surgery and surveillance sections. The whole guideline and every underlying reference have not been re-audited; confirm current recommendations in the licensed guideline.',['B20-R9-F09'],src)

# Incidental liver lesions: diagnostic categories are not histologic diagnoses.
src=MB+'28927870.md; Gore 2017 Figure 1 and PDF pp6–7; 33153555 ACR variant tables'
setp('incidental','gates.1.standard.0.t','Characterize an indeterminate liver lesion in a patient with known extrahepatic cancer using a test chosen for the lesion size, initial modality and clinical question; contrast MRI is often appropriate.',['MB055','MB056'],src)
setp('incidental','gates.1.standard.0.avoid','The 2010 meta-analysis concerns untreated colorectal-cancer staging. Its subcentimetre advantage for MRI does not restrict MRI to small lesions, and a nonsignificant comparison at ≥10 mm does not prove equivalence. Gadoxetate and gadobenate were not represented sufficiently to support a claim that modern liver-specific contrast agents provide no benefit.',['MB056'],MB+'20829538.md; Niekel 2010 PDF p4')
setp('incidental','gates.1.standard.0.pref','Use the scenario-specific ACR guidance. For a lesion <1 cm first seen on ultrasound in a patient with known cancer, contrast MRI is the only test rated usually appropriate in that variant. For a lesion first seen on limited CT or MRI, contrast MRI and multiphase CT may both be appropriate; the initial test and clinical context matter.',['MB055'],src)
setp('incidental','gates.3.avoid.0.t','Do not use FDG PET/CT routinely to characterize an incidental liver lesion; reserve it for selected oncology questions.',['MB055'],src)
setp('incidental','gates.1.alt.0.order','These are selected second tests. PET/CT may help in an appropriate oncology scenario, and biopsy may resolve a management-changing diagnosis after imaging review. Neither replaces scenario-specific cross-sectional characterization.',['MB055'],src)
setp('incidental','gates.6.standard.1.pref','Apply the ACR CT-incidental algorithm to its intended population. A low-risk lesion <1 cm generally needs no further workup, but suspicious features may justify MRI. A high-risk lesion <1 cm generally receives MRI in 3–6 months, with surveillance CT an alternative in the appropriate oncology setting. Exactly 1.0 cm enters the 1.0–1.5 cm branch. The separate ACR Appropriateness Criteria also depend on how the lesion was first detected.',['MB058','MB060'],src)
setp('incidental','quickref.2.rows.0.0','Low risk, <1 cm',['MB060'],src)
setp('incidental','quickref.2.rows.0.1','Usually no further workup; suspicious features may justify MRI',['MB058'],src)
setp('incidental','quickref.2.rows.3.0','High risk, <1 cm, new',['MB060'],src)
setp('incidental','quickref.2.rows.10.1','Choice depends on initial modality and risk: contrast MRI or multiphase CT are commonly appropriate; CEUS ratings vary by scenario. Equal appropriateness ratings do not establish equal diagnostic performance.',['MB055'],src)
setp('incidental','quickref.2.rows.11.1','After ultrasound: contrast MRI is usually appropriate. After limited CT/MRI: contrast MRI or multiphase CT may be appropriate. Apply the matching ACR variant.',['MB055'],src)
src=MB+'30251931.md; Chernyak 2018 PDF pp6–7 and 10–13; LI-RADS core category tables'
setp('incidental','gates.5.standard.2.t','For a nodule without arterial hyperenhancement in an at-risk liver, assign the full LI-RADS category using all major and ancillary features; absence of hyperenhancement does not establish a benign or dysplastic nodule.',['MB066'],src)
setp('incidental','gates.5.standard.2.pref','Classic benign findings can be LR-1 or LR-2. Other observations without arterial hyperenhancement may be LR-3 or LR-4, depending on size and the remaining features. LR-3 generally receives repeat or alternative diagnostic imaging in 3–6 months; LR-4 warrants multidisciplinary diagnostic planning, which may include biopsy.',['MB066'],src)
setp('incidental','gates.8.standard.1.t','An LR-M observation is probably or definitely malignant but is not specific for HCC. Clarify the diagnosis before choosing the HCC, iCCA, mixed-tumour or metastatic treatment pathway.',['MB062'],src)
setp('incidental','gates.8.standard.1.pref','The differential includes iCCA, combined HCC–CCA and atypical HCC. Historical pooled CT/MRI categories reported 93% malignancy and 36% HCC in LR-M; these are selected, earlier-version cohorts rather than a histologic diagnosis for the individual patient. Discuss tissue sampling and the safest route in the multidisciplinary team.',['MB062'],src)
setp('incidental','gates.6.alt.0.note','An LR-M or mixed-phenotype observation needs diagnostic clarification at decision 8, often including tissue, rather than routine interval follow-up alone. HCC remains in the differential; route to a disease-specific treatment pathway after clarification.',['MB062'],src)
setp('incidental','gates.8.alt.1.avoid','Do not assign an LR-M observation to HCC or cholangiocarcinoma treatment from the category alone. Establish the likely histology and extent through multidisciplinary review and appropriate sampling.',['MB062'],src)
setp('incidental','gates.8.standard.2.t','Route confirmed colorectal liver metastases to CRLM and confirmed neuroendocrine liver disease to NELM. A hepatocellular lesion in a normal liver requires positive assessment for HCA and exclusion of HCC; exclusion of FNH alone does not diagnose HCA.',['MB062'],src)
setp('incidental','gates.8.standard.2.avoid','Early cancer-roadmap referral does not require the colorectal primary already resected or extrahepatic disease absent; those factors affect treatment and transplant assessment later. Confirm the likely origin, and obtain expert pathology review of neuroendocrine grade and differentiation when relevant.',['MB024','MB061','MB062'],MB+'Priority_Clinical_Corrections.md; local CPG applies transplant-selection requirements separately')

# HCA: confirmed high-risk molecular disease, observation timing and honest harms.
src=MB+'38958301.md; ACG 2024 original PDF pp13–16; EASL 2016 HCA recommendations'
setp('adenoma','gates.1.alt.1.avoid','Do not let a reassuring imaging phenotype cancel risk from sex, size, growth or bleeding. Imaging subtype alone is not equivalent to a confirmed molecular diagnosis. Proven beta-catenin activation, particularly a high-risk exon 3 alteration, warrants specialist assessment for resection irrespective of size under EASL/ACG guidance; document the exon/codon and diagnostic certainty.',['MB078'],src)
setp('adenoma','gates.1.standard.2.t','Reimage after risk-factor modification and assess the trajectory. In women with lesions ≥5 cm, individualize reassessment and intervention over 6–12 months unless bleeding, concerning growth or suspected malignancy requires earlier action.',['MB075'],src)
setp('adenoma','gates.1.standard.2.pref','EASL recommends six months of observation after lifestyle change in women, then resection for lesions ≥5 cm or continuing to grow. ACG 2024 allows 6–12 months for an appropriate woman with a lesion ≥5 cm before deciding on treatment; this timing and size statement is an ungraded key concept. Individualize continued observation of a shrinking, otherwise low-risk lesion.',['MB075'],src)
setp('adenoma','gates.3.crit.0','Adenoma persistently ≥5 cm after an individualized trial of risk-factor modification, with duration, regression trajectory and any high-risk exception recorded',['MB075'],src)
setp('adenoma','gates.3.standard.0.t','Assess resection for a persistently ≥5 cm or growing adenoma after appropriate risk-factor modification; account for subtype, sex, symptoms, bleeding and suspicion of malignancy.',['MB075','MB078'],src)
setp('adenoma','gates.9.crit.2','For non-urgent oestrogen- or weight-associated disease, document the adequate modification period and trajectory; six months alone does not establish failure, particularly while a lesion is regressing',['B17-R8-F01','MB075'],src)
sub('documented progression despite at least 6 months of adequate risk-factor modification','documented progression despite an adequate, individualized risk-factor-modification period, with the trajectory and reason for intervention recorded',['B17-R8-F01'],src,['adenoma'],False)
src=MB+'31313827.md; van Rosmalen 2019 original PDF pp3–8, Table 2/Figure 2; Supplement Table S1'
sub('symptoms were unchanged','symptoms decreased from 34/59 (58%) to 22/59 (37%), without a statistically significant difference (P=.134); long-term benefit remains uncertain',['MB080'],src,['adenoma'],False)
sub('unchanged symptoms (P=0.134)','symptoms in 58% before versus 37% after TAE (P=.134), with long-term benefit uncertain',['MB080'],src,['adenoma'],False)
sub('one died at three months','one patient died three months after emergency TAE for haemorrhagic shock, following aspiration pneumonia; causal attribution was uncertain',['MB079'],src,['adenoma'],False)
sub('one reported death three months after the procedure','one death three months after emergency TAE for haemorrhagic shock followed by aspiration pneumonia, with uncertain causal attribution',['MB079'],src,['adenoma'],False)
sub('almost all of that mortality is attributable to the treatment rather than the disease','these observational data cannot determine how much mortality was attributable to treatment rather than underlying disease or comorbidity',['MB020'],MB+'35018302.md; Ziogas 2022 Tables 1–4 and cause-of-death results',['adenoma'],False)
src=MB+'26919265.md; Chiche 2016 original Figure 1, Tables 3–4 and Results'
sub('true malignant transformation was present in only 17 explants (35%)','17 patients had HCC before or at transplantation; the detailed tables record 12 positive explants, four negative explants after prior HCC and one unavailable result',['MB018'],src,['adenoma'],False)
sub('true malignant transformation was present in only 17 of 49 explants (35%)','17 of 49 patients had HCC before or at transplantation; Tables 3–4 record 12 positive explants, four negative after prior HCC and one unavailable result',['MB018'],src,['adenoma'],False)
sub('15 of 64 cases coded as adenomatosis in the registry were not adenomatosis at all once verified','the report assembled 49 confirmed cases using registry and additional centre ascertainment; the difference between 64 initially mentioned and 49 confirmed does not establish 15 miscoded cases',['MB018'],src,['adenoma'],False)
sub('15 of 64 cases coded as adenomatosis in the European registry were not adenomatosis once verified','the European report assembled 49 confirmed cases using registry and additional centre ascertainment, without establishing a 15-of-64 misclassification rate',['MB018'],src,['adenoma'],False)
sub('roughly one patient in eight died of the treatment or its failure, against a 2.5% ten-year transformation rate in adenomatosis managed conservatively','the series documents important mortality and graft harms, but comparison with a separate conservatively managed cohort cannot estimate transplant-attributable mortality or net benefit',['MB018','MB020'],src,['adenoma'],False)

# Ampullary: counted subgroups, subsequent treatment and ESGE safeguards.
src=B+'B22_ampullary_roadmap/reviews/R4/20375404.md; ABC-02 original Table 1 and Figure 3; '+PA+'33798493_ABC06_application.md'
sub('which did include ampullary cancers but did not report how many and was not an adjuvant trial','which included 20 ampullary patients (subgroup OS HR 0.62, 95% CI 0.21–1.82) and was not an adjuvant trial',['PA-049','B22-S98c1611658'],src,['ampullary'])
sub('but the number of ampullary patients was not reported, so the ampullary effect size is unknown; that trial is cited here from its abstract and from guideline text only','the ampullary subgroup contained 20 patients (9 cisplatin–gemcitabine, 11 gemcitabine), with OS HR 0.62 (95% CI 0.21–1.82), too imprecise to establish a separate ampullary benefit',['PA-049','B22-S98c1611658'],src,['ampullary'])
setp('ampullary','gates.8.standard.1.note','Subtype-directed selection partly extrapolates from colorectal, pancreatic and biliary cancers. ABC-02 did include 20 ampullary patients, with an imprecise subgroup OS HR of 0.62 (95% CI 0.21–1.82). ABC-06 separately included 11 ampullary patients after GemCis progression; it informs the subsequent-treatment discussion below, not first-line or adjuvant therapy. Screen for clinical trials and explain these population limits. [PROTOCOL]',['PA-049','PA107'],src)
sub('BILCAP and ABC-02 are cited here from their abstracts and from guideline text only, since neither full text was read for this page.','The full-text review confirms that BILCAP excluded ampullary carcinoma and that ABC-02 included the small, imprecise ampullary subgroup described above.',['PA-049'],src,['ampullary'])
sub('BILCAP in biliary tract cancer, whose own primary analysis','BILCAP in biliary tract cancer, which excluded ampullary carcinoma and whose primary analysis',['PA-049'],src,['ampullary'],False)
sub('ampullary patients included but not counted','20 ampullary patients; subgroup OS HR 0.62 (0.21–1.82)',['PA-049'],src,['ampullary'],False)
src=PA+'33798493_ABC06_application.md; ABC-06 main PDF pp3–5 and7/Figure3; original appendix PDF10'
append('ampullary','gates.8.alt',{'t':'After progression, reassess fitness, biliary drainage, prior treatment and toxicity, molecular targets and trial options; consider a subsequent regimen when appropriate.','l':'Reasonable','g':'D','refs':['33798493'],'pref':'For a fit patient after gemcitabine–cisplatin, FOLFOX with active symptom control is a qualified option. ABC-06 enrolled 162 biliary-tract patients with ECOG 0–1 after GemCis progression: median OS 6.2 versus 5.3 months, adjusted HR 0.69 (95% CI 0.50–0.97), against active symptom control alone.','avoid':'Only 11 patients had ampullary cancer (4 FOLFOX, 7 control); their exploratory OS HR was 0.71 (0.18–2.77). This does not establish an independent ampullary benefit, first-line or adjuvant efficacy, or benefit after prior oxaliplatin. Address drainage, organ function, infection and residual neuropathy before treatment.','note':'Continue active symptom control throughout. When further anticancer treatment is unsuitable or declined, prioritize supportive care, symptom treatment and goals-of-care planning.'},['PA107'],src)
addref('ampullary','33798493',['ABC-06','Systemic therapy','Lamarca A, et al. Second-line FOLFOX chemotherapy versus active symptom control for advanced biliary tract cancer (ABC-06). Lancet Oncol. 2021;22:690–701. doi:10.1016/S1470-2045(21)00027-9. PMID:33798493.'],['PA107'],src)
setp('ampullary','gates.8.alt.0.t','OPEN proposal AMP-R1: local therapy or surgery after systemic response in selected oligometastatic disease; not an activated institutional pathway.',['B22-R6-F01'],B+'B22_ampullary_roadmap/reviews/R6/R6_REPORT.md; AMP-R1 status OPEN/not activated')
setp('ampullary','gates.8.alt.0.l','Proposed — not activated',['B22-R6-F01'],B+'B22_ampullary_roadmap/reviews/R6/R6_REPORT.md',propagate=False)
src=PA+'PMID_33728632.md; ESGE original PDF pp4–6, Figure1/§3.3; pp8–12 §§4.1,4.3,5; p14 §7'
setp('ampullary','33728632.critique.7','ESGE recommends against papillectomy without proven adenoma and explicitly recommends repeat assessment and sampling after initial negative histology when suspicion remains. Figure 1 includes repeated biopsy, EUS-guided sampling and selected limited sphincterotomy pathways. A negative biopsy does not reliably exclude carcinoma.',['PA-030'],src,kind='critique')
setp('ampullary','33728632.critique.1','ESGE separates lesion diameter from ductal extension: en-bloc resection is intended for lesions up to 20–30 mm; 30–40 mm lesions require individualized assessment. Surgery is suggested when endoscopic treatment is technically infeasible, including some lesions >4 cm, or with intraductal extension >20 mm. Expert complementary treatment for lesser ductal extension is a separate context.',['PA-033'],src,kind='critique')
setp('ampullary','33728632.critique.5','ESGE specifies surveillance within three months, at six and twelve months, then yearly for at least five years. The minimum is not a fixed stopping point; longer monitoring should reflect recurrence risk, fitness and life expectancy. Evidence for the optimal interval and duration remains limited.',['PA-032'],src,kind='critique')
setp('ampullary','gates.2.avoid.0.t','Refer for surgical or expert endoscopic assessment when papillectomy is technically infeasible, including selected lesions >4 cm or intraductal extension >20 mm.',['PA-033'],src)
setp('ampullary','gates.2.avoid.0.pref','ESGE suggests surgical referral on weak, low-quality evidence in these settings. Lesion diameter, intraductal extent and access are distinct considerations; assess 30–40 mm lesions and limited ductal extension individually in an expert centre.',['PA-033'],src)
setp('ampullary','gates.2.standard.0.avoid','Do not attempt a technically infeasible resection. En-bloc intent generally applies up to 20–30 mm; 30–40 mm lesions require individualized expert assessment. ESGE suggests surgery for technical infeasibility, examples including size >4 cm or obstructing diverticulum, and for intraductal extension >20 mm.',['PA-033'],src)
sub('no submucosal injection','no submucosal injection at the papilla (lateral duodenal extension may require injection-assisted EMR)',['PA-033'],src,['ampullary'],False)

# Later-line PDAC and corrected daraxonrasib endpoint/eligibility statements.
src=B+'B19_pdac_roadmap/reviews/R2/42223072.md; RASolute 302 original PDF pp4–5, Figures2–3; FDA approval notice 26 August 2026 (rechecked 2 November 2026)'
setp('pdac','gates.8.alt.0.opts.0.name','Daraxonrasib for eligible metastatic PDAC; the US indication is not restricted to a RAS mutation',['B19-R7-F02'],src)
setp('pdac','gates.8.alt.0.opts.0.pref','The FDA approval of 26 August 2026 covers adults with metastatic PDAC after at least one systemic therapy, or those not candidates for multiagent systemic therapy. The randomized trial studied patients progressing after one prior line; it does not directly establish the same benefit in untreated patients unfit for combinations.',['B19-R7-F02'],src)
setp('pdac','gates.8.alt.0.opts.0.avoid','Benefit was shown in the RAS G12 and overall randomized populations. In the small non-G12 subgroup (n=41), PFS HR was 1.38 (95% CI 0.60–3.17) while OS HR was 0.37 (0.15–0.93); these exploratory, imprecise estimates do not establish lack of benefit. Interpretation also requires the open-label design, short follow-up and differential treatment non-initiation (38/252 chemotherapy versus 7/248 daraxonrasib). Check the current prescribing information and patient-specific toxicity risks.',['B19-R7-F01','B19-S0f33c8149a'],src)
sub('its benefit is established in the RAS <b>G12</b> population that was its primary analysis set, and the non-G12 subgroup points the other way (HR 1.38, 0.60–3.17)','benefit was demonstrated in both the RAS <b>G12</b> primary population and the overall population. Non-G12 estimates are exploratory: PFS HR 1.38 (0.60–3.17), OS HR 0.37 (0.15–0.93), n=41',['B19-R7-F01'],src,['pdac'])
sub('In patients <b>without</b> a G12 mutation the hazard ratio was 1.38 (95% CI 0.60–3.17), a point estimate favouring chemotherapy.','In 41 patients without G12, the PFS HR was 1.38 (95% CI 0.60–3.17) and OS HR 0.37 (0.15–0.93); these small exploratory estimates must be distinguished by endpoint.',['B19-R7-F01'],src,['pdac'],False)
sub('but the benefit is not established outside G12 (non-G12 HR 1.38, 0.60–3.17)','and benefit was also demonstrated in the overall population; the non-G12 subgroup was small and exploratory (n=41; PFS HR 1.38, 0.60–3.17; OS HR 0.37, 0.15–0.93)',['B19-R7-F01'],src,['pdac'],False)
sub('it is established only in RAS G12 disease','benefit was demonstrated in RAS G12 and overall populations',['B19-R7-F01'],src,['pdac'],False)
setp('pdac','quickref.2.rows.1.0','Metastatic PDAC eligible for daraxonrasib',['B19-R7-F02'],src)
setp('pdac','quickref.2.rows.1.1','RASolute 302: overall median OS 13.2 versus 6.7 months (HR 0.40, 95% CI 0.30–0.53); PFS 7.2 versus 3.6 (HR 0.49, 0.38–0.64). The US indication includes prior systemic therapy or inability to receive multiagent therapy and is not mutation-restricted. Non-G12 subgroup n=41: exploratory PFS HR 1.38 (0.60–3.17), OS HR 0.37 (0.15–0.93).',['B19-R7-F01','B19-R7-F02'],src)
sub('which is the point the non-G12 subgroup of RASolute 302 makes (HR 1.38, 0.60–3.17)','and do not confuse a small subgroup\'s PFS estimate with its OS result or with the overall trial result',['B19-R7-F01'],src,['pdac'],False)
setp('pdac','42223072.critique.3','The primary efficacy population was RAS G12, with positive key secondary endpoints in the overall randomized population. The non-G12 subgroup was only 41 patients: PFS HR 1.38 (0.60–3.17), OS HR 0.37 (0.15–0.93). These exploratory estimates cannot establish no benefit outside G12.',['B19-R7-F01'],src,kind='critique')
sub('and the non-G12 subgroup shows no benefit.','and the small non-G12 subgroup has different, imprecise PFS and OS estimates rather than proof of no benefit.',['B19-R7-F01'],src,['pdac'],False)
src=B+'B19_pdac_roadmap/reviews/R3/26615328.md; NAPOLI-1 original main report, Figures1–3/Tables1–3'
append('pdac','gates.8.alt',{'t':'After progression on gemcitabine-based therapy, consider liposomal irinotecan with fluorouracil/leucovorin for a suitable patient.','l':'Reasonable','g':'A','refs':['26615328'],'pref':'In NAPOLI-1, 117 combination patients versus 119 concurrent 5-FU/leucovorin controls had median OS 6.1 versus 4.2 months, HR 0.67 (95% CI 0.49–0.92). The trial selected patients with KPS ≥70 and adequate liver function. Reassess performance status, bilirubin/drainage, prior treatment and goals.','avoid':'The evidence does not establish immediate reuse after irinotecan-containing FOLFIRINOX or NALIRIFOX. Liposomal irinotecan is not interchangeable with conventional irinotecan; use the actual product label and pharmacy-verified dosing. Continue symptom-directed care and consider trials or supportive care when further cytotoxic therapy is unsuitable.'},['B19-R8-F01'],src)
addref('pdac','26615328',['NAPOLI-1','Systemic therapy','Wang-Gillam A, et al. Nanoliposomal irinotecan with fluorouracil and folinic acid in metastatic pancreatic cancer after previous gemcitabine-based therapy (NAPOLI-1). Lancet. 2016;387:545–557. doi:10.1016/S0140-6736(15)00986-1. PMID:26615328.'],['B19-R8-F01'],src)
setp('pdac','ops.board.4','Urgent clinical care precedes the board: suspected cholangitis requires same-day assessment and timely biliary decompression according to severity; symptomatic gastric outlet obstruction requires prompt assessment, resuscitation and relief as indicated. Escalate immediately for sepsis, dehydration or inability to maintain intake. The board can then coordinate the oncologic plan. Owner: treating clinician and appropriate emergency/endoscopy teams.',['B19-R8-F07'],B+'B19_pdac_roadmap/reviews/R8/R8_REPORT.md; NCCN drainage and palliation sections')
setp('pdac','gates.6.standard.0.order','Choose an adjuvant regimen using guideline recommendations, recovery, fitness and tolerance. PRODIGE-24 randomized mFOLFIRINOX against gemcitabine; ESPAC-4 randomized GemCap against gemcitabine. The two combinations have not been compared head to head, so their different survival medians do not establish a comparative ranking. Trial eligibility and subsequent therapy differ materially.',['PA101'],PA+'PMID_30575490.md; PMID_36048453.md; 2018Methods and 2022Table3')
sub('93% of the whole cohort received relapse treatment','305 of 327 evaluable relapsers (93.3%) received some relapse treatment; this was not 93% of all randomized patients',['PA100'],PA+'PMID_36048453.md; Supplement2 eTable4',['pdac','ampullary'],False)
sub('four months of mFOLFIRINOX','a planned 24-week course of mFOLFIRINOX',['PA100'],PA+'PMID_30575490.md; trial treatment schedule',['pdac','ampullary'],False)
src='FDA 16 October 2026 updated TMB-H indication; https://www.fda.gov/drugs/resources-information-approved-drugs/fda-grants-traditional-approval-pembrolizumab-or-pembrolizumab-and-berahyaluronidase-alfa-pmph ; checked 2 November 2026'
setp('pdac','gates.8.alt.0.opts.2.when','Separate MSI-high/dMMR eligibility from the TMB-high indication. Under the FDA update of 16 October 2026, pembrolizumab for TMB-H solid tumours requires ≥13 mut/Mb by an FDA-authorized test, progression after prior treatment and no satisfactory alternative. The prior ≥10 threshold is historical. Check the applicable current label for each agent.',['A-Continuation-S1ad19f1e04','A-Continuation-S6ba3a47eef'],src)
setp('pdac','quickref.2.rows.4.1','Pembrolizumab or other appropriately labelled therapy for MSI-H/dMMR. The updated US TMB-H pembrolizumab indication is ≥13 mut/Mb by an FDA-authorized test after progression on prior treatment with no satisfactory alternative; this is separate from MSI-H/dMMR.',['A-Continuation-S6ba3a47eef'],src)

# Clarify elective HCA counseling wherever the longest option text carried the errors.
src=MB+'31313827.md; original PDF pp3–8 and SupplementTablesS1–S5'
setp('adenoma','gates.3.standard.2.opts.1.avoid','Discuss the mixed elective/emergency cohort explicitly: 6/59 (10%) had major complications; the supplement records 3/36 nonbleeding elective cases and 3/23 bleeding cases. One patient died three months after emergency TAE for haemorrhagic shock, following aspiration pneumonia, with attribution uncertain. Twenty of 59 (34%) later underwent surgery for several indications. Symptoms were reported in 58% before versus 37% within three months (P=.134); durable symptom benefit remains uncertain. Lack of a whole-lesion specimen limits pathological assessment, but some patients had biopsy or previous resection.',['MB079','MB080'],src)
sub('symptoms unchanged at 3 months (P=0.134)','symptoms in 58% before versus 37% within three months (P=.134), with long-term symptom benefit uncertain',['MB080'],src,['adenoma'],False)
sub('no symptom improvement at 3 months (P=0.134)','an uncertain symptom effect at three months (58% symptomatic before versus 37% after; P=.134)',['MB080'],src,['adenoma'],False)
sub('unchanged symptoms at 3 months','uncertain long-term symptom benefit after the short three-month assessment',['MB080'],src,['adenoma'],False)
sub('one death three months after the procedure','one death after emergency TAE for haemorrhagic shock and later aspiration pneumonia, with uncertain attribution',['MB079'],src,['adenoma'],False)
sub('one death in 59 patients','one post-emergency-TAE death after haemorrhagic shock and aspiration pneumonia, with uncertain attribution',['MB079'],src,['adenoma'],False)
setp('adenoma','ops.approvals.9.why','HCA is not a standardized MELD exception. Transplant cohorts report selected-recipient outcomes without an untreated comparison: the UNOS analysis had 26 deaths among 142 recipients over median 62.9 months, while its 9.0% waitlist endpoint combined deaths and too-sick removals. These figures do not establish treatment-attributable mortality. The European series assembled 49 confirmed cases; 17 had HCC before or at LT, while the detailed tables record 12 positive explants. It does not establish a 15/64 miscoding rate. Graft stewardship and expected benefit require individual multidisciplinary review.',['MB018','MB020'],MB+'35018302.md; 26919265.md')

# Public provenance is an accurate bounded status, not a blanket verification claim.
for slug in SLUGS:
    setp(slug,'provenance','Revised 2 November 2026 using source-linked clinical audit findings. The change register records the original wording, revision and source locator. Source access and review depth vary; remaining critiques, unavailable sources and unreviewed material are retained in the audit record. Clinical decisions, society guidance and open local proposals retain their distinct status.',['B-handoff-source-status'],'B handoff 2 November 2026; A focused audit coverage statements')

shared.extend([
 {'type':'routing','file':'assets/roadmap-links.json','slug':'incidental','requested':'Add decision 1 → 6 for an indeterminate lesion after cancer-staging imaging; decision 7 → hilar for a suspected perihilar primary before primary-tumour biopsy; undetermined risk at decision 0 → hepatology clarification and repeat risk assessment.','finding_ids':['B18-R8-F01','B18-R8-F03','B18-R8-F05']},
 {'type':'routing','file':'assets/roadmap-links.json','slug':'ampullary','requested':'Add decision 1 → 5 for biopsy-proven invasive carcinoma and decision 3 → 5 for invasive carcinoma in a papillectomy specimen. Keep decision 3 → 4 specifically for residual adenoma. Locally advanced unresectable disease should reach decision 8.','finding_ids':['B22-R7-F01','B22-R7-F02']},
 {'type':'routing','file':'assets/roadmap-links.json','slug':'pdac','requested':'Remove navigation to PDAC-B1/B2 speculative transplant questions. Add operation/restaging → decision 8 for M1/positive washings and → decision 7 for locally unresectable nonmetastatic disease.','finding_ids':['PA-024','B19-R8-F03']},
 {'type':'routing','file':'assets/roadmap-links.json','slug':'pnet','requested':'Before operation selection at decision 5, link to decision 7 for hereditary/multifocal context and decision 8 for high-grade differentiation review; ensure decision 4 has a route to decision 5 when a 1–2 cm lesion is selected for resection.','finding_ids':['B20-R9-F01','B20-R9-F02']},
 {'type':'routing','file':'assets/roadmap-links.json','slug':'pcyst','requested':'Add decision 4 → 2 when cytology is suspicious/positive for high-grade dysplasia or carcinoma; note familial/genetic risk needs specialist assessment outside ordinary stopping rules.','finding_ids':['B21-R8-F01']},
 {'type':'routing','file':'assets/roadmap-links.json','slug':'adenoma','requested':'Qualify the decision 9 → HCC link: HCC treatment review does not imply automatic standardized transplant eligibility in a non-at-risk liver. Maintain decision 10 nonstandard transplant assessment and continued nontransplant-care route.','finding_ids':['B17-R9-F01']},
 {'type':'shared_evidence','requested':'Update shared compact rows that say ABC-02 did not count ampullary patients (n=20, subgroup OS HR0.62, 0.21–1.82); add ABC-06 only as subsequent therapy after GemCis, n11 ampullary, HR0.71,0.18–2.77.','finding_ids':['PA-049','PA107']},
 {'type':'shared_evidence','requested':'Propagate RASolute non-G12 endpoint correction: n41, PFS HR1.38(0.60–3.17), OS HR0.37(0.15–0.93); align current daraxonrasib eligibility with the FDA26Aug2026 approval, which is not mutation-restricted.','finding_ids':['B19-R7-F01','B19-R7-F02']},
 {'type':'shared_evidence','requested':'Propagate low cyst-fluid amylase as pseudocyst exclusion evidence, not rule-in; VHL pooled sensitivity56%, specificity99% (Pflüger37230894); retain assay-specific PancreaSeq71%/100% separately.','finding_ids':['PA-001','PA-015']},
 {'type':'shared_evidence','requested':'Propagate PRODIGE age uncertainty and exact relapse denominators; HCA TAE emergency-death context/symptom nonsignificance; LR-M histology and strict ACR<1cm boundary.','finding_ids':['PA099','PA100','MB079','MB080','MB060','MB062']},
 {'type':'shared_net_update','requested':'Add the dated NETTER-2 later OS/safety update where current treatment resources use the trial: interim OS HR1.25(0.74–2.13), OS benefit not established; 3 MDS patients, one progressing to AML. Preserve original2024cutoff values as historical, later crossover/attrition limits and EU/US distinction.','finding_ids':['PA-064'],'source_locator':PA+'PMID_42604001.md; EMA_Lutathera_II52_2025.md'},
 {'type':'calculator','file':'assets/clinical-scores.js','requested':'Spigelman: retain arithmetic, clarify restricted visible-polyp input scope and provide source-defined hyperplasia/inflammation 1-point histology/manual handling for microscopic-only cases; do not automatically map all modern LGD into both mild and moderate historical categories.','finding_ids':['PA-039']}
])

# Final propagation checks for the same accepted facts in summary/question copies.
src=PA+'PMID_38182527.md; Kyoto PDF p7 Figure3'
sub("whether a local 'suspicious' result is treated as an absolute indication, since that is what Kyoto 2024 now makes it","how a local 'suspicious' result triggers surgical assessment: Kyoto treats it as a high-risk stigma, with resection considered when clinically appropriate",['PA-016'],src,['pcyst'],False)
src=PA+'PMID_37230894.md; Pflüger2023Figure5; '+B+'B21_pcyst_roadmap/reviews/R3/36209796.md, Table2'
setp('pcyst','quickref.2.rows.8.0','VHL alterations — serous cystadenoma',['PA-015'],src)
setp('pcyst','quickref.2.rows.8.1','PancreaSeq VHL alone: 71% sensitivity, 100% specificity in a small resected subgroup (13 SCA plus one mixed serous–neuroendocrine lesion). Pooled VHL evidence: sensitivity 56% (33–78%), specificity 99% (99–100%); a negative result does not exclude SCA.',['PA-015'],src)
sub('VHL alterations identified serous cystadenomas (71% sensitivity, 100% specificity)','VHL alterations alone identified serous cystadenomas (71% sensitivity, 100% specificity; the combined alteration rule differs)',['B21-S1a6cff6f43'],src,['pcyst'],False)
setp('pcyst','quickref.2.rows.4.0','Cytology — direct assessment for high-grade dysplasia or carcinoma',['B21-S1a1fc14d99'],src)
setp('pcyst','quickref.2.intro','Allocate fluid according to the clinical question. Cytology directly assesses dysplasia/carcinoma; selected molecular panels can also inform the risk of advanced neoplasia, with assay-specific limits.',['B21-S83f2683c67'],src)
sub('and the decision to operate was informed by the molecular result','and the report does not establish whether molecular results influenced the decision to operate',['B21-S9775e43605'],src,['pcyst'],False)
sub('and the decision to operate was itself informed by the molecular result','and the report does not establish whether molecular results influenced the decision to operate',['B21-S29b33940ff'],src,['pcyst'],False)
src=B+'B21_pcyst_roadmap/reviews/R3/36209796.md; R2/28970292.md'
for f in ['pcyst/data/pathway.json']:
    def correct_panel_refs(obj,path=()):
        if isinstance(obj,dict):
            if isinstance(obj.get('refs'),list) and '28970292' in obj['refs'] and any(t in str(obj) for t in ['1,887','1,933','31 institutions']):
                old=copy.deepcopy(obj['refs']);obj['refs']=list(dict.fromkeys('36209796' if x=='28970292' else x for x in old));log(f,path+('refs',),old,obj['refs'],['B21-PancreaSeq-identity'],src)
            for k,v in obj.items():correct_panel_refs(v,path+(k,))
        elif isinstance(obj,list):
            for i,v in enumerate(obj):correct_panel_refs(v,path+(i,))
    correct_panel_refs(data[f])
src=B+'B21_pcyst_roadmap/reviews/R6/31473224.md; Oyama2020Table4 and Results pp5–8; R8-R8-D06'
sub('the increase in cyst size did not (1.46, 0.96 to 2.20)','the increase in cyst size did not show a significant association (SHR 1.46 per 10 mm, 0.96 to 2.20)',['B21-R8-D03'],src,['pcyst'],False)
sub('the increase in cyst size did not (1.46, 0.96 to 2.20)','the increase in cyst size did not show a significant association (SHR 1.46 per 10 mm, 0.96 to 2.20)',['B21-R8-D03'],src,['pcyst'],False)
setp('pcyst','gates.8.standard.1.order','These are different surveillance cohorts, not a randomized comparison of stopping rules. Selection at baseline and at the five-year landmark, endpoint definitions, follow-up duration and competing mortality differ. In Oyama, the SIR was 10.8 for the full 1,404-patient cohort but 5.8 (95% CI 3.7–7.9) among 804 patients followed beyond five years. The reported 107 months describes total follow-up, not an additional 107 months after year five. Decisions to continue or stop require the patient\'s current risk, life expectancy, surgical fitness and preferences.',['B21-R8-D06'],src)
setp('pcyst','honest.13.why','The stopping-rule studies differ in selection, endpoints and duration and cannot establish equivalent strategies. Oyama reported SIR 10.8 in the whole 1,404-patient cohort and 5.8 (3.7–7.9) in the 804 followed beyond five years. The 107-month follow-up figure is total follow-up, not time added after five years. Stable-lesion landmark cohorts also exclude patients who progressed or underwent surgery earlier. Consider competing mortality, surgical fitness and preference when choosing an interval or stopping rule.',['B21-R8-D06'],src)
setp('pcyst','quickref.1.foot','Use a named surveillance guideline and document any individualized stopping decision. Comparisons across the surveillance cohorts are limited by baseline and landmark selection, endpoint definitions, follow-up and competing mortality. Oyama\'s SIR 10.8 belongs to the whole cohort; the beyond-five-year subgroup SIR was 5.8 (3.7–7.9). The 107-month figure is total follow-up. Kyoto provides an IPMN-specific framework and does not supply a universal schedule for every pancreatic cyst type.',['B21-R8-D06'],src)

src=MB+'31313827.md; van Rosmalen2019PDF3–8 and SupplementS1'
setp('adenoma','honest.15.why','The 59-patient cohort combined elective and emergency embolisation. Major complications occurred in 6/59 (10%); one patient died three months after emergency treatment for haemorrhagic shock following aspiration pneumonia, with attribution uncertain. Twenty of 59 later underwent surgery for several indications. Symptoms fell from 58% to 37% within three months (P=.134); this does not establish no symptom benefit, and long-term benefit remains uncertain. Imaging denominators changed over time and some patients had biopsy or earlier resection. Discuss these limitations when comparing TAE with surgery.',['MB079','MB080'],src)
sub('one patient died three months after the procedure','one patient died three months after emergency TAE for haemorrhagic shock and aspiration pneumonia, with uncertain attribution',['MB079'],src,['adenoma'],False)
src=MB+'26919265.md; Chiche2016Figure1/Tables3–4; '+MB+'35018302.md'
setp('adenoma','quickref.3.rows.10.1','Chiche: 49 confirmed recipients; 17 had HCC before or at LT, with 12 positive explants in detailed tables, four negative after prior HCC and one unavailable. Three operative deaths, five retransplants and three fatal HCC recurrences. The study does not establish a 15/64 miscoding rate or a treatment-attributable mortality fraction.',['MB018','MB020'],src)
setp('adenoma','honest.21.why','The UNOS cohort and European adenomatosis series describe highly selected recipients and cannot estimate benefit versus nontransplant care. UNOS reported 26/142 deaths over median 62.9 months; deaths had diverse causes. Chiche identified 17 patients with HCC before or at LT, not 17 uniformly positive explants. These reports support careful counseling and graft stewardship but not attribution of nearly all mortality to treatment.',['MB018','MB020'],src)
setp('adenoma','honest.22.why','Registry coding, missing clinical variables and incomplete verification limit interpretation. Chiche assembled 49 confirmed cases through registry replies and additional centre ascertainment; subtracting 49 from 64 does not establish 15 miscoded cases. The UNOS analysis also lacked lesion number, size and complete case-level pathology review. Preserve these limitations without inventing a measured misclassification rate.',['MB018'],src)
sub('true transformation was found in only 17 explants, with three operative deaths, five retransplantations and three fatal recurrences; 15 of 64 registry-coded cases were not adenomatosis.','17 patients had HCC before or at LT, with 12 positive explants in detailed tables; there were three operative deaths, five retransplants and three fatal recurrences. The report does not establish a 15/64 miscoding rate.',['MB018'],src,['adenoma'],False)
src=MB+'38958301.md; ACG2024PDF13–16; EASL2016HCA recommendation; AISF PICO11'
sub("and an unreassuring subtype alone does not add an operation beyond size, growth and sex; a 4-5 cm lesion is a board judgement. A proven beta-catenin adenoma is still routed to resection assessment. The roadmap's two rules conflict for a sub-5 cm proven beta-catenin lesion, and it does not say which governs.","and an uncertain imaging subtype alone does not establish a molecular indication. A proven high-risk beta-catenin adenoma is referred for resection assessment irrespective of size, while the exon/codon, diagnostic certainty and the risks of intervention are documented. An intentional local departure remains an open decision requiring explicit approval.",['MB078'],src,['adenoma'],False)
setp('adenoma','ops.approvals.13.why','Imaging subtype and a confirmed molecular alteration are different findings. EASL recommends resection for proven beta-catenin mutation irrespective of size; ACG particularly identifies exon 3 risk, and AISF PICO 11 also recognizes proven beta-catenin mutation as an independent resection trigger. The programme should specify how molecular confirmation, exon/codon and operative risk inform this assessment rather than state a blanket size-only rule.',['MB078'],src)

src=MB+'30251931.md; EASL2016 benign liver lesion guidance'
setp('incidental','gates.8.crit.3','A hepatocellular lesion in a normal liver with unresolved FNH, HCA or HCC differential',['MB062'],src)
setp('incidental','gates.8.alt.0.pref','When HCA is suspected, obtain appropriate imaging and expert review, with tissue where it will change management. Excluding FNH alone does not establish HCA; exclude HCC and other mimics before definitive treatment routing.',['MB062'],src)
src=PA+'PMID_36048453.md; Supplement2 eTable4'
sub("chemotherapy at relapse reaching 66.9% of its relapsing patients against 83.0% of the control arm's, 74.2% of whom received FOLFIRINOX","first-relapse chemotherapy given to 107/160 (66.9%) versus 151/182 (83.0%) relapsers. Among the latter chemotherapy recipients, 112/151 (74.2%) received FOLFIRINOX",['PA100'],src,['pdac','ampullary'],False)
sub('postoperative CA 19-9 below 180 U/mL','postoperative CA 19-9 of 180 U/mL or less',['PA102'],PA+'PMID_30575490.md; Methods',['pdac','ampullary'],False)
sub('postoperative CA19-9 below 180 U/mL','postoperative CA19-9 of 180 U/mL or less',['PA102'],PA+'PMID_30575490.md; Methods',['pdac','ampullary'],False)
sub('RASolute 302 supports benefit only in previously treated RAS G12 disease while the US label is broader','RASolute 302 demonstrated benefit in both RAS G12 and the overall previously treated population; the US indication also includes patients unable to receive multiagent therapy',['B19-R7-F01','B19-R7-F02'],B+'B19_pdac_roadmap/reviews/R2/42223072.md; FDA26Aug2026',['pdac'],False)
src=B+'B20_pnet_roadmap/reviews/R9/R9_REPORT.md; ASPENTable1; '+PA+'37877341_ENETS_NF.md'
sub("two thirds of ASPEN's surveillance arm had no evaluable histology at all","215 of 406 ASPEN surveillance patients (53%) had no evaluable cytological grade",['B20-S2ed6332539'],src,['pnet'],False)
sub("Two thirds of ASPEN's surveillance arm had no evaluable histology","215 of 406 ASPEN surveillance patients (53%) had no evaluable cytological grade",['B20-S2ed6332539'],src,['pnet'],False)
sub('in ASPEN patient preference and centre preference together accounted for 84% of the stated indications for surgery, with anxiety independently associated with operating','in ASPEN preference accounted for many upfront operations; crossover from surveillance was mostly prompted by progression, so preference must not be described as the cause of most surveillance failures',['B20-ASPEN-crossover'],src,['pnet'],False)

def finish():
    manifest=[]
    for f,obj in data.items():
        before=original[f]
        after=json.dumps(obj,ensure_ascii=False,separators=(',',':')) if '/critique.json' in f else json.dumps(obj,ensure_ascii=False,indent=1)+'\n'
        if before==after:continue
        # Disjoint, uniquely anchored line chunks keep replay exact and efficient.
        before_lines,after_lines=before.splitlines(keepends=True),after.splitlines(keepends=True)
        matcher=difflib.SequenceMatcher(None,before_lines,after_lines,autojunk=False)
        for group in matcher.get_grouped_opcodes(3):
            a0,a1=group[0][1],group[-1][2];b0,b1=group[0][3],group[-1][4]
            old,new=''.join(before_lines[a0:a1]),''.join(after_lines[b0:b1])
            if before.count(old)!=1:raise ValueError('Nonunique diff chunk '+f)
            manifest.append({'file':f,'old':old,'new':new,'why':'Source-checked clinical audit correction; exact field-level changes and source locators are recorded in tools/audit_revision/other_change_register.json.'})
        replay=before
        for e in [x for x in manifest if x['file']==f]:
            if replay.count(e['old'])!=1:raise ValueError('Nonunique replay '+f)
            replay=replay.replace(e['old'],e['new'],1)
        assert replay==after,f
        (ROOT/f).write_text(after)
    revision={'id':'2026-11-02-other-roadmaps','requested_by':'Hao Liu: apply verified audit corrections to a new revised website edition','status':'Bounded, source-checked clinical corrections; open local decisions remain open; exhaustive source and critique audit is not claimed.','sources':[],'edits':[],'files':manifest}
    (ROOT/'tools/clinical_revisions/2026-11-02-other-roadmaps.json').write_text(json.dumps(revision,ensure_ascii=False,indent=2)+'\n')
    (ROOT/'tools/audit_revision/other_change_register.json').write_text(json.dumps({'reviewer':'Analyst A (Codex), internal implementation task','changes':changes},ensure_ascii=False,indent=2)+'\n')
    (ROOT/'tools/audit_revision/other_shared_proposals.json').write_text(json.dumps(shared,ensure_ascii=False,indent=2)+'\n')
    print(f'{len(changes)} field changes; {len(manifest)} protected replacement chunks; {len(shared)} shared proposals')

if __name__=='__main__': finish()
