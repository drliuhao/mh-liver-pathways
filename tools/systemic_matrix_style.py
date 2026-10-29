"""Rebuild the systemic therapy page in the structure of the liver-directed therapy matrix.

Presentation only. Every regimen paragraph, citation, link, PDF status, safety row and
source section is moved, not rewritten. Evidence rows are exact segments of each card's
own evidence sentence (tools/systemic_evidence_rows.json); the segments must reassemble
the original sentence, and each PMID chip points to that card's full citation.

Run on the published page:  python3 tools/systemic_matrix_style.py
Requires lxml. Idempotent: an already rebuilt page is left unchanged.
"""
from pathlib import Path
import copy
import json
from lxml import html, etree

ROOT = Path(__file__).resolve().parents[1]
VERSION = '20261029-docs1'
TUMORS = {'hcc': ('HCC', 'Hepatocellular carcinoma'), 'pcca': ('pCCA', 'Perihilar cholangiocarcinoma'),
          'icca': ('iCCA', 'Intrahepatic cholangiocarcinoma'), 'crlm': ('CRLM', 'Colorectal liver metastases'),
          'pdac': ('PDAC', 'Pancreatic adenocarcinoma'), 'pnet': ('pNET', 'Pancreatic neuroendocrine tumor'),
          'nelm': ('NELM', 'Neuroendocrine liver metastases'), 'ampullary': ('Ampullary', 'Ampullary cancer'),
          'chcca': ('cHCC–CCA', 'Combined HCC–cholangiocarcinoma')}
SETTINGS = {'first': ('Initial advanced disease', 'Initial advanced-disease treatment'),
            'biomarker': ('Molecularly selected', 'Molecularly selected treatment'),
            'later': ('Subsequent', 'Subsequent treatment'),
            'perioperative': ('Around curative local treatment', 'Around curative local treatment'),
            'combination': ('Combination / sequencing', 'Combination / sequencing evidence'),
            'transplant': ('Transplant strategy', 'Transplant strategy')}


def el(tag, text=None, **attrs):
    node = etree.Element(tag, {k.rstrip('_').replace('_', '-'): v for k, v in attrs.items()})
    node.text = text
    return node


def norm(s):
    return ' '.join(s.split())


def NUMS(s):
    import re
    return sorted(re.findall(r'\d+(?:\.\d+)?', s))


