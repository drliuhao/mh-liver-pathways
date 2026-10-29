"""Standardized Word files per tumor (V17, 29 October 2026).

usage: python3 tools/build_consensus_docs.py <template.docx> <v16-folder> <package-out> [--web]

For each tumor (documents/<tumor>/questions.json):
  1 Cancer roadmap            full-content document (V16 roadmap, with a companion-files note)
  2 Cancer roadmap questions  every question needing a consensus answer, fully detailed
  3 Standard transplant protocol / 4 its questions
  5 High-risk transplant protocol / 6 its questions
  7 Decision discussion       all settings for the tumor: source positions, our proposed selection, decision fields
Private copies (local PDF links kept) go to <package-out>/<NN>_<Tumor>/ with a _v17 suffix. With --web, public copies
(local file links replaced by PubMed or DOI links, no licensed PDFs) go to documents/<tumor>/ in this repository.
"""
import copy, json, re, sys, zipfile, base64
from pathlib import Path
from urllib.parse import unquote, urlsplit
import docx
from docx.shared import Pt, RGBColor
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.opc.constants import RELATIONSHIP_TYPE as RT
from lxml import etree as E
import docx_text_fixes

ROOT = Path(__file__).resolve().parents[1]
TEMPLATE, V16, OUT = Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3])
WEB = '--web' in sys.argv
SITE = 'https://drliuhao.github.io/mh-liver-pathways/'
DATE = '29 October 2026'
NAVY, FILL, LINE, GREY = '17365D', 'F1F5F8', 'CCD6DF', '5A6069'
ORDER = ['hcc', 'pcca', 'icca', 'crlm', 'nelm', 'hehe', 'hca', 'chcca', 'pdac', 'pnet', 'ampullary', 'pcyst', 'incidental']
V16_ROADMAP = {'hcc': 'HCC', 'pcca': 'HilarCCA', 'icca': 'iCCA', 'crlm': 'CRLM', 'nelm': 'NELM', 'hca': 'Adenoma', 'chcca': 'MixedTumour',
               'pdac': 'PDAC', 'pnet': 'PNET', 'ampullary': 'Ampullary', 'pcyst': 'PancreaticCyst', 'incidental': 'IncidentalMass'}
V16_TRANSPLANT = {'hcc': '01_HCC', 'pcca': '02_PCCA', 'icca': '03_ICCA', 'crlm': '04_CRLM', 'nelm': '05_NELM', 'hehe': '06_HEHE', 'hca': '07_HCA'}
SET_NAME = {'roadmap': 'Cancer roadmap', 'standard': 'Standard transplant pathway', 'highrisk': 'High-risk transplant protocol'}


# ---------------------------------------------------------------- low-level writing
def new_doc():
    d = docx.Document(str(TEMPLATE))
    body = d.element.body
    for el in list(body):
        if el.tag != qn('w:sectPr'):
            body.remove(el)
    for rid, rel in list(d.part.rels.items()):
        if rel.reltype.endswith('/comments') or rel.reltype.endswith('/commentsExtended') or rel.reltype == RT.HYPERLINK:
            d.part.drop_rel(rid)
    return d


def run(p, text, bold=False, italic=False, size=None, color=None):
    r = p.add_run(text)
    r.bold, r.italic = bold, italic
    if size: r.font.size = Pt(size)
    if color: r.font.color.rgb = RGBColor.from_string(color)
    return r


def para(d, text='', label=None, size=None, color=None, italic=False, style=None, after=4):
    p = d.add_paragraph(style=style)
    p.paragraph_format.space_after = Pt(after)
    if label: run(p, label + ' ', bold=True, size=size, color=color)
    if text: run(p, text, size=size, color=color, italic=italic)
    return p


def link(p, url, text, size=None):
    rid = p.part.relate_to(url, RT.HYPERLINK, is_external=True)
    h = OxmlElement('w:hyperlink'); h.set(qn('r:id'), rid)
    r = OxmlElement('w:r'); pr = OxmlElement('w:rPr')
    c = OxmlElement('w:color'); c.set(qn('w:val'), '0563C1'); pr.append(c)
    u = OxmlElement('w:u'); u.set(qn('w:val'), 'single'); pr.append(u)
    if size:
        s = OxmlElement('w:sz'); s.set(qn('w:val'), str(int(size * 2))); pr.append(s)
    r.append(pr); t = OxmlElement('w:t'); t.text = text; t.set(qn('xml:space'), 'preserve'); r.append(t); h.append(r)
    p._p.append(h)


