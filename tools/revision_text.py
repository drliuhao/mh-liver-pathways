"""Python counterpart of applyText in tools/apply_clinical_revisions.cjs, for the Python source-preservation tests.

apply_text(file, text) replays every recorded "files" edit for that file (each must match exactly once).
systemic_pdf_status(base_refs, refs) returns {pmid: status} for the systemic references whose PDF status a recorded
revision changed, and mark_library(html, changes) applies those statuses to a baseline systemic page's
References entries, so a baseline comparison accepts exactly the recorded change and nothing else.
"""
import json, re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def revisions():
    return [json.loads(p.read_text()) for p in sorted((ROOT / 'tools/clinical_revisions').glob('*.json'))]


def apply_text(file, text):
    for rev in revisions():
        for e in rev.get('files', []):
            if e['file'] == file:
                n = text.count(e['old'])
                assert n == 1, f"{rev['id']} {file}: expected one match, found {n}: {e['old'][:80]!r}"
                text = text.replace(e['old'], e['new'])
    return text


def systemic_pdf_status(base_refs, refs):
    return {pm: r['pdf_status'] for pm, r in refs.items()
            if base_refs.get(pm, {}).get('pdf_status') == 'Full PDF still needed' and r['pdf_status'] != 'Full PDF still needed'}


def mark_library(html, changes):
    for pm, status in changes.items():
        m = re.search(r'<article class="library-entry"[^>]*data-pdf="needed">(?:(?!</article>).)*?pubmed\.ncbi\.nlm\.nih\.gov/%s/(?:(?!</article>).)*</article>' % pm, html, re.S)
        assert m, pm
        new = m.group(0).replace('data-pdf="needed"', 'data-pdf="available"', 1).replace('Full PDF still needed', status, 1)
        html = html[:m.start()] + new + html[m.end():]
    return html
