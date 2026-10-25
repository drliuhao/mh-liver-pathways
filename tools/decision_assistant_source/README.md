# Essential transplant decision assistants

Source snapshot for the 46 decision assistants. Canonical authoring files live in `standard_protocol_website/src` in the transplant-protocol workspace, alongside the retained source-backed clinical pathways in `content.py`.

Build: `python3 standard_protocol_website/src/build.py`; export with `tools/build_portal.py <canonical-dist>`; validate with `tools/validate_portal.py <canonical-dist>` and `node tools/test_decision_assistants.cjs`.

Each choice maps to an existing route or an explicitly sourced clarification/reassessment. Proceed highlights require all essential questions. No identifiers, date entry, recording, exports, network submission or persistent storage. Clinical observation intervals remain criteria. Old recording URLs redirect to the associated decision. Licensed PDFs are not published.

October 24 clarity/continuity revision: `content.py` contains the reviewed clinical language; `care_options.py` supplies next actions for every branch and custom result, plus disease-specific treatment, best supportive care, emergency-care and follow-up plans. Six conditional actions are provided for an unmet HCC AFP requirement. Treatment options do not imply restored transplant or exception eligibility. NCCN references identify original PDF pages and the reviewed edition. Existing matching conditions, option values and threshold rules are preserved.

Validation includes 1,851 categorical states, all continuation destinations, the T1 distinction, six AFP actions, source locators, and checks against introducing saved patient records. The source snapshot does not include the licensed PDF depot or older Word documents.


## October 24 overview and preselected examples

Each of the seven pathways opens with explicit example selections that follow an existing proceed result at all 46 decisions. The interface labels these as examples, offers restore-example and clear-all controls, and never describes the prefilled choices as completed clinical assessments. Editing a finding clears choices in every later decision; navigation preserves those cleared states. The four-stage overview preserves the original decision order, and the step bar remains visible while scrolling, with an Overview shortcut. On phones the step bar scrolls horizontally. No clinical content, criteria, source statements, matching rules or continuing-care options were changed. No persistent storage was introduced.


## Integrated high-risk protocols — 24 October 2026

`high_risk_data.json` is the normalized reconciled V7 source, without local depot paths or article full texts. `high-risk.js` renders the 21 disease reviews at 31 relevant decisions in the seven standard protocols, plus four shared approval/readiness reviews. Orange labels identify high-risk protocols; each section retains its proposed, research-only or closed status. The renderer does not participate in eligibility matching or modify example answers.

`tools/integrate_high_risk.py <V7-package> <access-lookup.json> <canonical-source/high_risk_data.json>` regenerates the source from `decision_records.json`, `evidence_reviews_combined.json` and bibliographic/access metadata. The lookup used for this release is retained in the local integration audit. Rebuild standard pages, run `tools/build_high_risk.py <V7-package>` for the directory/legacy redirects, then export. Use `--preserve-existing-documents` when exporting into a checkout with independently edited Word documents.

Run `node tools/test_high_risk_integration.cjs` as well as the standard checks. Only the seven author-created V7 protocol PDFs in `transplant/high-risk/authored-documents.json` are allowed; the validators check their hashes. Licensed primary-source PDFs remain in the local depot. The website links to PMC, Europe PMC, publisher/repository PDFs where found, and TMC catalogue DOI searches for institutional access. A discovered PDF endpoint does not guarantee unauthenticated access; primary-source sites may require sign-in or a browser check.

## October 25 document-specific evidence libraries

The public `/evidence-libraries/` catalog lists each library, PDF availability, TMC access and exact PPT slide numbers. The 34 PPTs and licensed PDF depots remain private in Synology. Shared references repeat in the relevant libraries but count once globally. Catalog metadata records 618 unique publications, 573 matched PDFs, 45 unmatched PDFs and 25 pending appraisals. Reorganization does not imply a new full-text review. Run `python3 tools/test_evidence_libraries.py` to validate the public catalog.
