"""Print the publication and PMID coverage of the current evidence libraries and clinical bibliographies."""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def read_json(path):
    return json.loads(path.read_text())

def embedded_data(path, name):
    text = path.read_text()
    start = re.search(r'\bconst\s+' + name + r'\s*=\s*', text).end()
    return json.JSONDecoder().raw_decode(text[start:])[0]

def pmids_in_reference_records(records):
    """Read PMID fields and actual PubMed links; numbers in outcomes and dates do not identify a paper."""
    result = set()
    if isinstance(records, dict):
        candidate = str(records.get('pmid', '')).strip()
        if re.fullmatch(r'\d{5,9}', candidate):
            result.add(candidate)
        for key, value in records.items():
            if key == 'refs' and isinstance(value, list):
                result.update(str(n) for n in value if re.fullmatch(r'\d{5,9}', str(n)))
            result.update(pmids_in_reference_records(value))
    elif isinstance(records, list):
        for value in records:
            result.update(pmids_in_reference_records(value))
    elif isinstance(records, str):
        result.update(re.findall(r'(?:pubmed\.ncbi\.nlm\.nih\.gov/|libkey\.io/libraries/\d+/pmid/|\bPMID[\s:]+|[\"\']pmid[\"\']\s*:\s*[\"\']?)(\d{5,9})\b', records, flags=re.I))
    return result

def website_bibliographies():
    groups = {}
    for path in sorted(ROOT.glob('*/data/pathway.json')):
        refs = read_json(path).get('refs', {})
        groups[path.parents[1].name + ' roadmap'] = {p for p in refs if re.fullmatch(r'\d{5,9}',p)}
    refs = embedded_data(ROOT/'hcc/index.html', 'REF')
    groups['hcc roadmap'] = {k for k in refs if re.fullmatch(r'\d{5,9}',k)}
    pathways = read_json(ROOT/'transplant/assets/pathway-sections.json')['pathways']
    for slug, pathway in pathways.items():
        groups[slug + ' transplant pathway'] = pmids_in_reference_records(pathway['sources'])
    lrt = embedded_data(ROOT/'lrt/index.html', 'DATA')
    groups['liver-directed treatment matrix'] = pmids_in_reference_records(lrt['refs']) | pmids_in_reference_records(read_json(ROOT/'lrt/comparisons.json')['rows'])
    groups['systemic treatment matrix'] = pmids_in_reference_records(read_json(ROOT/'systemic/matrix.json'))
    for entry in ROOT.glob('*/index.html'):
        slug = entry.parent.name
        if slug+' roadmap' not in groups: continue
        markup = entry.read_text()
        extra = re.search(r'<script[^>]*id="roadmap-evidence-data"[^>]*>(.*?)</script>', markup, re.S)
        if extra:
            groups[slug+' roadmap'].update(pmids_in_reference_records(json.loads(extra[1])))
        for candidate in (entry.parent/'data').glob('*.json'):
            clinical_data = read_json(candidate)
            groups[slug+' roadmap'].update(pmids_in_reference_records(clinical_data))
            if candidate.name == 'critique.json':
                groups[slug+' roadmap'].update(p for p in clinical_data if re.fullmatch(r'\d{5,9}',p))
    groups['systemic treatment matrix'].update(pmids_in_reference_records(read_json(ROOT/'systemic/references.json')))
    shared = set()
    for script in ('clinical-scores.js','clinical-reference.js','decision-evidence-data.js','compact-evidence-data.js','document-references.js'):
        shared.update(pmids_in_reference_records((ROOT/'assets'/script).read_text()))
    groups['shared reference tools and clinical evidence'] = shared
    return groups

def census():
    catalog = read_json(ROOT/'evidence-libraries/catalog.json')
    documents = read_json(ROOT/'evidence-libraries/document-index.json')
    records = {}
    identities = {}
    def add(id_, pub):
        keys = [id_]
        doi, pmid = pub.get('doi'),pub.get('pmid')
        if doi: keys.append('doi:'+re.sub(r'^https?://(?:dx\.)?doi\.org/', '', doi.strip().lower()))
        if pmid: keys.append('pmid:'+str(pmid).strip())
        found = {identities[k] for k in keys if k in identities}
        if len(found) > 1:
            raise ValueError(f'Conflicting identities for {id_}: {found}')
        key = next(iter(found),id_)
        identities.update({k:key for k in keys})
        prior = records.setdefault(key,dict(pub))
        for field,value in pub.items():
            if prior.get(field) in (None,''): prior[field] = value
        if pub.get('pdf_available') is True: prior['pdf_available']=True
        return key
    slide_ids = {add(k,p) for k,p in catalog['publications'].items()}
    for k,p in documents['publications'].items(): add(k,p)
    registered = {str(p.get('pmid')) for p in records.values() if p.get('pmid')}
    sites = website_bibliographies()
    cited = set.union(*sites.values())
    statuses = [p.get('pdf_available') for p in records.values()]
    return {
        'libraries': len(catalog['libraries']),
        'unique_slide_publications': len(slide_ids),
        'additional_document_publications': len(records) - len(slide_ids),
        'unique_slide_and_document_publications': len(records),
        'unique_slide_and_document_pmids': len(registered),
        'matched_pdfs': statuses.count(True),
        'unmatched_pdfs': statuses.count(False),
        'unchecked_pdfs': statuses.count(None),
        'structured_web_bibliography_pmids': len(cited),
        'structured_web_bibliography_pmids_outside_document_and_slide_libraries': sorted(cited-registered,key=int),
        'web_bibliography_sources': {k:len(v) for k,v in sites.items()},
    }

if __name__ == '__main__':
    print(json.dumps(census(),ensure_ascii=False,indent=2))
