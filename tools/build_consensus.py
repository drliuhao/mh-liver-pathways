"""Consensus questions per tumor, in one structure for the Word files and the web views.

usage: python3 tools/build_consensus.py

Writes documents/<tumor>/questions.json and assets/documents.json (the download manifest used by the
Documents corner). Three sets per tumor, where the setting exists:
  roadmap   the roadmap's "Decisions this programme still has to make" (tools/consensus_source/
            roadmap_<slug>.json: positions extracted from the roadmap's own cited content) plus its
            extrahepatic-disease question (tools/ehd_positions.json); PDAC also carries PDAC-B1/B2.
  standard  the pathway's meeting questions (content.json index[].issues).
  highrisk  the pathway's high-risk reviews (content.json high_risk), with the source wording
            recorded for each B question (tools/consensus_source/high_risk_questions.json), and the shared
            approval requirements that every high-risk view also shows.
Nothing here changes clinical content: every field is copied from those sources.
"""
import json, re
from pathlib import Path
from urllib.parse import quote

ROOT = Path(__file__).resolve().parents[1]
BASE = '/mh-liver-pathways/'
DATE = '29 October 2026'
C = json.loads((ROOT / 'transplant/assets/content.json').read_text())
EHD = json.loads((ROOT / 'tools/ehd_positions.json').read_text())
HQ = json.loads((ROOT / 'tools/consensus_source/high_risk_questions.json').read_text())
HR = C['high_risk']
HRSRC = HR['sources']
STEPS = {(p['slug'], st['id']): st['title'] for p in C['index'] for st in p['steps']}
STATUS = dict(re.findall(r"'([a-z0-9-]+)':\['(?:closed|mixed|review|research|open|study|safety|checklist|limited)','([^']+)'\]",
                         (ROOT / 'transplant/assets/high-risk.js').read_text()))

TUMORS = [
    dict(key='hcc', code='HCC', name='Hepatocellular carcinoma', roadmap='hcc', transplant='hcc'),
    dict(key='pcca', code='pCCA', name='Perihilar cholangiocarcinoma', roadmap='hilar', transplant='pcca'),
    dict(key='icca', code='iCCA', name='Intrahepatic cholangiocarcinoma', roadmap='icca', transplant='icca'),
    dict(key='crlm', code='CRLM', name='Colorectal liver metastases', roadmap='crlm', transplant='crlm'),
    dict(key='nelm', code='NELM', name='Neuroendocrine liver metastases', roadmap='nelm', transplant='nelm'),
    dict(key='hehe', code='HEHE', name='Hepatic epithelioid hemangioendothelioma', roadmap=None, transplant='hehe'),
    dict(key='hca', code='HCA', name='Hepatocellular adenoma', roadmap='adenoma', transplant='hca'),
    dict(key='chcca', code='cHCC-CCA', name='Combined hepatocellular–cholangiocarcinoma', roadmap='chcca', transplant=None),
    dict(key='pdac', code='PDAC', name='Pancreatic ductal adenocarcinoma', roadmap='pdac', transplant=None),
    dict(key='pnet', code='pNET', name='Pancreatic neuroendocrine tumor', roadmap='pnet', transplant=None),
    dict(key='ampullary', code='AMP', name='Ampullary tumors', roadmap='ampullary', transplant=None),
    dict(key='pcyst', code='PCYST', name='Pancreatic cysts', roadmap='pcyst', transplant=None),
    dict(key='incidental', code='INC', name='Incidental liver lesions', roadmap='incidental', transplant=None),
]
HR_LABEL = {'hehe': 'High-risk pathway (boundary addendum)', 'hca': 'High-risk pathway (boundary addendum)'}
# Extrahepatic-disease questions and not-applicable notes, by tumor key.
EHD_TUMOR = {'HCC': 'hcc', 'cHCC–CCA': 'chcca', 'iCCA': 'icca', 'pCCA': 'pcca', 'CRLM': 'crlm', 'NELM': 'nelm', 'pNET': 'pnet',
             'HEHE': 'hehe', 'PDAC': 'pdac', 'Ampullary': 'ampullary'}
