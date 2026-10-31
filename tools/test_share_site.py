"""The share edition builds and holds no downloadable document (tools/build_share_site.py).

usage: python3 tools/test_share_site.py

- The build succeeds; its own check finds no Word/PDF/PowerPoint/Excel file, no page link to one, no address of the
  full site and every page marked data-edition="share".
- Every published page and data file of the full site is in the share edition, except the documents themselves.
- No page lost an element id (script mount points), and the roadmaps' Questions-for-consensus data are present.
- The full site is unchanged by the build, and its Documents menu and notes still work there (the share switches only
  act on data-edition="share").
"""
import re, subprocess, sys, tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
import build_share_site as S

fail = []
before = subprocess.run(['git', '-C', str(ROOT), 'status', '--porcelain'], capture_output=True, text=True).stdout
with tempfile.TemporaryDirectory() as tmp:
    out = Path(tmp) / 'share'
    S.build(out, 'mh-liver-pathways-share')
    published = set(S.published())
    built = {p.relative_to(out).as_posix() for p in out.rglob('*') if p.is_file()}
    missing = sorted(published - built)
    if missing:
        fail.append(f'published files missing from the share edition: {missing[:5]}')
    tracked = subprocess.run(['git', '-C', str(ROOT), 'ls-files'], capture_output=True, text=True).stdout.split()
    docs = [f for f in tracked if S.DOC.search(f)]
    if not docs or any(d in built for d in docs):
        fail.append('document files are published in the share edition')
    for f in [f for f in tracked if f.endswith('.html') and f in built]:
        a, b = (ROOT / f).read_text(), (out / f).read_text()
        lost = set(re.findall(r'\bid="([^"]+)"', a)) - set(re.findall(r'\bid="([^"]+)"', b))
        if lost:
            fail.append(f'{f}: lost element ids {sorted(lost)[:5]}')
    for slug in ('crlm', 'hcc', 'pnet'):
        if not (out / f'documents/{"pcca" if slug == "hilar" else slug}/questions.json').exists():
            fail.append(f'{slug}: Questions-for-consensus data missing')
    if not (out / 'assets/documents.json').exists():
        fail.append('assets/documents.json missing (it drives the roadmaps\' Questions for consensus)')
after = subprocess.run(['git', '-C', str(ROOT), 'status', '--porcelain'], capture_output=True, text=True).stdout
if before != after:
    fail.append('building the share edition changed the full site')
nav = (ROOT / 'assets/portal-navigation.js').read_text()
corner = (ROOT / 'assets/document-corner.js').read_text()
if "dataset.edition='share';" in nav or "edition==='share'" not in nav or "edition === 'share') return" not in corner:
    fail.append('the full site must keep its Documents menu; share behaviour only under data-edition="share"')
if 'html[data-edition=share] [data-doc-note]{display:none}' not in (ROOT / 'assets/portal-navigation.css').read_text():
    fail.append('notes that point to the Documents menu are not hidden in the share edition')
if fail:
    print('FAIL:\n- ' + '\n- '.join(fail)); sys.exit(1)
print(f'PASS: share edition builds with {len(published)} files and none of the {len(docs)} document files; no page lost '
      f'an element id; Questions-for-consensus data present; the full site is unchanged and keeps its Documents menu.')
