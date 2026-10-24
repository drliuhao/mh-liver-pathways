# HCC · Confirm HCC — recording template

Template 2026-10-24.2 · Is each liver lesion sufficiently characterized to diagnose HCC?

Complete applicable fields in the EHR / approved clinical system. Blank does not mean negative. These fields record findings; they do not add test requirements or determine eligibility.

Record a source and clinical date for each section; use one assessment-level sign-off. Status: recorded / pending / not done / not applicable / unknown / not documented.

## Information checklist

- [ ] Imaging and lesion map: Multiphase liver CT or MRI; transplant-radiology review of adequacy and at-risk liver context.

  Documentation status: ____  Result / record reference: ____  Date: ____  Outstanding action / clinician / due date: ____

- [ ] Imaging and lesion map: For every lesion: segment, maximum diameter, LI-RADS category, imaging date, prior treatment and pretreatment appearance.

  Documentation status: ____  Result / record reference: ____  Date: ____  Outstanding action / clinician / due date: ____

- [ ] Diagnostic context: AFP with trend; liver disease history. AFP alone does not establish HCC.

  Documentation status: ____  Result / record reference: ____  Date: ____  Outstanding action / clinician / due date: ____

- [ ] Diagnostic context: If imaging is indeterminate or the liver is outside the imaging-diagnosis population, decide whether tissue is needed.

  Documentation status: ____  Result / record reference: ____  Date: ____  Outstanding action / clinician / due date: ____

## Assessment identification

Section source / report: ____  Observation date: ____

- Coded patient / registry ID: ____________________ Use a coded ID in research exports. Keep any identifying linkage in the approved clinical system.

- Unique assessment ID: ____________________ New ID for each encounter or reassessment; retain earlier records.

- Date of clinical assessment: ____________________ YYYY-MM-DD; document date precision if only month or year is known.

- Phase of care: ____________________ Options: referral / evaluation / pretransplant treatment / listed / temporarily inactive / posttransplant / other.

- Treating center / service: ____________________

- Responsible clinician and role: ____________________

- Person recording / abstracting the information: ____________________

- Date entered: ____________________

- Local protocol name, version and approval status: ____________________

- Policy / guidance version used and date checked: ____________________ Record the version actually used for this assessment.

## Patient and liver-disease context

Section source / report: ____  Observation date: ____

- Age at assessment (years): ____________________

- Sex recorded for relevant clinical assessment: ____________________ Record source and clinical context; do not infer from name or gender identity.

- Date diagnosis was established: ____________________

- Basis for diagnosis: ____________________ Options: imaging / histology / cytology / protocol diagnostic criteria / other.

- Underlying liver disease and etiology: ____________________

- Cirrhosis: ____________________ Options: present / absent / uncertain / not assessed.

- Other malignancy, activity and treatment history: ____________________

- Current symptoms, severity and functional effect: ____________________

- Patient goals and treatment preferences: ____________________

## Imaging studies — one entry per examination [repeat as needed]

Repeat instance ID: ____  Linked assessment ID: ____

Section source / report: ____  Observation date: ____

- Stable imaging-study ID: ____________________

- Acquisition date: ____________________

- Imaging modality: ____________________ Options: CT / MRI / CEUS / PET CT / PET MRI / ultrasound / other.

- Anatomic coverage: ____________________ Liver, chest, abdomen, pelvis or other sites; record what was actually examined.

- Technical adequacy: ____________________ Options: adequate / limited / nondiagnostic.

- Comparison study IDs and dates: ____________________

- Expert radiology review, reviewer and date: ____________________

- Overall impression and uncertain findings: ____________________

- Contrast phases / imaging protocol: ____________________

## Liver lesion map — one entry per lesion at each imaging time point [repeat as needed]

Repeat instance ID: ____  Linked assessment ID: ____

Section source / report: ____  Observation date: ____

- Stable lesion ID: ____________________ Keep the same ID across scans, treatments and explant correlation; include disappeared sites.

- Linked imaging-study ID: ____________________

- Liver segment / distribution: ____________________ Options: I / II / III / IVa / IVb / V / VI / VII / VIII / multiple segments / other.

- Maximum total lesion diameter (mm): ____________________

- Maximum viable enhancing component, if applicable (mm): ____________________ Do not substitute treated-cavity size for viable-tumor size.

- Pretreatment maximum diameter (mm): ____________________

- Lesion diagnosis / suspicion: ____________________ Options: HCC / iCCA / mixed HCC iCCA / metastasis / benign / indeterminate / treated site / other.

- Imaging classification: ____________________ Options: LR 1 / LR 2 / LR 3 / LR 4 / LR 5 / LR M / LR TIV / LR NC / LR TR nonviable / LR TR viable / LR TR equivocal / LR TR nonevaluable / LR TR nonprogressing / not applicable / other. Use the classification and algorithm version in the radiology report.

- Relation to dominant tumor / nearby separate nodules: ____________________ Record distance, segment and distribution if available; a satellite label alone does not prove clonal origin.

- Linked treatment episode IDs: ____________________

- Linked tissue / explant specimen IDs: ____________________

- Diagnostic certainty: ____________________ Options: confirmed / suspected / indeterminate.

- Pretreatment measurement date: ____________________

- Classification / treatment-response algorithm version: ____________________

- Distance from dominant lesion, if relevant (mm): ____________________

## HCC diagnosis and allocation detail

Section source / report: ____  Observation date: ____

- Imaging-diagnosis population / liver background and evidence: ____________________

- Class 5 adjudication for each relevant lesion ID: ____________________ Keep indeterminate observations separate; cite the criterion/version used.

- Qualifying pretreatment lesion count: ____________________

- Sum of qualifying pretreatment diameters (mm): ____________________

- Highest documented AFP (ng/mL): ____________________

- AFP ever above 1,000 ng/mL: ____________________ Options: yes / no / unknown. Retain the subsequent dated AFP trend in the laboratory records.

- Clinical selection and allocation categories assessed: ____________________ Record Milan clinical assessment, T2, standardized downstaging or nonstandard review separately.

- Prior rupture or vascular invasion: dates, vessel/level, treatment and stability: ____________________

- Peak AFP collection date: ____________________

## Laboratory results — one entry per analyte and date [repeat as needed]

Repeat instance ID: ____  Linked assessment ID: ____

Section source / report: ____  Observation date: ____

- Analyte / test: ____________________ Options: bilirubin / albumin / INR / creatinine / sodium / platelets / hemoglobin / WBC / ANC / AST / ALT / ALP / AFP / CEA / CA 19-9 / IgG4 / other.

- Reported numeric value: ____________________ Keep the original value; do not convert missing results to zero.

- Result qualifier: ____________________ Options: exact / less than / greater than / below detection / qualitative.

- Reported unit: ____________________ Options: mg/dL / g/dL / mmol/L / 10^9/L / ng/mL / U/mL / U/L / unitless / other.

- Qualitative result, if applicable: ____________________

- Specimen collection date: ____________________

- Laboratory reference range: ____________________

- Relevant context at collection: ____________________ Cholangitis, obstruction/drainage, anticoagulation, dialysis, recent treatment or other confounder.

## Tissue / pathology — one entry per specimen [repeat as needed]

Repeat instance ID: ____  Linked assessment ID: ____

Section source / report: ____  Observation date: ____

- Specimen ID / source-report reference: ____________________

- Collection date: ____________________

- Exact sampled site / lesion or nodal station: ____________________

- Tissue acquisition method: ____________________ Options: core biopsy / brushing / intraductal biopsy / FNA / resection / explant / other.