def bullet(d, text, label=None):
    p = para(d, text, label=label, after=2)
    pPr = p._p.get_or_add_pPr()
    num = OxmlElement('w:numPr'); il = OxmlElement('w:ilvl'); il.set(qn('w:val'), '0'); nid = OxmlElement('w:numId'); nid.set(qn('w:val'), '5')
    num.append(il); num.append(nid); pPr.insert(0, num)
    return p


def heading(d, text, level):
    h = d.add_paragraph()
    st = OxmlElement('w:pStyle'); st.set(qn('w:val'), f'Heading{level}'); h._p.get_or_add_pPr().insert(0, st)
    h.paragraph_format.keep_with_next = True
    h.paragraph_format.space_before = Pt(14 if level == 1 else 10 if level == 2 else 6)
    h.paragraph_format.space_after = Pt(4)
    run(h, text)
    return h


def rule_line(d):
    p = d.add_paragraph(); p.paragraph_format.space_after = Pt(10)
    pPr = p._p.get_or_add_pPr(); b = OxmlElement('w:pBdr'); bt = OxmlElement('w:bottom')
    for k, v in (('val', 'single'), ('sz', '6'), ('space', '1'), ('color', '9AA8B4')): bt.set(qn('w:' + k), v)
    b.append(bt); pPr.append(b)


def table(d, headers, rows, widths):
    t = d.add_table(rows=1 + len(rows), cols=len(headers))
    tbl = t._tbl; tblPr = tbl.tblPr
    for tag, attrs in (('w:tblW', {'w': str(sum(widths)), 'type': 'dxa'}), ('w:tblLayout', {'type': 'fixed'})):
        el = OxmlElement(tag)
        for k, v in attrs.items(): el.set(qn('w:' + k), v)
        tblPr.append(el)
    borders = OxmlElement('w:tblBorders')
    for side in ('top', 'left', 'bottom', 'right', 'insideH', 'insideV'):
        b = OxmlElement('w:' + side)
        for k, v in (('val', 'single'), ('sz', '4'), ('color', LINE)): b.set(qn('w:' + k), v)
        borders.append(b)
    tblPr.append(borders)
    mar = OxmlElement('w:tblCellMar')
    for side in ('top', 'left', 'bottom', 'right'):
        m = OxmlElement('w:' + side); m.set(qn('w:w'), '90'); m.set(qn('w:type'), 'dxa'); mar.append(m)
    tblPr.append(mar)
    grid = tbl.tblGrid
    for i, gc in enumerate(grid.findall(qn('w:gridCol'))): gc.set(qn('w:w'), str(widths[i]))
    def fill(cell, color, w):
        tcPr = cell._tc.get_or_add_tcPr()
        tw = OxmlElement('w:tcW'); tw.set(qn('w:w'), str(w)); tw.set(qn('w:type'), 'dxa'); tcPr.append(tw)
        sh = OxmlElement('w:shd'); sh.set(qn('w:val'), 'clear'); sh.set(qn('w:color'), 'auto'); sh.set(qn('w:fill'), color); tcPr.append(sh)
    hdr = t.rows[0]
    trPr = hdr._tr.get_or_add_trPr(); th = OxmlElement('w:tblHeader'); trPr.append(th)
    for i, h in enumerate(headers):
        c = hdr.cells[i]; fill(c, NAVY, widths[i]); p = c.paragraphs[0]; run(p, h, bold=True, size=9.5, color='FFFFFF')
    for r, row in enumerate(rows):
        cells = t.rows[r + 1].cells
        cs = t.rows[r + 1]._tr.get_or_add_trPr(); cs.append(OxmlElement('w:cantSplit'))
        for i, val in enumerate(row):
            c = cells[i]; fill(c, FILL if r % 2 == 0 else 'FFFFFF', widths[i]); p = c.paragraphs[0]
            p.paragraph_format.space_after = Pt(0)
            if callable(val): val(p)
            else:
                for j, piece in enumerate(val if isinstance(val, list) else [val]):
                    if j: p = c.add_paragraph(); p.paragraph_format.space_after = Pt(0)
                    if isinstance(piece, tuple): run(p, piece[0], bold=piece[1] == 'b', italic=piece[1] == 'i', size=9 if piece[1] == 's' else 9.5, color=GREY if piece[1] == 's' else None)
                    else: run(p, str(piece), size=9.5)
    d.add_paragraph().paragraph_format.space_after = Pt(2)
    return t


