"""Build extrahepatic-disease/index.html: proposed positions on previously treated extrahepatic disease.

usage: python3 tools/build_ehd_page.py

Source: tools/ehd_positions.json, a copy of the V16 decision worksheet content (ehd_content.json in the
private V16_previously_treated_EHD_2026-10-29 folder) with public source links added. The page is a
reference for multidisciplinary review: every position is proposed and nothing is activated. Roadmap
decisions and transplant high-risk reviews link here; this page links back to them.
"""
import html, json, re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = '/mh-liver-pathways/'
KEY = '20261029-ehd2'
data = json.loads((ROOT / 'tools/ehd_positions.json').read_text())
links = json.loads((ROOT / 'assets/roadmap-links.json').read_text())
S = data['sources']
e = html.escape

# Transplant high-risk reviews (transplant/<slug>/#high-risk-<anchor>).
TRANSPLANT = {'HCC-B5': ('hcc', 'hcc-b5', 'HCC'), 'iCCA-B4': ('icca', 'icca-b4', 'iCCA'), 'pCCA-B1': ('pcca', 'pcca-b1', 'pCCA'),
              'CRLM-B5': ('crlm', 'crlm-b5', 'CRLM'), 'NET-B4': ('nelm', 'net-b4', 'NELM'), 'HEHE-B2': ('hehe', 'hehe-b2', 'HEHE')}
# Roadmap question -> transplant question for the same tumor (where one exists).
RELATED = {'HCC-R1': ['HCC-B5'], 'cHCC-CCA-R1': ['iCCA-B4'], 'iCCA-R1': ['iCCA-B4'], 'pCCA-R1': ['pCCA-B1'], 'CRLM-R1': ['CRLM-B5'],
           'NELM-R1': ['NET-B4'], 'pNET-R1': ['NET-B4']}
for r, ts in list(RELATED.items()):
    for t in ts: RELATED.setdefault(t, []).append(r)
ROADMAP_NAME = {'hcc': 'HCC', 'crlm': 'CRLM', 'icca': 'iCCA', 'hilar': 'Hilar cholangiocarcinoma', 'chcca': 'Combined HCC–CCA',
                'nelm': 'NELM', 'pnet': 'pNET', 'pdac': 'PDAC', 'ampullary': 'Ampullary'}
READ = {'full': 'Full text read', 'abstract': 'Abstract only · full text pending', 'policy': 'Policy text',
        'registry': 'Trial registry', 'existing': 'Earlier review'}


def gate_names(slug):
    if slug == 'hcc':
        s = (ROOT / 'hcc/index.html').read_text()
        return dict(re.findall(r'\{id:"([^"]+)", tone:"[a-z]+", name:"([^"]+)"', s))
    return {g['id']: g['name'] for g in json.loads((ROOT / f'{slug}/data/pathway.json').read_text())['gates']}


# Roadmap decisions that link to each question, read from roadmap-links.json so the two stay in step.
decisions = {}
for slug, gates in links.items():
    names = None
    for gid, recs in gates.items():
        for r in recs:
            m = re.fullmatch(r'extrahepatic-disease/#(.+)', r.get('url', ''))
            if m:
                names = names or gate_names(slug)
                decisions.setdefault(m.group(1), []).append((slug, gid, names[gid], r['when']))


def source_links(key):
    L = S[key].get('links', {})
    out = []
    if L.get('pubmed'): out.append(f'<a href="{e(L["pubmed"])}">PubMed</a>')
    if L.get('doi'): out.append(f'<a href="{e(L["doi"])}">Journal</a>')
    if L.get('pmc'): out.append(f'<a href="{e(L["pmc"])}">Free full text (PMC)</a>')
    if L.get('tmc'): out.append(f'<a href="{e(L["tmc"])}">TMC library full text</a>')
    if L.get('registry'): out.append(f'<a href="{e(L["registry"])}">Trial registry</a>')
    return ' · '.join(out)


