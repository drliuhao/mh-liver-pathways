"""Read-only source-to-live identity matching; writes proposals, never compact data."""
from pathlib import Path
import json, re, subprocess

ROOT = Path(__file__).resolve().parents[2]
NODE = '/Users/haoliu/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node'
BASELINE = '30039fe'
ROADS = ['hcc','crlm','icca','hilar','nelm','chcca','adenoma','incidental','pdac','pnet','pcyst','ampullary']
plain = lambda s: re.sub(r'\s+', ' ', str(s or '')).strip()

def option_key(road, lead):
    h=5381
    b=lead.encode('utf-16-le')
    for i in range(0,len(b),2): h=(h*33+int.from_bytes(b[i:i+2],'little')) & 0xffffffff
    digits='0123456789abcdefghijklmnopqrstuvwxyz'; out=''
    while h: h,k=divmod(h,36);out=digits[k]+out
    return road+':'+(out or '0')

def stages(road, baseline):
    file='hcc/index.html' if road=='hcc' else road+'/data/pathway.json'
    text=subprocess.check_output(['git','show',BASELINE+':'+file],cwd=ROOT,text=True) if baseline else (ROOT/file).read_text()
    if road!='hcc': return json.loads(text)['gates']
    code="const fs=require('fs'),vm=require('vm'),s=fs.readFileSync(0,'utf8'),a=s.indexOf('const STAGES = ['),b=s.indexOf('/* the quantifier',a);process.stdout.write(JSON.stringify(vm.runInNewContext(s.slice(a,b)+';STAGES')));"
    return json.loads(subprocess.check_output([NODE,'-e',code],input=text,text=True))

def display_copy(baseline):
    file='assets/contextual-copy.js'
    text=subprocess.check_output(['git','show',BASELINE+':'+file],cwd=ROOT,text=True) if baseline else (ROOT/file).read_text()
    return json.loads(text[text.index('{'):text.rfind('}')+1])['recommendations']

def identities(road, source, copies):
    out={}
    for s in source:
        for group in ['standard','alt','avoid']:
            for i,r in enumerate(s.get(group,[])):
                prefix=f"{road}/{s['id']}/{group}/{i}"
                if r.get('opts') is not None:
                    for j,o in enumerate(r['opts']):
                        lead=plain(str(o.get('name',''))+' '.join(o.get('flags',[]))+' '+str(o.get('when','')))
                        out[prefix+f'/opts/{j}']={'key':option_key(road,lead),'lead':lead,'decision':s['id']}
                elif r.get('t'):
                    lead=plain(r['t'])
                    copy=copies.get(prefix)
                    if copy and plain(copy['source'])==lead:lead=plain(copy['concise'])
                    out[prefix]={'key':option_key(road,lead),'lead':lead,'decision':s['id']}
    return out

live=json.loads((ROOT/'tools/audit_revision/live_option_keys.json').read_text())
live_by_key={}
for row in live:live_by_key.setdefault(row['key'],[]).append(row)
compact=json.loads((ROOT/'tools/compact_evidence_source.json').read_text())
old_by_key={}; current_by_path={}
old_copy,new_copy=display_copy(True),display_copy(False)
for road in ROADS:
    for path,row in identities(road,stages(road,True),old_copy).items():old_by_key.setdefault(row['key'],[]).append((path,row))
    current_by_path.update(identities(road,stages(road,False),new_copy))
proposals=[]; unresolved=[]
for old_key in sorted(set(compact['options'])|set(compact['reference_links'])):
    if old_key in live_by_key:continue
    candidates=[]
    for path,old in old_by_key.get(old_key,[]):
        new=current_by_path.get(path)
        if new and new['key'] in live_by_key and any(x['lead']==new['lead'] for x in live_by_key[new['key']]):
            candidates.append({'source_option_identity':path,'new_key':new['key'],'old_lead':old['lead'],'new_lead':new['lead'],
                'live_decisions':sorted({x['decision'] for x in live_by_key[new['key']]})})
    if candidates and len({x['new_key'] for x in candidates})==1:
        proposals.append({'old_key':old_key,**candidates[0],
            'old_option_rows':compact['options'].get(old_key,{}).get('rows',[]),
            'reference_links':compact['reference_links'].get(old_key,[]),
            'action':'Remap the option identity; validate each numerical row against the corrected live option text before retaining it. Preserve linked treatment-reference groups.'})
    else:
        unresolved.append({'old_key':old_key,'lead':compact['options'].get(old_key,{}).get('lead'),
            'rows':compact['options'].get(old_key,{}).get('rows',[]),'reference_links':compact['reference_links'].get(old_key,[]),
            'candidate_identities':candidates,'action':'Review before dropping or remapping; no unique source-to-live identity match.'})
output={'baseline':BASELINE,'live_option_occurrences':len(live),'live_unique_keys':len(live_by_key),
    'method':'Exact hash of source lead (including guarded contextual display copy) plus unchanged roadmap/gate/group/item/option identity, checked against full live lead. Numerical row validity is a separate check.',
    'remaps':proposals,'unresolved':unresolved}
(ROOT/'tools/audit_revision/compact_option_remap_proposals.json').write_text(json.dumps(output,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'live_occurrences':len(live),'live_keys':len(live_by_key),'remaps':len(proposals),'unresolved':len(unresolved),
    'linked_remaps':[{k:x[k] for k in ['old_key','new_key','reference_links']} for x in proposals if x['reference_links']],
    'unresolved_with_rows':[x['old_key'] for x in unresolved if x['rows'] or x['reference_links']]}))
