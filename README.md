# Liver tumour pathways — working consoles

Twelve Memorial Hermann HPB oncology roadmaps and seven transplant protocols,
with shared liver-directed and systemic therapy matrices. The roadmaps cover
HCC, CRLM, iCCA, pCCA, NELM, combined HCC-CCA, hepatic adenoma, incidental liver
lesions, PDAC, pancreatic NET, pancreatic cysts, and ampullary tumors.

**Under development.** These are drafts under active revision, prepared for
multidisciplinary and institutional governance review. They are not ratified
clinical policy, they have not been approved by the specialties named in them,
and they must not be used for patient care decisions. Every criterion drawn
from OPTN policy, drug labelling, NCCN or device authorisation must be
re-verified against the current source before any use.

## Layout

```
index.html          landing page
hcc/ crlm/ icca/ hilar/ nelm/ chcca/ adenoma/ incidental/ pdac/ pnet/ pcyst/ ampullary/
    index.html      the page
    data/           pathway.json, and the shared liver-directed matrix
```

Each roadmap has an HTML page. Eleven fetch clinical content from
`data/pathway.json`; `hcc/index.html` carries its clinical content inline.
All twelve use `assets/roadmap-flow.js` and `.css` for the topic selector,
criteria display, and conditional navigation in `assets/roadmap-links.json`.
Topic selection opens content; it does not compute patient eligibility.
Deep links use `#decision-ID`. Preserve the original topic IDs and clinical data.
After regenerating legacy HTML, run `python3 tools/integrate_roadmap_flow.py`.
Run `node tools/test_roadmap_flow.cjs` to check clinical-content preservation
and link coverage.

The seven interactive transplant protocols live in `transplant/`; their
source and verification tools are under `tools/decision_assistant_source`.
They have separate patient-finding logic and contextual high-risk reviews.
Do not transfer the roadmap topic-selector model to that evaluator.

Content is a decision-focused evidence synthesis, not a systematic review.
Single-arm response data are never used to infer superiority.
