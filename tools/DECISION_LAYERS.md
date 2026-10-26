# Decision interface

26 October 2026. Presentation and navigation only: clinical matching, thresholds, uncertainty, source records and approval statuses are retained.

## Display contract

- Current question summaries, threshold rules, relevant selected definitions, cautions and conditional actions are visible without opening an explanation.
- Definitions start open while selecting a finding; relevant recorded definitions remain visible while answering the next question.
- Sources, rationale and supplementary explanations can expand. Evidence is organized by clinical topic and study design, never promoted because it was added recently.
- History collapses; clinical conditions do not disappear into a navigation selector.

## Transplant pathways

Ordinary entry starts unanswered. **Show entry example** is optional and explicitly labeled. A dropdown stages a finding; **Use finding** or **Apply change** commits it. Arrow keys and Enter on the dropdown do not commit or advance. Unapplied choices identify the current recorded finding and offer Cancel; Escape cancels. Changing an earlier finding clears later dependent findings. Supplemental safety questions follow the same confirmation model.

Rows use the actual clinical decision number. There is no separate numbered navigation row or next-action dropdown. Each actual action appears once with its condition in the result. A single available action is a direct button, not a redundant selection. Earlier findings are available under **Selected findings — review or change**.

Care plans retain their originating result, status, option and condition. Opening a plan directly is reference-only. Choices remain in memory and are not persisted or included in URLs. Clinical suitability and allocation remain separate.

## Cancer roadmaps

**Clinical topics** is navigation, not patient classification. A topic choice requires **Open topic**; an unapplied choice identifies the topic still showing. **Previously viewed** is optional navigation history. The existing 284 conditional links remain beside their When statements. All/any criteria start expanded, with the no-eligibility-inference notice outside the disclosure. The 103 clinical topic records and their treatment renderers are unchanged.

## Documents and rebuilding

Seventeen current Word documents use subject-based headings and evidence placement. EndNote field instructions, embedded citation data and delimiters are preserved byte-for-byte as multisets. Orange high-risk styling and OPEN status remain. `clarity_document_hashes.json` records current editorial hashes; `orange_document_hashes.json` remains the earlier style-change record.

Preserve the current app/assistant source mirrors, roadmap-flow, contextual-info, decision-layers and portal-navigation assets. Cache key: `20261026-clarity2`. Follow `V12_REBUILD.md`, then run `normalize_evidence_presentation.py` after a legacy evidence rebuild. Do not regenerate the interface from stale procedural sources.

## Review and validation

External Analyst B (Claude.ai in Claude Desktop) reviewed the original and candidate interfaces and all 17 documents textually. Raw reviews and reconciliation are retained in the local `Website_Clarity_Review_2026-10-26` folder. Review is editorial/interface review, not clinical or institutional approval. Native Word/EndNote refresh is not part of the field-preservation check.

Run the decision-layer, assistant, clinical-flow, contextual, routing, roadmap, high-risk, action, matrix and release tests. Browser checks include all 46 direct decisions, all 103 topics, phone overflow, staged/committed edits, rollback, AFP alternatives, care origins and Back. Render and inspect both public and private document variants after document changes.
