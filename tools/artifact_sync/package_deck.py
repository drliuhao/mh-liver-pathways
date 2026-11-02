"""Preserve original PPTX objects while packaging artifact-tool-authored edits.

Only text verified in the authoring receipt may change. Publication figures,
native charts/workbooks, table geometry, and unrelated ZIP parts are preserved.
"""
from pathlib import Path
from zipfile import ZipFile,ZIP_DEFLATED
from lxml import etree as E
import json,hashlib,difflib,sys,posixpath,copy
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1];WORK=ROOT.parent
BUILD=WORK/'Artifact_Sync_2026-11-02/.build'
P='http://schemas.openxmlformats.org/presentationml/2006/main'
A='http://schemas.openxmlformats.org/drawingml/2006/main'
R='http://schemas.openxmlformats.org/officeDocument/2006/relationships'
REL='http://schemas.openxmlformats.org/package/2006/relationships'
NS={'p':P,'a':A,'r':R};Q=lambda n:'{'+A+'}'+n
serialize=lambda x:E.tostring(x,encoding='UTF-8',xml_declaration=True,standalone=True)
read=lambda p:json.loads(Path(p).read_text())
sha=lambda b:hashlib.sha256(b).hexdigest()
def text_nodes(p):return [t for t in p.iter() if t.tag in (Q('t'),Q('br'))]
def value(t):return '\n' if t.tag==Q('br') else (t.text or '')
def text(p):return ''.join(value(t) for t in text_nodes(p))
def patch(p,old,new):
    assert text(p)==old,(text(p),old)
    ops=[o for o in difflib.SequenceMatcher(None,old,new,autojunk=False).get_opcodes() if o[0]!='equal']
    for _,a,b,c,d in reversed(ops):
        nodes=text_nodes(p);spans=[];pos=0
        if a==b:
            for t in nodes:
                n=len(value(t))
                if pos<=a<=pos+n and t.tag==Q('t'):
                    t.text=(t.text or '')[:a-pos]+new[c:d]+(t.text or '')[a-pos:];break
                pos+=n
            else:raise ValueError('No insertion node')
            continue
        for t in nodes:
            n=len(value(t))
            if pos<b and pos+n>a:spans.append((t,pos))
            pos+=n
        assert spans
        assert all(t.tag==Q('t') for t,_ in spans),'Changed content crosses a retained line break'
        first,i=spans[0];last,j=spans[-1];tail=(last.text or '')[b-j:]
        if first is last:first.text=(first.text or '')[:a-i]+new[c:d]+tail
        else:
            first.text=(first.text or '')[:a-i]+new[c:d]
            for t,_ in spans[1:-1]:t.text=''
            last.text=tail
    assert text(p)==new
