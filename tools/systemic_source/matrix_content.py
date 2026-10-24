"""Clinical synthesis for the website. Trial outcomes retain their own comparator."""
CARDS=[]
def add(id,tumors,setting,title,position,who,evidence,limits,transplant,refs,links=()):
 CARDS.append(dict(id=id,tumors=tumors.split(),setting=setting,title=title,position=position,who=who,evidence=evidence,limits=limits,transplant=transplant,refs=refs.split(),links=list(links)))

add('hcc-atezo-bev','hcc','first','Atezolizumab + bevacizumab','Preferred first-line option',
 'Unresectable HCC requiring systemic treatment; strongest evidence in Child-Pugh A, ECOG 0–1. Assess and treat high-risk varices before bevacizumab.',
 'IMbrave150: updated median overall survival 19.2 versus 13.4 months with sorafenib; HR 0.66.',
 'Bleeding, portal hypertension, blood pressure, proteinuria and immune toxicity affect selection. Do not compare its survival median directly with a different trial.',
 'Checkpoint therapy can affect subsequent transplant timing and rejection risk. Discuss transplant intent before treatment.', '32402160 34902530')
add('hcc-stride','hcc','first','Durvalumab + tremelimumab (STRIDE)','Preferred first-line option',
 'Unresectable HCC, preserved liver function and fitness for dual checkpoint therapy. An option when bevacizumab is unsuitable and immunotherapy is appropriate.',
 'HIMALAYA: median overall survival 16.43 versus 13.77 months with sorafenib; HR 0.78. Progression-free survival was not significantly improved.',
 'Main portal-vein invasion was excluded from the pivotal trial. Immune toxicity remains important; avoiding bevacizumab does not remove treatment risk.',
 'Requires a transplant-specific plan if transplantation may later be considered.','38319892')
add('hcc-nivo-ipi','hcc','first','Nivolumab + ipilimumab','Preferred first-line option',
 'Unresectable HCC; select patients able to tolerate dual checkpoint therapy and close early monitoring.',
 'CheckMate 9DW: median overall survival 23.7 versus 20.6 months with lenvatinib or sorafenib; HR 0.79.',
 'Survival curves crossed: mortality was higher during the first six months (HR 1.65). Grade 3–4 treatment-related events occurred in 41% versus 42%; treatment-related deaths were 12 versus 3.',
 'Review future transplant intent and immune adverse effects before choosing this regimen.','40349714')
add('hcc-single-ici','hcc','first','Single-agent checkpoint therapy','Selected alternative',
 'Tislelizumab or durvalumab when a single-agent approach is appropriate. NCCN HCC v2.2026 also lists pembrolizumab first line, category 2B.',
 'RATIONALE-301 established overall-survival noninferiority of tislelizumab to sorafenib. HIMALAYA established noninferiority of durvalumab. KEYNOTE-394 supported later-line pembrolizumab in an Asian population; KEYNOTE-240 did not meet its prespecified statistical thresholds.',
 'These agents do not have identical evidence or regulatory indications. Check the current agent-specific label; a later-line study does not establish first-line superiority.',
 'Single-agent checkpoint therapy still carries transplant rejection concerns.','37796513 38319892 31790344 36455168')
add('hcc-tki','hcc','first','Lenvatinib or sorafenib','Alternative when immunotherapy is unsuitable',
 'Unresectable HCC with adequate liver reserve; consider when checkpoint therapy is contraindicated or inconsistent with the transplant plan.',
 'REFLECT: lenvatinib was noninferior to sorafenib for overall survival (13.6 versus 12.3 months). SHARP established sorafenib benefit over placebo (10.7 versus 7.9 months).',
 'REFLECT excluded main portal-vein invasion, ≥50% liver occupation and bile-duct invasion. Dose tolerance and hepatic function matter; trial medians are not individual predictions.',
 'Coordinate perioperative treatment interruption and liver reserve with the transplant team.','29433850 18650514')
