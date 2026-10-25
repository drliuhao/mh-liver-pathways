"""Check evidence identifiers, public-file boundaries and clinical review destinations."""
import json,re,subprocess,hashlib
from pathlib import Path
from urllib.parse import urlsplit,unquote

ROOT=Path(__file__).resolve().parents[1]
data=json.loads((ROOT/'transplant/assets/content.json').read_text())
base=json.loads(subprocess.check_output(['git','show','f77348e:transplant/assets/content.json'],cwd=ROOT))
for old,new in zip(base['index'],data['index']):
 assert old['slug']==new['slug']
 for k in old:
  if k not in ['docs','protocol','issues','steps']:assert old[k]==new[k],(old['slug'],k)
 assert new['issues'][:len(old['issues'])]==old['issues'],'An earlier decision was changed'
 additions=new['issues'][len(old['issues']):]
 assert len(additions)==(6 if old['slug']=='hcc' else 0)
 assert all(x['record'].startswith('HCC B1.1') and x['status']=='OPEN — not approved' for x in additions)
 assert len(old['steps'])==len(new['steps'])
 for a,b in zip(old['steps'],new['steps']):
  assert {k:v for k,v in a.items() if k!='issues'}=={k:v for k,v in b.items() if k!='issues'},'Standard clinical criteria changed'
  assert b['issues'][:len(a['issues'])]==a['issues']
  assert set(b['issues'][len(a['issues']):]).issubset({x['id'] for x in additions})
assert data['assistants']==base['assistants'], 'Standard matching rules changed'
assert all(data['sources'][k]==v for k,v in base['sources'].items()), 'An inherited source changed'
new_sources=set(data['sources'])-set(base['sources'])
assert len(new_sources)==14 and all(k.startswith('V12-') for k in new_sources)

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
print(f'PASS: unchanged standard criteria/rules; six OPEN AFP meeting questions; {len(review_links)} valid high-risk review destinations; 49 treatment summaries; {len(refs)} complete citations and TMC links; no PDAC transplant route, local paths or licensed PDFs published.')
