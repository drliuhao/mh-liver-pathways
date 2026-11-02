"""Focused shared evidence corrections, reusing the saved primary-source checks."""
import json, subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
p = ROOT / 'tools/compact_evidence_source.json'
d = json.loads(subprocess.check_output(['git', 'show', 'b3ef22b:tools/compact_evidence_source.json'], cwd=ROOT))
studies = d['studies']
studies['22782416']['caution'] = ('Ampullary subgroup underpowered; the adjusted secondary estimate does not confirm the primary null result')
s = studies['39908431']
s['arms'] = '204 treated; 161 efficacy patients; 158 measurable; 36 pancreatic'
s['result'] = ('Pancreatic subgroup: ORR 42% (15/36 investigator), 44% central; median DoR 7.4 mo; median PFS 9.2 mo (95% CI 5.5–11.2)')
s['caution'] = 'Single-arm basket trial; pancreatic OS not reported; no screening denominator'
s['quotes'] = [
 'A total of 204 patients with 12 tumor types were enrolled and treated.',
 'Among the 161 patients included in the primary efficacy population, 10 tumor types were reported (Table 1), primarily NSCLC (in 94 patients) and pancreatic cancer (in 36 patients).',
 'Of 158 patients in the primary efficacy population who had measurable disease, 47 had an investigator-assessed confirmed objective response',
 'Pancreatic cancer 15/36 42 (25 to 59) 7.4 (2.1+ to 20.7) 16/36 44 (28 to 62) 9.1 (1.9+ to 16.6)',
 'was 9.2 months (95% CI, 5.5 to 11.2) among patients with pancreatic cancer (Table S7 and Fig. S8).',
]
s['review'] = {'date': '2026-11-01', 'basis': 'Primary report, Results pp569/571 and Table2. PFS is reported in the main text; the cited supplementary table was not newly reviewed.', 'source': 'PMID39908431'}
p.write_text(json.dumps(d, ensure_ascii=False, indent=2) + '\n')

# Keep the compact layer's numeric guard tied to the corrected, source-cited
# clinical passages. These are internal provenance passages, not paper quotations.
pd = json.loads((ROOT / 'pdac/data/critique.json').read_text())['39908431']
studies['39908431']['quotes'] = [pd['n'], pd['bottom_line'], *pd['critique']]
def collect(v):
    if isinstance(v, dict):
        if '39908431' in v.get('refs', []):
            studies['39908431']['quotes'].extend(x for x in v.values() if isinstance(x, str))
        for x in v.values():
            collect(x)
    elif isinstance(v, list):
        for x in v:
            collect(x)
collect(json.loads((ROOT / 'pdac/data/pathway.json').read_text())['gates'])
p.write_text(json.dumps(d, ensure_ascii=False, indent=2) + '\n')

proposals = json.loads((ROOT / 'tools/audit_followup/c_liver_shared_proposals.json').read_text())
for x in proposals['study_field_replacements']:
    keys = x['pointer'].strip('/').split('/')
    target = d
    for k in keys[:-1]:
        target = target[k]
    assert target[keys[-1]] == x['old'], x['pointer']
    target[keys[-1]] = x['new']
studies['34283065']['caution'] = 'Small retrospective cohorts; inconsistent outcome labels require primary-report checks before citing numbers'
studies['33362387']['arms'] = '35 cHCC-CCA, 29 iCCA, 70 matched HCC; retrospective diagnostics'
studies['33362387']['caution'] = 'Selected surgical cohort; combined-test accuracy and modelled predictive values require validation'
studies['40478744']['result'] = 'PVE first; upfront/additional LVD for substantial augmentation (strong, level 3). LT: stronger support for selected unresectable/PSC than resectable pCCA'
studies['40478744']['caution'] = 'Consensus mass ≤3 cm is separate from OPTN <3 cm; mostly observational evidence'
studies['40478744']['quotes'].append(json.loads((ROOT / 'hilar/data/critique.json').read_text())['40478744']['n'])
for x in proposals['option_key_remaps']:
    a, b = x['old_key'], x['new_key']
    for field in ('options', 'reference_links'):
        if a in d[field]:
            assert b not in d[field], b
            d[field][b] = d[field].pop(a)
    if b in d['options']:
        d['options'][b]['lead'] = x['new_lead'][:80]
p.write_text(json.dumps(d, ensure_ascii=False, indent=2) + '\n')
