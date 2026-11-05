"""Reviewed compact display metadata, never a whole-modality treatment ranking.

Clinical records and the 101 explicit comparisons remain unchanged. Colors
refer to a named endpoint within one study. No null superiority test is NI.
"""
VERDICTS = {
 'superior': {'symbol':'▲','label':'Superiority','description':'A randomized comparison supports an advantage on the stated endpoint in its trial population. This does not imply superiority on every outcome or in other patients.'},
 'noninferior': {'symbol':'≈','label':'Non-inferiority','description':'The prespecified non-inferiority criterion was met for the stated endpoint and margin. This does not mean equivalence.'},
 'ni_uncertain': {'symbol':'≈?','label':'NI not established','description':'A non-inferiority trial or claim has unresolved precision or analysis limitations; do not read this as demonstrated non-inferiority.'},
 'signal': {'symbol':'↗','label':'Signal only','description':'An observational association, exploratory/secondary result, or limited pilot signal. It does not establish a general treatment advantage.'},
 'uncertain': {'symbol':'?','label':'No clear advantage','description':'The reported comparison did not establish superiority on the summarized endpoint, or the available estimate is too uncertain. Nonsignificance does not establish non-inferiority or equivalence.'},
}
# Classification is explicit, not inferred from p-values or keywords.
SUPERIOR = {
 '39693584':('SBRT','local PFS'), '32615109':('Transplant','survival after downstaging'),
 '34648352':('HAIC-FOLFOX','OS'), '34905388':('HAIC-FOLFOX','OS'),
 '36421345':('SBRT','local control'), '11981766':('TACE','OS'), '12049862':('TACE','OS'),
 '35258371':('Y90','TTP'), '27575820':('Y90','TTP'), '31070690':('HAIC + sorafenib','OS'),
 '29543938':('TACE + EBRT','12-week PFS'), '23269991':('TACE + RFA','OS'),
 '39798579':('TACE + durvalumab/bevacizumab','PFS'), '39798578':('TACE + lenvatinib/pembrolizumab','PFS'),
 '36525610':('Adjuvant HAIC','DFS'), '29420221':('Adjuvant TACE','RFS'),
 '33166497':('Personalized Y90 dose','3-month index-lesion response'), '39245060':('Whole-liver RT','pain response'),
 '39311927':('Radioactive stent + HAIC','OS; both arms received HAIC'),
 '22493375':('DEBIRI','OS'), '16505413':('HAI','OS'), '20567019':('Y90 + fluorouracil','liver TTP'),
 '34541864':('Y90 + second-line chemotherapy','PFS'), '42018958':('HAI oxaliplatin + IV LV5FU2','hepatic RFS'),
 '10615075':('HAI + systemic','2-year OS landmark only'),
}
SIGNAL = {
 '26628466':('SBRT','local control in tumors ≥2 cm'), '33230652':('Y90','mean target PFS'),
 '19552767':('Y90','downstaging'), '34358718':('Study treatment','waitlist dropout'),
 '39808828':('Y90','downstaging'), '41056563':('Y90','waitlist dropout'), '41580092':('Y90','waitlist dropout'),
 '35993224':('Added ablation after HAIC','2-year OS in selected responders'),
 '37328589':('Staged embolization/resection','perioperative mortality / OS'),
 '31283409':('Preoperative 3D-CRT','univariable HCC-death analysis'),
 '26695839':('HAI + systemic','OS'), '33868997':('HAIC','OS'), '40216615':('HAIC','OS vs cTACE only'),
 '37814188':('HAI ± systemic','OS'), '31517072':('SBRT','OS'), '26503201':('Higher radiation dose','OS / local control'),
 '37032423':('Neoadjuvant chemoradiation','recurrence; no OS gain'), '42433279':('Catheter HAIC','OS'),
 '30982687':('SABR + standard care','phase II OS signal; mixed cancers'),
 '32484754':('SABR + standard care','follow-up OS; mixed cancers'),
 '29181682':('HAI','OS from unresectable diagnosis'), '40709764':('HAI','OS after 1–2 prior lines; not 3–4'),
 '28376151':('Local treatment + systemic','OS, secondary endpoint'),
 '11843249':('Y90 added to HAI','tumor response'), '28426374':('Perioperative HAI','OS'),
 '16134179':('Bland embolization','carcinoid response; not all NETs'),
 '29167951':('Bland embolization','3-month response; 11-patient pilot'),
 '42006283':('Y90','local PFS in lung carcinoid'), '28677067':('cTACE','weighted OS'),
}
# Brief display strings keep the clinically important endpoint and arm direction.
# Ratios/HRs retain their source analysis. Full results and CIs remain in details.
MINI = {
 '16495695':'4-y OS: ablation 65.9%, surgery 64.0%; NS',
 '29503247':'2-y local progression: MWA 6%, RFA 12%; NS',
 '31774468':'5-y OS: surgery 43.6%, RFA 38.5%; NS',
 '29091283':'10-y OS: surgery 47.6%, RFA 41.8%; NS',
 '35949295':'Surgery RFS HR 0.92 (0.67–1.25); NS',
 '40554738':'5-y OS: surgery 74.6%, RFA 70.4%; P=.84',
 '26628466':'SBRT: better local control if ≥2 cm',
 '39693584':'2-y local PFS: SBRT 92.7%, RFA 75.8%',
 '33230652':'Mean target PFS: Y90 57.8, MWA 38.6 mo',
 '42434250':'Y90 PFS HR 0.56 (0.20–1.51); uncertain',
 '27930089':'CR / progression / OS: no clear difference',
 '35346857':'Y90 progression HR 1.16 (0.51–2.63)',
 '36100064':'DCR: Y90 94.7%, TACE+abl 100%; OS/PFS NS',
 '32615109':'5-y OS: LT 77.5%, non-LT 31.2%',
 '42379392':'Mean necrosis: Y90 83.6%, TACE+MWA 79%; NS',
 '19552767':'Downstaging: Y90 58%, TACE 31%',
 '28668402':'Recurrence: Y90 9%, TACE 8%; OS/RFS NS',
 '34331914':'Downstaging: no clear Y90–TACE difference',
 '35619164':'Recurrence: Y90 23%, TACE 11%; P=.12',
 '39808828':'2-y downstaging: Y90 74%, TACE 65%',
 '41056563':'Y90 dropout sHR 0.83 (0.74–0.93)',
 '41580092':'2-y dropout: Y90 14.2%, TACE 19.0%',
 '29631810':'OS: add-on 11.8, control 11.5 mo; NS',
 '34648352':'OS: HAIC 23.1, cTACE 16.1 mo',
 '34905388':'OS: HAIC 13.9, sorafenib 8.2 mo',
 '37037359':'Primary TTP: no clear difference',
 '36421345':'SBRT: better local control',
 '11981766':'TACE: survival benefit vs supportive care',
 '12049862':'TACE: OS HR 0.47 vs supportive care',
 '25373796':'PFS / OS: no clear difference',
 '35258371':'TTP: Y90 17.1, DEB-TACE 9.5 mo',
 '25443863':'DCR: Y90 76.9%, TACE 73.3%; QoL NS',
 '27575820':'TTP: Y90 >26, cTACE 6.8 mo; OS NS',
 '27284477':'Y90 OS HR 0.72 (0.49–1.07); NS',
 '29107679':'OS: Y90 8.0, sorafenib 9.9 mo; NS',
 '29498924':'OS: Y90 8.8, sorafenib 10.0 mo; NS',
 '33687130':'HAIC add-on: 3-y RFS 54.3% vs 34.3%; P=.094',
 '31070690':'OS: add-on 13.4, sorafenib 7.1 mo',
 '35993224':'Selected responders: 2-y OS 74.3% vs 27.7%',
 '39699905':'SBRT add-on: OS 15.8 vs 12.3 mo; primary P=.06',
 '29543938':'12-wk PFS: TACE+RT 86.7%, sorafenib 34.3%',
 '23269991':'4-y OS: TACE+RFA 61.8%, RFA 45.0%',
 '39798579':'Add-on PFS 15.0 vs 8.2 mo; OS unresolved',
 '39798578':'Add-on PFS 14.6 vs 10.0 mo; OS unresolved',
 '31421157':'Y90 added to sorafenib: no OS benefit',
 '36525610':'Adjuvant HAIC: DFS 20.3 vs 10.0 mo',
 '29420221':'Adjuvant TACE: longer RFS',
 '37328589':'Staged surgery: lower hospital mortality',
 '38488934':'Postoperative PFS / OS: no difference',
 '31283409':'Preop RT: HCC-death HR 0.47',
 '33166497':'3-mo response: personalized 71%, standard 36%',
 '39245060':'Pain response: RT 67%, supportive care 22%',
 '41528222':'OS: MWA 29.8, repeat resection 34.0 mo; NS',
 '38261915':'5-y OS: MWA 44.8%, resection 40.4%; NS',
 '26695839':'OS: HAI+systemic 30.8, systemic 18.4 mo',
 '33868997':'1-y OS: HAIC 60.2%, TACE 42.9%',
 '40216615':'OS: HAIC 10.3, cTACE 5.1 mo',
 '35544131':'HAI OS HR 0.75 (0.55–1.03); uncertain',
 '37814188':'OS: HAI±systemic 27.7, GemCis 11.8 mo',
 '30191056':'Disease control: Y90 48%, TACE 47%',
 '26503201':'3-y OS: higher RT dose 73%, lower 38%',
 '39936132':'OS / explant response: no clear difference',
 '37032423':'CRT recurrence HR 0.30; OS benefit absent',
 '42433279':'OS: HAIC 17.63, supportive care 6.10 mo',
 'abstract-ABC-07-randomized-phase-II':'SBRT add-on: PFS 8.6 vs 9.0 mo; HR 1.00',
 '39311927':'OS: radioactive stent 10.2, usual 6.7 mo',
 '42829779':'1-y FFLP: MWA 77.7%, SBRT 83%; NS',
 '30982687':'Mixed cancers: OS 41 vs 28 mo; P=.09',
 '32484754':'Mixed cancers: OS 50 vs 28 mo; HR 0.47',
 '39848272':'Ablation OS HR 1.05 (0.69–1.58); NI unresolved',
 '31177151':'DEB-TACE OS HR 0.94 (0.54–1.65); NS',
 '22493375':'OS: DEBIRI 22, FOLFIRI 15 mo',
 '16505413':'OS: HAI 24.4, bolus FU/LV 20.0 mo',
 '29181682':'OS from unresectability: HAI 31.2, Y90 16.3 mo',
 '40709764':'HAI signal after 1–2 lines; not 3–4',
 '41118066':'Conversion 7/11 vs 2/9; P=.09',
 '28376151':'8-y OS: local+systemic 35.9%, systemic 8.9%',
 '28781171':'OS: add-on 22.6, FOLFOX 23.3 mo; NS',
 '11843249':'Response: Y90+HAI 50%, HAI 24%',
 '20567019':'Liver TTP: add-on 5.5, FU 2.1 mo; OS NS',
 '34541864':'PFS: add-on 8.0, chemo 7.2 mo; OS NS',
 'abstract-Dutch-PUMP':'Adjuvant HAI PFS HR 0.88 (0.62–1.25); NS',
 '42018958':'Hepatic RFS: arterial 25, IV 12 mo',
 '10615075':'2-y OS: add-on 86%, control 72%; full curve NS',
 '39644535':'3-y RFS: add-on 31.4%, control 34.4%; NS',
 '28426374':'OS: perioperative HAI 67, no HAI 44 mo',
 'abstract-RETNET-RCT':'Hepatic PFS: no clear TAE–cTACE difference',
 '16134179':'Carcinoid response: TAE 81%, TACE 44.4%',
 '32032719':'Disease control: Y90 83%, TACE 96%; OS NS',
 '29167951':'3-mo response: TAE 5/5, Y90 0/6',
 '42006283':'Lung NET local PFS: Y90 30.57, TAE 13.9 mo',
 '33004146':'Chronic liver toxicity: TACE 22%, Y90 29%',
 '28257902':'Waitlist dropout: no clear difference',
 '28799575':'Recipient-only necrosis: Y90 75%, RFA 60%',
 '34358718':'Adjusted dropout sHR vs TACE: 0.85 / 0.95',
 '31517072':'SBRT vs Y90 OS HR 0.42 (0.21–0.84)',
 '28677067':'Weighted OS: cTACE 34.0, Y90 22.9 mo',
}
LABELS = {'40554738':'SURF final','35949295':'SURF','39848272':'COLLISION','42829779':'LAVA-CRLM','39699905':'RTOG 1112','35258371':'TRACE','27575820':'PREMIERE','34905388':'FOHAIC-1','34648352':'Li 2022','36525610':'Li 2023','29631810':'SILIUS','41118066':'SULTAN','39644535':'HARVEST','39798579':'EMERALD-1','39798578':'LEAP-012','16505413':'CALGB 9481','30982687':'SABR-COMET','32484754':'SABR-COMET LT','33166497':'DOSISPHERE-01','39245060':'CCTG HE1','37037359':'TRENDY','36421345':'Comito','29503247':'Vietti Violi','abstract-ABC-07-randomized-phase-II':'ABC-07','abstract-Dutch-PUMP':'Dutch PUMP','abstract-RETNET-RCT':'RETNET'}

