"""Keep additions inside the original roadmap evidence library, not release silos.

Presentation-only and idempotent. Source IDs, clinical text, citations and all
access URLs survive. Run after any legacy evidence/presentation build.
"""
from pathlib import Path
import json
import re
from lxml import html, etree

ROOT = Path(__file__).resolve().parents[1]
BASE = '/mh-liver-pathways/'
VERSION = '20261026-library1'
SLUGS = ['hcc', 'hilar', 'icca', 'crlm', 'nelm', 'chcca', 'pdac', 'pnet', 'ampullary', 'pcyst', 'adenoma', 'incidental']

def dumps(value):
    return json.dumps(value, ensure_ascii=False, indent=2)

def unify():
    sources = json.loads((ROOT / 'transplant/assets/content.json').read_text())['sources']
    by_doi = {v.get('doi', '').lower(): v for k,v in sources.items() if k.startswith('V12-')}
    systemic = json.loads((ROOT / 'systemic/references.json').read_text())
    for slug in SLUGS:
        path = ROOT / slug / 'index.html'
        raw = path.read_text()
        tree = html.fromstring(raw)
        group = tree.xpath('//*[@id="v12-treatment-evidence" and contains(@class,"study-appraisals")]')
        if group:
            group = group[0]
            papers = []
            for article in group.xpath('./details[contains(@class,"study-appraisal")]'):
                url = article.xpath('.//a[starts-with(@href,"https://doi.org/")]/@href')[0]
                doi = url.split('doi.org/', 1)[1]
                source = by_doi[doi.lower()]
                nested = article.find('details')
                paragraphs = [p.text_content() for p in nested.findall('p')]
                application = article.find('p').text_content().removeprefix('Application.').strip()
                pmid = source['pmid']
                ref = systemic.get(pmid, {})
                citation = ' '.join(str(ref[k]) for k in ['author', 'title', 'journal', 'year'] if ref.get(k))
                citation = citation or source['title']
                citation += f' DOI: {doi}. PMID: {pmid}.'
                category = 'Systemic & targeted therapy' if slug == 'pdac' else 'Systemic therapy'
                if source['kind'] == 'Clinical guidance': category = 'Guidelines & policy'
                if slug == 'hcc' and article.get('id', '').startswith('afp_'): category = 'Transplant & downstaging'
                papers.append({'id':article.get('id'), 'pmid':pmid, 'tag':source['short'], 'cit':citation,
                    'doi':doi, 'group':category, 'design':source['kind'], 'depot':True,
                    'access':[{'label':a.text_content(), 'url':a.get('href')} for a in article.xpath('./p/a')],
                    'appraisal':{'application':application, 'population':paragraphs[0], 'results':paragraphs[1],
                                 'limitations':paragraphs[2], 'locator':' '.join(paragraphs[3:])}})
            payload = etree.Element('script', type='application/json', id='roadmap-evidence-data')
            payload.text = dumps({'papers':papers}).replace('</', '<\\/')
            context = etree.Element('details', id='v12-treatment-evidence', attrib={'class':'more evidence-context'})
            etree.SubElement(context, 'summary').text = 'Scope and interpretation'
            body = etree.SubElement(context, 'div', attrib={'class':'moreinner'})
            for p in list(group.findall('p')):
                if p.text: p.text = p.text.replace('This is a cancer-treatment roadmap update only.', 'This evidence applies to the cancer-treatment roadmap only.')
                body.append(p)
            group.getparent().replace(group, context)
            context.addnext(payload)
            raw = '<!doctype html>\n' + html.tostring(tree, encoding='unicode', method='html')
        # A shared renderer uses the original card and critique disclosure for all papers.
        if 'roadmap-evidence.js' not in raw:
            raw = raw.replace('</head>', f'<link rel="stylesheet" href="{BASE}assets/roadmap-evidence.css?v={VERSION}"><script src="{BASE}assets/roadmap-evidence.js?v={VERSION}"></script></head>')
            raw = re.sub(r'function evRow\(r\)\{.*?\n\}', 'function evRow(r){ return RoadmapEvidence.row(r, CRIT);\n}', raw, count=1, flags=re.S)
            raw = re.sub(r'function critText\(r\)\{.*?\n\}', 'function critText(r){ return RoadmapEvidence.text(r, CRIT);\n}', raw, count=1, flags=re.S)
            raw = raw.replace('function renderEv(){', 'function renderEv(){\n  RoadmapEvidence.merge(ALL);')
            raw = raw.replace('const GROUPS = [...new Set(ALL.map(r=>r.group))];', 'RoadmapEvidence.merge(ALL);\nconst GROUPS = [...new Set(ALL.map(r=>r.group))];')
            raw = raw.replace('const groups = [...new Set(ALL.map(r=>r.group))];', 'RoadmapEvidence.merge(ALL);\n  const groups = [...new Set(ALL.map(r=>r.group))];')
            raw = raw.replace('rows.length + " of " + ALL.length + " sources";', 'rows.length + " of " + ALL.length + " sources";\n  RoadmapEvidence.reveal();')
            # Existing deep links, including old appraisal and TMC-only IDs, open the one card.
            bridge = '''
window.addEventListener('hashchange', () => {
  let id; try { id = decodeURIComponent(location.hash.slice(1)); } catch { return; }
  if (!ALL.some(r => id === 'ev-' + r.id || (r.aliases || []).some(a => id === a || id === 'ev-' + a))) return;
  evGroup = 'All'; evQuery = ''; document.getElementById('evSearch').value = '';
  document.querySelectorAll('#evGroups .tab').forEach(b => b.setAttribute('aria-selected', String(b.dataset.group === 'All')));
  renderEv();
});
'''
            end = raw.rfind('</script>')
            raw = raw[:end] + bridge + raw[end:]
        raw = raw.replace('data/pathway.json?v=20261023-language', f'data/pathway.json?v={VERSION}')
        raw = raw.replace(', Batch 09 HAI update (15 October 2026), filtered', ', filtered')
        raw = raw.replace('group:"Liver-directed ("+P.short+")"', 'group:"Liver-directed"').replace('group:"Liver-directed (HCC)"', 'group:"Liver-directed"')
        raw = raw.replace('const el = document.getElementById("ev-"+c.dataset.ref);', 'const el = document.getElementById("ev-"+c.dataset.ref)?.closest(".ev");')
        raw = raw.replace('const el = document.getElementById("ev-"+id);', 'const el = document.getElementById("ev-"+id)?.closest(".ev");')
        path.write_text(raw)

        data_path = ROOT / slug / 'data/pathway.json'
        if not data_path.exists(): continue
        data = json.loads(data_path.read_text())
        before = dumps(data)
        for key, ref in list(data['refs'].items()) + list(data['nonpm'].items()):
            if not ref[1].startswith('HAI '): continue
            target = key.removeprefix('tmc')
            ref[1] = 'Transplant' if target == '37210451' else 'Guidelines & policy' if target == '39962001' else 'Liver-directed'
        for topic in data.get('quickref', []):
            if topic.get('title') == 'HAI evidence and programme update · 15 October 2026':
                topic['title'] = 'Hepatic arterial infusion: selection, evidence and delivery'
            for row in topic.get('rows', []):
                if row[0] == 'Adjuvant HAI: updated evidence': row[0] = 'Adjuvant HAI: randomized evidence'
        if before != dumps(data): data_path.write_text(dumps(data) + '\n')

    changes = ROOT / 'changes/index.html'
    history = changes.read_text()
    note = 'Consolidated roadmap evidence into the original searchable paper cards and clinical-topic categories. HAI papers and later appraisals no longer form dated add-on groups; duplicate TMC access entries are links on the paper card. Study results, limitations, clinical rules and historical citation anchors are retained.'
    if note not in history:
        marker = '<h2>26 October 2026</h2><ul>'
        assert marker in history, 'Change-log date marker missing'
        changes.write_text(history.replace(marker, marker + '<li>' + note + '</li>', 1))

if __name__ == '__main__':
    unify()
    print('Integrated roadmap appraisals and HAI access records into the original evidence libraries.')
