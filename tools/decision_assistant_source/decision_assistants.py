"""Essential, source-linked choices for the 46 existing transplant decisions.

These rules select a passage to review, not a transplant eligibility verdict.
Stop/clarification rules precede proceed rules. Every proceed rule specifies all
questions in that decision. No identifiers, raw clinical records or dates.
"""
VERSION = '2026-10-24.5'

def option(value, label, *details):
    return dict(value=value, label=label, details=list(details))

def question(id, label, options, refs, help='', criteria=()):
    return dict(id=id, label=label, options=options+[option('unknown','Uncertain / not yet assessed')],
                refs=list(refs), help=help, criteria=list(criteria))

def criterion(title, items, refs, show_for=()):
    return dict(title=title, items=items, refs=list(refs), show_for=list(show_for))

def rule(when, branch=None, kind=None, title=None, text=None, refs=()):
    return dict(when=when, branch=branch, kind=kind, title=title, text=text, refs=list(refs))

def pause(when, title, text, refs):
    return rule(when, kind='hold', title=title, text=text, refs=refs)

def stop(when, text, refs, title='Review the treatment and transplant plan'):
    return rule(when, kind='stop', title=title, text=text, refs=refs)

def yesno(id, label, refs, help='', yes='Yes', no='No'):
    return question(id,label,[option('yes',yes),option('no',no)],refs,help)

ASSISTANTS={}
def add(pathway, step, questions, rules):
    ASSISTANTS[f'{pathway}/{step}']=dict(questions=questions,rules=rules)

H=['H-policy','H-aasld']; P=['P-policy','P-cohort']; I=['N-icca','I-cohort']
C=['N-crlm','C-transmet']; N=['N-net','NET-milan']; E=['N-hehe','E-consensus']; A=['N-hca','A-easl']

MILAN=criterion('Milan criteria',[
    'One HCC ≤5 cm, OR 2–3 HCCs each ≤3 cm.',
    'No macrovascular tumor invasion or extrahepatic tumor spread.',
    'Milan describes tumor selection. It is not identical to the T2 MELD-exception definition.'
],['H-milan','H-aasld'],['','t2','t1'])
T2=criterion('T2 size criteria for the standard exception',[
    'One qualifying Class 5 lesion 2–5 cm, OR 2–3 qualifying lesions each 1–3 cm.',
    'A single 1 to <2 cm HCC is T1: within Milan size limits but outside standard T2 exception criteria.'
],['H-policy'],['t2','t1'])
DS=criterion('UNOS downstaging: pretreatment inclusion criteria',[
    'One Class 5 lesion >5 to ≤8 cm; OR',
    '2–3 Class 5 lesions: at least one >3 cm, each ≤5 cm, and summed diameters ≤8 cm; OR',
    '4–5 Class 5 lesions: each <3 cm, with summed diameters ≤8 cm.',
    'No macrovascular invasion or extrahepatic disease. After treatment, viable tumor burden must meet T2 size requirements; AFP and observation requirements also apply.',
    'The current OPTN policy uses strictly <3 cm for the 4–5 lesion group, even though some study summaries use ≤3 cm.'
],['H-policy','H-yao','H-merits'],['ds'])
AFP_HELP='If AFP has never exceeded 1,000 ng/mL: current AFP ≤1,000. If it ever exceeded 1,000: treatment must reduce AFP to <500 and it must remain <500.'

add('hcc','diagnosis',[
 question('diagnosis','What establishes the diagnosis?',[
  option('hcc','HCC established by eligible LR-5 imaging or pathology'),
  option('lr4','LR-4: probable HCC'),option('lr3','LR-3: intermediate probability'),
  option('inadequate','Imaging incomplete or technically inadequate'),option('other','LR-M or a non-HCC diagnosis')],H,
  'Imaging-only diagnosis requires the appropriate at-risk population. AFP alone does not diagnose HCC.'),
], [stop({'diagnosis':'other'},'Establish the tumor type before using the HCC pathway. LR-M requires diagnostic assessment; do not count it as HCC.',H),
 rule({'diagnosis':['lr4','lr3','inadequate']},1),rule({'diagnosis':'hcc'},0)])

add('hcc','curative-route',[
 question('spread','What is the status of vascular invasion, extrahepatic spread or prior tumor rupture?',[
  option('clear','None of these findings'),option('excluded','Active invasion, spread or rupture'),option('prior','Previously treated rupture or vascular invasion')],['N-hcc']),
 question('operation','Which curative approach is supported by liver reserve and anatomy?',[
  option('resection','Safe complete resection is feasible'),option('transplant','Transplant is favored and fitness is acceptable'),
  option('review','Neither approach is established / fitness unresolved')],H,
  'Resection is favored by limited burden, compensated liver, no clinically significant portal hypertension and adequate remnant. Early HCC with decompensation or significant portal hypertension may favor transplant.'),
], [stop({'spread':'excluded'},'Active extrahepatic spread, macrovascular invasion or tumor rupture prevents a standardized HCC MELD exception. Reassess the transplant plan and review other HCC treatments.',['N-hcc']),
 pause({'spread':'prior'},'Review prior rupture or vascular invasion','Previously treated rupture or portal-branch invasion requires individual review by the transplant program and the NLRB if HCC MELD-exception points are requested.',['N-hcc']),
 pause({'operation':'review'},'Clarify the curative treatment plan','Review liver reserve, resection feasibility and transplant fitness.',H),
 rule({'spread':'clear','operation':'resection'},0),rule({'spread':'clear','operation':'transplant'},1)])

