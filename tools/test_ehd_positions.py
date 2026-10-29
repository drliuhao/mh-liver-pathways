"""Static check of the previously-treated-extrahepatic-disease index page.

usage: python3 tools/test_ehd_positions.py

- extrahepatic-disease/index.html is exactly what tools/build_ehd_page.py builds.
- It indexes every question and not-applicable note once and repeats no position text (each question lives in its
  own setting: roadmap Questions for consensus, or the transplant high-risk view).
- Every roadmap link to a question lands on a question present in that tumor's questions.json; every transplant
  link lands on a high-risk review that exists. The roadmap decisions link to their own roadmap's question.
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
manifest = json.loads((ROOT / 'assets/documents.json').read_text())['tumors']
ids = [q['id'] for q in data['questions']]
for q in data['questions']:
    if page.count(f'<b>{q["id"]}</b>') != 1:
        fail.append(f'{q["id"]} not indexed exactly once')
    if q['position'][:60] in page:
        fail.append(f'{q["id"]}: position text repeated on the index')
for n in data['not_applicable']:
    if n['position'] not in page:
        fail.append(f'{n["tumor"]} not-applicable note missing')
by_roadmap = {t['roadmap']: k for k, t in manifest.items() if t['roadmap']}
for slug, qid in re.findall(r'href="/mh-liver-pathways/([a-z]+)/#question-([^"]+)"', page):
    qs = json.loads((ROOT / 'documents' / by_roadmap[slug] / 'questions.json').read_text())
    if qid not in [q['id'] for q in qs['sets']['roadmap']['questions']]:
        fail.append(f'{slug}/#question-{qid}: no such roadmap question')
anchors = set(re.findall(r'"anchor": "([a-z0-9-]+)"', (ROOT / 'transplant/assets/content.json').read_text()))
for slug, anchor in re.findall(r'href="/mh-liver-pathways/transplant/([a-z]+)/#high-risk-([a-z0-9-]+)"', page):
    if anchor not in anchors:
        fail.append(f'transplant/{slug}/#high-risk-{anchor}: no such review')
links = json.loads((ROOT / 'assets/roadmap-links.json').read_text())
n_links = 0
for slug, gates in links.items():
    for gid, recs in gates.items():
        for r in recs:
            if 'extrahepatic-disease/' in r.get('url', ''):
                fail.append(f'{slug}/{gid}: still links to the cross-tumor page; link to the roadmap question instead')
            m = re.fullmatch(rf'{slug}/#question-(.+)', r.get('url', ''))
            if m:
                n_links += 1
                if m.group(1) not in ids:
                    fail.append(f'{slug}/{gid}: unknown question {m.group(1)}')
if '<meta name="robots" content="noindex">' not in page or 'Nothing is activated' not in page:
    fail.append('index must be noindex and state that nothing is activated')
if fail:
    print('FAIL:\n- ' + '\n- '.join(fail)); sys.exit(1)
print(f'PASS: index lists {len(ids)} questions and {len(data["not_applicable"])} not-applicable notes once, repeats no position text; '
      f'{n_links} roadmap decisions link to their own roadmap question; every link lands on an existing question.')
