"""Build exact, duplicate-aware PowerPoint propagation plan; no binary edits."""
from pathlib import Path
from collections import defaultdict,Counter
import json,hashlib,difflib
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1];WORK=ROOT.parent
read=lambda p:json.loads(Path(p).read_text())
rows=read(HERE/'shared/all_ppt_paragraphs.json')
proposals=[]
for name in ['liver/exact_paragraph_proposals.json','other/replacement_proposals.json']:
    d=read(HERE/name);d=d['proposals'] if isinstance(d,dict) else d
    proposals += [q for q in d if q['kind']=='pptx']
manual=read(HERE/'liver/manual_paragraph_proposals.json')['proposals']
rejected={'LIVER-MAN-0039'} | {f'LIVER-MAN-{i:04d}' for i in range(41,64)}
manual=[q for q in manual if q.get('id') not in rejected]
(HERE/'root_proposal_dispositions.json').write_text(json.dumps({'rejected_ids':sorted(rejected),'reason':'Generic category replacement was incorrectly extended to unrelated systemic-treatment papers. Only Auer PMID37174120 locations are eligible.'},indent=2)+'\n')
superseded={q['supersedes'] for q in manual if q.get('supersedes')}
proposals=[q for q in proposals if q.get('id') not in superseded]
proposals += [q for q in manual if q['kind']=='pptx']
tp_data=read(HERE/'transplant/transplant_exact_replacements.json');tp=tp_data['proposals']
byloc={(r['artifact'],r['part'],r['paragraph_index']):r for r in rows}
def retain_breaks(actual,old,new):
    assert actual.replace('\n','')==old.replace('\n',''),(actual[:100],old[:100])
    if actual==old:return new
    a=old.replace('\n','');b=new.replace('\n','')
    offsets=[i for i,c in enumerate(actual) if c!='\n']+[len(actual)]
    for tag,i,j,k,l in reversed(difflib.SequenceMatcher(None,a,b,autojunk=False).get_opcodes()):
        if tag!='equal':actual=actual[:offsets[i]]+b[k:l]+actual[offsets[j]:]
    return actual
full=defaultdict(dict)
allowed=defaultdict(set)
for q in proposals:
    r=byloc[(q['artifact'],q['part'],q['paragraph_index'])]
    old=r['text'];new=retain_breaks(old,q['old'],q['new'])
    full[old].setdefault(new,[]).append(q.get('id',q.get('proposal_id')))
    allowed[old].add(r['part_sha256'])
tp_full={}
for q in tp:
    for o in q['occurrences']:
        if o['artifact']=='word':continue
        hits=[r for r in rows if r['artifact']==o['path'] and r['slide']==o['slide'] and q['old'] in r['text']]
        assert hits,(q['id'],o)
        for r in hits:
            old=r['text'];entry=tp_full.setdefault(old,{'new':old,'ids':[]})
            allowed[old].add(r['part_sha256'])
            if q['old'] in entry['new']:entry['new']=entry['new'].replace(q['old'],q['new'])
            entry['ids'].append(q['id'])
for n in tp_data.get('notes_exact_matches',[]):
    old=n['paragraph_text'];entry=tp_full.setdefault(old,{'new':old,'ids':[]})
    if n['old'] in entry['new']:entry['new']=entry['new'].replace(n['old'],n['new'])
    entry['ids'].append(n['proposal_id'])
    for r in rows:
        if r['artifact']==n['path'] and r['part']==n['part'] and r['text']==old:allowed[old].add(r['part_sha256'])
for old,entry in tp_full.items():full[old].setdefault(entry['new'],[]).extend(entry['ids'])
conflicts=[{'old':k,'versions':v} for k,v in full.items() if len(v)>1]
(HERE/'ppt_conflicts.json').write_text(json.dumps(conflicts,indent=2))
assert not conflicts,('Resolve exact paragraph conflicts',len(conflicts))
out=[]
for r in rows:
    old=r['text'];new=old;ids=[]
    if old in full and (len(old)>=150 or r['part_sha256'] in allowed[old]):
        new=next(iter(full[old]));ids=full[old][new]
    else:
        # Full source-card paragraphs may also be embedded in speaker notes.
        for a,versions in sorted(full.items(),key=lambda x:-len(x[0])):
            b=next(iter(versions))
            if len(a)>=150 and a in new:
                new=new.replace(a,b);ids+=versions[b]
    if r['slide']==1:
        for a,b in [('V15','V18'),('v15','v18'),('25 October 2026','1 November 2026'),('2026-10-25','2026-11-02')]:
            if a in new:new=new.replace(a,b);ids+=['SYNC-EDITION']
    layout=None
    if '/slides/' in r['part'] and 'seven' in new and 'crossover' in new and 'TP-' in ' '.join(ids):
        new=new.replace('The control arm included seven resections and two transplants outside protocol; crossover was not allowed.', 'Control arm: seven resections and two off-protocol transplants; crossover was not allowed.')
    if '/slides/' in r['part'] and old.startswith('204 patients treated at 750 mg every 2 weeks;') and old!=new:
        new='204 treated (42 pancreatic). Primary efficacy: 161, including 158 with investigator-assessed measurable disease; pancreatic efficacy cohort: 36. Dose: 750 mg every 2 weeks.'
        layout={'height_px':40,'vertical_alignment':'top','reason':'Keep the expanded population definitions below their heading without reducing font size.'}
    if old!=new:
        record={**{k:v for k,v in r.items() if k!='text'},'old':old,'new':new,'source_ids':list(dict.fromkeys(ids))}
        if layout:record['layout_adjustment']=layout
        out.append(record)
inventory=read(HERE/'current_artifact_inventory.json')
grouped=defaultdict(list)
for r in out:grouped[r['artifact']].append(r)
cards=read(HERE/'source_card_additions.json')
decks=[]
for d in inventory['decks']:
    p=Path(d['current_master']);assert hashlib.sha256(p.read_bytes()).hexdigest()==d['sha256']
    target=WORK/'V18_consistent_release_2026-11-02/Evidence_Libraries'/d['family']/d['key']/'Evidence_Summaries_v18.pptx'
    decks.append({**d,'target':str(target),'changes':grouped[str(p)],'additions':[q for q in cards if q['target_library']==str(p)]})
(HERE/'ppt_sync_plan.json').write_text(json.dumps(decks,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'decks':len(decks),'paragraphs':len(out),'visible':sum('/slides/' in r['part'] for r in out),'notes':sum('/notesSlides/' in r['part'] for r in out),'source_cards':len(cards),'libraries_with_corrections':sum(bool(d['changes']) for d in decks)},indent=2))