- Sampling route: ____________________ Options: intraductal / percutaneous transperitoneal / EUS transperitoneal / operative / other / uncertain. Record the target separately. Primary-tumor and nodal sampling have different implications.

- Specimen adequacy: ____________________ Options: adequate / limited / nondiagnostic / pending.

- Pathologic diagnosis: ____________________ Options: HCC / iCCA / pCCA / mixed HCC iCCA / colorectal adenocarcinoma / well differentiated NET / poorly differentiated NEC / HEHE / HCA / benign / indeterminate / other.

- Differentiation: ____________________ Options: well / moderate / poor / undifferentiated / not assessed / other. Specify the grading system / version and any discordance in Notes.

- Immunohistochemistry, molecular findings and interpretation: ____________________

- Expert pathology reviewer, date and concordance: ____________________

## Clinical decision, actions and sign-off

Section source / report: ____  Observation date: ____

- Multidisciplinary review date: ____________________

- Clinical assessment: ____________________ Options: proceed with evaluation / proceed with treatment / pause for information / use alternative treatment / decline transplant / continue follow up / other.

- Clinical rationale, alternatives and benefit-risk discussion: ____________________

- Separate allocation conclusion / unresolved question: ____________________

- Discordant findings, uncertainty and how they will be resolved: ____________________

- Next actions, responsible clinician and due dates: ____________________

- Departure from protocol / pathway and rationale: ____________________

- Patient / referring-team communication and date: ____________________

- Next review date: ____________________

- Reviewer / typed signature: ____________________ One sign-off for this entire assessment; a typed name is not identity-authenticated by this site.

- MDT participants: ____________________

- Sign-off date: ____________________

- Assessment review status: ____________________ Options: draft / reviewed.

## Research and data-quality extension

Section source / report: ____  Observation date: ____

- Registry / study name and local approval reference: ____________________ Optional research fields; collection/use requires the applicable institutional process.

- Consent / waiver / permitted-use status and date: ____________________

- Analysis time-zero event and date: ____________________ Preserve referral, diagnosis, treatment, listing and transplant dates separately; specify which defines each endpoint.

- Outcome definition / protocol version used: ____________________ Specify survival, recurrence, progression, graft failure or dropout definition and time origin.

- Last date the endpoint was assessed and method: ____________________

- Censoring / lost-to-follow-up status, date and reason: ____________________ Do not equate missing follow-up with absence of an event.

- Data queries, discordance, resolution and adjudicator/date: ____________________

- Record version, correction reason and superseded record ID: ____________________ Retain the earlier value and its source in the governed system.


---

# HCC · Choose treatment with curative intent — recording template

Template 2026-10-24.2 · Is transplantation clinically preferable to a safe, complete resection?

Complete applicable fields in the EHR / approved clinical system. Blank does not mean negative. These fields record findings; they do not add test requirements or determine eligibility.

Record a source and clinical date for each section; use one assessment-level sign-off. Status: recorded / pending / not done / not applicable / unknown / not documented.

## Information checklist

- [ ] Liver reserve: Bilirubin, albumin, INR, creatinine, sodium, platelets; Child-Pugh and MELD assessment.

  Documentation status: ____  Result / record reference: ____  Date: ____  Outstanding action / clinician / due date: ____

- [ ] Liver reserve: Ascites, encephalopathy, varices, splenomegaly and other portal-hypertension evidence. Assess ECOG, nutrition and frailty.

  Documentation status: ____  Result / record reference: ____  Date: ____  Outstanding action / clinician / due date: ____

- [ ] Tumor stage and operation feasibility: Chest CT for initial exception staging; liver CT/MRI for vascular invasion and extrahepatic spread.

  Documentation status: ____  Result / record reference: ____  Date: ____  Outstanding action / clinician / due date: ____

- [ ] Tumor stage and operation feasibility: HPB review: achievable clearance, future liver remnant, inflow/outflow and biliary drainage; record why resection is or is not appropriate.

  Documentation status: ____  Result / record reference: ____  Date: ____  Outstanding action / clinician / due date: ____

## Assessment identification

Section source / report: ____  Observation date: ____

- Coded patient / registry ID: ____________________ Use a coded ID in research exports. Keep any identifying linkage in the approved clinical system.

- Unique assessment ID: ____________________ New ID for each encounter or reassessment; retain earlier records.

- Date of clinical assessment: ____________________ YYYY-MM-DD; document date precision if only month or year is known.

- Phase of care: ____________________ Options: referral / evaluation / pretransplant treatment / listed / temporarily inactive / posttransplant / other.

- Treating center / service: ____________________

- Responsible clinician and role: ____________________

- Person recording / abstracting the information: ____________________

- Date entered: ____________________

- Local protocol name, version and approval status: ____________________

- Policy / guidance version used and date checked: ____________________ Record the version actually used for this assessment.

## Liver reserve, nutrition and function

Section source / report: ____  Observation date: ____

- Calculated MELD value: ____________________ Enter the reported calculation; this form does not calculate MELD or exception scores.

- Child-Pugh class: ____________________ Options: A / B / C / not assessed.

- Ascites: ____________________ Options: absent / controlled / poorly controlled / not assessed.

- Encephalopathy: ____________________ Options: absent / present controlled / present not controlled / not assessed.

- Portal-hypertension evidence: ____________________ Varices/bleeding, splenomegaly, platelets, collaterals and pressure measurement if available.

- Renal function and dialysis status / dates: ____________________

- ECOG performance status: ____________________ Options: 0 / 1 / 2 / 3 / 4 / not assessable.

- Frailty / physical-function tool, value and date: ____________________ Name the instrument; retain raw components where available.

- Nutrition assessment, weight trend and sarcopenia assessment: ____________________

- MELD version: ____________________ Options: MELD 3.0 / MELD Na / MELD / other.

- MELD calculation date: ____________________

- Child-Pugh score: ____________________

## Laboratory results — one entry per analyte and date [repeat as needed]

Repeat instance ID: ____  Linked assessment ID: ____

Section source / report: ____  Observation date: ____

- Analyte / test: ____________________ Options: bilirubin / albumin / INR / creatinine / sodium / platelets / hemoglobin / WBC / ANC / AST / ALT / ALP / AFP / CEA / CA 19-9 / IgG4 / other.

- Reported numeric value: ____________________ Keep the original value; do not convert missing results to zero.

- Result qualifier: ____________________ Options: exact / less than / greater than / below detection / qualitative.

- Reported unit: ____________________ Options: mg/dL / g/dL / mmol/L / 10^9/L / ng/mL / U/mL / U/L / unitless / other.

- Qualitative result, if applicable: ____________________

- Specimen collection date: ____________________

- Laboratory reference range: ____________________

- Relevant context at collection: ____________________ Cholangitis, obstruction/drainage, anticoagulation, dialysis, recent treatment or other confounder.

## Imaging studies — one entry per examination [repeat as needed]

Repeat instance ID: ____  Linked assessment ID: ____

Section source / report: ____  Observation date: ____

- Stable imaging-study ID: ____________________

- Acquisition date: ____________________

- Imaging modality: ____________________ Options: CT / MRI / CEUS / PET CT / PET MRI / ultrasound / other.

- Anatomic coverage: ____________________ Liver, chest, abdomen, pelvis or other sites; record what was actually examined.

- Technical adequacy: ____________________ Options: adequate / limited / nondiagnostic.

- Comparison study IDs and dates: ____________________

- Expert radiology review, reviewer and date: ____________________

- Overall impression and uncertain findings: ____________________

- Contrast phases / imaging protocol: ____________________

## Disease extent and staging assessment

Section source / report: ____  Observation date: ____

- Confirmed liver tumor count: ____________________

