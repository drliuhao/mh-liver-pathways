"""Blank clinical recording instruments. These fields do not add eligibility rules.

Stable field IDs and repeated modules support a future governed registry. No entered
patient data is accepted, saved or transmitted by the public website.
"""
from pathlib import Path
from html import escape as e
import csv
import io
import json
import zipfile

VERSION = '2026-10-24.1'
MISSING = ['recorded', 'pending', 'not_done', 'not_applicable', 'unknown', 'not_documented']
MODULES = {}


def module(key, title, spec, repeat=False, note=''):
    fields = []
    for line in spec.strip().splitlines():
        parts = line.strip().split('|')
        parts += [''] * (6-len(parts))
        name, label, dtype, unit, choices, helptext = parts
        fields.append(dict(id=key+'.'+name, label=label, type=dtype or 'text',
                           unit=unit, choices=choices.split(';') if choices else [], help=helptext))
    MODULES[key] = dict(id=key, title=title, repeat=repeat, note=note, fields=fields)


module('record', 'Assessment identification', '''
record_id|Coded patient / registry ID|text|||Use a coded ID in research exports. Keep any identifying linkage in the approved clinical system.
assessment_id|Unique assessment ID|text|||New ID for each encounter or reassessment; retain earlier records.
assessment_date|Date of clinical assessment|date|||YYYY-MM-DD; document date precision if only month or year is known.
phase|Phase of care|choice||referral;evaluation;pretransplant_treatment;listed;temporarily_inactive;posttransplant;other|
site|Treating center / service|text
clinician|Responsible clinician and role|text
recorder|Person recording / abstracting the information|text
entry_date|Date entered|date
protocol|Local protocol name, version and approval status|text
source_version|Policy / guidance version used and date checked|text|||Record the version actually used for this assessment.
''')

module('context', 'Patient and liver-disease context', '''
age|Age at assessment|number|years
sex|Sex recorded for relevant clinical assessment|text|||Record source and clinical context; do not infer from name or gender identity.
diagnosis_date|Date diagnosis was established|date
diagnosis_basis|Basis for diagnosis|choice||imaging;histology;cytology;protocol_diagnostic_criteria;other|
liver_disease|Underlying liver disease and etiology|text
cirrhosis|Cirrhosis assessment and supporting evidence|text|||Record present / absent / uncertain and imaging, pathology or clinical basis.
prior_malignancy|Other malignancy, activity and treatment history|text
symptoms|Current symptoms, severity and functional effect|text
goals|Patient goals and treatment preferences|text
''')

module('labs', 'Laboratory results — one row per analyte and date', '''
analyte|Analyte / test name|text|||Examples as relevant: bilirubin, albumin, INR, creatinine, sodium, platelets, hemoglobin, WBC, ANC, AST, ALT, ALP, AFP, CEA, CA 19-9, IgG4.
value|Reported numeric value|number|||Keep the original value; do not convert missing results to zero.
qualifier|Result qualifier|choice||exact;less_than;greater_than;below_detection;qualitative|
unit|Reported unit|text|||For example mg/dL, g/dL, mmol/L, 10^9/L, ng/mL or U/mL; INR is unitless.
qualitative|Qualitative result, if applicable|text
collected|Specimen collection date|date
reference_range|Laboratory reference range|text
context|Relevant context at collection|text|||Cholangitis, obstruction/drainage, anticoagulation, dialysis, recent treatment or other confounder.
''', True)

module('reserve', 'Liver reserve, nutrition and function', '''
meld|Calculated MELD value, version and calculation date|text|||Keep laboratory MELD separate from exception / allocation score. Preserve source calculation rather than recalculate here.
child_pugh|Child-Pugh score / class and component assessment|text
ascites|Ascites severity, treatment and control|text
encephalopathy|Encephalopathy severity, treatment and control|text
portal_hypertension|Portal-hypertension evidence|text|||Varices/bleeding, splenomegaly, platelets, collaterals and pressure measurement if available.
renal|Renal function and dialysis status / dates|text
ecog|ECOG performance status|choice||0;1;2;3;4;not_assessable|
frailty|Frailty / physical-function tool, value and date|text|||Name the instrument; retain raw components where available.
nutrition|Nutrition assessment, weight trend and sarcopenia assessment|text
''')

module('imaging', 'Imaging studies — one row per examination', '''
study_id|Stable imaging-study ID|text
date|Acquisition date|date
modality|Modality and protocol|text|||CT / MRI / CEUS / PET; contrast phases or tracer as relevant.
coverage|Anatomic coverage|text|||Liver, chest, abdomen, pelvis or other sites; record what was actually examined.
adequacy|Technical adequacy and limitations|text
comparison|Comparison study IDs and dates|text
review|Expert radiology review, reviewer and date|text
findings|Overall impression and uncertain findings|text
''', True)

module('lesions', 'Liver lesion map — one row per lesion at each imaging time point', '''
lesion_id|Stable lesion ID|text|||Keep the same ID across scans, treatments and explant correlation; include disappeared sites.
study_id|Linked imaging-study ID|text
segment|Liver segment / lobe and location|text
diameter|Maximum total lesion diameter|number|mm
viable_diameter|Maximum viable enhancing component, if applicable|number|mm||Do not substitute treated-cavity size for viable-tumor size.
pretreatment|Pretreatment diameter and date / source|text
diagnosis|Lesion diagnosis / suspicion and certainty|text|||iCCA, HCC, metastasis, benign, indeterminate, treated site or other; do not count uncertain nodules as confirmed tumor.
classification|Imaging classification and version|text|||LI-RADS / LR-TR if applicable. Record Class 5 adjudication separately when relevant to HCC allocation.
relationship|Relation to dominant tumor / nearby separate nodules|text|||Record distance, segment and distribution if available; a satellite label alone does not prove clonal origin.
treatment_id|Linked treatment episode IDs|text
pathology_id|Linked tissue / explant specimen IDs|text
''', True)

