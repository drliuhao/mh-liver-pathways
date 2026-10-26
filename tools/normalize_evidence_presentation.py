"""Integrate evidence by topic without release-specific promotion.

Presentation only: retain stable source IDs, URLs, study text and clinical rules.
Run after a legacy evidence build; not a replacement for a clinical review.
"""
from pathlib import Path
from lxml import html, etree
import json, re

ROOT = Path(__file__).resolve().parents[1]
BASE = '/mh-liver-pathways/'

def serialize(tree):
    return '<!doctype html>\n' + html.tostring(tree, encoding='unicode', method='html')

def disclosure(article):
    """Keep the complete appraisal and stable anchor, with an ordinary disclosure."""
    article.tag = 'details'
    article.set('class', 'study-appraisal')
    heading = article.find('h3')
    if heading is not None:
        heading.tag = 'summary'
    return article

def text_only(node, value):
    for child in list(node):
        node.remove(child)
    node.text = value

def document_label(value):
    value = re.sub(r'^V\d+\s+', '', value).replace(' · DOCX', ' · Word')
    return value[:1].upper() + value[1:]

for slug in ['hcc', 'hilar', 'icca', 'crlm', 'pdac', 'chcca']:
    path = ROOT / slug / 'index.html'
    tree = html.fromstring(path.read_text())
    changed = False
    for notice in tree.xpath('//*[contains(concat(" ",normalize-space(@class)," ")," review-notice ")]'):
        if 'V12 evidence integration' in notice.text_content():
            notice.getparent().remove(notice); changed = True
    blocks = tree.xpath('//*[@id="v12-treatment-evidence" and self::section]')
    if blocks:
        block = blocks[0]
        evidence = tree.get_element_by_id('evidence')
        # The old anchor remains valid, but the content is part of the evidence library.
        group = html.Element('div', id='v12-treatment-evidence', attrib={'class':'study-appraisals'})
        for child in list(block):
            if child.tag == 'h2': continue
            if child.tag == 'article': child = disclosure(child)
            for link in child.xpath('.//a'):
                if 'complete roadmap DOCX' in link.text_content(): text_only(link, 'Roadmap document · Word')
            group.append(child)
        tree.get_element_by_id('evBody').append(group)
        block.getparent().remove(block); changed = True
    for group in tree.xpath('//*[@id="v12-treatment-evidence" and self::div]'):
        if group.getparent().get('id') != 'evBody':
            tree.get_element_by_id('evBody').append(group); changed = True
    if changed: path.write_text(serialize(tree))

for slug in ['hcc', 'pcca', 'icca', 'crlm']:
    path = ROOT / 'transplant/high-risk' / slug / 'index.html'
    tree = html.fromstring(path.read_text())
    blocks = tree.xpath('//*[@id="v12-full-text" and self::section]')
    if not blocks: continue
    block = blocks[0]
    # Put the current document beside the other document downloads, not above clinical content.
    current_link = block.xpath('./p/a[contains(@href,".docx")]')[0]
    text_only(current_link, 'High-risk protocol · Word')
    main = tree.xpath('//main')[0]
    download = html.Element('p'); download.append(current_link)
    footer = main.find('footer'); main.insert(list(main).index(footer), download)
    for link in main.xpath('./p/a'):
        if '/high-risk/docs/' in link.get('href', ''):
            text_only(link, 'Earlier protocol · ' + ('PDF' if link.get('href','').endswith('.pdf') else 'Word') + ' (archive)')
    if slug == 'hcc':
        question = block.get_element_by_id('hcc-b1-1')
        question.set('class', 'review-decision')
        for article in question.findall('article'): disclosure(article)
        first = tree.get_element_by_id('hcc-b1'); first.addnext(question)
        nav = tree.xpath('//nav[contains(@class,"tool-tabs")]')[0]
        link = html.Element('a', href='#hcc-b1-1'); link.text = 'B1.1. AFP-only failure / imaging discordance'
        nav.insert(1, link)
        # Stable historical fragment points to the integrated question, not a new banner.
        anchor = html.Element('span', id='v12-full-text'); question.insert(0, anchor)
    else:
        target = tree.get_element_by_id({'pcca':'pcca-b3','icca':'icca-b2','crlm':'crlm-b3'}[slug])
        group = html.Element('div', id='v12-full-text', attrib={'class':'study-appraisals'})
        for child in list(block):
            if child.tag == 'h2' or (child.tag == 'p' and not child.text_content().strip()): continue
            if child.tag == 'article': child = disclosure(child)
            group.append(child)
        target.append(group)
    block.getparent().remove(block)
    for node in tree.xpath('//header//*[not(*)]|//footer'):
        if node.text: node.text = node.text.replace('Transplant oncology · V7', 'Transplant oncology').replace('V7 source review', 'Source review')
    path.write_text(serialize(tree))