def relpart(p):return posixpath.join(posixpath.dirname(p),'_rels',posixpath.basename(p)+'.rels')
def target(p,t):return posixpath.normpath(posixpath.join(posixpath.dirname(p),t)).lstrip('/')
def main():
    key=sys.argv[1];plan=next(d for d in read(HERE/'ppt_sync_plan.json') if d['key']==key)
    source=Path(plan['current_master']);assert sha(source.read_bytes())==plan['sha256']
    receipt=read(BUILD/'ppt_authored'/key/'authored_text.json');assert receipt['source_sha256']==plan['sha256']
    with ZipFile(source) as z:parts={n:z.read(n) for n in z.namelist()}
    originals=dict(parts);roots={};changed_shapes=set()
    for q in receipt['changes']:
        assert q['new']==q['verified_authored_text']
        root=roots.setdefault(q['part'],E.fromstring(parts[q['part']]))
        hit=root.xpath(q['xpath'],namespaces=NS);assert len(hit)==1,q
        p=hit[0];patch(p,q['old'],q['new'])
        if q.get('layout_adjustment'):
            shape=next(a for a in p.iterancestors() if a.tag=='{'+P+'}sp')
            ext=shape.find('p:spPr/a:xfrm/a:ext',NS);ext.set('cy',str(round(q['layout_adjustment']['height_px']*9525)))
            shape.find('p:txBody/a:bodyPr',NS).set('anchor','t')
        if '/slides/' in q['part'] and len(q['new'])>1.12*len(q['old']):
            tx=p.getparent();body=tx.find(Q('bodyPr'))
            if body is not None:
                for t in list(body):
                    if t.tag in (Q('noAutofit'),Q('normAutofit'),Q('spAutoFit')):body.remove(t)
                E.SubElement(body,Q('normAutofit'))
        changed_shapes.add((q['part'],q.get('shape_id')))
    for n,r in roots.items():parts[n]=serialize(r)
    # Authoritative current edition in package metadata, without altering
    # bibliographic dates or historical source-review labels on paper slides.
    if 'docProps/core.xml' in parts:
        r=E.fromstring(parts['docProps/core.xml'])
        ns={'dcterms':'http://purl.org/dc/terms/','dc':'http://purl.org/dc/elements/1.1/'}
        for t in r.findall('dcterms:modified',ns):t.text='2026-11-02T00:00:00Z'
        parts['docProps/core.xml']=serialize(r)
    for name,data in originals.items():
        if name not in roots and name!='docProps/core.xml':assert parts[name]==data,(key,name)
    # Add compact source cards authored separately through artifact-tool.
    added=[]
    if plan['additions']:
        cardfile=BUILD/'source_cards.pptx'
        with ZipFile(cardfile) as z:newparts={n:z.read(n) for n in z.namelist()}
        allcards=read(HERE/'source_card_additions.json')
        pres=E.fromstring(parts['ppt/presentation.xml']);rels=E.fromstring(parts['ppt/_rels/presentation.xml.rels']);ct=E.fromstring(parts['[Content_Types].xml'])
        cpres=E.fromstring(newparts['ppt/presentation.xml']);crels=E.fromstring(newparts['ppt/_rels/presentation.xml.rels'])
        cid={r.get('Id'):target('ppt/presentation.xml',r.get('Target')) for r in crels}
        cseq=[cid[s.get('{'+R+'}id')] for s in cpres.find('{'+P+'}sldIdLst')]
        imported={};masters=set();notesmasters=set();existing={x.get('PartName') for x in ct};defs={x.get('Extension') for x in ct}
        def imp(name):
            if name in imported:return imported[name]
            dest=posixpath.join(posixpath.dirname(name),'v18_add_'+posixpath.basename(name));imported[name]=dest;parts[dest]=newparts[name]
            for x in E.fromstring(newparts['[Content_Types].xml']):
                if x.tag.endswith('Override') and x.get('PartName')=='/'+name and '/'+dest not in existing:
                    n=copy.deepcopy(x);n.set('PartName','/'+dest);ct.append(n);existing.add('/'+dest)
                elif x.tag.endswith('Default') and x.get('Extension') not in defs:ct.append(copy.deepcopy(x));defs.add(x.get('Extension'))
            rp=relpart(name)
            if rp in newparts:
                rr=E.fromstring(newparts[rp])
                for x in rr:
                    if x.get('TargetMode')!='External':x.set('Target',posixpath.relpath(imp(target(name,x.get('Target'))),posixpath.dirname(dest)))
                parts[relpart(dest)]=serialize(rr)
            if posixpath.dirname(name)=='ppt/slideMasters':masters.add(dest)
            if posixpath.dirname(name)=='ppt/notesMasters':notesmasters.add(dest)
            return dest
        seq=pres.find('{'+P+'}sldIdLst');base=list(seq);high=max(int(x.get('id')) for x in base)
        for j,q in enumerate(plan['additions'],1):
            ci=next(i for i,c in enumerate(allcards) if c['proposal_id']==q['proposal_id']);dest=imp(cseq[ci]);rid='rIdV18Card'+str(j)
            E.SubElement(rels,'{'+REL+'}Relationship',Id=rid,Type=R+'/slide',Target=posixpath.relpath(dest,'ppt'))
            n=E.Element('{'+P+'}sldId',id=str(high+j),attrib={'{'+R+'}id':rid});anchor=base[q['insert_after_active_slide']-1];anchor.addnext(n)
            added.append({'id':q['proposal_id'],'part':dest,'after_source_slide':q['insert_after_active_slide'],'new_slide':q['insert_after_active_slide']+1})
        for listname,tag,typ,values in [('sldMasterIdLst','sldMasterId','slideMaster',masters),('notesMasterIdLst','notesMasterId','notesMaster',notesmasters)]:
            lst=pres.find('{'+P+'}'+listname)
            if lst is None:lst=E.Element('{'+P+'}'+listname);pres.insert(0,lst)
            high=max([int(x.get('id','0')) for x in lst]+[2147483647])
            for j,name in enumerate(sorted(values),1):
                rid='rIdV18'+typ+str(j);E.SubElement(rels,'{'+REL+'}Relationship',Id=rid,Type=R+'/'+typ,Target=posixpath.relpath(name,'ppt'))
                attrs={'{'+R+'}id':rid}
                if tag=='sldMasterId':attrs['id']=str(high+j)
                E.SubElement(lst,'{'+P+'}'+tag,attrib=attrs)
        parts['ppt/presentation.xml']=serialize(pres);parts['ppt/_rels/presentation.xml.rels']=serialize(rels);parts['[Content_Types].xml']=serialize(ct)
    out=BUILD/'ppt_candidates'/(key+'.pptx');out.parent.mkdir(exist_ok=True)
    with ZipFile(out,'w',ZIP_DEFLATED) as z:
        for n,d in parts.items():z.writestr(n,d)
    audit={'key':key,'candidate':str(out),'target':plan['target'],'source_sha256':plan['sha256'],'candidate_sha256':sha(out.read_bytes()),'changed_parts':list(roots),'original_parts_preserved':len(originals)-len(roots)-1,'edits':len(receipt['changes']),'source_cards':added,'slides':plan['active_slides']+len(added),'native_charts_preserved':plan['objects']['native_charts_on_active_slides'],'native_tables_preserved':plan['objects']['native_tables_on_active_slides'],'all_original_media_and_workbooks_byte_identical':True}
    (BUILD/'ppt_candidates'/(key+'.json')).write_text(json.dumps(audit,indent=2)+'\n');print(json.dumps(audit))
if __name__=='__main__':main()
