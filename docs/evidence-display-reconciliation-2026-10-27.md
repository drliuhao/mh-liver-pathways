# Evidence display review — 27 October 2026

Analyst B (Claude.ai) prepared the shared evidence presentation update against release `235e1fc`. Analyst A (Codex) inspected B's actual Claude conversation and the supplied patch, integrated it, and independently tested the website. The complete handoff and reconciliation are retained in the project review folder.

## Accepted

- 484 study lines: source name and PMID, study comparison/population, principal result and limitation. The 418 results explicitly tied to treatment options retain priority over general study summaries.
- Smaller parallel indication, caution and evidence controls; source labels and explanatory context throughout roadmaps, transplant pathways and the systemic matrix.
- Green standard approaches, blue reasonable alternatives and brick avoid/caution panels. Orange remains reserved for high-risk protocols.
- Fourteen exact historical revision remarks moved to a separate disclosure; mixed clinical/history statements retained.
- Existing clinical criteria, recommendation grades, calculators and conditional routes preserved.

## Integration corrections

- Restored `stratification` in eight roadmap source files: 14 literal occurrences in the supplied patch. Historical preservation tests permit only this exact word correction; their other comparisons remain intact.
- AASLD 2025: systemic therapy **for** resection/ablation, rather than describing neoadjuvant treatment as occurring after surgery.
- IMbrave050: crossover complicates overall-survival interpretation; it does not make every survival analysis uninterpretable.
- Baveno VII: clarified that the virus/alcohol/non-obese NASH restriction belongs to the noninvasive rule-in cutoff. Confirmed against the local primary PDF, statements 2.15–2.16 (PDF p. 7). No standalone resection exclusion is inferred.
- Clarified five nonsignificant comparisons to avoid implying equivalence: PMIDs 26482044, 34925507, 35949295, 39693584 and 40523372. Numerical findings remain source-linked.

- Reconciled the completed depot audit: eight existing PDFs now show as in-depot at 32 website locations. Corrected author/journal/year metadata for nine HAI references across four roadmap libraries. PMID 36346892 remains marked for download because its complete local PDF was not verified.

## Independent verification

- All 17 JavaScript test suites and six Python release/evidence suites pass; legacy recording-template redirects also pass.
- All 1,337 deck-sourced quotations match their specified slides in 14 of the V15 evidence decks.
- Browser review: all 103 roadmap decisions, 115 visits including revisits, and 868 treatment-option views; each option enhanced, panels initially collapsed, study results present and three recommendation groups visually distinct.
- All seven transplant pathways have typed source controls; all seven high-risk entry points preserve study summaries and protocol controls. The systemic matrix retains all 49 regimen cards and supplies a study line for each PubMed source.
- Representative phone pages tested at 390 pixels, including expanded evidence and high-risk protocol controls; no horizontal overflow. Phone tabs switch between results and tools. High-risk headings remain orange.
- Of 29 protected clinical/reference files, 21 are byte-identical and eight differ only by the verified word restoration. No clinical routing or allocation criteria changed.

This is a presentation integration and evidence-wording review, not a new systematic review or institutional clinical approval.