add('hcc-later','hcc','later','Cabozantinib, regorafenib or AFP-selected ramucirumab','Subsequent treatment',
 'After progression or intolerance, choose an unused agent according to prior exposure and hepatic reserve. Ramucirumab requires AFP ≥400 ng/mL; RESORCE required prior sorafenib tolerance.',
 'Placebo-controlled overall-survival benefit: CELESTIAL HR 0.76; RESORCE HR 0.63; REACH-2 HR 0.71.',
 'These pivotal trials largely followed sorafenib. The best sequence after modern first-line immunotherapy has not been established by these trials.',
 'A treatment response does not itself restore transplant or MELD-exception eligibility.','29972759 27932229 30665869')
add('hcc-adjuvant','hcc','perioperative','After curative resection or ablation','Surveillance; avoid routine adjuvant atezolizumab–bevacizumab',
 'HCC with no residual disease after resection or ablation.',
 'IMbrave050 initially reported a recurrence-free survival advantage. The 2026 update did not sustain that result: RFS HR 0.90 (95% CI 0.72–1.12); overall survival remained immature.',
 'The updated evidence does not support routine adjuvant atezolizumab–bevacizumab. Trial participation remains an option.',
 'Continue surveillance and reassess recurrent disease through the standard pathway.','37871608 41580093')
add('hcc-tace-combination','hcc','combination','Systemic therapy combined with TACE','Selected multidisciplinary or trial consideration',
 'Embolization-eligible unresectable HCC with suitable liver reserve; review the specific regimen, current label and guideline position.',
 'EMERALD-1, LEAP-012 and EMERALD-3 reported progression-free survival benefit for their respective combinations. In EMERALD-3, STRIDE + lenvatinib + TACE yielded PFS 13.0 versus 9.8 months; overall-survival superiority was not established at the reported analysis.',
 'Regimens, comparators and follow-up differ. PFS benefit does not establish cure, transplant benefit or interchangeability. Combined treatment can increase serious toxicity.',
 'These trials do not validate routine checkpoint therapy as a transplant bridge. Review the transplant plan before treatment.','39798579 39798578 42636832')

add('btc-first','pcca icca','first','Gemcitabine + cisplatin + durvalumab or pembrolizumab','Preferred first-line options',
 'Unresectable or metastatic biliary cancer after addressing biliary obstruction, infection, renal function and performance status.',
 'TOPAZ-1: overall-survival HR 0.80 for durvalumab + chemotherapy versus chemotherapy. KEYNOTE-966: median overall survival 12.7 versus 10.9 months, HR 0.83, with pembrolizumab added.',
 'Mixed biliary-tract populations; neither trial establishes a separate pCCA-specific effect or superiority between these two checkpoint regimens.',
 'For potentially transplant-eligible pCCA or iCCA, obtain transplant-program review first. Palliative chemoimmunotherapy is not an interchangeable transplant neoadjuvant protocol.','38319896 37075781')
add('btc-chemo-only','pcca icca','first','Gemcitabine + cisplatin; adapt intensity when necessary','When checkpoint therapy is unsuitable',
 'Use chemotherapy alone when immunotherapy is unsuitable. Renal impairment, neuropathy, hearing loss or frailty may require a different platinum, regimen or single agent after oncology review.',
 'ABC-02 established cisplatin–gemcitabine over gemcitabine: median overall survival 11.7 versus 8.1 months; HR 0.64.',
 'Alternative platinum substitutions and dose reductions do not reproduce the exact ABC-02 evidence. Treat infection and improve drainage before reassessing fitness.',
 'An approved transplant regimen may use chemotherapy differently; confirm the protocol before starting treatment.','20375404')
add('btc-folfox','pcca icca','later','FOLFOX after gemcitabine–cisplatin','Evidence-based subsequent option',
 'Progression after gemcitabine–cisplatin, with adequate function and performance status; obtain molecular results before choosing the next treatment.',
 'ABC-06: FOLFOX + active symptom control versus active symptom control alone; median overall survival 6.2 versus 5.3 months, HR 0.69.',
 'Benefit was modest and toxicity substantial, including three treatment-related deaths. The trial preceded routine first-line chemoimmunotherapy.',
 'Persistent progression calls for reassessment of transplant candidacy and treatment goals.','33798493')
