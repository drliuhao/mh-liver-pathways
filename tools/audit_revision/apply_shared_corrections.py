"""One-time, source-recorded propagation of reconciled shared evidence corrections."""
import json, re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
manifest = ROOT / 'tools/clinical_revisions/2026-11-02-shared-audit.json'
assert not manifest.exists(), 'Shared audit already applied; do not apply twice.'
changes = []
def write(file, new, why):
    path = ROOT/file
    old = path.read_text()
    if old != new:
        changes.append(dict(file=file, old=old, new=new, why=why))
        path.write_text(new)
def dump(data):
    return json.dumps(data, ensure_ascii=False, indent=2)+'\n'

src = json.loads((ROOT/'tools/compact_evidence_source.json').read_text())
for proposal in json.loads((ROOT/'tools/audit_revision/liver_shared_proposals.json').read_text()):
    if proposal.get('file') != 'tools/compact_evidence_source.json' or 'new' not in proposal:
        continue
    p = proposal['json_path']; holder = src
    for key in p[:-1]: holder=holder[key]
    assert holder.get(p[-1]) == proposal['old'], p
    holder[p[-1]]=proposal['new']
s=src['studies']
s['34554208']['result']='ITT OS 10.3 vs 7.5 mo (HR 0.79, 95% CI 0.56–1.12; P=.09); corrected adjusted HR 0.49 (95% CI 0.25–1.24); primary PFS HR 0.37'
s['34554208']['caution']='70% crossover; corrected adjusted OS not significant; model-dependent estimate; 2% response'
s['38092727']['result']='Post-LT 5-y OS 45.4% iCCA-like vs 76.4% HCC-like (HR 2.69, 95% CI 1.15–6.31); model–pathologist reclassification kappa 0.19'
s['38092727']['caution']='Retrospective; small LT subset; no reclassification ground truth; resection/explant, not biopsy validation'
s['25014687']['caution']='96% stable; grade 2 HR 0.45 (0.22–0.91), pancreatic HR 0.58 (0.32–1.04); no predictive cutoff'
s['39802807']['arms']='Emprint MWA vs single-needle RFA'
s['39802807']['result']='2-y lesion-level local progression 20/122 (16.4%) vs 38/125 (30.4%); RR 0.54 (95% CI 0.33–0.87), P=.007; no OS advantage shown'
s['39802807']['caution']='Device-specific, mostly small lesions; complete-case lesion analysis; no universal MWA superiority claim'
s['42223137']['caution']='Closed early; crossover; GemCis comparator without ICI; no new first-line policy or LT strategy established'
# Quotes are attached to the reviewed source-specific fields, not unrelated numbers elsewhere on a page.
for slug,pm in [('icca','34554208'),('chcca','38092727'),('nelm','25014687')]:
    c=json.loads((ROOT/f'{slug}/data/critique.json').read_text())[pm]
    s[pm]['quotes']=[c['n'],c['bottom_line']]+c.get('critique',[])
s['42879142']={
    'label':'ClarIDHy OS correction','design':'Other','arms':'Correction to the ClarIDHy crossover-adjusted OS analysis',
    'result':'Adjusted OS HR 0.49; corrected bootstrap 95% CI 0.25–1.24; no statistically significant adjusted OS benefit',
    'caution':'Read with the original report; the correction changes uncertainty, not the ITT result',
    'quotes':[json.loads((ROOT/'icca/data/critique.json').read_text())['34554208']['bottom_line']]
}
write('tools/compact_evidence_source.json',dump(src),'B16; A HB040/HB081 and primary-source reconciliations; corrected endpoints, subgroup identity and study limits')