module('stage', 'Disease extent and staging assessment', '''
focality|Number and distribution of confirmed tumors|text|||Separate confirmed tumors, indeterminate nodules and treated sites.
vascular|Vascular involvement: vessel, level, extent and certainty|text|||Distinguish tumor invasion from bland thrombosis and microscopic from macroscopic invasion.
regional_nodes|Regional nodal findings and confirmation method|text
extrahepatic|Extrahepatic sites: suspected / confirmed / excluded / indeterminate|text
peritoneum|Peritoneal assessment and evidence|text
stage|Clinical TNM, staging edition and date|text|||T, N, M and overall stage separately; record uncertainty rather than deriving stage from lesion count alone.
unresolved|Unresolved staging findings and plan|text
''')

module('pathology', 'Tissue / pathology — one row per specimen', '''
specimen_id|Specimen ID / source-report reference|text
date|Collection date|date
site|Exact sampled site / lesion or nodal station|text
method|Acquisition method|text|||Core biopsy, brushing, intraductal biopsy, FNA, resection, explant or other.
route|Sampling route and needle trajectory, where relevant|text|||For pCCA distinguish primary tumor from regional node and transperitoneal from intraductal sampling.
adequacy|Specimen adequacy and limitations|text
histology|Diagnosis and differential|text
grade|Differentiation / grade and grading system|text
ihc|Immunohistochemistry, molecular findings and interpretation|text
review|Expert pathology reviewer, date and concordance|text
''', True)

module('molecular', 'Molecular testing — one row per assay / result', '''
specimen_id|Linked specimen / plasma sample ID|text
date|Sample / report date|date
assay|Laboratory, assay, method and panel version|text
marker|Gene / biomarker tested|text|||Record relevant tests actually obtained; this template does not order an expanded panel.
result|Exact alteration / result and assay limitations|text
status|Interpretation|choice||positive;negative;equivocal;failed;pending;not_tested|
impact|Treatment / selection implication documented by the team|text
''', True)

module('surgery', 'Resection and alternative-treatment assessment', '''
review_date|HPB review date and reviewing surgeons|text
resectability|Complete safe resection / ablation assessment|choice||feasible;potentially_feasible_after_treatment;not_feasible;uncertain|
operation|Proposed operation / combined treatment and sites addressed|text
remnant|Future liver remnant volume, percentage, method and functional assessment|text
vascular_biliary|Inflow, outflow, biliary drainage and reconstruction requirements|text
constraints|Specific technical or liver-function barriers|text|||State the anatomical / functional reason; lesion count alone is insufficient.
alternatives|Alternatives assessed and reasons accepted or rejected|text|||Include staged/parenchymal-sparing surgery, ablation, remnant augmentation or observation when relevant.
reassessment|Conditions for reassessment, date and responsible clinician|text
''')

module('therapy', 'Treatment episodes — repeat for each regimen, cycle group or procedure', '''
treatment_id|Stable treatment episode ID|text
intent|Treatment intent|choice||bridge;downstaging;conversion;disease_control;curative_intent;adjuvant;symptom_control;other|
modality|Modality / procedure and target lesion IDs|text
regimen|Drug(s), regimen and line of therapy|text
start|Start date|date
last_dose|Last administered dose / procedure date|date
end|End / stop date|date
dose|Planned and delivered doses, units and cycles|text
modifications|Dose delays, reductions, omissions and reasons|text
response_plan|Planned response examination and date|text
stop_reason|Reason stopped or changed|text
''', True)

module('radiation', 'Radiation / radiopharmaceutical exposure, when applicable', '''
treatment_id|Linked treatment episode ID|text
technique|Technique / isotope / agent and target|text
planning|Planning / mapping date and method|text
dose|Prescribed and delivered dose with units|text|||Gy, GBq or other reported unit; do not combine incompatible measures.
fractions|Fractions or administrations planned / delivered|text
volume|Target volume and uninvolved liver / organ-at-risk assessment|text
dosimetry|Tumor and normal-tissue dose estimates, method and limitations|text
cumulative|Prior/cumulative exposure and safety interpretation|text
''', True)

module('toxicity', 'Adverse events and treatment complications', '''
event_id|Event ID and linked treatment / procedure ID|text
event|Event / diagnosis|text
onset|Onset date|date
severity|Grade, grading system and version|text|||For example CTCAE or Clavien-Dindo as appropriate; do not mix scales.
attribution|Attribution and confidence|text
management|Management, hospitalization and treatment changes|text
resolution|Resolution date / ongoing status / sequelae|text
''', True)

module('ici', 'Immune-checkpoint inhibitor exposure and transplant safety', '''
exposure|Exposure status|choice||never_exposed;prior_exposure;current;uncertain|
agent|Agent(s), combination and treatment episode IDs|text
last_dose|Last ICI dose date|date
toxicity|Immune-related toxicity, organ, grade and resolution|text
management|Steroid / other immunosuppression used for toxicity|text
interval|Proposed transplant date and elapsed days from last ICI|text|||Record both dates and interval; no interval is asserted to guarantee safety.
review|Transplant, oncology and pharmacy review / date|text
plan|Risk discussion, immunosuppression / monitoring plan and unresolved issues|text
''')

