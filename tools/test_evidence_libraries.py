"""Current bibliography coverage and private/public boundaries."""
from pathlib import Path
from urllib.parse import urlsplit
import json

root=Path(__file__).resolve().parents[1]
directory=root/'evidence-libraries'
data=json.loads((directory/'catalog.json').read_text())
assert len(data['libraries'])==34
assert len(data['publications'])==data['unique_publications']==670
# 573 PDFs at V15 (25 October 2026); 23 more filed from the 29 October 2026 full-text batch.
# V18 adds four sources (ABC-06 was already indexed): two verified PDFs and
# two primary reports read as XML, whose unavailable PDFs stay explicit.
# V20 verifies and deposits all 34 papers from the comparative-study checklist.
assert sum(bool(p['pdf_available']) for p in data['publications'].values())==646
assert data['missing_publication_pdfs']==24 and data['appraisals_pending']==53
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