def words(s, n):
    w = (s or '').split()
    return ' '.join(w[:n]) + ('…' if len(w) > n else '')


# ---------------------------------------------------------------- content
class Book:
    def __init__(self, data):
        self.data, self.used = data, []
    def ref(self, key):
        if key and key in self.data['sources'] and key not in self.used: self.used.append(key)


def source_cell(b, row):
    b.ref(row.get('key'))
    out = [(row['source'], 'b')]
    if row.get('read'): out.append((row['read'], 's'))
    return out


def question(d, b, q, level=2):
    heading(d, f"{q['id']} — {q['title']}", level)
    meta = [q.get('status', '')]
    if q.get('kind'): meta.append(q['kind'].capitalize())
    para(d, ' · '.join(x for x in meta if x), size=9, color=GREY)
    if q.get('question') and q['question'] != q['title']:
        para(d, q['question'], label='Question:')
    if q.get('context'):
        para(d, q['context'], label='When it applies:')
    if q.get('where'):
        p = para(d, '', label='Where it is decided:', after=4)
        for i, w in enumerate(q['where']):
            if i: run(p, ' · ')
            link(p, SITE + w['url'], w['label'])
    if q.get('web'):
        p = para(d, '', label='Web page:', size=9, after=6); link(p, SITE + q['web'], 'open this question on the website', size=9)
    heading(d, 'Positions of guidelines, trials and papers', level + 1)
    if q.get('positions'):
        table(d, ['Source', 'Position', 'Where stated'],
              [[source_cell(b, x), x['says'], [(x.get('locator', ''), 's')]] for x in q['positions']], [2200, 5480, 2400])
    elif not q.get('studies'):
        para(d, 'No guideline, trial or paper takes a position on this question; it is a programme decision.', italic=True)
    if q.get('divergence'):
        para(d, q['divergence'], label='Where sources differ:')
    if q.get('studies'):
        heading(d, 'Evidence', level + 1)
        table(d, ['Source', 'Population and selection', 'Results, limits and location'],
              [[source_cell(b, s), s.get('population', ''), [s.get('results', ''), ('Limits: ' + s['limits'], 'i') if s.get('limits') else '', (s.get('locator', ''), 's')]]
               for s in q['studies']], [2000, 3900, 4180])
    heading(d, 'Our proposed selection (OPEN)', level + 1)
    para(d, q.get('proposal') or 'No proposal yet; the group decides.')
    if q.get('proposal_locator'):
        para(d, q['proposal_locator'], label='Basis in the document:', size=9, color=GREY)
    for r in q.get('rules') or []:
        bullet(d, r)
    for label, key in (('Why:', 'rationale'), ('Against, or uncertain:', 'counter'), ('Certainty:', 'certainty'),
                       ('What would change the answer:', 'change'), ('Tests and records:', 'tests'), ('Allocation:', 'allocation'),
                       ('Owners:', 'owners'), ('What gets audited:', 'audit'), ('Roadmap note:', 'note')):
        if q.get(key):
            para(d, q[key], label=label)
    tb = q.get('threshold_basis') or []
    tb = [tb] if isinstance(tb, str) else tb
    if tb:
        para(d, '', label='Basis for the proposed thresholds:', after=2)
        for t in tb:
            bullet(d, t)
    if q.get('supporting'):
        para(d, ', '.join(q['supporting']), label='Further sources:')
    heading(d, f"{q['id']} — group decision", level + 1)
    for label in ('Accepted position (or alternative chosen):', 'Rationale, dissent and exceptions:', 'Owner · approval date · implementation date:'):
        para(d, '', label=label, after=0); rule_line(d)