module('response', 'Response assessments — one row per time point', '''
date|Assessment date|date
study_ids|Linked imaging-study IDs and biomarker dates|text
baseline|Comparator / baseline date and tumor measurements|text
system|Response criteria and version used|text|||RECIST 1.1, mRECIST, LR-TR or other; allocation criteria must be assessed separately.
response|Response designation and supporting measurements|text
new_lesions|New lesions, sites, certainty and action|text
extrahepatic|Extrahepatic status at this time point|text
review|Reviewer and unresolved discordance|text
''', True)

module('interval', 'Observation intervals — one row per applicable interval', '''
purpose|Purpose / source-defined interval|text
start_event|Start event and rationale|text|||Diagnosis, last treatment, primary resection, clearance or another explicitly named event.
start_date|Start date|date
end_event|End event / request / assessment date definition|text
end_date|End date|date
elapsed|Elapsed time and unit / calculation method|text|||Keep dates and units; calendar months and fixed day counts are not interchangeable.
evidence|Intervening scan / treatment / biomarker record IDs|text
interruption|Progression, new treatment or other interruption and team interpretation|text
interpretation|Source wording, interpretation and approving clinician|text
''', True)

module('fitness', 'Clinical transplant evaluation and readiness', '''
medical|Comorbidities and transplant medical assessment|text
cardiopulmonary|Cardiac / pulmonary evaluation, results, dates and outstanding actions|text
infection|Active infection, treatment, microbiology and clearance assessment|text
functional|Frailty, nutrition, mobility and rehabilitation plan|text
psychosocial|Psychosocial / support / adherence assessment status|text|||Reference the approved clinical record; avoid unnecessary sensitive narrative in research exports.
consent|Patient understanding, alternatives and consent discussion / date|text
donor_strategy|Deceased / living donor strategy and evaluation status|text|||Do not place identifiable donor information in this template or research export.
barriers|Outstanding issues, responsible clinician and completion date|text
clearance|Clinical approval / deferral / decline and date|text
''')

module('allocation', 'Exception request and allocation record', '''
route|Request route|choice||standardized;nonstandard_nlrb;native_meld;other;not_determined|
request_type|Request type|choice||initial;extension;appeal;other|
request_date|Submitted / planned submission date|date
version|Policy / guidance version, section and verification date|text
criteria|Criterion-by-criterion assessment and supporting record IDs|text|||Met / not met / uncertain / not applicable for each; explain discrepancies.
score|Requested / assigned score, MMaT reference and calculation date|text|||Keep calculated MELD, exception score and final allocation score distinct.
disposition|Review disposition|choice||not_submitted;pending;approved;denied;withdrawn;appeal;other|
decision_date|Disposition date / official request ID|text
renewal|Expiry / renewal due date and evidence needed|text
reviewer|Allocation coordinator / clinician and verification date|text
''')

module('decision', 'Clinical decision, actions and sign-off', '''
mdt_date|Multidisciplinary review date and participants|text
clinical_decision|Clinical assessment|choice||proceed_with_evaluation;proceed_with_treatment;pause_for_information;use_alternative_treatment;decline_transplant;continue_follow_up;other|
rationale|Clinical rationale, alternatives and benefit-risk discussion|text
allocation_separate|Separate allocation conclusion / unresolved question|text
uncertainty|Discordant findings, uncertainty and how they will be resolved|text
actions|Next actions, responsible clinician and due dates|text
deviation|Departure from protocol / pathway and rationale|text
communication|Patient / referring-team communication and date|text
next_review|Next review date and triggers for earlier review|text
signoff|Reviewing clinician, signature / attestation and date|text
''')

module('milestones', 'Program milestones and follow-up — repeat as events occur', '''
event|Milestone / event|choice||referral;evaluation;diagnosis;first_treatment;protocol_enrollment;clinical_acceptance;listing;inactive;reactivated;exception_request;exception_decision;delisting;transplant;recurrence;graft_failure;retransplant;death;last_contact;other|
date|Event date|date
reason|Reason / cause and adjudication source|text|||Record evaluation declines, waitlist dropout and patients never transplanted as well as transplant recipients.
status|Patient / listing / graft / disease status at event|text
source|Source document and reviewer|text
''', True)

module('transplant', 'Transplant operation and explant', '''
date|Transplant date|date
donor_type|Graft / donor type|text|||Living or deceased; DBD / DCD and preservation method if recorded. No donor identifiers.
operation|Operation, reconstruction and perioperative events|text
explant_id|Explant pathology report ID / review date|text
tumors|Number, sites, sizes and viable tumor / treatment effect|text
histology|Histology, grade and pretransplant–explant concordance|text
invasion|Microvascular, macrovascular, perineural and biliary invasion|text
nodes_margins|Nodes examined / positive, stations and margins|text
stage|Pathologic TNM / staging edition|text
submission|Required pathology / registry submission and completion date|text
''')

module('followup', 'Post-transplant / program outcomes — repeat at each follow-up', '''
date|Follow-up / last-contact date|date
vital_status|Vital status|choice||alive;dead;unknown|
death|Death date, cause and source if applicable|text
graft|Graft function, graft failure / retransplant date and cause|text
immunosuppression|Actual regimen, doses and relevant trough levels / dates|text
rejection|Rejection diagnosis, biopsy / grade, date, treatment and resolution|text
complications|Infection, biliary, vascular, renal and other major complications|text
surveillance|Surveillance completed: study IDs, dates and results|text
recurrence|Recurrence date, site, confirmation method and treatment|text
function|Performance, symptoms, quality-of-life tool / score and rehabilitation needs|text
next|Next surveillance plan, date and responsible team|text
''', True)

