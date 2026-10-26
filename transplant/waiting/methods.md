# Houston waiting outcomes and MELD-exception overview

Analysis/source review: 26 October 2026. Analyst A. Entry restricted to **2021–2025**, the last five complete years in the available registry.

## Sources and scope

The quantitative analysis was reconstructed from the original December 2025 OPTN STAR liver registry (392,625 records) and exception data in the 10,000 LDLT study. The dynamic HCC project has copies of these source files, but its marker-complete modeling cohort was not used: requiring serial tumor/AFP/laboratory measurements would change the population whose access is being described.

Houston refers to three adult listing programs: Memorial Hermann, Houston Methodist and Baylor St. Luke’s. The existing study crosswalk is **inferred from aggregate transplant-count fingerprints**, not an official registry crosswalk. Each program matched all 58 annual donor-type count cells for 1996–2024; all six held-out donor-type cells in 2025 also matched. Those earlier records validate program identification only; the waiting-outcome cohorts include **2021–2025 entrants only**. The analysis is pooled, unadjusted and does not rank programs. It does not cover every Houston resident, every possible Houston program, or current 2026 waiting-list performance.

## Cohorts and clocks

- **HCC: 463 adults.** First recorded HCC exception application nationally, dated 1 January 2021–31 December 2025, at a mapped Houston program. All first records are marked Initial. Named HCC application categories include T2, nonstandard HCC, historical T1 and the newer HCC category. Requests are included regardless of approval. First requests elsewhere, HCC without an application, and prior requests before the entry window are outside this cohort.
- **All diagnoses: 2,890 adults.** First recorded national liver registration, at age ≥18, at a mapped Houston program during the same entry window. This separate cohort is general access context, not a rare-cancer prediction.
- HCC time begins at application; all-diagnosis time begins at listing. No future transplant or complete longitudinal-marker requirement defines either cohort. Earlier records are read to establish the first national request/listing and prevent including repeat entries as new candidates.
- Follow-up stops at the index registration’s first terminal outcome or its recorded end, no later than 31 December 2025. Inactive time is included.
- **Follow-up is shorter for recent entrants.** 124 HCC applicants and 696 all-diagnosis candidates entered in 2025. Administrative censoring occurred before 12 months for 93 HCC applicants and 327 all-diagnosis candidates. These candidates contribute their observed follow-up; they are not excluded or counted as known one-year non-events. Longer-term estimates draw increasingly on earlier entrants.

The 1,692 registry rows without a listing identifier are not used as index registrations; their transplant information remains available for exact person linkage. Every nonblank registration identifier is unique. All 149,004 named HCC forms link to the registry. Five national forms have application dates outside registration bounds; none contributes an invalid entry to the Houston cohort. All included entries have usable age, center, start and end dates.

## Outcomes and estimation

Deceased-donor transplantation (DDLT), living-donor transplantation, death/removal as too sick, other removal, and transplant with unknown donor source are competing terminal outcomes. Transplant dates and donor source are linked by exact encrypted person identifiers within the index-registration period. All included transplant outcomes have exact donor-source linkage; no removal-code fallback or unknown-donor category was needed. The death/too-sick outcome includes registry removal codes for death, deterioration and intraoperative death when a transplant event was not linked; a documented death before the registration terminal date is retained. Same-day linked transplant/death is classified as transplant. Death/too-sick removal does not establish cancer progression as the cause.

Other removal includes transfer, medically unsuitable removal (code 5), improvement, refusal and other non-transplant removal codes. These outcomes end the index registration. Outcomes after those removals are not followed in this estimand. These estimates therefore concern transplantation before leaving the index listing, not eventual transplantation anywhere or overall survival after referral.

Aalen–Johansen cumulative incidence accounts for competing terminal outcomes and right censoring. Event ties use the risk set immediately before the event, before same-day censoring. Displayed curves are monthly evaluations through 24 months. A month equals 365.25/12 days. Intervals are pointwise 95% percentile intervals from 2,000 person-level bootstrap samples, seed 20261026. They do not include center-mapping uncertainty or adjustment for calendar changes, blood group, severity, readiness, donor preferences or program practice. The pooled estimates assume non-informative censoring; calendar changes may limit how well longer follow-up from earlier entrants represents recent candidates. These are not 2025-only or current-year predictions.