- Vascular tumor involvement: ____________________ Options: present / absent / uncertain / not assessed. Describe vessel, level, extent and distinction from bland thrombosis in Notes.

- Regional nodal status: ____________________ Options: not detected / suspected / confirmed / indeterminate / not assessed.

- Extrahepatic disease: ____________________ Options: not detected / suspected / confirmed / indeterminate / not assessed.

- Peritoneal disease: ____________________ Options: not detected / suspected / confirmed / indeterminate / not assessed.

- Clinical TNM, staging edition and date: ____________________ T, N, M and overall stage separately; record uncertainty rather than deriving stage from lesion count alone.

- Unresolved staging findings and plan: ____________________

- Tumor distribution: ____________________ Options: solitary / multiple unilobar / multiple bilobar / diffuse / indeterminate.

## Resection and alternative-treatment assessment

Section source / report: ____  Observation date: ____

- HPB review date: ____________________

- Complete safe resection / ablation assessment: ____________________ Options: feasible / potentially feasible after treatment / not feasible / uncertain.

- Proposed operation / combined treatment and sites addressed: ____________________

- Future liver remnant (%): ____________________

- Inflow, outflow, biliary drainage and reconstruction requirements: ____________________

- Specific technical or liver-function barriers: ____________________ State the anatomical / functional reason; lesion count alone is insufficient.

- Alternatives assessed and reasons accepted or rejected: ____________________ Include staged/parenchymal-sparing surgery, ablation, remnant augmentation or observation when relevant.

- Conditions for reassessment, date and responsible clinician: ____________________

- Reviewing surgeons: ____________________

- Future liver remnant volume (mL): ____________________

- Volumetry method and functional assessment: ____________________

## Clinical decision, actions and sign-off

Section source / report: ____  Observation date: ____

- Multidisciplinary review date: ____________________

- Clinical assessment: ____________________ Options: proceed with evaluation / proceed with treatment / pause for information / use alternative treatment / decline transplant / continue follow up / other.

- Clinical rationale, alternatives and benefit-risk discussion: ____________________

- Separate allocation conclusion / unresolved question: ____________________

- Discordant findings, uncertainty and how they will be resolved: ____________________

- Next actions, responsible clinician and due dates: ____________________

- Departure from protocol / pathway and rationale: ____________________

- Patient / referring-team communication and date: ____________________

- Next review date: ____________________

- Reviewer / typed signature: ____________________ One sign-off for this entire assessment; a typed name is not identity-authenticated by this site.

- MDT participants: ____________________

- Sign-off date: ____________________

- Assessment review status: ____________________ Options: draft / reviewed.

## Research and data-quality extension

Section source / report: ____  Observation date: ____

- Registry / study name and local approval reference: ____________________ Optional research fields; collection/use requires the applicable institutional process.

- Consent / waiver / permitted-use status and date: ____________________

- Analysis time-zero event and date: ____________________ Preserve referral, diagnosis, treatment, listing and transplant dates separately; specify which defines each endpoint.

- Outcome definition / protocol version used: ____________________ Specify survival, recurrence, progression, graft failure or dropout definition and time origin.

- Last date the endpoint was assessed and method: ____________________

- Censoring / lost-to-follow-up status, date and reason: ____________________ Do not equate missing follow-up with absence of an event.

- Data queries, discordance, resolution and adjudicator/date: ____________________

- Record version, correction reason and superseded record ID: ____________________ Retain the earlier value and its source in the governed system.


---

# HCC · Check MELD-exception criteria — recording template

Template 2026-10-24.2 · Does pretreatment tumor burden fit T2 or the standardized downstaging criteria?

Complete applicable fields in the EHR / approved clinical system. Blank does not mean negative. These fields record findings; they do not add test requirements or determine eligibility.

Record a source and clinical date for each section; use one assessment-level sign-off. Status: recorded / pending / not done / not applicable / unknown / not documented.

## Information checklist

- [ ] Baseline record: Count qualifying Class 5 lesions and record each diameter before LRT. Keep indeterminate observations separate.

  Documentation status: ____  Result / record reference: ____  Date: ____  Outstanding action / clinician / due date: ____

- [ ] Baseline record: Record current AFP and whether AFP has EVER exceeded 1,000 ng/mL.

  Documentation status: ____  Result / record reference: ____  Date: ____  Outstanding action / clinician / due date: ____

## Assessment identification

Section source / report: ____  Observation date: ____

- Coded patient / registry ID: ____________________ Use a coded ID in research exports. Keep any identifying linkage in the approved clinical system.

- Unique assessment ID: ____________________ New ID for each encounter or reassessment; retain earlier records.

- Date of clinical assessment: ____________________ YYYY-MM-DD; document date precision if only month or year is known.

- Phase of care: ____________________ Options: referral / evaluation / pretransplant treatment / listed / temporarily inactive / posttransplant / other.

- Treating center / service: ____________________

- Responsible clinician and role: ____________________

- Person recording / abstracting the information: ____________________

- Date entered: ____________________

- Local protocol name, version and approval status: ____________________

- Policy / guidance version used and date checked: ____________________ Record the version actually used for this assessment.

## HCC diagnosis and allocation detail

Section source / report: ____  Observation date: ____

- Imaging-diagnosis population / liver background and evidence: ____________________

- Class 5 adjudication for each relevant lesion ID: ____________________ Keep indeterminate observations separate; cite the criterion/version used.

- Qualifying pretreatment lesion count: ____________________

- Sum of qualifying pretreatment diameters (mm): ____________________

- Highest documented AFP (ng/mL): ____________________

- AFP ever above 1,000 ng/mL: ____________________ Options: yes / no / unknown. Retain the subsequent dated AFP trend in the laboratory records.

- Clinical selection and allocation categories assessed: ____________________ Record Milan clinical assessment, T2, standardized downstaging or nonstandard review separately.

- Prior rupture or vascular invasion: dates, vessel/level, treatment and stability: ____________________

- Peak AFP collection date: ____________________

## Liver lesion map — one entry per lesion at each imaging time point [repeat as needed]

Repeat instance ID: ____  Linked assessment ID: ____

Section source / report: ____  Observation date: ____

- Stable lesion ID: ____________________ Keep the same ID across scans, treatments and explant correlation; include disappeared sites.

- Linked imaging-study ID: ____________________

- Liver segment / distribution: ____________________ Options: I / II / III / IVa / IVb / V / VI / VII / VIII / multiple segments / other.

- Maximum total lesion diameter (mm): ____________________

- Maximum viable enhancing component, if applicable (mm): ____________________ Do not substitute treated-cavity size for viable-tumor size.

- Pretreatment maximum diameter (mm): ____________________

- Lesion diagnosis / suspicion: ____________________ Options: HCC / iCCA / mixed HCC iCCA / metastasis / benign / indeterminate / treated site / other.

- Imaging classification: ____________________ Options: LR 1 / LR 2 / LR 3 / LR 4 / LR 5 / LR M / LR TIV / LR NC / LR TR nonviable / LR TR viable / LR TR equivocal / LR TR nonevaluable / LR TR nonprogressing / not applicable / other. Use the classification and algorithm version in the radiology report.

- Relation to dominant tumor / nearby separate nodules: ____________________ Record distance, segment and distribution if available; a satellite label alone does not prove clonal origin.

- Linked treatment episode IDs: ____________________

- Linked tissue / explant specimen IDs: ____________________

- Diagnostic certainty: ____________________ Options: confirmed / suspected / indeterminate.

- Pretreatment measurement date: ____________________

- Classification / treatment-response algorithm version: ____________________

- Distance from dominant lesion, if relevant (mm): ____________________

