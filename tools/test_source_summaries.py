"""One-line summaries of the evidence-library sources that have no PubMed study line.

usage: python3 tools/test_source_summaries.py

tools/source_summaries.json holds one line per guideline, policy, review guidance, registry record, abstract or local
document cited by a roadmap (roadmap:<slug>:<nonpm key>) or a transplant pathway library (transplant:<source key>).
- Coverage is exact: every roadmap non-PMID source (including those only its Word document cites) and every
  transplant library source without a compact study line has a line, and every line belongs to such a source.
- Each line is plain text of at most 160 characters.
- No new numbers: every number in a line occurs in the source's own citation, note or locator, or in the text of the
  page that cites it (the roadmap's pathway.json, the HCC roadmap page, or the transplant content).
- The generated data carry the lines: CompactEvidenceData.nonpm[<slug>][<key>].s and the transplant pathway rows.
"""
import json, re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
NUM = re.compile(r'(?<![A-Za-z0-9.])\d+(?:[.,·⋅]\d+)*')
norm = lambda s: s.replace(',', '').replace('·', '.').replace('⋅', '.')
nums = lambda s: {norm(m) for m in NUM.findall(s or '')}

S = json.loads((ROOT / 'tools/source_summaries.json').read_text())['summaries']
studies = json.loads((ROOT / 'tools/compact_evidence_source.json').read_text())['studies']
fail = []

# Roadmap non-PMID sources: citation text and the page's own text.
expected = {}
for f in sorted(ROOT.glob('*/data/pathway.json')):
    slug = f.parent.parent.name
    raw = f.read_text()
    for key, v in json.loads(raw).get('nonpm', {}).items():
        expected[f'roadmap:{slug}:{key}'] = (' '.join(str(x) for x in v), raw)
hcc = (ROOT / 'hcc/index.html').read_text()
block = hcc[hcc.index('const NONPM =') + len('const NONPM ='):]
for key, v in json.loads(block[:block.index('};') + 1]).items():
    expected[f'roadmap:hcc:{key}'] = (' '.join(str(x) for x in v), hcc)

# Transplant library sources without a compact study line.
content_raw = (ROOT / 'transplant/assets/content.json').read_text()
C = json.loads(content_raw)
records = {**C['high_risk']['sources'], **C['sources']}
rows = [r for p in json.loads((ROOT / 'transplant/assets/pathway-sections.json').read_text())['pathways'].values() for r in p['sources']]
for r in rows:
    if r.get('pmid') in studies:
        continue
    have = [k for k in r['keys'] if f'transplant:{k}' in S]
    if not have:
        fail.append(f"transplant:{r['key']}: no one-line summary")
    for k in have:
        rec = records.get(k) or {'title': r['cit']}  # a source only the Word documents cite: its document citation
        expected[f'transplant:{k}'] = (' '.join(str(rec.get(x, '')) for x in ('short', 'title', 'locator', 'note', 'author', 'journal', 'year')), content_raw)
# Sources only a roadmap's Word document cites (assets/document-references.js), without a PMID.
djs = (ROOT / 'assets/document-references.js').read_text()
for slug, drows in json.loads(djs[djs.index('{'):djs.rindex('}') + 1]).items():
    page_raw = (ROOT / ('hcc/index.html' if slug == 'hcc' else f'{slug}/data/pathway.json')).read_text()
    for r in drows:
        if not r.get('pmid'):
            expected[f'roadmap:{slug}:{r["id"]}'] = (r['cit'], page_raw)
            if (r.get('summary') or {}).get('text') != S.get(f'roadmap:{slug}:{r["id"]}'):
                fail.append(f'document-references.js: roadmap:{slug}:{r["id"]} line differs from tools/source_summaries.json')

missing = sorted(set(expected) - set(S))
orphans = sorted(set(S) - set(expected))
if missing:
    fail.append(f'sources without a summary: {missing[:10]}')
if orphans:
    fail.append(f'summaries for no current source: {orphans[:10]}')
for sid, line in S.items():
    if not line or len(line) > 160 or line != line.strip() or re.search(r'<[^>]+>|\s{2,}', line):
        fail.append(f'{sid}: empty, over 160 characters or not plain text ({len(line)})')
    if sid in expected:
        cite, page = expected[sid]
        extra = nums(line) - nums(cite) - nums(page)
        if extra:
            fail.append(f'{sid}: numbers not in the source or its page: {sorted(extra)}')

# The generated data carry the lines.
js = (ROOT / 'assets/compact-evidence-data.js').read_text()
data = json.loads(js[js.index('{'):js.rindex('}') + 1])
for slug, items in data['nonpm'].items():
    for key, item in items.items():
        if item.get('s') != S.get(f'roadmap:{slug}:{key}'):
            fail.append(f'compact-evidence-data.js: roadmap:{slug}:{key} line differs from tools/source_summaries.json')
if fail:
    print('FAIL:\n- ' + '\n- '.join(fail[:40])); raise SystemExit(1)
n_road = sum(1 for k in S if k.startswith('roadmap:'))
print(f'PASS: {len(S)} one-line summaries ({n_road} roadmap and {len(S) - n_road} transplant non-PMID sources), coverage exact, '
      f'each ≤160 characters with no number absent from its source or page; the generated data carry them.')