add('hcc','allocation',[
 question('burden','Which pretreatment tumor pattern applies?',[
  option('t2','Within Milan and meets T2'),option('t1','Within Milan, but single T1 tumor (1 to <2 cm)'),
  option('ds','Beyond Milan, within UNOS downstaging criteria'),option('beyond','Beyond UNOS downstaging criteria'),
  option('other','Other / qualifying lesion classification unresolved')],['H-milan','H-policy','H-merits'],
  'Use the confirmed pretreatment lesion count and sizes, not just the treated scan.',[MILAN,T2,DS]),
 question('afp','Does AFP meet the HCC MELD-exception requirement?',[
  option('met','Yes — applicable AFP rule met'),option('not-met','No — AFP requirement not met')],['H-policy'],AFP_HELP),
 yesno('spread','Has imaging excluded macrovascular tumor invasion and extrahepatic disease?', ['H-policy','N-hcc']),
], [stop({'spread':'no'},'Macrovascular tumor invasion or extrahepatic disease prevents a standardized HCC MELD exception. Reassess transplant suitability and review other HCC treatment options.',['H-policy','N-hcc']),
 pause({'burden':'other'},'Clarify the qualifying tumor burden','Confirm qualifying Class 5 lesions and pretreatment measurements before determining whether a standardized HCC MELD-exception request is appropriate.',['H-policy']),
 rule({'burden':'beyond'},3),
 rule({'burden':'t1','spread':'yes'},2),
 pause({'afp':'not-met'},'AFP does not meet the HCC MELD-exception requirement','Reassess AFP trend, viable tumor, liver function and treatment response. Choose the next treatment or individual exception review from the options below; tumor size alone does not establish eligibility for HCC MELD-exception points.',['H-policy','N-hcc','NCCN-hcc']),
 rule({'burden':'t2','afp':'met','spread':'yes'},0),rule({'burden':'ds','afp':'met','spread':'yes'},1)])

add('hcc','treatment',[
 question('response','What does post-treatment imaging show?',[
  option('controlled','Viable burden within required limits / no viable tumor'),option('residual','Residual burden above limits or equivocal response'),
  option('spread','New macrovascular invasion or extrahepatic disease')],H,
  'Assess viable tumor separately from the treated cavity and retain pretreatment stage. For downstaging, guidance advises imaging ≥4 weeks after the last treatment.'),
 yesno('afp','Required AFP response maintained?', ['H-policy'],AFP_HELP),
 yesno('reserve','Liver reserve and treatment safety acceptable?', ['H-aasld'],
  'Treatment-related decompensation needs reassessment. Prior checkpoint immunotherapy requires transplant/pharmacy review before transplantation.'),
], [stop({'response':'spread'},'New macrovascular invasion or extrahepatic disease prevents a standardized HCC MELD exception and requires a new treatment and transplant assessment.',['N-hcc']),
 rule({'response':'residual'},1),rule({'afp':'no'},1),rule({'reserve':'no'},1),
 rule({'response':'controlled','afp':'yes','reserve':'yes'},0)])

add('hcc','listing',[
 yesno('exception','Applicable HCC MELD-exception criteria and supporting evidence verified?', ['H-policy'],
  'Baseline/response imaging, qualifying lesions, AFP history, chest staging and resection assessment. Adults retain calculated MELD initially and at first extension; later eligible extensions use MMaT−3.'),
 yesno('fitness','Transplant selection and treatment-safety reviews complete?', ['H-aasld','N-hcc'],
  'Include cardiopulmonary, infectious, functional and psychosocial suitability; any prior ICI exposure needs a specific rejection-risk plan.'),
], [rule({'exception':'no'},1),rule({'fitness':'no'},1),rule({'exception':'yes','fitness':'yes'},0)])

add('hcc','waitlist',[
 question('control','Current tumor / AFP assessment?',[
  option('maintained','Qualifying disease control and AFP maintained'),option('equivocal','Equivocal enhancement or AFP change'),
  option('lost','HCC exception renewal criteria no longer met, or new tumor spread')],H,
  'Use updated liver imaging, AFP and treatment history. No residual enhancement is required after complete treatment; preserve the original qualifying history.'),
 yesno('fitness','Still clinically suitable for transplantation?', ['H-aasld']),
], [stop({'control':'lost'},'Request individual review if automatic HCC MELD-exception renewal criteria are no longer met. New metastasis or macrovascular invasion also requires reassessment of transplant suitability.',['H-policy','N-hcc']),
 rule({'control':'equivocal'},1),pause({'fitness':'no'},'Reassess transplant readiness','Resolve the new clinical safety concern before activating the patient for organ offers or accepting an organ.',['H-aasld']),
 rule({'control':'maintained','fitness':'yes'},0)])

def follow_up(pathway, step, refs, help, title='Are pathology review and the follow-up plan in place?'):
 add(pathway,step,[
  yesno('plan',title,refs,help),
  question('concern','Any new concerning finding?',[
   option('none','No unresolved concern'),option('concern','Possible recurrence, progression or new safety concern')],refs),
 ],[pause({'concern':'concern'},'Evaluate the new finding','Ask the relevant tumor and transplant teams to assess the new finding and revise treatment or surveillance as needed.',refs),
    pause({'plan':'no'},'Complete the follow-up plan','Review pathology, agree the surveillance schedule and identify the team that will evaluate suspected recurrence.',refs),
    rule({'plan':'yes','concern':'none'},0)])

follow_up('hcc','after-transplant',['H-aasld','H-policy'],
 'Review explant viable burden and vascular invasion; arrange abdominal/chest surveillance. The HCC exception explant report is due within 60 days. Surveillance intervals are individualized.')

