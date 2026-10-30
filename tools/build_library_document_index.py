"""Add document-only references to the PPT index without inventing slides or PDF matches.

The V15 catalog remains the audited slide inventory. This reproducible supplement
joins the 26 document bibliographies to their corresponding libraries.
"""
import json
import re
from pathlib import Path
from urllib.parse import quote
import document_refs as R

ROOT = Path(__file__).resolve().parents[1]
DEST = ROOT / 'evidence-libraries/document-index.json'


def library_key(doc):
    slug = {'adenoma': 'hca', 'hilar': 'pcca'}.get(doc['slug'], doc['slug'])
    prefix = {'roadmap': 'roadmap', 'standard': 'standard', 'highrisk': 'high_risk'}[doc['setting']]
    return f'{prefix}_{slug}'


def build():
    catalog = json.loads((ROOT / 'evidence-libraries/catalog.json').read_text())
    originals = {lib['key']: lib for lib in catalog['libraries']}
    pmids = {str(p['pmid']): key for key, p in catalog['publications'].items() if p.get('pmid')}
    dois = {p['doi'].lower(): key for key, p in catalog['publications'].items() if p.get('doi')}
    pathways = json.loads((ROOT / 'transplant/assets/pathway-sections.json').read_text())['pathways']
    output = {'about': 'Document references not represented by slides in the corresponding V15 PPT. No slide number or PDF availability is inferred.', 'libraries': {}, 'publications': {}}
    for name, doc in R.DOCS.items():
        key = library_key(doc)
        original = originals[key]
        # Document citations often abbreviate a study title or omit its identifiers.
        # Resolve them through the already-reviewed page record before testing PPT coverage.
        by_tag = {}
        if doc['family'] == 'roadmap':
            if doc['slug'] == 'hcc':
                page = (ROOT / 'hcc/index.html').read_text()
                block = page.split('const REF = {', 1)[1]
                refs = json.loads('{' + block.split('};', 1)[0] + '}')
            else:
                refs = json.loads((ROOT / doc['slug'] / 'data/pathway.json').read_text())['refs']
            for refid, record in refs.items():
                pmid = refid if refid.isdigit() else ''
                found = re.search(r'PMID[:\s]*(\d{6,9})', record[2])
                if found: pmid = found.group(1)
                if pmid: by_tag[R.norm(record[0])] = pmid
        seen = R.Library()
        for entry in original['papers']:
            p = catalog['publications'][entry['id']]
            seen.add(pmid=p.get('pmid'), doi=p.get('doi'), cit=p['title'], key=entry['id'])
        for p in original['policy_records']:
            seen.add(cit=p['title'])
        additions, policies = {}, {}
        for ref in R.resolved(name):
            ref = dict(ref)
            if not ref['pmid'] and doc['family'] == 'roadmap':
                ref['pmid'] = by_tag.get(R.norm(ref['label']), '')
            elif doc['family'] == 'transplant':
                citation = R.cited([(doc['setting'], ref['label'])])
                for source in pathways[doc['slug']]['sources']:
                    if citation in source.get('appraisal', {}).get('cited', '').split('; '):
                        ref['pmid'] = source.get('pmid') or ref['pmid']
                        ref['doi'] = source.get('doi') or ref['doi']
                        break
            if seen.has(ref):
                continue
            cited = R.cited([(doc['setting'], ref['label'])])
            pmid, doi = str(ref.get('pmid') or ''), ref.get('doi') or ''
            if pmid or doi:
                rid = pmids.get(pmid) or dois.get(doi.lower()) or (f'pmid:{pmid}' if pmid else f'doi:{doi.lower()}')
                if rid not in catalog['publications'] and rid not in output['publications']:
                    url = f'https://pubmed.ncbi.nlm.nih.gov/{pmid}/' if pmid else f'https://doi.org/{doi}'
                    tmc = f'https://libkey.io/libraries/480/pmid/{pmid}' if pmid else f'https://libkey.io/libraries/480/{quote(doi, safe="/")}'
                    output['publications'][rid] = {'title': ref['cite'], 'doi': doi, 'pmid': pmid, 'year': '',
                        'publication_type': 'Document reference', 'url': url, 'tmc': tmc,
                        'pdf_available': None, 'coverage': 'Document citation; slide appraisal not yet available in this PPT'}
                row = additions.setdefault(rid, {'id': rid, 'slides': [], 'inclusion': [], 'document_only': True})
                if cited not in row['inclusion']:
                    row['inclusion'].append(cited)
            else:
                # An unidentified legacy citation may already have a slide under a
                # shortened title. Do not manufacture a missing-slide claim for it.
                if not re.fullmatch(r'V16-\d+', ref['label'] or ''):
                    continue
                rid = R.norm(ref['cite'])
                row = policies.setdefault(rid, {'title': ref['cite'], 'slides': [], 'pdf_available': None,
                    'url': ref.get('url') or '', 'inclusion': [], 'document_only': True})
                if cited not in row['inclusion']:
                    row['inclusion'].append(cited)
        output['libraries'][key] = {'papers': list(additions.values()), 'policy_records': list(policies.values())}
    return output


if __name__ == '__main__':
    data = build()
    DEST.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n')
    print(f"Document index: {sum(len(v['papers']) for v in data['libraries'].values())} paper entries and "
          f"{sum(len(v['policy_records']) for v in data['libraries'].values())} policy/document entries without slides "
          f"across {len(data['libraries'])} libraries; {len(data['publications'])} additional publications.")