module('research', 'Research and data-quality extension', '''
project|Registry / study name and local approval reference|text|||Optional research fields; collection/use requires the applicable institutional process.
permission|Consent / waiver / permitted-use status and date|text
time_zero|Analysis time-zero event and date|text|||Preserve referral, diagnosis, treatment, listing and transplant dates separately; specify which defines each endpoint.
endpoint|Outcome definition / protocol version used|text|||Specify survival, recurrence, progression, graft failure or dropout definition and time origin.
ascertainment|Last date the endpoint was assessed and method|text
censoring|Censoring / lost-to-follow-up status, date and reason|text|||Do not equate missing follow-up with absence of an event.
adjudication|Data queries, discordance, resolution and adjudicator/date|text
revision|Record version, correction reason and superseded record ID|text|||Retain the earlier value and its source in the governed system.
''')

module('hcc', 'HCC diagnosis and allocation detail', '''
at_risk|Imaging-diagnosis population / liver background and evidence|text
class5|Class 5 adjudication for each relevant lesion ID|text|||Keep indeterminate observations separate; cite the criterion/version used.
baseline_count|Qualifying pretreatment lesion count|integer
baseline_sum|Sum of qualifying pretreatment diameters|number|mm
afp_peak|Highest documented AFP and date|text|||State whether the available record is complete; record history above 1,000 ng/mL separately.
afp_history|AFP ever above 1,000 ng/mL and subsequent dated trend|text
category|Clinical selection and allocation categories assessed|text|||Record Milan clinical assessment, T2, standardized downstaging or nonstandard review separately.
prior_invasion|Prior rupture or vascular invasion: dates, vessel/level, treatment and stability|text
''')

module('biliary', 'Perihilar anatomy, drainage and diagnostic context', '''
location|Stricture location / extent and Bismuth-Corlette description|text
mass|Mass present, number, radial diameter and measurement plane|text|||Record actual measurement in mm perpendicular to the duct, date and reviewer.
duct_extent|Longitudinal duct extent / segments involved|text|||Keep distinct from radial mass size.
psc|PSC and other liver disease / benign mimics assessed|text
igG4|IgG4 assessment and interpretation, if indicated|text
drainage|Stent / drain type, side, segment, insertion and exchange dates|text
bilirubin|Bilirubin trend before / after drainage|text
cholangitis|Cholangitis / infection at relevant sampling and CA 19-9 dates|text
ca199|CA 19-9 result, date, obstruction/infection context and interpretation|text
prior_procedures|Prior primary-tumor biopsy / surgery / treatment and route|text
''')

module('biliary_sampling', 'pCCA diagnostic evidence and sampling review', '''
ercp|ERCP date, cholangiography, brushings and intraductal biopsies|text
cytology|Cytology result, adequacy and review date|text
fish|FISH / aneuploidy result, method, specimen and interpretation|text
ngs|NGS result, assay and clinical interpretation if obtained|text|||Record separately from the named policy diagnostic alternatives.
criteria|Accepted diagnostic criterion/criteria and supporting records|text
primary_route|Primary-tumor transperitoneal sampling history|text|||Record performed / not performed / uncertain, target, route and date; do not confuse nodal with primary sampling.
node_plan|Regional-node sampling indication, target and trajectory|text
review|Advanced GI / transplant review of route and implications|text
''')

module('protocol', 'Protocol enrollment and regimen delivery', '''
name|Written protocol name, version and approval authority/date|text
enrollment|Enrollment / acceptance date and clinician|text
regimen|Approved neoadjuvant regimen and sequence|text
delivered|Linked actual treatment episodes / dose records|text
completion|Completion status and last treatment date|text
deviations|Regimen deviations, reasons and approval|text
restaging|Restaging / operative staging plan and dates|text
''')

module('operative_stage', 'Operative staging report', '''
date|Operation date|date
relation|Relationship to neoadjuvant therapy and proposed transplant|text|||Record therapy completion date; explicitly identify staging before/after therapy.
approach|Laparoscopy / laparotomy / other approach and surgeon|text
extent|Areas examined and any limitations|text
liver|Liver surface / parenchymal findings and lesion IDs|text
peritoneum|Peritoneal inspection, suspicious sites and biopsy / cytology findings|text
nodes|Regional hepatic nodal stations examined / sampled|text|||Use one specimen row per station or site below.
complete|Staging completeness and reason for any incomplete assessment|text
result|Final staging interpretation after permanent pathology|text|||Distinguish preliminary / frozen section from final pathology.
reconciliation|Imaging, pathology and operative findings reconciled by / date|text
complications|Operative complications, recovery and fitness implications|text
''')

module('staging_specimens', 'Staging specimens — one row per nodal station / peritoneal site', '''
specimen_id|Specimen ID and linked pathology report|text
site|Exact nodal station / peritoneal or other site|text
method|Sampling method and date|text
examined|Number of nodes examined, when applicable|integer
positive|Number of nodes positive, when applicable|integer
preliminary|Frozen / preliminary result and date|text
final|Permanent result, adequacy and date|text
review|Reviewer, discrepancies and final interpretation|text
''', True)

module('icca', 'iCCA / mixed-tumor focality and histology detail', '''
histology|Expert diagnosis: iCCA / mixed HCC-iCCA / other / uncertain|text
cirrhosis|Evidence and date establishing cirrhosis|text
dominant|Dominant lesion ID and actual diameter / date|text
additional|Additional nodule IDs, certainty and diagnosis|text|||Include possible HCC and benign nodules; do not assume all nodules are iCCA.
pattern|Distribution: unilobar / bilobar, nearby separate nodules and distances|text
terminology|Satellite / intrahepatic-metastasis label used, definition and author/source|text|||Record a descriptive pattern separately from any proven clonal relationship.
clonality|Evidence for shared / separate origin, if tested|text|||Unknown is an acceptable entry; imaging alone is not proof.
solitary|Solitary-tumor criterion assessment and unresolved nodules|text
mixed_acceptance|Local program / NLRB interpretation for mixed histology or concurrent HCC|text
''')