add('pcca','localize',[
 question('origin','Where does the lesion arise?',[
  option('hilar','Perihilar bile duct'),option('other','Intrahepatic or distal bile duct')],['C-aasld'],
  'Use MRI/MRCP or appropriate CT to establish the duct of origin; distinguish the radial mass from its length along the bile duct.'),
 yesno('review','Has the transplant team considered transplantation before primary-tumor sampling?',P,
  'Assess liver disease, resection options and benign causes of the stricture before choosing a biopsy approach.'),
], [rule({'origin':'other'},1),pause({'review':'no'},'Review the transplant option before sampling','Consult the transplant and HPB teams before primary-tumor sampling. A transperitoneal primary-tumor biopsy can affect eligibility for the pCCA transplant protocol.',P),
 rule({'origin':'hilar','review':'yes'},0)])

add('pcca','diagnosis',[
 yesno('diagnosis','Malignant-appearing stricture plus at least one diagnostic criterion?',P,'At least one: malignant biopsy/cytology; CA 19-9 >100 U/mL without cholangitis; aneuploidy; or a hilar mass <3 cm radially.'),
 question('biopsy','Has the primary tumor been sampled through the peritoneum?',[
  option('no','No'),option('yes','Yes — transperitoneal primary-tumor biopsy')],P,
  'Avoid transperitoneal EUS, percutaneous or operative biopsy of the primary. Sampling a regional node without traversing the primary is a different procedure.'),
], [stop({'biopsy':'yes'},'Ask the transplant program to review the biopsy approach, tumor-seeding risk and eligibility for its pCCA transplant protocol before enrollment.',P,'Primary-biopsy history requires review'),
 rule({'diagnosis':'no'},1),rule({'diagnosis':'yes','biopsy':'no'},0)])

add('pcca','phenotype',[
 question('size','What is the radial mass size?',[
  option('small','Single mass <3 cm'),option('none','No discrete mass'),option('large','Mass ≥3 cm or multiple masses')],P,
  'Measure perpendicular to the bile duct. Exactly 3 cm does not meet <3 cm; longitudinal duct involvement is not this measurement.'),
 yesno('unresectable','Unresectable because of anatomy or underlying liver disease?',P),
 question('spread','Regional nodes, intrahepatic metastases or extrahepatic spread?',[
  option('clear','No metastatic disease identified'),option('present','Metastatic disease present')],P,
  'Chest/abdominal imaging must exclude metastases within 90 days before the initial exception request.'),
 yesno('diagnosis','Hilar diagnostic criteria met and primary-biopsy history acceptable?',P,
  'Confirm the preceding diagnostic assessment, including avoidance of transperitoneal primary-tumor biopsy.'),
], [stop({'spread':'present'},'Metastatic disease excludes transplantation under this pCCA protocol. Review other cancer treatments and symptom management.',P),
 rule({'size':'large'},1),rule({'unresectable':'no'},1),
 pause({'diagnosis':'no'},'Resolve diagnosis and biopsy-related eligibility concerns','Return to the diagnostic assessment with the transplant team.',P),
 rule({'size':['small','none'],'unresectable':'yes','spread':'clear','diagnosis':'yes'},0)])

add('pcca','neoadjuvant',[
 yesno('protocol','Approved center protocol and required treatment milestones satisfied?',P,
  'The written protocol includes selection, neoadjuvant therapy and operative staging. Regimen modifications require program review.'),
 question('status','Current disease control and clinical condition?',[
  option('safe','No progression; drainage, infection and toxicity controlled'),option('complication','Cholangitis, toxicity or incomplete recovery'),
  option('spread','Metastatic progression')],P),
], [stop({'status':'spread'},'Metastatic progression excludes transplantation under this pCCA protocol. Review other cancer treatments and symptom management.',P),
 rule({'protocol':'no'},1),rule({'status':'complication'},1),rule({'protocol':'yes','status':'safe'},0)])

add('pcca','staging',[
 question('stage','What did operative staging after neoadjuvant therapy show?',[
  option('negative','Complete staging: no nodal, liver or peritoneal metastasis'),
  option('positive','Regional node, intrahepatic or extrahepatic metastasis'),
  option('incomplete','Not performed, incomplete or pathology indeterminate')],P,
  'Assess regional hepatic nodes and the peritoneum after neoadjuvant therapy, before transplant. Negative EUS before therapy does not replace operative staging.'),
 yesno('ready','Interval imaging, protocol milestones and clinical fitness acceptable?',P,
  'Reconcile interval imaging with operative findings; resolve cholangitis and other active safety issues.'),
], [stop({'stage':'positive'},'Positive regional nodes, intrahepatic metastases or other metastases exclude transplantation under this pCCA protocol.',P),
 rule({'stage':'incomplete'},1),pause({'ready':'no'},'Resolve the remaining transplant-readiness issue','Review interval imaging, treatment completion, infection control and clinical fitness before confirming readiness for transplantation.',P),
 rule({'stage':'negative','ready':'yes'},0)])

add('pcca','listing',[
 yesno('evidence','Required exception evidence and imaging current?',P,
  'Diagnostic and approved-protocol evidence must be complete. Chest/abdomen imaging: within 90 days for the initial request; within 30 days for extension.'),
 question('ready','Final staging and transplant readiness?',[
  option('ready','No metastases at operative staging; protocol requirements met and fitness confirmed'),
  option('pending','Transplant assessment incomplete or a new abnormality unresolved'),option('spread','New metastatic disease')],P),
], [stop({'ready':'spread'},'New metastatic disease excludes transplantation under this pCCA protocol; review other cancer treatments.',P),rule({'evidence':'no'},1),rule({'ready':'pending'},1),
 rule({'evidence':'yes','ready':'ready'},0)])
follow_up('pcca','follow-up',P,'Review residual disease, nodes and margins. Agree recurrence surveillance jointly with oncology and transplantation; there is no universal OPTN surveillance regimen.')

