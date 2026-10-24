"""Validate published blank instruments, mappings and data integrity."""
import csv
from html import escape
import io
import json
from pathlib import Path
import zipfile

ROOT=Path(__file__).resolve().parents[1]
data=json.loads((ROOT/'transplant/assets/content.json').read_text())
folder=ROOT/'transplant/recording-templates'
count=0; observations=0; checklist_items=0

def leaves(items):
    for item in items:
        if item.get('children'): yield from leaves(item['children'])
        else: yield item

def rows(z,name):
    return list(csv.DictReader(io.StringIO(z.read(name).decode())))

for p in data['index']:
    with zipfile.ZipFile(folder/(p['slug']+'-recording-kit.zip')) as z:
        assert z.testzip() is None
        schema=json.loads(z.read('schema.json'))
        fields={f['id']:f for g in schema['modules'] for f in g['fields']}
        assert len(fields)==sum(len(g['fields']) for g in schema['modules']), 'Duplicate field IDs'
        assert all(f['type'] in ('text','date','number','integer','choice') for f in fields.values())
        assert all(f['choices'] for f in fields.values() if f['type']=='choice')
        assert set(fields)=={r['field_id'] for r in rows(z,'dictionary.csv')}
        source_ids=set(json.loads(z.read('sources.json')))
        required=rows(z,'source_checklist.csv')
        mapping=rows(z,'decision_modules.csv')
        for s in p['steps']:
            stem=p['slug']+'--'+s['id']
            html=(folder/(stem+'.html')).read_text()
            md=(folder/(stem+'.md')).read_text()
            assert 'data-copy' in html and 'data-print' in html
            assert '<form id="assessment"' in html and 'data-save' in html and 'data-import' in html
            assert html.count('id="signoff-decision-signoff"')==1
            assert "connect-src 'none'" in html and "form-action 'none'" in html
            assert 'data-module-source' in html
            assert f'../{p["slug"]}/#{s["id"]}' in html
            assert stem+'.md' in html and p['slug']+'-recording-kit.zip' in html
            source_items=[x['text'] for g in s['orders'] for x in leaves(g['items'])]
            actual=[r for r in required if r['decision_id']==s['id']]
            assert source_items==[r['required_information'] for r in actual], stem
            for item in source_items:
                assert item in md and escape(item) in html, (stem,item)
            for r in actual:
                assert set(r['source_ids'].split(';'))<=source_ids
                assert all(not r[k] for k in ('record_id','assessment_id','documentation_status','result_record_reference','observed_date'))
            values=rows(z,'blank_values/'+s['id']+'.csv')
            assert all(None not in v and None not in v.values() for v in values), 'Malformed CSV row'
            modules={r['module_id'] for r in mapping if r['decision_id']==s['id']}
            expected={f['id'] for g in schema['modules'] if g['id'] in modules for f in g['fields']}
            assert expected=={v['field_id'] for v in values}, stem
            for v in values:
                assert v['pathway_id']==p['slug'] and v['decision_id']==s['id']
                assert all(not v[k] for k in ('record_id','assessment_id','value','value_status','observed_date','source_document','verified_by'))
                assert fields[v['field_id']]['label'] in md
            import re
            schema_html=json.loads(re.search(r'<script type="application/json" id="form-schema">(.*?)</script>',html,re.S)[1].replace('<\\/','</'))
            assert {f['id'] for g in schema_html['modules'] for f in g['fields']}==expected
            if any(g['repeat'] for g in schema_html['modules']):assert 'data-add' in html
            for g in schema_html['modules']:
                for f in g['fields']:
                    assert 'data-field="'+f['id']+'"' in html
            count+=1; observations+=len(values); checklist_items+=len(actual)
assert count==46
assert len(list(folder.glob('*--*.html')))==count
assert len(list(folder.glob('*.zip')))==7
assert len(list(folder.glob('*--*.md')))==count
js=(folder/'templates.js').read_text()
assert not any(x in js for x in ('fetch(', 'XMLHttpRequest', 'localStorage', 'sessionStorage', 'indexedDB'))
print(f'PASS: {count} decision templates; 7 intact kits; {checklist_items} original checklist items retained; {observations} blank field rows; schema, source references, field mapping and electronic-control checks.')
