"""Explicit next actions and continuing care for every transplant decision outcome.

These options are for clinician review. They do not infer treatment suitability
from a failed exception criterion, and do not change the existing selection rules.
"""

def action(label, detail='', *, step=None, care=None, url=None):
    assert sum(x is not None for x in (step, care, url)) == 1
    return dict(label=label, detail=detail, step=step, care=care, url=url)

def plan(id, title, when, tasks, refs, actions=(), endpoint=False):
    return dict(id=id, title=title, when=when, tasks=tasks, refs=refs,
                actions=list(actions), endpoint=endpoint)

MATRIX='https://drliuhao.github.io/mh-liver-pathways/lrt/'
ROADMAP='https://drliuhao.github.io/mh-liver-pathways/'
HIGH_RISK=ROADMAP+'transplant/high-risk/'
SYSTEMIC=ROADMAP+'systemic/'
CARE={}

CARE['hcc']=[
 plan('treatment','Reassess the HCC treatment plan',
      'An AFP requirement is unmet, tumor response is inadequate, or transplantation is currently unsuitable.',[
      'Review AFP trend together with multiphase imaging, viable tumor, extrahepatic staging, liver function, performance status and prior toxicity.',
      'Select a treatment below based on the findings and patient goals. An unmet AFP threshold alone does not show that every option is feasible.',
      'After treatment, reassess response and liver function. Reconsider resection and transplant only when the full clinical and allocation criteria support them.'
      ],['NCCN-hcc','H-policy'],[
       action('Continue or change liver-directed treatment',care='local'),
       action('Review systemic therapy or a clinical trial',care='systemic'),
       action('Reassess resection',care='resection'),
       action('Review an individual MELD-exception request',care='exception'),
       action('Best supportive care',care='supportive')]),
 plan('local','Continue or change liver-directed treatment',
      'There is treatable liver disease, and liver reserve and anatomy permit another local treatment.',[
      'Continue the current downstaging approach if it is producing useful tumor control and remains safe. If response is inadequate, review a different modality with interventional radiology and radiation oncology.',
      'Options include ablation, arterial treatment such as TACE or Y90, and radiation such as SBRT. Select by viable tumor location, prior treatment, normal-liver exposure and liver function.',
      'If no suitable viable target remains, clarify the AFP rise and staging before repeating liver-directed treatment. If local treatment is unsuitable or ineffective, review systemic therapy, a trial or best supportive care.',
      'Recheck imaging and AFP after treatment, then reassess transplant and MELD-exception criteria.'
      ],['NCCN-hcc','H-aasld','H-policy'],[
       action('Plan treatment and response assessment',step='treatment'),
       action('Compare liver-directed modalities',url=MATRIX),
       action('If local treatment is unsuitable: systemic options',care='systemic'),
       action('Best supportive care',care='supportive')]),
 plan('systemic','Systemic therapy or a clinical trial',
      'Liver-directed treatment is unsuitable or has not controlled the disease, or the disease extent favors systemic treatment.',[
      'Medical oncology should choose the regimen using liver function, performance status, prior drugs, toxicity, bleeding risk and patient goals. Select subsequent-line therapy or a trial after progression when appropriate.',
      'Most systemic-therapy evidence is in Child-Pugh A disease. Treatment in Child-Pugh B requires individual assessment; Child-Pugh C or progressive liver failure generally limits treatment to selected circumstances or trials.',
      'If transplantation remains a possibility, discuss immune checkpoint inhibitors with transplant surgery, hepatology and pharmacy before treatment because later transplantation carries rejection risk.',
      'For recurrence after liver transplantation, select systemic therapy jointly with the transplant team because checkpoint inhibitors can cause graft rejection.',
      'After response, reconsider local treatment or surgery when feasible. If further tumor-directed treatment is unsuitable or declined, arrange best supportive care.'
      ],['NCCN-hcc','H-aasld','N-hcc'],[
       action('Open HCC systemic treatment options',url=ROADMAP+'hcc/?topic=sys#topics'),
       action('Reassess response after treatment',step='treatment'),
       action('Best supportive care',care='supportive')]),
 plan('resection','Reassess liver resection',
      'An HPB surgeon believes complete tumor removal may be feasible, including after a treatment response.',[
      'Reassess future liver remnant, liver function, portal hypertension and vascular/biliary anatomy. AFP failure alone is not an indication for surgery.',
      'Offer resection only when the expected oncologic benefit and operative risk are acceptable. If resection is unsuitable, return to local or systemic treatment selection.',
      'After resection, arrange HCC surveillance and reconsider treatment if recurrence develops.'
      ],['NCCN-hcc','H-aasld'],[
       action('Compare resection and transplantation',step='curative-route'),
       action('After treatment: arrange surveillance',care='follow-up'),
       action('Other HCC treatment options',care='treatment')]),
 plan('exception','Individual transplant and MELD-exception review',
      'Standardized exception criteria are not met, but the transplant team considers an individually justified request.',[
      'Document pretreatment tumor burden, treatment response, AFP history, staging, liver function and expected transplant benefit. Review calculated MELD and donor options separately from an exception request.',
      'For prior AFP >1,000, the standardized requirement remains a treatment response to <500 and continued AFP <500. NLRB guidance permits individual consideration in selected cases; approval is not assured.',
      'If the request is deferred or declined, continue an appropriate cancer-treatment or supportive-care plan. Do not leave the patient waiting without a care plan.'
      ],['H-policy','N-hcc'],[
       action('Review the listing and exception evidence',step='listing'),
       action('Continue cancer treatment planning',care='treatment'),
       action('Best supportive care',care='supportive')]),
]

