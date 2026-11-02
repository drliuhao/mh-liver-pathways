"""Read current evidence libraries and locate accepted matrix/source corrections."""
from pathlib import Path
import importlib.util, json, zipfile, posixpath, xml.etree.ElementTree as ET, collections
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
spec=importlib.util.spec_from_file_location('prep',HERE/'other/prepare.py')
P=importlib.util.module_from_spec(spec);spec.loader.exec_module(P)
OUT=HERE/'shared';OUT.mkdir(exist_ok=True)
inventory=json.loads((HERE/'current_artifact_inventory.json').read_text())
records=[]
for d in inventory['decks']:
    f=Path(d['current_master']);base={'kind':'pptx','artifact':str(f),'artifact_sha256':d['sha256'],'library':d['key'],'disease':'shared'}
    with zipfile.ZipFile(f) as z:
        pres=ET.fromstring(z.read('ppt/presentation.xml'))
        rels={x.get('Id'):x.get('Target') for x in ET.fromstring(z.read('ppt/_rels/presentation.xml.rels'))}
        for i,el in enumerate(pres.findall('p:sldIdLst/p:sldId',P.NS),1):
            part=posixpath.normpath(posixpath.join('ppt',rels[el.get('{'+P.NS['r']+'}id')]))
            records.extend(P.paragraphs(z,part,'pptx',base,i))
            rp=posixpath.join(posixpath.dirname(part),'_rels',posixpath.basename(part)+'.rels')
            if rp not in z.namelist():continue
            for rel in ET.fromstring(z.read(rp)):
                if rel.get('Type','').endswith('/notesSlide'):
                    np=posixpath.normpath(posixpath.join(posixpath.dirname(part),rel.get('Target'))).lstrip('/')
                    records.extend(P.paragraphs(z,np,'pptx',base,i))
(OUT/'all_ppt_paragraphs.json').write_text(json.dumps(records,ensure_ascii=False,indent=2))
rows=json.loads((ROOT/'tools/audit_revision/matrix_change_register.json').read_text())
if isinstance(rows,dict):rows=rows['changes']
changes=[]
for i,x in enumerate(rows):
    if not isinstance(x.get('old'),str) or not isinstance(x.get('new'),str):continue
    a,b=P.plain(x['old']),P.plain(x['new'])
    if len(a)<35 or a==b:continue
    changes.append(dict(disease='shared',old_text=a,new_text=b,change_id=f'MATRIX-{i+1}',finding_ids=[x.get('batch','matrix')],source_locators=[x.get('source_locator','')],web_locations=[x['file']+str(x.get('path',''))]))
P.OUT=OUT
proposals,coverage=P.match(records,changes)
print(json.dumps({'all_active_paragraphs':len(records),'shared_matrix_proposals':len(proposals),'slides':len({(x['artifact'],x['slide']) for x in proposals})}))