add('icca','diagnosis',[
 question('histology','What does expert pathology show?',[
  option('icca','Biopsy-proven iCCA'),option('mixed','Mixed HCC–iCCA'),option('other','Other primary / metastatic cancer')],['N-icca','C-aasld'],
  'Confirm tissue diagnosis; exclude metastasis from another primary. Mixed HCC–iCCA is included in current guidance, but local program acceptance must be explicit.'),
 yesno('extent','Liver tumor map and metastatic staging complete?',I),
], [stop({'histology':'other'},'Use the pathway for the verified tumor type.',['C-aasld']),
 rule({'histology':'mixed'},1),rule({'extent':'no'},1),rule({'histology':'icca','extent':'yes'},0)])

add('icca','phenotype',[
 question('focality','How many confirmed malignant liver nodules?',[
  option('solitary','One solitary iCCA / mixed HCC–iCCA'),option('multiple','Multiple malignant nodules, including satellites'),
  option('uncertain','An additional nodule is indeterminate / separate HCC possible')],['N-icca','I-focality','I-satellites'],
  'Multifocal = ≥2 separate tumor nodules. Satellites = nearby separate nodules, without a universal distance cutoff. Intrahepatic metastasis describes spread within the liver; distribution alone cannot establish clonality.',[
   criterion('How this changes the transplant discussion',[
    'A confirmed iCCA satellite or additional iCCA nodule does not meet the solitary-tumor criterion for the described MELD exception. A separate HCC requires individual program and NLRB interpretation.',
    'Multiple liver nodules do not by themselves establish distant M1 disease.',
    'An indeterminate nodule may be benign or another tumor: clarify it rather than assuming multifocal iCCA.'
   ],['N-icca','I-focality','I-satellites'],['multiple','uncertain'])]),
 question('profile','Size, liver background and resection assessment?',[
  option('fits','≤3 cm, cirrhosis, and no safe complete resection'),
  option('outside','>3 cm, noncirrhotic, or resectable')],I,
  'These are the current NLRB guidance criteria. The foundational “very early” cohort studied a narrower ≤2 cm group; it does not alone validate every ≤3 cm case.'),
 yesno('spread','Has staging excluded extrahepatic disease?', ['N-icca']),
 yesno('program','Has the local iCCA transplant program accepted the case for continued evaluation?',I),
], [stop({'spread':'no'},'Extrahepatic disease excludes the patient from the iCCA transplant protocol described here; review other cancer treatments.',['N-icca']),
 rule({'focality':'multiple'},1),rule({'profile':'outside'},1),
 pause({'focality':'uncertain'},'Clarify the additional nodule','Review imaging and pathology; biopsy may help if it would change management. Separate HCC alongside iCCA requires explicit program/NLRB interpretation.',['N-icca','I-focality']),
 pause({'program':'no'},"Obtain the iCCA transplant program's selection decision",'The transplant program must assess expected benefit and fitness for transplantation even when tumor size and cirrhosis criteria are met.',I),
 rule({'focality':'solitary','profile':'fits','spread':'yes','program':'yes'},0)])

add('icca','therapy',[
 question('control','Tumor status during therapy?',[
  option('controlled','Solitary tumor ≤3 cm, no new lesions or extrahepatic disease'),option('unclear','Response unclear'),
  option('progression','Growth beyond criteria / new tumor or metastasis')],['N-icca']),
 yesno('safe','Treatment tolerable and transplant safety reviewed?', ['N-icca','C-aasld'],
  'Review liver function and toxicity. Assess rejection risk with the transplant team before checkpoint immunotherapy when transplantation remains an option.'),
], [stop({'control':'progression'},'The patient no longer meets the described iCCA transplant criteria. Reassess treatment and obtain program review before proposing further transplant evaluation.',['N-icca']),
 rule({'control':'unclear'},1),rule({'safe':'no'},1),rule({'control':'controlled','safe':'yes'},0)])

add('icca','stability',[
 question('duration','Has the full qualifying stability period been met?',[
  option('met','At least 6 months, with the starting point agreed'),option('short','Less than 6 months / starting point unresolved')],['N-icca'],
  'Guidance specifies 6 months from diagnosis or last treatment. The team must establish the applicable start; a good early response is not the full interval.'),
 question('disease','Disease throughout that period?',[
  option('stable','Solitary ≤3 cm, no new lesions or extrahepatic disease'),option('progression','Progression or a new malignant lesion')],['N-icca']),
], [stop({'disease':'progression'},'Reassess the iCCA treatment and transplant plan. A new observation interval requires program review after progression or a new malignant lesion.',['N-icca']),
 rule({'duration':'short'},1),rule({'duration':'met','disease':'stable'},0)])

def review_step(pathway, step, refs, help, target=0, hold=1, loss_text='Reassess the treatment plan and eligibility for the disease-specific MELD exception. Any further transplant proposal needs an explicit selection-team decision.'):
 add(pathway,step,[
  question('criteria','Are the disease-specific MELD-exception criteria still met?',[
   option('met','Yes, with current supporting tests'),option('pending','Tests incomplete / a finding unresolved'),option('lost','A required criterion is no longer met')],refs,help),
  yesno('reviews','Are the transplant selection decision and applicable MELD-exception review complete?',refs,
   "Record the transplant team's decision on clinical suitability separately from the decision on MELD-exception points. The highlighted text does not approve either decision."),
 ],[stop({'criteria':'lost'},loss_text,refs),rule({'criteria':'pending'},hold),rule({'reviews':'no'},hold),
    rule({'criteria':'met','reviews':'yes'},target)])

review_step('icca','review',I,'Confirm biopsy, cirrhosis, unresectability, solitary ≤3 cm disease and ≥6 months stability. Extensions require imaging every 3 months with continuing control.')
follow_up('icca','follow-up',I,'Reconfirm disease control, fitness and informed consent. Review explant findings and agree oncology/transplant surveillance; selected cohort evidence does not establish a universal interval.',
 'Final clinical review and recurrence-surveillance plan complete?')

