# Focused ESPAC-3 / eNRGy correction closure

Analyst A (Codex), internal implementation. Baseline `b3ef22b`.

Implemented C0063–C0065 (PMID22782416) and C0234/C0237/C0241 (PMID39908431) in five assigned files, with 14 field changes and ten exact protected replacement chunks. The PDAC consensus source contained no matching eNRGy claim and was left unchanged. No generated question data, shared assets, Word documents, PPTs or publication targets were edited.

`c_other_source_closure.json` records each old/new field and primary locator. `c_other_shared_proposals.json` records shared compact/source-summary/generated-question propagation. `c_other_document_ppt_replacement_map.json` provides four compact factual replacement groups for cross-format synchronization, with short/long wording and caveats.

Read extent: the established A adjudications and targeted original text (ESPAC-3 Table1; eNRGy Methods, Results, Tables1–2). The pancreatic PFS value is explicitly present in eNRGy main Results; its cited supplement was not newly read. This is not a new broad audit or external Analyst C review.

Remaining consequential statements observed but not expanded into this task: the ampullary ESPAC-3 note and critique still infer that shorter bile-duct subgroup medians prove where the pooled benefit is carried; that inference is stronger than a formal interaction result. Several surrounding NCCN/source-availability statements retain historical extraction-only wording despite later original-source checks. Those issues require separately scoped adjudication/propagation; this correction does not clear them. Other sources discussed in adjacent multi-drug critiques were not re-reviewed.

The negative unadjusted ESPAC-3 primary result, hypothesis-generating adjusted analysis, and limited ampullary-specific inference are preserved. eNRGy remains single-arm evidence; PFS reporting is not a comparative survival-benefit claim.

Validation: exact replay from `b3ef22b` and targeted clinical assertions pass. `test_content_hierarchy.cjs`, `test_roadmap_flow.cjs` (103 topics/305 conditional links) and `test_uniform_evidence.cjs` all pass.
