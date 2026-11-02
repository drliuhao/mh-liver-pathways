# Reconciled website release — 1 November 2026

This release implements supported clinical findings from Analyst B's completed review package and the preserved Analyst A/C reconciliations. It is not a claim that every review flag or every source appendix has been independently resolved. Reviewer originals were preserved. No external reviewer was restarted.

## Scope

- Twelve cancer roadmaps, seven transplant pathways, 103 roadmap decisions and 46 transplant decisions.
- Liver-directed and systemic treatment matrices, conditional links, concise study summaries, tools and web discussion questions.
- Two website editions: the full site and a separately built sharing site. Both retain the same clinical decisions and literature citations. The sharing build excludes downloadable local documents/decks, direct links back to the full site, internal depot/slide metadata and all tooling.
- Historical Word, PDF and PowerPoint files retain their separately dated source versions. The full site's document menu labels them as source editions. They have not been regenerated or certified as corrected by this web release.

## Main corrections

Corrected patient populations, outcome denominators and time origins, trial-versus-label distinctions, source attribution, imaging and selection thresholds, allocation versus clinical eligibility, and conditional routing. Specific examples include the corrected ClarIDHy adjusted-survival interval, the later Houston iCCA cohort's survival measured from listing, device-specific ablation evidence, NET trial interpretation, source-specific cyst biomarker accuracy, and the final RTOG 0848 report. The source-linked manifests and three implementation registers record exact replacements.

The HCC AFP decisions retain observation, additional liver-directed or systemic treatment, resection where feasible, individual high-risk review and supportive-care routes with their respective prerequisites. Prior proven disease and post-transplant contexts are handled separately. Local proposals remain unactivated; this release does not approve them.

## Verification

- All 35 non-browser suites pass, including exact recorded clinical-revision replay, clinical routing, source provenance, score calculations, internal links and share-site privacy checks.
- Compact treatment browser sweep: 103 topics, 286 mapped treatment options, 10 HCC treatment-reference connections; no phone overflow or page errors.
- Tools browser sweep: all 103 topics and 12 calculator interactions pass.
- Full and sharing transplant browser checks: 46 decisions, 169 canonical outcomes, six AFP alternatives, seven phone pages; no page errors.
- Sharing parity: 46 assistant definitions, 187 rules and all 80 explicit null branches preserved. A discovered sanitizer defect that removed null branches was corrected and regression-tested before publication.
- Sharing exclusion: all 119 document binaries omitted; publication citations and 34 evidence libraries retained. No local document download targets remain in the checked output.

## Limits and unresolved items

See `liver_remaining.md`, `other_remaining.md`, `transplant_remaining.md` and the frozen original review reports for unavailable full texts, source-specific appraisal depth, methodological disagreements and work limited to historical documents/slides. The implementation registers count exact edits, not distinct scientific findings. Site-wide prose that described inventory or source access as comprehensive appraisal was qualified where revised. No patient-level waiting data were uploaded or recalculated.

Release base: `30039fe0cec15a29ac2f326e0ee316eaf6bfb48e`. Client asset key: `20261102-review1`.