## Laboratory results — one entry per analyte and date [repeat as needed]

Repeat instance ID: ____  Linked assessment ID: ____

Section source / report: ____  Observation date: ____

- Analyte / test: ____________________ Options: bilirubin / albumin / INR / creatinine / sodium / platelets / hemoglobin / WBC / ANC / AST / ALT / ALP / AFP / CEA / CA 19-9 / IgG4 / other.

- Reported numeric value: ____________________ Keep the original value; do not convert missing results to zero.

- Result qualifier: ____________________ Options: exact / less than / greater than / below detection / qualitative.

- Reported unit: ____________________ Options: mg/dL / g/dL / mmol/L / 10^9/L / ng/mL / U/mL / U/L / unitless / other.

- Qualitative result, if applicable: ____________________

- Specimen collection date: ____________________

- Laboratory reference range: ____________________

- Relevant context at collection: ____________________ Cholangitis, obstruction/drainage, anticoagulation, dialysis, recent treatment or other confounder.

## Exception request and allocation record

Section source / report: ____  Observation date: ____

- Request route: ____________________ Options: standardized / nonstandard nlrb / native meld / other / not determined.

- Request type: ____________________ Options: initial / extension / appeal / other.

- Submitted / planned submission date: ____________________

- Policy / guidance version, section and verification date: ____________________

- Criterion-by-criterion assessment and supporting record IDs: ____________________ Met / not met / uncertain / not applicable for each; explain discrepancies.

- Assigned exception / allocation score: ____________________

- Review disposition: ____________________ Options: not submitted / pending / approved / denied / withdrawn / appeal / other.

- Allocation disposition date: ____________________

- Renewal / expiry date: ____________________

- Allocation coordinator / clinician and verification date: ____________________

- Requested exception score: ____________________

- MMaT reference: ____________________

- Score / MMaT reference date: ____________________

- Official request ID: ____________________

## Clinical decision, actions and sign-off

Section source / report: ____  Observation date: ____

- Multidisciplinary review date: ____________________

- Clinical assessment: ____________________ Options: proceed with evaluation / proceed with treatment / pause for information / use alternative treatment / decline transplant / continue follow up / other.

- Clinical rationale, alternatives and benefit-risk discussion: ____________________

- Separate allocation conclusion / unresolved question: ____________________

- Discordant findings, uncertainty and how they will be resolved: ____________________

- Next actions, responsible clinician and due dates: ____________________

- Departure from protocol / pathway and rationale: ____________________

- Patient / referring-team communication and date: ____________________

- Next review date: ____________________

- Reviewer / typed signature: ____________________ One sign-off for this entire assessment; a typed name is not identity-authenticated by this site.

- MDT participants: ____________________

- Sign-off date: ____________________

- Assessment review status: ____________________ Options: draft / reviewed.

## Research and data-quality extension

Section source / report: ____  Observation date: ____

- Registry / study name and local approval reference: ____________________ Optional research fields; collection/use requires the applicable institutional process.

- Consent / waiver / permitted-use status and date: ____________________

- Analysis time-zero event and date: ____________________ Preserve referral, diagnosis, treatment, listing and transplant dates separately; specify which defines each endpoint.

- Outcome definition / protocol version used: ____________________ Specify survival, recurrence, progression, graft failure or dropout definition and time origin.

- Last date the endpoint was assessed and method: ____________________

- Censoring / lost-to-follow-up status, date and reason: ____________________ Do not equate missing follow-up with absence of an event.

- Data queries, discordance, resolution and adjudicator/date: ____________________

- Record version, correction reason and superseded record ID: ____________________ Retain the earlier value and its source in the governed system.


---

# HCC · Bridge or downstage — recording template

Template 2026-10-24.2 · What treatment and response assessment are needed to maintain or achieve transplant eligibility?

Complete applicable fields in the EHR / approved clinical system. Blank does not mean negative. These fields record findings; they do not add test requirements or determine eligibility.

Record a source and clinical date for each section; use one assessment-level sign-off. Status: recorded / pending / not done / not applicable / unknown / not documented.

## Information checklist

- [ ] Treatment planning: Specify bridge versus downstaging; document anatomy, liver reserve, anticipated wait and modality rationale.

  Documentation status: ____  Result / record reference: ____  Date: ____  Outstanding action / clinician / due date: ____

- [ ] Treatment planning: Record dates of LRT and all systemic agents, especially immune checkpoint inhibitors.

  Documentation status: ____  Result / record reference: ____  Date: ____  Outstanding action / clinician / due date: ____

- [ ] Response evidence: Schedule multiphase CT/MRI and AFP; NLRB guidance advises imaging ≥4 weeks after the last downstaging treatment.

  Documentation status: ____  Result / record reference: ____  Date: ____  Outstanding action / clinician / due date: ____

- [ ] Response evidence: Report residual viable disease separately from the entire treated cavity; retain baseline tumor history.

  Documentation status: ____  Result / record reference: ____  Date: ____  Outstanding action / clinician / due date: ____

## Assessment identification

Section source / report: ____  Observation date: ____

- Coded patient / registry ID: ____________________ Use a coded ID in research exports. Keep any identifying linkage in the approved clinical system.

- Unique assessment ID: ____________________ New ID for each encounter or reassessment; retain earlier records.

- Date of clinical assessment: ____________________ YYYY-MM-DD; document date precision if only month or year is known.

- Phase of care: ____________________ Options: referral / evaluation / pretransplant treatment / listed / temporarily inactive / posttransplant / other.

- Treating center / service: ____________________

- Responsible clinician and role: ____________________

- Person recording / abstracting the information: ____________________

- Date entered: ____________________

- Local protocol name, version and approval status: ____________________

- Policy / guidance version used and date checked: ____________________ Record the version actually used for this assessment.

## Liver reserve, nutrition and function

Section source / report: ____  Observation date: ____

- Calculated MELD value: ____________________ Enter the reported calculation; this form does not calculate MELD or exception scores.

- Child-Pugh class: ____________________ Options: A / B / C / not assessed.

- Ascites: ____________________ Options: absent / controlled / poorly controlled / not assessed.

- Encephalopathy: ____________________ Options: absent / present controlled / present not controlled / not assessed.

- Portal-hypertension evidence: ____________________ Varices/bleeding, splenomegaly, platelets, collaterals and pressure measurement if available.

- Renal function and dialysis status / dates: ____________________

- ECOG performance status: ____________________ Options: 0 / 1 / 2 / 3 / 4 / not assessable.

- Frailty / physical-function tool, value and date: ____________________ Name the instrument; retain raw components where available.

- Nutrition assessment, weight trend and sarcopenia assessment: ____________________

- MELD version: ____________________ Options: MELD 3.0 / MELD Na / MELD / other.

- MELD calculation date: ____________________

- Child-Pugh score: ____________________

## Treatment episodes — repeat for each regimen, cycle group or procedure [repeat as needed]

Repeat instance ID: ____  Linked assessment ID: ____

Section source / report: ____  Observation date: ____

- Stable treatment episode ID: ____________________

- Treatment intent: ____________________ Options: bridge / downstaging / conversion / disease control / curative intent / adjuvant / symptom control / other.

- Treatment modality: ____________________ Options: systemic therapy / resection / thermal ablation / SBRT / external beam radiation / Y90 / TACE / HAI / histotripsy / PRRT / other.

- Drug(s), regimen and line of therapy: ____________________

- Start date: ____________________

- Last administered dose / procedure date: ____________________

- End / stop date: ____________________

- Planned and delivered doses, units and cycles: ____________________

- Dose delays, reductions, omissions and reasons: ____________________

- Planned response examination and date: ____________________

