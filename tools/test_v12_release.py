"""V12 links, embedded payloads, citation packages and private/public boundaries."""
from pathlib import Path
from urllib.parse import urlsplit,unquote,urljoin
from html.parser import HTMLParser
from zipfile import ZipFile
from xml.etree import ElementTree as E
import re,json,base64

ROOT=Path(__file__).resolve().parents[1]
BASE='/mh-liver-pathways/'
content=json.loads((ROOT/'transplant/assets/content.json').read_text())
reviews=json.loads((ROOT/'evidence/2026-10-25/review.json').read_text())
assert len(reviews)==14
assert sum(x['pages'] for x in reviews.values())==199
class Links(HTMLParser):
 def __init__(self):super().__init__();self.urls=[]
 def handle_starttag(self,tag,attrs):
  for name,value in attrs:
   if name in ['href','src'] and value:self.urls.append(value)

pages=[ROOT/p/'index.html' for p in ['hcc','hilar','icca','crlm','pdac','chcca','systemic','evidence/2026-10-25','transplant/meeting-records/hcc-b1-1']]
pages+=list((ROOT/'transplant').rglob('*.html'))
checked=0;embedded=0
for file in pages:
 text=file.read_text();parser=Links();parser.feed(text)
 for link in parser.urls:
  parsed=urlsplit(link)
  if parsed.scheme or parsed.netloc or not parsed.path:continue
  url=urlsplit(urljoin('https://drliuhao.github.io'+BASE+str(file.relative_to(ROOT)),link))
  assert url.path.startswith(BASE),(file,link)
  target=ROOT/unquote(url.path[len(BASE):])
  if target.is_dir():target=target/'index.html'
  assert target.is_file(),(file,link,target)
  checked+=1
 match=re.search(r'<script[^>]*id="protocol-data"[^>]*>(.*?)</script>',text,re.S)
 if match:
  data=json.loads(match.group(1));slug=(data.get('pathway') or {}).get('slug')
  if slug in ['hcc','pcca','icca','crlm',None]:
   assert data['high_risk']==content['high_risk'],file
   assert data['sources']==content['sources'],file
   assert data['assistants']==content['assistants'],file
   if slug:assert data['pathway']==next(x for x in content['index'] if x['slug']==slug)
   embedded+=1

documents=list((ROOT/'evidence/2026-10-25/docs').glob('*.docx'))
assert len(documents)==17
ns={'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
for path in documents:
 with ZipFile(path) as z:
  assert z.testzip() is None
  for name in z.namelist():
   if name.endswith(('.xml','.rels')):
    raw=z.read(name);E.fromstring(raw)
    assert b'/Users/' not in raw and b'file://' not in raw,(path,name)
  tree=E.fromstring(z.read('word/document.xml'))
  depth=0
  for f in tree.findall('.//w:fldChar',ns):
   kind=f.get('{'+ns['w']+'}fldCharType');depth+=1 if kind=='begin' else -1 if kind=='end' else 0
   assert depth>=0,path
  assert depth==0,path
  for data in tree.findall('.//w:fldData',ns):
   raw=base64.b64decode(data.text);E.fromstring(raw)
   assert b'/Users/' not in raw and b'file://' not in raw,path
assert not list((ROOT/'evidence/2026-10-25').rglob('*.pdf'))
for path in [ROOT/'evidence/2026-10-25/review.json',ROOT/'tools/v12_content_snapshot.json']:
 assert '/Users/' not in path.read_text() and 'file://' not in path.read_text(),path
for k in reviews:
 assert 'V12-'+k in content['sources']
 assert content['high_risk']['sources'][k]['pmid'],k
 assert content['high_risk']['sources'][k]['doi']==reviews[k]['doi'],k
print(f'PASS: {checked} static internal links; {embedded} synchronized embedded payloads; 17 valid public DOCX citation packages; 14/14 sources; no licensed PDFs or private file paths in new publication.')