add('btc-adjuvant','pcca icca','perioperative','Capecitabine after resection','Usual adjuvant discussion',
 'Resected biliary cancer after recovery; discuss approximately six months of adjuvant treatment and margin-specific radiation considerations.',
 'BILCAP: primary intention-to-treat overall-survival comparison was not significant (HR 0.81; p=0.097); prespecified sensitivity and per-protocol analyses favored capecitabine. ASCOT supported S-1 in a Japanese population.',
 'Do not describe BILCAP as an unequivocally positive primary-endpoint trial. PRODIGE-12 and BCAT did not establish adjuvant GEMOX or gemcitabine benefit. S-1 applicability and access differ by region.',
 'Adjuvant treatment after resection and neoadjuvant treatment before transplant are separate settings.','30922733 36681415 30707660 29405274')
add('cca-fgfr','icca pcca','biomarker','FGFR2 fusion/rearrangement-directed therapy','Previously treated, biomarker-selected CCA',
 'Confirm an actionable FGFR2 fusion or rearrangement. Pemigatinib and lirafugratinib have CCA indications; futibatinib evidence and indication are specific to iCCA. Most evidence comes from iCCA.',
 'FIGHT-202 final: pemigatinib ORR 37.0%. FOENIX-CCA2: futibatinib ORR 42%. FDA approval of lirafugratinib in September 2026 was based on REFOCUS: ORR 46%, median response duration 11.8 months.',
 'Single-arm response studies do not establish a survival advantage or the preferred FGFR inhibitor. REFOCUS efficacy cohort was FGFR-inhibitor-naïve; sequence after an FGFR inhibitor needs separate evidence.',
 'Response may prompt reassessment of resectability or a study, but does not establish transplant eligibility.','32203698 38838500 36652354',[('FDA · lirafugratinib / REFOCUS','https://www.fda.gov/drugs/resources-information-approved-drugs/fda-approves-lirafugratinib-previously-treated-unresectable-locally-advanced-or-metastatic')])
add('cca-idh1','icca pcca','biomarker','Ivosidenib for IDH1-mutant CCA','Previously treated, biomarker-selected disease',
 'Confirmed susceptible IDH1 mutation after previous treatment; most enrolled tumors were intrahepatic.',
 'ClarIDHy: median PFS 2.7 versus 1.4 months, HR 0.37. Final unadjusted overall survival was 10.3 versus 7.5 months, HR 0.79, with extensive crossover.',
 'Primarily a disease-control strategy. Crossover-adjusted survival analyses require modeling assumptions; do not present them as the unadjusted randomized result.',
 'Continue multidisciplinary reassessment; a molecular response is not a transplant selection rule.','32416072 34554208')
add('btc-her2-braf','pcca icca','biomarker','HER2- or BRAF-directed treatment','Selected molecular options after prior treatment',
 'For HER2-positive disease, use the exact assay/label: zanidatamab requires IHC 3+ for its US indication. For BRAF V600E, consider dabrafenib + trametinib. Other HER2 options require agent-specific review.',
 'HERIZON-BTC-01 supports zanidatamab activity in previously treated HER2-positive biliary cancer. ROAR: investigator-assessed ORR 51% with dabrafenib + trametinib in 43 BRAF V600E-mutant biliary cancers.',
 'Single-arm cohorts; do not infer superiority over chemotherapy or assume all HER2 assay categories have the same activity. Confirm the current indication, cardiac status and relevant toxicities.',
 'Treat the confirmed molecular alteration while reviewing the separate surgical and transplant options.','41264278 32818466')
