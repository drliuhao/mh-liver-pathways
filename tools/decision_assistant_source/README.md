# Essential transplant decision assistants

Source snapshot for the 46 decision assistants. Canonical authoring files live in `standard_protocol_website/src` in the transplant-protocol workspace, alongside the retained source-backed clinical pathways in `content.py`.

Build: `python3 standard_protocol_website/src/build.py`; export with `tools/build_portal.py <canonical-dist>`; validate with `tools/validate_portal.py <canonical-dist>` and `node tools/test_decision_assistants.cjs`.

Each choice maps to an existing route or an explicitly sourced clarification/reassessment. Proceed highlights require all essential questions. No identifiers, date entry, recording, exports, network submission or persistent storage. Clinical observation intervals remain criteria. Old recording URLs redirect to the associated decision. Licensed PDFs are not published.
