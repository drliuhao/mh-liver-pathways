"""Confirm that every full-text quote behind the concise study lines is verbatim in the paper's PDF.

Usage: python3 tools/check_compact_evidence_fulltext.py <folder> [<folder> ...]
The folders are searched for PDFs (the private evidence depots, or a folder of the downloaded papers); each quote
names its PDF by SHA-256, so file names do not matter. Text comes from pdftotext (poppler); line-end hyphenation is
joined and whitespace collapsed before matching. Quotes stay under 15 words.
"""
from pathlib import Path
import hashlib, json, re, subprocess, sys

ROOT = Path(__file__).resolve().parents[1]
data = json.loads((ROOT / 'tools/compact_evidence_fulltext_quotes.json').read_text())['quotes']
need = {q['sha256'] for qs in data.values() for q in qs}
found = {}
for folder in sys.argv[1:]:
    for pdf in Path(folder).rglob('*.pdf'):
        if len(found) == len(need):
            break
        h = hashlib.sha256(pdf.read_bytes()).hexdigest()
        if h in need:
            found.setdefault(h, pdf)


def text(pdf):
    out = []
    for mode in ([], ['-layout']):
        t = subprocess.run(['pdftotext', *mode, str(pdf), '-'], capture_output=True, text=True).stdout
        t = re.sub(r'-\n(?=[a-z])', '', t)
        out.append(' '.join(t.split()))
    return out


cache, errors, checked = {}, [], 0
for pmid, quotes in data.items():
    for q in quotes:
        pdf = found.get(q['sha256'])
        if not pdf:
            errors.append(f'{pmid}: PDF {q["sha256"][:12]} not found'); continue
        if pdf not in cache:
            cache[pdf] = text(pdf)
        checked += 1
        if len(q['quote'].split()) >= 15:
            errors.append(f'{pmid}: quote of 15 words or more')
        if not any(' '.join(q['quote'].split()) in t for t in cache[pdf]):
            errors.append(f'{pmid}: not verbatim: {q["quote"][:80]}')
if errors:
    print('FAIL:\n- ' + '\n- '.join(errors)); sys.exit(1)
print(f'PASS: {checked} full-text quotes for {len(data)} papers verbatim in their PDFs ({len(found)} PDFs matched by SHA-256).')
