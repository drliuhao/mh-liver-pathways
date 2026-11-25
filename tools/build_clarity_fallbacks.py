"""Canonical redirects with no-JavaScript fallback from the current clinical dataset.
Historical HTML is preserved in Website_Clarity_Release_2026-11-24/archive/.
"""
import html,json,re,subprocess
from pathlib import Path
R=Path(__file__).resolve().parents[1];D=json.loads((R/'transplant/assets/content.json').read_text());e=html.escape
BASE='/mh-liver-pathways/';KEY='20261125-alignment1'
def shell(title,content,script=''):
 return f'<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{e(title)}</title><link rel="stylesheet" href="{BASE}assets/portal-navigation.css?v={KEY}"><link rel="stylesheet" href="{BASE}assets/evidence-tools.css?v={KEY}"><script src="{BASE}assets/portal-navigation.js?v={KEY}" defer></script>{f"<script>{script}</script>" if script else ""}</head><body><main class="evidence-wrap">{content}</main></body></html>'
for p in D['index']:
 slug=p['slug'];url=BASE+'transplant/'+slug+'/'
 links=''.join(f'<li><a href="{url}#meeting-{e(q["id"])}">{e(q["question"])}</a></li>' for q in p['issues'] if not q.get('resolved'))
 records=[]
 for q in p['issues']:
  comp=''.join(f'<section><h3>{e(D["sources"][c["ref"]]["short"])}</h3><p>{e(c["text"])}</p><p>{e(c.get("locator") or "")} · <a href="{e(D["sources"][c["ref"]]["url"])}">Source</a></p></section>' for c in q['comparisons'])
  records.append(f'<section id="{e(q["id"])}"><h2>{e(q["question"])}</h2><p><strong>{e(q["status"]) if q.get("resolved") else "Pending multidisciplinary approval."}</strong> <a href="{url}#meeting-{e(q["id"])}">Open this question in the pathway →</a></p>{comp}<h3>{"Applicable guidance" if q.get("resolved") else "Proposed local approach"}</h3><p>{e(q["proposal"])}</p><h3>Why this matters</h3><p>{e(q["rationale"])}</p><p>Proposed responsible team: {e(q["owners"])}</p></section>')
 script=f'var id=location.hash.slice(1).replace(/^meeting-/,"");location.replace({json.dumps(url)}+({json.dumps([q["id"] for q in p["issues"]])}.includes(id)?"#meeting-"+id:"#meeting"));'
 content=f'<h1>{e(p["code"])} discussion questions</h1><p>This printable fallback is generated from the same current question records as the interactive pathway. It redirects to the canonical record when JavaScript is available.</p><ul>{links}</ul>'+''.join(records)
 (R/'transplant/meeting-records'/f'{slug}.html').write_text(shell(p['code']+' discussion record',content,script))
 # Retain every legacy high-risk anchor; remove stale duplicated clinical prose.
 statuses=json.loads(subprocess.check_output(['node','-e',f'const H=require("./transplant/assets/high-risk.js");process.stdout.write(JSON.stringify({json.dumps([r["anchor"] for r in D["high_risk"]["pathways"][slug]["reviews"]])}.map(x=>H.statusLabel(x))));'],cwd=R,text=True))
 links=''.join(f'<li id="{e(r["anchor"])}"><a href="{url}#high-risk-{e(r["anchor"])}">{e(r["title"])}</a> — {e(status)}</li>' for r,status in zip(D['high_risk']['pathways'][slug]['reviews'],statuses))
 script=f'location.replace({json.dumps(url+"#high-risk")}+(location.hash?"-"+location.hash.slice(1):""));'
 (R/'transplant/high-risk'/slug/'index.html').write_text(shell(p['code']+' high-risk reviews',f'<h1>{e(p["code"])} high-risk reviews</h1><p>These reviews now live with the standard pathway. A proposal is not an activated protocol; each review states its actual status.</p><ul>{links}</ul>',script))
# AFP has unique six-part discussion text and source comparisons; preserve that owned record.
p=R/'transplant/meeting-records/hcc-b1-1/index.html';s=p.read_text()
if 'afp-discussion.js' not in s:
 s=s.replace('</head>',f'<script src="{BASE}assets/afp-discussion.js?v={KEY}" defer></script></head>')
 s=s.replace('<h1>HCC B1.1 — AFP-only decision record</h1>','<h1>AFP response: questions for consensus</h1>')
 s=s.replace('<b>OPEN proposal:</b>','<b>Proposed · not activated:</b>')
 s=re.sub(r'<h2>(B1\.1[a-f]) — (.*?)</h2>',r'<p class="small">Record \1</p><h2>\2</h2>',s)
 p.write_text(s)
print('Seven discussion fallbacks and seven high-risk redirects generated from current records.')
