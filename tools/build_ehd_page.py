"""Build extrahepatic-disease/index.html: where each tumor's previously-treated-extrahepatic-disease question is discussed.

usage: python3 tools/build_ehd_page.py

Since the standardized documents (29 October 2026), each question lives once, in its own setting: the roadmap
questions in the roadmap's "Questions for consensus" section, the transplant questions in the pathway's high-risk
view, and both in the tumor's Word files (Documents corner). This page is only an index to those places, so the
positions are not repeated here. Source: tools/ehd_positions.json and assets/documents.json.
"""
import html, json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = '/mh-liver-pathways/'
KEY = '20261030-review1'
data = json.loads((ROOT / 'tools/ehd_positions.json').read_text())
manifest = json.loads((ROOT / 'assets/documents.json').read_text())['tumors']
e = html.escape
TUMOR = {'HCC': 'hcc', 'cHCC–CCA': 'chcca', 'iCCA': 'icca', 'pCCA': 'pcca', 'CRLM': 'crlm', 'NELM': 'nelm', 'pNET': 'pnet', 'HEHE': 'hehe',
         'PDAC': 'pdac', 'Ampullary': 'ampullary'}
NA = {'Hepatocellular adenoma': 'hca', 'Pancreatic cystic lesions': 'pcyst', 'Incidental liver lesions': 'incidental'}
ANCHOR = {'HCC-B5': 'hcc-b5', 'iCCA-B4': 'icca-b4', 'pCCA-B1': 'pcca-b1', 'CRLM-B5': 'crlm-b5', 'NET-B4': 'net-b4', 'HEHE-B2': 'hehe-b2'}

rows = {}
for q in data['questions']:
    key = TUMOR[q['tumor']]
    t = manifest[key]
    if q['setting'] == 'roadmap':
        url = f'{BASE}{t["roadmap"]}/#question-{q["id"]}'
        place = 'Roadmap · Questions for consensus'
    else:
        url = f'{BASE}transplant/{t["transplant"]}/#high-risk-{ANCHOR[q["id"]]}'
        place = 'Pathway · high-risk view'
    rows.setdefault(key, []).append(f'<li><a href="{url}"><b>{e(q["id"])}</b> {e(q["title"])}</a><small>{e(place)} · {e(q["status"])}</small></li>')
for n in data['not_applicable']:
    key = NA[n['tumor']]
    rows.setdefault(key, []).append(f'<li><span><b>Not applicable.</b> {e(n["position"])}</span></li>')

order = ['hcc', 'chcca', 'icca', 'pcca', 'crlm', 'nelm', 'pnet', 'hehe', 'hca', 'pdac', 'ampullary', 'pcyst', 'incidental']
css = ('.ehd-list{list-style:none;padding:0;margin:0}.ehd-list li{padding:9px 0;border-top:1px solid var(--line)}.ehd-list li:first-child{border-top:0}'
       '.ehd-list a{text-decoration:none}.ehd-list a b{margin-right:6px}.ehd-list small{display:block;color:var(--muted);font-size:12.5px;margin-top:2px}'
       '.ehd-tumor{background:var(--paper);border:1px solid var(--line);border-radius:8px;padding:14px 18px;margin:12px 0}.ehd-tumor h2{font:600 20px/1.3 Georgia,serif;margin:0 0 6px}')
out = ['<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
       '<meta name="robots" content="noindex"><title>Previously treated extrahepatic disease | Memorial Hermann HPB Oncology</title>'
       f'<link rel="stylesheet" href="{BASE}assets/evidence-tools.css?v=20261024-integrated-high-risk">'
       f'<link rel="stylesheet" href="{BASE}assets/portal-navigation.css"><script src="{BASE}assets/portal-navigation.js?v={KEY}" defer></script>'
       f'<style>{css}</style></head><body><main class="evidence-wrap" id="ehd-positions">',
       '<header class="tool-hero"><p class="eyebrow">Index · proposed positions</p><h1>Previously treated extrahepatic disease</h1>'
       '<p>Each tumor\'s question is discussed once, in its own setting: the roadmap\'s Questions for consensus, or the pathway\'s '
       'high-risk view. The tumor\'s Word files (Documents, top right on those pages) carry the same questions with every source.</p></header>',
       '<div class="review-notice"><strong>Proposed for multidisciplinary review. Nothing is activated.</strong>'
       'These positions open no eligibility rule, allocation route, MELD exception request or study.</div>']
for key in order:
    if key in rows:
        out.append(f'<section class="ehd-tumor" id="{e(key)}"><h2>{e(manifest[key]["name"])}</h2><ul class="ehd-list">{"".join(rows[key])}</ul></section>')
out.append(f'<footer class="evidence-footer">Prepared {e(data["prepared"])} (Claude.ai) for Hao Liu. Index only; positions, sources and decision fields are in each tumor\'s pages and Word files.</footer></main></body></html>')
dest = ROOT / 'extrahepatic-disease/index.html'
dest.write_text(''.join(out) + '\n')
print(f'written {dest.relative_to(ROOT)}: {sum(len(v) for v in rows.values())} entries for {len(rows)} tumors')