# Apply the same document naming to all seven high-risk routes, including addenda.
for path in (ROOT / 'transplant/high-risk').glob('*/index.html'):
    tree = html.fromstring(path.read_text()); changed = False
    for link in tree.xpath('//a'):
        label = link.text_content()
        if re.match(r'^V\d+\s+high-risk', label):
            text_only(link, document_label(label)); changed = True
    for node in tree.xpath('//header//*[not(*)]|//footer'):
        if node.text:
            value = node.text.replace('Transplant oncology · V7', 'Transplant oncology').replace('V7 source review', 'Source review')
            if value != node.text: node.text = value; changed = True
    if changed: path.write_text(serialize(tree))

# Preserve the existing URL as an ordinary, citable appraisal archive, not a featured release.
path = ROOT / 'evidence/2026-10-25/index.html'
tree = html.fromstring(path.read_text())
text_only(tree.find('head/title'), 'Study appraisals | MH HPB pathways')
text_only(tree.xpath('//h1')[0], 'Study appraisals')
for article in tree.xpath('//article[@class="regimen-card"]'): disclosure(article)
for node in tree.xpath('//footer'):
    node.text = 'Review record · 25 October 2026 · Local proposals remain OPEN.'
path.write_text(serialize(tree))

content_path = ROOT / 'transplant/assets/content.json'
data = json.loads(content_path.read_text())
designs={
    'AFP_RESPONSE':'Retrospective cohort','AFP_500':'Retrospective cohort',
    'AFP_SLOPE':'Retrospective cohort','AFP_NYCA':'Retrospective validation cohort',
    'AFP_OCCULT':'Retrospective cohort','SHARP':'Randomized phase III trial',
    'ASCO_BTC':'Clinical guidance','NALIRICC':'Randomized phase II trial',
    'MOUNTAINEER':'Noncomparative phase II study','SUNLIGHT':'Randomized phase III trial',
    'FRESCO2':'Randomized phase III trial','CASSANDRA':'Randomized phase III trial',
    'NAPOLI1':'Randomized phase III trial','MIXED_PRIMARY':'Retrospective cohort',
}
for key,design in designs.items():data['sources']['V12-'+key]['kind']=design
for pathway in data['index']:
    pathway['docs'] = [d for d in pathway['docs'] if d['url'] != pathway['protocol']]
    for doc in pathway['docs']: doc['label'] = document_label(doc['label'])
for pathway in data['high_risk']['pathways'].values():
    for doc in pathway.get('documents', []): doc['label'] = document_label(doc['label'])
for plans in data['care'].values():
    for plan in plans:
        # A release index is not a clinical next action. Study sources remain in plan.refs.
        plan['actions'] = [a for a in plan['actions'] if a.get('label') != 'V12 full-text appraisals']
content_path.write_text(json.dumps(data, ensure_ascii=False, indent=2))
(ROOT / 'tools/v12_content_snapshot.json').write_text(json.dumps(data, ensure_ascii=False, indent=2))
for path in (ROOT / 'transplant').rglob('*.html'):
    raw = path.read_text()
    m = re.search(r'(<script[^>]*id="protocol-data"[^>]*>)(.*?)(</script>)', raw, re.S)
    if not m: continue
    old = json.loads(m.group(2)); slug = (old.get('pathway') or {}).get('slug')
    payload = {**data, 'pathway':next((p for p in data['index'] if p['slug']==slug), None), 'mode':old.get('mode')}
    encoded = json.dumps(payload, ensure_ascii=False).replace('</', '<\\/')
    path.write_text(raw[:m.start(2)] + encoded + raw[m.end(2):])

# Prefixes are editorial provenance, not efficacy or recommendation strength.
for name in ['systemic/matrix.json', 'systemic/index.html']:
    path = ROOT / name
    raw = path.read_text().replace('Full-text update: ', '')
    path.write_text(raw)
print('Integrated topic evidence; neutral document labels; preserved sources and clinical rules.')
