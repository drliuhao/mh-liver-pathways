"""Build assets/document-references.js: the sources each roadmap's Word document cites that its web library lacks.

usage: python3 tools/build_document_references.py

Hao Liu, 30 October 2026: "make all the library complete in both protocol/pathways and the roadmaps". A roadmap
page's evidence library is built from its pathway data (refs, non-PMID sources, appraised papers and the
liver-directed matrix papers its cells cite). The V16 roadmap documents add reference lists the pages never took
in (previously treated extrahepatic disease, drug labels, regulatory notices). This file lists, per roadmap, every
document reference the page lacks, as library rows that assets/roadmap-evidence.js merges in: tag, clinical
category, the document's citation, PubMed/DOI identity, where the document cites it and, for a source without a
PMID, its one-line summary (tools/source_summaries.json). PubMed papers take their compact study line.

The transplant pathways take their documents' references in tools/build_pathway_sections.py.
"""
import json, re
from pathlib import Path
import document_refs as R

ROOT = Path(__file__).resolve().parents[1]
STUDIES = json.loads((ROOT / 'tools/compact_evidence_source.json').read_text())['studies']
SUMMARIES = json.loads((ROOT / 'tools/source_summaries.json').read_text())['summaries']
SLUGS = ['adenoma', 'ampullary', 'chcca', 'crlm', 'hcc', 'hilar', 'icca', 'incidental', 'nelm', 'pcyst', 'pdac', 'pnet']

# Clinical category of an added row on each roadmap (its own tab names): drug labels and regulatory notices go to
# the page's systemic tab, guidelines to Guidelines & policy, and the papers on previously treated extrahepatic
# disease to the page's surgical or oligometastatic tab unless named below.
SYSTEMIC = {'crlm': 'Systemic therapy', 'hcc': 'Systemic therapy', 'hilar': 'Systemic therapy', 'icca': 'Systemic therapy',
            'pdac': 'Systemic & targeted therapy', 'nelm': 'Systemic therapy', 'pnet': 'Systemic therapy', 'ampullary': 'Systemic therapy',
            'chcca': 'Systemic therapy'}
SURGICAL = {'ampullary': 'Surgery', 'chcca': 'Surgery', 'crlm': 'Resection', 'hcc': 'Resection & ablation', 'hilar': 'Resection',
            'icca': 'Resection', 'nelm': 'Resection', 'pdac': 'Oligometastatic disease', 'pnet': 'Surgery'}
GROUP = {
    # HCC: immunotherapy before transplant, systemic trials, radiotherapy for extrahepatic disease, nodal staging.
    '40042053': 'Transplant & downstaging', '39255928': 'Transplant & downstaging', '37760542': 'Transplant & downstaging',
    '29433850': 'Systemic therapy', '37796513': 'Systemic therapy', '38467379': 'Radiotherapy', '39299553': 'Radiotherapy',
    '23532111': 'Resection & ablation',
    # iCCA and hilar: nodal staging; HAI pump before transplant.
    '42804100': 'Staging & risk', '33079246': 'Staging & risk', '40317676': 'Staging & risk', '37210451': 'Transplant',
    # Ampullary nodal staging; NET bone metastases; NCCN ampullary guideline.
    '42905970': 'Staging & risk', '40778558': 'Staging & risk', '37433437': 'Guidelines & policy',
    # PDAC consensus and trial protocols stay with oligometastatic disease.
}
NONPM_GROUP = {'label': None, 'guidance': 'Guidelines & policy', 'abstract': 'Liver-directed', 'policy': 'Guidelines & policy'}