def rebuild(path=ROOT / 'systemic/index.html'):
    page = html.fromstring(path.read_text())
    if page.get('data-systemic-layout') == 'lrt-matrix':
        return False
    matrix = json.loads((ROOT / 'systemic/matrix.json').read_text())
    refs = json.loads((ROOT / 'systemic/references.json').read_text())
    rows = json.loads((ROOT / 'tools/systemic_evidence_rows.json').read_text())
    cards_data = {c['id']: c for c in matrix['cards']}
    page.set('data-systemic-layout', 'lrt-matrix')
    head = page.find('head')
    for link in head.findall('link'):
        if 'matrix.css' in link.get('href', ''):
            link.set('href', f'matrix.css?v={VERSION}')
    for script in head.findall('script'):
        src = script.get('src', '')
        if 'matrix.js' in src:
            script.set('src', f'matrix.js?v={VERSION}')
        if 'portal-navigation.js' in src:
            script.set('src', f'/mh-liver-pathways/assets/portal-navigation.js?v={VERSION}')
    main = page.xpath('//main')[0]
    main.set('class', (main.get('class') or '') + ' st-wrap')

    hero = main.find('header')
    eyebrow = hero.find('p[@class="eyebrow"]')
    eyebrow.text = 'Roadmaps / Treatment matrices · systemic therapy by tumor type'
    lede = [p for p in hero.findall('p') if not p.get('class')][0]
    lede.set('class', 'lede')
    lede.text = ('Choose a tumor and a treatment setting. Each card shows when to consider a regimen and its trial results, '
                 'with every PMID linked to the full citation; open Limits, Transplant or Sources for the rest.')

    # Views keep their four panels; labels follow the liver-directed matrix.
    views = main.find('nav[@class="matrix-views"]')
    views.set('class', 'matrix-views st-views')
    for button in views.findall('button'):
        button.text = {'options': 'By tumor', 'comparison': 'Matrix', 'precautions': 'Safety & transplant', 'library': 'References'}[button.get('data-view')]

    # Setting legend: role in the treatment sequence, not an evidence grade. It doubles as a filter.
    legend = el('div', class_='st-legend', id='setting-legend', role='group', aria_label='Treatment settings — select to filter')
    legend.append(el('span', 'Settings', class_='st-legend-label'))
    for key, (short, _long) in SETTINGS.items():
        legend.append(el('button', short, type='button', class_=f'st-chip st-{key}', data_setting_chip=key, aria_pressed='false'))
    legend.append(el('button', 'All settings', type='button', class_='st-clear', data_setting_chip='all', aria_pressed='true'))
    legend_note = el('p', 'Colour marks the treatment setting — its place in the treatment sequence. It is not an evidence grade or a ranking.', class_='st-legend-note')
    main.insert(main.index(views) + 1, legend)
    main.insert(main.index(legend) + 1, legend_note)

    # Tumor tabs in the LRT style: abbreviation over full name.
    tumor_nav = main.find('nav[@class="tool-tabs tumor-tabs"]')
    tumor_nav.set('class', 'tool-tabs tumor-tabs st-tumtabs')
    for button in tumor_nav.findall('button'):
        key = button.get('data-filter')
        label = button.text
        button.text = None
        button.append(el('strong', label))
        button.append(el('span', TUMORS[key][1] if key in TUMORS else 'Compare every tumor type'))

    # Treatment options: ladder of settings plus LRT-style cards.
    options = page.get_element_by_id('options')
    heading = options.find('div[@class="options-heading"]')
    heading.find('h2').text = 'Treatment options by setting'
    for button in heading.iter('button'):
        if button.get('id') == 'expand-options':
            button.text = 'Open all evidence details'
        if button.get('id') == 'collapse-options':
            button.text = 'Close all'
    ladder = el('div', class_='st-ladder', id='ladder', aria_label='Settings for the selected tumor')
    options.insert(options.index(heading) + 1, ladder)
    for group in options.xpath('./section[@class="setting-group"]'):
        key = group.get('data-setting-group')
        group.set('class', f'setting-group st-{key}')
        h3 = group.find('h3')
        h3.text = None
        h3.append(el('span', SETTINGS[key][1], class_=f'st-chip st-{key}'))
        grid = group.find('div[@class="regimen-grid"]')
        grid.set('class', 'regimen-grid st-cards')
        for card in grid.findall('article'):
            rebuild_card(card, cards_data[card.get('id')], refs, rows[card.get('id')])
    note = options.find('details[@class="matrix-reading-note"]')
    for p in note.findall('p'):
        if (p.text or '').startswith('Open an option to read its full clinical context.'):
            p.text = 'Each card shows when to consider the option and its evidence rows; open Limits, Transplant or Sources for the rest. Position labels describe the existing recommendations; they are not a new evidence grading.'

    rebuild_matrix(page)

    # Safety view: shown as cards, like the LRT contraindications view (opened by matrix.js).
    safety = page.get_element_by_id('safety')
    safety.find('div[@class="safety-grid"]').set('class', 'safety-grid st-cxgrid')

    path.write_text('<!doctype html>\n' + html.tostring(page, encoding='unicode', method='html') + '\n')
    return True


