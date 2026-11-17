"""Explicit study-arm placement for the treatment × treatment presentation.

This is a display index, not a network meta-analysis. Never derive pairs from
modality tags: add-on studies and multigroup cohorts require explicit arms.
Brief results abbreviate already reviewed text; full results remain attached.
"""

MODES = {'direct':'Treatment vs treatment', 'combined':'Combination / add-on', 'technique':'Technique / dose'}
ARMS = {
 'abl':'Thermal ablation', 'sbrt':'SBRT / EBRT', 'y90':'Y-90 (TARE)',
 'tace':'TACE / TAE', 'hai':'HAI / HAIC', 'htx':'Histotripsy',
 'resection':'Resection', 'lt':'Transplant', 'systemic':'Systemic therapy',
 'supportive':'Supportive care', 'nonlt':'Non-transplant care',
 'tace_abl':'TACE + ablation', 'hai_abl':'HAIC + ablation',
 'hai_sys':'HAI / HAIC + systemic', 'sbrt_sys':'SBRT + systemic',
 'tace_rt':'TACE + EBRT', 'tace_sys':'TACE + systemic',
 'y90_sys':'Y-90 + systemic', 'y90_hai':'Y-90 + HAI',
 'abl_sys':'Ablation ± resection + systemic',
 'rt_surgery':'Radiotherapy → resection', 'embol_surgery':'Embolization → resection',
 'surgery_hai':'Resection + perioperative HAI', 'surgery_tace':'Resection + adjuvant TACE',
 'surgery_nohai':'Resection without HAI', 'surgery_observe':'Resection → observation',
 'sabr_care':'SABR + standard care', 'standard_care':'Standard care',
 'hai_mixed':'Pump HAI ± systemic', 'drain_hai':'Drainage + HAIC',
 'drain_support':'Drainage + supportive care', 'nat_rt':'RT-containing neoadjuvant therapy',
 'nat_gemcis':'GemCis neoadjuvant therapy', 'lt_crt':'Chemoradiation → transplant',
 'lt_nocrt':'Transplant without chemoradiation', 'gemcis_sbrt':'GemCis → SBRT',
 'gemcis':'Continued GemCis', 'mwa':'MWA', 'rfa':'RFA',
 'personal_y90':'Personalized Y-90 dosimetry', 'standard_y90':'Standard Y-90 dosimetry',
 'high_rt':'Higher radiation dose', 'low_rt':'Lower radiation dose',
 'ctace':'Conventional TACE', 'debtace':'DEB-TACE', 'tae':'Bland embolization',
 'stent_radio':'Radioactive stent + HAIC', 'stent_plain':'Conventional stent + HAIC',
}

