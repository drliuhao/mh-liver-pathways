"""Static check of the previously-treated-extrahepatic-disease positions page.

usage: python3 tools/test_ehd_positions.py

- extrahepatic-disease/index.html is exactly what tools/build_ehd_page.py builds from tools/ehd_positions.json.
- Every roadmap link to the page lands on a question section, and every question is reachable from a
  roadmap decision or a transplant high-risk review (transplant/<slug>/#high-risk-<anchor> exists in the data).
- Every study line names its source and read status; abstract-only sources are labelled as such.
- The page is noindex, marks every position as proposed, and publishes no local paths or licensed PDFs.
"""
import json, re, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
page_file = ROOT / 'extrahepatic-disease/index.html'
before = page_file.read_text()
subprocess.run([sys.executable, str(ROOT / 'tools/build_ehd_page.py')], check=True, capture_output=True)
page = page_file.read_text()
fail = []
if page != before:
    fail.append('page is stale: rerun tools/build_ehd_page.py')

data = json.loads((ROOT / 'tools/ehd_positions.json').read_text())
ids = [q['id'] for q in data['questions']]
sections = re.findall(r'<section class="review-decision [^"]+" id="([^"]+)" data-ehd-question=', page)
if sections != ids:
    fail.append(f'sections {sections} != questions {ids}')

links = json.loads((ROOT / 'assets/roadmap-links.json').read_text())
targets = {}
for slug, gates in links.items():
    for gid, recs in gates.items():
        for r in recs:
            m = re.fullmatch(r'extrahepatic-disease/#(.+)', r.get('url', ''))
            if m:
                targets.setdefault(m.group(1), []).append(f'{slug}/{gid}')
                if m.group(1) not in ids:
                    fail.append(f'{slug}/{gid} links to missing question {m.group(1)}')
                if f'/mh-liver-pathways/{slug}/#decision-{gid}"' not in page:
                    fail.append(f'{m.group(1)} does not link back to {slug} decision {gid}')

anchors = set(re.findall(r'"anchor": "([a-z0-9-]+)"', (ROOT / 'transplant/assets/content.json').read_text()))
for slug, anchor in re.findall(r'/mh-liver-pathways/transplant/([a-z]+)/#high-risk-([a-z0-9-]+)"', page):
    if anchor not in anchors:
        fail.append(f'transplant/{slug}/#high-risk-{anchor}: no such review')
transplant_q = [q['id'] for q in data['questions'] if q['setting'] == 'transplant']
for q in data['questions']:
    if q['setting'] == 'roadmap' and q['id'] not in targets:
        fail.append(f'{q["id"]}: no roadmap decision links here')
    for s in q['evidence']:
        if s['key'] not in data['sources']:
            fail.append(f'{q["id"]}: unknown source {s["key"]}')
    if q['read_full'] + q['read_abstract'] > len(q['evidence']):
        fail.append(f'{q["id"]}: read counts exceed study lines')
n_lines = sum(len(q['evidence']) for q in data['questions'])
n_abs = sum(1 for q in data['questions'] for s in q['evidence'] if s['read'] == 'abstract')
if page.count('class="study ehd-study"') != n_lines:
    fail.append('study line count mismatch')
if page.count('Abstract only · full text pending') != n_abs:
    fail.append('abstract-only labels mismatch')
if '<meta name="robots" content="noindex">' not in page:
    fail.append('missing noindex')
if page.count('Open proposal') != len(ids) or 'Nothing is activated' not in page:
    fail.append('every position must be labelled as an open proposal')
for bad in ('/Users/', 'file://', 'computer://', 'SynologyDrive', '.pdf"'):
    if bad in page:
        fail.append(f'private path or licensed PDF link: {bad}')
if '/mh-liver-pathways/extrahepatic-disease/' not in (ROOT / 'transplant/high-risk/index.html').read_text():
    fail.append('transplant high-risk overview does not link to the positions page')

if fail:
    print('FAIL:\n- ' + '\n- '.join(fail)); sys.exit(1)
print(f'PASS: {len(ids)} questions ({len(transplant_q)} transplant, {len(ids) - len(transplant_q)} roadmap) built from current data; '
      f'{sum(len(v) for v in targets.values())} roadmap decisions land on their question and are linked back; '
      f'{n_lines} study lines with read status ({n_abs} abstract only); noindex; no private paths or licensed PDFs.')
