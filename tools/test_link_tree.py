"""Static check of the site's link tree: one page per transplant pathway, no duplicate copies, no dead internal links.

usage: python3 tools/test_link_tree.py

- Each transplant pathway exists once, at transplant/<slug>/. The meeting record (#meeting, #meeting-<question>)
  and the high-risk protocols (#high-risk, #high-risk-<review>) are views of that page.
- The old alignment-record URLs (transplant/alignment/<slug>.html and /<slug>/) are small redirects to
  that page (#<question> becomes #meeting-<question>), not second copies of it, and nothing links to them.
- The transplant/high-risk/<slug>/ pages redirect to the pathway's high-risk view (they keep the archived V7
  review text for readers without JavaScript).
- Every internal href/src in the published HTML, and every internal URL in the transplant protocol data,
  resolves to a file in the repository.
"""
import json, re, subprocess, sys
from pathlib import Path
from urllib.parse import urlsplit, unquote

ROOT = Path(__file__).resolve().parents[1]
BASE = '/mh-liver-pathways/'
SITE = 'https://drliuhao.github.io/mh-liver-pathways/'
files = subprocess.check_output(['git', 'ls-files'], cwd=ROOT, text=True).split('\n')
html = [f for f in files if f.endswith('.html')]
failures = []

slugs = [p['slug'] for p in json.loads((ROOT / 'transplant/assets/content.json').read_text())['index']]
assert slugs == ['hcc', 'pcca', 'icca', 'crlm', 'nelm', 'hehe', 'hca'], slugs

# 1. One full page per pathway (plus the transplant home); the alignment URLs are redirects.
with_data = sorted(f for f in html if 'id="protocol-data"' in (ROOT / f).read_text(encoding='utf-8'))
want = sorted(['transplant/index.html'] + [f'transplant/{s}/index.html' for s in slugs])
if with_data != want:
    failures.append(f'pages embedding the protocol data: {with_data}')
for s in slugs:
    for f, target in [(f'transplant/alignment/{s}.html', f'../{s}/'), (f'transplant/alignment/{s}/index.html', f'../../{s}/')]:
        t = (ROOT / f).read_text(encoding='utf-8')
        if len(t.encode()) > 2000 or f'location.replace("{target}"+(q?(' not in t or '"#meeting-"+q' not in t or f'url={target}#meeting' not in t:
            failures.append(f'{f}: expected a small redirect to {target}#meeting')

# 2. Nothing links to the retired copies.
code = [f for f in files if f.endswith(('.html', '.js', '.json', '.py', '.cjs'))
        and not f.startswith(('transplant/alignment/', 'tools/test_')) and f != 'tools/v12_content_snapshot.json']
for f in code:
    t = (ROOT / f).read_text(encoding='utf-8', errors='replace')
    if re.search(r'transplant/alignment/|["\'/]alignment/\$\{', t):
        failures.append(f'{f}: links to a retired alignment copy')
# The high-risk review pages are redirects to the pathway view (#high-risk-<review>); keep them as such.
for s in slugs:
    t = (ROOT / f'transplant/high-risk/{s}/index.html').read_text(encoding='utf-8')
    if f'location.replace("/mh-liver-pathways/transplant/{s}/#high-risk"' not in t:
        failures.append(f'transplant/high-risk/{s}/: expected a redirect to the pathway view')

# 3. Internal links resolve.
for f in ('transplant/assets/app.js', 'tools/decision_assistant_source/app.js'):
    app = (ROOT / f).read_text()
    assert 'href="#meeting-${i.id}" data-issue="${i.id}"' in app, f'{f}: meeting links must also work when copied or opened in a new tab'

def target(url, page):
    """Repository path for an internal URL, or None when the URL is external, an anchor or a template."""
    if not url or url.startswith(('#', 'mailto:', 'tel:', 'javascript:', 'data:')) or '${' in url or '{' in url:
        return None
    if url.startswith(SITE):
        url = BASE + url[len(SITE):]
    u = urlsplit(url)
    if u.scheme or u.netloc:
        return None
    path = unquote(u.path)
    if path.startswith(BASE):
        rel = path[len(BASE):]
    elif path.startswith('/'):
        return ('outside', path)
    else:
        rel = str((Path(page).parent / path).as_posix())
    parts = []
    for x in rel.split('/'):
        if x == '..':
            if parts: parts.pop()
        elif x not in ('', '.'):
            parts.append(x)
    rel = '/'.join(parts)
    return rel + ('/index.html' if (path.endswith('/') or (ROOT / rel).is_dir()) and rel else ('index.html' if not rel else ''))

checked = 0
attr = re.compile(r'\b(?:href|src)="([^"]+)"|content="0;\s*url=([^"]+)"')
for f in html:
    t = (ROOT / f).read_text(encoding='utf-8')
    t = re.sub(r'<script id="protocol-data".*?</script>', '', t, flags=re.S)
    for m in attr.finditer(t):
        r = target((m[1] or m[2]).replace('&amp;', '&'), f)
        if r is None:
            continue
        checked += 1
        if isinstance(r, tuple):
            failures.append(f'{f}: root-relative link outside the site: {r[1]}')
        elif not (ROOT / r).is_file():
            failures.append(f'{f}: missing {m[1] or m[2]}')

def urls(x):
    if isinstance(x, dict):
        for k, v in x.items():
            if k in ('url', 'href', 'protocol', 'pdf') and isinstance(v, str) and v.startswith(('/', 'http', './', '../')):
                yield v
            else:
                yield from urls(v)
    elif isinstance(x, list):
        for v in x:
            yield from urls(v)

data = json.loads((ROOT / 'transplant/assets/content.json').read_text())
matrix_text = (ROOT / 'systemic/matrix.json').read_text()
for old_url, new_url in json.loads((ROOT / 'tools/systemic_link_targets.json').read_text()).items():
    assert old_url not in matrix_text and new_url in matrix_text, 'Matrix review links must be direct'
    destination = urlsplit(new_url)
    slug = destination.path.rstrip('/').split('/')[-1]
    review = destination.fragment.removeprefix('high-risk-')
    assert destination.fragment.startswith('high-risk-')
    assert any(r['anchor'] == review for r in data['high_risk']['pathways'][slug]['reviews']), new_url
for u in set(urls(data)):
    r = target(u, 'transplant/index.html')
    if r is None:
        continue
    checked += 1
    if isinstance(r, tuple) or not (ROOT / r).is_file():
        failures.append(f'protocol data: missing {u}')

assert not failures, '\n'.join(failures[:40])
print(f'PASS: {len(slugs)} transplant pathways each published once ({len(with_data)} pages carry the protocol data); '
      f'{2 * len(slugs)} alignment URLs are small redirects and nothing links to them; the high-risk review pages '
      f'redirect to the pathway view; {checked} internal links resolve.')
