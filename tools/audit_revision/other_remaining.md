# Assigned-roadmap implementation and remaining items

Analyst A (Codex), internal implementation task, 2 November 2026. This is not an additional external Analyst B review. Clinical files are stable for integration.

## Completed scope

Applied 267 recorded field changes across 22 owned files: HCA, incidental liver lesions, PDAC, pNET, pancreatic cysts and ampullary roadmap data, selected critique data, matching consensus sources and public question JSON. Exact old/new values, finding IDs and source locators are in `other_change_register.json`. The 166 unique replacement chunks in `../clinical_revisions/2026-11-02-other-roadmaps.json` replay these files exactly from baseline `30039fe`.

The corrections include cyst-fluid amylase direction and VHL specificity; Kyoto high-risk assessment and young/fit context; conditional PDAC drainage and MRI staging; PRODIGE denominators and age uncertainty; current daraxonrasib/TMB label boundaries; NAPOLI-1 and final RTOG 0848; pNET grading, functioning syndromes, location/hereditary context, NEC/NET G3 distinctions, ERASING, surveillance and NETPET; ampullary ABC-02/ABC-06 population limits and later-line/supportive care, ESGE biopsy/size/surveillance context; HCA beta-catenin risk and selected-cohort denominators; ACR incidental-lesion context and LR-M interpretation. Removed PDAC-B1/B2 and their orphan historical cluster-transplant source from owned public question data.

## Integration dependencies

`other_shared_proposals.json` contains 17 requests for shared source summaries, compact evidence and routing. Shared files, matrices, transplant content, static document downloads, slide decks, publication and deployment belong to the parent integration task. This implementation did not rebuild or verify those outputs. Rebuilding question JSON must retain the corrected consensus text and PDAC removals. The final primary RTOG report is PMID 42456089; its source-summary proposal is the last entry.

## Explicitly deferred or not adopted

- These are supported clinical corrections, not clearance of every critique sentence, funding/COI statement, bibliographic detail or source-availability claim. The six page-level provenance statements now describe bounded verification. Historical audit documents remain preserved unchanged.
- B's partly-supported flags were not treated as instructions to replace whole statements. Accurate numeric components and qualifications were retained where the underlying record supported them. Source absence was not treated as proof that an assertion was false.
- The apparent PRODIGE age-subgroup disagreement was resolved by retaining the reported estimate and its uncertainty; a nonsignificant subgroup does not establish lack of benefit. The earlier objection that the DFS estimate was absent was not accepted as a reason to delete it when the original figure supplied it.
- HCA observation was individualized as approximately 6–12 months with earlier treatment for higher-risk disease. No universal mandatory 12-month delay was introduced. An imaging subtype and a confirmed molecular high-risk alteration remain different findings.
- The VHL pNET three-factor approach was preserved. No universal biological 2-cm pancreatic-head trigger was introduced.
- The newer AGA ampullary guidance was not used to replace ESGE thresholds on abstract-only access. The retrieved ESGE and original guideline sections support the implemented corrections.
- Pancreatic-cyst guideline growth cutoffs, additional PancreaSeq cost/bias descriptions and lower-priority critique/editorial statements require source-specific follow-up where not represented in the change register. European absolute-indication terminology was retained in its own guideline context; Kyoto wording was not indiscriminately applied to it.
- Unread supplements, inaccessible primary texts and unreviewed document/deck statements retain their prior source-review limitations. PAXG and other residual PDAC source-status/critique details were not expanded into a new exhaustive audit in this implementation.
- Passing software tests verifies replay and structure, not clinical validity of every remaining statement. No clinical institutional proposal was activated by this task, and no publication was performed.

## Evidence trail

The implementation used the preserved Analyst B handoff, B17–B22 summaries and relevant reader reports, A's continuation/reconciliation, and the pancreatic/ampullary and metastatic/benign priority/source reviews. The RTOG follow-up uses A's `batches/B26_residual_sources/42456089.md` and original PMC author-manuscript text. The NETPET follow-up uses B20 R7's `36434154.md` with its explicit overlap and PRRT qualifications. Source locators are recorded per change, rather than implying that all papers were newly read in this task.
