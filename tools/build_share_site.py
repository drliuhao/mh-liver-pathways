"""Build the share edition of the website: every page and tool, without the downloadable documents.

usage: python3 tools/build_share_site.py <output folder> [--base mh-liver-pathways-share]

Hao Liu, 31 October 2026: "a sharable version of the website where the downloadable documents are not available".
- Copies every published file (git ls-files) except tools/, docs/, the repository notes (*.md) and the site's own Word,
  PDF, PowerPoint and Excel files (documents/<tumor>/, evidence/2026-10-25/docs/, transplant/docs/,
  transplant/high-risk/docs/, transplant/protocols/, lrt/*.pdf), and the index of the high-risk protocol files.
- Serves under its own base path: every /mh-liver-pathways/ address, the absolute drliuhao.github.io address and the
  page-slug helper point at the share edition, so no page loads or links back to the full site.
- Marks every page data-edition="share" (assets/portal-navigation.js also sets it): the Documents menu is not built,
  notes that point to it are hidden, links to the site's own documents are removed here and, for anything a page
  renders later, by assets/portal-navigation.js.
- Drops the link to the repository history (the repository holds the documents).
- Checks the result: no document file, no link to one in a page, no address of the full site.
"""
import re, shutil, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FULL = 'mh-liver-pathways'
DOC = re.compile(r'\.(?:docx?|pdf|pptx?|xlsx?)$', re.I)
SKIP_DIRS = ('tools/', 'docs/')
SKIP_FILES = {'transplant/high-risk/authored-documents.json'}  # assets/documents.json stays: it also drives the roadmaps' Questions for consensus
TEXT = ('.html', '.js', '.css', '.json', '.svg', '.txt', '.xml', '.webmanifest')


def published():
    files = subprocess.run(['git', '-C', str(ROOT), 'ls-files'], capture_output=True, text=True, check=True).stdout.split()
    for f in files:
        if f.startswith(SKIP_DIRS) or f in SKIP_FILES or DOC.search(f) or (f.endswith('.md') and '/' not in f):
            continue
        if not (ROOT / f).exists():
            continue
        yield f


def local_doc(href, page, base):
    """True when the link opens one of the site's own document files."""
    href = href.split('#')[0].split('?')[0]
    if not DOC.search(href):
        return False
    if re.match(r'https?://', href):
        return f'.github.io/{base}/' in href or f'.github.io/{FULL}/' in href
    return True


ANCHOR = re.compile(r'<a\b[^>]*\bhref=(["\'])(.*?)\1[^>]*>(.*?)</a>', re.S)


def strip_links(html, page, base):
    def rep(m):
        if not local_doc(m.group(2), page, base):
            return m.group(0)
        inner = m.group(3)
        return inner if re.search(r'<(img|svg|picture)\b', inner) else '\x00'
    html = ANCHOR.sub(rep, html)
    # the separator that joined a removed link to its neighbour, then an element the removal left empty (only
    # those: empty elements elsewhere are mount points that scripts fill)
    html = re.sub(r'\s*[·|]\s*\x00|\x00\s*[·|]\s*', '\x00', html)
    for _ in range(3):
        html = re.sub(r'<(p|li|span|small|div)(\s[^>]*)?>\s*\x00\s*</\1>', '\x00', html)
    return html.replace('\x00', '')


def build(out, base):
    out = Path(out)
    if out.exists():
        for child in out.iterdir():
            if child.name == '.git':
                continue
            shutil.rmtree(child) if child.is_dir() else child.unlink()
    out.mkdir(parents=True, exist_ok=True)
    n = 0
    for f in published():
        src, dst = ROOT / f, out / f
        dst.parent.mkdir(parents=True, exist_ok=True)
        if not f.endswith(TEXT):
            shutil.copyfile(src, dst); n += 1
            continue
        s = src.read_text(encoding='utf8')
        # every address of the full site -> the share edition (the repository history link is removed below)
        s = re.sub(r'(?<![\w/.-]github\.com/drliuhao)/' + FULL + r'/', f'/{base}/', s)
        s = s.replace(f"parts.indexOf('{FULL}')", f"parts.indexOf('{base}')")
        if f.endswith('.html'):
            s = re.sub(r'<p>\s*<a href="https://github\.com/drliuhao/[^"]*">[^<]*</a>\s*</p>', '', s)
            s = re.sub(r'<a href="https://github\.com/drliuhao/[^"]*">([^<]*)</a>', r'\1', s)
            s = re.sub(r'<html\b(?![^>]*data-edition)', '<html data-edition="share"', s, count=1)
            s = strip_links(s, f, base)
        if f == 'assets/portal-navigation.js':
            s = s.replace('(() => {', "(() => {\n  document.documentElement.dataset.edition='share';", 1)
            assert "dataset.edition='share';" in s, 'portal-navigation.js entry point changed'
        dst.write_text(s, encoding='utf8'); n += 1
    (out / 'robots.txt').write_text('User-agent: *\nDisallow: /\n')
    check(out, base)
    print(f'Share edition: {n} files in {out} (base /{base}/); no document files, no links to them, no address of the full site.')


def check(out, base):
    fail = []
    for p in out.rglob('*'):
        if p.is_dir() or '.git' in p.parts:
            continue
        rel = p.relative_to(out).as_posix()
        if DOC.search(rel):
            fail.append(f'document file published: {rel}')
            continue
        if not rel.endswith(TEXT):
            continue
        s = p.read_text(encoding='utf8', errors='ignore')
        if re.search(r'(?<![\w/.-]github\.com/drliuhao)/' + FULL + r'/', s):
            fail.append(f'{rel}: still addresses the full site')
        if 'github.com/drliuhao/' + FULL in s and rel.endswith('.html'):
            fail.append(f'{rel}: links to the repository')
        if rel.endswith('.html'):
            for m in ANCHOR.finditer(s):
                if local_doc(m.group(2), rel, base):
                    fail.append(f'{rel}: links to a document ({m.group(2)[:80]})')
            if 'data-edition="share"' not in s[:400]:
                fail.append(f'{rel}: not marked as the share edition')
    nav = (out / 'assets/portal-navigation.js').read_text()
    if "dataset.edition='share'" not in nav or "edition==='share'" not in nav:
        fail.append('portal-navigation.js does not run the share edition')
    if "edition === 'share') return" not in (out / 'assets/document-corner.js').read_text():
        fail.append('document-corner.js would still build the Documents menu')
    if fail:
        raise SystemExit('FAIL:\n- ' + '\n- '.join(fail[:40]))


if __name__ == '__main__':
    args = sys.argv[1:]
    if not args:
        raise SystemExit(__doc__)
    base = 'mh-liver-pathways-share'
    if '--base' in args:
        base = args[args.index('--base') + 1]
    build(args[0], base)
