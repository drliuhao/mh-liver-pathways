"""Keep the matrix's displayed rows, source tags and source module synchronized."""
import json, re
from pathlib import Path
from lxml import html, etree
ROOT=Path(__file__).resolve().parents[2]
path=ROOT/'systemic/index.html'
page=html.fromstring(path.read_text())
data=json.loads((ROOT/'systemic/matrix.json').read_text())
refs=json.loads((ROOT/'systemic/references.json').read_text())
rows=json.loads((ROOT/'tools/systemic_evidence_rows.json').read_text())
rev=json.loads((ROOT/'tools/clinical_revisions/2026-11-02-matrices.json').read_text())
before=json.loads(next(e['old'] for e in rev['files'] if e['file']=='systemic/matrix.json'))
prior={c['id']:c for c in before['cards']}
explicit={
 'hcc-tki':[['29433850'],['18650514']],
 'crlm-other-targets':[['41526345'],['37870968'],['38587856']],
 'crlm-refractory':[['37133585'],['37331369'],['23177514']],
}

def paragraph(node,label,text):
    node.clear(keep_tail=True)
    b=etree.SubElement(node,'strong');b.text=label;b.tail=' '+text

for c in data['cards']:
    cid=c['id'];node=page.get_element_by_id(cid)
    node.set('data-setting',c['setting'])
    node.xpath('.//*[@class="st-title"]')[0].text=c['title']
    node.xpath('.//*[contains(@class,"st-position")]')[0].text=c['position']
    for field,cls,label in [('who','st-when','When to consider.'),('limits','limits','Limits of the evidence.'),('transplant','st-transplant','Transplant implications.')]:
        n=node.xpath('.//p[@class=$cls]',cls=cls)[0]
        # Do not clear the identifying class along with its old content.
        paragraph(n,label,c[field]);n.set('class',cls)
    if c['evidence']!=prior[cid]['evidence']:
        if cid in explicit:
            parts=re.split(r' (?=(?:REFLECT:|SHARP:|MOUNTAINEER final:|CodeBreaK 300,|KRYSTAL-1:|SUNLIGHT:|FRESCO-2:|CORRECT:))',c['evidence'])
            assert len(parts)==len(explicit[cid]),cid
            rows[cid]=[{'text':t,'refs':p} for t,p in zip(parts,explicit[cid])]
        elif cid=='hcc-adjuvant': rows[cid]=[{'text':c['evidence'],'refs':['37871608','41580093']}]
        elif cid=='crlm-conversion':
            a,b=c['evidence'].split(' TRICE studied',1)
            rows[cid]=[{'text':a,'refs':['37329889']},{'text':'TRICE studied'+b,'refs':['38728364']}]
        elif cid=='crlm-msi':
            a,b=c['evidence'].split(' CheckMate 8HW:',1)
            rows[cid]=[{'text':a,'refs':['33264544']},{'text':'CheckMate 8HW:'+b,'refs':['39602630','39874977']}]
        else: rows[cid]=[{'text':c['evidence'],'refs':c['refs']}]
        ul=node.xpath('.//div[contains(@class,"st-evidence")]/ul')[0]
        ul.clear();ul.set('class','ev')
        for seg in rows[cid]:
            li=etree.SubElement(ul,'li',{'class':'st-ev-row'});keys=etree.SubElement(li,'span',{'class':'st-ev-keys'})
            for pm in seg['refs']:
                etree.SubElement(keys,'a',{'class':'pm','href':f'#sources-{cid}-{pm}','data-pmid':pm,'aria-label':f'{refs[pm]["trial"]} · PMID {pm} — full citation'})
            etree.SubElement(li,'span',{'class':'st-ev-text'}).text=seg['text'];li.tail=' '
    if c['setting']!=prior[cid]['setting']:
        target=page.xpath('//section[@data-setting-group=$s]//div[contains(@class,"regimen-grid")]',s=c['setting'])[0]
        target.append(node)
        for a in page.xpath('//div[@class="matrix-option"]/a[@href=$h]',h='#'+cid):
            option=a.getparent()
            # The comparison is a tumor row with setting cells.
            row=option.xpath('ancestor::tr')[0]
            dest=row.xpath('.//td[@data-setting=$s]',s=c['setting'])
            if dest: dest[0].append(option)

# Safety text keeps its own source links.
for n,s in zip(page.xpath('//details[@class="safety-disclosure"]'),data['safety']):
    divs=n.xpath('./div[@class="context-body"]/div')
    divs[0].text=s[1]
    divs[1].text=s[2]

# A paper belongs to every card that cites it; preserve additional existing tags.
for pm,r in refs.items():
    relevant={t for c in data['cards'] if pm in c['refs'] for t in c['tumors']}
    r['diseases']=sorted(set('pcca' if t=='hilar' else t for t in r.get('diseases',[]))|relevant)
    if pm=='41781152':r['trial']='Hong 2026 review'
    if pm=='39908431':r['trial']='eNRGy'
    if pm=='41275879':r['year']=2025
    for node in page.xpath('//article[@class="library-entry"]'):
        if node.xpath('.//a[contains(@href,$pm)]',pm='pubmed.ncbi.nlm.nih.gov/'+pm+'/'):
            node.set('data-tumors',' '.join(r['diseases']))
    for li in page.xpath('//*[@id]'):
        if li.get('id','').endswith('-'+pm) and li.tag=='li':
            strong=li.find('strong')
            if strong is not None:strong.text=r['trial']

old_refs=(ROOT/'systemic/references.json').read_text()
new_refs=json.dumps(refs,ensure_ascii=False,indent=2)+'\n'
(ROOT/'systemic/references.json').write_text(new_refs)
manifest_path=ROOT/'systemic/publication-manifest.json'
old_manifest=manifest_path.read_text();manifest=json.loads(old_manifest)
available=sum(r.get('pdf_status')!='Full PDF still needed' for r in refs.values())
manifest.update(review_date='2026-11-02',local_pdfs=available,missing_pdfs=len(refs)-available)
new_manifest=json.dumps(manifest,ensure_ascii=False,indent=2)+'\n';manifest_path.write_text(new_manifest)
for p in page.xpath('//*[@id="library"]/p'):
    if 'indexed papers' in p.text_content():
        p.text=f'{len(refs)} indexed papers · {available} marked available in the reference depot · {len(refs)-available} still needed. Availability is separate from the depth of appraisal.'
(ROOT/'tools/systemic_evidence_rows.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2)+'\n')
(ROOT/'tools/systemic_source/matrix_content.py').write_text('# Canonical systemic content synchronized after the reconciled audit.\n'+ '\n'.join(k+' = '+repr(data[v]) for k,v in [('CARDS','cards'),('SAFETY','safety'),('GUIDELINES','guidelines')])+'\n')
page.get_element_by_id('options') # preserve mount points
path.write_text('<!doctype html>\n'+html.tostring(page,encoding='unicode',method='html')+'\n')
for name,old,new in [('systemic/references.json',old_refs,new_refs),('systemic/publication-manifest.json',old_manifest,new_manifest)]:
    if old!=new: rev['files'].append(dict(file=name,old=old,new=new,why='B10 metadata/reference filter and count correction; actual card citation ownership'))
(ROOT/'tools/clinical_revisions/2026-11-02-matrices.json').write_text(json.dumps(rev,ensure_ascii=False,indent=2)+'\n')
print('Systemic content, display, study rows and tumor-specific reference tags synchronized.')
