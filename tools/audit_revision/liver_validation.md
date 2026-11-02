# Liver roadmap validation — 2026-11-02

- PASS: exact sequential replay from baseline `30039fe`; 275 patches in 22 protected files. `python3 tools/audit_revision/compact_liver_manifest.py`.
- PASS: all 21 changed JSON files parse.
- PASS: `node tools/test_content_hierarchy.cjs` — 49 references assigned to clinical decisions; recommendation/evidence hierarchy retained.
- PASS: `node tools/test_roadmap_flow.cjs` — 103 topics across 12 roadmaps, 294 conditional links valid.
- Earlier integrated clinical-flow run encountered an unowned transplant mirror path-prefix mismatch; parent owns final rerun.

## Targeted browser result

The existing `test_tools_column_browser.py` was executed in memory with ROADMAPS limited to HCC, CRLM, iCCA, pCCA, NET and cHCC-CCA, and mobile checks extended to those six. No protected or shared test source was edited. Preview: `http://127.0.0.1:8892/mh-liver-pathways/`. Python Playwright and installed Chromium from the shared audit environment.

**FAIL during shared integration:**

- HCC decision 0: no Tools column mounted.
- HCC decision B: ALBI example reported “Choose both laboratory units.” The existing test example lacks the now-required unit inputs.
- CRLM decision 4: no Tools column mounted.
- pCCA decisions 0, 3 and 5: no Tools column mounted.
- NET decision 1: no Tools column mounted.
- cHCC-CCA decision 5: no Tools column mounted.

The test reported no phone overflow or page errors. This is not a final integrated UI pass; shared generation and the changed calculator contract require the parent task's final check. The liver data files remain stable for that integration.
