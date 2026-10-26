# Decision previews and clinical tools — 26 October 2026

The shared loader adds `clinical-reference.js`, `clinical-tools.js` and `clinical-tools.css` to the cancer roadmaps and transplant pathways.

- All 46 transplant decisions can be previewed from the top toolbar, the sticky Preview button, the existing All decisions control, or the pathway overview. A preview is read-only: it neither applies a finding nor changes the current assessment, URL, or decision trail. Its numbered buttons select reference content only.
- Preview content comes from the same embedded pathway, assistant questions, criteria, options, rules, checklists and source records as the working assessment. Conditional supplemental findings are included under “when applicable.” High-risk references retain orange presentation and link to their existing review.
- Full checklist and sources opens by default once for each newly rendered assessment. A reader can close it. Preview checklists, criteria and source details are expanded.
- LR-5, ECOG, Child-Pugh and MELD use the existing hover/tap/hold/keyboard explanation component. A top reference row is always available; relevant terms also appear beside the current finding or checklist. Original clinical text, source guards and matching logic are retained.
- The MELD calculator is separate from pathway choices. No result is copied into a decision, URL, storage, or network request. Input changes invalidate the displayed result. Closing or clearing removes entered values.

## Calculation and sources

MELD 3.0 uses OPTN policy 9.1.D, effective 1 October 2026, PDF page 183, checked 26 October 2026: https://www.hrsa.gov/sites/default/files/hrsa/optn/optn_policies.pdf#page=183

The formula uses natural logarithms, sex for purposes of adult MELD, and age **at registration**. People registered before 18 who are currently at least 12 receive the 7.33-intercept formula without the adult sex term. Children currently under 12 are directed to PELD. Creatinine is bounded to 1–3 mg/dL, bilirubin and INR floored to 1, sodium bounded to 125–137 mmol/L, and albumin bounded to 1.5–3.5 g/dL. Qualifying dialysis sets creatinine to 3. Results are rounded and bounded to 6–40. Adjusted inputs are disclosed. This computes laboratory MELD, not cancer exceptions or final allocation priority.

- Official OPTN calculator: https://www.hrsa.gov/optn/data-calculators/allocation-calculators/meld-calculator
- ACR CT/MRI LI-RADS: https://www.acr.org/-/media/ACR/Files/RADS/LI-RADS/LI-RADS-2018-Core.pdf
- ACR population/application: https://radssupport.acr.org/support/solutions/articles/11000079463-application
- ECOG-ACRIN scale: https://ecog-acrin.org/resources/ecog-performance-status/ (Oken et al., Am J Clin Oncol 1982; PMID 7165009)
- UW Child-Pugh table/calculator: https://www.hepatitisc.uw.edu/page/clinical-calculators/ctp
- NHS Child-Pugh interpretation: https://sps.nhs.uk/articles/calculating-and-using-the-child-pugh-score/

## Validation

`test_clinical_tools.cjs` checks required/invalid inputs, age groups, sex, dialysis, limits, and 320 combinations; all 46 previews and 116 source placements. Existing clinical, contextual-routing, roadmap, evidence and release tests are retained.

The official OPTN web calculator was operated with synthetic test inputs: bilirubin 2.5 mg/dL, INR 1.5, creatinine 1.2 mg/dL, sodium 132 mmol/L, albumin 2.8 g/dL. Results matched: adult male 20; adult female 21; adult female with qualifying dialysis 30; registration before 18/current age 16 without dialysis 21.

Browser QA covered all 46 previews; all 19 clinical pages at normal and 390-pixel widths; preservation of current findings/result/hash during a future preview; mobile reference-to-calculator access; stale-result clearing; under-12 routing; close/reset behavior; and no page/strip overflow. Local audit artifacts are retained outside the public repository.