add('crlm','map-disease',[
 yesno('primary','Colorectal adenocarcinoma confirmed and liver burden mapped?',C,
  'Use primary pathology, pretreatment liver imaging and current liver/chest/abdomen/pelvis staging.'),
 question('spread','Extrahepatic disease / local primary recurrence?',[
  option('clear','No excluded extrahepatic site or local recurrence'),option('equivocal','Indeterminate extrahepatic finding'),
  option('present','Extrahepatic disease after primary resection or local relapse')],['N-crlm']),
], [stop({'spread':'present'},'This finding excludes CRLM MELD-exception consideration under the described NLRB guidance. Review other colorectal cancer treatments.',['N-crlm']),
 rule({'spread':'equivocal'},1),pause({'primary':'no'},'Complete diagnosis and the disease map','Confirm primary histology and baseline/current disease extent.',C),
 rule({'primary':'yes','spread':'clear'},0)])

add('crlm','biology',[
 question('molecular','BRAF and MSI/MMR profile?',[
  option('fits','BRAF wild type and microsatellite stable'),option('outside','BRAF-mutant or MSI-H / dMMR')],['N-crlm','C-consensus']),
 question('cea','Current CEA?',[
  option('low','<80 µg/L'),option('boundary','Exactly 80 µg/L'),option('high','>80 µg/L')],['N-crlm'],
  'µg/L and ng/mL have the same numeric value. Initial guidance excludes >80; extensions require <80. Resolve exactly 80 explicitly.'),
 yesno('size','Every pretreatment liver lesion ≤10 cm?', ['N-crlm']),
], [rule({'molecular':'outside'},1),stop({'cea':'high'},'CEA >80 µg/L excludes an initial CRLM MELD exception under the described guidance, even if the value is falling.',['N-crlm']),
 stop({'size':'no'},'A pretreatment liver lesion >10 cm does not meet the CRLM MELD-exception criteria described in NLRB guidance.',['N-crlm']),
 pause({'cea':'boundary'},'Clarify the CEA boundary','Obtain allocation review rather than assuming that exactly 80 satisfies both initial and extension wording.',['N-crlm']),
 rule({'molecular':'fits','cea':'low','size':'yes'},0)])

add('crlm','unresectability',[
 question('clearance','Can an expert liver team safely treat all liver disease by resection or ablation?',[
  option('yes','Yes — resection and/or ablation is feasible'),option('no','No — unresectable after expert review'),
  option('uncertain','Only scars / disappearing lesions or disputed viability')],['C-consensus','C-transmet'],
  'Review remnant, vascular/biliary anatomy, staged or parenchymal-sparing resection and combined ablation. Tumor count alone does not establish unresectability.'),
], [rule({'clearance':'yes'},0),rule({'clearance':'no'},1),rule({'clearance':'uncertain'},2)])

add('crlm','control',[
 question('response','Disease course during therapy?',[
  option('controlled','Stable or regressing, without new extrahepatic disease'),option('progression','Progression / new lesion')],C,
  'The NLRB footnote describes >10% lesion-diameter growth or a new lesion. Do not equate that threshold with usual RECIST 1.1 progression.'),
 yesno('duration','At least 6 months of qualifying control during systemic and/or local therapy?', ['N-crlm']),
 yesno('unresectable','Still no feasible curative resection / ablation after response?', ['C-consensus']),
], [stop({'response':'progression'},'Progression does not meet the CRLM MELD-exception guidance criteria. Reassess systemic treatment and other cancer-control options.',['N-crlm']),
 rule({'duration':'no'},1),pause({'unresectable':'no'},'Revisit the nontransplant curative option','If all liver disease may now be treated safely by resection or ablation, obtain an updated HPB surgical assessment.',['C-consensus']),
 rule({'response':'controlled','duration':'yes','unresectable':'yes'},0)])

add('crlm','clocks',[
 yesno('primary','Primary R0-resected with no local recurrence?', ['N-crlm'],
  'Confirm negative margins and colonoscopy excluding recurrence within 12 months before the request.'),
 yesno('interval','At least 12 months since CRLM diagnosis?', ['N-crlm']),
 question('synchronous','For synchronous disease, does the actual treatment sequence fit guidance?',[
  option('na','Not synchronous — additional sequence does not apply'),option('met','Synchronous — all listed intervals met'),
  option('different','Synchronous — different sequence / interval incomplete')],['N-crlm'],
  'Synchronous = primary colorectal cancer and liver metastases present together.',[
   criterion('Additional guidance for synchronous disease',[
    'Primary resection more than 6 months after initial diagnosis.',
    'At least 6 months of chemotherapy after primary resection before the request.',
    'At least 12 months total disease stability after initial diagnosis.',
    'Do not delay appropriate primary treatment to fit this sequence; seek individual interpretation when it differs.'
   ],['N-crlm'],['met','different'])]),
], [stop({'primary':'no'},'Treat residual or recurrent primary colorectal cancer before reconsidering a CRLM MELD-exception request.',['N-crlm']),
 rule({'interval':'no'},1),rule({'synchronous':'different'},1),
 rule({'primary':'yes','interval':'yes','synchronous':['na','met']},0)])