| Population | DDLT at 6 months | DDLT at 12 months | DDLT at 24 months |
|---|---:|---:|---:|
| HCC applicants, N=463 | 10.3% (7.5–13.2) | 40.9% (35.8–45.7) | 55.1% (49.9–60.3) |
| All adult first listings, N=2,890 | 40.6% (38.8–42.5) | 49.4% (47.4–51.2) | 54.9% (52.9–56.8) |

Parentheses are pointwise 95% confidence intervals. At 12 months, HCC death/too-sick removal was 19.0% (15.4–23.0); all-diagnosis death/too-sick removal was 15.2% (13.9–16.6).

| Population | At risk just before 6 months | At risk just before 12 months | At risk just before 24 months |
|---|---:|---:|---:|
| HCC applicants | 303 | 103 | 24 |
| All adult first listings | 1146 | 629 | 252 |

At risk means still followed on the index registration without a terminal outcome. Censoring and competing events reduce these counts. Later estimates have less follow-up support, particularly for HCC.

Do not substitute the median among recipients for the expected wait of an unselected candidate. In the HCC cohort, recipient-only median time from application was 8.1 months, while cumulative DDLT across all applicants reached 50% at about 16.8 months. Recipient-only summaries omit candidates still waiting or with competing outcomes and favor shorter observed waits among recent entrants. The curves do not establish the allocation score used for each offer; a transplant before six months does not by itself establish a policy violation. The policy delay, pre-application observation requirements and observed waiting time are different clocks.

## Verification and reproducibility

The saved local builder records raw-file hashes, source schemas, cohort exclusions, endpoint counts, date checks, environment and bootstrap seed. Independent event-by-event arithmetic reproduces the vectorized cumulative-incidence estimator. The date audit confirms that every included entry is in 2021–2025 and every endpoint is on or before 31 December 2025. Censoring before 6, 12 and 24 months is explicitly counted. Crude observed event proportions are not used as one-year estimates when follow-up is censored. A second SAS reader in R verifies included keys and dates against raw data, and `survival::survfit` independently reproduces the 6-, 12- and 24-month competing-risk estimates from the reconstructed endpoints. Check type: adapted raw-source reconstruction with independent estimator verification; not an independent reconstruction of every endpoint or external analyst consensus.

Patient-level records, center-code mappings and local working paths are excluded from the public repository. The downloadable JSON contains pooled aggregate estimates only. Rare-cancer and small subgroup estimates are not provided. The prior entry-window analysis remains archived locally; this five-year revision replaces its website figures and methods.

## Current policy references

- [OPTN policies, effective 1 October 2026](https://www.hrsa.gov/sites/default/files/hrsa/optn/optn_policies.pdf): adult MELD §9.1.D; requests/extensions §9.4.A–C; donor-hospital MMaT and floor §9.4.D–E; pCCA §9.5.A; HCC §9.5.I.
- [Adult transplant-oncology NLRB guidance](https://www.hrsa.gov/sites/default/files/hrsa/optn/adult-meld-exception-transplant-oncology-review-guidance.pdf): distinct individual-review recommendations for HCC, iCCA/mixed HCC–iCCA, NELM, CRLM, HEHE and adenomas. Guidance does not create automatic standardized exceptions.
- [September 2026 MMaT table](https://www.hrsa.gov/sites/default/files/hrsa/optn/median-meld-peld-at-tranplant-sept2026.pdf#page=100): Houston donor-hospital entries have MMaT 34; the source transplant cohort is 1 September 2025–31 August 2026. The corresponding MMaT − 3 example is 31; MMaT − 20 has a floor of 15. MMaT is donor-hospital-specific and must be checked for an actual offer.

The page is an educational reference accompanying draft clinical pathways. Its historical analysis is not a validated individual prediction or an official OPTN/SRTR report.