add('pcca-protocol','pcca','transplant','Protocol-directed chemoradiation before transplant','Transplant-team decision before treatment',
 'Patients meeting the center’s pCCA transplant protocol criteria. Protect diagnostic routes and confirm staging before beginning a palliative regimen.',
 'The established transplant strategy combines protocol-directed neoadjuvant treatment, operative staging and transplantation. The V7 review keeps alternative chemotherapy or SBRT regimens as separate proposals.',
 'Gemcitabine–cisplatin ± checkpoint therapy is not automatically a replacement for the established transplant regimen. Expanded size, biopsy-history and prior-node strata remain closed in the V7 proposal.',
 'Open the standard pCCA pathway; unresolved regimen questions go to the high-risk review.','', [('Standard pCCA transplant pathway','/mh-liver-pathways/transplant/pcca/'),('V7 regimen review and primary evidence','/mh-liver-pathways/transplant/high-risk/pcca/#pcca-b3')])
add('icca-response','icca','transplant','Systemic treatment followed by repeat surgical review','Response assessment; transplantation only through the appropriate pathway',
 'Initially unresectable iCCA. Reassess whether response permits complete resection; persistent unresectability alone does not establish transplant benefit.',
 'The V7 advanced-disease proposal uses sustained disease control and pure favorable-grade morphology, with one mass-forming focus ± adjacent satellites. Separate multifocal tumors are outside its initial cohort.',
 'This is a proposed study boundary, not a result established by a randomized transplant trial. Separate the small-cirrhotic NLRB route from advanced-disease studies.',
 'Review imaging distribution, histology and treatment history in the standard and high-risk pathways.','',[('Standard iCCA pathway','/mh-liver-pathways/transplant/icca/'),('V7 selection review and primary evidence','/mh-liver-pathways/transplant/high-risk/icca/#icca-b1')])

add('crlm-doublet','crlm','first','FOLFOX / CAPEOX or FOLFIRI + selected biologic','First-line metastatic treatment',
 'MSS/pMMR disease: use primary sidedness, RAS/BRAF status, fitness and the chance of conversion to resection. Left-sided RAS/BRAF wild-type tumors may favor an anti-EGFR doublet; bevacizumab-based therapy is another established approach.',
 'PARADIGM: left-sided RAS-wild-type disease had median OS 37.9 versus 34.3 months with panitumumab versus bevacizumab, both with mFOLFOX6. FIRE-3 and CALGB/SWOG 80405 provide complementary, differently designed comparisons.',
 'Anti-EGFR selection depends on molecular status and sidedness. Do not generalize a response-rate advantage to all primary sites or automatically add cetuximab around resection.',
 'Map lesions before treatment and reassess resectability repeatedly. Systemic response alone does not establish a transplant indication.','37071094 27575024 28632865')
add('crlm-conversion','crlm','combination','Selected triplet chemotherapy for conversion','For fit patients with initially unresectable liver disease',
 'A more intensive regimen may be appropriate when substantial shrinkage could permit complete local treatment. Review by an experienced liver multidisciplinary team is essential.',
 'CAIRO5: FOLFOXIRI–bevacizumab improved PFS over doublet–bevacizumab in its right-sided or RAS/BRAF-mutant group (10.6 versus 9.0 months; HR 0.76), with greater toxicity. TRICE studied cetuximab with triplet versus doublet chemotherapy in RAS/BRAF-wild-type CRLM.',
 'Do not prescribe triplet therapy for every patient or extrapolate one molecular/sidedness group to another. Response, conversion and survival are different endpoints.',
 'Confirm persistent unresectability after reviewing resection, ablation and selected HAI conversion options before transplant review.','37329889 38728364')
add('crlm-msi','crlm','biomarker','Pembrolizumab or nivolumab + ipilimumab','MSI-H / dMMR metastatic colorectal cancer',
 'Confirm mismatch-repair deficiency or microsatellite instability before treatment.',
 'KEYNOTE-177: pembrolizumab PFS 16.5 versus 8.2 months with chemotherapy. CheckMate 8HW established first-line PFS benefit of nivolumab–ipilimumab versus chemotherapy; its separate comparison versus nivolumab alone also favored the combination (HR 0.62).',
 'These are not head-to-head pembrolizumab versus nivolumab–ipilimumab data. Dual therapy increased grade 3–4 treatment-related toxicity versus nivolumab alone.',
 'Effective immunotherapy is a major competing option. MSI-H/dMMR expansion is closed in the initial V7 CRLM transplant proposal.','33264544 39602630 39874977')
