# Decision workspace

The shared three-column layout covers 103 topics on 12 cancer roadmaps and
46 decisions on seven transplant pathways, including read-ahead previews.

1. **Tests & data:** required findings and the original transplant checklist;
   concise, topic-specific input summaries on the cancer roadmaps.
2. **Criteria & next options:** the original selectors, exact thresholds,
   recommendations, cautions, source links and conditional next actions.
3. **Decision team / Tools & references:** responsible specialties first,
   followed by relevant score definitions, the existing MELD 3.0 calculator,
   evidence access and applicable allocation overviews.

Desktop uses three columns, with extra width for criteria and options. Narrow
screens stack the columns and provide three section shortcuts. The existing
decision trail remains fixed above the content. Criteria expand inline;
explanations retain their information panels. High-risk items retain orange
styling and their original conditional placement.

`assets/decision-workspace.js` moves existing DOM nodes and never records or
changes findings. Clinical matching, selection, confirmation, reset, routing,
citations and calculator logic remain in their original modules.

## Source maintenance

Transplant teams and checklists come directly from each embedded protocol.
Roadmap input/team/tool summaries are maintained in
`tools/decision_workspace_source.json`. These are presentation and proposed
workflow summaries, not specialty approval or new clinical eligibility rules.

Run `node tools/build_decision_workspace.cjs` after reviewing source changes.
The generated metadata retains the exact original topic title and criteria
as guards. If they do not match the rendered source, the original layout
remains available instead of displaying mismatched summaries.

Run `node tools/test_decision_workspace.cjs` and the existing clinical,
routing, compact-trail, clinical-tool and release checks. Browser verification
must cover desktop and phone layouts, read-ahead previews, a confirmed finding,
an unapplied edit, downstream clearing after applying an edit, score tools,
evidence access, and source-specific high-risk actions.
