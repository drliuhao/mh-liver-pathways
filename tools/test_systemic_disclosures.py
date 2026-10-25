"""Protect clinical text, metadata and links during the presentation-only change."""
from pathlib import Path
from collections import Counter
from urllib.parse import urlsplit
import json
import subprocess
from lxml import html

ROOT = Path(__file__).resolve().parents[1]
BASELINE = '33746b0'
old = html.fromstring(subprocess.check_output(['git', 'show', f'{BASELINE}:systemic/index.html'], cwd=ROOT))
new = html.fromstring((ROOT / 'systemic/index.html').read_text())
matrix = json.loads((ROOT / 'systemic/matrix.json').read_text())
refs = json.loads((ROOT / 'systemic/references.json').read_text())
norm = lambda s: ' '.join(s.split())

for file in ['matrix.json', 'references.json', 'publication-manifest.json']:
    assert (ROOT / 'systemic' / file).read_bytes() == subprocess.check_output(
        ['git', 'show', f'{BASELINE}:systemic/{file}'], cwd=ROOT), file
assert new.get('data-systemic-ui') == 'disclosures'
assert len(new.xpath('//article[@class="regimen-card"]')) == 49
assert len(new.xpath('//article[@class="library-entry"]')) == 96
assert len(new.xpath('//*[@class="matrix-panel"]')) == 4
assert not new.xpath('//details[@open]'), 'All explanatory disclosures start closed'
ids = [e.get('id') for e in new.xpath('//*[@id]')]
assert len(ids) == len(set(ids)), 'Duplicate IDs'
for card in matrix['cards']:
    node = new.get_element_by_id(card['id'])
    assert node.get('data-tumors').split() == card['tumors']
    assert node.get('data-setting') == card['setting']
    for key in ['title', 'position', 'who', 'evidence', 'limits', 'transplant']:
        assert norm(card[key]) in norm(node.text_content()), (card['id'], key)
    before = old.get_element_by_id(card['id'])
    assert before.xpath('.//a/@href') == [u for u in node.xpath('.//a/@href') if not u.startswith('#sources-')]
    for paragraph in before.findall('p'):
        assert norm(paragraph.text_content()) in norm(node.text_content()), card['id']
for before, after in zip(old.xpath('//article[@class="library-entry"]'), new.xpath('//article[@class="library-entry"]')):
    assert before.get('data-pdf') == after.get('data-pdf')
    assert before.get('data-tumors') == after.get('data-tumors')
    for child in before:
        assert norm(child.text_content()) in norm(after.text_content())
    assert before.xpath('.//a/@href') == after.xpath('.//a/@href')
for section_id in ['molecular', 'supportive', 'guidelines']:
    before, after = old.get_element_by_id(section_id), new.get_element_by_id(section_id)
    assert norm(before.text_content()) == norm(after.text_content()), section_id
    assert before.xpath('.//a/@href') == after.xpath('.//a/@href')
for before, after in zip(old.xpath('//table[@class="safety-table"]/tbody/tr'), new.xpath('//details[@class="safety-disclosure"]')):
    for cell in before:
        assert norm(cell.text_content()) in norm(after.text_content()), cell.text_content()
    assert before.xpath('.//a/@href') == after.xpath('.//a/@href')
before_links = Counter(u for u in old.xpath('//a/@href') if not u.startswith('#'))
after_links = Counter(u for u in new.xpath('//a/@href') if not u.startswith('#'))
assert before_links == after_links, 'Source/destination links changed'
for u in new.xpath('//a/@href'):
    if u.startswith('#'):
        assert u[1:] in ids, u
assert len(new.xpath('//div[@class="matrix-option"]')) == len(old.xpath('//table[@class="therapy-matrix"]//td/p'))
assert new.xpath('//button[@data-view="options"]/@aria-selected') == ['true']
assert new.xpath('//button[@data-filter="hcc"]/@aria-pressed') == ['true']
print('PASS: 49 complete regimen records, 96 reference records, all safety/molecular/guideline text and all external links unchanged; native disclosures and four views valid.')