add('crlm-braf','crlm','biomarker','Encorafenib + cetuximab + fluorouracil-based chemotherapy','BRAF V600E-mutant metastatic disease',
 'Confirm BRAF V600E. BREAKWATER supports first-line encorafenib–cetuximab with chemotherapy; the February 2026 FDA indication includes mFOLFOX6 or FOLFIRI.',
 'BREAKWATER: encorafenib–cetuximab + mFOLFOX6 improved PFS (12.8 versus 7.1 months) and OS (30.3 versus 15.1 months) over standard care. BEACON established encorafenib–cetuximab-based treatment after prior therapy.',
 'A first-line chemotherapy-containing regimen and later-line targeted doublet are different settings. Do not switch between them without considering prior treatment.',
 'BRAF-mutant expansion remains closed in the initial V7 CRLM transplant proposal; response does not remove that boundary.','40444708 31566309',[('FDA · 2026 BREAKWATER indication','https://www.fda.gov/drugs/resources-information-approved-drugs/fda-grants-traditional-approval-encorafenib-metastatic-colorectal-cancer-braf-v600e-mutation')])
add('crlm-other-targets','crlm','biomarker','HER2 or KRAS G12C-directed combinations','After appropriate prior therapy',
 'HER2-positive, RAS-wild-type disease: tucatinib + trastuzumab. KRAS G12C: sotorasib + panitumumab or adagrasib + cetuximab, subject to the agent’s prior-treatment indication.',
 'MOUNTAINEER: ORR 38.1% in its combination cohorts. CodeBreaK 300: PFS 5.6 versus 2.2 months with the approved-dose sotorasib combination versus standard care. KRYSTAL-1: adagrasib–cetuximab ORR 34% in 94 patients.',
 'MOUNTAINEER and KRYSTAL-1 do not establish randomized survival superiority. Do not compare their response rates across different molecular groups.',
 'Review the full tumor biology and donor/allocation requirements separately from the treatment response.','37142372 37870968 38587856')
add('crlm-later','crlm','later','Change chemotherapy backbone or use a matched targeted option','After progression',
 'After oxaliplatin, consider an irinotecan-based regimen; after irinotecan, consider oxaliplatin if suitable. Select anti-VEGF or anti-EGFR treatment according to prior exposure, biomarkers, sidedness and tolerance.',
 'NCCN Colon Cancer v2.2026, original PDF pages 46–51, organizes subsequent treatment by previous agents and molecular profile.',
 'There is no universal second-line regimen. Rechallenge requires a specific rationale; cumulative neuropathy, marrow reserve, liver injury and progression pattern matter.',
 'Reassess local treatment when complete clearance becomes feasible; do not postpone an achievable resection solely to continue chemotherapy.','',[('NCCN Colon Cancer','https://www.nccn.org/professionals/physician_gls/pdf/colon.pdf')])
add('crlm-refractory','crlm','later','Trifluridine–tipiracil + bevacizumab; fruquintinib or regorafenib','Later-line options when treatment remains appropriate',
 'Disease progressing after relevant standard chemotherapy and biomarker-directed options; select according to performance status and toxicity.',
 'SUNLIGHT: OS 10.8 versus 7.5 months for trifluridine–tipiracil + bevacizumab versus trifluridine–tipiracil alone. FRESCO-2 and CORRECT demonstrated survival benefit of fruquintinib and regorafenib, respectively, versus placebo.',
 'Different prior-treatment populations and comparators; these numbers do not rank the options. RECOURSE supports trifluridine–tipiracil alone when combination treatment is unsuitable.',
 'If further treatment offers little benefit or is declined, agree best supportive care and symptom management.','37133585 37331369 23177514 25970050')
