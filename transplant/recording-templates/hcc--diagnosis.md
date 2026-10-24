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
