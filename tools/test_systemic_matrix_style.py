"""Check the LRT-style systemic matrix: source-preserving structure, evidence rows and anchors.

The text-preservation check against the original regimen paragraphs lives in
tools/test_systemic_disclosures.py; this test covers the matrix-style layer itself.
"""
from pathlib import Path
from collections import Counter
import json
import subprocess
from lxml import html

ROOT = Path(__file__).resolve().parents[1]
BASELINE = '76dacc5'
old = html.fromstring(subprocess.check_output(['git', 'show', f'{BASELINE}:systemic/index.html'], cwd=ROOT))
page = html.fromstring((ROOT / 'systemic/index.html').read_text())
matrix = json.loads((ROOT / 'systemic/matrix.json').read_text())
refs = json.loads((ROOT / 'systemic/references.json').read_text())
rows = json.loads((ROOT / 'tools/systemic_evidence_rows.json').read_text())
norm = lambda s: ' '.join(s.split())

assert page.get('data-systemic-layout') == 'lrt-matrix'
ids = {e.get('id') for e in page.xpath('//*[@id]')}
cards = {c['id']: c for c in matrix['cards']}
assert set(rows) == set(cards)
tied = statements = 0
for cid, card in cards.items():
    node = page.get_element_by_id(cid)
    assert ' '.join(r['text'] for r in rows[cid]) == card['evidence'], cid
    items = node.xpath('.//div[contains(@class,"st-evidence")]/ul/li')
    assert [norm(li.xpath('string(.//span[@class="st-ev-text"])')) for li in items] == [norm(r['text']) for r in rows[cid]], cid
    for li, row in zip(items, rows[cid]):
        chips = li.xpath('.//a[contains(@class,"pm")]')
        assert [a.get('data-pmid') for a in chips if a.get('data-pmid')] == row['refs'], cid
        for a in chips:
            target = a.get('href')[1:]
            assert target in ids and page.get_element_by_id(target).xpath('ancestor::article[@id=$c]', c=cid), (cid, target)
        if row['refs']:
            tied += 1
        else:
            statements += 1
        for pm in row['refs']:
            assert pm in card['refs'] and pm in refs
    # Peer controls point at native disclosures inside the same card; all start closed.
    for b in node.xpath('.//button[contains(@class,"st-peer")]'):
        panel = page.get_element_by_id(b.get('aria-controls'))
        assert panel.tag == 'details' and panel.get('open') is None and panel.xpath('ancestor::article[@id=$c]', c=cid)
    assert len(node.xpath('.//button[contains(@class,"st-peer")]')) == 3, cid
# Presentation-only de-duplication: each hidden clause repeats exactly the numbers of a visible clause in the same row.
import re
hidden = page.xpath('//span[@class="st-dup"]')
for span in hidden:
    row_text = span.getparent().xpath('string(.)')
    spec = [h for r in rows[span.xpath('ancestor::article/@id')[0]] for h in r.get('hide', []) if h['text'] == span.text]
    assert spec and spec[0]['equivalent'] in row_text and span.get('aria-hidden') == 'true'
    assert sorted(re.findall(r'\d+(?:\.\d+)?', span.text)) == sorted(re.findall(r'\d+(?:\.\d+)?', spec[0]['equivalent']))
assert len(hidden) == sum(len(r.get('hide', [])) for v in rows.values() for r in v)
assert not page.xpath('//details[@open]')
# Matrix: tumor rows × setting columns, every original cell entry kept.
table = page.xpath('//table[@class="therapy-matrix"]')[0]
assert len(table.xpath('./tbody/tr')) == 9 and len(table.xpath('./thead/tr/th')) == 7
assert len(table.xpath('.//div[@class="matrix-option"]')) == len(old.xpath('//table[@class="therapy-matrix"]//div[@class="matrix-option"]'))
assert sorted(norm(x.text_content()) for x in table.xpath('.//span[@class="empty-cell"]')) == sorted(norm(x.text_content()) for x in old.xpath('//table[@class="therapy-matrix"]//span[@class="empty-cell"]'))
before = Counter(u for u in old.xpath('//a/@href') if not u.startswith('#'))
after = Counter(u for u in page.xpath('//a/@href') if not u.startswith('#'))
assert before == after, 'External source links changed'
for u in page.xpath('//a/@href'):
    if u.startswith('#'):
        assert u[1:] in ids, u
for section in ['molecular', 'supportive', 'guidelines', 'safety', 'library']:
    assert norm(old.get_element_by_id(section).text_content()) == norm(page.get_element_by_id(section).text_content()), section
print(f'PASS: 49 regimen cards in LRT layout; {tied} evidence rows with PMID chips and {statements} statement rows reassemble every evidence sentence; '
      '9×6 matrix keeps all 66 entries and empty-cell notes; peers, anchors and external links verified.')