add('crlm-periop','crlm','perioperative','Perioperative chemotherapy around liver resection','Individualize with the liver multidisciplinary team',
 'Resectable CRLM: balance recurrence risk, prior treatment, liver injury and surgical timing. Surgery-first or perioperative chemotherapy may be appropriate.',
 'EORTC 40983 showed PFS signals in eligible/resected analyses; its intention-to-treat PFS comparison and long-term OS comparison were not significant. New EPOC found worse OS when cetuximab was added to perioperative chemotherapy.',
 'Do not use metastatic anti-EGFR response data to justify routine perioperative cetuximab for resectable CRLM. Exploratory molecular subtypes from New EPOC are not validated selectors for transplantation.',
 'Resectability is reviewed before a transplant route. Radiographic disappearance alone does not prove eradication.','18358928 24120480 24717919 32014119 37471075')

add('net-ssa','nelm','first','Octreotide LAR or lanreotide','Indolent, well-differentiated, usually SSTR-positive NET',
 'Choose according to primary site, somatostatin-receptor status, growth and hormone symptoms. Selected asymptomatic, low-burden stable disease may be observed.',
 'PROMID: time to progression 14.3 versus 6 months with octreotide versus placebo in midgut NET. CLARINET established PFS benefit with lanreotide in nonfunctional enteropancreatic NET, Ki-67 <10%.',
 'These trials chiefly demonstrate tumor control, not cure or a proven overall-survival advantage. Functional tumors may need ongoing hormonal treatment even when another antitumor treatment is added.',
 'Stable low-burden disease may have greater benefit from continued nontransplant care than immediate transplantation.','19704057 25014687')
add('net-prrt','nelm','later','177Lu-DOTATATE peptide receptor radionuclide therapy','Progressive SSTR-positive, well-differentiated disease',
 'Confirm adequate receptor uptake, renal function and marrow reserve. NETTER-1 directly studied progressive midgut NET despite a somatostatin analogue.',
 'NETTER-1: 20-month PFS 65.2% versus 10.8% with high-dose octreotide. Final median OS 48.0 versus 36.3 months was not statistically significant (HR 0.84; p=0.30).',
 'Long-term risks include marrow toxicity and uncommon myelodysplasia/leukemia. Primary site and prior therapy affect applicability.',
 'Record disease control and treatment toxicity before any transplant benefit review. PRRT response does not expand accepted grade or spread criteria.','28076709 34793718')
add('net-prrt-first','nelm','first','First-line PRRT for selected higher-grade NET','Well-differentiated G2/G3, SSTR-positive GEP-NET',
 'NETTER-2 population: newly diagnosed advanced, well-differentiated GEP-NET, Ki-67 10–55%, with suitable somatostatin-receptor expression.',
 'NETTER-2: median PFS 22.8 versus 8.5 months with 177Lu-DOTATATE + octreotide versus high-dose octreotide; HR 0.276. The 2026 subgroup report supports activity across pancreatic/GI origin and G2/G3 subsets.',
 'Comparator was high-dose octreotide, not CAPTEM or another chemotherapy regimen. This does not apply to poorly differentiated NEC.',
 'G3 treatment activity does not make G3 disease eligible for the initial V7 NET transplant cohort.','38851203 42604001')
add('net-captem','nelm','first','Capecitabine + temozolomide (CAPTEM)','Particularly for pancreatic NET when shrinkage matters',
 'Advanced well-differentiated pancreatic NET, especially progressive, bulky or symptomatic disease. Decide sequence alongside PRRT and targeted agents.',
 'E2211 randomized phase II: median PFS 22.7 versus 14.4 months with CAPTEM versus temozolomide at the scheduled interim analysis; final OS was not significantly different.',
 'Do not generalize pancreatic NET data to all small-bowel NET or poorly differentiated NEC. Review marrow reserve, infection risk and fluoropyrimidine safety.',
 'Tumor control can inform a transplant assessment, but selection still requires favorable grade, distribution and expected benefit.','36260828')
