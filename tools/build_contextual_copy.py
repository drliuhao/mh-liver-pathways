"""Reviewed display summaries. Full source wording is retained in information panels.

Source strings are captured as exact-match guards. No rules or options are changed.
Run after reviewing any revised source; never regenerate to bypass a mismatch.
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
data = json.loads((ROOT / 'transplant/assets/content.json').read_text())
import subprocess

roadmaps = {}
for slug in json.loads((ROOT / 'assets/roadmap-links.json').read_text()):
    if slug == 'hcc':
        # Existing HCC data is a JavaScript literal rather than a separate JSON file.
        node = subprocess.check_output(['which', 'node'], text=True).strip()
        script = "const fs=require('fs'),vm=require('vm');const s=fs.readFileSync('hcc/index.html','utf8');console.log(JSON.stringify(vm.runInNewContext(s.slice(s.indexOf('const STAGES = ['),s.indexOf('/* the quantifier'))+';STAGES')));"
        roadmaps[slug] = json.loads(subprocess.check_output([node, '-e', script], cwd=ROOT, text=True))
    else:
        roadmaps[slug] = json.loads((ROOT / slug / 'data/pathway.json').read_text())['gates']

headings = {
    'hcc/diagnosis': 'Is HCC established for each lesion?',
    'hcc/curative-route': 'Transplant or safe, complete resection?',
    'hcc/allocation': 'Does pretreatment burden meet T2 or UNOS downstaging criteria?',
    'hcc/treatment': 'What treatment and response assessment supports transplant eligibility?',
    'hcc/listing': 'Suitability confirmed and HCC exception evidence complete?',
    'hcc/waitlist': 'Still transplant-suitable and eligible for HCC exception renewal?',
    'hcc/after-transplant': 'What must be recorded and monitored after transplant?',
    'pcca/localize': 'Perihilar origin? Should transplant be considered?',
    'pcca/diagnosis': 'Can diagnosis and nodal staging avoid transperitoneal primary-tumor biopsy?',
    'pcca/phenotype': 'Do extent, size and resectability fit the protocol?',
    'pcca/neoadjuvant': 'Is the approved protocol regimen proceeding with safe drainage and infection control?',
    'pcca/staging': 'After neoadjuvant therapy, is regional and peritoneal staging negative?',
    'pcca/listing': 'Are pCCA exception evidence and transplant fitness current?',
    'pcca/follow-up': 'Who coordinates recurrence assessment and protocol review?',
    'icca/diagnosis': 'Biopsy-proven iCCA or mixed HCC–iCCA?',
    'icca/phenotype': 'Fits the guidance population, with no curative resection option?',
    'icca/therapy': 'How will therapy and observation establish durable control?',
    'icca/stability': 'Are six months of stability documented?',
    'icca/review': 'Is the iCCA exception supported and transplant selection complete?',
    'icca/follow-up': 'Has selection been rechecked and recurrence follow-up assigned?',
    'crlm/map-disease': 'Are the primary, liver burden and extrahepatic sites fully assessed?',
    'crlm/biology': 'Do molecular results and CEA meet CRLM exception guidance?',
    'crlm/unresectability': 'Can expert resection or ablation treat all clinically relevant disease?',
    'crlm/control': 'Has therapy achieved the required sustained control?',
    'crlm/clocks': 'Is the primary fully treated and are all required intervals met?',
    'crlm/restaging': 'Do current imaging and biomarkers support liver-only disease?',
    'crlm/review': 'Who confirms suitability, manages the exception and arranges surveillance?',
    'crlm/transplant': 'Does transplant benefit still justify risk, with recurrence follow-up assigned?',
    'nelm/biology': 'Well-differentiated grade 1–2 gastroenteropancreatic NET meeting guidance?',
    'nelm/distribution': 'Liver-only disease with the primary removed?',
    'nelm/options': 'What benefit does transplant add over other treatments?',
    'nelm/exposure': 'Do liver reserve and prior PRRT / liver-directed therapy permit the plan?',
    'nelm/observation': 'Does current staging still exclude extrahepatic disease?',
    'nelm/review': 'Are NET exception criteria documented and the patient accepted on expected benefit?',
    'nelm/follow-up': 'Is follow-up planned for recurrence and hormone-related symptoms?',
    'hehe/diagnosis': 'HEHE confirmed and angiosarcoma excluded?',
    'hehe/stage': 'Resectable liver disease? Extrahepatic disease affecting treatment?',
    'hehe/risk': 'What reflects disease behavior versus prognosis alone?',
    'hehe/review': 'HEHE confirmed, unresectable, no macrovascular invasion, and accepted for transplant?',
    'hehe/follow-up': 'How will explant findings and recurrence risk guide surveillance?',
    'hca/characterize': 'HCA? Which subtype, growth or complication matters?',
    'hca/standard-care': 'Can risk be managed without transplant?',
    'hca/exception-route': 'Which guidance criterion supports an exception request?',
    'hca/transformation': 'Benign adenoma or malignant transformation?',
    'hca/review': 'Do the exceptional indication and individual benefit justify transplant?',
    'hca/follow-up': 'Are complications controlled and long-term follow-up assigned?',
}

help_copy = {
    'hcc/diagnosis/diagnosis': 'Imaging-only diagnosis requires an at-risk patient. AFP alone is insufficient.',
    'hcc/curative-route/operation': 'Favors resection: limited burden, compensated liver, no clinically significant portal hypertension, adequate remnant. Early HCC with decompensation or significant portal hypertension may favor transplant.',
    'hcc/allocation/burden': 'Use confirmed pretreatment lesion counts and sizes.',
    'hcc/treatment/response': 'Assess viable tumor separately from the treated cavity; retain pretreatment stage. Downstaging imaging ≥4 weeks after last treatment.',
    'hcc/treatment/reserve': 'Reassess decompensation. Prior checkpoint immunotherapy needs transplant/pharmacy review before transplant.',
    'hcc/listing/exception': 'Verify qualifying lesions, baseline/response imaging, AFP history, chest staging and resection assessment.',
    'hcc/listing/fitness': 'Review cardiopulmonary, infection, functional and psychosocial suitability; prior ICI requires a rejection-risk plan.',
    'hcc/after-transplant/plan': 'Review viable explant burden and vascular invasion; plan chest/abdominal surveillance. Exception explant report due within 60 days.',
    'pcca/localize/origin': 'MRI/MRCP or appropriate CT: establish duct of origin; separate radial mass size from duct length.',
    'pcca/localize/review': 'Review liver disease, resectability and benign stricture causes before biopsy.',
    'pcca/diagnosis/diagnosis': 'At least one: malignant biopsy/cytology; CA 19-9 >100 U/mL without cholangitis; aneuploidy; or hilar mass <3 cm radially.',
    'pcca/diagnosis/biopsy': 'Avoid transperitoneal primary biopsy (EUS, percutaneous or operative). Regional-node sampling without traversing the primary is a different procedure.',
    'pcca/phenotype/size': 'Measure perpendicular to the duct. Exactly 3 cm fails <3 cm; duct length is separate.',
    'pcca/phenotype/spread': 'Chest/abdominal imaging ≤90 days before the initial exception request must show no metastases.',
    'pcca/phenotype/diagnosis': 'Confirm diagnostic criteria and no transperitoneal primary-tumor biopsy.',
    'pcca/neoadjuvant/protocol': 'Written protocol: selection, neoadjuvant therapy and operative staging. Review regimen changes with the program.',
    'pcca/staging/stage': 'Stage regional hepatic nodes and peritoneum after therapy, before transplant. Negative pretreatment EUS does not replace operative staging.',
    'pcca/staging/ready': 'Reconcile imaging and operative findings; resolve cholangitis and active safety issues.',
    'pcca/listing/evidence': 'Complete diagnosis/protocol evidence. Chest/abdomen imaging: ≤90 days for initial request; ≤30 days for extension.',
    'pcca/follow-up/plan': 'Review residual disease, nodes and margins; agree oncology/transplant surveillance. No universal OPTN regimen.',
    'icca/diagnosis/histology': 'Tissue diagnosis; exclude another primary. Mixed HCC–iCCA needs explicit local acceptance despite inclusion in guidance.',
    'icca/phenotype/focality': 'Multifocal: ≥2 separate nodules. Satellites: nearby separate nodules, no universal distance cutoff. Intrahepatic metastasis: spread within liver; distribution does not prove clonality.',
    'icca/phenotype/profile': 'Current guidance: ≤3 cm. Foundational “very early” cohort: ≤2 cm; it does not alone validate every ≤3 cm case.',
    'icca/therapy/safe': 'Review liver function/toxicity. Before checkpoint immunotherapy, assess rejection risk with the transplant team if transplant remains possible.',
    'icca/stability/duration': 'Six months from diagnosis or last treatment; team must confirm the applicable start. Early response is insufficient.',
    'icca/review/criteria': 'Confirm biopsy, cirrhosis, unresectability, solitary ≤3 cm tumor and ≥6 months stability. Extensions: imaging every 3 months, continued control.',
    'icca/follow-up/plan': 'Recheck control, fitness and consent. Review explant; agree surveillance. Selected cohorts do not define a universal interval.',
    'crlm/map-disease/primary': 'Primary pathology, pretreatment liver imaging and current liver/chest/abdomen/pelvis staging.',
    'crlm/biology/cea': 'µg/L = ng/mL numerically. Initial request excludes >80; extensions require <80. Exactly 80 needs explicit review.',
    'crlm/unresectability/clearance': 'Review remnant, vascular/biliary anatomy, staged or parenchymal-sparing surgery and combined ablation. Count alone does not establish unresectability.',
    'crlm/control/response': 'NLRB: >10% diameter growth or a new lesion; this differs from RECIST 1.1 progression.',
    'crlm/clocks/primary': 'Confirm negative margins and colonoscopy excluding recurrence ≤12 months before the request.',
    'crlm/restaging/timing': 'CT/MRI chest/abdomen/pelvis AND PET ≤1 month before initial request. PET after ≥4 weeks off chemotherapy; coordinate pause with oncology. ctDNA cannot substitute.',
    'crlm/review/criteria': 'Confirm initial selection. For renewal: CT/MRI chest/abdomen/pelvis and CEA every 3 months; no progression/extrahepatic disease; CEA <80 µg/L.',
    'crlm/transplant/plan': 'Recheck control, fitness, consent and feasibility of complete resection/ablation; agree recurrence surveillance and oncology care.',
    'nelm/biology/grade': 'Ki-67 <20% AND mitoses <20/10 HPF. Reconcile discordant primary and liver samples.',
    'nelm/biology/primary': 'Excluded primaries: lower rectum, esophagus, lung, adrenal and thyroid.',
    'nelm/distribution/spread': 'Anatomic and SSTR staging. Distinguish treated from active nodes; lung/bone exclusions remain separate.',
    'nelm/options/strategy': 'Compare complete resection/ablation, symptoms, tempo, SSTR, SSA, PRRT, systemic and embolization options. Debulking ≠ complete clearance.',
    'nelm/exposure/safety': 'Review PRRT, Y90/embolization, surgery and systemic therapy. NLRB gives no universal PRRT/Y90 sequence or cumulative-dose cutoff.',
    'nelm/observation/imaging': 'Guidance says “at least 3 months prior” to initial/extension request. Confirm chronology and imaging adequacy with allocation leadership.',
    'nelm/review/criteria': 'Confirm grade, portal-drained primary, clearance interval, liver-only disease, functional staging and benefit. Cohort age/burden limits are local choices.',
    'nelm/follow-up/plan': 'Review explant grade/burden, functional symptoms and treatment history; agree NET/transplant recurrence surveillance.',
    'hehe/diagnosis/pathology': 'Expert morphology plus appropriate immunohistochemical/molecular assessment.',
    'hehe/stage/extrahepatic': 'Extrahepatic disease alone does not exclude HEHE exception review. Assess sites, behavior and expected transplant benefit.',
    'hehe/risk/benefit': 'HEHE-LT informs counseling, not MELD points or automatic selection. Some prognostic features require explant.',
    'hehe/review/criteria': 'Confirm biopsy-proven, unresectable HEHE without macrovascular invasion; assess extrahepatic disease effects on benefit and exception review.',
    'hehe/follow-up/plan': 'Reconcile explant/pretransplant findings; plan risk-based, long-term recurrence imaging. No universal OPTN interval.',
    'hca/characterize/diagnosis': 'MRI: burden, growth, bleeding. Review sex, hormones, metabolic disease and subtype. Imaging cannot reliably prove β-catenin activation or always exclude HCC.',
    'hca/standard-care/management': 'Men or proven β-catenin mutation: resection at any size. Women: after lifestyle change/observation, ≥5 cm or growth favors feasible resection.',
    'hca/exception-route/route': 'Any one criterion (OR), not all.',
    'hca/transformation/diagnosis': 'Confirmed HCC → HCC diagnosis/staging pathway. Transformation alone does not establish standard HCC exception eligibility.',
    'hca/review/criteria': 'Confirm the guidance alternative, unresectability where required, prior management and benefit. Narrower molecular thresholds need local agreement.',
    'hca/follow-up/plan': 'While waiting: reassess bleeding/transformation. After transplant: explant review and continuing metabolic/vascular care.',
}
for slug in ['icca', 'crlm', 'nelm', 'hehe', 'hca']:
    help_copy[f'{slug}/review/reviews'] = 'Confirm transplant suitability and MELD-exception review separately; a highlight approves neither.'

labels = {
    'hcc/curative-route/operation': 'Which curative approach fits liver reserve and anatomy?',
    'hcc/listing/exception': 'HCC exception criteria and evidence verified?',
    'hcc/listing/fitness': 'Transplant selection and treatment safety reviewed?',
    'hcc/after-transplant/plan': 'Pathology reviewed and follow-up planned?',
    'pcca/localize/review': 'Transplant reviewed before primary-tumor sampling?',
    'pcca/diagnosis/diagnosis': 'Malignant-appearing stricture plus ≥1 diagnostic criterion?',
    'pcca/diagnosis/biopsy': 'Prior transperitoneal primary-tumor biopsy?',
    'pcca/phenotype/diagnosis': 'Diagnostic criteria and primary-biopsy history acceptable?',
    'pcca/neoadjuvant/protocol': 'Approved center protocol and treatment milestones met?',
    'pcca/staging/stage': 'Operative staging result after neoadjuvant therapy?',
    'pcca/staging/ready': 'Interval imaging, protocol milestones and fitness acceptable?',
    'pcca/follow-up/plan': 'Pathology reviewed and follow-up planned?',
    'icca/follow-up/plan': 'Final clinical review and recurrence plan complete?',
    'crlm/unresectability/clearance': 'Can expert resection/ablation safely clear all liver disease?',
    'crlm/clocks/synchronous': 'Synchronous disease: does treatment sequence fit guidance?',
    'crlm/transplant/plan': 'Benefit–risk review supports transplant, with follow-up agreed?',
    'nelm/exposure/safety': 'Do organ function and prior toxicity permit planned treatment?',
    'nelm/observation/imaging': 'Negative metastatic workup, including functional imaging, accepted?',
    'nelm/follow-up/plan': 'Pathology reviewed and follow-up planned?',
    'hehe/risk/benefit': 'Team assessment of expected transplant benefit?',
    'hehe/follow-up/plan': 'Pathology reviewed and follow-up planned?',
    'hca/standard-care/management': 'Can standard nontransplant treatment address the risk?',
    'hca/follow-up/plan': 'Transplant fitness confirmed and underlying-condition follow-up agreed?',
}
for slug in ['icca', 'crlm', 'nelm', 'hehe', 'hca']:
    labels[f'{slug}/review/criteria'] = 'Disease-specific MELD-exception criteria still met?'
    labels[f'{slug}/review/reviews'] = 'Transplant selection and MELD-exception reviews complete?'

recommendations = {
    'crlm/3/standard/3': 'Broadly unresectable liver disease: leave an asymptomatic primary during systemic therapy. Resect for a local threat, and before transplant after favorable response.',
    'crlm/2/standard/4': 'After clearance: imaging/CEA at 3–6 months, then by risk; review ablation margins at 4–8 weeks; colonoscopy and 2-/5-year follow-up.',
    'crlm/1/standard/2': 'At metastatic diagnosis: obtain RAS, BRAF, MMR/MSI and HER2 results; broaden profiling when an actionable finding would change treatment.',
    'crlm/2/standard/1': 'Small lesions: curative-intent ablation ± resection, treating every original site with a confirmed circumferential margin.',
    'icca/1/standard/0': 'No imaging-only diagnosis. Histology is required before systemic therapy or tissue-defined transplant assessment. Selected clearly resectable masses may proceed directly to surgery after multidisciplinary review.',
    'icca/10/standard/2': 'Evidence: 15 patients with a single tumor ≤2 cm, cancer first diagnosed on explant pathology. Recurrence and survival figures are in the evidence panel.',
    'icca/8/standard/0': 'Discuss adjuvant therapy with the BILCAP limitations: its primary intention-to-treat survival analysis was not statistically significant.',
    'icca/9/standard/0': 'First line: cisplatin–gemcitabine plus a checkpoint inhibitor (durvalumab or pembrolizumab). Trial outcomes and effect sizes are in the evidence panel.',
    'hilar/4/standard/0': 'Refer potentially eligible patients before primary biopsy, treatment outside the transplant protocol, or attempted resection; assess in parallel without delaying indicated curative resection. Do not perform transperitoneal primary biopsy (including EUS/percutaneous) while transplant remains an option. Coordinate intraductal/ERCP and indicated regional-node sampling. Do not delay urgent drainage or infection treatment.',
    'hilar/1/standard/1': 'Record Bismuth–Corlette (ductal pattern); it does not decide resectability. Assess vascular involvement, lobar atrophy, nodes and remnant volume.',
    'hilar/3/standard/0': 'Extended hepatectomy with en bloc extrahepatic bile duct resection, regional nodes and biliary reconstruction; portal-vein resection/reconstruction when needed for R0.',
    'nelm/9/standard/1': 'Maintain complete allocation/renewal records with a named coordinator and physician sign-off. Required record elements are listed in the information panel.',
    'nelm/5/standard/0': 'For meaningful burden reduction: parenchymal-sparing resection, adjunct ablation for unsuitable lesions, and primary resection when appropriate.',
    'nelm/3/standard/0': 'Continue SSA when needed for functional symptoms. After clinically significant progression in nonfunctional disease, do not automatically continue SSA for antiproliferative benefit.',
    'nelm/1/standard/3': 'Document liver burden/distribution/resectability, primary site and resection, extrahepatic sites, and the main clinical problem.',
    'chcca/5/standard/1': 'NLRB exception review: biopsy-proven mixed HCC–iCCA, solitary ≤3 cm, cirrhosis, unresectable, 6 months stability after local/systemic therapy, no extrahepatic disease; MMaT−3.',
    'chcca/1/standard/1': 'Transplant assessment requires biopsy-proven mixed HCC–iCCA. The pCCA transperitoneal-biopsy prohibition does not apply here.',
    'chcca/7/standard/1': 'Before systemic therapy: multigene panel and trial screening. The only randomized trial closed with four patients.',
    'chcca/0/standard/0': 'WHO 2019: unequivocal hepatocytic AND cholangiocytic differentiation within one tumor on H&E. Immunostains are supportive, not essential.',
    'adenoma/4/standard/0': 'Persistent size >5 cm or growth ≥20% is an indication for curative treatment. Explain that 5 cm is a conventional threshold.',
    'adenoma/5/alt/1': 'Stable patient, small peripheral/exophytic bleeding lesion, no local IR: limited resection may be an alternative to transfer.',
    'adenoma/5/standard/0': 'Unstable bleeding: blood-product resuscitation, contrast CT and transfer for embolization; embolization precedes resection.',
    'adenoma/2/standard/2': 'Repeat contrast MRI at 6 months; assess trajectory. This is too early to declare risk-factor modification unsuccessful.',
    'incidental/0/alt/1': 'Vascular liver disorder: use a separate benign-liver-tumor multidisciplinary assessment, outside this pathway’s two arms.',
    'incidental/5/alt/0': 'Vascular liver disorder with regenerative/FNH-like nodules: follow vascular-liver-disease guidance and team-set intervals, not LI-RADS intervals.',
    'incidental/7/standard/0': 'Suspected pCCA: do not perform transperitoneal or primary-tumor needle biopsy until the transplant pathway has been reviewed (local safety rule).',
    'incidental/0/standard/2': 'Outside the HCC at-risk population, imaging criteria cannot establish HCC. An unresolved solid lesion requires tissue.',
    'pdac/2/standard/3': 'No routine drainage before imminent surgery. Drain for cholangitis/fever, severe symptomatic jaundice or delayed surgery, including neoadjuvant therapy.',
    'pdac/2/standard/0': 'High suspicion with planned upfront resection: biopsy confirmation is unnecessary; a nondiagnostic biopsy should not delay surgery.',
    'pdac/1/standard/0': 'Multidisciplinary staging by vessel-contact criteria: exactly one of resectable, borderline resectable, locally advanced or metastatic.',
    'pdac/7/standard/0': 'Multiagent induction chemotherapy if performance, biliary drainage and nutrition permit; schedule reassessment at treatment start.',
    'pnet/4/standard/1': 'Observation evidence: three uncontrolled cohorts, 2–4 years follow-up; no randomized or direct strategy comparison.',
    'pnet/5/alt/0': 'Small, superficial tumor clear of the main duct: consider enucleation/central pancreatectomy at an experienced center, with the nodal question settled before incision.',
    'pnet/3/alt/0': 'Unlocalized insulinoma after CT/MRI and EUS: GLP-1 receptor imaging or arterial stimulation with venous sampling, not another anatomic study.',
    'pnet/7/standard/1': 'MEN1: resect functional tumors at any size; observe nonfunctional <1 cm; resect >2 cm or significant growth. Surgery will not clear the gland.',
    'pcyst/2/standard/0': 'If fit for pancreatectomy, resect for: jaundice with a head cyst; enhancing mural nodule ≥5 mm or solid component; main duct ≥10 mm; or suspicious/positive high-grade dysplasia/carcinoma cytology.',
    'pcyst/1/standard/0': 'MRI/MRCP: characterize the cyst and record main duct diameter in mm; 5-/10-mm thresholds affect management.',
    'pcyst/8/alt/1': 'Consider earlier resection in young, fit patients facing decades of surveillance; explain that surveillance duration motivates this choice.',
    'pcyst/9/alt/0': 'In a fit patient, consider stopping cyst surveillance while remaining alert to a separate pancreatic adenocarcinoma.',
    'ampullary/1/standard/0': 'An adenoma biopsy does not exclude underlying carcinoma: reported sampling false-negative rate 20–40%.',
    'ampullary/9/standard/0': 'After papillectomy/ampullectomy: duodenoscopy with scar/abnormal-area biopsies within 3 months, at 6 and 12 months, then yearly for ≥5 years.',
    'ampullary/2/alt/0': 'If en bloc removal is impossible and benign disease would otherwise require pancreatoduodenectomy: consider piecemeal resection plus residual-tissue ablation, accepting higher recurrence.',
    'ampullary/0/standard/3': 'Name the histologic primary by epicenter: ampulla, duodenum, distal bile duct or pancreatic head. Shared surgery does not imply shared prognosis.',
    'hcc/C/alt/0': 'Consider radiation or radioembolization with systemic therapy. Evidence used sorafenib comparators; RTOG 1112 missed its primary survival endpoint, and Asan used TACE–radiation. Neither tested an immunotherapy backbone.',
    'hcc/B/standard/0': 'Superselective conventional/DEB-TACE: define delivery, response target and when to stop or switch.',
    'hcc/C/standard/0': 'Systemic therapy is primary. If eligible, start an immunotherapy combination; do not delay it for a liver-directed procedure.',
}

out = {'version': '2026-10-25.2', 'headings': {}, 'help': {}, 'recommendations': {}}
for p in data['index']:
    for step in p['steps']:
        key = p['slug'] + '/' + step['id']
        out['headings'][key] = {'source': step['question'], 'concise': headings[key]}
for key, a in data['assistants'].items():
    for q in a['questions']:
        if not q.get('help'):
            continue
        qkey = key + '/' + q['id']
        out['help'][qkey] = {'source': q['help'], 'concise': help_copy.get(qkey, q['help']), 'title': q['label'], 'label': labels.get(qkey, q['label'])}
assert set(help_copy) <= set(out['help'])
for key, concise in recommendations.items():
    slug, step, group, index = key.split('/')
    source = next(s for s in roadmaps[slug] if s['id'] == step)[group][int(index)]['t']
    out['recommendations'][key] = {'source': source, 'concise': concise}
(ROOT / 'assets/contextual-copy.js').write_text('/* Reviewed display copy; exact source guards prevent stale summaries. */\nwindow.ContextualCopy = ' + json.dumps(out, ensure_ascii=False, indent=2) + ';\n')
print({k: len(v) for k, v in out.items() if isinstance(v, dict)})
