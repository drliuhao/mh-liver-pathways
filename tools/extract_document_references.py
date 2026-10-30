"""Extract the reference list of every V16 Word document (roadmaps and transplant protocols).

usage: python3 tools/extract_document_references.py "<V16 folder>"

Writes tools/document_references.json: for each document, the page it belongs to and every entry of its
reference lists, so the website's evidence libraries can be checked against (and completed from) what the
documents cite (Hao Liu, 30 October 2026: "make all the library complete in both protocol/pathways and the
roadmaps").

Reference lists read:
- Roadmaps: the main References section (entries "Label. Citation", grouped under category headings), "Sources
  not abstracted in full" ("Label — citation"), the HAI "Additional reference register" and the V16 lists
  ("[V16-n] Citation").
- Protocols and boundary addenda: the References section ("[V16-n] Citation").
Each entry keeps its text, its category heading where there is one, and its PMID and DOI where the text or its
hyperlinks give them (local file links are dropped).
"""
import html, json, re, sys, zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOCS = {
    'Memorial_Hermann_Adenoma_System_Roadmap_v16.docx': ('roadmap', 'adenoma', 'roadmap'),
    'Memorial_Hermann_Ampullary_System_Roadmap_v16.docx': ('roadmap', 'ampullary', 'roadmap'),
    'Memorial_Hermann_CRLM_System_Roadmap_v16.docx': ('roadmap', 'crlm', 'roadmap'),
    'Memorial_Hermann_HCC_System_Roadmap_v16.docx': ('roadmap', 'hcc', 'roadmap'),
    'Memorial_Hermann_HilarCCA_System_Roadmap_v16.docx': ('roadmap', 'hilar', 'roadmap'),
    'Memorial_Hermann_IncidentalMass_System_Roadmap_v16.docx': ('roadmap', 'incidental', 'roadmap'),
    'Memorial_Hermann_MixedTumour_System_Roadmap_v16.docx': ('roadmap', 'chcca', 'roadmap'),
    'Memorial_Hermann_NELM_System_Roadmap_v16.docx': ('roadmap', 'nelm', 'roadmap'),
    'Memorial_Hermann_PDAC_System_Roadmap_v16.docx': ('roadmap', 'pdac', 'roadmap'),
    'Memorial_Hermann_PNET_System_Roadmap_v16.docx': ('roadmap', 'pnet', 'roadmap'),
    'Memorial_Hermann_PancreaticCyst_System_Roadmap_v16.docx': ('roadmap', 'pcyst', 'roadmap'),
    'Memorial_Hermann_iCCA_System_Roadmap_v16.docx': ('roadmap', 'icca', 'roadmap'),
    '01_HCC_Standard_Guidance_Aligned_Protocol_v16.docx': ('transplant', 'hcc', 'standard'),
    '01_HCC_High_Risk_Protocol_v16.docx': ('transplant', 'hcc', 'highrisk'),
    '02_PCCA_Standard_Guidance_Aligned_Protocol_v16.docx': ('transplant', 'pcca', 'standard'),
    '02_PCCA_High_Risk_Protocol_v16.docx': ('transplant', 'pcca', 'highrisk'),
    '03_ICCA_Standard_Guidance_Aligned_Protocol_v16.docx': ('transplant', 'icca', 'standard'),
    '03_ICCA_High_Risk_Protocol_v16.docx': ('transplant', 'icca', 'highrisk'),
    '04_CRLM_Standard_Guidance_Aligned_Protocol_v16.docx': ('transplant', 'crlm', 'standard'),
    '04_CRLM_High_Risk_Protocol_v16.docx': ('transplant', 'crlm', 'highrisk'),
    '05_NELM_Standard_Guidance_Aligned_Protocol_v16.docx': ('transplant', 'nelm', 'standard'),
    '05_NELM_High_Risk_Protocol_v16.docx': ('transplant', 'nelm', 'highrisk'),
    '06_HEHE_Standard_Guidance_Aligned_Protocol_v16.docx': ('transplant', 'hehe', 'standard'),
    '06_HEHE_Clinical_Protocol_Boundary_Addendum_v16.docx': ('transplant', 'hehe', 'highrisk'),
    '07_HCA_Standard_Guidance_Aligned_Protocol_v16.docx': ('transplant', 'hca', 'standard'),
    '07_HCA_Clinical_Protocol_Boundary_Addendum_v16.docx': ('transplant', 'hca', 'highrisk'),
}
DOI = re.compile(r'10\.\d{4,9}/[^\s"<>|?#]+')
APPRAISAL = {'Population', 'Bottom line', 'Why this figure', 'Funding', 'Read this as', 'Key limit'}


