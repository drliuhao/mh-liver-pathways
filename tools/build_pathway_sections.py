"""Build transplant/assets/pathway-sections.json: the four closing sections of each transplant pathway page.

usage: python3 tools/build_pathway_sections.py

The roadmaps end with Practice choices with limited evidence, Questions for consensus, Team responsibilities and
quality monitoring, and the Evidence library. The pathways now end the same way (Hao Liu, 29 October 2026):

- Practice choices with limited evidence, the protocol team description and its quality measures come from
  tools/transplant_sections/<slug>.json, extracted from the V16 standard and high-risk protocols and checked
  independently against them (see that folder's notes).
- Decision owners and timing come from the pathway's own steps in transplant/assets/content.json.
- Questions for consensus is an index, not a copy: each meeting question opens in the meeting record
  (#meeting-<id>) and each high-risk review in the high-risk view (#high-risk-<anchor>), where its positions,
  proposal and decision fields live once.
- The Evidence library lists every source the pathway cites (the same set as the #evidence view) plus the
  high-risk reviews' sources and those cited only by a limited-evidence item.
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
C = json.loads((ROOT / 'transplant/assets/content.json').read_text())
HR = C['high_risk']
SOURCES, HRS = C['sources'], HR['sources']
ORDER = ['hcc', 'pcca', 'icca', 'crlm', 'nelm', 'hehe', 'hca']


def pathway_refs(p):
    """Same set as allRefs() in transplant/assets/app.js."""
    ids = []
    add = lambda r: ids.append(r) if r not in ids else None
    for s in p['steps']:
        for g in s['orders']:
            for x in g['items']:
                for r in x['refs']: add(r)
        for b in s['branches']:
            for x in b['criteria']:
                for r in x['refs']: add(r)
            for r in b['refs']: add(r)
        for x in s['stops']:
            for r in x['refs']: add(r)
    for i in p['issues']:
        for c in i['comparisons']: add(c['ref'])
    for c in C['care'][p['slug']]:
        for r in c['refs']: add(r)
    for s in p['steps']:
        a = C['assistants'][f"{p['slug']}/{s['id']}"]
        for q in a['questions']:
            for r in q['refs']: add(r)
            for c in q['criteria']:
                for r in c['refs']: add(r)
        for rule in a['rules']:
            for r in rule['refs']: add(r)
    return ids


def ref(key):
    if key in SOURCES:
        s = SOURCES[key]
        return {'key': key, 'label': s['short'], 'dialog': True}
    s = HRS[key]
    url = f"https://pubmed.ncbi.nlm.nih.gov/{s['pmid']}/" if s.get('pmid') else s.get('url') or s.get('tmc') or ''
    return {'key': key, 'label': s['short'], 'url': url}


def source_row(key):
    if key in SOURCES:
        s = SOURCES[key]
        return {'key': key, 'short': s['short'], 'title': s['title'], 'kind': s.get('kind', ''), 'dialog': True}
    s = HRS[key]
    r = ref(key)
    meta = ' · '.join(str(x) for x in [s.get('author'), s.get('journal'), s.get('year')] if x)
    return {'key': key, 'short': s['short'], 'title': s['title'], 'kind': meta, 'url': r['url'], 'pmid': s.get('pmid') or ''}


def doc_name(text):
    """Locators name the Word documents by their new titles (Standard pathway / High-risk pathway)."""
    return (text or '').replace('Standard protocol', 'Standard pathway document').replace('High-risk protocol', 'High-risk pathway document') \
        .replace('high-risk protocol', 'high-risk pathway document').replace('standard protocol', 'standard pathway document')


out = {}
for slug in ORDER:
    p = next(x for x in C['index'] if x['slug'] == slug)
    src = json.loads((ROOT / f'tools/transplant_sections/{slug}.json').read_text())
    issues = {i['id'] for i in p['issues']}
    reviews = HR['pathways'][slug]['reviews']
    anchors = {r['id']: r['anchor'] for r in reviews}
    limited = []
    for it in src['limited']:
        for k in it.get('refs', []):
            assert k in SOURCES or k in HRS, (slug, k)
        rel = it.get('related')
        related = None
        if rel:
            if rel in issues:
                q = next(i for i in p['issues'] if i['id'] == rel)
                related = {'label': q['question'], 'href': f'#meeting-{rel}'}
            elif rel in anchors:
                r = next(r for r in reviews if r['id'] == rel)
                related = {'label': f"{rel} · {r['title']}", 'href': f"#high-risk-{anchors[rel]}"}
            else:
                raise SystemExit(f'{slug}: unknown related question {rel}')
        loc = doc_name(it['locator'])
        for st in p['steps']:
            loc = loc.replace(f"step '{st['id']}'", f"decision '{st['title']}'")
        assert "step '" not in loc, (slug, loc)
        limited.append({'t': it['t'], 'why': it['why'], 'setting': it['setting'], 'locator': loc,
                        'refs': [ref(k) for k in it.get('refs', [])], 'related': related})
    keys = pathway_refs(p)
    for r in reviews:
        for k in r['references']:
            if k not in keys: keys.append(k)
    for it in src['limited']:
        for k in it.get('refs', []):
            if k not in keys: keys.append(k)
    out[slug] = {
        'code': p['code'], 'name': p['name'],
        'limited': limited,
        'owners': [{'id': s['id'], 'title': s['title'], 'owner': s.get('owner', ''), 'timing': s.get('timing', '')} for s in p['steps']],
        'team': {'text': src.get('team'), 'locator': doc_name(src.get('team_locator'))} if src.get('team') else None,
        'quality': {'standard': [q['text'] for q in src['quality'] if q['setting'] == 'standard'],
                    'highrisk': [q['text'] for q in src['quality'] if q['setting'] == 'highrisk'],
                    'locator': doc_name(src.get('quality_locator'))},
        'questions': {'standard': [{'id': i['id'], 'question': i['question'], 'href': f"#meeting-{i['id']}"} for i in p['issues']],
                      'highrisk': [{'id': r['id'], 'title': r['title'], 'status': r['status'], 'href': f"#high-risk-{r['anchor']}"} for r in reviews]},
        'sources': [source_row(k) for k in keys],
    }
dest = ROOT / 'transplant/assets/pathway-sections.json'
dest.write_text(json.dumps({'about': 'Closing sections of the transplant pathway pages; built by tools/build_pathway_sections.py.', 'pathways': out},
                           ensure_ascii=False, indent=1) + '\n')
for slug, d in out.items():
    print(f"{slug:5} limited {len(d['limited']):2} · owners {len(d['owners'])} · quality {len(d['quality']['standard'])}+{len(d['quality']['highrisk'])} · "
          f"questions {len(d['questions']['standard'])}+{len(d['questions']['highrisk'])} · sources {len(d['sources'])}")
