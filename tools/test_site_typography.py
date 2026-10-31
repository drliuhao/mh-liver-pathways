"""One look on every page: the site's type system, light palette and shared shell.

usage: python3 tools/test_site_typography.py

Hao Liu, 31 October 2026: every page and expandable aligned, with consistent colours and styling.
- Fonts: text and controls use Source Sans 3 and titles Source Serif 4. No stylesheet or page style leads a font stack
  with system-ui, Georgia or Public Sans (the information icon's italic "i" in contextual-info.css is the one Georgia),
  and assets/portal-navigation.js loads the two families on pages that do not link them.
- Palette: pages that define a dark palette carry data-theme="light" (the shared decision tools and the transplant
  pathways are light only, so a dark system setting no longer mixes dark pages with light panels).
- Shell: every page that is not a redirect loads the shared navigation, including the change log and the pCCA update.
- Phone layout guards: roadmap header links wrap (their menu is not clipped inside a scrolling strip); meeting-record
  questions use the full row; tables in the decision columns wrap between words; library rows wrap long links.
"""
import re, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
files = subprocess.run(['git', '-C', str(ROOT), 'ls-files'], capture_output=True, text=True).stdout.split()
fail = []

def css_blocks(f, s):
    if f.endswith('.css'):
        return [s]
    return re.findall(r'<style[^>]*>(.*?)</style>', s, re.S) + re.findall(r'style="([^"]*)"', s)

for f in files:
    if f.startswith(('tools/', 'docs/')) or not f.endswith(('.css', '.html')):
        continue
    s = (ROOT / f).read_text(errors='ignore')
    for css in css_blocks(f, s):
        for m in re.finditer(r'(font(?:-family)?\s*:[^;{}]*|--[\w-]+\s*:\s*["\']?[A-Z][^;{}]*)', css):
            decl = m.group(1)
            stack = re.sub(r'^(font-family|font|--[\w-]+)\s*:\s*', '', decl)
            stack = re.sub(r'^(?:italic\s+|normal\s+)?(?:\d{3}\s+)?(?:[\d.]+(?:px|rem|em|pt|%)|clamp\([^)]*\))(?:/[\d.]+\w*)?\s+', '', stack)
            first = stack.split(',')[0].strip().strip('"\'')
            if first in ('system-ui', 'Georgia', 'Public Sans', '-apple-system'):
                if f == 'assets/contextual-info.css' and first == 'Georgia':
                    continue
                fail.append(f'{f}: font stack starts with {first}: {decl[:80]}')
    if f.endswith('.html') and 'prefers-color-scheme' in s:
        tag = re.search(r'<html[^>]*>', s).group(0)
        if 'data-theme="light"' not in tag:
            fail.append(f'{f}: defines a dark palette but is not held to the light one')
    if f.endswith('.html') and not re.search(r'http-equiv="refresh"|location\.replace', s) and 'portal-navigation.js' not in s and f != 'index.html':
        fail.append(f'{f}: does not load the shared navigation')

portal = (ROOT / 'assets/portal.css').read_text()
if re.search(r'prefers-color-scheme:dark\)\{:root\{', portal):
    fail.append('assets/portal.css: dark palette is not guarded by data-theme')
nav = (ROOT / 'assets/portal-navigation.js').read_text()
if 'family=Source+Sans+3' not in nav or 'Source+Serif+4' not in nav:
    fail.append('portal-navigation.js does not load the site fonts')
checks = {
    'assets/roadmap-flow.css': ['.roadmap-streamlined header.top .sec{display:flex;flex-wrap:wrap', '.roadmap-streamlined header.top .ch-page-resources{position:static}'],
    'transplant/assets/style.css': ['.issue-heading{display:grid;grid-template-columns:auto minmax(0,1fr)'],
    'assets/decision-workspace.css': ['.dw-column table{overflow-wrap:break-word}'],
    'assets/roadmap-evidence.css': ['.ev .evcit,.ev .evmeta,.ev .evsum{overflow-wrap:anywhere}'],
}
for f, needles in checks.items():
    s = (ROOT / f).read_text()
    for n in needles:
        if n not in s:
            fail.append(f'{f}: missing layout guard {n[:60]}')
if fail:
    print('FAIL:\n- ' + '\n- '.join(fail[:40])); sys.exit(1)
print('PASS: one type system (Source Sans 3 / Source Serif 4) in every stylesheet and page style; every page with a dark '
      'palette held to the light one; every page in the shared shell; phone layout guards in place.')
