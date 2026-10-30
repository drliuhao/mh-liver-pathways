"""Check that every document-sourced quote behind a study line is verbatim in the named V16 Word document.

usage: python3 tools/check_compact_evidence_documents.py "<V16 folder>"

tools/compact_evidence_document_quotes.json → quotes[<pmid>] = [{document, quote}]; the document text is its
paragraphs joined, whitespace collapsed (tools/extract_document_references.paragraphs).
"""
import json, re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
from extract_document_references import paragraphs

ws = lambda s: re.sub(r'\s+', ' ', s or '').strip()
folder = Path(sys.argv[1])
data = json.loads((ROOT / 'tools/compact_evidence_document_quotes.json').read_text())['quotes']
cache, bad, n = {}, [], 0
for pmid, quotes in data.items():
    for q in quotes:
        name = q['document']
        if name not in cache:
            cache[name] = ws('\n'.join(t for _, t, _ in paragraphs(folder / name) if t))
        n += 1
        if ws(q['quote']) not in cache[name]:
            bad.append(f'{pmid} {name}: {q["quote"][:80]}')
if bad:
    print('FAIL:\n- ' + '\n- '.join(bad)); sys.exit(1)
print(f'PASS: {n} document-sourced quotes checked in {len(cache)} V16 documents; 0 not found')