add('crlm','restaging',[
 question('stage','What does current restaging show?',[
  option('clear','Liver-only disease; no local primary recurrence'),option('equivocal','Equivocal PET or other unresolved lesion'),
  option('spread','Confirmed extrahepatic disease / local relapse')],['N-crlm']),
 yesno('timing','Required studies and PET timing satisfied?', ['N-crlm'],
  'CT/MRI chest, abdomen and pelvis AND PET within 1 month of the initial request. Guidance specifies PET after ≥4 weeks off chemotherapy; coordinate any pause with oncology. ctDNA does not substitute.'),
 yesno('control','Tumor control and CEA still satisfy the reviewed criteria?',C),
], [stop({'stage':'spread'},'Confirmed extrahepatic disease or local primary recurrence excludes CRLM MELD-exception consideration under the described guidance.',['N-crlm']),
 rule({'stage':'equivocal'},1),rule({'timing':'no'},1),pause({'control':'no'},'Reassess control and biomarker criteria','Review the change in imaging or CEA before submitting a CRLM MELD-exception request.',C),
 rule({'stage':'clear','timing':'yes','control':'yes'},0)])
review_step('crlm','review',C,'Confirm the initial selection evidence. For renewal: CT/MRI chest/abdomen/pelvis and CEA every 3 months, no progression or extrahepatic disease, and CEA <80 µg/L.')
follow_up('crlm','transplant',C,'Recheck disease control, fitness and consent, and whether resection or ablation can now treat all liver disease. Agree recurrence surveillance and postoperative oncology care.',
 'Final benefit–risk review supports transplant and follow-up is agreed?')

add('nelm','biology',[
 question('grade','Differentiation / grade?',[
  option('fits','Well-differentiated G1/G2; Ki-67 and mitoses below guidance limits'),
  option('outside','G3, poorly differentiated NEC or discordant aggressive biology')],N,
  'Guidance specifies Ki-67 (proliferative index) <20% and mitoses <20 per 10 HPF. Reconcile discordant primary and liver samples.'),
 yesno('primary','Gastroenteropancreatic primary with portal-system drainage?', ['N-net'],
  'Lower rectal, esophageal, lung, adrenal and thyroid primaries do not meet the NET MELD-exception criteria.'),
], [stop({'primary':'no'},'The primary site does not meet the NET MELD-exception criteria; use the treatment pathway for the confirmed tumor type.',['N-net']),
 rule({'grade':'outside'},1),rule({'grade':'fits','primary':'yes'},0)])

add('nelm','distribution',[
 yesno('primary','Primary removed, with unresectable liver metastases remaining?', ['N-net']),
 question('spread','Extrahepatic disease history and current status?',[
  option('none','No active or prior excluded extrahepatic site'),option('cleared','Permitted prior extrahepatic disease now cleared'),
  option('active','Active extrahepatic progression'),option('solid','Lung or bone metastasis history')],['N-net'],
  'Confirm anatomic and somatostatin-receptor functional staging. A treated node is different from an active metastatic node; lung/bone exclusions remain separate.'),
], [stop({'spread':'solid'},'NLRB guidance describes lung or bone metastases as permanent exclusions from this NET transplant selection framework. Review nontransplant treatment options.',['N-net']),
 stop({'spread':'active'},'Active extrahepatic progression requires transplant-listing review; NLRB guidance advises delisting. Review the treatment plan with the NET team.',['N-net']),
 pause({'primary':'no'},'Resolve primary control and liver resectability','Complete treatment of the primary and assess whether resection or ablation can treat all liver disease.',['N-net']),
 rule({'primary':'yes','spread':'cleared'},1),rule({'primary':'yes','spread':'none'},0)])

add('nelm','options',[
 question('strategy','Which strategy currently offers the best clinical benefit?',[
  option('transplant','Complete resection or ablation unsuitable; tumor board supports transplant evaluation'),
  option('other','Resection, ablation or lower-risk disease control is preferable')],N,
  'Consider complete resection/ablation, symptoms, tempo, SSTR status, SSA, PRRT, systemic and embolization options. Debulking is not complete clearance.',[
   criterion('Milan-NET evidence versus allocation guidance',[
    'The selected Milan-NET cohort used <50% liver involvement and ≥6 months of stable/responding disease.',
    'These cohort criteria are not identical to the NLRB list and do not alone establish a transplant indication.'
   ],N,['transplant'])]),
], [rule({'strategy':'other'},1),rule({'strategy':'transplant'},0)])

add('nelm','exposure',[
 question('safety','Do organ function and prior treatment toxicity permit the planned treatment sequence?',[
  option('acceptable','Yes — hepatic, renal and marrow reserve reviewed'),
  option('concern','Cumulative toxicity or sequencing remains unresolved')],N,
  'Review PRRT, Y90/embolization, operations and systemic therapy. There is no universal NLRB PRRT/Y90 sequence or numerical cumulative-dose cutoff.'),
], [rule({'safety':'concern'},1),rule({'safety':'acceptable'},0)])

add('nelm','observation',[
 question('clearance','Have the primary and any permitted extrahepatic disease been removed without recurrence?',[
  option('met','Removed and recurrence-free for ≥6 months'),option('short','Less than 6 months without recurrence, or removal of extrahepatic disease uncertain'),
  option('recurrence','Extrahepatic recurrence or excluded lung/bone history')],['N-net']),
 yesno('imaging','Negative metastatic workup, including functional imaging, accepted?', ['N-net'],
  'The guidance says “at least 3 months prior” to initial/extension request. Clarify chronology and current imaging adequacy with allocation leadership rather than silently reversing that wording.'),
 yesno('control','Liver disease and clinical profile still appropriate for this program?',N),
], [stop({'clearance':'recurrence'},'Review transplant listing and treatment after extrahepatic recurrence. Previously removed nodal disease may allow later reconsideration; lung or bone metastases remain a separate exclusion in the guidance.',['N-net']),
 rule({'clearance':'short'},1),rule({'imaging':'no'},1),rule({'control':'no'},1),
 rule({'clearance':'met','imaging':'yes','control':'yes'},0)])
