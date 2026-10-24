# Electronic transplant oncology assessments

Version: 2026-10-24.2. Complete dropdowns, numeric inputs with units, date controls, and
narrative fields directly in the browser. These documentation fields do not determine
eligibility or add test requirements.

## Working with an assessment
- Open a decision-specific form. No normal/negative clinical values are preselected.
- Expand relevant sections. Use Add another entry for each lesion, study, specimen,
  treatment episode, adverse event or follow-up record; retain stable clinical IDs.
- Use Notes / missing value to record uncertainty, pending / not-done / not-applicable
  findings or an explanation of Other. Blank is not negative, normal or zero.
- Record source/date once per section; optional field-level source/date overrides are
  available. There is one optional reviewer / typed signature and date for the assessment.
- Review status returns to Draft if clinical information is edited after review. Typed
  sign-off is not identity-authenticated or integrated with the EHR.
- Save / download JSON creates a local file containing the entered values. Reopen saved
  JSON restores the same decision and template version, including repeated entries.
- Copy completed note / Download note produces a readable note of entered values and
  explicitly marked missing data. Export CSV creates a structured long-format data file.
  Print / PDF prints the completed note rather than blank writing lines.

## Local data handling
Entries stay in the current tab. There is no server submission, database, analytics,
automatic browser storage or background save. Refreshing/closing loses unsaved entries.
The page blocks connection requests and form submissions through its content policy.
Save completed files only in an institution-approved location and use the approved EHR
for the clinical record. The public GitHub repository must contain only blank templates
and test data that is explicitly synthetic. This site is not an institutional EHR or
an authenticated signature system.

## Research structure
The dictionary is a local draft, not a validated registry or direct REDCap import.
Stable field IDs, units, response choices, date precision and repeated instances support
mapping to an approved registry. Validate that mapping and endpoint definitions before
prospective collection. The electronic version separates previously combined narrative
items into typed fields; earlier blank dictionaries must not be treated as equivalent.

JSON format: mh-transplant-assessment, format_version 1, template_version 2026-10-24.2.
A saved file must match the form's disease, decision and template version. Unknown fields,
invalid choices, invalid numeric types and malformed dates are rejected without replacing
the current assessment. An integer count can be zero; missing data is not converted to zero.
Dates support exact day, month-only or year-only precision; no date is imputed.
The form permits clinical incompleteness. Numeric bounds enforce basic units (nonnegative
counts/lengths and 0–100 percentages); no clinical eligibility score is calculated.

Each JSON module contains one or more instances, with source/observed_date and a values
object keyed by field ID. Every value has value, missing, notes, source, observed_date and
precision. Blank value is null. Missing uses pending / not_done / not_applicable / unknown /
not_documented; an absent value with no explicit status is exported as not_documented.
The single sign-off is stored under decision.signoff, decision.signoff_date and
 decision.review_status. Field-level reviewer signatures are not collected.

The live CSV export includes record/assessment IDs, pathway and decision, module and
instance IDs, field ID and label, typed value, unit, missing status, date precision,
observation date, source, notes, and the assessment-level sign-off. Checklist data use
module information_checklist and field IDs checklist.<item>.<property>. Values starting
with spreadsheet formula characters are escaped in the CSV. JSON preserves literal text.
The blank values/*.csv files retain the original research-mapping scaffold; the live
export includes the typed electronic fields and expanded note/sign-off columns.

## Longitudinal outcomes
Include evaluated patients who are declined, never listed or never transplanted, with
reasons. Preserve diagnosis, treatment, listing and transplant dates separately. Define
time zero and endpoint ascertainment for each analysis. Record last contact, censoring,
dropout, recurrence, death and graft outcomes; missing follow-up is not absence of an event.

## Kit contents
- clinical_templates.md: blank fallback notes for every decision in this pathway.
- dictionary.csv / schema.json: field IDs, types, units, choices, numeric bounds and definitions.
- decision_modules.csv: fields grouped by decision.
- blank_values/*.csv: blank long-format research-mapping scaffold.
- source_checklist.csv: original required-information items and source IDs.
- sources.json: source titles, authority, locators and official access links.

## Basis
Clinical information checklists come from the existing source-linked pathways. Additional
documentation and research fields are local design proposals. Clinical criteria are unchanged.
Sources checked 2026-10-24:
- https://www.hrsa.gov/sites/default/files/hrsa/optn/optn_policies.pdf
- https://www.hrsa.gov/sites/default/files/hrsa/optn/adult-meld-exception-transplant-oncology-review-guidance.pdf
- https://cde.nlm.nih.gov/home (data-definition approach; no endorsement implied)
