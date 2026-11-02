# Assigned-roadmap validation

Analyst A (Codex), 2 November 2026. Validation completed after the final NETPET/RTOG follow-up; owned clinical files stable for integration.

Runtime: `/Users/haoliu/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node`. The first test-launch attempt used `node` on PATH and did not run because that command was unavailable. The tests below were then run successfully with the bundled runtime, and repeated after the final clinical edits.

| Check | Result |
| --- | --- |
| `tools/test_content_hierarchy.cjs` | PASS — 49 reference assignments and presentation hierarchy |
| `tools/test_roadmap_flow.cjs` | PASS — 103 topics, 12 roadmaps, 294 conditional links |
| `tools/test_uniform_evidence.cjs` | PASS — 12 libraries, integrated appraisals and source identities |
| `tools/test_clinical_flow.cjs` | PASS — 33 care plans, 77 actions and source mirror |
| `tools/test_contextual_routing.cjs` | PASS — 130 targeted assertions, 2,091 categorical states, 46 decisions |
| Exact protected replay of owned files from Git `30039fe` | PASS — 22 files via 166 unique chunks, byte-for-byte comparison |
| Root `refs`/`nonpm` dictionaries, citation tuples and nested reference-list schema | PASS — checked across all roadmaps after repairing the pancreatic-cyst root-reference propagation |
| `tools/test_evidence_libraries.py` | PASS — 34 libraries, 618 publications, 596 matched PDFs |
| `tools/test_compact_evidence.py` | FAIL during shared integration — quote-provenance and numeric-token checks; details reported to parent, shared files not edited by this task |
| Owned JSON parsing and change-register completeness | PASS — all JSON parsed; all 267 changes include old/new, finding IDs and source locators |
| PDAC speculative-question removal | PASS — no PDAC-B1, PDAC-B2 or orphan `hr-cluster` in owned pathway/consensus/question data |

Shared assets and the final full/share builds may continue to change under the parent task and require its release checks. No browser or deployment validation was performed by this internal implementation task.

Integration caught a reference-propagation error that had converted the pancreatic-cyst root citation dictionary into a list. It was restored from baseline plus PMID37230894, the helper was limited to list fields, and schema/replay/evidence-library checks passed. The requested evidence-library suite is `test_evidence_libraries.py`; an attempted `test_evidence_library.cjs` invocation found no such file.