EHD_NA = {'Hepatocellular adenoma': 'hca', 'Pancreatic cystic lesions': 'pcyst', 'Incidental liver lesions': 'incidental'}


def files(t):
    """Standardized file names (identical on the website and in the V17 package)."""
    c = t['code'].replace('-', '')
    f = {}
    if t['roadmap']:
        f['roadmap_info'] = f'{c}_1_Roadmap.docx'
        f['roadmap_questions'] = f'{c}_2_Roadmap_Questions.docx'
    if t['transplant']:
        f['standard_info'] = f'{c}_3_Standard_Pathway.docx'
        f['standard_questions'] = f'{c}_4_Standard_Pathway_Questions.docx'
        f['highrisk_info'] = f'{c}_5_High_Risk_Pathway.docx'
        f['highrisk_questions'] = f'{c}_6_High_Risk_Pathway_Questions.docx'
    f['decision'] = f'{c}_7_Decision_Discussion.docx'
    return f


def links_for(pmid='', doi='', url='', tmc='', pmc=''):
    L = {}
    if pmid: L['pubmed'] = f'https://pubmed.ncbi.nlm.nih.gov/{pmid}/'
    if doi: L['doi'] = 'https://doi.org/' + doi
    if pmc: L['pmc'] = pmc
    if url and url not in L.values(): L['url'] = url
    if tmc: L['tmc'] = tmc
    elif doi: L['tmc'] = 'https://libkey.io/libraries/480/' + doi
    return L


class Sources:
    def __init__(self): self.s = {}
    def add(self, key, short, title='', kind='', **links):
        if key and key not in self.s: self.s[key] = dict(short=short, title=title, kind=kind, links={k: v for k, v in links.items() if v})
        return key


def gate_names(slug):
    if slug == 'hcc':
        return dict(re.findall(r'\{id:"([^"]+)", tone:"[a-z]+", name:"([^"]+)"', (ROOT / 'hcc/index.html').read_text()))
    return {g['id']: g['name'] for g in json.loads((ROOT / f'{slug}/data/pathway.json').read_text())['gates']}


GATES = {t['roadmap']: gate_names(t['roadmap']) for t in TUMORS if t['roadmap']}


def roadmap_refs(slug):
    if slug == 'hcc':
        return {}, {}
    d = json.loads((ROOT / slug / 'data/pathway.json').read_text())
    return d['refs'], d['nonpm']


def roadmap_set(t, S):
    slug = t['roadmap']
    src = json.loads((ROOT / f'tools/consensus_source/roadmap_{slug}.json').read_text())
    refs, nonpm = roadmap_refs(slug)
    out = []
    # Extrahepatic-disease question for this roadmap first: it is the newest open position.
    for q in EHD['questions']:
        if q['setting'] == 'roadmap' and EHD_TUMOR.get(q['tumor']) == t['key']:
            out.append(ehd_question(q, S, 'roadmap', f'{slug}/#question-{q["id"]}'))
    for q in src['questions']:
        positions = []
        for p in q.get('positions', []):
            ref = str(p.get('ref') or '')
            key = None
            if ref in refs:
                r = refs[ref]; key = S.add('pm' + ref, r[0], r[2], r[1], **links_for(pmid=ref))
            elif ref in nonpm:
                r = nonpm[ref]; key = S.add('np-' + slug + '-' + ref, r[0], r[2], r[1], **links_for(url=r[3] if len(r) > 3 else ''))
            elif re.fullmatch(r'\d{6,9}', ref):
                key = S.add('pm' + ref, p['source'], '', '', **links_for(pmid=ref))
            positions.append(dict(source=p['source'], key=key, says=p['position'], locator=p.get('locator', '')))
        out.append(dict(id=q['id'], set='roadmap', title=q['question'], question=q['question'], kind=q['kind'],
                        status='OPEN — not yet decided', where=[dict(label=GATES[slug].get(str(d), f'Decision {d}'), url=f'{slug}/#decision-{d}') for d in q.get('decisions', [])],
                        positions=positions, divergence=q.get('divergence', ''), proposal=q.get('proposal', ''),
                        proposal_locator=q.get('proposal_locator', ''), rationale=q.get('rationale', ''), audit=q.get('audit', ''),
                        web=f'{slug}/#question-{q["id"]}'))
    ratify = [dict(id=r['id'], specialty=r['specialty'], question=r['question'], kind=r.get('kind', ''), proposal=r.get('proposal', ''),
                   proposal_locator=r.get('proposal_locator', ''),
                   positions=[dict(source=p['source'], key=None, says=p['position'], locator=p.get('locator', '')) for p in r.get('positions', [])])
              for r in src.get('ratify', [])]
    if t['key'] == 'pdac':
        for qid in ('PDAC-B1', 'PDAC-B2'):
            out.append(pdac_question(qid, S))
    return out, ratify