def rebuild_card(card, data, refs, segments):
    detail = card.find('details[@class="regimen-disclosure"]')
    summary = detail.find('summary')
    title = summary.xpath('.//span[@class="regimen-title"]')[0].text_content()
    badge = summary.xpath('.//span[@class="badge"]')[0]
    body = detail.find('div[@class="regimen-body"]')
    eyebrow = body.find('span[@class="eyebrow"]')
    paragraphs = body.findall('p')
    who, evidence, limits, transplant = paragraphs
    sources = body.find('details[@class="regimen-sources"]')
    card.remove(detail)

    head = el('div', class_='st-card-head')
    row1 = el('div', class_='st-row1')
    row1.append(el('h3', title, class_='st-title'))
    eyebrow.set('class', 'eyebrow st-tumors')
    row1.append(eyebrow)
    head.append(row1)
    badge.set('class', 'badge st-position')
    head.append(badge)
    card.append(head)

    content = el('div', class_='st-card-body')
    who.set('class', 'st-when')
    content.append(who)

    # Evidence rows: exact segments of this card's evidence sentence, each with its own PMID chip(s).
    original = evidence.xpath('string(.)')
    assert norm(original).startswith('Clinical evidence.'), data['id']
    assert ' '.join(s['text'] for s in segments) == data['evidence'], data['id']
    block = el('div', class_='evidence-result st-evidence')
    label = el('strong', 'Clinical evidence.', class_='st-sr')
    label.tail = ' '
    block.append(label)
    ul = el('ul', class_='ev')
    for i, seg in enumerate(segments):
        li = el('li', class_='st-ev-row' if seg['refs'] or seg.get('links') else 'st-ev-row st-ev-statement')
        keys = el('span', class_='st-ev-keys')
        for pm in seg['refs']:
            keys.append(el('a', None, class_='pm', href=f"#sources-{data['id']}-{pm}", data_pmid=pm,
                           aria_label=f"{refs[pm]['trial']} · PMID {pm} — full citation"))
        for index in seg.get('links', []):
            text, _url = data['links'][index]
            keys.append(el('a', None, class_='pm pm-link', href=f"#sources-{data['id']}-link{index}", data_label='Source',
                           aria_label=f'{text} — source link'))
        if len(keys):
            li.append(keys)
        res = el('span', None, class_='st-ev-text')
        text = seg['text']
        # Presentation-only de-duplication: a clause that repeats numbers stated again in the same row is
        # kept in the DOM (and in print/reading order) but not shown twice. Guarded for equivalence.
        hidden = seg.get('hide', [])
        for h in hidden:
            assert text.count(h['text']) == 1 and h['equivalent'] in text, (data['id'], h)
            assert NUMS(h['text']) == NUMS(h['equivalent']), (data['id'], h)
        pieces, rest = [], text
        for h in hidden:
            before, after = rest.split(h['text'], 1)
            pieces += [('t', before), ('h', h['text'])]
            rest = after
        pieces.append(('t', rest))
        last = None
        for kind, value in pieces:
            if kind == 't':
                if last is None:
                    res.text = (res.text or '') + value
                else:
                    last.tail = (last.tail or '') + value
            else:
                last = el('span', value, class_='st-dup', aria_hidden='true')
                res.append(last)
        li.append(res)
        li.tail = ' '
        ul.append(li)
    block.append(ul)
    content.append(block)

    # Peer details: Limits · Transplant · Sources (native disclosures; summaries hidden when scripted).
    peers = el('div', class_='st-peers', role='group', aria_label='Details for this option')
    panels = el('div', class_='st-panels')
    for key, node, label_text in [('limits', limits, 'Limits of the evidence'), ('transplant', transplant, 'Transplant implications')]:
        d = el('details', class_=f'st-panel st-panel-{key}', id=f"{key}-{data['id']}")
        d.append(el('summary', label_text))
        node.set('class', 'limits' if key == 'limits' else 'st-transplant')
        d.append(node)
        panels.append(d)
        peers.append(el('button', label_text, type='button', class_=f'st-peer st-peer-{key}', aria_controls=d.get('id'), aria_expanded='false'))
    sources.set('class', 'regimen-sources st-panel st-panel-sources')
    count = len(data['refs']) + len(data['links'])
    for li, pm in zip(sources.xpath('./ul/li'), data['refs']):
        li.set('id', f"sources-{data['id']}-{pm}")
    for paragraph in sources.findall('p'):
        for index, a in enumerate(paragraph.findall('a')):
            a.set('id', f"sources-{data['id']}-link{index}")
    panels.append(sources)
    peers.append(el('button', 'Sources', type='button', class_='st-peer st-peer-sources', aria_controls=sources.get('id'), aria_expanded='false', data_count=str(count)))
    content.append(peers)
    content.append(panels)
    card.append(content)


def rebuild_matrix(page):
    """Tumor rows × setting columns, as in the LRT matrix. Every cell entry and empty-cell note is reused."""
    table = page.xpath('//table[@class="therapy-matrix"]')[0]
    cells = {}
    for tr in table.xpath('./tbody/tr'):
        for td in tr.xpath('./td'):
            cells[(td.get('data-tumor'), tr.get('data-setting'))] = td
    thead = el('thead')
    hr = el('tr')
    hr.append(el('th', 'Tumor', scope='col', class_='st-corner'))
    for key, (short, long) in SETTINGS.items():
        th = el('th', None, scope='col', data_setting=key, class_=f'st-{key}')
        th.text = short
        hr.append(th)
    thead.append(hr)
    tbody = el('tbody')
    for tumor, (abbr, name) in TUMORS.items():
        tr = el('tr', data_tumor=tumor)
        th = el('th', abbr, scope='row')
        th.append(el('small', name))
        tr.append(th)
        for key in SETTINGS:
            td = cells[(tumor, key)]
            td.attrib.pop('data-tumor', None)
            td.set('data-setting', key)
            td.set('class', f'st-cell st-{key}')
            for option in td.xpath('./div[@class="matrix-option"]'):
                detail = option.find('details[@class="cell-sources"]')
                if detail is not None:
                    keys = detail.find('small')
                    option.remove(detail)
                    keys.set('class', 'st-keys')
                    option.append(keys)
            tr.append(td)
        tbody.append(tr)
    for child in list(table):
        table.remove(child)
    table.append(thead)
    table.append(tbody)
    table.set('class', 'therapy-matrix')
    comparison = page.get_element_by_id('comparison')
    comparison.find('h2').text = 'Systemic therapy matrix'
    for p in comparison.findall('p'):
        if p.get('class') == 'screen-note':
            p.text = 'Rows are tumor types and columns are treatment settings. Select a regimen for its evidence rows, limitations and sources. On a phone, choose a tumor to narrow the matrix or scroll it sideways.'


if __name__ == '__main__':
    print('rebuilt' if rebuild() else 'already rebuilt')