def summary(d, qs, setting=False):
    rows = []
    for q in qs:
        r = [[(q['id'], 'b')], q['question'], words(q.get('proposal'), 30), [(q.get('status', ''), 's')]]
        rows.append(([SET_NAME[q['set']]] if setting else []) + r)
    hdr = (['Setting'] if setting else []) + ['ID', 'Question', 'Proposed selection (summary)', 'Status']
    w = [1500, 1100, 2900, 3080, 1500] if setting else [1300, 3500, 3780, 1500]
    table(d, hdr, rows, w)


def references(d, b):
    if not b.used:
        return
    heading(d, 'Sources', 1)
    for k in sorted(b.used, key=lambda k: b.data['sources'][k]['short'].lower()):
        s = b.data['sources'][k]
        p = para(d, '', after=3)
        run(p, s['short'], bold=True, size=9.5)
        if s.get('title') and s['title'] != s['short']:
            run(p, ' — ' + re.sub(r'\s+', ' ', s['title']), size=9.5)
        L = s.get('links', {})
        names = [('pubmed', 'PubMed'), ('doi', 'Journal'), ('pmc', 'Free full text'), ('url', 'Source'), ('tmc', 'TMC library')]
        first = True
        for k2, label in names:
            if L.get(k2):
                run(p, '  ' if first else ' · ', size=9.5); link(p, L[k2], label, size=9.5); first = False


def front(d, data, title, lines, companions):
    t = d.add_paragraph(style='Title'); run(t, title, size=22)
    t.paragraph_format.line_spacing = 1.05; t.paragraph_format.space_after = Pt(6)
    para(d, f'UTHealth Houston and Memorial Hermann · HPB oncology · {DATE} · V17 standardized documents', size=9, color=GREY)
    for x in lines:
        para(d, x)
    p = para(d, '', label='Companion files:', after=8)
    for i, (label, name) in enumerate(companions):
        run(p, ('' if i == 0 else ' · ') + f'{label}: ', size=10); run(p, name, italic=True)


def questions_doc(data, setname, path):
    d = new_doc(); b = Book(data); s = data['sets'][setname]; f = data['files']
    info = {'roadmap': f.get('roadmap_info'), 'standard': f.get('standard_info'), 'highrisk': f.get('highrisk_info')}[setname]
    label = s['label']
    front(d, data, f"{data['name']} — {label}: questions for consensus",
          [f"Every question in the {label.lower()} that still needs a consensus answer. Each one shows what guidelines, trials and papers say, "
           "our proposed selection, and space for the group decision. All proposals are OPEN; nothing in this document is activated or approved.",
           f"Web page: {SITE + s['web']}"],
          [('Full content', info), ('Decision discussion for all settings', f['decision'])])
    heading(d, 'Summary', 1)
    summary(d, s['questions'])
    heading(d, 'Questions', 1)
    for q in s['questions']:
        question(d, b, q)
    if s.get('ratify'):
        heading(d, 'Specialty ratification items', 1)
        para(d, 'Each specialty approves the exact wording in the roadmap, not the concept. Positions are listed only where the roadmap contrasts sources.')
        table(d, ['ID', 'Specialty', 'Item to ratify', "Roadmap's stated position", 'Decision'],
              [[[(r['id'], 'b')], r['specialty'], r['question'], [r.get('proposal', ''), (r.get('proposal_locator', ''), 's')], ''] for r in s['ratify']],
              [1000, 1500, 2900, 3280, 1400])
    if s.get('shared'):
        heading(d, 'Shared approval requirements (all transplant pathways)', 1)
        para(d, 'Recipient selection, allocation, donor protection and institutional study approval are separate decisions. These apply to every high-risk proposal.')
        for q in s['shared']:
            question(d, b, q)
    for n in data.get('not_applicable', []) if setname == 'roadmap' else []:
        heading(d, 'Previously treated extrahepatic disease', 1)
        para(d, n['text'])
    references(d, b)
    d.save(path)


