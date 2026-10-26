# Layered decision interface — 25 October 2026

This supersedes the earlier all-decisions example preset and floating-criteria behavior. It changes navigation and disclosure, not the clinical matcher, source criteria, action conditions, evidence, or approval statuses.

## Display contract

- Essential actions, next-action conditions, cautions, and high-risk status remain visible.
- Criteria and definitions use native inline click-to-expand disclosures, including short threshold instructions that previously appeared as floating help. Source links remain inside those criteria.
- Rationale, explanatory text and evidence summaries use the existing hover/tap/optional-hold information panels. Keyboard and phone Back dismissal remain supported.

## Transplant pathways

A labeled example fills only the first finding on ordinary entry. Direct links to later decisions start unanswered. Each essential question then appears in sequence, followed by applicable safety/high-risk clarification questions and an unanswered next-action selector. Completed choices stay in a pinned trail above the current question. Long histories scroll within a bounded area on phones; the current question stays outside that scroll area. Earlier edits clear later questions in the same decision, later decisions and dependent risk context. Supplemental safety findings must be chosen before the ordinary forward assessment button can be used; known stop findings still offer appropriate care routes without requiring irrelevant later transplant findings. No matching rule was changed.

Care pages preserve their exact originating result, condition and return link. Opening a care plan directly remains a reference. Browser navigation stores only topic/step IDs; findings remain in memory and are not saved. A previously preselected entry finding retains its example label until it is changed.

## Cancer roadmaps

The starting topic and conditional next assessments form a pinned trail using the existing 284 conditional links. Choosing an earlier alternative truncates subsequent topics and replaces the next options. Each new next-assessment selector is blank. Roadmap topic selection is navigation, not patient classification or eligibility. The older staging diagram remains in a reference expansion. All 103 topic data records and their treatment/evidence renderers are unchanged.

## Validation and rebuild

Run `test_decision_layers.cjs` with the existing clinical, contextual, high-risk, roadmap, action, V12 and matrix tests. New tests exercise 96 essential questions and 96 intra-decision/downstream rollback cases, with unchanged clinical matching and source links. Browser checks cover all 46 decisions and all 103 topics at desktop and 390 px phone width, plus branch replacement, AFP alternatives, inline criteria, info sheets, Back/Forward and care origins. Prior orange document checksums remain unchanged.

Keep the current `transplant/assets/app.js` and `assistant.js`, their `tools/decision_assistant_source` mirrors, `assets/decision-layers.css`, `assets/roadmap-flow.js`, `assets/contextual-info.js`, and the portal loader together. The cache version is `20261025-layers1`. Follow V12_REBUILD.md for source/evidence preservation. Canonical source files are mirrored under `standard_protocol_website/src` in the local workspace. Do not regenerate from stale procedural content.

Analyst A performed this interface revision and validation. Earlier external analyst reviews are retained in the prior review folders; they are not claimed as a new review of this iteration.


## Compact trail — 26 October 2026

The shared `compact-trail.js`/`.css` and `compact-trail-labels.js` enhance the existing controls into a horizontal numbered strip. Only one exact-answer editor opens at a time. Tapping to inspect a finding does not change answers; selecting a new answer uses the original reset/routing handlers. Phone history scrolls horizontally, separately from the current question.

Labels are checked against 96 full source questions, 23 supplemental question types and 103 roadmap topics. Short noun labels never replace the complete active question for bare Yes/No choices. Keep full questions, exact options, criteria and citations in the source data. The enhancement does not change matching, actions or source files.

The shared loader version is `20261026-compact1`; core layered app/assistant versions remain `20261025-layers1`. The portal loader must retain the compact assets after a rebuild. Run `test_compact_trail.cjs` with the existing regression suite. Review/reconciliation and actual external Analyst B comments are retained in the local `Compact_Trail_Review_2026-10-26` folder.

Final compact layout: only the numbered strip is sticky (54 px at tested phone width). The current control and editor remain in normal page flow. A completed editor expands its exact criteria locally without changing the hash or visible trail. The unnumbered Next steps tile goes to the original conditional action panel, including high-risk review options. No action-only dropdown remains in the sticky strip. Active Yes/No questions retain the full source predicate.


## Single progression area — 26 October 2026

Supersedes the compact Next steps jump tile. `compact-trail.js` moves the original decision section and result into one working area beneath the strip. Source controls, result elements, clinical event handlers, evidence and care-origin capture are reused without copying. Each chosen finding reveals the next unanswered finding; when the findings are complete, the same area presents the original named next-action buttons. Actions retain their conditions and high-risk statuses. The numbered buttons reopen earlier choices only; the current marker is noninteractive. Earlier edits still clear dependent answers.

Current and completed Criteria controls expand locally without navigating. The whole-pathway map is secondary, collapsed browsing; browse previous/next controls and duplicate source finding controls are hidden in the enhanced view. Printing restores source findings. The next assessment and current finding receive corrected focus and scroll placement. Roadmaps keep conditional action links as the sole forward controls.

The shared loader version is `20261026-navigation1`; the app, clinical matching engine, source payloads, high-risk routing and authoring documents are unchanged. Run the existing regression suite and verify real browser progression, criteria, rollback, high-risk and care routes. No new external-analyst review is claimed for this follow-up.
