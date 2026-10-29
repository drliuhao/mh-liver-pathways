"""Standardized documents: complete, public-safe, and offered once.

usage: python3 tools/test_documents.py

- documents/<tumor>/questions.json and assets/documents.json are exactly what tools/build_consensus.py builds.
- Every roadmap decision still to be made (pathway.json ops.approvals; HCC APPROVALS and RATIFY), every transplant
  meeting question and every high-risk review appears once as a consensus question, with no duplicate ids.
- Every file in the manifest exists, is a valid Word package, and carries no local path, file link or licensed PDF.
- Each questions file names every question of its set; each decision-discussion file names every question of the tumor.
- Old download lists are gone: no meeting-record document box, no roadmap 'Roadmap document' link, no high-risk
  download list. The Documents corner is the single place to download each file.
"""
import base64, json, re, subprocess, sys, zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
fail = []
snap = {p: p.read_text() for p in [ROOT / 'assets/documents.json', *sorted((ROOT / 'documents').glob('*/questions.json'))]}
subprocess.run([sys.executable, str(ROOT / 'tools/build_consensus.py')], check=True, capture_output=True)
for p, text in snap.items():
    if p.read_text() != text:
        fail.append(f'{p.relative_to(ROOT)} is stale: rerun tools/build_consensus.py')
manifest = json.loads((ROOT / 'assets/documents.json').read_text())['tumors']
content = json.loads((ROOT / 'transplant/assets/content.json').read_text())
assert len(manifest) == 13, len(manifest)


def hcc_constants():
    s = (ROOT / 'hcc/index.html').read_text()
    out = subprocess.run(['node', '-e', """
const s=require('fs').readFileSync(process.argv[1],'utf8'),vm=require('vm');
const g=k=>{const a=s.indexOf('const '+k+' =');const b=s.indexOf('\\n];',a)+3;return vm.runInNewContext(s.slice(a,b).replace('const '+k+' =','x=')+';x');};
console.log(JSON.stringify({a:g('APPROVALS'),r:g('RATIFY')}));""", str(ROOT / 'hcc/index.html')], capture_output=True, text=True, check=True).stdout
    return json.loads(out)


n_q = n_files = 0
for key, t in manifest.items():
    data = json.loads((ROOT / 'documents' / key / 'questions.json').read_text())
    ids = [q['id'] for s in data['sets'].values() for q in s['questions']]
    if len(ids) != len(set(ids)):
        fail.append(f'{key}: duplicate question ids')
    n_q += len(ids)
    if t['roadmap']:
        qs = [q['question'] for q in data['sets']['roadmap']['questions']]
        if t['roadmap'] == 'hcc':
            k = hcc_constants()
            want = k['a']; ratify = [x for _, items in k['r'] for x in items]
            got_r = [r['question'] for r in data['sets']['roadmap']['ratify']]
            if got_r != ratify:
                fail.append('hcc: ratification items differ from the roadmap')
        else:
            want = [re.sub(r'<[^>]+>', '', a['q']).strip() for a in json.loads((ROOT / t['roadmap'] / 'data/pathway.json').read_text())['ops']['approvals']]
        for w in want:
            if re.sub(r'\s+', ' ', w) not in [re.sub(r'\s+', ' ', q) for q in qs]:
                fail.append(f'{key}: roadmap decision missing from questions: {w[:70]}')
    if t['transplant']:
        p = next(x for x in content['index'] if x['slug'] == t['transplant'])
        if len(data['sets']['standard']['questions']) != len(p['issues']):
            fail.append(f'{key}: standard questions != meeting questions')
        reviews = content['high_risk']['pathways'][t['transplant']]['reviews']
        if [q['id'] for q in data['sets']['highrisk']['questions']] != [r['id'] for r in reviews]:
            fail.append(f'{key}: high-risk questions != reviews')
    # Files
    for slot, name in t['files'].items():
        f = ROOT / 'documents' / key / name
        if not f.exists():
            fail.append(f'missing {f.relative_to(ROOT)}'); continue
        n_files += 1
        with zipfile.ZipFile(f) as z:
            if z.testzip() is not None:
                fail.append(f'{name}: corrupt'); continue
            blob = b''.join(z.read(n) for n in z.namelist() if n.endswith(('.xml', '.rels')))
            doc = z.read('word/document.xml').decode('utf8')
        for bad in (b'file:///', b'/Users/', b'SynologyDrive', b'PDF_depot'):
            if bad in blob:
                fail.append(f'{name}: private path {bad.decode()}')
        for d in re.findall(r'<w:fldData[^>]*>([^<]+)</w:fldData>', doc):
            try: dec = base64.b64decode(d)
            except Exception: continue
            if b'file:' in dec or b'/Users/' in dec:
                fail.append(f'{name}: private path inside a citation payload'); break
        text = re.sub(r'<[^>]+>', '', doc)
        if slot.endswith('_questions'):
            for q in data['sets'][slot.replace('_questions', '')]['questions']:
                if q['id'] not in text:
                    fail.append(f'{name}: {q["id"]} missing')
        if slot == 'decision':
            for i in ids:
                if i not in text:
                    fail.append(f'{name}: {i} missing')
app = (ROOT / 'transplant/assets/app.js').read_text()
if 'docbox' in app or 'Protocol & meeting documents' in app:
    fail.append('transplant meeting record still lists its own documents')
if '${downloads(data,slug)}' in (ROOT / 'transplant/assets/high-risk.js').read_text():
    fail.append('high-risk view still lists its own documents')
for slug in [t['roadmap'] for t in manifest.values() if t['roadmap']]:
    s = (ROOT / slug / 'index.html').read_text()
    if 'Roadmap document · Word' in s:
        fail.append(f'{slug}: old roadmap document link')
    if 'id:"appr"' in s or 'id:"rat"' in s:
        fail.append(f'{slug}: approvals still duplicated in the operations tabs')
nav = (ROOT / 'assets/portal-navigation.js').read_text()
if "'document-corner.js'" not in nav or 'document-corner.css' not in nav:
    fail.append('portal navigation must load the Documents corner')
if fail:
    print('FAIL:\n- ' + '\n- '.join(fail[:60])); sys.exit(1)
print(f'PASS: 13 tumors, {n_q} consensus questions (every roadmap decision, meeting question and high-risk review once); '
      f'{n_files} Word files present, valid and free of local paths; each questions file and decision file names its questions; '
      'old download lists removed; corner loaded.')