def paragraphs(path):
    z = zipfile.ZipFile(path)
    xml = z.read('word/document.xml').decode()
    rels = {}
    for m in re.finditer(r'<Relationship [^>]*>', z.read('word/_rels/document.xml.rels').decode()):
        a = dict(re.findall(r'(\w+)="([^"]*)"', m.group(0)))
        rels[a.get('Id')] = html.unescape(a.get('Target', ''))
    for p in re.findall(r'<w:p[ >].*?</w:p>', xml, re.S):
        style = (re.search(r'<w:pStyle w:val="([^"]+)"', p) or [None, ''])[1]
        text = html.unescape(''.join(re.findall(r'<w:t[^>]*>([^<]*)</w:t>', p))).strip()
        links = [rels.get(r, '') for r in re.findall(r'r:id="(rId\d+)"', p)]
        yield style, text, [l for l in links if l and not l.startswith('file:')]


def ids(text, links):
    pmid = re.search(r'PMID[:\s]*(\d{6,9})', text)
    pmid = pmid.group(1) if pmid else next((m.group(1) for l in links for m in [re.search(r'pubmed\.ncbi\.nlm\.nih\.gov/(\d{6,9})', l)] if m), '')
    doi = DOI.search(text) or next((m for l in links for m in [DOI.search(l)] if m), None)
    doi = doi.group(0).rstrip('.,;)').lower() if doi else ''
    return pmid, doi


def extract(path, kind):
    P = list(paragraphs(path))
    out, section, group = [], None, ''
    first_refs = True
    for style, text, links in P:
        heading = style.startswith('Heading')
        if heading:
            group = ''
            if style == 'Heading1' and text.startswith('References'):
                section = 'main' if (kind == 'roadmap' and first_refs and text == 'References') else 'v16'
                first_refs = False
            elif text == 'Sources not abstracted in full':
                section = 'not_abstracted'
            elif text == 'Additional reference register':
                section = 'register'
            elif style == 'Heading3' and section == 'main':
                group = text
                continue
            else:
                section = None
            continue
        if not section or not text:
            continue
        if section == 'main':
            # Entries only: the PDAC roadmap interleaves each paper's appraisal (title, Population, Bottom line,
            # author-stated limits, funding) with the list, so a line must read as "Label. Citation ... year".
            if not group or style == 'ListParagraph':
                continue
            m = re.match(r'(.+?)\.\s+(.*)', text)
            label, cite = (m.group(1), m.group(2)) if m else ('', text)
            if (not m or label in APPRAISAL or text.isupper() or text.startswith(('Funding', 'WHAT THEY', 'LIMITATIONS'))
                    or not re.search(r'\b(19|20)\d{2}\b', cite) or len(label) > 90):
                continue
        elif section == 'not_abstracted':
            if style != 'ListParagraph':
                continue
            label, _, cite = text.partition(' — ')
        elif section == 'register':
            label, cite = '', text
        else:
            m = re.match(r'\[(V\d+-\d+)\]\s+(.*)', text)
            if not m:
                continue
            label, cite = m.group(1), m.group(2)
        cite = re.sub(r'\s*Source\s*\|\s*(Full text PDF|Local PDF not available[^|]*)\s*$', '', cite).strip()
        pmid, doi = ids(text, links)
        url = next((l for l in links if l.startswith('http')), '')
        out.append({'section': section, 'group': group, 'label': label.strip(), 'cite': cite, 'pmid': pmid, 'doi': doi, 'url': url})
    return out


def main(folder):
    folder = Path(folder)
    result = {}
    for name, (family, slug, setting) in DOCS.items():
        refs = extract(folder / name, family)
        result[name] = {'family': family, 'slug': slug, 'setting': setting, 'refs': refs}
        print(f'{len(refs):3} {name}')
    dest = ROOT / 'tools/document_references.json'
    dest.write_text(json.dumps({'about': 'Reference lists of the V16 Word documents (tools/extract_document_references.py). '
                                         'Source folder: V16_previously_treated_EHD_2026-10-29.', 'documents': result},
                               ensure_ascii=False, indent=1) + '\n')


if __name__ == '__main__':
    main(sys.argv[1])