add('net-targeted','nelm','later','Everolimus or sunitinib','Progressive disease; primary site determines the option',
 'Everolimus: pancreatic NET or appropriate nonfunctional GI/lung NET. Sunitinib: pancreatic NET.',
 'RADIANT-3: PFS 11.0 versus 4.6 months in pancreatic NET. RADIANT-4: PFS 11.0 versus 3.9 months in nonfunctional GI/lung NET. Sunitinib trial: PFS 11.4 versus 5.5 months in pancreatic NET.',
 'Trials used placebo comparators, not contemporary PRRT/CAPTEM sequencing. Monitor infection/pneumonitis/metabolic toxicity with everolimus and vascular/cardiac toxicity with sunitinib.',
 'The efficacy of nontransplant options must be considered before exposing a recipient and donor to transplantation.','21306238 26703889 21306237')
add('net-cabo','nelm','later','Cabozantinib','Previously treated, progressive well-differentiated NET',
 'Pancreatic or extrapancreatic NET after appropriate prior treatment.',
 'CABINET: median PFS 13.8 versus 4.4 months in pancreatic NET and 8.4 versus 3.9 months in extrapancreatic NET, each compared with placebo.',
 'The two cohorts are distinct; do not pool their effect sizes. Toxicity and dose reductions are common. PFS benefit does not establish an OS advantage.',
 'An additional effective nontransplant option changes the benefit discussion, not the transplant criteria.','39282913')
add('net-emerging','nelm','combination','PRRT sequencing: OCLURANDOM and COMPETE','Evidence informing discussion; check product availability',
 'OCLURANDOM: pretreated progressive SSTR-positive pancreatic NET. COMPETE: progressive SSTR-positive G1/G2 GEP-NET.',
 'OCLURANDOM was a randomized noncomparative phase II trial of 177Lu-DOTATATE with an internal sunitinib control. COMPETE phase III found PFS 23.9 versus 14.1 months with 177Lu-edotreotide versus everolimus (HR 0.67).',
 'OCLURANDOM does not establish phase III superiority. Edotreotide and DOTATATE are different products; the COMPETE result alone does not establish US authorization or interchangeability.',
 'Use these results when comparing alternatives to transplantation; they are not transplant outcome studies.','42225102 42392118')
add('net-nec','nelm','first','Platinum + etoposide or irinotecan for poorly differentiated NEC','A separate disease pathway',
 'Digestive-system poorly differentiated neuroendocrine carcinoma requires pathology confirmation and a NEC treatment plan. It is different from well-differentiated G3 NET.',
 'TOPIC-NEC: cisplatin–etoposide versus cisplatin–irinotecan did not differ significantly in OS (12.5 versus 10.9 months; HR 1.04).',
 'Toxicity differed, including more myelosuppression with etoposide. Do not apply SSA/PRRT evidence from well-differentiated NET automatically to NEC.',
 'Poorly differentiated NEC is outside the NET transplant pathway.','35980649')

