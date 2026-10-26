# Evidence-library presentation contract

- One original searchable evidence library on each cancer roadmap, with one card per source and the existing clinical-topic filters.
- Add papers to the relevant clinical category. A recent user request, import date or release version must not create a separate category or change visual emphasis.
- Put additional findings and limitations inside the source's ordinary appraisal disclosure. Never leave appended study cards outside the search, count or filters.
- Keep study design and evidence maturity explicit. Conference results, ongoing trials, retrospective cohorts and randomized trials must not be made equivalent by presentation.
- Keep publication years and guideline editions; remove editorial update dates from category labels. Retain history in the footer/change log.
- Keep TMC/DOI/PubMed access on the paper card. Preserve historical citation anchors as aliases when consolidating duplicate access records.
- Do not alter clinical criteria, thresholds, outcomes, caveats or evidence grades during a presentation change.

`unify_evidence_libraries.py` migrates earlier appended appraisals and HAI-only groupings. `roadmap-evidence.js` renders the original cards and preserves citation aliases. The systemic matrix and depot/PPT catalogue retain their context-specific filters; neither should acquire release-specific evidence groups.

Validation: `node tools/test_uniform_evidence.cjs`, the existing evidence/matrix and clinical-flow tests, then browser checks of filters, source anchors, appraisals and phone layout before publishing.
