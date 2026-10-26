# Allocation and Houston waiting reference

Added 26 October 2026. The seven adult pathways receive a read-only exception/waiting overview at relevant pretransplant decisions and before the final follow-up content. It is also available in read-ahead previews and through the top “Exception & wait” link. No clinical findings, eligibility rules, result matching or patient storage change.

`assets/allocation-reference.js` owns the seven disease summaries and official source/page links. `assets/allocation-overview.js` attaches the reference without changing pathway state. `transplant/waiting/` provides the complete policy overview, Houston context and methods; `assets/waiting-analysis.js` renders reviewed aggregate JSON from `transplant/assets/houston-waiting.json`.

The analysis was rebuilt locally from original registry files in the 10,000 LDLT project. Only pooled aggregates are included here. The study’s dated `code/houston_waiting_20261026` and `drafts/houston_waiting_20261026` directories retain builders, raw-file hashes, environment, seed, cohort/endpoint audits and independent R checks. Patient rows and center-code mappings stay local.

Run `node tools/test_allocation_overview.cjs` together with the existing clinical-tools, contextual-copy, assistant, routing and release tests. Browser QA must check all seven final decisions and read-ahead previews, the two population selectors, score-specific disease summaries, calculator access, mobile layout and unchanged assessment findings.