CARE['pcca']=[
 plan('treatment','Treatment when the pCCA transplant protocol is unsuitable',
      'Transplant selection criteria are not met, the patient is unfit for transplant, or transplantation is declined.',[
      'If disease remains localized, review whether complete resection is feasible with the HPB team. Reconfirm the diagnosis and stage before choosing nontransplant treatment.',
      'Address biliary obstruction and cholangitis. For unresectable disease, review systemic therapy, a clinical trial, or selected radiotherapy/chemoradiation with oncology.',
      'Use palliative procedures or radiation when they are expected to relieve symptoms. If further cancer treatment is unsuitable or declined, arrange best supportive care.',
      'Reassess after treatment. A response does not by itself remove a biopsy-related, metastatic or other transplant-protocol exclusion.'
      ],['NCCN-pcca','P-policy','C-aasld'],[
       action('Reassess size, resectability and spread',step='phenotype'),
       action('Open pCCA treatment roadmap',url=ROADMAP+'hilar/'),
       action('Best supportive care',care='supportive')]),
]
CARE['icca']=[
 plan('treatment','Treatment when iCCA transplant criteria are not met',
      'The tumor is resectable, multifocal, outside the described transplant criteria, or transplant is unsuitable.',[
      'Assess complete resection with the HPB team when technically and clinically feasible.',
      'For unresectable or metastatic disease, review molecularly informed systemic therapy or a clinical trial. Selected liver-directed treatment or radiotherapy may be appropriate after multidisciplinary review.',
      'Assess response and reconsider resection or local treatment when feasible. Transplant reconsideration requires the program to review all selection criteria; an additional confirmed iCCA nodule does not meet the solitary-tumor criterion.',
      'If further tumor-directed treatment is unsuitable or declined, arrange best supportive care.'
      ],['NCCN-icca','N-icca','C-aasld'],[
       action('Reassess tumor distribution and resectability',step='phenotype'),
       action('Open iCCA treatment roadmap',url=ROADMAP+'icca/'),
       action('Compare liver-directed modalities',url=MATRIX),
       action('Best supportive care',care='supportive')]),
]
CARE['crlm']=[
 plan('treatment','Continue colorectal cancer care when transplant is unsuitable',
      'MELD-exception criteria are not met, disease progresses, or another treatment is preferable.',[
      'Review whether response permits complete treatment of liver disease by resection or ablation; assess the primary and any extrahepatic disease separately.',
      'Medical oncology should review the molecular profile, prior regimens, response, toxicity and performance status to choose systemic treatment or a clinical trial.',
      'After treatment, reassess resectability and disease control. Reconsider transplantation only if the program accepts the full clinical and MELD-exception evidence.',
      'When further tumor-directed therapy is unsuitable or declined, arrange best supportive care, including management of pain, obstruction and other symptoms.'
      ],['NCCN-crlm','C-consensus','N-crlm'],[
       action('Reassess resection or ablation',step='unresectability'),
       action('Open CRLM treatment roadmap',url=ROADMAP+'crlm/'),
       action('Reassess disease control after treatment',step='control'),
       action('Best supportive care',care='supportive')]),
]
CARE['nelm']=[
 plan('treatment','Continue NET treatment when transplant is unsuitable',
      'Transplant criteria are not met or another treatment currently offers greater benefit.',[
      'Confirm primary site, differentiation, grade and current distribution. G3 disease or poorly differentiated neuroendocrine carcinoma requires its own oncology treatment plan.',
      'For well-differentiated G1/G2 disease, review resection/ablation, systemic therapy, somatostatin-receptor-directed treatment, liver-directed treatment or a trial according to tumor type, receptor status, disease behavior and organ function.',
      'Continue treatment of hormone-related symptoms when needed, even when the cancer-control strategy changes. Reassess disease extent and response before any transplant reconsideration.',
      'Arrange best supportive care when further tumor-directed treatment is unsuitable or declined.'
      ],['NCCN-net','N-net','NET-milan'],[
       action('Compare NET treatment options',step='options'),
       action('Open NELM treatment roadmap',url=ROADMAP+'nelm/'),
       action('Best supportive care',care='supportive')]),
]
CARE['hehe']=[
 plan('treatment','Agree a rare-tumor treatment or observation plan',
      'Transplant benefit is uncertain or transplantation is unsuitable.',[
      'Confirm HEHE with expert pathology. A revised diagnosis of angiosarcoma requires a separate sarcoma treatment plan.',
      'The sarcoma and liver teams should compare resection, observation, local treatment and systemic treatment according to symptoms, distribution and disease behavior.',
      'During observation or treatment, define which new symptoms or imaging changes require reassessment. Limited extrahepatic HEHE alone does not automatically exclude MELD-exception consideration.',
      'Arrange best supportive care when further tumor-directed treatment is unsuitable or declined.'
      ],['E-consensus','N-hehe','NCI-support'],[
       action('Reassess disease extent and alternatives',step='stage'),
       action('Open EHE treatment consensus',url='https://doi.org/10.1016/j.esmoop.2021.100170'),
       action('Best supportive care',care='supportive')]),
]
CARE['hca']=[
 plan('treatment','Continue standard adenoma management',
      'An HCA MELD-exception criterion is not met or transplantation is not justified.',[
      'Review hormone exposure, metabolic risk factors, subtype, size and growth with the benign liver tumor team.',
      'Choose observation, resection or a suitable local treatment according to risk and feasibility. Set a surveillance and reassessment plan.',
      'Treat active bleeding urgently. Investigate suspected malignant transformation through the appropriate cancer pathway.',
      'For ongoing symptoms or liver disease, arrange hepatology and symptom-management follow-up even when transplantation is not indicated.'
      ],['A-easl','N-hca'],[
       action('Review standard adenoma treatment',step='standard-care'),
       action('Investigate possible malignant transformation',step='transformation'),
       action('Arrange continuing care and surveillance',care='follow-up'),
       action('Open adenoma roadmap',url=ROADMAP+'adenoma/')]),
 plan('urgent','Treat unstable hemorrhage',
      'There is hemodynamic instability from adenoma bleeding.',[
      'Arrange immediate resuscitation and urgent interventional-radiology and surgical assessment, including embolization where appropriate.',
      'After stabilization, reassess residual viable adenoma, resection feasibility and the longer-term treatment plan.'
      ],['A-easl'],[action('After stabilization: reassess standard treatment',step='standard-care')],True),
]

