"""All-file structural and rendered-page checks; visual review is recorded separately."""
import base64
import copy
from collections import Counter
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys
import zipfile
from lxml import etree as E
from PIL import Image
from pypdf import PdfReader
import sync_words as SYNC

HERE=Path(__file__).resolve().parent
WEB=HERE.parents[1]
WORK=WEB.parent
BUILD=WORK/'Artifact_Sync_2026-11-02/.build'
OUT=BUILD/'word_qa'
OUT.mkdir(parents=True,exist_ok=True)
TXT=Path('/Users/haoliu/.cache/codex-runtimes/codex-primary-runtime/dependencies/native/poppler/poppler/bin/pdftotext')
NS={'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
W='{'+NS['w']+'}'
X='{http://www.w3.org/1999/xhtml}'
sha=lambda b:hashlib.sha256(b).hexdigest()
visible=lambda p:''.join(t.text or '' for t in p.iter(W+'t'))
norm=lambda s:re.sub(r'\s+',' ',s).strip()
manifest=json.loads((HERE/'word_sync_manifest.json').read_text())
inventory=json.loads((HERE/'current_artifact_inventory.json').read_text())
meta={d['source_master']:d for d in inventory['documents']}
renders={}
for folder in ['word_renders','word_full_renders']:
    f=BUILD/folder/'render_status.json'
    if f.exists():renders.update({x['file']:x for x in json.loads(f.read_text())})
public='--public' in sys.argv

def package(path):
    with zipfile.ZipFile(path) as z:return {n:z.read(n) for n in z.namelist()}

def job(item):
    path=Path(item['output']);source=Path(item['source']);detail={'file':str(path),'status':item['status'],'errors':[],'warnings':[]}
    parts=package(path);root=E.fromstring(parts['word/document.xml'])
    full=item['status']=='synchronized'
    text='\n'.join(visible(p) for p in root.iter(W+'p'))
    if sha(path.read_bytes())!=item['sha256']:detail['errors'].append('Output hash differs from synchronization manifest')
    if full:
        base=package(source);oldroot=E.fromstring(base['word/document.xml'])
        detail['source_hash_unchanged']=sha(source.read_bytes())==meta[str(source)]['source_sha256']
        if not detail['source_hash_unchanged']:detail['errors'].append('Archived source changed')
        detail['unrelated_package_parts_identical']=all(parts.get(k)==v for k,v in base.items() if k!='word/document.xml')
        if not detail['unrelated_package_parts_identical']:detail['errors'].append('Unrelated package parts differ')
        detail['preserved_fields_and_drawings']={}
        for tag in ['instrText','fldData','fldChar','drawing','pict']:
            a=[E.tostring(x) for x in oldroot.iter(W+tag)];b=[E.tostring(x) for x in root.iter(W+tag)]
            detail['preserved_fields_and_drawings'][tag]={'count':len(a),'identical':a==b}
            if a!=b:detail['errors'].append(tag+' changed')
        for change in item.get('changes',[]):
            strings=change['new'] if isinstance(change['new'],list) else [change['new']]
            for s in strings:
                if s and s not in text:detail['errors'].append('Applied text missing: '+s[:120])
    detail['paragraphs']=len(list(root.iter(W+'p')))
    detail['tables']=len(list(root.iter(W+'tbl')))
    detail['drawings']=len(list(root.iter(W+'drawing')))
    detail['field_instruction_types']=dict(Counter((x.text or '').strip().split(' ')[0] for x in root.iter(W+'instrText')))
    if public:
        target=Path(meta[str(source)]['published_path']);pub=package(target);pr=E.fromstring(pub['word/document.xml'])
        detail['published_path']=str(target);detail['published_sha256']=sha(target.read_bytes())
        if detail['published_sha256']!=item.get('published_sha256'):detail['errors'].append('Published hash differs from manifest')
        expected=SYNC.sanitize(dict(parts))
        detail['public_package_equals_documented_sanitization']=set(pub)==set(expected) and all(pub.get(k)==v for k,v in expected.items())
        if not detail['public_package_equals_documented_sanitization']:detail['errors'].append('Public package differs from documented sanitization')
        for tag in ['instrText','drawing','pict']:
            if [E.tostring(x) for x in root.iter(W+tag)]!=[E.tostring(x) for x in pr.iter(W+tag)]:detail['errors'].append('Public '+tag+' changed')
        def field_structure(node):
            c=copy.deepcopy(node)
            # fldData sits inside the begin fldChar. Its private PDF URL is
            # deliberately scrubbed; compare the remaining field structure and
            # separately require the entire public package to equal sanitization.
            for f in c.iter(W+'fldData'):f.text=''
            return E.tostring(c)
        if [field_structure(x) for x in root.iter(W+'fldChar')]!=[field_structure(x) for x in pr.iter(W+'fldChar')]:detail['errors'].append('Public field structure changed')
        leaks=[]
        for n,b in pub.items():
            if n.endswith('.rels'):
                for rel in E.fromstring(b):
                    t=rel.get('Target','')
                    if t.startswith(('file:','/Users/')):leaks.append({'part':n,'target':t})
        for f in pr.iter(W+'fldData'):
            try:b=base64.b64decode(f.text or '')
            except Exception:continue
            if b'file://' in b or b'/Users/' in b:leaks.append({'part':'word/document.xml','target':'private citation payload'})
        detail['public_private_link_leaks']=leaks
        if leaks:detail['errors'].append('Private file paths remain in public package')
    rd=renders.get(str(path));detail['render']=rd
    if not rd or rd.get('returncode')!=0:
        detail['errors'].append('No successful render');return detail
    folder=Path(rd['folder']);pdf=folder/(path.stem+'.pdf')
    if not pdf.exists():detail['errors'].append('PDF absent');return detail
    if full and rd.get('sha256')!=item['sha256']:detail['errors'].append('Rendered source hash is stale')
    if not full:
        detail['existing_render_after_source_mtime']=pdf.stat().st_mtime>=path.stat().st_mtime
        if not detail['existing_render_after_source_mtime']:detail['errors'].append('Generated document is newer than existing render')
    count=len(PdfReader(pdf).pages)
    pages=sorted(folder.glob('page-*.png'),key=lambda p:int(p.stem.split('-')[-1]))
    detail['pages']=count;detail['png_pages']=len(pages)
    if len(pages)!=count or rd.get('pages')!=count:detail['errors'].append('Page count mismatch')
    dims=Counter()
    for png in pages:
        try:
            with Image.open(png) as im:dims[str(im.size)]+=1;im.verify()
        except Exception as ex:detail['errors'].append(str(png)+': '+str(ex))
    detail['png_dimensions']=dict(dims)
    bbox=subprocess.run([str(TXT),'-bbox-layout',str(pdf),'-'],capture_output=True,check=True).stdout
    bboxroot=E.fromstring(bbox,E.XMLParser(no_network=True,resolve_entities=False))
    oob=[];empty=[];unknown=[];page_text=[]
    for i,p in enumerate(bboxroot.findall('.//'+X+'page'),1):
        width=float(p.get('width'));height=float(p.get('height'));words=p.findall('.//'+X+'word')
        page_text.append(' '.join(''.join(x.itertext()) for x in words))
        if not words:empty.append(i)
        for x in words:
            t=''.join(x.itertext());b=[float(x.get(k)) for k in ['xMin','yMin','xMax','yMax']]
            if b[0]<-1 or b[1]<-1 or b[2]>width+1 or b[3]>height+1:oob.append({'page':i,'text':t,'bbox':b,'page_size':[width,height]})
            if '\ufffd' in t:unknown.append({'page':i,'text':t})
    detail['out_of_page_words']=oob;detail['empty_text_pages']=empty;detail['replacement_glyph_words']=unknown
    if oob:detail['warnings'].append('Text bounding boxes extend outside physical page')
    if empty:detail['warnings'].append('Pages with no extracted text require inspection')
    if unknown:detail['warnings'].append('Replacement glyphs require inspection')
    matches=[]
    for ch in item.get('changes',[]):
        strings=ch['new'] if isinstance(ch['new'],list) else [ch['new']]
        for s in strings:
            key=norm(s)[:100]
            if len(key)<20:continue
            hits=[i+1 for i,t in enumerate(page_text) if key in norm(t)]
            matches.append({'sources':ch['sources'],'excerpt':key,'pages':hits})
    detail['changed_text_page_matches']=matches
    detail['changed_pages']=sorted({n for x in matches for n in x['pages']})
    detail['render_text_file']=str(OUT/(path.stem+'.txt'))
    (OUT/(path.stem+'.txt')).write_text('\f'.join(page_text))
    return detail

results=[]
with ThreadPoolExecutor(max_workers=3) as pool:
    futures={pool.submit(job,x):x for x in manifest}
    for f in as_completed(futures):
        try:r=f.result()
        except Exception as ex:r={'file':futures[f]['output'],'errors':[repr(ex)],'warnings':[]}
        results.append(r)
        print(f'{len(results)}/{len(manifest)} {Path(r["file"]).name}: {r.get("pages",0)} pages; {len(r["errors"])} errors; {len(r["warnings"])} flags',flush=True)
summary={'documents':len(results),'full_content':sum(r.get('status')=='synchronized' for r in results),
         'pages':sum(r.get('pages',0) for r in results),'errors':sum(len(r['errors']) for r in results),
         'documents_with_warnings':sum(bool(r['warnings']) for r in results),'published_checked':public,
         'visual_review':'Separate sampled page-image review; automatic page geometry checks do not establish exhaustive visual cleanliness.'}
report={'generated_utc':datetime.now(timezone.utc).isoformat(),'summary':summary,'documents':sorted(results,key=lambda x:x['file'])}
name='word_qa_public.json' if public else 'word_qa_private.json'
(HERE/name).write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(summary))
sys.exit(bool(summary['errors']))