- Reason stopped or changed: ____________________

- Target lesion / site IDs: ____________________

- Cycles delivered: ____________________

## Radiation / radiopharmaceutical exposure, when applicable [repeat as needed]

Repeat instance ID: ____  Linked assessment ID: ____

Section source / report: ____  Observation date: ____

- Linked treatment episode ID: ____________________

- Radiation / radiopharmaceutical technique: ____________________ Options: external beam radiation / SBRT / brachytherapy / Y90 / PRRT / other.

- Planning / mapping date and method: ____________________

- Delivered dose / administered activity: ____________________

- Fractions / administrations delivered: ____________________

- Target volume and uninvolved liver / organ-at-risk assessment: ____________________

- Tumor and normal-tissue dose estimates, method and limitations: ____________________

- Prior/cumulative exposure and safety interpretation: ____________________

- Dose / activity unit: ____________________ Options: Gy / GBq / MBq / mCi / other.

- Planned dose / activity: ____________________

- Planned fractions / administrations: ____________________

## Immune-checkpoint inhibitor exposure and transplant safety

Section source / report: ____  Observation date: ____

- Exposure status: ____________________ Options: never exposed / prior exposure / current / uncertain.

- Agent(s), combination and treatment episode IDs: ____________________

- Last ICI dose date: ____________________

- Immune-related toxicity, organ, grade and resolution: ____________________

- Steroid / other immunosuppression used for toxicity: ____________________

- Proposed transplant date and elapsed days from last ICI: ____________________ Record both dates and interval; no interval is asserted to guarantee safety.

- Transplant, oncology and pharmacy review / date: ____________________

- Risk discussion, immunosuppression / monitoring plan and unresolved issues: ____________________

## Response assessments — one entry per time point [repeat as needed]

Repeat instance ID: ____  Linked assessment ID: ____

Section source / report: ____  Observation date: ____

- Assessment date: ____________________

- Linked imaging-study IDs and biomarker dates: ____________________

- Comparator / baseline date and tumor measurements: ____________________

- Response assessment system: ____________________ Options: RECIST 1.1 / mRECIST / LI RADS treatment response / other.

- Reported response: ____________________ Options: complete response / partial response / stable disease / progressive disease / nonviable / viable / equivocal / nonevaluable / nonprogressing / other. Select the reported designation within the named response system; these systems are not interchangeable.

- New lesions: ____________________ Options: none detected / suspected / confirmed / indeterminate / not assessed. Specify sites, certainty and action in Notes.

- Extrahepatic status: ____________________ Options: not detected / suspected / confirmed / indeterminate / not assessed.

- Reviewer and unresolved discordance: ____________________

## Laboratory results — one entry per analyte and date [repeat as needed]

Repeat instance ID: ____  Linked assessment ID: ____

Section source / report: ____  Observation date: ____

- Analyte / test: ____________________ Options: bilirubin / albumin / INR / creatinine / sodium / platelets / hemoglobin / WBC / ANC / AST / ALT / ALP / AFP / CEA / CA 19-9 / IgG4 / other.

- Reported numeric value: ____________________ Keep the original value; do not convert missing results to zero.

- Result qualifier: ____________________ Options: exact / less than / greater than / below detection / qualitative.

- Reported unit: ____________________ Options: mg/dL / g/dL / mmol/L / 10^9/L / ng/mL / U/mL / U/L / unitless / other.

- Qualitative result, if applicable: ____________________

- Specimen collection date: ____________________

- Laboratory reference range: ____________________

- Relevant context at collection: ____________________ Cholangitis, obstruction/drainage, anticoagulation, dialysis, recent treatment or other confounder.

## Clinical decision, actions and sign-off

Section source / report: ____  Observation date: ____

- Multidisciplinary review date: ____________________

- Clinical assessment: ____________________ Options: proceed with evaluation / proceed with treatment / pause for information / use alternative treatment / decline transplant / continue follow up / other.

- Clinical rationale, alternatives and benefit-risk discussion: ____________________

- Separate allocation conclusion / unresolved question: ____________________

- Discordant findings, uncertainty and how they will be resolved: ____________________

- Next actions, responsible clinician and due dates: ____________________

- Departure from protocol / pathway and rationale: ____________________

- Patient / referring-team communication and date: ____________________

- Next review date: ____________________

- Reviewer / typed signature: ____________________ One sign-off for this entire assessment; a typed name is not identity-authenticated by this site.

- MDT participants: ____________________

- Sign-off date: ____________________

- Assessment review status: ____________________ Options: draft / reviewed.

## Research and data-quality extension

Section source / report: ____  Observation date: ____

- Registry / study name and local approval reference: ____________________ Optional research fields; collection/use requires the applicable institutional process.

- Consent / waiver / permitted-use status and date: ____________________

- Analysis time-zero event and date: ____________________ Preserve referral, diagnosis, treatment, listing and transplant dates separately; specify which defines each endpoint.

- Outcome definition / protocol version used: ____________________ Specify survival, recurrence, progression, graft failure or dropout definition and time origin.

- Last date the endpoint was assessed and method: ____________________

- Censoring / lost-to-follow-up status, date and reason: ____________________ Do not equate missing follow-up with absence of an event.

- Data queries, discordance, resolution and adjudicator/date: ____________________

- Record version, correction reason and superseded record ID: ____________________ Retain the earlier value and its source in the governed system.


---

# HCC · Verify listing record — recording template

Template 2026-10-24.2 · Are clinical clearance, exception evidence and treatment-safety review all complete?

Complete applicable fields in the EHR / approved clinical system. Blank does not mean negative. These fields record findings; they do not add test requirements or determine eligibility.

Record a source and clinical date for each section; use one assessment-level sign-off. Status: recorded / pending / not done / not applicable / unknown / not documented.

## Information checklist

- [ ] Allocation packet: Baseline and response images, Class 5 assessments, AFP chronology, initial chest CT, LRT record and resection-ineligibility statement.

  Documentation status: ____  Result / record reference: ____  Date: ____  Outstanding action / clinician / due date: ____

- [ ] Allocation packet: For adults, initial request and first extension retain calculated MELD; subsequent eligible extensions receive MMaT−3. Verify current policy at filing.

  Documentation status: ____  Result / record reference: ____  Date: ____  Outstanding action / clinician / due date: ____

- [ ] Clinical safety — a separate decision: Complete the center’s medical, cardiopulmonary, infectious, functional and psychosocial evaluation. An exception does not establish surgical fitness.

  Documentation status: ____  Result / record reference: ____  Date: ____  Outstanding action / clinician / due date: ____

- [ ] Clinical safety — a separate decision: For ICI exposure: agent, last dose, toxicity history and transplant/pharmacy risk plan; distinguish exception consideration from rejection safety.

  Documentation status: ____  Result / record reference: ____  Date: ____  Outstanding action / clinician / due date: ____

## Assessment identification

Section source / report: ____  Observation date: ____

- Coded patient / registry ID: ____________________ Use a coded ID in research exports. Keep any identifying linkage in the approved clinical system.

- Unique assessment ID: ____________________ New ID for each encounter or reassessment; retain earlier records.

- Date of clinical assessment: ____________________ YYYY-MM-DD; document date precision if only month or year is known.

- Phase of care: ____________________ Options: referral / evaluation / pretransplant treatment / listed / temporarily inactive / posttransplant / other.

- Treating center / service: ____________________

- Responsible clinician and role: ____________________

- Person recording / abstracting the information: ____________________

- Date entered: ____________________

- Local protocol name, version and approval status: ____________________

- Policy / guidance version used and date checked: ____________________ Record the version actually used for this assessment.

## HCC diagnosis and allocation detail