SUPPORT_REFS={'hcc':['NCCN-hcc'],'pcca':['NCCN-pcca'],'icca':['NCCN-icca'],
              'crlm':['NCCN-crlm'],'nelm':['NCCN-net'],'hehe':['E-consensus']}
for slug in SUPPORT_REFS:
    specific={
      'hcc':'Continue hepatology care for ascites, encephalopathy and other liver-disease complications; review symptom-directed radiation or procedures when expected benefit exceeds burden.',
      'pcca':'Review biliary drainage, infection treatment and relief of jaundice or pruritus according to expected benefit and patient goals.',
      'icca':'Review pain, biliary obstruction and liver-disease complications; consider symptom-directed procedures when beneficial.',
      'crlm':'Review pain, bowel symptoms or obstruction and treatment adverse effects with oncology and the relevant procedural team.',
      'nelm':'Continue appropriate management of hormone-related symptoms, diarrhea and nutrition; cancer progression does not end symptom treatment.',
      'hehe':'Review pain, effusions and other disease-related symptoms with the sarcoma team.'
    }[slug]
    CARE[slug].append(plan('supportive','Best supportive care',
      'Further tumor-directed treatment is unsuitable, offers insufficient expected benefit, or is declined after discussion.',[
      'Arrange palliative care for symptom relief, psychosocial support and goals-of-care discussions.',
      specific,
      'Agree follow-up and an urgent-contact plan; discuss hospice when appropriate. Palliative care can accompany cancer treatment.'
      ],SUPPORT_REFS[slug]+['NCI-support'],[
       action('Reconsider cancer treatment if circumstances change',care='treatment')],True))