def study(s):
    rd = s['read']
    acc = source_links(s['key'])
    return (f'<div class="study ehd-study"><h4>{e(S[s["key"]]["short"])}</h4>'
            f'<p class="ehd-read{" ehd-abstract" if rd == "abstract" else ""}">{e(READ.get(rd, rd))}</p>'
            f'<p><b>Population and selection.</b> {e(s["design_population"])} {e(s["selection"])}</p>'
            f'<p><b>Results.</b> {e(s["results"])}</p>'
            f'<p class="limits"><b>Limits.</b> {e(s["limits"])}</p>'
            f'<small class="ehd-locator">{e(s["locator"])}</small>'
            + (f'<p class="source-access">{acc}</p>' if acc else '') + '</div>')


def where(q):
    items = []
    if q['id'] in TRANSPLANT:
        slug, anchor, label = TRANSPLANT[q['id']]
        items.append(f'<li><a href="{BASE}transplant/{slug}/#high-risk-{anchor}">{e(label)} transplant pathway · high-risk review {e(q["id"])}</a></li>')
    for slug, gid, name, when in decisions.get(q['id'], []):
        items.append(f'<li><a href="{BASE}{slug}/#decision-{e(gid)}">{e(ROADMAP_NAME[slug])} roadmap · {e(name)}</a> <span class="ehd-when">{e(when)}</span></li>')
    for rel in RELATED.get(q['id'], []):
        items.append(f'<li><a href="#{e(rel)}">Related question {e(rel)}</a></li>')
    return '<ul class="ehd-where">' + ''.join(items) + '</ul>' if items else ''


def label(status):
    """'Proposed; MDT selection' -> 'Open proposal · MDT selection'; 'Closed; registry only' -> 'Open proposal · Closed; registry only'."""
    rest = re.sub(r'^Proposed[;:,]?\s*', '', status)
    return 'Open proposal' + (f' · {rest[:1].upper()}{rest[1:]}' if rest else '')


qs = data['questions']
nfull = sum(q['read_full'] for q in qs)
nabs = sum(q['read_abstract'] for q in qs)
nlines = sum(len(q['evidence']) for q in qs)
tumors = []
for q in qs:
    if q['tumor'] not in tumors: tumors.append(q['tumor'])

css = ('.ehd-ask{font-size:18px;font-weight:600;margin:6px 0 14px}.ehd-position{background:#f6f9fa;border:1px solid var(--line);border-radius:6px;padding:12px 16px}'
       '.review-decision.ehd-roadmap{border-left-color:#2f6f95}.review-decision.ehd-roadmap>.section-top .badge{background:#2f6f95;border-color:#245a7a}'
       '.review-decision.ehd-roadmap .proposed-label{color:#245a7a}.ehd-where{list-style:none;padding:0;margin:8px 0 0}.ehd-where li{margin:0 0 6px}'
       '.ehd-when{display:block;color:var(--muted);font-size:13px}.ehd-read{font-size:12px;font-weight:700;color:var(--teal);margin:0}'
       '.ehd-read.ehd-abstract{color:var(--amber)}.ehd-locator{display:block;color:var(--muted);font-size:12px;margin:-6px 0 6px}'
       '.ehd-index{width:100%;border-collapse:collapse;background:var(--paper);font-size:14px;margin:10px 0 6px}'
       '.ehd-index th,.ehd-index td{text-align:left;padding:9px 12px;border:1px solid var(--line);vertical-align:top}'
       '.ehd-index th{background:#edf4f5;width:22%}.ehd-index a{display:inline-block;margin:0 14px 4px 0}.ehd-index small{display:block;color:var(--muted)}'
       '.ehd-na{background:var(--paper);border:1px solid var(--line);border-radius:6px;padding:14px 18px;margin:12px 0}'
       '@media(max-width:700px){.ehd-index th{width:auto}.ehd-index th,.ehd-index td{display:block;border-top:none}}')