def decision_doc(data, path):
    d = new_doc(); b = Book(data); f = data['files']; sets = data['sets']
    comp = [(SET_NAME[k] + (' (full content)' if k else ''), f[k + '_info']) for k in ('roadmap', 'standard', 'highrisk') if k + '_info' in f]
    front(d, data, f"{data['name']} — decision discussion",
          ["One file for the multidisciplinary decision on this tumor, covering every setting: " +
           ', '.join(SET_NAME[k].lower() for k in sets) + '. ' +
           'For each question: the positions of guidelines, trials and papers where they differ, our proposed selection, and space for the decision. '
           'All proposals are OPEN; nothing in this document is activated or approved.'],
          comp)
    allq = [q for k in sets for q in sets[k]['questions']]
    heading(d, 'Summary of open questions', 1)
    summary(d, allq, setting=True)
    for n, k in enumerate(sets, 1):
        s = sets[k]
        heading(d, f'Part {n}. {s["label"]}', 1)
        para(d, f"Web page: {SITE + s['web']}", size=9, color=GREY)
        for q in s['questions']:
            question(d, b, q)
        if s.get('ratify'):
            heading(d, 'Specialty ratification items', 2)
            table(d, ['ID', 'Specialty', 'Item to ratify', "Roadmap's stated position", 'Decision'],
                  [[[(r['id'], 'b')], r['specialty'], r['question'], [r.get('proposal', ''), (r.get('proposal_locator', ''), 's')], ''] for r in s['ratify']],
                  [1000, 1500, 2900, 3280, 1400])
        if s.get('shared'):
            heading(d, 'Shared approval requirements (all transplant pathways)', 2)
            for q in s['shared']:
                question(d, b, q, level=3)
    for x in data.get('not_applicable', []):
        heading(d, 'Previously treated extrahepatic disease', 1); para(d, x['text'])
    references(d, b)
    d.save(path)


# ---------------------------------------------------------------- full-content documents (V16 copies)
W = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
NS = {'w': W}


def companion_note(xml, text):
    """Insert one plain paragraph after the title block; fields, citations and other content are untouched."""
    t = E.fromstring(xml); body = t.find('w:body', NS)
    paras = body.findall('w:p', NS)
    anchor = paras[1] if len(paras) > 1 else paras[0]
    p = E.Element(f'{{{W}}}p'); pPr = E.SubElement(p, f'{{{W}}}pPr'); sp = E.SubElement(pPr, f'{{{W}}}spacing'); sp.set(f'{{{W}}}after', '120')
    r = E.SubElement(p, f'{{{W}}}r'); rPr = E.SubElement(r, f'{{{W}}}rPr'); E.SubElement(rPr, f'{{{W}}}i')
    sz = E.SubElement(rPr, f'{{{W}}}sz'); sz.set(f'{{{W}}}val', '18')
    tt = E.SubElement(r, f'{{{W}}}t'); tt.text = text; tt.set('{http://www.w3.org/XML/1998/namespace}space', 'preserve')
    anchor.addnext(p)
    return E.tostring(t, xml_declaration=True, encoding='UTF-8', standalone=True)


def public_target(target):
    name = Path(unquote(urlsplit(target).path)).name
    m = re.match(r'(\d{6,9})__', name)
    if m: return f'https://pubmed.ncbi.nlm.nih.gov/{m.group(1)}/'
    return SITE + 'evidence-libraries/'


# Corrections to the V16 text from papers read in full after V16 (tools/consensus_source/document_fixes_*.json).
FIXES = {}
for _f in sorted((ROOT / 'tools/consensus_source').glob('document_fixes_*.json')):
    for _x in json.loads(_f.read_text())['fixes']:
        FIXES.setdefault(_x['document'], []).append(_x)
APPLIED = set()