FOLLOWUP_REFS={'hcc':['H-policy','H-aasld'],'pcca':['P-cohort','P-policy'],'icca':['I-cohort'],
 'crlm':['C-consensus','C-transmet'],'nelm':['NET-milan'],'hehe':['E-consensus','E-score'],'hca':['A-easl','N-hca']}
for slug, refs in FOLLOWUP_REFS.items():
    CARE[slug].append(plan('follow-up','Continue planned follow-up',
      'The treatment or transplant decision is complete and ongoing care has been agreed.',[
      'Confirm the responsible clinical team, surveillance schedule and plan for new symptoms or suspicious imaging.',
      'After transplantation, review explant findings and continue transplant care. Adapt cancer surveillance to the diagnosis and recurrence risk; no single schedule fits every pathway.',
      'If recurrence or a new safety problem is suspected, arrange prompt specialist review. After transplantation, treatment selection must account for graft function, immunosuppression and rejection risk.'
      ],refs,[action('Review treatment options for new disease',care='treatment')],True))

def build_continuations(pathways, assistants):
    """Every displayed result has a real destination or an ongoing-care endpoint."""
    result={}
    for p in pathways:
        slug=p['slug']
        for s in p['steps']:
            key=f'{slug}/{s["id"]}'
            clarify=action('Reassess after resolving the finding',
                'Complete the assessment described above, then update the choices for this decision.',step=s['id'])
            alternatives=action('Review treatment and continuing care',
                'If transplantation is unsuitable, choose a disease-specific treatment or ongoing-care plan.',care='treatment')
            branches={}
            for n,b in enumerate(s['branches']):
                if b['to']:
                    branches[str(n)]=[action('Continue: '+next(x['title'] for x in p['steps'] if x['id']==b['to']),step=b['to'])]
                elif b['kind']=='advance':
                    branches[str(n)]=[action('Open the continuing-care plan',care='follow-up')]
                elif b['kind']=='redirect':branches[str(n)]=[alternatives]
                else:branches[str(n)]=[clarify,alternatives]
            rules={}
            for n,r in enumerate(assistants[key]['rules']):
                if r['branch'] is not None:continue
                rules[str(n)]=[clarify,alternatives] if r['kind']=='hold' else [alternatives]
            result[key]=dict(branches=branches,rules=rules,clarify=[clarify])

    def custom(key, condition, actions):
        rule_ids=[n for n,r in enumerate(assistants[key]['rules']) if r['when']==condition]
        assert len(rule_ids)==1,(key,condition)
        result[key]['rules'][str(rule_ids[0])]=actions

    custom('hcc/allocation',{'afp':'not-met'},[
        action('Continue downstaging', 'If the current treatment is helping and further treatment remains safe.',care='local'),
        action('Change liver-directed modality', 'If response is inadequate and anatomy and liver function permit another modality.',care='local'),
        action('Systemic therapy or clinical trial', 'If local treatment is unsuitable or ineffective; review liver function and transplant intent.',care='systemic'),
        action('Reassess resection', 'If complete removal may now be safe; AFP failure alone does not justify surgery.',care='resection'),
        action('Individual MELD-exception review', 'If the transplant team supports an individually justified request.',care='exception'),
        action('Best supportive care', 'If further tumor-directed treatment is unsuitable or declined.',care='supportive'),
    ])
    result['hcc/allocation']['branches']['2']=[
        action('Agree surveillance or immediate treatment',
            'Use the T1 clinical recommendation above; review treatment feasibility and patient goals.',care='t1'),
        action('Review transplant suitability separately',step='curative-route')]
    result['hcc/allocation']['branches']['3']=[action('Review an individual exception request',care='exception'),action('Review HCC treatment options',care='treatment')]
    for key,condition in [('hca/characterize',{'diagnosis':'bleeding'}),('hca/standard-care',{'bleeding':'yes'})]:
        custom(key,condition,[action('Urgent bleeding management',care='urgent')])
    custom('pcca/diagnosis',{'biopsy':'yes'},[
        action('After program review: reassess diagnostic eligibility',
            'Obtain an explicit decision about the biopsy history and seeding risk before concluding that the protocol is available or excluded.',step='diagnosis'),
        action('If transplant is unsuitable: review other care',care='treatment')])
    # Diagnostic uncertainty does not trigger empiric anticancer treatment.
    for key, condition, step in [
        ('hcc/diagnosis',{'diagnosis':'other'},'diagnosis'),
        ('icca/diagnosis',{'histology':'other'},'diagnosis'),
        ('hehe/diagnosis',{'pathology':'angiosarcoma'},'diagnosis'),
    ]:
        custom(key,condition,[action('Confirm diagnosis and arrange the appropriate specialist care',
            'Use pathology and imaging to select the treatment pathway for the confirmed tumor type.',step=step),
            action('Open cancer roadmaps',url=ROADMAP)])
    # Review destinations preserve the standard selection rules and their stop states.
    def review(key, bucket, index, slug, anchor, label, detail):
        result[key][bucket][str(index)].append(action(label, detail, url=HIGH_RISK+slug+'/#'+anchor))
    review('hcc/allocation','branches',3,'hcc','hcc-b1','Review the proposed beyond-UNOS study',
        'A bounded study proposal; reaching Milan does not automatically create standardized MELD-exception eligibility.')
    review('hcc/curative-route','rules',1,'hcc','hcc-b2','Review previously treated portal-vein invasion',
        'Only selected portal-branch invasion is proposed for study. This does not open a transplant route for prior rupture or other excluded findings.')
    review('pcca/phenotype','branches',1,'pcca','pcca-b1','Review the size, biopsy and nodal boundaries',
        'These expanded transplant groups remain closed in the V7 proposal; review clarifies the limit rather than granting eligibility.')
    review('pcca/phenotype','branches',1,'pcca','pcca-b2','Review resection as the curative option',
        'Resection remains preferred when complete removal and an adequate functional remnant are feasible.')
    review('pcca/diagnosis','rules',0,'pcca','pcca-b1','Review the primary-biopsy exclusion',
        'Confirm the biopsy route. Expansion after a transperitoneal primary-tumor biopsy remains closed in this proposal.')
    review('pcca/neoadjuvant','branches',1,'pcca','pcca-b3','Review alternative neoadjuvant proposals',
        'Alternative regimens require separate approval; they are not automatically equivalent to the established transplant regimen.')
    review('icca/phenotype','branches',1,'icca','icca-b1','Review the proposed advanced-iCCA study',
        'Distinguish adjacent satellites from separate multifocal tumors. The initial proposal excludes separate multifocal disease, nodes and extrahepatic spread.')
    review('icca/therapy','rules',0,'icca','icca-b2','Review whether a future study reassessment is possible',
        'The proposal allows only a defined liver-only salvage scenario after renewed control. Nodal or extrahepatic progression does not qualify.')
    review('icca/stability','branches',1,'icca','icca-b2','Review the proposed observation requirements',
        'Continue appropriate treatment and reassessment; the required period of control is not waived.')
    review('icca/review','branches',1,'icca','icca-b3','Review living-donor study readiness',
        'Study development only. Donor availability does not establish recipient eligibility or permission to transplant.')
    review('crlm/unresectability','branches',2,'crlm','crlm-b1','Obtain the high-risk resectability review',
        'Two experienced HPB reviews should address resection, ablation and appropriate conversion options before a transplant study is considered.')
    review('crlm/biology','branches',1,'crlm','crlm-b3','Review the molecular selection limits',
        'The initial proposal does not open BRAF-mutant or MSI-H/dMMR expansion. KRAS mutation alone is treated differently.')
    review('crlm/biology','rules',3,'crlm','crlm-b3','Review the proposed CEA boundary',
        'The local proposed threshold and NLRB guidance are distinct; neither should be silently substituted for the other.')
    review('nelm/options','branches',1,'nelm','net-b1','Compare expected transplant benefit with other treatment',
        'Review symptoms, threat to liver function and available systemic or liver-directed options. Stable low-burden disease usually favors nontransplant care.')
    review('nelm/distribution','branches',1,'nelm','net-b2','Review previously cleared extrahepatic disease',
        'Prior nodes and prior solid-organ metastases have different boundaries; confirm the required disease-free interval.')
    review('nelm/review','branches',1,'nelm','net-b3','Review age and liver-burden boundaries',
        'Age is an individual review factor; any proposed burden expansion requires separate approval.')
    review('hehe/stage','branches',2,'hehe','hehe-b2','Review the HEHE clinical boundary',
        'NLRB guidance and the narrower proposed opening cohort are different. Stable extrahepatic disease is not automatically accepted by the local proposal.')
    review('hehe/risk','branches',1,'hehe','hehe-b1','Review observation and expected transplant benefit',
        'A proposed observation period should not mechanically delay review of urgent liver failure.')
    review('hca/exception-route','branches',1,'hca','hca-b1','Review the four HCA exception routes',
        'Clarify whether a guidance route is met; exception criteria and a clinical need for transplantation remain separate.')
    review('hca/standard-care','branches',1,'hca','hca-b2','Review whether transplantation is clinically justified',
        'First assess feasible nontransplant treatment. Tumor size alone is not an indication for transplantation.')
    return result

