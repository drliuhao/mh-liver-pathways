"""The share edition builds and holds no downloadable document (tools/build_share_site.py).

usage: python3 tools/test_share_site.py
       python3 tools/test_share_site.py --sanitize-only  # no output build

- The build succeeds; its own check finds no Word/PDF/PowerPoint/Excel file, no page link to one, no address of the
  full site and every page marked data-edition="share".
- Every published page and data file of the full site is in the share edition, except the documents themselves.
- No page lost an element id (script mount points), and the roadmaps' Questions-for-consensus data are present.
- The full site is unchanged by the build, and its Documents menu and notes still work there (the share switches only
  act on data-edition="share").
"""
import json, re, subprocess, sys, tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
import build_share_site as S

fail = []


def assistant_rules(data):
    return {key: value['rules'] for key, value in data['assistants'].items()}


def compare_assistants(original, public, label):
    expected, actual = assistant_rules(original), assistant_rules(public)
    expected_count = sum(len(rules) for rules in expected.values())
    actual_count = sum(len(rules) for rules in actual.values())
    expected_nulls = sum('branch' in rule and rule['branch'] is None
                         for rules in expected.values() for rule in rules)
    actual_nulls = sum('branch' in rule and rule['branch'] is None
                       for rules in actual.values() for rule in rules)
    if (len(actual), actual_count, actual_nulls) != (len(expected), expected_count, expected_nulls):
        fail.append(f'{label}: clinical assistant/rule/null counts changed')
    if actual != expected:
        fail.append(f'{label}: clinical assistant rules changed during sanitization')
    # A null branch is an explicit stop/hold, distinct from an absent branch key.
    representative = actual['hcc/diagnosis'][0]
    if 'branch' not in representative or representative['branch'] is not None:
        fail.append(f'{label}: HCC diagnosis stop rule lost its explicit null branch')
    return len(expected), expected_count, expected_nulls


null_fixture = {'branch': None, 'nested': {'nullable': None, 'pdf_path': None},
                'values': [None, False, 0, '', {'branch': None}, 'private.docx']}
null_expected = {'branch': None, 'nested': {'nullable': None},
                 'values': [None, False, 0, '', {'branch': None}]}
if S.clean_data(null_fixture) != null_expected or S.clean_data(None) is not None:
    fail.append('authored nulls or other falsy values lost in dictionaries/lists')
clinical_source = json.loads((ROOT/'transplant/assets/content.json').read_text())
clinical_counts = compare_assistants(clinical_source, S.clean_data(clinical_source), 'in-memory share data')

# Private targets can be encoded or hosted through the repository's raw domain.
# Genuine publisher PDFs remain available as publication citations.
for target in ('../protocols/a.pdf', '../protocols/a%2Epdf?download=1',
               '//drliuhao.github.io/mh-liver-pathways/protocols/a.pdf',
               'https://raw.githubusercontent.com/drliuhao/mh-liver-pathways/main/a.pdf',
               'https://drliuhao.github.io/custom-share/a.pdf'):
    if not S.local_doc(target, '', 'custom-share'):
        fail.append(f'private document destination not recognized: {target}')
public_pdf='https://publisher.example/article.pdf'
if S.local_doc(public_pdf, '', 'custom-share'):
    fail.append('external publication PDF must remain available')
fixture={'title':'A randomized clinical trial', 'pmid':'12345', 'doi':'10.1000/example',
         'url':public_pdf, 'slides':[1,2], 'pdf_available':True,
         'local_path':'C:\\private\\article.pdf',
         'nested':{'destination':'https://drliuhao.github.io/custom-share/a.pdf'},
         'depot':'roadmap/PDF_depot/private.pdf'}
cleaned=S.clean_data(fixture,base='custom-share',library=True)
if cleaned != {'title':fixture['title'],'pmid':'12345','doi':'10.1000/example','url':public_pdf,'nested':{}}:
    fail.append(f'private-data sanitization or public-citation retention failed: {cleaned}')

if '--sanitize-only' in sys.argv:
    if fail:
        print('FAIL:\n- ' + '\n- '.join(fail)); sys.exit(1)
    print(f'PASS: no-build sanitization; {clinical_counts[0]} assistants, {clinical_counts[1]} rules and '
          f'{clinical_counts[2]} explicit null branches preserved; null/falsy fixtures and privacy cases pass.')
    sys.exit(0)

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
    compare_assistants(clinical_source, json.loads((out/'transplant/assets/content.json').read_text()),
                       'built share content.json')
    # Every embedded copy is sanitized independently by the builder.
    for page in (out/'transplant').rglob('*.html'):
        for match in re.finditer(r'<script\b[^>]*type=["\']application/json["\'][^>]*>(.*?)</script>',
                                 page.read_text(), re.S):
            embedded=json.loads(match[1])
            if isinstance(embedded,dict) and 'assistants' in embedded:
                compare_assistants(clinical_source, embedded, str(page.relative_to(out)))
    for filename in ('catalog.json','document-index.json'):
        original=json.loads((ROOT/'evidence-libraries'/filename).read_text())
        public=json.loads((out/'evidence-libraries'/filename).read_text())
        if set(original['publications']) != set(public['publications']):
            fail.append(f'{filename}: publication identities lost')
        for key, record in original['publications'].items():
            for field in ('title','doi','pmid','year','publication_type','url','tmc'):
                if record.get(field) != public['publications'][key].get(field):
                    fail.append(f'{filename}: public citation field changed: {key}/{field}')
        original_libraries=original['libraries'].values() if isinstance(original['libraries'],dict) else original['libraries']
        public_libraries=public['libraries'].values() if isinstance(public['libraries'],dict) else public['libraries']
        original_policy=[row['title'] for lib in original_libraries for row in lib.get('policy_records',[])]
        public_policy=[row['title'] for lib in public_libraries for row in lib.get('policy_records',[])]
        if original_policy != public_policy:
            fail.append(f'{filename}: policy citation titles lost')
    # The final scanner must reject an unexpected binary even when its suffix is new.
    binary=out/'unexpected-download.zip';binary.write_bytes(b'PK\x03\x04private payload')
    try:
        S.check(out,'mh-liver-pathways-share')
        fail.append('unexpected binary was accepted')
    except SystemExit as exc:
        if 'unexpected-download.zip' not in str(exc):
            fail.append(f'unexpected failure while testing binary rejection: {exc}')
    finally:
        binary.unlink()
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
      f'an element id; Questions-for-consensus data and publication citations retained; encoded/private destinations and '
      f'unknown binaries rejected; {clinical_counts[0]} clinical assistants/{clinical_counts[1]} rules/'
      f'{clinical_counts[2]} null branches preserved; the full site is unchanged and keeps its Documents menu.')
