# Analyst A source-specific closure — cHCC-CCA and pCCA

Implemented 48 exact text changes in chcca/hilar pathway and critique JSON plus their two consensus-source JSON files. Manifest: `tools/clinical_revisions/2026-11-02-zzzzzzz-c-liver.json`. Exact field register: `c_liver_change_register.json`.

Confirmed source groups: Lee PMID 30552477 targetoid HCC-control positivity 23/66 (34.8%) and specificity 65.2%; Auer PMID 37174120 interventional iCCA review with mixed-tumour outlook rather than a systemic-regimen recommendation; Renzulli PMID 34283065 dedicated small retrospective mixed-tumour LRT evidence and enhancement-pattern analysis without pooled/comparative efficacy; Milan PMID 40478744 PVE initial (rec23, strong/level3), upfront or additional LVD for substantial augmentation (rec24, strong/level3) and ALPPS not initial (weak/level5); CEUS PMID 33362387 combined CEUS/AFP/CA19-9 rule and modelled PPV; NLRB solitary ≤3cm/cirrhosis/stability pathway distinguished from stricter local open decisions; Milan transplant recommendations59 and64 separated by phenotype and recommendation strength and from OPTN strict <3cm.

Preserved local approval status and clinical grades. No protocol activated. Did not insert unverified modality-specific outcomes from review tables with inconsistent denominators/time origins; Chan erratum and complete primary papers remain necessary before using those numbers. Did not convert source recommendation strength into randomized comparative proof or mixed-histology efficacy.

Shared exact study-field replacements and option remaps are in `c_liver_shared_proposals.json` for root. Document/PPT group-level factual mapping is in `c_liver_document_ppt_replacements.json`; the final current-artifact paragraph proposals are in `tools/artifact_sync/liver/`.

Verification: exact b3ef22b+manifest replay passes for all six owned files; content-hierarchy test passes (49 references); roadmap-flow test passes (103 topics,305 links); old targeted source-error phrases were checked in owned fields. Browser preview showed a stale workspace criterion-key mount failure; root identified stale generated decision-workspace data and owns regeneration/final UI verification. No runtime patch, deployment, commit or binary authoring performed.

Two remaining non-viral HCC source-appraisal sentences were encountered while preparing accepted factual propagation. They are outside current source ownership and are supplied in `c_liver_remaining_website_proposals.json`; they are not left unreported or silently treated as consistent.