CARE['hcc'].append(plan('t1','T1 HCC: agree surveillance or treatment',
    'A single HCC is 1 to <2 cm and there is no macrovascular invasion or extrahepatic spread.',[
    'For a transplant-eligible patient with decompensated cirrhosis, discuss CT or MRI at least every 3 months until exception criteria are met, as advised by AASLD.',
    'Consider immediate liver-directed treatment when AFP is significantly elevated or transplantation is not appropriate. Choose treatment through the tumor board using liver function, anatomy and patient goals.',
    'At each reassessment, review tumor size, AFP and transplant suitability. T1 alone does not qualify for HCC MELD-exception points and does not by itself rule out transplantation.'
    ],['H-aasld','N-hcc'],[
      action('After surveillance: reassess tumor and AFP criteria',step='allocation'),
      action('If treating now: review local treatment',care='local'),
      action('Reassess transplant versus resection',step='curative-route')]))

# Shared matrices supplement the existing disease-specific treatment plans.
for slug in ('hcc','pcca','icca','crlm','nelm'):
    treatment=next(p for p in CARE[slug] if p['id']==('systemic' if slug=='hcc' else 'treatment'))
    treatment['actions'].append(action('Open the systemic therapy matrix',
        'Compare treatment setting, biomarkers, pivotal trials and major precautions.',url=SYSTEMIC+'?tumor='+slug))
next(p for p in CARE['hcc'] if p['id']=='exception')['actions'].append(action(
    'Review high-risk HCC study proposals',
    'Selected scenarios require separate review and study approval; unmet AFP criteria alone do not create an alternative transplant entitlement.',url=HIGH_RISK+'hcc/'))
next(p for p in CARE['hcc'] if p['id']=='systemic')['actions'].append(action(
    'Review immunotherapy and transplant timing',
    'Previous checkpoint therapy requires assessment of immune toxicity and rejection risk; no washout interval guarantees safety.',url=HIGH_RISK+'hcc/#hcc-b3'))
next(p for p in CARE['crlm'] if p['id']=='treatment')['actions'].append(action(
    'If no tumor remains visible: review the treatment goal',
    'The V7 proposal does not offer transplantation solely for presumed microscopic cancer. Assess resection feasibility or treatment-related liver failure separately.',url=HIGH_RISK+'crlm/#crlm-b2'))
