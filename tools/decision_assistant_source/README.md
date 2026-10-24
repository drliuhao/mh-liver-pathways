# Essential transplant decision assistants

Source snapshot for the 46 decision assistants. Canonical authoring files live in `standard_protocol_website/src` in the transplant-protocol workspace, alongside the retained source-backed clinical pathways in `content.py`.

Build: `python3 standard_protocol_website/src/build.py`; export with `tools/build_portal.py <canonical-dist>`; validate with `tools/validate_portal.py <canonical-dist>` and `node tools/test_decision_assistants.cjs`.

Each choice maps to an existing route or an explicitly sourced clarification/reassessment. Proceed highlights require all essential questions. No identifiers, date entry, recording, exports, network submission or persistent storage. Clinical observation intervals remain criteria. Old recording URLs redirect to the associated decision. Licensed PDFs are not published.

October 24 clarity/continuity revision: `content.py` contains the reviewed clinical language; `care_options.py` supplies next actions for every branch and custom result, plus disease-specific treatment, best supportive care, emergency-care and follow-up plans. Six conditional actions are provided for an unmet HCC AFP requirement. Treatment options do not imply restored transplant or exception eligibility. NCCN references identify original PDF pages and the reviewed edition. Existing matching conditions, option values and threshold rules are preserved.

Validation includes 1,851 categorical states, all continuation destinations, the T1 distinction, six AFP actions, source locators, and checks against introducing saved patient records. The source snapshot does not include the licensed PDF depot or older Word documents.
