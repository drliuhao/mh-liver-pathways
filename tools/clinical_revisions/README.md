# Recorded clinical revisions

Each JSON file here is one approved change to protected clinical content: new sources and reviews, exact replacements in existing reviews or assistant option labels, and the matching edits to `transplant/assets/risk-routing.js` and `high-risk.js`.

- `node tools/apply_clinical_revisions.cjs --write <id>` applies a revision once. It updates `content.json`, the V12 snapshot, every embedded `protocol-data` payload and the listed scripts.
- The guards (`test_contextual_info.cjs`, `test_content_hierarchy.cjs`, `test_matrix_integration.py`) apply every recorded revision to their pinned originals before comparing. Any clinical change not recorded here still fails.

| File | Summary |
|---|---|
| `2026-10-29-extrahepatic-disease.json` | A dedicated position on previously treated extrahepatic disease per tumor. New reviews: CRLM-B5, HCC-B5, iCCA-B4, NET-B4. Expanded: pCCA-B1, HEHE-B2. CRLM-B3, NET-B2, HCC-B1/B2 and iCCA-B1 now point to these. 27 sources (11 added after full-text reading); numbers re-checked against the sources by an independent check. Proposed; not activated. |
| `2026-10-29-standardized-documents.json` | Standardized documents: high-risk views no longer list their own Word downloads (the Documents corner offers each tumor's files once), and the roadmap extrahepatic-disease links open the question in the roadmap's own Questions for consensus section. Presentation and linking only. |
