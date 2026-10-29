"""Presentation-only transform of the published systemic matrix.

Reuses every clinical paragraph, citation and PDF status. Run after the evidence
builder; native disclosures also work without JavaScript. Requires lxml.
"""
from pathlib import Path
from lxml import html, etree

ROOT = Path(__file__).resolve().parents[1]
VERSION = '20261025-disclosures1'
SETTINGS = {
    'first': 'Initial advanced-disease treatment',
    'biomarker': 'Molecularly selected treatment',
    'later': 'Subsequent treatment',
    'perioperative': 'Around curative local treatment',
    'combination': 'Combination / sequencing evidence',
    'transplant': 'Transplant strategy',
}


def el(tag, text=None, **attrs):
    node = etree.Element(tag, {k.rstrip('_').replace('_', '-'): v for k, v in attrs.items()})
    node.text = text
    return node


def disclosure(section):
    section.tag = 'details'
    section.set('class', 'context-disclosure')
    heading = section.find('h2')
    summary = el('summary', heading.text_content())
    section.remove(heading)
    body = el('div', class_='context-body')
    for child in list(section):
        body.append(child)
    section.append(summary)
    section.append(body)


def enhance(path=ROOT / 'systemic/index.html', source_html=None):
    page = html.fromstring(source_html if source_html is not None else path.read_text())
    if page.get('data-systemic-ui') == 'disclosures':
        return
    page.set('data-systemic-ui', 'disclosures')
    head = page.find('head')
    head.append(el('link', rel='stylesheet', href=f'matrix.css?v={VERSION}'))
    for script in head.findall('script'):
        if 'matrix.js' in script.get('src', ''):
            script.set('src', f'matrix.js?v={VERSION}')
        if 'portal-navigation.js' in script.get('src', ''):
            script.set('src', '/mh-liver-pathways/assets/portal-navigation.js?v=20261029-ehd1')
    main = page.xpath('//main')[0]
    hero = main.find('header')
    hero.findall('p')[-1].text = 'Choose a tumor and treatment setting. Expand a regimen for its evidence, limitations, transplant implications and source links.'
    notice = main.xpath('./div[@class="review-notice"]')[0]
    notice.tag = 'details'
    notice.set('class', 'review-disclosure')
    strong = notice.find('strong')
    text = strong.tail or ''
    strong.tail = None
    notice.remove(strong)
    summary = el('summary')
    summary.append(strong)
    notice.insert(0, summary)
    notice.append(el('p', text.strip()))
    hero.append(el('p', 'Multidisciplinary review aid, not prescribing orders. Cross-trial survival medians do not rank treatments.', class_='matrix-caution'))
    old_nav = main.xpath('./nav[@class="jump-links"]')[0]
    old_nav.getparent().remove(old_nav)
    views = el('nav', class_='matrix-views', role='tablist', aria_label='Matrix views')
    for key, label in [('options', 'By tumor'), ('comparison', 'Comparison matrix'), ('precautions', 'Safety & transplant'), ('library', 'References')]:
        views.append(el('button', label, type='button', role='tab', id=f'tab-{key}', data_view=key,
                        aria_controls=f'view-{key}', aria_selected='true' if key == 'options' else 'false',
                        tabindex='0' if key == 'options' else '-1'))
    tumor_nav = main.xpath('./nav[@class="tool-tabs"]')[0]
    main.insert(main.index(tumor_nav), views)
    tumor_nav.set('class', 'tool-tabs tumor-tabs')
    for button in tumor_nav.findall('button'):
        button.set('aria-pressed', 'true' if button.get('data-filter') == 'hcc' else 'false')
    all_button = tumor_nav.find('button')
    all_button.text = 'All tumors'
    tumor_nav.remove(all_button)
    tumor_nav.append(all_button)
    toolbar = main.xpath('./div[@class="matrix-toolbar"]')[0]
    toolbar.set('id', 'treatment-controls')
    toolbar.set('class', 'matrix-toolbar treatment-controls')
    toolbar.find('input').set('placeholder', 'Regimen, biomarker or trial…')
    main.insert(main.index(toolbar) + 1, el('p', class_='selection-context', id='selection-context', aria_live='polite'))

    options = page.get_element_by_id('options')
    options.find('h2').text = 'Treatment options'
    options.find('p').set('class', 'screen-note abbreviations')
    options.insert(1, el('p', 'Open an option to read its full clinical context. Position labels describe the existing recommendations; they are not a new evidence grading.', class_='screen-note'))
    controls = el('div', class_='disclosure-controls')
    controls.append(el('button', 'Expand visible options', type='button', id='expand-options'))
    controls.append(el('button', 'Collapse all', type='button', id='collapse-options'))
    options.insert(2, controls)
    heading_row = el('div', class_='options-heading')
    heading_row.append(options.find('h2'))
    heading_row.append(controls)
    options.insert(0, heading_row)
    help_note = el('details', class_='matrix-reading-note')
    help_note.append(el('summary', 'How to read this matrix & abbreviations'))
    for paragraph in list(options.findall('p')):
        if paragraph.get('id') != 'no-results':
            help_note.append(paragraph)
    options.append(help_note)
    grid = options.xpath('./div[@class="regimen-grid"]')[0]
    cards = list(grid)
    groups = {}
    for key, label in SETTINGS.items():
        group = el('section', class_='setting-group', data_setting_group=key)
        group.append(el('h3', label))
        group.append(el('div', class_='regimen-grid'))
        options.insert(options.index(grid), group)
        groups[key] = group
    for card in cards:
        top = card.find('div')
        badge = top.find('span[@class="badge"]')
        eyebrow = top.find('span[@class="eyebrow"]')
        heading = card.find('h3')
        title = heading.text_content()
        card.remove(top)
        card.remove(heading)
        detail = el('details', class_='regimen-disclosure')
        summary = el('summary')
        label = el('span', class_='regimen-label')
        label.append(el('span', title, class_='regimen-title'))
        label.append(badge)
        summary.append(label)
        summary.append(el('span', 'Details', class_='disclosure-hint', aria_hidden='true'))
        detail.append(summary)
        body = el('div', class_='regimen-body')
        body.append(eyebrow)
        for child in list(card):
            body.append(child)
        source = body.find('details')
        source.set('class', 'regimen-sources')
        source.set('id', 'sources-' + card.get('id'))
        evidence = body.find('p[@class="evidence-result"]')
        evidence.append(el('a', 'Trials and source links ↓', href='#' + source.get('id'), class_='evidence-source-link'))
        detail.append(body)
        card.append(detail)
        groups[card.get('data-setting')].find('div').append(card)
    options.remove(grid)
    comparison = page.get_element_by_id('comparison')
    comparison.find('h2').text = 'Compare treatment settings'
    comparison.insert(2, el('button', 'Compare all tumors', type='button', id='compare-all', class_='quiet-button'))
    for cell in comparison.xpath('.//td'):
        for paragraph in cell.findall('p'):
            paragraph.tag = 'div'
            paragraph.set('class', 'matrix-option')
            smalls = paragraph.findall('small')
            if len(smalls) > 1:
                detail = el('details', class_='cell-sources')
                detail.append(el('summary', 'Evidence preview'))
                detail.append(smalls[-1])
                paragraph.append(detail)

    precautions = el('section', id='precautions')
    precautions.append(el('h2', 'Safety and transplant context'))
    precautions.append(el('p', 'Choose a drug class to review reasons to avoid, delay or seek specialist input. Regimen-specific transplant implications remain inside each treatment option.', class_='screen-note'))
    safety = page.get_element_by_id('safety')
    safety_table = safety.find('table')
    safety_grid = el('div', class_='safety-grid')
    for row in safety_table.xpath('./tbody/tr'):
        name, avoid, implications = list(row)
        detail = el('details', class_='safety-disclosure')
        detail.append(el('summary', name.text_content()))
        body = el('div', class_='context-body')
        body.append(el('h4', 'Reasons to avoid, delay or obtain specialist review'))
        avoid.tag = 'div'
        body.append(avoid)
        body.append(el('h4', 'Practical implications and sources'))
        implications.tag = 'div'
        body.append(implications)
        detail.append(body)
        safety_grid.append(detail)
    safety.replace(safety_table, safety_grid)
    safety.find('h2').text = 'Drug-class precautions'
    precautions.append(safety)
    for key in ['molecular', 'supportive']:
        section = page.get_element_by_id(key)
        disclosure(section)
        precautions.append(section)
    library = page.get_element_by_id('library')
    library.find('h2').text = 'Papers and source documents'
    for paper in library.xpath('.//article[@class="library-entry"]'):
        title = paper.find('p[@class="paper-title"]')
        paper.remove(title)
        detail = el('details', class_='paper-disclosure')
        detail.append(el('summary', title.text_content()))
        body = el('div', class_='paper-body')
        for child in list(paper):
            body.append(child)
        detail.append(body)
        paper.append(detail)
    guidelines = page.get_element_by_id('guidelines')
    disclosure(guidelines)
    library.insert(3, guidelines)
    footer = main.find('footer')
    for key, section in [('options', options), ('comparison', comparison), ('precautions', precautions), ('library', library)]:
        panel = el('div', id=f'view-{key}', class_='matrix-panel', role='tabpanel', aria_labelledby=f'tab-{key}', tabindex='0')
        panel.append(section)
        main.insert(main.index(footer), panel)
    main.insert(main.index(views), el('noscript', 'JavaScript is off: all sections are shown. Open each disclosure to read the details.'))
    path.write_text('<!doctype html>\n' + html.tostring(page, encoding='unicode', method='html') + '\n')


if __name__ == '__main__':
    enhance()