out = ['<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
       '<meta name="robots" content="noindex"><title>Previously treated extrahepatic disease | Memorial Hermann HPB Oncology</title>'
       f'<link rel="stylesheet" href="{BASE}assets/evidence-tools.css?v=20261024-integrated-high-risk">'
       f'<link rel="stylesheet" href="{BASE}assets/portal-navigation.css"><script src="{BASE}assets/portal-navigation.js?v={KEY}" defer></script>'
       f'<style>{css}</style></head><body><main class="evidence-wrap" id="ehd-positions">',
       '<header class="tool-hero"><p class="eyebrow">Transplant pathways and cancer roadmaps · proposed positions</p>'
       '<h1>Previously treated extrahepatic disease</h1>'
       '<p>One question per tumor and setting: may a patient whose extrahepatic disease has been treated and has responded enter a transplant route, '
       'or proceed to liver-directed surgery on a cancer roadmap? Each question has a proposed position, rules, the evidence and what would change the answer.</p></header>',
       '<div class="review-notice"><strong>Proposed for multidisciplinary review. Nothing is activated.</strong>'
       'These positions open no eligibility rule, allocation route, MELD exception request or study. Standard pathway criteria and allocation rules still apply.</div>',
       f'<p class="ehd-count">{len(qs)} questions · {nlines} study lines · {nfull} read in full · {nabs} abstract only (full text pending; positions will be revised when read).</p>',
       '<table class="ehd-index"><caption class="eyebrow" style="text-align:left;padding:6px 0">Questions by tumor</caption>']
for t in tumors:
    cells = []
    for q in qs:
        if q['tumor'] != t: continue
        kind = 'Transplant' if q['setting'] == 'transplant' else 'Roadmap'
        cells.append(f'<a href="#{e(q["id"])}">{kind} · {e(q["id"])}<small>{e(q["status"])}</small></a>')
    out.append(f'<tr><th scope="row">{e(t)}</th><td>{"".join(cells)}</td></tr>')
out.append('<tr><th scope="row">Not applicable</th><td>' + ''.join(f'<a href="#na-{e(n["id"])}">{e(n["tumor"])}</a>' for n in data['not_applicable']) + '</td></tr></table>')

for q in qs:
    t = q['setting'] == 'transplant'
    out.append(f'<section class="review-decision {"ehd-transplant" if t else "ehd-roadmap"}" id="{e(q["id"])}" data-ehd-question="{e(q["id"])}">'
               f'<div class="section-top"><span class="badge">{"Transplant pathway" if t else "Cancer roadmap"} · {e(q["tumor"])}</span>'
               f'<span class="proposed-label">{e(label(q["status"]))}</span></div>'
               f'<h2>{e(q["id"])} · {e(q["title"])}</h2>'
               f'<p class="ehd-ask">{e(q["question"])}</p>'
               f'<h3>Proposed position</h3><p class="ehd-position">{e(q["position"])}</p>'
               '<h3>Proposed rules</h3><ul>' + ''.join(f'<li>{e(r)}</li>' for r in q['rules']) + '</ul>'
               f'<h3>Where this applies</h3>{where(q)}'
               f'<h3>Why</h3><p>{e(q["why"])}</p>'
               f'<details><summary>Evidence: {len(q["evidence"])} sources · {q["read_full"]} read in full · {q["read_abstract"]} abstract only</summary>'
               + ''.join(study(s) for s in q['evidence']) + '</details>'
               f'<h3>Against, or uncertain</h3><p>{e(q["counter"])}</p>'
               f'<p><b>Certainty.</b> {e(q["certainty"])}</p>'
               f'<p class="next-step"><b>What would change the answer.</b> {e(q["change"])}</p></section>')

out.append('<h2 id="not-applicable">Not applicable</h2>')
for n in data['not_applicable']:
    refs = ' · '.join(f'{e(S[k]["short"])}' + (f' ({source_links(k)})' if source_links(k) else '') for k in n.get('evidence', []))
    out.append(f'<div class="ehd-na" id="na-{e(n["id"])}"><b>{e(n["tumor"])}.</b> {e(n["position"])}' + (f'<small class="citation">{refs}</small>' if refs else '') + '</div>')

out.append(f'<footer class="evidence-footer">Prepared {e(data["prepared"])} (Claude.ai) for Hao Liu. No institutional approval or external-analyst consensus is implied. '
           'PMIDs and abstract quotations were re-checked against PubMed, and every study line was re-checked against its full text or abstract by an independent check. TMC library links need a Texas Medical Center library sign-in; '
           'licensed PDFs stay in the private depot.</footer></main></body></html>')
dest = ROOT / 'extrahepatic-disease/index.html'
dest.parent.mkdir(exist_ok=True)
dest.write_text(''.join(out) + '\n')
print(f'written {dest.relative_to(ROOT)}: {len(qs)} questions, {nlines} study lines, '
      f'{sum(len(v) for v in decisions.values())} roadmap decisions')