def info_doc(src, dest, note, public):
    with zipfile.ZipFile(src) as z:
        parts = {n: z.read(n) for n in z.namelist()}
    fixes = FIXES.get(Path(src).name, [])
    if fixes:
        parts['word/document.xml'], done = docx_text_fixes.apply(parts['word/document.xml'], fixes)
        APPLIED.update(done)
        note += (f' {len(fixes)} statement{"s" if len(fixes) > 1 else ""} corrected on 29 October 2026 against the full texts of '
                 'papers previously cited from their abstracts.')
    parts['word/document.xml'] = companion_note(parts['word/document.xml'], note)
    if public:
        doc = E.fromstring(parts['word/document.xml'])
        for f in doc.xpath('//w:fldData', namespaces=NS):
            try: r = E.fromstring(base64.b64decode(f.text))
            except Exception: continue
            changed = False
            for u in r.findall('.//urls/pdf-urls'):
                for l in list(u):
                    if (l.text or '').startswith('file:'): u.remove(l); changed = True
            if changed: f.text = base64.b64encode(E.tostring(r)).decode()
        for t in doc.xpath('//w:t', namespaces=NS):
            if t.text == 'Full text PDF': t.text = 'Full-text access'
        parts['word/document.xml'] = E.tostring(doc, xml_declaration=True, encoding='UTF-8', standalone=True)
        for n, data in list(parts.items()):
            if not n.endswith('.rels'): continue
            rels = E.fromstring(data); hit = False
            for rel in rels:
                tg = rel.get('Target', '')
                if tg.startswith('file:') or tg.startswith('/Users/'):
                    rel.set('Target', public_target(tg)); rel.set('TargetMode', 'External'); hit = True
            if hit: parts[n] = E.tostring(rels, xml_declaration=True, encoding='UTF-8', standalone=True)
        blob = b''.join(parts.values())
        assert b'file:///' not in parts['word/_rels/document.xml.rels'], dest
    with zipfile.ZipFile(dest, 'w', zipfile.ZIP_DEFLATED) as z:
        for n, data in parts.items(): z.writestr(n, data)


def info_sources(key):
    out = {}
    if key in V16_ROADMAP: out['roadmap_info'] = V16 / f'Memorial_Hermann_{V16_ROADMAP[key]}_System_Roadmap_v16.docx'
    if key in V16_TRANSPLANT:
        pre = V16_TRANSPLANT[key]
        out['standard_info'] = V16 / f'{pre}_Standard_Guidance_Aligned_Protocol_v16.docx'
        hr = V16 / f'{pre}_High_Risk_Protocol_v16.docx'
        out['highrisk_info'] = hr if hr.exists() else V16 / f'{pre}_Clinical_Protocol_Boundary_Addendum_v16.docx'
    return out


def v17(name):
    return name.replace('.docx', '_v17.docx')


report = []
for n, key in enumerate(ORDER, 1):
    data = json.loads((ROOT / 'documents' / key / 'questions.json').read_text())
    f = data['files']
    folder = OUT / f'{n:02d}_{data["code"].replace("-", "")}'
    folder.mkdir(parents=True, exist_ok=True)
    targets = [(folder, v17, False)] + ([(ROOT / 'documents' / key, lambda x: x, True)] if WEB else [])
    for setname, src in info_sources(key).items():
        base = setname.replace('_info', '')
        note = (f'Standardized document set, {DATE}: this is the full-content document for the {SET_NAME[base].lower()}. '
                f'Questions for consensus: {f[base + "_questions"]}. Decision discussion for all settings: {f["decision"]}. '
                f'Web page: {SITE + data["sets"][base]["page"]}')
        for out, nm, public in targets:
            info_doc(src, out / nm(f[setname]), note, public)
    for setname in data['sets']:
        for out, nm, public in targets:
            questions_doc(data, setname, out / nm(f[setname + '_questions']))
    for out, nm, public in targets:
        decision_doc(data, out / nm(f['decision']))
    report.append((data['code'], sorted(p.name for p in folder.iterdir())))
    print(f"{data['code']:9} {len(list(folder.iterdir()))} files")
missing = {x['id'] for fs in FIXES.values() for x in fs} - APPLIED
assert not missing, f'document corrections not applied: {sorted(missing)}'
(OUT / 'document_manifest.json').write_text(json.dumps(report, indent=1))
print(f'{len(APPLIED)} recorded text corrections applied to the full-content documents')