# Each tuple: PMID (or report id suffix), mode, row treatment, column treatment,
# concise endpoint, essential qualification. Numeric order follows the study's
# displayed arm line, NEVER an inferred ordering of matrix axes.
SPECS = [
('25957784', 'combined', 'tace_sys', 'tace', 'Progression: 7 per arm. TTP HR 1.11 (0.39–3.16).', 'Small waitlist RCT. Severe treatment-related events 50% vs 16%.'),
('24681342', 'combined', 'y90_sys', 'y90', 'Transplanted 8/10 vs 9/10. Biliary complications within 30 days occurred in 4/8 vs 0/9 recipients.', 'Safety pilot, 23 randomized and 20 treated. All 10 sorafenib patients required dose reduction.'),
('35158918', 'combined', 'tace_sys', 'tace', 'Mean explant necrosis 69.6% vs 43.8%.', 'Recipient subgroup, 12 vs 24. Milan classification included explant findings.'),
('42421575', 'combined', 'tace_sys', 'tace', 'Imaging response 33.3% vs 16.7%.', 'Matched recipients, 60 per arm. Waitlist dropout unmeasured.'),

('16495695','direct','abl','resection','4-y OS 65.9% vs 64.0%; no significant difference.','RCT; crossover; not equivalence.'),
('29503247','technique','mwa','rfa','2-y local progression 6% vs 12% (P=.27).','Per-lesion analysis; superiority not shown.'),
('31774468','direct','resection','abl','5-y OS 43.6% vs 38.5% (P=.17).','Recurrent HCC; primary endpoint negative.'),
('29091283','direct','resection','abl','10-y OS 47.6% vs 41.8% (P=.531).','RCT; superiority not shown.'),
('35949295', 'direct', 'resection', 'abl', 'Median RFS 3.46 vs 3.04 years (P=.58).', 'Final RFS report. Enrollment was slow. Conditional power <8% was calculated after enrollment stopped.'),
('40554738','direct','resection','abl','5-y OS 74.6% vs 70.4% (P=.84).','SURF final; not proven equivalence.'),
('26628466','direct','sbrt','abl','Better freedom from local progression with SBRT for tumors ≥2 cm.','Retrospective; treatment selection differed.'),
('39693584','direct','sbrt','abl','2-y local PFS 92.7% vs 75.8%; HR 0.45.','Recurrent HCC; no significant OS difference.'),
('33230652','direct','y90','abl','Mean target PFS 57.8 vs 38.6 mo; OS difference NS.','Matched cohort; means, not medians.'),
('42434250','direct','y90','abl','PFS HR 0.56 (0.20–1.51); OS HR 1.38 (0.30–6.34).','Retrospective; wide CIs.'),
('27930089','combined','y90','tace_abl','No significant CR, progression or OS difference.','Matched cohort; comparator includes MWA.'),
('35346857', 'direct', 'y90', 'resection', 'Time to any progression 21.9 months after Y90 vs 29.4 after resection (P=.03). Adjusted HR 1.16 (0.51–2.63).', 'Retrospective cohort. Liver reserve and surgical candidacy differed.'),
('36100064','combined','y90','tace_abl','Disease control 94.7% vs 100%; sessions 1.3 vs 1.9.','Retrospective; no significant OS/PFS difference.'),
('32615109', 'direct', 'lt', 'nonlt', 'Five-year OS 77.5% vs 31.2%, HR 0.32 (0.11–0.92).', 'Corrected full report. 45 randomized downstaging responders. Trial closed early.'),
('42379392','combined','y90','tace_abl','Mean explant necrosis 83.6% vs 79.0% (P=.484).','Recipients only; no dropout estimate.'),
('19552767','direct','y90','tace','Downstaging: 25/43 (58%) vs 11/35 (31%).','Retrospective; 8 TACE scans missing; older criteria.'),
('28668402','direct','y90','tace','Recurrence 9% vs 8%; OS/RFS differences NS.','Recipients only; excludes waitlist dropout.'),
('34331914','direct','y90','tace','No significant difference in downstaging.','Nonrandom treatment; not equivalence.'),
('35619164','direct','y90','tace','Recurrence 23% vs 11% (P=.1224).','Recipients only; baseline burden differed.'),
('39808828', 'direct', 'y90', 'tace', 'Two-year downstaging (Y90 vs TACE): 73.8% vs 64.6% beyond UNOS-DS, 78.1% vs 86.5% within UNOS-DS.', 'Prospective cohort. First LRT type did not predict success after stratification by center (P=.07).'),
('41056563','direct','y90','tace','Dropout sHR 0.83 (0.74–0.93); OS aHR 0.94 (0.85–1.03).','Observational; overlapping OPTN cohorts.'),
('41580092','direct','y90','tace','2-y dropout 14.2% vs 19.0%; cause-specific HR 0.78.','IPTW registry cohort; residual confounding.'),
('29631810','combined','hai_sys','systemic','OS 11.8 vs 11.5 mo; HR 1.009 (0.743–1.371).','SILIUS: no OS benefit; more toxicity.'),
('34648352','direct','hai','tace','OS 23.1 vs 16.1 mo; resection conversion 24% vs 12%.','RCT; no macrovascular invasion; mostly HBV.'),
('34905388', 'direct', 'hai', 'systemic', 'OS 13.9 vs 8.2 months, HR 0.408 (0.301–0.552).', 'HBV infection in 89% overall and 92% of the HAIC arm. Single-center trial with sorafenib.'),
('37037359','direct','sbrt','tace','TTP difference NS; local-control signal post hoc.','TRENDY: 30 patients; underpowered.'),
('36421345','direct','sbrt','tace','Local control favored SBRT over repeat embolization.','40 patients; most controls had bland TAE.'),
('11981766','direct','tace','supportive','TACE improved survival over symptomatic treatment.','RCT; selected, mostly HBV population.'),
('12049862','direct','tace','supportive','TACE vs supportive care: OS HR 0.47.','Three-arm RCT; estimate is for TACE only.'),
('25373796','direct','y90','tace','PFS 180 vs 216 d; OS 592 vs 788 d; both NS.','Pilot RCT; older dosimetry.'),
('35258371','direct','y90','tace','TTP 17.1 vs 9.5 mo; OS 30.2 vs 15.6 mo.','TRACE RCT; stopped early at 72 patients.'),
('25443863','direct','y90','tace','Disease control 76.9% vs 73.3%; QoL difference NS.','SIRTACE pilot; not survival equivalence.'),
('27575820','direct','y90','tace','TTP >26 vs 6.8 mo; OS 18.6 vs 17.7 mo (NS).','PREMIERE RCT; 45 patients; 12 TTP events.'),
('27284477','direct','y90','sbrt','OS HR 0.72 (0.49–1.07); difference NS.','Registry; historical radiation coding.'),
('29107679','direct','y90','systemic','OS 8.0 vs 9.9 mo; HR 1.15 (0.94–1.41).','SARAH RCT; 22% of Y-90 arm untreated.'),
('29498924', 'direct', 'y90', 'systemic', 'ITT OS 8.8 vs 10.0 months, HR 1.12 (0.9–1.4). ITT response 16.5% vs 1.7% (P<.001).', 'SIRveNIB. Higher response did not translate into longer survival.'),
('33687130', 'combined', 'hai_abl', 'abl', 'Three-year RFS 54.3% vs 34.3% (P=.094).', 'Primary RFS result was inconclusive. Distant intrahepatic recurrence was examined post hoc.'),
('31070690','combined','hai_sys','systemic','OS 13.4 vs 7.1 mo.','RCT; 80.6% Vp3/4 invasion; sorafenib control.'),
('35993224','combined','hai_abl','hai','2-y OS 74.3% vs 27.7%.','Selected responders; tests adding ablation.'),
('39699905', 'combined', 'sbrt_sys', 'systemic', 'OS 15.8 vs 12.3 months, primary P=.06. PFS 9.2 vs 5.5 months.', 'Original 368 at 85% power. Amended 292 at 80%. Early closure: 177 analyzed at 65% power.'),
('29543938','combined','tace_rt','systemic','12-wk PFS 86.7% vs 34.3%; OS 55 vs 43 wk.','RCT; high control-arm crossover.'),
('23269991','combined','tace_abl','abl','4-y OS 61.8% vs 45.0%; OS HR 0.525.','Single-center RCT; changed sample size.'),
('39798579', 'combined', 'tace_sys', 'tace', 'Add-on PFS 15.0 vs 8.2 months (HR 0.77). Final OS 29.9 vs 33.3 months (HR 1.10, 95% CI 0.87–1.39).', 'EMERALD-1. PFS from the randomized trial publication. OS from ESMO GI 2026 abstract 183O.'),
('39798578', 'combined', 'tace_sys', 'tace', 'Add-on PFS 14.6 vs 10.0 months (HR 0.66). Long-term OS 40.4 vs 40.8 months (HR 0.98, 95% CI 0.76–1.26).', 'LEAP-012. Published primary PFS. Long-term OS from ESMO 2026 abstract 1678RO and the trial registry.'),
('31421157','combined','y90_sys','systemic','No OS benefit from adding Y-90 to sorafenib.','SORAMIC; major treatment noncompletion.'),
('36525610','combined','surgery_hai','surgery_observe','DFS 20.3 vs 10.0 mo; OS difference NS.','Adjuvant HAIC-FOLFOX; detection asymmetry.'),
('29420221','combined','surgery_tace','surgery_observe','3-y OS 85.2% vs 77.4%; RFS favored adjuvant TACE.','HBV RCT; does not establish routine adjuvant use.'),
('37328589','combined','embol_surgery','resection','Lower in-hospital mortality; better 1-/3-y OS.','Ruptured HCC; nonrandomized meta-analysis.'),
('38488934','direct','sbrt','tace','No PFS or OS difference after resection.','Postoperative RCT; no surgery-alone arm.'),
('31283409', 'combined', 'rt_surgery', 'resection', 'Two-year tumor-related survival 27.4% vs 9.4% (P<.001). Adjusted HCC-death HR 0.35 (0.23–0.54).', 'Preoperative 3D-CRT in resectable Cheng II/III PVTT. One hospital enrolled 96%. No SBRT arm.'),
('33166497', 'technique', 'personal_y90', 'standard_y90', 'Index-lesion response at 3 months: 71% vs 36% by investigator. Masked central assessment: 79% vs 43% (P=.0062).', 'Phase 2, 60 patients, index-lesion response. Early stop and subsequent resections complicate OS.'),
('39245060','direct','sbrt','supportive','Pain response 67% vs 22%.','Whole-liver 8 Gy; mixed hepatic cancers; not OS.'),
('41528222', 'direct', 'abl', 'resection', 'MWA vs repeat resection: OS 29.8 vs 34.0 and DFS 10.7 vs 14.8 months.', 'HRs compare repeat resection to MWA: OS 0.89, DFS 0.78. Observational study.'),
('38261915', 'direct', 'abl', 'resection', 'Five-year OS 44.8% vs 40.4%. Median DFS 1.7 vs 3.6 years.', 'Matched cohort within Milan: one tumor ≤5 cm or up to three, each ≤3 cm. DFS favored resection.'),
('26695839','combined','hai_sys','systemic','OS 30.8 vs 18.4 mo; PFS difference NS.','Nonrandomized; unadjusted OS.'),
('33868997','direct','hai','tace','1-y OS 60.2% vs 42.9%; 2-y OS 38.7% vs 29.4%.','Retrospective; catheter HAIC, not pump FUDR.'),
('40216615','direct','hai','tace','OS 10.3 vs 5.1 mo vs cTACE; DEB-TACE contrast NS.','Retrospective; 24 HAIC patients.'),
('35544131', 'direct', 'hai', 'resection', 'Median OS 20.3 vs 18.9 months, adjusted HR 0.75 (0.55–1.03).', 'All patients had multifocal iCCA. Bilobar disease and ≥4 lesions were more frequent with HAIP.'),
('37814188','combined','hai_mixed','systemic','OS 27.7 vs 11.8 mo.','Cross-center cohort; most HAI also received systemic.'),
('30191056','direct','y90','tace','Disease control 12/25 (48%) vs 7/15 (47%).','Small cohort; survival not assessed.'),
('26503201','technique','high_rt','low_rt','3-y OS 73% vs 38%; local control 78% vs 45%.','Retrospective; only 19 high-dose patients.'),
('39936132','combined','nat_gemcis','nat_rt','No significant OS or explant-response difference.','Recipients only; small nonrandom groups.'),
('37032423', 'combined', 'lt_crt', 'lt_nocrt', 'Recurrence HR 0.30. Five-year OS 41% vs 53% (NS).', 'Table 3: all major vascular complications 11/27 vs 3/22, including hepatic artery complications 9/27 vs 2/22.'),
('42433279','combined','drain_hai','drain_support','OS 17.63 vs 6.10 mo.','Nonrandomized; investigational; not transplant bridging.'),
('abstract-ABC-07-randomized-phase-II','combined','gemcis_sbrt','gemcis','PFS 8.6 vs 9.0 mo; HR 1.00; OS difference NS.','Conference results; 84% perihilar.'),
('39311927', 'technique', 'stent_radio', 'stent_plain', 'Median OS 10.2 vs 6.7 months, HR 0.53 (0.36–0.79), P=.002.', 'Both arms received HAIC. The stent comparison enrolled unresectable Bismuth III/IV pCCA.'),
('42829779','direct','abl','sbrt','1-y freedom from local progression 77.7% vs 83.0% (P=.70).','LAVA-CRLM RCT; no noninferiority conclusion.'),
('30982687','combined','sabr_care','standard_care','OS 41 vs 28 mo (P=.09; phase II α=.20).','Mixed primaries/sites; not a CRLM-specific result.'),
('32484754','combined','sabr_care','standard_care','OS 50 vs 28 mo; HR 0.47 (0.27–0.81).','SABR-COMET follow-up; mixed primaries/sites.'),
('39848272', 'direct', 'abl', 'resection', 'OS HR 1.05 (0.69–1.58). Adverse events 19% vs 46%.', 'Early-stop NI trial. Both treatments used in 18% assigned ablation and 35% assigned resection (Table 1).'),
('31177151','direct','tace','y90','OS HR 0.94 (0.54–1.65); no significant difference.','Matched cohort; not equivalence.'),
('22493375', 'direct', 'tace', 'systemic', 'OS 22 vs 15 months and PFS 7 vs 4 months.', 'Small randomized trial with concurrent FOLFIRI limited to four months.'),
('16505413','direct','hai','systemic','OS 24.4 vs 20.0 mo (P=.0034).','CALGB RCT; superseded bolus FU/LV control.'),
('29181682','direct','hai','y90','OS 31.2 vs 16.3 mo from unresectable diagnosis.','Retrospective; from stage IV diagnosis, OS difference NS.'),
('40709764','direct','hai','y90','Y-90 vs HAI mortality HR 1.46 / 1.96 / 0.88 after 1 / 2 / 3–4 lines.','Matched cohorts; treatment and center confounded.'),
('41118066','combined','hai_sys','systemic','Conversion 7/11 vs 2/9 (P=.09); PFS 12.6 vs 4.37 mo.','SULTAN; 20 patients; conversion endpoint NS.'),
('28376151','combined','abl_sys','systemic','8-y OS 35.9% vs 8.9%; OS HR 0.58.','CLOCC phase II; OS was secondary.'),
('28781171','combined','y90_sys','systemic','OS 22.6 vs 23.3 mo; HR 1.04 (0.90–1.19).','FOXFIRE pooled RCTs; no OS benefit.'),
('11843249', 'combined', 'y90_hai', 'hai', 'Tumor-volume response 50% vs 24%. Liver progression was delayed.', 'The study closed early and shifted from survival to response and progression. OS benefit was not established.'),
('20567019','combined','y90_sys','systemic','Liver TTP 5.5 vs 2.1 mo; OS difference NS.','Small RCT; control crossover.'),
('34541864','combined','y90_sys','systemic','PFS 8.0 vs 7.2 mo; OS 14.0 vs 14.4 mo (NS).','EPOCH; more grade ≥3 toxicity.'),
('abstract-Dutch-PUMP','combined','surgery_hai','surgery_nohai','PFS HR 0.88 (0.62–1.25); OS immature.','Conference results; no adjuvant systemic therapy.'),
('42018958','combined','hai_sys','systemic','Hepatic RFS 25 vs 12 mo; OS HR 0.61 (0.33–1.12).','Adjuvant oxaliplatin route; both arms IV LV5FU2.'),
('10615075', 'combined', 'hai_sys', 'systemic', 'Two-year co-primary OS 86% vs 72% (P=.03) and all-site PFS 57% vs 42% (P=.07).', 'Full OS curves P=.21. Secondary hepatic PFS 90% vs 60% (P<.001).'),
('39644535', 'combined', 'hai_sys', 'systemic', 'Three-year RFS 31.4% vs 34.4% (P=.28).', 'HARVEST. Allocation moved to after resection following the first 11 patients. FUDR shortage closed enrollment.'),
('28426374', 'combined', 'surgery_hai', 'surgery_nohai', 'Median OS 67 vs 44 months, propensity-adjusted HR 0.67 (0.59–0.76).', 'Single center. Propensity covariates listed, coefficients unreported. Residual confounding possible.'),
('abstract-RETNET-RCT','technique','tae','ctace','Hepatic PFS difference not significant.','Conference results; PMID opens protocol, not results.'),
('16134179', 'technique', 'tae', 'ctace', 'Carcinoid response 81.0% with bland embolization vs 44.4% with chemoembolization (adjusted OR 6.41).', 'Retrospective. Islet-cell response 25% vs 50% (P=.06). No survival advantage was established.'),
('32032719', 'direct', 'y90', 'tace', 'Initial disease control 83% after Y90 vs 96% after TACE (P<.01). OS and PFS differences were nonsignificant.', 'Retrospective cohort. The association was confined to disease control.'),
('29167951','direct','y90','tace','3-mo response 0/6 vs 5/5; 6-mo 2/6 vs 4/5.','Y-90 vs bland TAE; 11 patients; no survival comparison.'),
('42006283','direct','y90','tace','Local PFS 30.57 vs 13.9 mo; OS difference NS.','Lung carcinoid only; retrospective; bland TAE control.'),
('33004146','direct','tace','y90','Chronic hepatic toxicity 22% vs 29%; solely attributed 3% vs 14% (P=.07).','Survivors ≥1 y only; not all treated patients.'),
]