module('colorectal', 'Colorectal primary and molecular profile', '''
primary_site|Primary location and histologic diagnosis|text
diagnosis|Primary and CRLM diagnosis dates / evidence|text
presentation|Synchronous / metachronous presentation and definition used|text
resection|Primary resection date, operation and final margin status|text
primary_stage|Primary pathologic stage, nodal status and adverse features|text
recurrence|Primary-site / local recurrence assessment|text
colonoscopy|Colonoscopy date, completeness, result and report ID|text
braf|BRAF result and exact variant / assay|text
msi_mmr|MSI and MMR results, method and discordance|text
ras|KRAS / NRAS results and exact variants|text
cea|CEA trend with dates, units and relevant confounders|text
max_baseline|Largest pretreatment liver-lesion diameter and source|text
''')

module('pet', 'Functional imaging and treatment timing', '''
study_id|Linked functional-imaging study ID|text
date|Acquisition date|date
tracer|Tracer / modality and protocol|text
treatment_interval|Last relevant systemic-treatment date and elapsed interval|text|||For CRLM record actual chemotherapy timing; any pause is an oncology decision.
sites|Sites of uptake / negative metastatic survey and interpretation|text
discordance|Discordance with anatomic imaging, biomarkers or pathology|text
resolution|Additional evaluation / MDT interpretation|text
''', True)

module('net', 'NET differentiation, function and primary origin', '''
primary|Primary site and evidence / portal drainage|text
differentiation|Well / poorly differentiated / uncertain and expert review|text
grade|Grade, classification/version and specimen|text
ki67|Ki-67 percentage, method, hotspot and specimen/date|text
mitoses|Mitotic count, reporting unit and specimen|text
discordance|Primary versus liver pathology discordance and resolution|text
syndrome|Functional syndrome, biomarkers and control|text
cardiac|Carcinoid-heart-disease assessment if clinically indicated|text
sstr|SSTR expression / imaging assessment and date|text
burden|Liver tumor volume / percentage, method and date|text
clearance|Primary / permitted extrahepatic resection dates, sites and clearance evidence|text
''')

module('hehe', 'HEHE confirmation and behavior', '''
diagnosis|Morphology and expert diagnostic conclusion|text
markers|Endothelial / diagnostic markers and fusion testing if performed|text
angiosarcoma|Angiosarcoma excluded, uncertain or alternative diagnosis; supporting evidence|text
tempo|Interval growth / stability, dates and comparable measurements|text
symptoms|Pain, systemic symptoms and functional impact|text
outside_liver|Extrahepatic site, confirmation, behavior and treatment|text
risk|Risk model name/version, inputs and whether known before transplant|text|||Separate explant findings from pretransplant information; no automated qualification score.
''')

module('adenoma', 'HCA subtype, exposures and complications', '''
subtype|Subtype and basis / certainty|text
beta_catenin|Beta-catenin result, exact mutation/test and specimen|text
number|Adenoma count and method / date|text
size_growth|Largest lesion, size and interval growth / dates|text
anatomy|Exophytic anatomy and vascular relationship|text
exposure|Estrogen / androgen exposure, indication and cessation dates|text
metabolic|Metabolic risk, weight trend and lifestyle intervention / dates|text
gsd|Glycogen storage disease type / confirmation|text
abernethy|Abernethy / portosystemic shunt anatomy and confirmation|text
bleeding|Hemorrhage / rupture date, instability and treatment|text
transformation|Suspected / confirmed malignant transformation and evidence|text
''')

module('hca_indication', 'HCA management and exception rationale', '''
management|Nonoperative / operative management attempted and response|text
observation|Observation / lifestyle-change interval and dated reassessment|text
unresectability|Unresectability evidence where required and alternatives assessed|text
alternative|Specific guidance alternative invoked and supporting findings|text
complication|Progression / hemorrhage / rupture / transformation evidence|text
benefit|Expected individual benefit, competing risks and team decision|text
''')


