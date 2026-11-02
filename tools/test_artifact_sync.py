"""Prevent current website content from silently drifting from released artifacts."""
from pathlib import Path
import hashlib,json,zipfile
R=Path(__file__).resolve().parents[1]
d=json.loads((R/'tools/artifact_release_manifest.json').read_text())
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert len(d['word_documents'])==65 and len(d['presentations'])==34
for rel,expected in d['clinical_source_sha256'].items():
 assert sha(R/rel)==expected,f'{rel}: clinical source changed; reconcile current Word/PPT artifacts and renew the release manifest.'
assert {str(p.relative_to(R)) for p in (R/'documents').rglob('*.docx')}=={x['path'] for x in d['word_documents']}
for x in d['word_documents']:
 p=R/x['path'];assert sha(p)==x['sha256'],p
 with zipfile.ZipFile(p) as z:
  assert z.testzip() is None,p
  for n in z.namelist():
   if n.endswith(('.xml','.rels')):
    s=z.read(n).decode('utf-8');assert 'file:///' not in s and '/Users/haoliu/' not in s,(p,n)
local=R.parent/d['release']
if local.is_dir():
 for x in d['presentations']:assert sha(local/x['path'])==x['sha256'],x['path']
 for x in d['word_documents']:assert sha(local/x['local_master'])==x['local_sha256'],x['local_master']
catalog=json.loads((R/'evidence-libraries/catalog.json').read_text())
for x in d['presentations']:
 lib=next(v for v in catalog['libraries'] if v['key']==x['key'])
 assert lib['slides']==x['slides'] and lib['ppt_filename']=='Evidence_Summaries_v18.pptx'
assert d['counts']['slides']==4182 and d['counts']['native_charts']==109 and d['counts']['native_tables']==64
print('PASS: 65 current Word downloads, 34 PPT libraries, 4182 slides; source and artifact hashes aligned, private links absent, catalog slide counts exact.')