SAFETY=[
 ('Checkpoint inhibitors','Review solid-organ transplant history, unresolved immune toxicity, significant autoimmune disease, immunosuppression and infection. These are different clinical situations; obtain oncology/transplant input rather than treating them as one blanket label contraindication.','After liver transplantation, rejection and graft loss are major concerns. Before transplantation, no washout interval guarantees safety.', [('HCC immunotherapy / transplant review','/mh-liver-pathways/transplant/high-risk/hcc/#hcc-b3')]),
 ('VEGF antibodies and VEGFR inhibitors','Avoid or delay when uncontrolled serious bleeding, unhealed major wounds, uncontrolled hypertension or relevant vascular complications make treatment unsafe. Check proteinuria and agent-specific hepatic/cardiac risks.','Coordinate surgery and agent-specific interruption intervals. HCC with portal hypertension needs particular attention to varices.', [('Bevacizumab prescribing information','https://www.gene.com/download/pdf/avastin_prescribing.pdf')]),
 ('Fluorouracil / capecitabine','FDA labeling recommends DPYD testing before treatment unless immediate treatment is necessary. Avoid in known complete DPD deficiency; individualize treatment in partial deficiency. Review renal function for capecitabine, marrow reserve, severe diarrhea/mucositis and prior cardiac toxicity.','Relevant to FOLFOX, FOLFIRI, CAPEOX, CAPTEM and fluoropyrimidine chemoradiation.', [('FDA · DPYD safety labeling, 2026','https://www.fda.gov/drugs/resources-information-approved-drugs/safety-labeling-update-capecitabine-and-fluorouracil-5-fu-risks-associated-dihydropyrimidine')]),
 ('Platinum agents / irinotecan / cytotoxic combinations','Correct active infection and major organ dysfunction before treatment. Cisplatin: renal function, hearing and neuropathy. Oxaliplatin: neuropathy and hepatic sinusoidal injury. Irinotecan: bilirubin, severe diarrhea and UGT1A1-related toxicity risk.','Review cumulative chemotherapy-associated liver injury and functional remnant before liver surgery.', [('NCCN Colon Cancer','https://www.nccn.org/professionals/physician_gls/pdf/colon.pdf'),('NCCN Biliary Tract Cancers','https://www.nccn.org/professionals/physician_gls/pdf/btc.pdf')]),
 ('Biomarker-directed agents','Confirm the exact alteration and assay required for the agent. FGFR inhibitors: eye examination and phosphate monitoring. HER2 agents: cardiac assessment; trastuzumab deruxtecan also requires pneumonitis vigilance. Ivosidenib: QT interval and interactions.','A negative or nonspecific molecular result is not an indication for empirical targeted treatment.', [('FDA · lirafugratinib safety and indication','https://www.fda.gov/drugs/resources-information-approved-drugs/fda-approves-lirafugratinib-previously-treated-unresectable-locally-advanced-or-metastatic')]),
 ('177Lu-DOTATATE PRRT','Requires suitable somatostatin-receptor expression, renal function and marrow reserve. Review pregnancy, prior marrow-toxic treatment, blood counts and the ability to receive renal-protective amino acids.','Assess cumulative radiation and marrow toxicity when sequencing with alkylating chemotherapy.', [('NETTER-1','https://pubmed.ncbi.nlm.nih.gov/28076709/'),('Long-term safety','https://pubmed.ncbi.nlm.nih.gov/34793718/')]),
 ('Everolimus / somatostatin analogues / temozolomide','Everolimus: infection, pneumonitis, glucose control and interactions. Somatostatin analogues: gallbladder, glucose and bradycardia concerns. Temozolomide/CAPTEM: marrow suppression, infection risk and cumulative exposure.','Choose according to tumor grade, primary site, hormonal symptoms and growth rate.', [('NCCN Neuroendocrine and Adrenal Tumors','https://www.nccn.org/professionals/physician_gls/pdf/neuroendocrine.pdf')]),
]
GUIDELINES=[
 ('HCC','NCCN Hepatocellular Carcinoma v2.2026 (14 August 2026)','Original PDF pages 27–28: systemic therapy; page 12: treatment and supportive care.','https://www.nccn.org/professionals/physician_gls/pdf/hcc.pdf'),
 ('pCCA / iCCA','NCCN Biliary Tract Cancers v1.2026 (10 March 2026)','Original PDF pages 36–38: adjuvant, advanced and biomarker-directed systemic treatment.','https://www.nccn.org/professionals/physician_gls/pdf/btc.pdf'),
 ('CRLM','NCCN Colon Cancer v2.2026 (7 April 2026)','Original PDF pages 46–51: treatment sequence and molecular subgroups.','https://www.nccn.org/professionals/physician_gls/pdf/colon.pdf'),
 ('NELM','NCCN Neuroendocrine and Adrenal Tumors v1.2026 (21 April 2026)','Original PDF pages 104–109: systemic options by primary site and disease features; pages 28 and 32: metastatic GI NET management.','https://www.nccn.org/professionals/physician_gls/pdf/neuroendocrine.pdf'),
]
