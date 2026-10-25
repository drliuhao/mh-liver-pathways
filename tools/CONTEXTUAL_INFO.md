# Contextual explanation display

The 25 October 2026 interface is a progressive enhancement loaded by `assets/portal-navigation.js`. `assets/contextual-info.js` and `.css` serve both the 12 cancer roadmaps and 7 transplant pathways. They rearrange existing DOM nodes, never clinical data. Older browsers retain native disclosures.

Keep selection criteria, essential question help, timing/ordering, action conditions, safety warnings and proposed/closed high-risk statuses on the page. Selected assistant definitions remain inline. The explicit 8-suffix allowlist is checked against the exact V12 source text; do not replace it with keyword-based automatic hiding. A changed source simply remains visible until reviewed.

Native Popover API on desktop; modal dialogue sheet on phone. Tap is primary, long press optional on information buttons only. Keyboard Enter/Space and Escape work. `ContextualInfo.handleHistory` integrates phone Back dismissal with the transplant renderer; `sourceOrigin` restores focus after reading a source. Roadmap reference chips dismiss the information sheet and focus the evidence-library entry. Do not remove these integration hooks during regeneration.

Reading mode expands contextual explanations inline. Print expands contextual panels plus checklists, definitions and discussion questions, then restores their previous state. Original information remains in the DOM. No patient selections or new preferences are saved.

After a legacy rebuild, follow `V12_REBUILD.md` and preserve the current shared renderer and contextual assets. Do not regenerate V12 content from stale procedural data. Run all V12/routing/roadmap tests plus `node tools/test_contextual_info.cjs`. Browser validation includes all 46 decisions and 103 topics, desktop/mobile interaction, source navigation and selected high-risk/safety cases. Review/reconciliation is stored in the local Contextual_Explanations_Review_2026-10-25 folder.