Section source / report: ____  Observation date: ____

- Imaging-diagnosis population / liver background and evidence: ____________________

- Class 5 adjudication for each relevant lesion ID: ____________________ Keep indeterminate observations separate; cite the criterion/version used.

- Qualifying pretreatment lesion count: ____________________

- Sum of qualifying pretreatment diameters (mm): ____________________

- Highest documented AFP (ng/mL): ____________________

- AFP ever above 1,000 ng/mL: ____________________ Options: yes / no / unknown. Retain the subsequent dated AFP trend in the laboratory records.

- Clinical selection and allocation categories assessed: ____________________ Record Milan clinical assessment, T2, standardized downstaging or nonstandard review separately.

- Prior rupture or vascular invasion: dates, vessel/level, treatment and stability: ____________________

- Peak AFP collection date: ____________________

## Exception request and allocation record

Section source / report: ____  Observation date: ____

- Request route: ____________________ Options: standardized / nonstandard nlrb / native meld / other / not determined.

- Request type: ____________________ Options: initial / extension / appeal / other.

- Submitted / planned submission date: ____________________

- Policy / guidance version, section and verification date: ____________________

- Criterion-by-criterion assessment and supporting record IDs: ____________________ Met / not met / uncertain / not applicable for each; explain discrepancies.

- Assigned exception / allocation score: ____________________

- Review disposition: ____________________ Options: not submitted / pending / approved / denied / withdrawn / appeal / other.

- Allocation disposition date: ____________________

- Renewal / expiry date: ____________________

- Allocation coordinator / clinician and verification date: ____________________

- Requested exception score: ____________________

- MMaT reference: ____________________

- Score / MMaT reference date: ____________________

- Official request ID: ____________________

## Clinical transplant evaluation and readiness

Section source / report: ____  Observation date: ____

- Comorbidities and transplant medical assessment: ____________________

- Cardiac / pulmonary evaluation, results, dates and outstanding actions: ____________________

- Active infection, treatment, microbiology and clearance assessment: ____________________

- Frailty, nutrition, mobility and rehabilitation plan: ____________________

- Psychosocial / support / adherence assessment status: ____________________ Reference the approved clinical record; avoid unnecessary sensitive narrative in research exports.

- Patient understanding, alternatives and consent discussion / date: ____________________

- Donor strategy: ____________________ Options: deceased donor / living donor / both / not determined.

- Outstanding issues, responsible clinician and completion date: ____________________

- Clinical transplant evaluation decision: ____________________ Options: approved / deferred / declined / in progress.

- Clinical evaluation decision date: ____________________

## Immune-checkpoint inhibitor exposure and transplant safety

Section source / report: ____  Observation date: ____

- Exposure status: ____________________ Options: never exposed / prior exposure / current / uncertain.

- Agent(s), combination and treatment episode IDs: ____________________

- Last ICI dose date: ____________________

- Immune-related toxicity, organ, grade and resolution: ____________________

- Steroid / other immunosuppression used for toxicity: ____________________

- Proposed transplant date and elapsed days from last ICI: ____________________ Record both dates and interval; no interval is asserted to guarantee safety.

- Transplant, oncology and pharmacy review / date: ____________________

- Risk discussion, immunosuppression / monitoring plan and unresolved issues: ____________________

## Program milestones and follow-up — repeat as events occur [repeat as needed]

Repeat instance ID: ____  Linked assessment ID: ____

Section source / report: ____  Observation date: ____

- Milestone / event: ____________________ Options: referral / evaluation / diagnosis / first treatment / protocol enrollment / clinical acceptance / listing / inactive / reactivated / exception request / exception decision / delisting / transplant / recurrence / graft failure / retransplant / death / last contact / other.

- Event date: ____________________

- Reason / cause and adjudication source: ____________________ Record evaluation declines, waitlist dropout and patients never transplanted as well as transplant recipients.

- Patient / listing / graft / disease status at event: ____________________

- Source document and reviewer: ____________________

## Clinical decision, actions and sign-off

Section source / report: ____  Observation date: ____

- Multidisciplinary review date: ____________________

- Clinical assessment: ____________________ Options: proceed with evaluation / proceed with treatment / pause for information / use alternative treatment / decline transplant / continue follow up / other.

- Clinical rationale, alternatives and benefit-risk discussion: ____________________

- Separate allocation conclusion / unresolved question: ____________________

- Discordant findings, uncertainty and how they will be resolved: ____________________

- Next actions, responsible clinician and due dates: ____________________

- Departure from protocol / pathway and rationale: ____________________

- Patient / referring-team communication and date: ____________________

- Next review date: ____________________

- Reviewer / typed signature: ____________________ One sign-off for this entire assessment; a typed name is not identity-authenticated by this site.

- MDT participants: ____________________

- Sign-off date: ____________________

- Assessment review status: ____________________ Options: draft / reviewed.

## Research and data-quality extension

Section source / report: ____  Observation date: ____

- Registry / study name and local approval reference: ____________________ Optional research fields; collection/use requires the applicable institutional process.

- Consent / waiver / permitted-use status and date: ____________________

- Analysis time-zero event and date: ____________________ Preserve referral, diagnosis, treatment, listing and transplant dates separately; specify which defines each endpoint.

- Outcome definition / protocol version used: ____________________ Specify survival, recurrence, progression, graft failure or dropout definition and time origin.

- Last date the endpoint was assessed and method: ____________________

- Censoring / lost-to-follow-up status, date and reason: ____________________ Do not equate missing follow-up with absence of an event.

- Data queries, discordance, resolution and adjudicator/date: ____________________

- Record version, correction reason and superseded record ID: ____________________ Retain the earlier value and its source in the governed system.


---

# HCC · Reassess to transplant — recording template

Template 2026-10-24.2 · Does the candidate still satisfy clinical and allocation requirements?

Complete applicable fields in the EHR / approved clinical system. Blank does not mean negative. These fields record findings; they do not add test requirements or determine eligibility.

Record a source and clinical date for each section; use one assessment-level sign-off. Status: recorded / pending / not done / not applicable / unknown / not documented.

## Information checklist

- [ ] Renewal and final review: Updated multiphase CT/MRI tumor stage, AFP and treatment details for extension. Chest CT is not mandated for every HCC extension; order clinically indicated metastatic reassessment.

  Documentation status: ____  Result / record reference: ____  Date: ____  Outstanding action / clinician / due date: ____

- [ ] Renewal and final review: Review liver reserve, infection, new treatment exposure and any unexplained biomarker or imaging change.

  Documentation status: ____  Result / record reference: ____  Date: ____  Outstanding action / clinician / due date: ____

## Assessment identification

Section source / report: ____  Observation date: ____

- Coded patient / registry ID: ____________________ Use a coded ID in research exports. Keep any identifying linkage in the approved clinical system.

- Unique assessment ID: ____________________ New ID for each encounter or reassessment; retain earlier records.

- Date of clinical assessment: ____________________ YYYY-MM-DD; document date precision if only month or year is known.

- Phase of care: ____________________ Options: referral / evaluation / pretransplant treatment / listed / temporarily inactive / posttransplant / other.

- Treating center / service: ____________________

- Responsible clinician and role: ____________________

- Person recording / abstracting the information: ____________________

- Date entered: ____________________

- Local protocol name, version and approval status: ____________________

- Policy / guidance version used and date checked: ____________________ Record the version actually used for this assessment.

## Imaging studies — one entry per examination [repeat as needed]

Repeat instance ID: ____  Linked assessment ID: ____

Section source / report: ____  Observation date: ____

- Stable imaging-study ID: ____________________

- Acquisition date: ____________________