# Explicit mapping, reviewed against every Tests and information needed item.
MAPPING = {
 'hcc': {
  'diagnosis':['context','imaging','lesions','hcc','labs','pathology'],
  'curative-route':['reserve','labs','imaging','stage','surgery'],
  'allocation':['hcc','lesions','labs','allocation'],
  'treatment':['reserve','therapy','radiation','ici','response','labs'],
  'listing':['hcc','allocation','fitness','ici','milestones'],
  'waitlist':['imaging','lesions','labs','response','reserve','therapy','allocation','milestones'],
  'after-transplant':['transplant','followup','milestones']},
 'pcca': {
  'localize':['context','imaging','biliary','stage','labs','surgery'],
  'diagnosis':['biliary','biliary_sampling','pathology','molecular','staging_specimens','labs'],
  'phenotype':['biliary','imaging','stage','surgery','allocation'],
  'neoadjuvant':['protocol','therapy','radiation','biliary','toxicity','response'],
  'staging':['operative_stage','staging_specimens','pathology','imaging','biliary','fitness'],
  'listing':['allocation','imaging','operative_stage','fitness','milestones'],
  'follow-up':['transplant','protocol','followup','milestones']},
 'icca': {
  'diagnosis':['context','pathology','icca','imaging','stage','labs','molecular'],
  'phenotype':['icca','lesions','stage','surgery'],
  'therapy':['reserve','labs','therapy','radiation','toxicity','ici'],
  'stability':['interval','therapy','imaging','lesions','response','stage'],
  'review':['icca','surgery','interval','allocation','fitness'],
  'follow-up':['fitness','response','transplant','followup','milestones']},
 'crlm': {
  'map-disease':['context','colorectal','imaging','lesions','stage','pathology'],
  'biology':['colorectal','molecular','labs','lesions'],
  'unresectability':['surgery','lesions','imaging','response'],
  'control':['therapy','toxicity','response','interval','surgery'],
  'clocks':['colorectal','interval','therapy','milestones'],
  'restaging':['imaging','pet','stage','labs','colorectal'],
  'review':['allocation','fitness','interval','response','labs','milestones'],
  'transplant':['stage','surgery','fitness','transplant','followup','milestones']},
 'nelm': {
  'biology':['context','pathology','net','therapy'],
  'distribution':['imaging','pet','lesions','stage','net','surgery'],
  'options':['net','surgery','therapy','reserve','response'],
  'exposure':['therapy','radiation','toxicity','reserve','labs'],
  'observation':['net','interval','imaging','pet','stage','response'],
  'review':['net','allocation','fitness','surgery','milestones'],
  'follow-up':['net','transplant','followup','milestones']},
 'hehe': {
  'diagnosis':['context','pathology','hehe','imaging'],
  'stage':['imaging','lesions','stage','hehe','surgery'],
  'risk':['hehe','stage','surgery','fitness'],
  'review':['hehe','stage','surgery','allocation','fitness','milestones'],
  'follow-up':['transplant','hehe','followup','milestones']},
 'hca': {
  'characterize':['context','imaging','lesions','adenoma','pathology','molecular'],
  'standard-care':['adenoma','hca_indication','therapy','surgery','response','interval'],
  'exception-route':['adenoma','hca_indication','surgery','allocation'],
  'transformation':['adenoma','imaging','lesions','pathology','stage','hcc'],
  'review':['hca_indication','allocation','fitness','milestones'],
  'follow-up':['adenoma','response','transplant','followup','milestones']}
}

README = '''# Transplant oncology recording templates

Version: {version}. These are blank documentation tools for the existing review pathways,
not additional test orders, eligibility rules or automatic clearance. Complete applicable
fields in the EHR or an institution-approved data system. The public website has no patient
entry or upload function. Do not publish completed forms or identifying linkage files.

## Clinical use
Use one assessment ID for each decision encounter and a stable coded record ID across care.
Copy the clinical template into the EHR, or print it. Reconcile source reports with the
responsible clinician. A copied prior value must retain its date and source. Record what is
unknown and who will resolve it. Record clinical candidacy separately from allocation review.
Fields can be not applicable; their presence does not mandate a test or procedure.

## Research structure
The dictionary is a local draft, not an endorsed NIH CDE set, a validated registry, or a direct
REDCap import. Stable field IDs, units and response choices support mapping into a governed
registry. Validate that mapping and endpoint definitions before prospective collection.
The package includes all pathway decisions and a blank long-format values CSV for each.

Each values row is one field observation. Key: record_id + assessment_id + module_id +
repeat_instance + field_id. A repeating module uses one instance per imaging study, lesion
time point, specimen, treatment episode, adverse event or follow-up. A field ID is stable
across decisions; an assessment ID distinguishes repeated encounters. Link imaging, lesion,
specimen and treatment IDs explicitly. Add rows/instances without overwriting earlier ones.

value_status: recorded / pending / not_done / not_applicable / unknown / not_documented.
If recorded, enter value and unit where applicable. If not recorded, leave value empty and
state why. Empty, zero, no and not applicable are different. Preserve reported units and
qualifiers. Dates use YYYY-MM-DD (day), YYYY-MM (month), or YYYY (year). Use
value_date_precision for a date-valued field and observed_date_precision for the clinical
measurement date: day / month / year / unknown. Never invent a day to complete a partial date.
The date of a result is separate from data-entry date.
source_document and source_locator identify the report and section; observed_date is the
clinical measurement date. verified_by and verified_date document adjudication. The date and
source columns also apply to the blank narrative fields in the printable/EHR template.

## Longitudinal outcomes
Include evaluated patients who are declined, never listed or never transplanted; record why.
Keep diagnosis, treatment start, listing, exception decision and transplant dates separately.
Define time zero for every analysis. Record death, recurrence, progression, dropout and graft
failure with their ascertainment dates, definitions and sources. Preserve last contact and
censoring reason. Do not assume missing follow-up means no event. Record patient-reported
function using the named instrument/version rather than merging incompatible scales.

## Files
- clinical_templates.md: all decision templates for this pathway.
- dictionary.csv / schema.json: field IDs, meanings, types, units and allowed choices.
- decision_modules.csv: modules used at each clinical decision.
- blank_values/*.csv: blank observations for each decision; duplicate repeat instances as needed.
- source_checklist.csv: the pathway's required-information items, with blank documentation status.
- sources.json: source IDs, titles, authority, locators and official access links.

## Basis
The information checklist and source links come from the existing transplant pathways.
Additional documentation/research fields are local design proposals. OPTN policy and NLRB
guidance remain distinct sources. Current sources checked 2026-10-24:
- https://www.hrsa.gov/sites/default/files/hrsa/optn/optn_policies.pdf
- https://www.hrsa.gov/sites/default/files/hrsa/optn/adult-meld-exception-transplant-oncology-review-guidance.pdf
The NIH CDE repository informs the use of defined fields and value sets, not endorsement:
https://cde.nlm.nih.gov/home
'''


def groups(pathway, step):
    return [MODULES[k] for k in ['record']+MAPPING[pathway['slug']][step['id']]+['decision','research']]


def checklist(step):
    out=[]
    def flatten(items, group):
        for x in items:
            if x.get('children'): flatten(x['children'], group+' / '+x['text'])
            else: out.append(dict(group=group, text=x['text'], refs=x['refs']))
    for g in step['orders']: flatten(g['items'],g['label'])
    return out