review_step('nelm','review',N,'Confirm grade, portal-drained primary, resection/clearance interval, liver-only disease, functional staging and clinical benefit. Age/burden restrictions derived from a cohort remain local selection choices.')
follow_up('nelm','follow-up',N,'Review explant grade/burden, functional symptoms and treatment history. Agree disease-specific recurrence surveillance with the NET and transplant teams.')

add('hehe','diagnosis',[
 question('pathology','Expert pathology conclusion?',[
  option('hehe','Biopsy-proven HEHE; angiosarcoma excluded'),option('angiosarcoma','Angiosarcoma / hemangiosarcoma'),
  option('uncertain','Diagnosis not established')],E,
  'Use expert morphology and appropriate immunohistochemical/molecular assessment.'),
], [stop({'pathology':'angiosarcoma'},'Do not use the HEHE transplant pathway for angiosarcoma.',E),rule({'pathology':'uncertain'},1),rule({'pathology':'hehe'},0)])

add('hehe','stage',[
 yesno('vascular','Has imaging or biopsy excluded macrovascular invasion?', ['N-hehe']),
 question('strategy','Resection, observation or transplant consideration?',[
  option('transplant','Unresectable liver disease; transplant discussion appropriate'),option('other','Resection or observation currently preferable')],E),
 question('extrahepatic','Extrahepatic disease?',[
  option('none','None identified'),option('limited','Limited disease needing case-level review'),option('other','Progressive / incompletely characterized disease')],E,
  'Extrahepatic disease alone does not exclude HEHE MELD-exception consideration under NLRB guidance. Review its sites, behavior and effect on expected transplant benefit.'),
], [stop({'vascular':'no'},'Macrovascular invasion is outside the described HEHE exception criteria.',['N-hehe']),
 pause({'extrahepatic':'other'},'Characterize disease behavior and benefit','Obtain rare-tumor/transplant MDT review rather than applying a blanket extrahepatic exclusion.',E),
 rule({'vascular':'yes','strategy':'other'},1),rule({'vascular':'yes','strategy':'transplant','extrahepatic':'limited'},2),
 rule({'vascular':'yes','strategy':'transplant','extrahepatic':'none'},0)])

add('hehe','risk',[
 yesno('criteria','Unresectable disease without macrovascular invasion remains confirmed?', ['N-hehe']),
 question('benefit','What is the MDT assessment of expected transplant benefit?',[
  option('supported','Benefit supported after review of tempo, sites and alternatives'),option('uncertain','Tempo / benefit remains uncertain')],['E-score','E-consensus'],
  'HEHE-LT registry findings inform counseling; they are not a MELD score or an automatic selection rule. Some prognostic features are known only on explant.'),
], [stop({'criteria':'no'},'Reassess resectability and vascular involvement before requesting a HEHE MELD exception.',['N-hehe']),
 rule({'benefit':'uncertain'},1),rule({'criteria':'yes','benefit':'supported'},0)])
review_step('hehe','review',E,'Confirm biopsy-proven HEHE, unresectability and absence of macrovascular invasion. Document how any extrahepatic disease affects expected transplant benefit and MELD-exception consideration.')
follow_up('hehe','follow-up',['E-score','E-consensus'],'Reconcile explant and pretransplant findings; agree risk-informed imaging and long-term recurrence assessment. No universal OPTN surveillance interval is specified.')

add('hca','characterize',[
 question('diagnosis','Current diagnosis and complication status?',[
  option('hca','HCA confirmed; risk features characterized'),option('malignant','Possible malignant transformation'),
  option('bleeding','Active unstable hemorrhage')],A,
  'MRI assesses burden, growth and bleeding. Consider sex, hormonal exposure, metabolic disease and subtype. Imaging cannot reliably establish β-catenin activation or exclude HCC in every case.'),
], [stop({'diagnosis':'bleeding'},'Stabilize urgently and assess embolization; pause elective transplant decision-making.',['A-easl'],'Treat the bleeding emergency'),
 rule({'diagnosis':'malignant'},1),rule({'diagnosis':'hca'},0)])

add('hca','standard-care',[
 question('bleeding','Any hemodynamically unstable bleeding?',[
  option('no','No'),option('yes','Yes')],['A-easl']),
 question('management','Can the risk be addressed with standard nontransplant management?',[
  option('yes','Yes — observation, resection or local treatment is suitable'),
  option('no','No suitable conventional approach / exceptional syndrome')],A,
  'In men or proven β-catenin-mutated HCA, resection is recommended irrespective of size. In women, after lifestyle modification/observation, ≥5 cm or continued growth favors resection when feasible.'),
], [stop({'bleeding':'yes'},'Treat the acute hemorrhage before elective transplant review.',['A-easl'],'Treat the bleeding emergency'),
 rule({'bleeding':'no','management':'yes'},0),rule({'bleeding':'no','management':'no'},1)])

add('hca','exception-route',[
 question('route','Which HCA criterion supports an individual MELD-exception request?',[
  option('syndrome','HCA with glycogen storage disease or Abernethy malformation'),
  option('beta','Unresectable HCA with β-catenin mutation'),
  option('adenomatosis','Unresectable HCA with >10 adenomas'),
  option('complicated','Unresectable + nonoperative treatment failure + progression/complication'),
  option('none','None of these / multiplicity alone')],['N-hca'],
  'These are alternatives (OR), not requirements that must all be present.',[
   criterion('Treatment-failure alternative: all three required',[
    'Unresectable.',
    'Unresponsive to nonoperative management.',
    'Progressive, or complicated by hemorrhage, rupture or malignant transformation.'
   ],['N-hca'],['complicated'])]),
], [rule({'route':'none'},1),rule({'route':['syndrome','beta','adenomatosis','complicated']},0)])

