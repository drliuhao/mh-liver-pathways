# V12 source and rebuild boundary

25 October 2026: the V12 update adds 14 full-main-paper appraisals, expands the systemic matrix to 49 cards across nine tumor filters, and adds HCC B1.1 with six OPEN meeting questions. It does not change standard eligibility matching rules.

`v12_content_snapshot.json` is the current complete transplant content snapshot. The older procedural source modules predate this evidence integration; do not use them alone to regenerate the site. After a legacy transplant rebuild, run `apply_v12_snapshot.py` and the routing/release tests. Current `transplant/assets/app.js`, `high-risk.js` and `risk-routing.js` must also be preserved; they contain the dedicated AFP review navigation.

The complete local release builder and private evidence metadata are retained under the Synology transplant-protocol workspace in `V12_full_text_integration_2026-10-25/source`. That builder also creates the sanitized public DOCX copies, the six roadmap evidence sections, systemic cards, full-text review page and meeting page. Licensed journal PDFs and private file paths must not be added to this repository.

Tests:

```text
node tools/test_decision_assistants.cjs
node tools/test_contextual_routing.cjs
node tools/test_streamlined_actions.cjs
node tools/test_high_risk_integration.cjs
python3 tools/test_matrix_integration.py
python3 tools/test_v12_release.py
```