def pdac_question(qid, S):
    r = HQ[qid]; ps = HQ['_pdac_sources']
    for k, v in ps.items():
        S.add('hr-' + k, v['short'], v['title'], 'Study or consensus', **links_for(pmid=v.get('pmid', ''), doi=v.get('doi', ''), url=v.get('url', '')))
    return dict(id=qid, set='roadmap', title=r['question'], question=r['question'], kind='transplant (no PDAC transplant pathway)',
                status='OPEN — not activated; no PDAC transplant route', where=[], positions=positions_from_records(r['source_positions'], S),
                proposal=r['stance'] or '', rules=r['rules'] or [], rationale=r['rationale'] or '', tests=r['tests'] or '', allocation=r['allocation'] or '',
                owners=r['owner'] or '', note=r['roadmap'] or '', supporting=[ps[k]['short'] for k in r.get('supporting_refs', []) if k in ps],
                web='pdac/#question-' + qid)


def hr_source(key, S):
    s = HRSRC.get(key) or HQ['_pdac_sources'].get(key)
    if not s:
        return None
    pdf = next((x['url'] for x in s.get('pdf_links', []) if 'pmc.ncbi' in x.get('url', '')), '')
    return S.add('hr-' + key, s['short'], s.get('title', ''), 'Study, guidance or policy',
                 **links_for(pmid=s.get('pmid') or '', doi=s.get('doi') or '', url=s.get('url', ''), tmc=s.get('tmc', ''), pmc=pdf))


def positions_from_records(evidence, S):
    out = []
    for e in evidence or []:
        k = hr_source(e.get('key'), S)
        short = S.s[k]['short'] if k else e.get('key', '')
        out.append(dict(source=short, key=k, says=(('“' + e['quote'] + '”') if e.get('quote') else '') + (' ' + e['meaning'] if e.get('meaning') else ''),
                        locator=e.get('locator', '')))
    return out


def studies(review, S):
    out = []
    for s in review['evidence'].get('studies', []):
        k = hr_source(s.get('key'), S)
        out.append(dict(source=S.s[k]['short'] if k else s.get('key', ''), key=k, population=' '.join(x for x in [s.get('design_population', ''), s.get('selection', '')] if x),
                        results=s.get('results', ''), limits=s.get('limits', ''), locator=s.get('locator', '')))
    return out


def ehd_question(q, S, setting, web):
    rows = []
    for s in q['evidence']:
        src = EHD['sources'][s['key']]
        k = S.add('ehd-' + s['key'], src['short'], '', 'Study, guidance or policy', **src.get('links', {}))
        rows.append(dict(source=src['short'], key=k, population=(s['design_population'] + ' ' + s['selection']).strip(), results=s['results'],
                         limits=s['limits'], locator=s['locator'], read={'full': 'Full text read', 'abstract': 'Abstract only; full text pending'}.get(s['read'], '')))
    return dict(id=q['id'], set=setting, title=q['title'], question=q['question'], kind='clinical', status=q['status'] + ' · OPEN proposal',
                where=[], proposal=q['position'], rules=q['rules'], rationale=q['why'], studies=rows, counter=q['counter'],
                certainty=q['certainty'], change=q['change'], web=web)


