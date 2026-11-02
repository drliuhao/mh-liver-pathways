# Liver roadmap implementation handoff — Analyst A — 2026-11-02

This is an implementation reconciliation of existing source-verified reviews, not a new full-paper audit and not an endorsement of every B priority flag. Analyst A is Codex; the external Analyst B reports and A/C reconciliation were preserved unchanged. Work is confined to the six assigned roadmaps, their consensus sources and public question copies, plus this implementation register. Shared assets, source decks, transplant calculators, matrices and deployment are handled by the parent task.

## Completed

The final liver manifest contains **275 exact replacement patches across 22 files**, replayed successfully from baseline `30039fe`. Patches are implementation units, not a count of unique findings. Each has the old/new text and a finding/source locator in `liver_change_register.json`; the same patches are in `../clinical_revisions/2026-11-02-liver-roadmap-audit.json` for protected-content guards.

- HCC: separate BCLC stage from CSPH treatment selection; correct no-APHE LI-RADS sizing; remove the PSVD stiffness item from cirrhotic CSPH criteria; add the device-specific MWA local-control trial; retain TACE/systemic combinations as trial-only; distinguish OPTN AFP >1000 from AASLD ≥1000 and EASL's <1000 observation condition; correct the broad AASLD systemic-adjuvant statement; replace fixed two-session TACE stopping with per-session assessment; qualify nonviral IMbrave inference, published XXL estimate, selected CSPH resection safety and bridging comparisons; separate post-LT ICI evidence from pre-LT washout.
- pCCA: regional nodes do not automatically prohibit resection; preserve strict standardized LT size and nodal restrictions; imaging precedes elective drainage; accurately attribute adjuvant guidance despite imprecise pCCA subgroup results; keep the neoadjuvant-first regional-node strategy an explicitly OPEN divergence.
- iCCA: NLRB directly specifies six months for the solitary ≤3 cm cirrhotic route, separate from early referral; preserve existing satellite/multifocal distinction; add the later Houston cohort with OS measured from listing; distinguish randomized second-line evidence; add FIGHT-302 as a qualified published update with the new option reference; apply the October 2026 ClarIDHy correction and remove categorical no-conversion inference.
- CRLM: separate initial/extension exception wording and clinical referral; distinguish primary regional nodes from extrahepatic metastases; preserve exact CEA/progression operators; qualify the Hill mixed-diagnosis technical series (3 CRLM, not 7); distinguish DEBIRI and EPOCH OS results; remove exclusive CAIRO5 clearance wording; reconcile the OPEN combined peritoneal/liver proposal with avoidance of routine oxaliplatin HIPEC.
- NET: allow adequate Ki-67 grading when biopsy mitoses are unobtainable; use receptor imaging selectively at follow-up; distinguish later randomized PRRT populations; correct SSA withholding and telotristat clinical dose; correct PROMID/CLARINET subgroup denominators and estimates; distinguish response goals from unproven comparative response/OS benefits; correct Ki-67 55% diagnostic inference, NEC randomized-evidence/grade assertions, E2211 arm labels and G3 extrapolation; distinguish RETNET protocol from conference results and soften unsupported universal biliary-injury/causal-death claims while retaining NCCN-supported DEB avoidance.
- cHCC-CCA: correct NLRB size/grade attribution, dominant-component reclassification kappa interpretation, mixed-histology inclusion in KEYNOTE-966 and the scope of the Auer source; preserve OPEN local restrictions as local proposals.

## Remaining and no-change decisions

1. No claim that all 1,048 priority CSV rows in B11–B16 have been independently adjudicated or fixed. Many flags concern wording, source reading depth, author/disclosure counts, article-version access, source-report rhetoric or unsupported methodological inference. Only changes traceable to the reviewed source locators were accepted. Original reviewer conclusions remain in their reports.
2. The corrected AASLD Figure 10 is not an image in the owned roadmap files. Source-deck/PDF exhibits and downloadable historical evidence packages require a separate versioned update. No historical document was regenerated here.
3. Public question copies were synchronized for the acted-on roadmap statements. Their distinct high-risk material is owned by the transplant integration lane. Source documents, decks, report previews and final share-site generation are outside this lane.
4. FIGHT-302's source package remains partially audited; its result updates the evidence description without establishing a new first-line policy. ClarIDHy's corrected bootstrap interval, not an ad hoc narrower interval, governs the adjusted-OS statement. Wong2021 is explicitly abstract-verified. The final XXL full report remains an access gap; the published abstract supports its corrected estimate.
5. McMillan2022's later Houston OS estimates are from listing, including an eventual-recipient subset. This primary-source A locator controls over a B summary that called them post-LT. Earlier Houston cases overlap and are not independent validation cohorts.
6. NLRB guidance remains nonbinding allocation guidance and is distinct from clinical candidacy, referral and approved local policy. Existing OPEN stricter local proposals were not silently approved or deleted. Existing iCCA satellite/multifocal distinctions were retained.
7. No current-trial-recruitment re-audit was undertaken for all registry-only cHCC-CCA studies. Registry claims and source gaps remain dated; the implementation does not certify current recruiting status.
8. Detailed methodological claims remaining in historical source critiques (including broader pCCA surgical/drainage critiques, trial-specific funding/author counts, uncommon subgroup inferences and claims dependent on inaccessible supplements) are not fully cleared by this pass. The corrected key clinical statements must not be read as whole-source clearance.
9. Shared propagation requests are in `liver_shared_proposals.json`. The parent must refresh literal compact-evidence quotes, regenerate decision-workspace data, retain option-level Reasonable/Trial status and integrate the compact ClarIDHy, MWA, FIGHT-302, CLARINET, kappa and RETNET corrections. Generated UI copies may remain stale until that build completes.
10. No deployment, commit or push was performed by this lane. Parent owns final full/share validation and publication.

## Verification

- Exact baseline replay: PASS, 275 patches / 22 files.
- `test_content_hierarchy.cjs`: PASS (49 references assigned; recommendations precede evidence and secondary navigation).
- `test_roadmap_flow.cjs`: PASS (103 topics / 12 roadmaps; 294 conditional links).
- Earlier `test_clinical_flow.cjs` was blocked by the separately owned transplant mirror prefix issue; no liver-file failure was reported by that run. Parent owns the final integrated rerun.
- Targeted desktop/mobile Tools browser result is recorded in `liver_validation.md` after completion.

## Changed protected files

- `chcca/data/critique.json`
- `chcca/data/pathway.json`
- `crlm/data/pathway.json`
- `documents/chcca/questions.json`
- `documents/crlm/questions.json`
- `documents/hcc/questions.json`
- `documents/icca/questions.json`
- `documents/nelm/questions.json`
- `documents/pcca/questions.json`
- `hcc/data/critique.json`
- `hcc/index.html`
- `hilar/data/pathway.json`
- `icca/data/critique.json`
- `icca/data/pathway.json`
- `nelm/data/critique.json`
- `nelm/data/pathway.json`
- `tools/consensus_source/roadmap_chcca.json`
- `tools/consensus_source/roadmap_crlm.json`
- `tools/consensus_source/roadmap_hcc.json`
- `tools/consensus_source/roadmap_hilar.json`
- `tools/consensus_source/roadmap_icca.json`
- `tools/consensus_source/roadmap_nelm.json`
