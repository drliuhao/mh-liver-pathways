"""Exact text corrections inside a Word document, run by run, without touching fields or formatting.

apply(document_xml_bytes, fixes) -> (new_bytes, applied_ids)
Each fix is {"id", "old", "new"}. `old` must occur exactly once in the document's paragraph text. The span may
cross several runs only when they share identical run formatting; it may not touch a field (EndNote citation,
hyperlink field, page number), so citations and their payloads stay as they are. The replacement text goes into
the first run of the span; the rest of the span is removed from the following runs.
"""
from lxml import etree

W = '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}'
XML_SPACE = '{http://www.w3.org/XML/1998/namespace}space'


def _texts(p):
    """Visible text nodes of a paragraph in order, each with a flag for being inside a field."""
    out, depth = [], 0
    for el in p.iter():
        if el.tag == W + 'fldChar':
            kind = el.get(W + 'fldCharType')
            depth += 1 if kind == 'begin' else -1 if kind == 'end' else 0
        elif el.tag == W + 't':
            in_simple = any(a.tag == W + 'fldSimple' for a in el.iterancestors())
            out.append((el, depth > 0 or in_simple))
    return out


def _rpr(t):
    r = t.getparent()
    rpr = r.find(W + 'rPr') if r is not None else None
    return etree.tostring(rpr) if rpr is not None else b''


def apply(xml, fixes):
    root = etree.fromstring(xml)
    applied = []
    for fx in fixes:
        old, new = fx['old'], fx['new']
        hits = []
        for p in root.iter(W + 'p'):
            nodes = _texts(p)
            text = ''.join(t.text or '' for t, _ in nodes)
            n = text.count(old)
            if n:
                hits.append((nodes, text, n))
        total = sum(h[2] for h in hits)
        if total != 1:
            raise ValueError(f"{fx['id']}: expected one match in the document, found {total}: {old[:80]!r}")
        nodes, text, _ = hits[0]
        i = text.index(old); j = i + len(old)
        span, pos = [], 0
        for t, in_field in nodes:
            n = len(t.text or '')
            if pos < j and pos + n > i:
                span.append((t, in_field, pos))
            pos += n
        if any(f for _, f, _ in span):
            raise ValueError(f"{fx['id']}: the text to replace touches a field: {old[:80]!r}")
        if len({_rpr(t) for t, _, _ in span}) > 1:
            raise ValueError(f"{fx['id']}: the text to replace crosses differently formatted runs: {old[:80]!r}")
        first, _, p0 = span[0]
        last, _, pl = span[-1]
        tail = (last.text or '')[j - pl:]
        if first is last:
            first.text = first.text[:i - p0] + new + tail
        else:
            first.text = first.text[:i - p0] + new
            for t, _, _ in span[1:-1]:
                t.text = ''
            last.text = tail
        for t, _, _ in span:
            t.set(XML_SPACE, 'preserve')
        applied.append(fx['id'])
    return etree.tostring(root, xml_declaration=True, encoding='UTF-8', standalone=True), applied
