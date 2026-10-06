# Liver tumour pathways — working consoles

Five Memorial Hermann system roadmaps rendered as interactive pathway pages:
hepatocellular carcinoma, colorectal liver metastases, intrahepatic
cholangiocarcinoma, perihilar cholangiocarcinoma and neuroendocrine liver
metastases.

**Under development.** These are drafts under active revision, prepared for
multidisciplinary and institutional governance review. They are not ratified
clinical policy, they have not been approved by the specialties named in them,
and they must not be used for patient care decisions. Every criterion drawn
from OPTN policy, drug labelling, NCCN or device authorisation must be
re-verified against the current source before any use.

## Layout

```
index.html          landing page
hcc/   crlm/   icca/   hilar/   nelm/
    index.html      the page
    data/           pathway.json, and the shared liver-directed matrix
```

Each page is a single self-contained HTML document that fetches its content
from `data/`. `hcc/index.html` carries its content inline and predates the
shared renderer; the other four are built from one template
(`page.tpl.html` in the source tree) plus a `pathway.json` per tumour.

Content is a decision-focused evidence synthesis, not a systematic review.
Single-arm response data are never used to infer superiority.