- Imaging modality: ____________________ Options: CT / MRI / CEUS / PET CT / PET MRI / ultrasound / other.

- Anatomic coverage: ____________________ Liver, chest, abdomen, pelvis or other sites; record what was actually examined.

- Technical adequacy: ____________________ Options: adequate / limited / nondiagnostic.

- Comparison study IDs and dates: ____________________

- Expert radiology review, reviewer and date: ____________________

- Overall impression and uncertain findings: ____________________

- Contrast phases / imaging protocol: ____________________

## Liver lesion map — one entry per lesion at each imaging time point [repeat as needed]

Repeat instance ID: ____  Linked assessment ID: ____

Section source / report: ____  Observation date: ____

- Stable lesion ID: ____________________ Keep the same ID across scans, treatments and explant correlation; include disappeared sites.

- Linked imaging-study ID: ____________________

- Liver segment / distribution: ____________________ Options: I / II / III / IVa / IVb / V / VI / VII / VIII / multiple segments / other.

- Maximum total lesion diameter (mm): ____________________

- Maximum viable enhancing component, if applicable (mm): ____________________ Do not substitute treated-cavity size for viable-tumor size.

- Pretreatment maximum diameter (mm): ____________________

- Lesion diagnosis / suspicion: ____________________ Options: HCC / iCCA / mixed HCC iCCA / metastasis / benign / indeterminate / treated site / other.

- Imaging classification: ____________________ Options: LR 1 / LR 2 / LR 3 / LR 4 / LR 5 / LR M / LR TIV / LR NC / LR TR nonviable / LR TR viable / LR TR equivocal / LR TR nonevaluable / LR TR nonprogressing / not applicable / other. Use the classification and algorithm version in the radiology report.

- Relation to dominant tumor / nearby separate nodules: ____________________ Record distance, segment and distribution if available; a satellite label alone does not prove clonal origin.

- Linked treatment episode IDs: ____________________

- Linked tissue / explant specimen IDs: ____________________

- Diagnostic certainty: ____________________ Options: confirmed / suspected / indeterminate.

- Pretreatment measurement date: ____________________

- Classification / treatment-response algorithm version: ____________________

- Distance from dominant lesion, if relevant (mm): ____________________

## Laboratory results — one entry per analyte and date [repeat as needed]

Repeat instance ID: ____  Linked assessment ID: ____

Section source / report: ____  Observation date: ____

- Analyte / test: ____________________ Options: bilirubin / albumin / INR / creatinine / sodium / platelets / hemoglobin / WBC / ANC / AST / ALT / ALP / AFP / CEA / CA 19-9 / IgG4 / other.

- Reported numeric value: ____________________ Keep the original value; do not convert missing results to zero.

- Result qualifier: ____________________ Options: exact / less than / greater than / below detection / qualitative.

- Reported unit: ____________________ Options: mg/dL / g/dL / mmol/L / 10^9/L / ng/mL / U/mL / U/L / unitless / other.

- Qualitative result, if applicable: ____________________

- Specimen collection date: ____________________

- Laboratory reference range: ____________________

- Relevant context at collection: ____________________ Cholangitis, obstruction/drainage, anticoagulation, dialysis, recent treatment or other confounder.

## Response assessments — one entry per time point [repeat as needed]

Repeat instance ID: ____  Linked assessment ID: ____

Section source / report: ____  Observation date: ____

- Assessment date: ____________________

- Linked imaging-study IDs and biomarker dates: ____________________

- Comparator / baseline date and tumor measurements: ____________________

- Response assessment system: ____________________ Options: RECIST 1.1 / mRECIST / LI RADS treatment response / other.

- Reported response: ____________________ Options: complete response / partial response / stable disease / progressive disease / nonviable / viable / equivocal / nonevaluable / nonprogressing / other. Select the reported designation within the named response system; these systems are not interchangeable.

- New lesions: ____________________ Options: none detected / suspected / confirmed / indeterminate / not assessed. Specify sites, certainty and action in Notes.

- Extrahepatic status: ____________________ Options: not detected / suspected / confirmed / indeterminate / not assessed.

- Reviewer and unresolved discordance: ____________________

## Liver reserve, nutrition and function

Section source / report: ____  Observation date: ____

- Calculated MELD value: ____________________ Enter the reported calculation; this form does not calculate MELD or exception scores.

- Child-Pugh class: ____________________ Options: A / B / C / not assessed.

- Ascites: ____________________ Options: absent / controlled / poorly controlled / not assessed.

- Encephalopathy: ____________________ Options: absent / present controlled / present not controlled / not assessed.

- Portal-hypertension evidence: ____________________ Varices/bleeding, splenomegaly, platelets, collaterals and pressure measurement if available.

- Renal function and dialysis status / dates: ____________________

- ECOG performance status: ____________________ Options: 0 / 1 / 2 / 3 / 4 / not assessable.

- Frailty / physical-function tool, value and date: ____________________ Name the instrument; retain raw components where available.

- Nutrition assessment, weight trend and sarcopenia assessment: ____________________

- MELD version: ____________________ Options: MELD 3.0 / MELD Na / MELD / other.

- MELD calculation date: ____________________

- Child-Pugh score: ____________________

## Treatment episodes — repeat for each regimen, cycle group or procedure [repeat as needed]

Repeat instance ID: ____  Linked assessment ID: ____

Section source / report: ____  Observation date: ____

- Stable treatment episode ID: ____________________

- Treatment intent: ____________________ Options: bridge / downstaging / conversion / disease control / curative intent / adjuvant / symptom control / other.

- Treatment modality: ____________________ Options: systemic therapy / resection / thermal ablation / SBRT / external beam radiation / Y90 / TACE / HAI / histotripsy / PRRT / other.

- Drug(s), regimen and line of therapy: ____________________

- Start date: ____________________

- Last administered dose / procedure date: ____________________

- End / stop date: ____________________

- Planned and delivered doses, units and cycles: ____________________

- Dose delays, reductions, omissions and reasons: ____________________

- Planned response examination and date: ____________________

- Reason stopped or changed: ____________________

- Target lesion / site IDs: ____________________

- Cycles delivered: ____________________

## Exception request and allocation record

Section source / report: ____  Observation date: ____

- Request route: ____________________ Options: standardized / nonstandard nlrb / native meld / other / not determined.

- Request type: ____________________ Options: initial / extension / appeal / other.

- Submitted / planned submission date: ____________________

- Policy / guidance version, section and verification date: ____________________

- Criterion-by-criterion assessment and supporting record IDs: ____________________ Met / not met / uncertain / not applicable for each; explain discrepancies.

- Assigned exception / allocation score: ____________________

- Review disposition: ____________________ Options: not submitted / pending / approved / denied / withdrawn / appeal / other.

- Allocation disposition date: ____________________

- Renewal / expiry date: ____________________

- Allocation coordinator / clinician and verification date: ____________________

- Requested exception score: ____________________

- MMaT reference: ____________________

- Score / MMaT reference date: ____________________

- Official request ID: ____________________

## Program milestones and follow-up — repeat as events occur [repeat as needed]

Repeat instance ID: ____  Linked assessment ID: ____

Section source / report: ____  Observation date: ____

- Milestone / event: ____________________ Options: referral / evaluation / diagnosis / first treatment / protocol enrollment / clinical acceptance / listing / inactive / reactivated / exception request / exception decision / delisting / transplant / recurrence / graft failure / retransplant / death / last contact / other.

- Event date: ____________________

- Reason / cause and adjudication source: ____________________ Record evaluation declines, waitlist dropout and patients never transplanted as well as transplant recipients.

- Patient / listing / graft / disease status at event: ____________________