def page_library(slug):
    lib = R.Library()
    page = (ROOT / f'{slug}/index.html').read_text()
    if slug == 'hcc':
        blk = page[page.index('const REF = {') + 12:]
        refs = json.loads(blk[:blk.index('};') + 1])
        blk = page[page.index('const NONPM =') + 13:]
        nonpm = json.loads(blk[:blk.index('};') + 1])
        matrix = 'hcc'
    else:
        p = json.loads((ROOT / f'{slug}/data/pathway.json').read_text())
        refs, nonpm, matrix = p.get('refs', {}), p.get('nonpm', {}), p.get('matrix')
    for pmid, v in refs.items():
        lib.add(pmid=pmid, cit=v[2] if len(v) > 2 else '', tag=v[0], key=pmid)
    for key, v in nonpm.items():
        lib.add(key=key, cit=v[2], tag=v[0])
    m = re.search(r'<script[^>]*id="roadmap-evidence-data"[^>]*>(.*?)</script>', page, re.S)
    for paper in (json.loads(m.group(1))['papers'] if m else []):
        lib.add(pmid=paper.get('pmid', ''), doi=paper.get('doi', ''), cit=paper.get('cit', ''), tag=paper.get('tag', ''), key=paper.get('id', ''))
    mx = ROOT / f'{slug}/data/lrt_matrix.json'
    if matrix and mx.exists():
        used = {e[1] for k, c in json.loads(mx.read_text())['cells'].items() if k.startswith(matrix + '|')
                for role in c['roles'] for e in role['ev'] if len(e) > 1 and e[1]}
        for r in json.loads((ROOT / f'{slug}/data/lrt_refs.json').read_text()):
            if r['pmid'] in used:
                lib.add(pmid=r['pmid'], doi=r.get('doi', ''), cit=f"{r['au']} et al. {r['t']} {r['j']}. {r['y']}.", tag=f"{r['au']} {r['y']}")
    return lib


def build():
    out = {}
    for slug in SLUGS:
        lib = page_library(slug)
        rows = {}
        for name, setting in R.documents('roadmap', slug):
            for ref in R.resolved(name):
                if lib.has(ref):
                    continue
                if ref['pmid']:
                    rid = ref['pmid']
                    st = STUDIES.get(rid)
                    assert st, f'{slug}: no compact study line for PMID {rid} ({ref["cite"][:60]})'
                    group = GROUP.get(rid) or SURGICAL.get(slug, 'Guidelines & policy')
                    if st.get('design') in ('Guideline', 'Consensus') and rid not in GROUP and slug != 'pdac':
                        group = 'Guidelines & policy'
                    row = {'id': rid, 'pmid': rid, 'tag': st['label'], 'group': group, 'cit': ref['cite']}
                    if ref['doi']:
                        row['doi'] = ref['doi']
                else:
                    item = ref['nonpm']
                    assert item and item.get('key'), f'{slug}: no key for non-PubMed reference {ref["cite"][:70]}'
                    rid = 'doc-' + item['key']
                    line = SUMMARIES.get(f'roadmap:{slug}:{rid}')
                    assert line, f'no one-line summary for roadmap:{slug}:{rid} in tools/source_summaries.json'
                    group = NONPM_GROUP.get(item.get('kind')) or SYSTEMIC.get(slug, 'Guidelines & policy')
                    if item['key'] == 'lirads-rt-tra':
                        group = 'Guidelines & policy'
                    row = {'id': rid, 'tag': item.get('tag') or R.tag_from_cite(ref['cite']), 'group': group, 'cit': ref['cite'],
                           'summary': {'lead': '', 'text': line}}
                    if ref['url']:
                        row['url'] = ref['url']
                row = rows.setdefault(rid, {**row, 'uses': []})
                row['uses'].append((setting, ref['label']))
        out[slug] = [{**{k: v for k, v in r.items() if k != 'uses'}, 'cited': R.cited(r['uses'])} for r in rows.values()]
    js = ('/* Generated by tools/build_document_references.py from the V16 roadmap documents (tools/document_references.json). '
          'Sources each roadmap document cites that the page library lacks; merged by assets/roadmap-evidence.js. */\n'
          'window.DocumentReferences=' + json.dumps(out, ensure_ascii=False, separators=(',', ':')) + ';\n')
    (ROOT / 'assets/document-references.js').write_text(js)
    return out


if __name__ == '__main__':
    out = build()
    for slug, rows in out.items():
        print(f'{slug:10} {len(rows):3} added')
