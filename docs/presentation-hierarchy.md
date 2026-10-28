# Clinical presentation hierarchy

Use the same hierarchy on every roadmap and transplant pathway. A recent revision is not a reason for greater prominence.

1. **Disease / pathway**: navigation between diseases and clinical pathways. Treatment matrices are resources; individual studies are never disease-level navigation.
2. **Major clinical decision**: always-visible pinned topic strip. Only clinical questions, care states, or assessments belong here. Viewing a topic does not record a finding or establish eligibility.
3. **Decision workspace**: Tests needed / Results & criteria / Tools & resources. Three columns on desktop; tabs on phones. Decision team appears first in Tools.
4. **Current clinical work**: relevant criteria; recommended options and possible results (or the matched result in optional finding mode); then conditional next actions. Keep critical cautions and approval status visible. High-risk reviews are orange, with their triggering conditions and approval status shown beside the relevant decision.
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

## Compact treatment evidence

- Use the shared compact Indications / Contraindications & cautions / Evidence & sources controls on roadmap treatment options. Keep critical safety statements outside optional panels. Phone labels may shorten while accessible names retain their meaning.
- Keep numerical evidence attached to its actual treatment option and named study. State the population, arms, endpoint/time horizon and material limitations. A shared PMID alone does not justify moving another study result into an option.
- Every cited study appears as one line in the liver-directed matrix format: name · PMID · arms · main result · limitation (the PREMIERE row is the model). A result the option's own text reports for that study is shown first; otherwise the line is the study's own result in its own population, labelled by its arms, never restated as the option's effect. Non-PMID sources show their category and citation. Lines are curated in `tools/compact_evidence_source.json`; every number must sit in a quoted passage from the site or the team's V15 evidence decks (`tools/compact_evidence_ppt_quotes.json`, checked by `tools/check_compact_evidence_ppt.py`). Figures from the decks are not published.
- Source chips anywhere (refchips, transplant citations, decision-aid links, systemic source lists) carry a PMID and a short description beside the name.
- Recommendation groups are separate tinted panels: Standard approach (green), Reasonable alternatives (blue), Avoid / cautions (brick, never the orange reserved for high-risk protocols). Items without indication blocks (most Avoid items) use the same peer controls (Why · Evidence & sources); no pop-up explanation links remain inside recommendations.
- Version-history remarks ("v0.2 said…", "the page previously quoted…") do not belong in clinical text. Curated exact strings are hidden in place and listed verbatim under "Revision notes" beside the change log; mixed sentences that carry clinical content stay until the source text is reworded.
- Source documents and clinical data remain the source of truth. Explicit, reviewed reference groups can reuse treatment-reference results when the option's own text is insufficient; preserve their cohort limits and distinguish a response endpoint from survival.
- Do not infer equivalence from nonsignificance, or rank regimens by survival from different trials. Keep study evidence separate from patient eligibility and treatment recommendations.
- Do not display standalone “Outcome evidence for this decision” or “Outcome evidence library” panels (Hao, 28 October). Retain evidence under the actual options and in the source libraries. The former outcome-card assets remain archived, unloaded, for future review.
- The systemic matrix uses tumor tabs, setting filters, a setting overview and compact regimen cards. Its build pipeline applies `tools/systemic_matrix_style.py` after regenerating the source page and data. Evidence row segments and reviewed de-duplication rules are in `tools/systemic_evidence_rows.json`.
- Regenerate shared evidence with `python3 tools/build_compact_evidence.py`. Validate with `tools/test_compact_evidence.py`, `tools/test_systemic_matrix_style.py`, source-preservation checks and browser checks of both desktop and phone.

## Transplant pathway workspace

- Transplant pathways use the roadmap's visual language (`assets/transplant-workspace.css/.js`, presentation only). The decision strip groups the decisions under the pathway's four phases (Diagnosis and extent · Transplant suitability · Preparation and reassessment · Transplant and follow-up) and numbers them when the row fits. Each decision is one card: question, context line, three columns.
- **Default view (Hao, 28 October): nothing has to be chosen.** The middle column lists every possible result of the decision the way a roadmap lists its options: "What this decision assesses" (questions, definitions, and an Evidence & sources peer), then "Possible results within this decision", grouped as Continue assessment (green) · Clarify before continuing (amber) · Another route (blue) · Stop (brick) · High-risk protocol reviews that cover this decision (orange) · Reasons to reassess (brick). Each option shows its title and action verbatim from the page's protocol data, its next-step links (the page's own renderer, so routing is unchanged), and peer panels for **Applies when** (criteria with sources) and **Evidence & sources** (one matrix-style line per source: studies with PMID, arms, result and limitation; guidance and policy with type, note, locator and link).
- **Optional step-by-step entry** ("Record findings step by step" in Tools) switches to the original finding-by-finding view: findings → criteria → matched result → reasons to reassess → other results. Nodes are regrouped, not rewritten. The choice is a per-viewer convenience in browser storage.
- Orange remains reserved for high-risk protocols. Routing, criteria and wording are unchanged.
- Validate with `tools/test_transplant_workspace_browser.py` (all 46 decisions of the seven pathways compared with their protocol data; next-step links; step-by-step mode; phone).