- Source document and reviewer: ____________________

## Clinical decision, actions and sign-off

Section source / report: ____  Observation date: ____

- Multidisciplinary review date: ____________________

- Clinical assessment: ____________________ Options: proceed with evaluation / proceed with treatment / pause for information / use alternative treatment / decline transplant / continue follow up / other.

- Clinical rationale, alternatives and benefit-risk discussion: ____________________

- Separate allocation conclusion / unresolved question: ____________________

- Discordant findings, uncertainty and how they will be resolved: ____________________

- Next actions, responsible clinician and due dates: ____________________

- Departure from protocol / pathway and rationale: ____________________

- Patient / referring-team communication and date: ____________________

- Next review date: ____________________

- Reviewer / typed signature: ____________________ One sign-off for this entire assessment; a typed name is not identity-authenticated by this site.

- MDT participants: ____________________

- Sign-off date: ____________________

- Assessment review status: ____________________ Options: draft / reviewed.

## Research and data-quality extension

Section source / report: ____  Observation date: ____

- Registry / study name and local approval reference: ____________________ Optional research fields; collection/use requires the applicable institutional process.

- Consent / waiver / permitted-use status and date: ____________________

- Analysis time-zero event and date: ____________________ Preserve referral, diagnosis, treatment, listing and transplant dates separately; specify which defines each endpoint.

- Outcome definition / protocol version used: ____________________ Specify survival, recurrence, progression, graft failure or dropout definition and time origin.

- Last date the endpoint was assessed and method: ____________________

- Censoring / lost-to-follow-up status, date and reason: ____________________ Do not equate missing follow-up with absence of an event.

- Data queries, discordance, resolution and adjudicator/date: ____________________

- Record version, correction reason and superseded record ID: ____________________ Retain the earlier value and its source in the governed system.


---

# HCC · Post-transplant follow-up — recording template

Template 2026-10-24.2 · What must be recorded and monitored after transplant?

Complete applicable fields in the EHR / approved clinical system. Blank does not mean negative. These fields record findings; they do not add test requirements or determine eligibility.

Record a source and clinical date for each section; use one assessment-level sign-off. Status: recorded / pending / not done / not applicable / unknown / not documented.

## Information checklist

- [ ] Required record: Submit the HCC explant pathology form within 60 days for recipients transplanted with HCC exception priority.

  Documentation status: ____  Result / record reference: ____  Date: ____  Outstanding action / clinician / due date: ____

- [ ] Follow-up plan: Document explant burden, viable tumor, vascular invasion and recurrence-risk assessment. Use cross-sectional abdominal and chest surveillance; choose interval with the transplant team.

  Documentation status: ____  Result / record reference: ____  Date: ____  Outstanding action / clinician / due date: ____

## Assessment identification

Section source / report: ____  Observation date: ____

- Coded patient / registry ID: ____________________ Use a coded ID in research exports. Keep any identifying linkage in the approved clinical system.

- Unique assessment ID: ____________________ New ID for each encounter or reassessment; retain earlier records.

- Date of clinical assessment: ____________________ YYYY-MM-DD; document date precision if only month or year is known.

- Phase of care: ____________________ Options: referral / evaluation / pretransplant treatment / listed / temporarily inactive / posttransplant / other.

- Treating center / service: ____________________

- Responsible clinician and role: ____________________

- Person recording / abstracting the information: ____________________

- Date entered: ____________________

- Local protocol name, version and approval status: ____________________

- Policy / guidance version used and date checked: ____________________ Record the version actually used for this assessment.

## Transplant operation and explant

Section source / report: ____  Observation date: ____

- Transplant date: ____________________

- Donor type: ____________________ Options: living / deceased DBD / deceased DCD / other / unknown.

- Operation, reconstruction and perioperative events: ____________________

- Explant pathology report ID / review date: ____________________

- Explant tumor count: ____________________

- Histology, grade and pretransplant–explant concordance: ____________________

- Microvascular, macrovascular, perineural and biliary invasion: ____________________

- Nodes examined / positive, stations and margins: ____________________

- Pathologic TNM / staging edition: ____________________

- Required pathology / registry submission and completion date: ____________________

- Graft type: ____________________ Options: whole / split / partial / other.

- Preservation method: ____________________ Options: static cold storage / machine perfusion / other / unknown.

- Lesion-level size, site, viability and treatment effect: ____________________

## Post-transplant / program outcomes — repeat at each follow-up [repeat as needed]

Repeat instance ID: ____  Linked assessment ID: ____

Section source / report: ____  Observation date: ____

- Follow-up / last-contact date: ____________________

- Vital status: ____________________ Options: alive / dead / unknown.

- Death date, cause and source if applicable: ____________________

- Graft function, graft failure / retransplant date and cause: ____________________

- Actual regimen, doses and relevant trough levels / dates: ____________________

- Rejection diagnosis, biopsy / grade, date, treatment and resolution: ____________________

- Infection, biliary, vascular, renal and other major complications: ____________________

- Surveillance completed: study IDs, dates and results: ____________________

- Recurrence date, site, confirmation method and treatment: ____________________

- Performance, symptoms, quality-of-life tool / score and rehabilitation needs: ____________________

- Next surveillance plan, date and responsible team: ____________________

## Program milestones and follow-up — repeat as events occur [repeat as needed]

Repeat instance ID: ____  Linked assessment ID: ____

Section source / report: ____  Observation date: ____

- Milestone / event: ____________________ Options: referral / evaluation / diagnosis / first treatment / protocol enrollment / clinical acceptance / listing / inactive / reactivated / exception request / exception decision / delisting / transplant / recurrence / graft failure / retransplant / death / last contact / other.

- Event date: ____________________

- Reason / cause and adjudication source: ____________________ Record evaluation declines, waitlist dropout and patients never transplanted as well as transplant recipients.

- Patient / listing / graft / disease status at event: ____________________

- Source document and reviewer: ____________________

## Clinical decision, actions and sign-off

Section source / report: ____  Observation date: ____

- Multidisciplinary review date: ____________________

- Clinical assessment: ____________________ Options: proceed with evaluation / proceed with treatment / pause for information / use alternative treatment / decline transplant / continue follow up / other.

- Clinical rationale, alternatives and benefit-risk discussion: ____________________

- Separate allocation conclusion / unresolved question: ____________________

- Discordant findings, uncertainty and how they will be resolved: ____________________

- Next actions, responsible clinician and due dates: ____________________

- Departure from protocol / pathway and rationale: ____________________

- Patient / referring-team communication and date: ____________________

- Next review date: ____________________

- Reviewer / typed signature: ____________________ One sign-off for this entire assessment; a typed name is not identity-authenticated by this site.

- MDT participants: ____________________

- Sign-off date: ____________________

- Assessment review status: ____________________ Options: draft / reviewed.

## Research and data-quality extension

Section source / report: ____  Observation date: ____

- Registry / study name and local approval reference: ____________________ Optional research fields; collection/use requires the applicable institutional process.

- Consent / waiver / permitted-use status and date: ____________________

- Analysis time-zero event and date: ____________________ Preserve referral, diagnosis, treatment, listing and transplant dates separately; specify which defines each endpoint.

- Outcome definition / protocol version used: ____________________ Specify survival, recurrence, progression, graft failure or dropout definition and time origin.

- Last date the endpoint was assessed and method: ____________________

- Censoring / lost-to-follow-up status, date and reason: ____________________ Do not equate missing follow-up with absence of an event.

- Data queries, discordance, resolution and adjudicator/date: ____________________

- Record version, correction reason and superseded record ID: ____________________ Retain the earlier value and its source in the governed system.
