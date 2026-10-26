# Houston waiting outcomes and MELD-exception overview

Analysis/source review: 26 October 2026.

## Sources and scope

The quantitative analysis was reconstructed from the original December 2025 OPTN STAR liver registry (392,625 records) and exception data in the 10,000 LDLT study. The dynamic HCC project has copies of these source files, but its marker-complete modeling cohort was not used: requiring serial tumor/AFP/laboratory measurements would change the population whose access is being described.

Houston refers to three adult listing programs: Memorial Hermann, Houston Methodist and Baylor St. Luke’s. The existing study crosswalk is **inferred from aggregate transplant-count fingerprints**, not an official registry crosswalk. Each program matched all 58 annual donor-type count cells for 1996–2024; all six held-out donor-type cells in 2025 also matched. The analysis is pooled, unadjusted and does not rank programs. It does not cover every Houston resident, every possible Houston program, or current 2026 waiting-list performance.

## Cohorts and clocks

- **HCC: 425 adults.** First recorded HCC exception application nationally, dated 4 February 2020–31 December 2024, at a mapped Houston program. All 425 first records are marked Initial. Named HCC application categories include T2, nonstandard HCC, historical T1 and the newer HCC category. Requests are included regardless of approval. First requests elsewhere, HCC without an application, and prior requests before the entry window are outside this cohort.
- **All diagnoses: 2,668 adults.** First recorded national liver registration, at age ≥18, at a mapped Houston program during the same entry window. This separate cohort is general access context, not a rare-cancer prediction.
- HCC time begins at application; all-diagnosis time begins at listing. No future transplant or complete longitudinal-marker requirement defines either cohort.
- Follow-up stops at the index registration’s first terminal outcome or its recorded end, no later than 31 December 2025. Inactive time is included. No one was administratively censored before the one-year summary.

The 1,692 registry rows without a listing identifier are not used as index registrations; their transplant information remains available for exact person linkage. Every nonblank registration identifier is unique. All 149,004 named HCC forms link to the registry. Five national forms have application dates outside registration bounds; none contributes an invalid entry to the Houston cohort. All included entries have usable age, center, start and end dates.

## Outcomes and estimation

Deceased-donor transplantation (DDLT), living-donor transplantation, death/removal as too sick, other removal, and transplant with unknown donor source are competing terminal outcomes. Transplant dates and donor source are linked by exact encrypted person identifiers within the index-registration period. All 222 HCC and 1,491 all-diagnosis transplant outcomes have exact donor-source linkage; no removal-code fallback or unknown-donor category was needed. The death/too-sick outcome includes registry removal codes for death, deterioration and intraoperative death when a transplant event was not linked; a documented death before the registration terminal date is retained. Same-day linked transplant/death is classified as transplant. Death/too-sick removal does not establish cancer progression as the cause.

Other removal includes transfer, medically unsuitable removal (code 5), improvement, refusal and other non-transplant removal codes. These outcomes end the index registration. Outcomes after those removals are not followed in this estimand. These estimates therefore concern transplantation before leaving the index listing, not eventual transplantation anywhere or overall survival after referral.

Aalen–Johansen cumulative incidence accounts for the competing terminal outcomes. Event ties use the risk set immediately before the event, before same-day censoring. Displayed curves are monthly evaluations through 24 months. A month equals 365.25/12 days. Intervals are pointwise 95% percentile intervals from 2,000 person-level bootstrap samples, seed 20261026. They do not include center-mapping uncertainty or adjustment for calendar changes, blood group, severity, readiness, donor preferences or program practice.

| Population | DDLT at 6 months | DDLT at 12 months | DDLT at 24 months |
|---|---:|---:|---:|
| HCC applicants, N=425 | 9.9% (7.1–12.7) | 35.3% (30.8–40.0) | 50.7% (45.8–55.4) |
| All adult first listings, N=2,668 | 38.9% (37.1–40.8) | 47.3% (45.4–49.3) | 53.1% (51.2–55.1) |

Parentheses are pointwise 95% confidence intervals. At 12 months, HCC death/too-sick removal was 19.8% (16.0–23.5); all-diagnosis death/too-sick removal was 16.6% (15.2–18.0).

Do not substitute the median among recipients for the expected wait of an unselected candidate. In the HCC cohort, recipient-only median time from application was 8.9 months, while cumulative DDLT across all applicants reached 50% at about 22.0 months. The curves do not establish the allocation score used for each offer; a transplant before six months does not by itself establish a policy violation. The policy delay, pre-application observation requirements and observed waiting time are different clocks.

## Verification and reproducibility

The saved local builder records raw-file hashes, source schemas, cohort exclusions, endpoint counts, date checks, environment and bootstrap seed. Independent event-by-event arithmetic reproduces the vectorized cumulative-incidence estimator. One-year estimates also match direct endpoint proportions, because no administrative censoring occurs before one year. A second SAS reader in R verifies included keys and dates against raw data, and `survival::survfit` independently reproduces the 6-, 12- and 24-month competing-risk estimates from the reconstructed endpoints. This is not an independent reconstruction of every endpoint or external analyst consensus.

Patient-level records, center-code mappings and local working paths are excluded from the public repository. The downloadable JSON contains pooled aggregate estimates only. Rare-cancer and small subgroup estimates are not provided.

## Current policy references

- [OPTN policies, effective 1 October 2026](https://www.hrsa.gov/sites/default/files/hrsa/optn/optn_policies.pdf): adult MELD §9.1.D; requests/extensions §9.4.A–C; donor-hospital MMaT and floor §9.4.D–E; pCCA §9.5.A; HCC §9.5.I.
- [Adult transplant-oncology NLRB guidance](https://www.hrsa.gov/sites/default/files/hrsa/optn/adult-meld-exception-transplant-oncology-review-guidance.pdf): distinct individual-review recommendations for HCC, iCCA/mixed HCC–iCCA, NELM, CRLM, HEHE and adenomas. Guidance does not create automatic standardized exceptions.
- [September 2026 MMaT table](https://www.hrsa.gov/sites/default/files/hrsa/optn/median-meld-peld-at-tranplant-sept2026.pdf#page=100): Houston donor-hospital entries have MMaT 34; the source transplant cohort is 1 September 2025–31 August 2026. The corresponding MMaT − 3 example is 31; MMaT − 20 has a floor of 15. MMaT is donor-hospital-specific and must be checked for an actual offer.

The page is an educational reference accompanying draft clinical pathways. Its historical analysis is not a validated individual prediction or an official OPTN/SRTR report.
