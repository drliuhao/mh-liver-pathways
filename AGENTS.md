# Website editing conventions

## Clinical hierarchy

Read `docs/presentation-hierarchy.md` before changing roadmap or pathway presentation. Prominence follows clinical role, never the recency of a request or addition. Individual studies belong under the clinical decisions they support; do not add them to top-level navigation or global quick-reference strips.

Keep clinical decisions visible, preserve conditional next actions and source qualifiers, and retain orange labels for high-risk protocols. Assign reference ownership in `tools/content_hierarchy.json`. Verify switching decisions, source access, desktop columns and phone tabs before publishing. Run the hierarchy, source-preservation and relevant routing tests.

## Analyst designations

Analyst A = Codex; B = Claude.ai; C = Claude.science (localhost service); D = Doximity; E = OpenEvidence. App and web interfaces retain the same designation. Do not substitute internal subagents for these named external analysts. Preserve reviewer comments and reconciliation in Markdown when conducting multi-analyst reviews.

## Keep website, documents and presentations consistent

When clinical website content changes, propagate the accepted correction to all affected current Word documents and PowerPoint evidence libraries before publishing. Preserve prior editions locally and preserve editable figures, charts, citations and source qualifiers. Regenerate discussion documents from the current decision data, verify updated artifacts and record their hashes in the artifact release manifest. Publish the same clinical content to the full and sharing websites; the sharing edition must not expose institutional document or presentation downloads. Do not treat historical archived editions as current downloads.