add('hca','transformation',[
 question('diagnosis','Is malignant transformation established?',[
  option('benign','HCA remains the verified diagnosis'),option('malignant','Malignancy established'),option('uncertain','Malignancy remains unresolved')],A,
  'If HCC is diagnosed, use the HCC diagnostic and staging assessments. Malignant transformation alone does not establish eligibility for a standardized HCC MELD exception.'),
], [pause({'diagnosis':'uncertain'},'Resolve the diagnosis','Review imaging/pathology and consider additional tissue when management depends on it.',A),
 rule({'diagnosis':'malignant'},1),rule({'diagnosis':'benign'},0)])
review_step('hca','review',A,'Confirm the specific guidance alternative, unresectability where required, prior management and expected benefit. Molecular thresholds narrower than guidance need explicit local agreement.')
follow_up('hca','follow-up',A,'Reassess bleeding or transformation while waiting. After transplant, review explant findings and continuing care for the underlying metabolic/vascular condition.',
 'Fitness for transplantation confirmed and follow-up for the underlying condition agreed?')

assert len(ASSISTANTS)==46

# One explicit illustrative path per disease. These are example choices, not
# inferred findings, completion flags, or changes to the matching rules.
EXAMPLES = {
 'hcc/diagnosis': {'diagnosis':'hcc'},
 'hcc/curative-route': {'spread':'clear','operation':'transplant'},
 'hcc/allocation': {'burden':'t2','afp':'met','spread':'yes'},
 'hcc/treatment': {'response':'controlled','afp':'yes','reserve':'yes'},
 'hcc/listing': {'exception':'yes','fitness':'yes'},
 'hcc/waitlist': {'control':'maintained','fitness':'yes'},
 'hcc/after-transplant': {'plan':'yes','concern':'none'},
 'pcca/localize': {'origin':'hilar','review':'yes'},
 'pcca/diagnosis': {'diagnosis':'yes','biopsy':'no'},
 'pcca/phenotype': {'size':'small','unresectable':'yes','spread':'clear','diagnosis':'yes'},
 'pcca/neoadjuvant': {'protocol':'yes','status':'safe'},
 'pcca/staging': {'stage':'negative','ready':'yes'},
 'pcca/listing': {'evidence':'yes','ready':'ready'},
 'pcca/follow-up': {'plan':'yes','concern':'none'},
 'icca/diagnosis': {'histology':'icca','extent':'yes'},
 'icca/phenotype': {'focality':'solitary','profile':'fits','spread':'yes','program':'yes'},
 'icca/therapy': {'control':'controlled','safe':'yes'},
 'icca/stability': {'duration':'met','disease':'stable'},
 'icca/review': {'criteria':'met','reviews':'yes'},
 'icca/follow-up': {'plan':'yes','concern':'none'},
 'crlm/map-disease': {'primary':'yes','spread':'clear'},
 'crlm/biology': {'molecular':'fits','cea':'low','size':'yes'},
 'crlm/unresectability': {'clearance':'no'},
 'crlm/control': {'response':'controlled','duration':'yes','unresectable':'yes'},
 'crlm/clocks': {'primary':'yes','interval':'yes','synchronous':'na'},
 'crlm/restaging': {'stage':'clear','timing':'yes','control':'yes'},
 'crlm/review': {'criteria':'met','reviews':'yes'},
 'crlm/transplant': {'plan':'yes','concern':'none'},
 'nelm/biology': {'grade':'fits','primary':'yes'},
 'nelm/distribution': {'primary':'yes','spread':'none'},
 'nelm/options': {'strategy':'transplant'},
 'nelm/exposure': {'safety':'acceptable'},
 'nelm/observation': {'clearance':'met','imaging':'yes','control':'yes'},
 'nelm/review': {'criteria':'met','reviews':'yes'},
 'nelm/follow-up': {'plan':'yes','concern':'none'},
 'hehe/diagnosis': {'pathology':'hehe'},
 'hehe/stage': {'vascular':'yes','strategy':'transplant','extrahepatic':'none'},
 'hehe/risk': {'criteria':'yes','benefit':'supported'},
 'hehe/review': {'criteria':'met','reviews':'yes'},
 'hehe/follow-up': {'plan':'yes','concern':'none'},
 'hca/characterize': {'diagnosis':'hca'},
 'hca/standard-care': {'bleeding':'no','management':'no'},
 'hca/exception-route': {'route':'syndrome'},
 'hca/transformation': {'diagnosis':'benign'},
 'hca/review': {'criteria':'met','reviews':'yes'},
 'hca/follow-up': {'plan':'yes','concern':'none'},
}
assert EXAMPLES.keys() == ASSISTANTS.keys()
for key, answers in EXAMPLES.items():
    ASSISTANTS[key]['example'] = answers

# Groups are navigation only. They preserve the existing decision sequence.
_GROUPS = {
 'hcc': [['diagnosis'],['curative-route','allocation'],['treatment','listing','waitlist'],['after-transplant']],
 'pcca': [['localize','diagnosis'],['phenotype'],['neoadjuvant','staging','listing'],['follow-up']],
 'icca': [['diagnosis'],['phenotype'],['therapy','stability','review'],['follow-up']],
 'crlm': [['map-disease','biology'],['unresectability'],['control','clocks','restaging','review'],['transplant']],
 'nelm': [['biology','distribution'],['options'],['exposure','observation','review'],['follow-up']],
 'hehe': [['diagnosis'],['stage','risk'],['review'],['follow-up']],
 'hca': [['characterize'],['standard-care','exception-route','transformation'],['review'],['follow-up']],
}
_TITLES = ['Diagnosis and extent','Transplant suitability','Preparation and reassessment','Transplant and follow-up']
JOURNEYS = {slug:[dict(title=title,steps=steps) for title,steps in zip(_TITLES,groups)] for slug,groups in _GROUPS.items()}