def standard_set(t, S):
    p = next(x for x in C['index'] if x['slug'] == t['transplant'])
    out = []
    for i in p['issues']:
        pos = []
        for c in i['comparisons']:
            s = C['sources'][c['ref']]
            k = S.add('std-' + c['ref'], s['short'], s.get('title', ''), s.get('kind', ''), **links_for(url=s.get('url', '')))
            pos.append(dict(source=s['short'], key=k, kind=s.get('kind', ''), says=('“' + c['text'] + '”') if c['quote'] else c['text'],
                            locator=c.get('locator') or s.get('locator', '')))
        rid = i['record'].replace(' — detailed web subquestion', ' (detail)')
        steps = [s for s in p['steps'] if i['id'] in s.get('issues', [])]
        out.append(dict(id=rid, set='standard', title=i['question'], question=i['question'], kind='standard pathway', status=i['status'],
                        where=[dict(label=s['title'], url=f'transplant/{p["slug"]}/#{s["id"]}') for s in steps],
                        positions=pos, proposal=i['proposal'], rationale=i['rationale'], owners=i.get('owners', ''),
                        web=f'transplant/{p["slug"]}/#meeting-{i["id"]}'))
    return out


def review_question(r, slug, S, shared=False):
    rec = HQ.get(r['id'], {})
    ehd = next((q for q in EHD['questions'] if q['id'] == r['id']), None)
    question = rec.get('question') or (ehd['question'] if ehd else r['title'])
    ev = r['evidence']
    return dict(id=r['id'], set='highrisk', title=r['title'], question=question, kind='shared approval requirement' if shared else 'high-risk review',
                status=STATUS.get(r['anchor'], 'OPEN proposal') + ' · not activated', context=r.get('context', ''),
                where=[dict(label=STEPS.get((slug, s), s), url=f'transplant/{slug}/#{s}') for s in (r.get('steps') or []) if isinstance(s, str)],
                positions=positions_from_records(rec.get('source_positions'), S), proposal=r.get('stance', ''), rules=r.get('rules', []),
                tests=r.get('tests', ''), allocation=r.get('allocation', ''), rationale=ev.get('synthesis', ''), counter=ev.get('counterevidence', ''),
                certainty=ev.get('certainty', ''), threshold_basis=ev.get('threshold_basis', []), studies=studies(r, S),
                web=f'transplant/{slug}/#high-risk-{r["anchor"]}')


def highrisk_set(t, S):
    slug = t['transplant']
    qs = [review_question(r, slug, S) for r in HR['pathways'][slug]['reviews']]
    shared = [review_question(r, slug, S, True) for r in HR['readiness']]
    return qs, shared


manifest = {'generated': DATE, 'base': 'documents/', 'tumors': {}}
for t in TUMORS:
    S = Sources()
    sets = {}
    if t['roadmap']:
        qs, ratify = roadmap_set(t, S)
        sets['roadmap'] = dict(label='Roadmap', page=t['roadmap'] + '/', web=t['roadmap'] + '/#questions', questions=qs, ratify=ratify)
    if t['transplant']:
        sets['standard'] = dict(label='Standard pathway', page=f'transplant/{t["transplant"]}/', web=f'transplant/{t["transplant"]}/#meeting',
                                questions=standard_set(t, S))
        qs, shared = highrisk_set(t, S)
        sets['highrisk'] = dict(label=HR_LABEL.get(t['key'], 'High-risk pathway'), page=f'transplant/{t["transplant"]}/#high-risk',
                                web=f'transplant/{t["transplant"]}/#high-risk', questions=qs, shared=shared)
    na = [dict(id='EHD-' + t['code'], text=n['position']) for n in EHD['not_applicable'] if EHD_NA.get(n['tumor']) == t['key']]
    doc = dict(key=t['key'], code=t['code'], name=t['name'], generated=DATE, files=files(t), sets=sets, not_applicable=na, sources=S.s)
    out = ROOT / 'documents' / t['key']
    out.mkdir(parents=True, exist_ok=True)
    (out / 'questions.json').write_text(json.dumps(doc, ensure_ascii=False, indent=1) + '\n')
    manifest['tumors'][t['key']] = dict(code=t['code'], name=t['name'], roadmap=t['roadmap'], transplant=t['transplant'],
                                        files=files(t), counts={k: len(v['questions']) for k, v in sets.items()})
    print(f"{t['code']:9} " + ' · '.join(f'{k} {len(v["questions"])}' for k, v in sets.items()) + f' · {len(S.s)} sources')
(ROOT / 'assets/documents.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=1) + '\n')