def add_screen_metadata(rows,pairs):
 by_id={r['id']:r for r in rows}
 assert {i.split('-',1)[1] for i in by_id}==set(MINI)
 for p in pairs:
  r=by_id[p['study']];pid=p['study'].split('-',1)[1]
  verdict='superior' if pid in SUPERIOR else ('signal' if pid in SIGNAL else 'uncertain')
  favored,endpoint=(SUPERIOR.get(pid) or SIGNAL.get(pid) or ('','summarized outcome'))
  micro=MINI[pid]
  if pid=='39848272':verdict='ni_uncertain';endpoint='OS non-inferiority';favored=''
  if pid=='34358718':
   favored='Y90' if p['a']=='y90' else 'Ablation'
   micro=favored+' dropout sHR '+('0.85 (0.81–0.89)' if p['a']=='y90' else '0.95 (0.91–0.99)')
  if pid=='28677067' and p['b']=='debtace':micro='Weighted OS: cTACE 33.8, DEB-TACE 23.4 mo'
  label=LABELS.get(pid,r['label'].replace(' RCT','').replace(' ph III','').replace(' ph II',''))
  p['screen']={'label':label,'result':micro,'verdict':verdict,'favored':favored,'endpoint':endpoint,'rationale':p['note']}
  if pid=='39848272':p['screen']['rationale']='Trial stopped using its conditional-power rule. The observed OS confidence interval extends beyond the 1.30 non-inferiority margin; the current review therefore retains an unresolved NI label. Reduced adverse events are a separate safety result.'
  assert len(micro)<=64,(pid,len(micro))
 return VERDICTS
