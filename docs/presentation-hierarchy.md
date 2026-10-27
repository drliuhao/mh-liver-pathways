# Clinical presentation hierarchy

Use the same hierarchy on every roadmap and transplant pathway. A recent revision is not a reason for greater prominence.

1. **Disease / pathway**: navigation between diseases and clinical pathways. Treatment matrices are resources; individual studies are never disease-level navigation.
2. **Major clinical decision**: always-visible pinned topic strip. Only clinical questions, care states, or assessments belong here. Viewing a topic does not record a finding or establish eligibility.
3. **Decision workspace**: Tests needed / Results & criteria / Tools & resources. Three columns on desktop; tabs on phones. Decision team appears first in Tools.
4. **Current clinical work**: relevant criteria; recommended options or the result matched to recorded findings; then conditional next actions. Keep critical cautions and approval status visible. High-risk reviews are orange and appear only with the relevant findings.
5. **Decision support**: scores and classification definitions in Tools for the relevant decision; individual studies and detailed evidence after recommendations and next actions. Indications and contraindications remain peer disclosures. Unrelated evidence stays in the evidence library.
6. **Background**: full source library, document provenance, operational approvals, and change log. These must not compete with clinical choices.

## Adding or revising content

- Assign a clinical owner before adding a panel. `tools/content_hierarchy.json` maps each inherited reference to its owning decisions and its role: tool, criteria, guide, or evidence.
- Do not add a top-level banner, quick-reference item, new primary tab, or colored callout simply because material is new.
- A trial supports a treatment decision. It is not itself a clinical option. A prognostic association is not an eligibility rule.
- Scores, clinical options, source papers, administrative documents, and proposed study protocols must not share an undifferentiated list of buttons.
- Preserve thresholds, cohort qualifiers, source links, recommendation labels, and critical precautions when moving content. Do not regrade evidence as part of layout work.
- Default to the existing shared structure. Avoid disease-specific global cards when the content applies to one assessment.
- Regenerate `assets/content-hierarchy-data.js` with `node tools/build_content_hierarchy.cjs`; run `node tools/test_content_hierarchy.cjs` plus the existing presentation and clinical-routing checks.
- Check every changed decision on desktop and phone. Confirm all original reference content remains accessible and unchanged after topic switches.
