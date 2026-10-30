"""Shared helpers: the V16 documents' reference lists (tools/document_references.json) resolved to PMIDs and keys,
and matched against what a page's evidence library already lists.

Used by tools/build_document_references.py (roadmaps) and tools/build_pathway_sections.py (transplant pathways),
and by tools/test_document_references.py.
"""
import json, re, unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOCS = json.loads((ROOT / 'tools/document_references.json').read_text())['documents']
IDS = json.loads((ROOT / 'tools/document_reference_ids.json').read_text())
CATALOG = json.loads((ROOT / 'evidence-libraries/catalog.json').read_text())['publications']
DOI_PMID = {p['doi'].lower(): str(p['pmid']) for p in CATALOG.values() if p.get('doi') and p.get('pmid')}
DOI_PMID.update(IDS['doi_pmid'])
SETTING_NAME = {'roadmap': 'Roadmap document', 'standard': 'Standard pathway document', 'highrisk': 'High-risk pathway document'}


def norm(s):
    s = unicodedata.normalize('NFKD', s or '').encode('ascii', 'ignore').decode().lower()
    return re.sub(r'[^a-z0-9]+', ' ', s).strip()


def segments(cite):
    """Candidate title segments of a citation (author lists dropped)."""
    parts = re.split(r'(?<=[a-z0-9\)\]])\.\s+(?=[A-Z0-9#\[\(])', cite or '')
    return [p for p in parts if len(p) >= 30 and not re.search(r'et al\.?$|;\s*et al', p)]


def nonpm_key(cite):
    """Key of a non-PubMed document reference (drug label, FDA notice, guideline...), from its citation prefix."""
    for prefix, item in IDS['nonpm'].items():
        if (cite or '').startswith(prefix):
            return item
    return None


def resolved(doc_name):
    """The document's references with pmid resolved (text, catalog DOI, PubMed DOI look-ups, overrides)."""
    out = []
    for r in DOCS[doc_name]['refs']:
        o = IDS['override'].get(f"{doc_name}#{r['label']}") or {}
        item = nonpm_key(r['cite']) or {}
        slug = DOCS[doc_name]['slug']
        pmid = o.get('pmid') or r['pmid'] or DOI_PMID.get(r['doi'], '') or item.get('pmid', '')
        key = o.get('key') or item.get('key') or item.get('key_by_slug', {}).get(slug, '')
        out.append({**r, 'pmid': pmid, 'key': key, 'nonpm': None if pmid else {**item, 'key': key}})
    return out


def documents(family, slug):
    return [(name, d['setting']) for name, d in DOCS.items() if d['family'] == family and d['slug'] == slug]


class Library:
    """What a page's library already lists: PMIDs, DOIs, keys and citation text."""
    def __init__(self):
        self.pmids, self.dois, self.keys, self.text, self.tags = set(), set(), set(), [], set()

    def add(self, pmid='', doi='', key='', cit='', tag=''):
        if pmid: self.pmids.add(str(pmid))
        if doi: self.dois.add(doi.lower())
        if key: self.keys.add(key)
        for m in re.finditer(r'10\.\d{4,9}/[^\s"<>|?#]+', cit or ''):
            self.dois.add(m.group(0).rstrip('.,;)').lower())
        for m in re.finditer(r'PMID[:\s]*(\d{6,9})', cit or ''):
            self.pmids.add(m.group(1))
        self.text.append(norm(f'{cit} {tag}'))
        if tag: self.tags.add(norm(tag))

    def has(self, ref):
        if ref['pmid'] and ref['pmid'] in self.pmids: return True
        if ref['doi'] and ref['doi'] in self.dois: return True
        if ref.get('key') and ref['key'] in self.keys: return True
        text = ' || '.join(self.text)
        if any(norm(t)[:90] in text for t in segments(ref['cite'])): return True
        return bool(ref['label']) and not re.fullmatch(r'V\d+-\d+', ref['label']) and norm(ref['label']) in self.tags


def cited(uses):
    """'Standard pathway document, reference V16-12; High-risk pathway document, reference V16-30'."""
    parts = []
    for setting, label in uses:
        name = SETTING_NAME[setting]
        parts.append(f'{name}, reference {label}' if re.fullmatch(r'V\d+-\d+', label or '') else name)
    return '; '.join(dict.fromkeys(parts))


def tag_from_cite(cite):
    m = re.match(r"\s*([A-Za-zÀ-ÿ'\- ]+?)[,;.]", cite or '')
    y = re.search(r'\.\s*((?:19|20)\d{2})[;.]', cite or '')
    return ' '.join(x for x in [m.group(1).strip() if m else '', y.group(1) if y else ''] if x)