def note_md(pathway, step):
    out=[f'# {pathway["code"]} · {step["title"]} — recording template',
         f'Template {VERSION} · {step["question"]}',
         'Complete applicable fields in the EHR / approved clinical system. Blank does not mean negative. These fields record findings; they do not add test requirements or determine eligibility.',
         'For each entry retain the clinical date, source report/section and reviewer. Status: recorded / pending / not done / not applicable / unknown / not documented.',
         '## Information checklist']
    for x in checklist(step):
        out += [f'- [ ] {x["group"]}: {x["text"]}', '  Documentation status: ____  Result / record reference: ____  Date: ____  Outstanding action / clinician / due date: ____']
    for g in groups(pathway,step):
        out += [f'## {g["title"]}'+(' [repeat as needed]' if g['repeat'] else '')]
        if g['repeat']:out += ['Repeat instance ID: ____  Linked assessment ID: ____']
        for f in g['fields']:
            unit=f' ({f["unit"]})' if f['unit'] else ''
            options=f' Options: {" / ".join(c.replace("_", " ") for c in f["choices"])}.' if f['choices'] else ''
            out += [f'- {f["label"]}{unit}: ____________________'+options+(f' {f["help"]}' if f['help'] else ''), '  Clinical date: ____  Source / section: ____  Status: ____  Reviewer: ____']
    return '\n\n'.join(out)+'\n'


def csv_text(headers, rows):
    f=io.StringIO(newline=''); w=csv.writer(f);w.writerow(headers);w.writerows(rows);return f.getvalue()


def dictionary(pathway):
    keys=list(dict.fromkeys(k for s in pathway['steps'] for k in ['record']+MAPPING[pathway['slug']][s['id']]+['decision','research']))
    return [MODULES[k] for k in keys]


VALUE_HEADERS=['record_id','assessment_id','pathway_id','decision_id','module_id','repeat_instance','field_id','value','unit','value_status','missing_reason','value_date_precision','observed_date','observed_date_precision','source_document','source_locator','verified_by','verified_date','entry_date','record_version','supersedes_record']


def blank_values(pathway,step):
    rows=[]
    for g in groups(pathway,step):
        for f in g['fields']:
            fixed=dict(pathway_id=pathway['slug'],decision_id=step['id'],module_id=g['id'],repeat_instance='1',field_id=f['id'],unit=f['unit'])
            rows.append([fixed.get(k,'') for k in VALUE_HEADERS])
    return csv_text(VALUE_HEADERS,rows)


def template_page(pathway, step, sources):
    title=f'{pathway["code"]} · {step["title"]} — recording template'
    gs=groups(pathway,step); sections=[]
    for g in gs:
        rows=[]
        for f in g['fields']:
            unit=f' <span class="unit">({e(f["unit"])})</span>' if f['unit'] else ''
            helptext=f'<small>{e(f["help"])}</small>' if f['help'] else ''
            options=f'<small>Options: {e(" / ".join(c.replace("_", " ") for c in f["choices"]))}</small>' if f['choices'] else ''
            rows.append(f'<tr><th scope="row">{e(f["label"])}{unit}{helptext}{options}</th><td><span class="write-line"></span></td><td class="record-meta">Date: __________<br>Source / section: __________<br>Status: __________<br>Reviewer: __________</td></tr>')
        repeat='<p class="repeat">Repeat this section for each item / time point. Instance ID: __________</p>' if g['repeat'] else ''
        sections.append(f'<section class="record-section" id="{g["id"]}"><h2>{e(g["title"])}</h2>{repeat}<table><thead><tr><th>Information to record</th><th>Value / finding</th><th>Date, source and status</th></tr></thead><tbody>{"".join(rows)}</tbody></table></section>')
    checks=''.join(f'<li><small>{e(x["group"])}</small><b>{e(x["text"])}</b><p>Status: __________ &nbsp; Record / result: __________ &nbsp; Date: __________</p><p>Outstanding action / responsible clinician / due date: ____________________________________</p></li>' for x in checklist(step))
    ref_ids=list(dict.fromkeys(r for x in checklist(step) for r in x['refs']))
    reflinks=''.join(f'<li><a href="{e(sources[r]["url"],quote=True)}">{e(sources[r]["short"])}</a> · {e(sources[r]["locator"])}</li>' for r in ref_ids)
    slug=pathway['slug'];stem=slug+'--'+step['id'];md=note_md(pathway,step)
    dictionary_rows=''.join(f'<tr><td>{e(f["id"])}</td><td>{e(f["type"])}</td><td>{e(f["unit"] or "—")}</td><td>{e("; ".join(f["choices"]) or "—")}</td></tr>' for g in gs for f in g['fields'])
    return f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="robots" content="noindex"><title>{e(title)}</title><link rel="stylesheet" href="templates.css?v={VERSION}"><script src="templates.js?v={VERSION}" defer></script></head><body><main>
