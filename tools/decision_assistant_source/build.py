"""Build the static review site without altering the protocol DOCX/PDF depots."""
from html import escape as e
from pathlib import Path
import json
import shutil
import sys
from content import DIST, PATHWAYS, SOURCES
from decision_assistants import ASSISTANTS, JOURNEYS, VERSION
from care_options import CARE, build_continuations

STAMP='20261025-streamlined-v1'
HIGH_RISK=json.loads((Path(__file__).parent/'high_risk_data.json').read_text())

def document(title, data):
    payload=json.dumps(data,ensure_ascii=False).replace('</','<\\/')
    return f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="robots" content="noindex"><meta name="description" content="Source-linked, decision-by-decision transplant oncology pathways. Clinical review draft.">
<title>{e(title)} · Memorial Hermann Transplant Oncology</title><link rel="stylesheet" href="/assets/style.css?v={STAMP}"><link rel="stylesheet" href="/assets/assistant.css?v={STAMP}">
<link rel="stylesheet" href="/assets/high-risk.css?v={STAMP}"><script src="/assets/high-risk.js?v={STAMP}" defer></script><script src="/assets/assistant.js?v={STAMP}" defer></script><script src="/assets/risk-routing.js?v={STAMP}" defer></script><script src="/assets/app.js?v={STAMP}" defer></script></head><body><div id="app"></div>
<dialog id="source-dialog" aria-labelledby="source-title"></dialog><script id="protocol-data" type="application/json">{payload}</script>
<noscript><main><h1>{e(title)}</h1><p>This interactive reference needs JavaScript. The printable alignment records and original protocols remain available.</p><ul>{''.join(f'<li><a href="/meeting-records/{p["slug"]}.html">{e(p["name"])} alignment record</a> · <a href="{p["protocol"]}">V3 protocol</a></li>' for p in PATHWAYS)}</ul></main></noscript></body></html>'''

def ref_link(c):
    r=SOURCES[c['ref']]
    return f'<a href="{e(r["pdf"],quote=True)}">{e(r["short"])} · full text</a>'

def printable(p):
    sections=[]
    for i in p['issues']:
        comparisons=''.join(f'<section class="comparison"><div class="source-kind">{e(SOURCES[c["ref"]]["kind"])}</div><h4>{e(SOURCES[c["ref"]]["short"])}</h4><p class="quotation">{("“" if c["quote"] else "")+e(c["text"])+("”" if c["quote"] else "")}</p><p class="small muted">{"Short verbatim excerpt" if c["quote"] else "Source summary / scope"} · {e(c["locator"] or SOURCES[c["ref"]]["locator"])}</p>{ref_link(c)}</section>' for c in i['comparisons'])
        sections.append(f'<article class="issue-record" id="{i["id"]}"><p class="eyebrow">{e(i["record"])}</p><h2>{e(i["question"])}</h2><p class="small">Status: discussion required — not yet approved. <a href="/{p["slug"]}/">Return to interactive pathway</a></p><div class="comparison-grid">{comparisons}</div><div class="proposal"><div><b>Proposed local approach</b><p>{e(i["proposal"])}</p></div><div><b>Rationale</b><p>{e(i["rationale"])}</p></div></div><p class="small">Proposed responsible team: {e(i["owners"])}</p><p>Meeting decision: ____________________ &nbsp; Responsible team/date: ____________________</p><p>Implementation / protocol changes: __________________________________________________</p></article>')
    return f'<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{e(p["code"])} — alignment meeting record</title><link rel="stylesheet" href="/assets/style.css?v={STAMP}"></head><body><main class="wrap"><div class="pathhero"><div><p class="eyebrow">Source comparison: October 17, 2026 · language revision: October 24, 2026</p><h1>{e(p["code"])} alignment & decision record</h1><p>Draft for meeting discussion. No proposal is approved. Use browser Print to save this current record as PDF; reconcile agreed decisions with the separately linked V3 Word documents.</p></div></div>{"".join(sections)}</main></body></html>'

def build():
    (DIST/'assets').mkdir(exist_ok=True)
    for asset in ['app.js','style.css','assistant.js','assistant.css','high-risk.js','high-risk.css','risk-routing.js']:
        shutil.copyfile(Path(__file__).parent/asset,DIST/'assets'/asset)
    base=dict(index=PATHWAYS,sources=SOURCES,assistants=ASSISTANTS,assistant_version=VERSION,journeys=JOURNEYS,high_risk=HIGH_RISK,
              care=CARE,continuations=build_continuations(PATHWAYS,ASSISTANTS))
    (DIST/'index.html').write_text(document('Decision pathways',dict(base,mode='home')),encoding='utf8')
    (DIST/'meeting-records').mkdir(exist_ok=True)
    (DIST/'alignment').mkdir(exist_ok=True)
    for p in PATHWAYS:
        folder=DIST/p['slug'];folder.mkdir(exist_ok=True)
        (folder/'index.html').write_text(document(p['name'],dict(base,pathway=p,mode='pathway')),encoding='utf8')
        aligned=document(p['code']+' alignment record',dict(base,pathway=p,mode='alignment'))
        (DIST/'alignment'/f'{p["slug"]}.html').write_text(aligned,encoding='utf8')
        (DIST/'alignment'/p['slug']).mkdir(exist_ok=True)
        (DIST/'alignment'/p['slug']/'index.html').write_text(aligned,encoding='utf8')
        (DIST/'meeting-records'/f'{p["slug"]}.html').write_text(printable(p),encoding='utf8')
        # Preserve existing inbound detailed-roadmap links, but stop duplicating treatment encyclopedias.
        target=p['roadmap'] or SOURCES['E-consensus']['pdf']
        (folder/'clinical-roadmap.html').write_text(f'<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{e(p["code"])} treatment roadmap</title><meta http-equiv="refresh" content="0;url={e(target,quote=True)}"></head><body><h1>{e(p["code"])} treatment reference</h1><p><a href="{e(target,quote=True)}">Open the tumor-specific treatment roadmap / reference</a></p><p><a href="/{p["slug"]}/">Return to the transplant decision pathway</a></p></body></html>',encoding='utf8')
    (DIST/'assets'/'content.json').write_text(json.dumps(base,ensure_ascii=False,indent=2),encoding='utf8')
    # Retired recording URLs remain usable, but lead directly to the short assistant.
    retired=DIST/'recording-templates'
    retired.mkdir(exist_ok=True)
    for old in retired.iterdir():
        if old.is_file() and old.suffix in ('.html','.md','.zip','.css','.js'):
            old.unlink()
    def redirect(name,target):
        (retired/name).write_text(f'<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Transplant decision assistant</title><meta http-equiv="refresh" content="0;url={e(target,quote=True)}"></head><body><h1>Choose the essential findings in the pathway</h1><p>The short decision assistant is now in “Tests and information needed.”</p><p><a href="{e(target,quote=True)}">Open the decision assistant →</a></p></body></html>',encoding='utf8')
    redirect('index.html','/')
    for p in PATHWAYS:
        for s in p['steps']:redirect(f'{p["slug"]}--{s["id"]}.html',f'/{p["slug"]}/#{s["id"]}')
    print(f'Built {len(PATHWAYS)} pathways, {sum(len(p["steps"]) for p in PATHWAYS)} decisions, {sum(len(p["issues"]) for p in PATHWAYS)} linked meeting questions.')

def validate():
    problems=[]
    continuations=build_continuations(PATHWAYS,ASSISTANTS)
    def local(url):
        if url.startswith('/'):
            if not (DIST/url.split('#')[0].lstrip('/')).exists():problems.append(f'Missing local resource: {url}')
    for id,r in SOURCES.items():local(r['pdf'])
    for p in PATHWAYS:
        ids=[s['id'] for s in p['steps']];issues={i['id'] for i in p['issues']}
        if [id for phase in JOURNEYS[p['slug']] for id in phase['steps']] != ids:
            problems.append(f'Overview must preserve the complete decision sequence: {p["slug"]}')
        care_ids={c['id'] for c in CARE[p['slug']]}
        def validate_action(a):
            if a['step'] and a['step'] not in ids:problems.append(f'Unknown continuation step: {a}')
            if a['care'] and a['care'] not in care_ids:problems.append(f'Unknown care plan: {a}')
        for c in CARE[p['slug']]:
            if not c['tasks'] or not c['refs']:problems.append(f'Incomplete care plan: {c["id"]}')
            if not c['actions'] and not c['endpoint']:problems.append(f'Care plan has no next action: {c["id"]}')
            for r in c['refs']:
                if r not in SOURCES:problems.append(f'Unknown care source: {r}')
            for a in c['actions']:validate_action(a)
        if len(set(ids))!=len(ids):problems.append(f'Duplicate steps: {p["slug"]}')
        local(p['protocol'])
        for d in p['docs']:local(d['url'])
        if len(p['docs'])!=2:problems.append(f'Missing governance documents: {p["slug"]}')
        used=set()
        for s in p['steps']:
            a=ASSISTANTS.get(f'{p["slug"]}/{s["id"]}')
            onward=continuations[f'{p["slug"]}/{s["id"]}']
            for n,b in enumerate(s['branches']):
                actions=onward['branches'].get(str(n),[])
                if not actions:problems.append(f'Branch without next action: {p["slug"]}/{s["id"]}/{n}')
                for x in actions:validate_action(x)
            for n,r in enumerate(a['rules']):
                if r['branch'] is None:
                    actions=onward['rules'].get(str(n),[])
                    if not actions:problems.append(f'Rule without next action: {p["slug"]}/{s["id"]}/{n}')
                    for x in actions:validate_action(x)
            if not a:problems.append(f'Missing decision assistant: {p["slug"]}/{s["id"]}')
            else:
                qids={q['id']:q for q in a['questions']}
                if set(a['example']) != set(qids):problems.append(f'Incomplete example: {p["slug"]}/{s["id"]}')
                for q in a['questions']:
                    if a['example'].get(q['id']) not in {o['value'] for o in q['options'] if o['value']!='unknown'}:
                        problems.append(f'Invalid example choice: {p["slug"]}/{s["id"]}/{q["id"]}')
                if not 1<=len(qids)<=4:problems.append('Expected 1–4 essential choices')
                for q in a['questions']:
                    for ref in q['refs']+[r for c in q['criteria'] for r in c['refs']]:
                        if ref not in SOURCES:problems.append(f'Unknown assistant source: {ref}')
                for r in a['rules']:
                    if r['branch'] is not None and not 0<=r['branch']<len(s['branches']):problems.append('Invalid assistant branch')
                    for ref in r['refs']:
                        if ref not in SOURCES:problems.append(f'Unknown rule source: {ref}')
                    for q,values in r['when'].items():
                        if q not in qids:problems.append(f'Unknown assistant question: {q}');continue
                        opts={o['value'] for o in qids[q]['options']}
                        if not set(values if isinstance(values,list) else [values])<=opts:problems.append(f'Unknown option in {p["slug"]}/{s["id"]}/{q}')
            if not s['orders'] or not s['branches']:problems.append(f'Empty decision: {p["slug"]}/{s["id"]}')
            for i in s['issues']:
                used.add(i)
                if i not in issues:problems.append(f'Missing question: {p["slug"]}/{i}')
            for b in s['branches']:
                if b['to'] and b['to'] not in ids:problems.append(f'Invalid branch: {p["slug"]}/{b["to"]}')
            items=[x for g in s['orders'] for x in g['items']]+[x for b in s['branches'] for x in b['criteria']]+s['stops']
            def flattened(entries):
                for x in entries:
                    yield x
                    yield from flattened(x.get('children',[]))
            for x in flattened(items):
                if not x['refs']:problems.append(f'Uncited statement: {x["text"]}')
                for ref in x['refs']:
                    if ref not in SOURCES:problems.append(f'Unknown reference: {ref}')
        if issues-used:problems.append(f'Orphan questions: {p["slug"]}: {issues-used}')
        for i in p['issues']:
            if not i['comparisons']:problems.append(f'No comparison: {i["id"]}')
            for c in i['comparisons']:
                if c['ref'] not in SOURCES:problems.append(f'Unknown comparison source: {c["ref"]}')
    if problems:
        print('\n'.join(problems));sys.exit(1)
    print('PASS: every decision has inputs/results; every clinical bullet is referenced; every branch/question/resource resolves; all seven protocol + paired governance DOCX links preserved.')

if __name__=='__main__':
    validate()
    build()