summaries=json.loads((ROOT/'tools/source_summaries.json').read_text())
summaries['summaries']['roadmap:hcc:doc-imfinzi-label']='US durvalumab label: HCC use with tremelimumab (STRIDE); durvalumab monotherapy is not a separate FDA-approved HCC regimen.'
summaries['summaries']['roadmap:crlm:doc-fda-encorafenib']='FDA approval of encorafenib plus cetuximab and mFOLFOX6 or FOLFIRI for BRAF V600E metastatic colorectal cancer.'
write('tools/source_summaries.json',dump(summaries),'B26 regulatory source summaries: distinguish trial arms from approved regimens; restore cetuximab')
for file in ['tools/document_references.json','evidence-libraries/catalog.json']:
    raw=(ROOT/file).read_text()
    write(file,raw.replace('10.1016/j.gie.2021.05.011','10.1016/j.gie.2020.12.035'),'B24/B26 PMID34023067 ASGE source DOI correction')

matrix=json.loads((ROOT/'lrt/matrix.json').read_text())
matrix['summary']=[
 [1,'Randomized comparisons support ablation for selected small HCC and CRLM. A nonsignificant difference does not establish equivalence: read each trial’s population, endpoint and limits.'],
 [2,'Selected definitive local treatment: SBRT or Y-90 segmentectomy in HCC; SBRT for selected CRLM or iCCA; ablation for small iCCA. Evidence and feasibility differ by tumour. NELM ablation is cytoreductive or symptom-directed, with no established curative survival benefit.'],
 [3,'Treatment within a curative strategy: bridge or downstage to transplant; selected perioperative or conversion treatment; liver-volume optimisation. pCCA radiotherapy is a component of an approved transplant regimen. These roles do not establish benefit as stand-alone treatment.'],
 [4,'Disease control or symptom relief: embolisation for appropriate HCC or NELM; selected Y-90, HAI/HAIC or radiotherapy in the relevant disease. Compare eligibility, endpoints and harms in each cell.'],
 [5,'Investigational or unsupported routine use: histotripsy as an oncologic strategy; SBRT or HAI for NELM; routine first-line Y-90 for CRLM. Trial participation and MDT review depend on the clinical setting.']]
write('lrt/matrix.json',dump(matrix),'B09/B15 reconciled treatment intent; summary must match the corrected tumour-specific cells')

flow=(ROOT/'assets/roadmap-flow.js').read_text()
needle="  const group=(label,items,cls)=>"
insert="  const recommendations=[...(s.standard||[]),...(s.alt||[])];\n  const standard=recommendations.filter(x=>! /^(Reasonable|Trial|Investigational)/i.test(x.l||''));\n  const alternative=recommendations.filter(x=> /^(Reasonable|Trial|Investigational)/i.test(x.l||''));\n"
assert needle in flow
flow=flow.replace(needle,insert+needle).replace("group('Standard approach',s.standard,","group('Standard approach',standard,").replace("group('Reasonable alternatives',s.alt,","group('Reasonable alternatives / protocol options',alternative,")
write('assets/roadmap-flow.js',flow,'B15-R10-F1: honour explicit recommendation labels instead of storage-container name')

page=(ROOT/'lrt/pcca-update.html').read_text()
page=page.replace('What changed in the pCCA pathway','pCCA liver-directed treatment evidence').replace('Evidence review updated 23 October 2026','Evidence reconciled 2 November 2026')
page=page.replace('chemotherapy-only versus RT-containing protocols; no significant difference, not proof of equivalence.','chemotherapy-only versus RT-containing protocols; recurrence 6/12 versus 3/14. This small observational comparison does not establish equivalence.')
page=page.replace('<h2>Updated chart</h2><p><a href="pcca-decision-chart.pdf">Open the decision-chart PDF</a> · <a href="evidence-matrix.pdf">Full evidence-matrix PDF</a></p>','<h2>Clinical decisions</h2><p><a href="../hilar/">pCCA roadmap</a> · <a href="../transplant/pcca/">Transplant pathway</a> · <a href="./?tumor=pcca">Current evidence matrix</a></p>')
write('lrt/pcca-update.html',page,'B09: report the recurrence denominator and direct readers to current reviewed clinical pages')

manifest.write_text(dump(dict(id='2026-11-02-shared-audit',date='2026-11-02',scope='Shared evidence and recommendation presentation',files=changes)))
print(f'{len(changes)} shared files revised and recorded.')
