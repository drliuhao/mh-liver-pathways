"""Every reference of every V16 Word document is in its page's evidence library, with a one-line summary.

usage: python3 tools/test_document_references.py

Hao Liu, 30 October 2026: the libraries must be complete for the roadmaps and for both transplant protocols.
- tools/document_references.json holds the 26 documents' reference lists (tools/extract_document_references.py).
- Roadmaps: each reference is already in the page's library data or is a row of assets/document-references.js,
  which must be exactly what tools/build_document_references.py builds; every added row has a category, a
  citation, where the document cites it and a summary source (its compact study line, or its line in
  tools/source_summaries.json).
- Transplant pathways: each reference of the standard and the high-risk document is a row of the pathway's library
  in transplant/assets/pathway-sections.json, whose "Cited in" names that document and reference number.
- Roadmap pages load the generated file before assets/roadmap-evidence.js, which merges it.
"""
import json, re, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
import document_refs as R
import build_document_references as B

fail = []
dest = ROOT / 'assets/document-references.js'
before = dest.read_text()
B.build()
if dest.read_text() != before:
    fail.append('assets/document-references.js is stale: rerun tools/build_document_references.py')
    dest.write_text(before)
added = json.loads(before[before.index('{'):before.rindex('}') + 1])
studies = json.loads((ROOT / 'tools/compact_evidence_source.json').read_text())['studies']
summaries = json.loads((ROOT / 'tools/source_summaries.json').read_text())['summaries']
docs = R.DOCS
assert len(docs) == 26 and sum(1 for d in docs.values() if d['family'] == 'roadmap') == 12, 'expected 12 roadmap and 14 transplant documents'

n_road = n_road_added = 0
for slug in B.SLUGS:
    lib = B.page_library(slug)
    rows = added.get(slug, [])
    ids = {r['id'] for r in rows} | {r.get('pmid') for r in rows if r.get('pmid')}
    for r in rows:
        if not (r['tag'] and r['group'] and r['cit'] and r.get('cited', '').startswith('Roadmap document')):
            fail.append(f'{slug}: added row {r["id"]} lacks tag, category, citation or "Cited in"')
        if r.get('pmid'):
            if r['pmid'] not in studies:
                fail.append(f'{slug}: added PMID {r["pmid"]} has no compact study line')
        elif (r.get('summary') or {}).get('text') != summaries.get(f'roadmap:{slug}:{r["id"]}'):
            fail.append(f'{slug}: added source {r["id"]} has no one-line summary')
    for name, _ in R.documents('roadmap', slug):
        for ref in R.resolved(name):
            n_road += 1
            if lib.has(ref):
                continue
            rid = ref['pmid'] or 'doc-' + ((ref['nonpm'] or {}).get('key') or '')
            if rid not in ids:
                fail.append(f'{slug}: document reference missing from the library: {ref["cite"][:80]}')
    n_road_added += len(rows)

P = json.loads((ROOT / 'transplant/assets/pathway-sections.json').read_text())['pathways']
n_tx = 0
for slug, d in P.items():
    cited = ' | '.join(s.get('appraisal', {}).get('cited', '') for s in d['sources'])
    for name, setting in R.documents('transplant', slug):
        doc = R.SETTING_NAME[setting]
        for ref in R.resolved(name):
            n_tx += 1
            if f'{doc}, reference {ref["label"]}' not in cited:
                fail.append(f'transplant/{slug}: {doc} reference {ref["label"]} is in no library row ({ref["cite"][:60]})')
    for s in d['sources']:
        if not (s.get('summary') or {}).get('text'):
            fail.append(f'transplant/{slug}: {s["key"]} has no one-line summary')

for slug in B.SLUGS:
    page = (ROOT / f'{slug}/index.html').read_text()
    i, j = page.find('assets/document-references.js'), page.find('assets/roadmap-evidence.js')
    if i < 0 or j < 0 or i > j:
        fail.append(f'{slug}: document-references.js must load before roadmap-evidence.js')
if 'window.DocumentReferences' not in (ROOT / 'assets/roadmap-evidence.js').read_text():
    fail.append('roadmap-evidence.js does not merge the document references')

if fail:
    print('FAIL:\n- ' + '\n- '.join(fail[:40])); sys.exit(1)
print(f'PASS: {n_road} roadmap document references (12 documents) all in their libraries, {n_road_added} added from the documents; '
      f'{n_tx} transplant document references (14 documents) each a library row that names its document and number; '
      f'every row with a one-line summary; generated data in sync.')