<nav><a href="../{slug}/#{step['id']}">← Return to this decision</a> · <a href="index.html">All recording templates</a></nav>
<p class="eyebrow">Memorial Hermann · Transplant oncology · Documentation draft</p><h1>{e(title)}</h1><p class="question">{e(step['question'])}</p>
<div class="actions"><button type="button" data-copy>Copy blank template for EHR</button><button type="button" data-print>Print / save as PDF</button><a href="{stem}.md" download>Download Markdown</a><a href="{slug}-recording-kit.zip" download>Research data kit · ZIP</a></div><p id="copy-status" role="status" aria-live="polite"></p>
<aside><b>Use in the EHR or an approved clinical system.</b> This public page provides a blank template and accepts no patient entries. Record applicable information; the template does not order tests or determine eligibility. Field definitions and repeatable logs are local proposals for clinical documentation and future registry design.</aside>
<p class="instructions">For each value, retain its clinical date, source report / section and reviewer. Use <b>recorded, pending, not done, not applicable, unknown, or not documented</b>; blank does not mean normal or negative. Dates: YYYY-MM-DD, with precision stated for partial dates. Preserve earlier assessments and stable lesion / treatment / specimen IDs.</p>
<details class="section-index"><summary>Sections in this template</summary><ul>{''.join(f'<li><a href="#{g["id"]}">{e(g["title"])}</a></li>' for g in gs)}</ul></details>
<section class="record-section"><h2>Information checklist for this decision</h2><ol class="checklist">{checks}</ol></section>
{''.join(sections)}
<details class="dictionary"><summary>Field IDs and data types for registry mapping</summary><p>Local draft dictionary; not a validated registry or direct REDCap import. The research kit supplies field definitions, units, choices, missing-value rules and blank longitudinal CSVs.</p><div class="table-scroll"><table><thead><tr><th>Field ID</th><th>Type</th><th>Unit</th><th>Choices</th></tr></thead><tbody>{dictionary_rows}</tbody></table></div></details>
<section class="sources"><h2>Sources for the required information</h2><ul>{reflinks}</ul><p>Additional recording and research fields are documentation proposals, not new source-mandated requirements. <a href="README.md">Instructions and research data model</a>.</p></section>
<footer>Template version {VERSION} · Clinical source dates remain on the pathway. Clinical candidacy and allocation eligibility require separate clinician review.</footer>
<pre id="copy-text" hidden>{e(md)}</pre></main></body></html>'''


def build_templates(dist, pathways, sources):
    target=dist/'recording-templates';target.mkdir(exist_ok=True)
    (target/'README.md').write_text(README.format(version=VERSION))
    from shutil import copyfile
    for asset in ['templates.css','templates.js']:
        copyfile(Path(__file__).parent/asset,target/asset)
    count=0; cards=[]
    for p in pathways:
        assert set(MAPPING[p['slug']])=={s['id'] for s in p['steps']},p['slug']
        schema=dict(version=VERSION,pathway=p['slug'],missing_value_status=MISSING,modules=dictionary(p))
        fields=[(g,f) for g in schema['modules'] for f in g['fields']]
        dict_csv=csv_text(['module_id','module_label','repeatable','field_id','label','type','unit','choices','definition'],[[g['id'],g['title'],g['repeat'],f['id'],f['label'],f['type'],f['unit'],';'.join(f['choices']),f['help']] for g,f in fields])
        all_md='\n\n---\n\n'.join(note_md(p,s) for s in p['steps'])
        (target/(p['slug']+'-all-decisions.md')).write_text(all_md)
        with zipfile.ZipFile(target/(p['slug']+'-recording-kit.zip'),'w',zipfile.ZIP_DEFLATED) as z:
            z.writestr('README.md',README.format(version=VERSION));z.writestr('clinical_templates.md',all_md)
            z.writestr('dictionary.csv',dict_csv);z.writestr('schema.json',json.dumps(schema,indent=2,ensure_ascii=False))
            source_ids=set(r for s in p['steps'] for x in checklist(s) for r in x['refs'])
            public_sources={r:{k:v for k,v in sources[r].items() if k!='pdf'} for r in sorted(source_ids)}
            z.writestr('sources.json',json.dumps(public_sources,indent=2,ensure_ascii=False))
            z.writestr('decision_modules.csv',csv_text(['decision_id','decision_label','module_id'],[[s['id'],s['title'],g['id']] for s in p['steps'] for g in groups(p,s)]))
            z.writestr('source_checklist.csv',csv_text(['record_id','assessment_id','decision_id','item_id','group','required_information','source_ids','documentation_status','result_record_reference','observed_date','responsible_clinician','due_date'],[['','',s['id'],f'{s["id"]}.{i+1}',x['group'],x['text'],';'.join(x['refs']),'','','','',''] for s in p['steps'] for i,x in enumerate(checklist(s))]))
            for s in p['steps']:
                gs=groups(p,s);assert all(g['fields'] for g in gs)
                ids=[f['id'] for g in gs for f in g['fields']];assert len(ids)==len(set(ids)),(p['slug'],s['id'])
                stem=p['slug']+'--'+s['id']
                (target/(stem+'.md')).write_text(note_md(p,s))
                (target/(stem+'.html')).write_text(template_page(p,s,sources))
                z.writestr('blank_values/'+s['id']+'.csv',blank_values(p,s));count+=1
        links=''.join(f'<li><a href="{p["slug"]}--{s["id"]}.html">{i+1}. {e(s["title"])}</a></li>' for i,s in enumerate(p['steps']))
        cards.append(f'<section><h2>{e(p["name"])}</h2><ul>{links}</ul><p><a href="{p["slug"]}-all-decisions.md" download>All decision templates · Markdown</a> · <a href="{p["slug"]}-recording-kit.zip" download>Research data kit · ZIP</a></p></section>')
    assert count==46,count
    (target/'index.html').write_text(f'<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Transplant oncology recording templates</title><link rel="stylesheet" href="templates.css?v={VERSION}"></head><body><main><nav><a href="../">← Transplant pathways</a></nav><p class="eyebrow">Documentation draft · {VERSION}</p><h1>Clinical recording templates</h1><p>46 decision-specific templates across seven transplant pathways. Copy into the EHR, print, or download blank structured files for an approved registry. This public site accepts no patient entries.</p><p><a href="README.md">Instructions and data definitions</a></p>{"".join(cards)}</main></body></html>')
    print(f'Built {count} clinical recording templates and {len(pathways)} research data kits.')
