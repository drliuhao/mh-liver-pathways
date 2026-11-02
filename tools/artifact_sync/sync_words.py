"""Apply approved, exact paragraph corrections to copied current Word masters.

This preserves fields, run formatting, relationships and all unrelated ZIP parts.
Generated question/discussion documents are built separately from current data.
"""
import base64, copy, difflib, hashlib, json, re, sys, zipfile
from collections import defaultdict
from pathlib import Path
from urllib.parse import unquote, urlsplit
from lxml import etree as E

ROOT = Path(__file__).resolve().parents[2]
WORK = ROOT.parent
OUT = WORK / 'V18_consistent_release_2026-11-02' / 'Documents'
HERE = Path(__file__).resolve().parent
NS = {'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
W = '{'+NS['w']+'}'
SPACE = '{http://www.w3.org/XML/1998/namespace}space'
REJECTED_PROPOSALS = {
    'LIVER-MAN-0039': 'Rejected during final source mapping QA: generic bibliography category heading above ABC-02/HIMALAYA/Hsu, not an Auer paper title. Preserve Systemic therapy.'
}
sys.path.insert(0,str(ROOT/'tools'))
import docx_text_fixes as FX

def visible(p): return ''.join(t.text or '' for t in p.iter(W+'t'))
def sha(b): return hashlib.sha256(b).hexdigest()
def serial(root): return E.tostring(root,encoding='UTF-8',xml_declaration=True,standalone=True)

def patch_paragraph(p, old, new, identity):
    assert visible(p)==old,(identity,visible(p),old)
    # Apply the changed spans from right to left, retaining unchanged citations
    # and formatting. A changed span must never overlap an EndNote/Word field.
    changes=[o for o in difflib.SequenceMatcher(None,old,new,autojunk=False).get_opcodes() if o[0]!='equal']
    for tag,a,b,c,d in reversed(changes):
        nodes=FX._texts(p); spans=[]; pos=0
        for t,field in nodes:
            n=len(t.text or '')
            if pos < b and pos+n > a: spans.append((t,field,pos))
            pos+=n
        if a==b:
            pos=0; target=None
            for t,field in nodes:
                n=len(t.text or '')
                if pos<=a<=pos+n and not field:
                    target=(t,pos); break
                pos+=n
            assert target,(identity,'no field-safe insertion location',a)
            t,pos=target;t.text=(t.text or '')[:a-pos]+new[c:d]+(t.text or '')[a-pos:]
            t.set(SPACE,'preserve');continue
        assert spans and not any(f for _,f,_ in spans),(identity,'changed text touches citation field',old[a:b])
        # A replacement crossing a style boundary retains the prefix/suffix in
        # their original runs and takes the first changed run's style.
        first,_,start=spans[0]; last,_,end=spans[-1]
        tail=(last.text or '')[b-end:]
        if first is last: first.text=(first.text or '')[:a-start]+new[c:d]+tail
        else:
            first.text=(first.text or '')[:a-start]+new[c:d]
            for t,_,_ in spans[1:-1]:t.text=''
            last.text=tail
        for t,_,_ in spans:t.set(SPACE,'preserve')
    assert visible(p)==new,(identity,'postcondition',visible(p),new)

def proposals():
    rows=[]
    liver=json.loads((HERE/'liver/exact_paragraph_proposals.json').read_text())
    liver=liver.get('proposals',liver) if isinstance(liver,dict) else liver
    manual_path=HERE/'liver/manual_paragraph_proposals.json'
    manual=json.loads(manual_path.read_text()) if manual_path.exists() else []
    manual=manual.get('proposals',manual) if isinstance(manual,dict) else manual
    for q in manual:
        if q.get('id') in REJECTED_PROPOSALS:
            assert q.get('kind')=='docx' and q.get('old')=='Systemic therapy' and q.get('new')=='Interventional therapy',q
    manual=[q for q in manual if q.get('id') not in REJECTED_PROPOSALS]
    superseded={q['supersedes'] for q in manual if q.get('supersedes')}
    rows += [q for q in liver if q.get('id') not in superseded]
    rows += manual
    rows += json.loads((HERE/'other/replacement_proposals.json').read_text())
    supplement=HERE/'other/supplemental_provenance_proposals.json'
    if supplement.exists():rows += json.loads(supplement.read_text())
    tp=json.loads((HERE/'transplant/transplant_exact_replacements.json').read_text())
    for q in tp['proposals']:
        for o in q['occurrences']:
            if o['artifact']!='word':continue
            rows.append({'kind':'docx','artifact':o['path'],'paragraph_index':o['paragraph_index'],
                'part':'word/document.xml','old':o['paragraph_text'],
                'new':o['paragraph_text'].replace(q['old'],q['new']),
                'id':q['id'],'source_locator':q['source_locator'],'fragment_old':q['old'],'fragment_new':q['new']})
    return [r for r in rows if r.get('kind')=='docx']

def insertion_proposals():
    rows=[]
    for n in ['other/insertion_proposals.json','liver/insertion_proposals.json']:
        f=HERE/n
        if f.exists():
            data=json.loads(f.read_text());data=data.get('proposals',[]) if isinstance(data,dict) else data
            for q in data:
                if q.get('kind','docx')!='docx':continue
                if q.get('anchor'):
                    q=dict(q, xpath=q['anchor']['xpath'],anchor_text=q['anchor']['text'],
                           insert_paragraphs=[q['new']],proposal_id=q.get('id'))
                rows.append(q)
    tp=json.loads((HERE/'transplant/transplant_exact_replacements.json').read_text())
    for q in tp.get('insertions',[]):
        for o in q['occurrences']:
            if o['artifact']!='word':continue
            rows.append({'kind':'docx','artifact':o['path'],
                'xpath':o['anchor_paragraph_xpath'],'anchor_text':o['anchor_text'],
                'insert_paragraphs':q['paragraphs'],'proposal_id':q['id'],
                'paragraph_roles':['Heading4']+['Normal']*(len(q['paragraphs'])-1),
                'source_locator':q['source_locator']})
    return rows

def inserted_paragraph(anchor,text,role=None):
    """Borrow document typography, without turning body insertions into headings."""
    p=E.Element(W+'p');pr=anchor.find(W+'pPr')
    if pr is not None:
        pr=copy.deepcopy(pr)
    else:pr=E.Element(W+'pPr')
    current=pr.find(W+'pStyle');style=current.get(W+'val','') if current is not None else ''
    # A provenance heading is an anchor, not a template for its new body prose.
    if role or style.lower().startswith(('heading','title')):
        if current is None:current=E.SubElement(pr,W+'pStyle')
        current.set(W+'val',role or 'Normal')
        for name in ['numPr','outlineLvl','pageBreakBefore','keepNext']:
            for el in list(pr.findall(W+name)):pr.remove(el)
        if role and role.lower().startswith('heading'):E.SubElement(pr,W+'keepNext')
    p.append(pr)
    r=E.SubElement(p,W+'r');t=E.SubElement(r,W+'t');t.text=text;t.set(SPACE,'preserve')
    return p

def sanitize(parts):
    doc=E.fromstring(parts['word/document.xml'])
    for f in doc.xpath('//w:fldData',namespaces=NS):
        try:r=E.fromstring(base64.b64decode(f.text))
        except Exception:continue
        changed=False
        for u in r.findall('.//urls/pdf-urls'):
            for l in list(u):
                if (l.text or '').startswith('file:'):u.remove(l);changed=True
        if changed:f.text=base64.b64encode(E.tostring(r)).decode()
    for t in doc.iter(W+'t'):
        if t.text=='Full text PDF':t.text='Full-text access'
    parts['word/document.xml']=serial(doc)
    for n,data in list(parts.items()):
        if not n.endswith('.rels'):continue
        root=E.fromstring(data);changed=False
        for rel in root:
            tg=rel.get('Target','')
            if tg.startswith('file:') or tg.startswith('/Users/'):
                name=Path(unquote(urlsplit(tg).path)).name;m=re.match(r'(\d{6,9})__',name)
                target=f'https://pubmed.ncbi.nlm.nih.gov/{m.group(1)}/' if m else 'https://drliuhao.github.io/mh-liver-pathways/evidence-libraries/'
                rel.set('Target',target);rel.set('TargetMode','External');changed=True
        if changed:parts[n]=serial(root)
    return parts

def writezip(path,parts):
    path.parent.mkdir(parents=True,exist_ok=True)
    # Publishing a verified package must not change its private hash solely due
    # to fresh ZIP timestamps, or invalidate its completed render evidence.
    if path.exists():
        with zipfile.ZipFile(path) as old:
            if set(old.namelist())==set(parts) and all(old.read(k)==v for k,v in parts.items()):return
    temp=path.with_name(path.name+'.tmp')
    with zipfile.ZipFile(temp,'w',zipfile.ZIP_DEFLATED) as z:
        for k,v in parts.items():z.writestr(k,v)
    temp.replace(path)

def main():
    inventory=json.loads((HERE/'current_artifact_inventory.json').read_text())
    grouped=defaultdict(list)
    for q in proposals():grouped[q['artifact']].append(q)
    inserts=defaultdict(list)
    for q in insertion_proposals():inserts[q['artifact']].append(q)
    log=[];publish='--publish' in sys.argv
    for item in inventory['documents']:
        src=Path(item['source_master']); dest=OUT/src.parent.name/src.name.replace('_v17','_v18')
        if item['role'].endswith('_info'):
            raw=src.read_bytes();assert sha(raw)==item['source_sha256'],src
            with zipfile.ZipFile(src) as z:parts={n:z.read(n) for n in z.namelist()}
            oldparts=dict(parts);root=E.fromstring(parts['word/document.xml']);paras=list(root.iter(W+'p'))
            bypara=defaultdict(list)
            for q in grouped.get(str(src),[]):
                if q.get('xpath'):
                    matches=root.xpath(q['xpath'],namespaces=NS);assert len(matches)==1,q
                    p=matches[0]
                else:
                    # Transplant inventory uses zero-based paragraph indexes.
                    p=paras[q['paragraph_index']]
                assert visible(p)==q['old'],(src,q.get('id'),q.get('paragraph_index'),visible(p)[:100],q['old'][:100])
                bypara[p].append(q)
            anchors=[]
            for q in inserts.get(str(src),[]):
                hit=root.xpath(q['xpath'],namespaces=NS);assert len(hit)==1,q
                assert visible(hit[0])==q['anchor_text'],(src,'original insertion anchor')
                anchors.append((q,hit[0]))
            changed=[];removed=[]
            for p,qs in bypara.items():
                old=visible(p);new=old
                for q in qs:
                    if new==old:new=q['new']
                    elif q['new']==new:pass
                    elif q.get('fragment_old') and q['fragment_old'] in new:new=new.replace(q['fragment_old'],q['fragment_new'])
                    else:raise ValueError(('Conflicting paragraph proposals',src,qs))
                patch_paragraph(p,old,new,str(src))
                if not new and not list(p.iter(W+'fldChar')) and p.getparent().tag==W+'body':removed.append(p)
                changed.append({'old':old,'new':new,'sources':[q.get('proposal_id',q.get('id')) for q in qs]})
            for q,p in anchors:
                # Some anchors also have an approved text replacement.
                assert visible(p) in (q['anchor_text'],next((x['new'] for x in grouped[str(src)] if x['old']==q['anchor_text']),q['anchor_text'])),(src,'insertion anchor changed')
                previous=p
                for i,text in enumerate(q['insert_paragraphs']):
                    roles=q.get('paragraph_roles',[])
                    n=inserted_paragraph(p,text,roles[i] if i<len(roles) else None)
                    previous.addnext(n);previous=n
                changed.append({'insertion_after':q['anchor_text'],'new':q['insert_paragraphs'],'sources':[q.get('proposal_id')]})
            # Keep an emptied insertion anchor attached until all insertions
            # have been placed, then remove only that now-empty body paragraph.
            for p in removed:p.getparent().remove(p)
            # Replace the edition companion note, preserving the original source
            # version/date in historical headers and bibliographic references.
            note='V18 synchronized edition · 1 November 2026. Clinical recommendations and key results incorporate the accepted A/B/C review corrections used in the current website. Companion questions and discussion documents use the same decision data. Draft pending institutional approval.'
            found=0
            for p in root.iter(W+'p'):
                text=visible(p)
                if text.startswith('V17 ') or text.startswith('V17:'):
                    patch_paragraph(p,text,note,str(src));found+=1
            if not found:
                body=root.find(W+'body');p=E.Element(W+'p');r=E.SubElement(p,W+'r');pr=E.SubElement(r,W+'rPr');E.SubElement(pr,W+'i');sz=E.SubElement(pr,W+'sz');sz.set(W+'val','18');E.SubElement(r,W+'t').text=note
                body.insert(2,p)
            parts['word/document.xml']=serial(root)
            # All citation instructions/data and embedded media remain identical.
            oldroot=E.fromstring(oldparts['word/document.xml'])
            for tag in ['instrText','fldData','fldChar','drawing']:
                assert [E.tostring(x) for x in oldroot.iter(W+tag)]==[E.tostring(x) for x in root.iter(W+tag)],(src,tag)
            unchanged=[n for n in oldparts if n!='word/document.xml']
            assert all(parts[n]==oldparts[n] for n in unchanged),(src,'unrelated package parts changed')
            writezip(dest,parts)
            if publish:writezip(Path(item['published_path']),sanitize(dict(parts)))
            log.append({'source':str(src),'source_sha256':item['source_sha256'],
                'output':str(dest),'sha256':sha(dest.read_bytes()),'changes':changed,
                'preserved_package_parts':len(unchanged),'citation_and_drawing_xml_preserved':True,
                'published_path':item['published_path'] if publish else None,
                'published_sha256':sha(Path(item['published_path']).read_bytes()) if publish else None,
                'status':'synchronized'})
        else:
            assert dest.exists(),dest
            if publish:
                with zipfile.ZipFile(dest) as z:parts={n:z.read(n) for n in z.namelist()}
                writezip(Path(item['published_path']),sanitize(parts))
            log.append({'source':str(src),'output':str(dest),'sha256':sha(dest.read_bytes()),
                'published_path':item['published_path'] if publish else None,
                'published_sha256':sha(Path(item['published_path']).read_bytes()) if publish else None,
                'status':'regenerated from current decision data'})
    (HERE/'word_sync_manifest.json').write_text(json.dumps(log,indent=2)+'\n')
    (HERE/'word_sync_dispositions.json').write_text(json.dumps({
        'rejected_proposals':REJECTED_PROPOSALS,
        'proposal_inputs':{str(p.relative_to(HERE)):sha(p.read_bytes()) for p in [
            HERE/'liver/exact_paragraph_proposals.json',HERE/'liver/manual_paragraph_proposals.json',
            HERE/'liver/insertion_proposals.json',HERE/'other/replacement_proposals.json',
            HERE/'other/insertion_proposals.json',HERE/'other/supplemental_provenance_proposals.json',
            HERE/'transplant/transplant_exact_replacements.json'] if p.exists()},
        'documents':len(log),'full_content':sum(x['status']=='synchronized' for x in log),
        'changed_paragraph_and_insertion_records':sum(len(x.get('changes',[])) for x in log),
        'published_to_canonical_files':publish,
    },indent=2)+'\n')
    print(json.dumps({'documents':len(log),'full_content':sum(x['status']=='synchronized' for x in log),'changed_paragraphs':sum(len(x.get('changes',[])) for x in log),'published':publish}))

if __name__=='__main__':main()