# Multigroup reports: map only contrasts actually supported by the reviewed
# result. Do not imply that a shared comparator establishes an indirect effect.
MULTI = {
 '28257902':[
  ('direct','sbrt','tace','SBRT vs TACE','Dropout 16.7% vs 20.2%; 5-y ITT OS 61% vs 56%.','Three-group P=.7 / .4; no pairwise significance claim.'),
  ('direct','sbrt','abl','SBRT vs RFA','Dropout 16.7% vs 16.8%; 5-y ITT OS 61% vs 61%.','Nonrandomized; SBRT reserved for less suitable patients.'),
  ('direct','tace','abl','TACE vs RFA','Dropout 20.2% vs 16.8%; 5-y ITT OS 56% vs 61%.','Three-group P=.7 / .4; no pairwise significance claim.')],
 '28799575':[
  ('direct','y90','abl','Y-90 vs RFA','Explant complete necrosis 75% vs 60%.','Tiny, unequal recipient groups; no dropout inference.')],
 '34358718':[
  ('direct','y90','tace','Y-90 vs TACE','Dropout sHR 0.85 (0.81–0.89) with IPTW, 1.03 (0.91–1.17) in the conventional multivariable model.','Observational first-treatment registry comparison. The result depended on adjustment method.'),
  ('direct','abl','tace','Ablation vs TACE','Dropout sHR 0.95 (0.91–0.99) with IPTW, 0.97 (0.90–1.05) in the conventional multivariable model.','Ablation vs TACE in the same registry. The result depended on adjustment method.')],
 '31517072':[
  ('direct','sbrt','y90','SBRT vs TARE','SBRT vs TARE OS HR 0.42 (0.21–0.84) in the multivariable model and 0.58 (0.37–0.91) after IPTW (P=.019).','Weighted P=.019 missed the Bonferroni threshold of .017. Tumor burden and treatment selection differed.')],
 '28677067':[
  ('direct','tace','y90','cTACE vs Y-90','Weighted OS 34.0 vs 22.9 mo.','Retrospective; pairwise weighting; not a modality ranking.'),
  ('technique','ctace','debtace','cTACE vs DEB-TACE','Weighted OS 33.8 vs 23.4 mo.','Same report, different weighted cohorts.')],
}

def build_pairs(rows):
 specs={s[0]:s[1:] for s in SPECS}
 assert len(specs)==len(SPECS)
 assert not set(specs)&set(MULTI)
 pairs=[]
 for r in rows:
  key=r['id'].split('-',1)[1]
  if key in MULTI:
   entries=MULTI[key]
  else:
   mode,a,b,brief,note=specs[key]
   entries=[(mode,a,b,r['comparison'],brief,note)]
  for i,(mode,a,b,arms,brief,note) in enumerate(entries):
   assert a in ARMS and b in ARMS and a!=b and mode in MODES
   pairs.append({'study':r['id'],'id':r['id']+'-'+str(i),'mode':mode,'a':a,'b':b,'arms':arms,'brief':brief,'note':note})
 assert {r['id'].split('-',1)[1] for r in rows}==set(specs)|set(MULTI)
 return pairs
