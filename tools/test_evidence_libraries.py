"""Current bibliography coverage and private/public boundaries."""
from pathlib import Path
from urllib.parse import urlsplit
import json

root=Path(__file__).resolve().parents[1]
directory=root/'evidence-libraries'
data=json.loads((directory/'catalog.json').read_text())
assert len(data['libraries'])==34
assert len(data['publications'])==data['unique_publications']
assert sum(p.get('pdf_available') is True for p in data['publications'].values())==data['matched_publication_pdfs']
assert sum(p.get('pdf_available') is False for p in data['publications'].values())==data['missing_publication_pdfs']
# A publication cited on the website, a document-only reference and an appraised slide are different scopes.
from evidence_census import census
summary=census()
assert summary['unique_slide_publications']==data['unique_publications']
assert summary['unique_slide_and_document_publications']==summary['unique_slide_publications']+summary['additional_document_publications']
assert summary['matched_pdfs']+summary['unmatched_pdfs']+summary['unchecked_pdfs']==summary['unique_slide_and_document_publications']
assert summary['structured_web_bibliography_pmids_outside_document_and_slide_libraries']
chen_id = next(key for key,p in data['publications'].items() if str(p.get('pmid'))=='39311927')
for key in ('liver_directed_matrix','roadmap_pcca'):
    library=next(l for l in data['libraries'] if l['key']==key)
    assert any(r['id']==chen_id and r['slides'] for r in library['papers'])
for pmid in ('24681342', '38466889', '42421575'):
    pub = next(p for p in data['publications'].values() if p.get('pmid') == pmid)
    assert pub['pdf_available'] and pub['coverage'] == 'Focused full-text appraisal', pmid
used=set()
for library in data['libraries']:
    ids=[p['id'] for p in library['papers']]
    assert len(ids)==len(set(ids))==library['publication_count'],library['key']
    assert sum(data['publications'][i]['pdf_available'] for i in ids)==library['matched_pdfs']
    for paper in library['papers']:
        used.add(paper['id'])
        assert paper['slides'] and all(1<=s<=library['slides'] for s in paper['slides'])
        assert paper['inclusion']
    for policy in library['policy_records']:
        assert all(1<=s<=library['slides'] for s in policy['slides'])
assert used==set(data['publications'])
for publication in data['publications'].values():
    for key in ('url','tmc'):
        assert urlsplit(publication[key]).scheme=='https',publication
assert not list(directory.rglob('*.pdf')) and not list(directory.rglob('*.pptx'))
for file in directory.iterdir():
    if file.is_file():
        text=file.read_text()
        assert '/Users/' not in text and 'file://' not in text,file
print(f"PASS: 34 libraries, {data['unique_publications']} unique publications, {data['matched_publication_pdfs']} matched PDFs, exact slide references, inclusion reasons and HTTPS access links; no licensed PDFs, PPTs or private absolute paths published.")
