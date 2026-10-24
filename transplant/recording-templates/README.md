# Transplant oncology recording templates

Version: 2026-10-24.1. These are blank documentation tools for the existing review pathways,
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
