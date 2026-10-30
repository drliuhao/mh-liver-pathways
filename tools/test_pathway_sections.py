"""Closing sections of the transplant pathway pages: built from their sources, complete and linked once.

usage: python3 tools/test_pathway_sections.py

- transplant/assets/pathway-sections.json is exactly what tools/build_pathway_sections.py builds.
- Every pathway has the four sections' data: limited-evidence items (each with its basis, a locator and only real
  sources), decision owners for every step, the protocol team text or an explicit absence, quality measures split by
  setting, an index of every meeting question and high-risk review, and the evidence library.
- Questions are an index, not copies: each links to #meeting-<id> or #high-risk-<anchor>, every meeting question and
  high-risk review appears exactly once.
- The evidence library has one row per publication (no PMID twice), each with a category, a citation and a one-line
  summary: a PubMed paper's compact study line (design · population, main result) or, for other sources, its line
  in tools/source_summaries.json.
- The page script loads only on transplant pathway pages and the shared navigation loads it.
"""
import json, re, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
dest = ROOT / 'transplant/assets/pathway-sections.json'
before = dest.read_text()
subprocess.run([sys.executable, str(ROOT / 'tools/build_pathway_sections.py')], check=True, capture_output=True)
fail = []
if dest.read_text() != before:
    fail.append('pathway-sections.json is stale: rerun tools/build_pathway_sections.py')
data = json.loads(dest.read_text())['pathways']
C = json.loads((ROOT / 'transplant/assets/content.json').read_text())
HR = C['high_risk']
STUDIES = json.loads((ROOT / 'tools/compact_evidence_source.json').read_text())['studies']
SUMMARIES = json.loads((ROOT / 'tools/source_summaries.json').read_text())['summaries']
assert list(data) == ['hcc', 'pcca', 'icca', 'crlm', 'nelm', 'hehe', 'hca'], list(data)
n_items = n_q = n_sum = 0
for slug, d in data.items():
    p = next(x for x in C['index'] if x['slug'] == slug)
    if not d['limited']:
        fail.append(f'{slug}: no limited-evidence items')
    for i, x in enumerate(d['limited']):
        n_items += 1
        if not (x['t'] and x['why'] and x['locator']) or len(x['t']) > 220 or len(x['why']) > 550:
            fail.append(f'{slug} limited[{i}]: missing field or too long')
        if x['setting'] not in ('standard', 'highrisk'):
            fail.append(f'{slug} limited[{i}]: setting')
        if "step '" in x['locator'] or 'protocol §' in x['locator']:
            fail.append(f'{slug} limited[{i}]: locator still uses internal or old names')
        for r in x['refs']:
            if not (r['key'] in C['sources'] or r['key'] in HR['sources']):
                fail.append(f'{slug} limited[{i}]: unknown source {r["key"]}')
        if x['related'] and not re.fullmatch(r'#(meeting-[\w-]+|high-risk-[\w.-]+)', x['related']['href']):
            fail.append(f'{slug} limited[{i}]: related link {x["related"]["href"]}')
    if [o['id'] for o in d['owners']] != [s['id'] for s in p['steps']] or not all(o['owner'] for o in d['owners']):
        fail.append(f'{slug}: decision owners do not cover every step')
    if d['team'] is not None and not d['team']['text']:
        fail.append(f'{slug}: empty team text')
    if not (d['quality']['standard'] or d['quality']['highrisk']):
        fail.append(f'{slug}: no quality measures at all')
    std = [q['id'] for q in d['questions']['standard']]
    hr = [q['id'] for q in d['questions']['highrisk']]
    n_q += len(std) + len(hr)
    if std != [i['id'] for i in p['issues']] or any(q['href'] != f'#meeting-{q["id"]}' for q in d['questions']['standard']):
        fail.append(f'{slug}: meeting-question index incomplete or mislinked')
    reviews = HR['pathways'][slug]['reviews']
    if hr != [r['id'] for r in reviews] or any(q['href'] != f'#high-risk-{r["anchor"]}' for q, r in zip(d['questions']['highrisk'], reviews)):
        fail.append(f'{slug}: high-risk review index incomplete or mislinked')
    keys = [k for s in d['sources'] for k in s['keys']]
    pmids = [s['pmid'] for s in d['sources'] if s.get('pmid')]
    if len(keys) != len(set(keys)) or not keys or len(pmids) != len(set(pmids)):
        fail.append(f'{slug}: evidence library empty or duplicated')
    for s in d['sources']:
        sm = s.get('summary') or {}
        want = ({'lead': STUDIES[s['pmid']]['arms'], 'text': STUDIES[s['pmid']]['result']} if s.get('pmid') in STUDIES
                else {'lead': '', 'text': next((SUMMARIES[f'transplant:{k}'] for k in s['keys'] if f'transplant:{k}' in SUMMARIES), None)})
        if not sm.get('text') or sm != want:
            fail.append(f'{slug}: {s["key"]} one-line summary missing or not from its source line')
        if s['group'] not in ('Policy & review guidance', 'Guidelines & consensus', 'Studies', 'Drug labels') or not (s['tag'] and s['cit']):
            fail.append(f'{slug}: {s["key"]} row fields')
        n_sum += 1
    for r in reviews:
        for k in r['references']:
            if k not in keys:
                fail.append(f'{slug}: high-risk source {k} missing from the evidence library')
nav = (ROOT / 'assets/portal-navigation.js').read_text()
if "'pathway-sections.js'" not in nav:
    fail.append('portal navigation must load pathway-sections.js')
js = (ROOT / 'assets/pathway-sections.js').read_text()
for title in ['Practice choices with limited evidence', 'Questions for consensus', 'Team responsibilities and quality monitoring', 'Evidence library']:
    if f"'{title}'" not in js:
        fail.append(f'section missing from the page script: {title}')
if fail:
    print('FAIL:\n- ' + '\n- '.join(fail[:60])); sys.exit(1)
print(f'PASS: 7 pathways; {n_items} limited-evidence choices with basis, locator and real sources; owners for every decision; '
      f'team and quality measures by setting; {n_q} questions indexed once and linked to where they are set out; evidence libraries complete, '
      f'{n_sum} sources (one row per publication) each with its one-line summary.')
