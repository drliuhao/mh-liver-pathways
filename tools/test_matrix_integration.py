"""Check evidence identifiers, public-file boundaries and clinical review destinations."""
import json,re,subprocess,hashlib,shutil
from pathlib import Path
from urllib.parse import urlsplit,unquote

ROOT=Path(__file__).resolve().parents[1]
data=json.loads((ROOT/'transplant/assets/content.json').read_text())
# Replay every recorded release content edit through the same strict exact-value applier.
# File-only manifests are valid; unrecorded changes anywhere in content.json still fail.
node=shutil.which('node') or str(Path.home()/'.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node')
replay=r"""
const cp=require('node:child_process'), R=require('./tools/apply_clinical_revisions.cjs');
const base=JSON.parse(cp.execFileSync('git',['show','30039fe:transplant/assets/content.json'],{encoding:'utf8'}));
const revisions=R.revisions().filter(r=>r.id.startsWith('2026-11-02'));
if(!revisions.length)throw new Error('No recorded release revisions found');
process.stdout.write(JSON.stringify(R.applyContent(base,revisions)));
"""
expected=json.loads(subprocess.check_output([node,'-e',replay],cwd=ROOT))
assert data==expected, 'Content differs from exact 30039fe baseline plus recorded 2026-11-02 revisions'

links=[]
for config in data['continuations'].values():
 for kind in ['branches','rules']:
  for actions in config[kind].values():links.extend(a['url'] for a in actions if a.get('url'))
for plans in data['care'].values():
 for plan in plans:links.extend(a['url'] for a in plan['actions'] if a.get('url'))
review_links=[x for x in links if '/transplant/high-risk/' in x]
assert len(review_links)==3, "Specific AFP, ICI and CRLM continuing-care links; decisions use tested conditional routing"
for url in review_links:
 u=urlsplit(url);p=ROOT/unquote(u.path).removeprefix('/mh-liver-pathways/');p=p/'index.html' if p.is_dir() else p
 assert p.is_file(),url
 if u.fragment:assert f'id="{u.fragment}"' in p.read_text(),url
assert not (ROOT/'transplant/high-risk/pdac').exists()
for page in (ROOT/'transplant/high-risk').rglob('*.html'):
 t=page.read_text();assert '/Users/' not in t and 'file://' not in t,page
 assert 'not been activated' in t or 'proposals remain open' in t,page
 assert not re.search(r'href="[^"]*pdac',t,re.I),page
assert 'Expansion remains closed' in (ROOT/'transplant/high-risk/pcca/index.html').read_text()
assert 'separate multifocal tumors in different segments' in (ROOT/'transplant/high-risk/icca/index.html').read_text()
assert 'Systemic treatment options' not in (ROOT/'transplant/high-risk/hca/index.html').read_text()

matrix=json.loads((ROOT/'systemic/matrix.json').read_text());refs=json.loads((ROOT/'systemic/references.json').read_text())
assert len({c['id'] for c in matrix['cards']})==len(matrix['cards'])==49
assert set(t for c in matrix['cards'] for t in c['tumors'])=={'hcc','pcca','icca','crlm','nelm','pdac','pnet','ampullary','chcca'}
for c in matrix['cards']:
 assert c['refs'] or c['links'],c['id']
 for pm in c['refs']:assert pm in refs,(c['id'],pm)
for pm,r in refs.items():
 assert all(r[k] for k in ['author','journal','year','doi','pmid','title','tmc']),pm
 assert ('thslc-houston.primo.exlibrisgroup.com/discovery/search' in r['tmc'] or r['tmc'].startswith('https://libkey.io/libraries/480/')),pm
 assert r['doi'] in unquote(r['tmc']),pm
 assert r['pmid']==pm
 assert not any(k in r for k in ['abstract','pdf_file','origin']),pm
assert not list((ROOT/'systemic').rglob('*.pdf'))
authored=json.loads((ROOT/'transplant/high-risk/authored-documents.json').read_text())
allowed={x['path']:x['sha256'] for x in authored if x['path'].endswith('.pdf')}
public_pdfs=list((ROOT/'transplant').rglob('*.pdf'))
assert len(public_pdfs)==len(allowed)==7
for pdf in public_pdfs:assert hashlib.sha256(pdf.read_bytes()).hexdigest()==allowed[str(pdf.relative_to(ROOT))]
home=(ROOT/'index.html').read_text()
assert home.index('id="therapy-matrices"')>home.index('id="hpb-roadmaps"')
assert 'href="systemic/"' in home and 'href="transplant/high-risk/"' in home
print(f'PASS: exact release baseline plus recorded clinical revisions; {len(review_links)} valid high-risk review destinations; 49 treatment summaries; {len(refs)} complete citations and TMC links; no PDAC transplant route, local paths or licensed PDFs published.')
