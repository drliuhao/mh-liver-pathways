"""Confirm that every deck-sourced quote behind the concise study lines is verbatim in the V15 evidence-summary decks.

Usage: python3 tools/check_compact_evidence_ppt.py "<path>/V15_complete_evidence_libraries_2026-10-25"
Reads slide text only (figures are not used). Standard library only.
"""
from pathlib import Path
from xml.etree import ElementTree as ET
import json, sys, zipfile

ROOT = Path(__file__).resolve().parents[1]
NS = {'a': 'http://schemas.openxmlformats.org/drawingml/2006/main',
      'p': 'http://schemas.openxmlformats.org/presentationml/2006/main',
      'r': 'http://schemas.openxmlformats.org/officeDocument/2006/relationships'}

def deck_text(deck):
    z = zipfile.ZipFile(deck)
    pres = ET.fromstring(z.read('ppt/presentation.xml'))
    rid = {r.get('Id'): r.get('Target') for r in ET.fromstring(z.read('ppt/_rels/presentation.xml.rels'))}
    slides = {}
    for i, s in enumerate(pres.find('p:sldIdLst', NS), 1):
        x = ET.fromstring(z.read('ppt/' + rid[s.get('{%s}id' % NS['r'])]))
        paras = [''.join(r.text or '' for r in p.iter('{%s}t' % NS['a'])).strip() for p in x.iter('{%s}p' % NS['a'])]
        slides[i] = '\n'.join(p for p in paras if p)
    return slides

base = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT.parent.parent / 'V15_complete_evidence_libraries_2026-10-25'
decks = {d.parent.name: d for d in base.glob('*/*/Evidence_Summaries_v15.pptx')}
prov = json.loads((ROOT / 'tools/compact_evidence_ppt_quotes.json').read_text())['quotes']
cache, errors, checked = {}, [], 0
for pmid, quotes in prov.items():
    for q in quotes:
        lib = q['library']
        if lib not in decks:
            errors.append(f'{pmid}: deck {lib} not found'); continue
        if lib not in cache:
            cache[lib] = deck_text(decks[lib])
        text = '\n'.join(cache[lib].get(n, '') for n in q['slides'])
        checked += 1
        if q['quote'] not in text:
            errors.append(f"{pmid} {lib} slides {q['slides']}: {q['quote'][:80]}")
for e in errors[:40]:
    print('ERROR', e)
print(f'{"FAIL" if errors else "PASS"}: {checked} deck-sourced quotes checked in {len(cache)} V15 decks; {len(errors)} not found')
sys.exit(1 if errors else 0)
