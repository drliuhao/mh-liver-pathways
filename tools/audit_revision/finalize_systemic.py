import json
from pathlib import Path
from lxml import html,etree
R=Path(__file__).resolve().parents[2]
f=R/'systemic/matrix.json';old=f.read_text();d=json.loads(old)
c=next(c for c in d['cards'] if c['id']=='crlm-conversion')
c['links']=[['CAIRO5 overall-survival analysis · PMID 39570583','https://pubmed.ncbi.nlm.nih.gov/39570583/'],['CAIRO5 survival paper · TMC Library','https://libkey.io/libraries/480/pmid/39570583']]
new=json.dumps(d,ensure_ascii=False,indent=2)+'\n';f.write_text(new)
m=R/'tools/clinical_revisions/2026-11-02-zzzz-evidence.json';rev=json.loads(m.read_text());rev['files'].append(dict(file='systemic/matrix.json',old=old,new=new));m.write_text(json.dumps(rev,ensure_ascii=False,indent=2)+'\n')
p=R/'systemic/index.html';doc=html.fromstring(p.read_text());n=doc.get_element_by_id('sources-crlm-conversion')
for i,(label,url) in enumerate(c['links']):
 par=etree.SubElement(n,'p');etree.SubElement(par,'a',href=url,target='_blank',rel='noopener',id='sources-crlm-conversion-link'+str(i)).text=label
n.find('summary').text='Trials and supporting sources (4)'
doc.xpath('//*[@aria-controls="sources-crlm-conversion"]')[0].set('data-count','4')
refs=json.loads((R/'systemic/references.json').read_text())
for pm in ['39908431','41781152','41275879']:
 for q in doc.xpath('//article[@class="library-entry"]'):
  if q.xpath('.//a[contains(@href,$p)]',p='pubmed.ncbi.nlm.nih.gov/'+pm+'/'):
   for strong in q.xpath('.//p/strong'):strong.text=refs[pm]['trial']
 for q in doc.xpath('//*[self::li or self::p]'):
  if q.xpath('./span[@class="source-access"]//a[contains(@href,$p)]',p='pubmed.ncbi.nlm.nih.gov/'+pm+'/'):
   strong=q.find('strong')
   if strong is not None:
    strong.text=refs[pm]['trial']
    if pm=='41275879':strong.tail=(strong.tail or '').replace('2026','2025')
for sm in doc.xpath('//small[@class="st-keys"]'):
 if '41275879' in sm.text_content() and sm.text:sm.text=sm.text.replace('Reni M 2026','Reni M 2025')
 if '39908431' in sm.text_content() and sm.text:sm.text=sm.text.replace('NRG1 ·','eNRGy ·')
 if '41781152' in sm.text_content() and sm.text:sm.text=sm.text.replace('MIXED_REVIEW ·','Hong 2026 review ·')
p.write_text('<!doctype html>\n'+html.tostring(doc,encoding='unicode',method='html')+'\n')
(R/'tools/systemic_source/matrix_content.py').write_text('# Canonical systemic content synchronized after the reconciled audit.\n'+'\n'.join(k+' = '+repr(d[v]) for k,v in [('CARDS','cards'),('SAFETY','safety'),('GUIDELINES','guidelines')])+'\n')
print('Added primary CAIRO5 survival links; aligned citation labels/year.')
