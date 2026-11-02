"""Check local URLs, retained clinical payloads, and the public-file allowlist."""
import json
import hashlib
import re
import sys
from html import unescape
from pathlib import Path
from urllib.parse import unquote, urlsplit
from build_portal import ROOT, BASE, ROADMAPS, transform
from current_downloads import canonical_files

source=Path(sys.argv[1])
expected=json.loads((source/'assets/content.json').read_text())
actual=json.loads((ROOT/'transplant/assets/content.json').read_text())
assert actual==transform(expected), 'Clinical payload changed beyond URL transform'
problems=[]
checked=0
for file in [ROOT/'index.html']+list((ROOT/'transplant').rglob('*.html'))+list((ROOT/'systemic').rglob('*.html')):
    text=file.read_text()
    for url in re.findall(r'(?:href|src)="([^"]+)"',text):
        url=unescape(url);parsed=urlsplit(url)
        if parsed.scheme or parsed.netloc or not parsed.path:continue
        path=unquote(parsed.path)
        if path.startswith(BASE+'/'):target=ROOT/path[len(BASE)+1:]
        elif path.startswith('/'):problems.append(f'Wrong base: {file}:{url}');continue
        else:target=file.parent/path
        if target.is_dir():target=target/'index.html'
        checked+=1
        if not target.is_file():problems.append(f'Missing: {file}:{url}')
for p in actual['index']:
    assert len({d['url'] for d in p['docs']})>=2
    for url in [p['protocol']]+[d['url'] for d in p['docs']]:
        assert (ROOT/url.removeprefix(BASE+'/')).is_file(),url
    for s in p['steps']:
        for issue in s['issues']:assert any(i['id']==issue for i in p['issues'])
    old=next(x for x in expected['index'] if x['slug']==p['slug'])
    assert len(p['steps'])==len(old['steps'])
assert len(re.findall(r'class="portal-card"', (ROOT/'index.html').read_text()))==22
for _,slug,_,_,_ in ROADMAPS:assert 'portal-navigation.js' in (ROOT/slug/'index.html').read_text()
assert not list((ROOT/'transplant/protocols').glob('*.docx'))
assert not list((ROOT/'transplant/docs').glob('*.docx'))
assert len(canonical_files())==65 and all((ROOT/rel).is_file() for rel in canonical_files())
authored=json.loads((ROOT/'transplant/high-risk/authored-documents.json').read_text())
public_pdfs=list((ROOT/'transplant').rglob('*.pdf'))
assert not public_pdfs
assert len(authored)==7 and all((ROOT/x['path']).is_file() for x in authored)
for file in (ROOT/'transplant').rglob('*'):
    if file.is_file() and file.suffix in ('.json','.html','.js'):
        assert '/evidence/' not in file.read_text(),str(file)
if problems:raise SystemExit('\n'.join(problems))
print(f'PASS: {checked} static local links; 22 portal cards; 65 current Word documents; clinical content preserved; no local PDF upload.')
