"""Check that every abstract-sourced quote behind a study line is verbatim in its PubMed abstract.

usage: python3 tools/check_compact_evidence_abstracts.py <abstracts.json>

<abstracts.json> is a {pmid: {"abstract": ...}} export from PubMed, kept outside the repository; each quote in
tools/compact_evidence_abstract_quotes.json must be fewer than 15 words and verbatim in its abstract.
"""
import json, re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ws = lambda s: re.sub(r'\s+', ' ', s or '').strip()
abstracts = json.loads(Path(sys.argv[1]).read_text())
data = json.loads((ROOT / 'tools/compact_evidence_abstract_quotes.json').read_text())['quotes']
bad, n = [], 0
for pmid, quotes in data.items():
    for q in quotes:
        n += 1
        if len(q.split()) >= 15 or ws(q) not in ws(abstracts.get(pmid, {}).get('abstract')):
            bad.append(f'{pmid}: {q[:80]}')
if bad:
    print('FAIL:\n- ' + '\n- '.join(bad)); sys.exit(1)
print(f'PASS: {n} abstract-sourced quotes checked in {len(data)} PubMed abstracts; 0 not found')
