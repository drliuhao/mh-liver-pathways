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
- The Evidence library lists every source the pathway cites plus the high-risk reviews' sources and those cited
  only by a limited-evidence item, one row per publication (a paper filed under two source keys appears once), in
  the roadmaps' row format (assets/roadmap-evidence.js): citation, one-line summary, access links and "How far this
  one goes". The one-line summary of a PubMed paper is its compact study line (tools/compact_evidence_source.json:
  design and population, main result); other sources use tools/source_summaries.json (30 October 2026).
"""
import json, re
from pathlib import Path
import document_refs as DR

ROOT = Path(__file__).resolve().parents[1]
C = json.loads((ROOT / 'transplant/assets/content.json').read_text())
HR = C['high_risk']
SOURCES, HRS = C['sources'], HR['sources']
ORDER = ['hcc', 'pcca', 'icca', 'crlm', 'nelm', 'hehe', 'hca']
CATALOG = json.loads((ROOT / 'evidence-libraries/catalog.json').read_text())['publications']
DOI_PMID = {p['doi'].lower(): str(p['pmid']) for p in CATALOG.values() if p.get('doi') and p.get('pmid')}
STUDIES = json.loads((ROOT / 'tools/compact_evidence_source.json').read_text())['studies']
SUMMARIES = json.loads((ROOT / 'tools/source_summaries.json').read_text())['summaries']
POLICY = {'Allocation policy', 'NLRB guidance'}
GUIDANCE = {'Clinical guidance', 'Expert consensus', 'Pathology reporting standard', 'Supportive-care reference'}
GROUPS = ['Policy & review guidance', 'Guidelines & consensus', 'Studies', 'Drug labels']
DOCREC = {}  # sources the V16 documents cite that no site record holds: 'doc:<pmid or key>'
NONPM_GROUP = {'label': 'Drug labels', 'policy': 'Policy & review guidance', 'guidance': 'Guidelines & consensus', 'abstract': 'Studies'}


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


def record(key):
    return SOURCES.get(key) or HRS.get(key) or DOCREC[key]


def match_record(ref, keys):
    """The site record a document reference names: its key, PMID, DOI or title; a key already listed wins."""
    if ref.get('key') and (ref['key'] in SOURCES or ref['key'] in HRS):
        return ref['key']
    pool = list(keys) + [k for k in list(SOURCES) + list(HRS) if k not in keys]
    cite = DR.norm(ref['cite'])
    for test in (lambda k: ref['pmid'] and pmid_of(k) == ref['pmid'],
                 lambda k: ref['doi'] and doi_of(k) == ref['doi'],
                 lambda k: len(DR.norm(record(k).get('title'))) >= 30 and DR.norm(record(k).get('title'))[:90] in cite):
        hit = next((k for k in pool if not k.startswith('doc:') and test(k)), None)
        if hit:
            return hit
    return None


def doc_record(ref):
    """A library record for a document reference no site record holds."""
    item = ref.get('nonpm') or {}
    key = 'doc:' + (ref['pmid'] or item.get('key', ''))
    assert key != 'doc:', f'no PMID or key for document reference {ref["cite"][:70]}'
    if key not in DOCREC:
        tag = STUDIES[ref['pmid']]['label'] if ref['pmid'] in STUDIES else item.get('tag') or DR.tag_from_cite(ref['cite'])
        DOCREC[key] = {'short': tag, 'title': ref['cite'], 'pmid': ref['pmid'], 'doi': ref['doi'], 'url': '' if ref['pmid'] else ref['url'],
                       'kind': item.get('kind', '')}
    return key


def doi_of(key):
    s = record(key)
    m = re.search(r'10\.\d{4,9}/[^\s#?]+', s.get('url') or '')
    return (s.get('doi') or (m.group(0) if m else '')).rstrip('.').lower()


def pmid_of(key):
    """PMID from the source record, else from its DOI through the evidence-library catalog."""
    s = record(key)
    return str(s.get('pmid') or DOI_PMID.get(doi_of(key)) or DR.DOI_PMID.get(doi_of(key)) or '')


def group_of(key, pmid):
    s = record(key)
    if key in DOCREC and s.get('kind'):
        return NONPM_GROUP[s['kind']]
    if (key in SOURCES and s.get('kind') in POLICY) or (key in HRS and 'Organ Procurement' in (s.get('author') or '')):
        return GROUPS[0]
    if (key in SOURCES and s.get('kind') in GUIDANCE) or STUDIES.get(pmid, {}).get('design') in ('Guideline', 'Consensus'):
        return GROUPS[1]
    return GROUPS[2]


def citation(key):
    s = record(key)
    if key in DOCREC:
        return s['title']
    if key in SOURCES:
        return f"{s['title'].rstrip('.')}. {s.get('locator', '')}".strip()
    # A personal author is a surname (with initials); an organisation is named in full, without "et al.".
    author = s.get('author') or ''
    head = (f'{author}. ' if len(author.split()) >= 3 else f'{author} et al. ') if author else ''
    tail = '. '.join(str(x) for x in [s.get('journal'), s.get('year')] if x)
    return f"{head}{s['title'].rstrip('.')}." + (f' {tail}.' if tail else '')


def library(keys, standard, reviews, uses=None):
    """One row per publication, in citation order; the roadmaps' row fields (assets/roadmap-evidence.js)."""
    studies = {}
    for r in reviews:
        for st in r['evidence']['studies']:
            prev = studies.get(st['key'])
            if not prev or len(st.get('design_population', '') + st.get('results', '')) > len(prev.get('design_population', '') + prev.get('results', '')):
                studies[st['key']] = st
    rows, by_id = [], {}
    for key in keys:
        pmid = pmid_of(key)
        row = by_id.get(pmid or key)
        if row:
            row['keys'].append(key)
        else:
            row = by_id[pmid or key] = {'key': key, 'keys': [key], 'pmid': pmid}
            rows.append(row)
    out = []
    for row in rows:
        keys_ = row['keys']
        lead = next((k for k in keys_ if k in HRS and HRS[k].get('author')), keys_[0])
        s = record(lead)
        item = {'key': row['key'], 'keys': keys_, 'tag': record(keys_[0])['short'], 'cit': citation(lead),
                'group': group_of(keys_[0], row['pmid']) if keys_[0] in SOURCES else group_of(lead, row['pmid'])}
        if row['pmid']:
            item['pmid'] = row['pmid']
        doi = next((record(k).get('doi') for k in keys_ if record(k).get('doi')), '')
        if doi:
            item['doi'] = doi
        if not row['pmid']:
            url = next((record(k).get('url') or record(k).get('tmc') for k in keys_ if record(k).get('url') or record(k).get('tmc')), '')
            if url:
                item['url'] = url
        access = []
        for k in keys_:
            r = record(k)
            if r.get('pdf'):
                access.append({'label': 'Full PDF', 'url': r['pdf']})
            for l in r.get('pdf_links', []):
                access.append({'label': l['label'], 'url': l['url']})
        if access:
            item['access'] = list({a['url']: a for a in access}.values())
        st = STUDIES.get(row['pmid'])
        line = next((SUMMARIES[f'transplant:{k}'] for k in keys_ if f'transplant:{k}' in SUMMARIES), None)
        if st:
            item['summary'] = {'lead': st['arms'], 'text': st['result']}
        else:
            assert line, f'no one-line summary for transplant:{keys_[0]} (add it to tools/source_summaries.json)'
            item['summary'] = {'lead': '', 'text': line}
        appraisal = {}
        note = next((record(k).get('note') for k in keys_ if record(k).get('note')), '')
        if note:
            appraisal['note'] = note
        hs = next((studies[k] for k in keys_ if k in studies), None)
        if hs:
            for src, dst in [('design_population', 'scope'), ('results', 'results'), ('limits', 'limitations'), ('locator', 'locator')]:
                if hs.get(src):
                    appraisal[dst] = hs[src]
        used = [u for k in keys_ for u in (uses or {}).get(k, [])]
        if used:
            appraisal = {'cited': DR.cited(used), **appraisal}
        if appraisal:
            item['appraisal'] = appraisal
        if not any(k in standard for k in keys_):
            item['flag'] = 'High-risk pathway'
        out.append(item)
    order = {g: i for i, g in enumerate(GROUPS)}
    return sorted(out, key=lambda x: order[x['group']])


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
    standard = set(keys) | {k for it in src['limited'] if it['setting'] == 'standard' for k in it.get('refs', [])}
    for r in reviews:
        for k in r['references']:
            if k not in keys: keys.append(k)
    for it in src['limited']:
        for k in it.get('refs', []):
            if k not in keys: keys.append(k)
    # Every reference of the pathway's two Word documents (30 October 2026): a source a site record holds joins under
    # its key; any other gets a document record. Each row says where the documents cite it.
    uses = {}
    for name, setting in DR.documents('transplant', slug):
        for dref in DR.resolved(name):
            key = match_record(dref, keys) or doc_record(dref)
            if key not in keys: keys.append(key)
            if setting == 'standard': standard.add(key)
            uses.setdefault(key, []).append((setting, dref['label']))
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
        'sources': library(keys, standard, reviews, uses),
    }
dest = ROOT / 'transplant/assets/pathway-sections.json'
dest.write_text(json.dumps({'about': 'Closing sections of the transplant pathway pages; built by tools/build_pathway_sections.py.', 'pathways': out},
                           ensure_ascii=False, indent=1) + '\n')
for slug, d in out.items():
    print(f"{slug:5} limited {len(d['limited']):2} · owners {len(d['owners'])} · quality {len(d['quality']['standard'])}+{len(d['quality']['highrisk'])} · "
          f"questions {len(d['questions']['standard'])}+{len(d['questions']['highrisk'])} · sources {len(d['sources'])}")
