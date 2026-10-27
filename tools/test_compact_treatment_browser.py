"""Browser check of the compact treatment/evidence layer (requires Python Playwright and a local server).

usage: python3 tools/test_compact_treatment_browser.py [base-url]
       default base-url: http://127.0.0.1:8884/mh-liver-pathways/
Checks all 103 roadmap topics, the seven high-risk protocol pages and the systemic matrix on
desktop, plus selected phone layouts: every option enhanced, panels closed initially, every
mapped option-tied result rendered with its numbers present in that option's own text, study
summaries compacted with results visible, no page errors and no horizontal overflow at 390 px.
"""
import asyncio, json, re, sys
from pathlib import Path
from playwright.async_api import async_playwright

ROOT = Path(__file__).resolve().parents[1]
BASE = sys.argv[1] if len(sys.argv) > 1 else 'http://127.0.0.1:8884/mh-liver-pathways/'
ROADS = ['hcc', 'crlm', 'icca', 'hilar', 'nelm', 'chcca', 'adenoma', 'incidental', 'pdac', 'pnet', 'pcyst', 'ampullary']
SLUGS = ['hcc', 'pcca', 'icca', 'crlm', 'nelm', 'hehe', 'hca']
NUM = re.compile(r'(?<![A-Za-z0-9.])\d+(?:[.,·]\d+)*')
nums = lambda s: {m.replace(',', '').replace('·', '.') for m in NUM.findall(s or '')}
mapping = json.loads((ROOT / 'tools/compact_evidence_source.json').read_text())['options']
expected_rows = {k: len(v['rows']) for k, v in mapping.items() if v['rows']}
reference_links = json.loads((ROOT / 'tools/compact_evidence_source.json').read_text())['reference_links']
OPTIONS = """()=>[...document.querySelectorAll('#answer .ci-treatment-criteria')].map(tc=>{const row=tc.previousElementSibling,ev=tc.querySelector('.ct-evidence');
 return {ready:tc.dataset.ctReady==='true',key:tc.dataset.ctOption,peers:row&&row.matches('.ct-peers')?row.querySelectorAll('.ct-peer').length:0,
 panels:tc.querySelectorAll(':scope>details').length,open:tc.querySelectorAll(':scope>details[open]').length,
 text:CompactTreatment.optionText(tc),groups:ev?ev.querySelectorAll('.ct-ref').length:0,tied:ev?[...ev.querySelectorAll('.ct-ev-tied')].map(li=>li.querySelector('.ct-ev-result').textContent+' '+(li.querySelector('.ct-ev-caution')?.textContent||'')):[]}})"""

async def topic(page, road, key):
    await page.evaluate(f"()=>{{location.hash='#decision-{key}'}}")
    for _ in range(60):
        if await page.evaluate("()=>document.querySelector('#answer')?.dataset.workspaceKey") == f'{road}/{key}':
            break
        await page.wait_for_timeout(100)
    await page.wait_for_timeout(250)

async def main():
    failures, seen, groups_seen, options, tied = [], {}, {}, 0, 0
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page(viewport={'width': 1280, 'height': 900})
        errors = []
        page.on('pageerror', lambda e: errors.append(str(e)))
        for road in ROADS:
            await page.goto(BASE + road + '/', wait_until='networkidle')
            ids = await page.evaluate("()=>[...new Set([...document.querySelectorAll('button.rf-topic')].map(b=>b.dataset.roadmapDecision))]")
            for key in ids + ids[:1]:  # revisit the first topic: enhancement must survive switching
                await topic(page, road, key)
                for o in await page.evaluate(OPTIONS):
                    options += 1
                    if not o['ready'] or o['peers'] < o['panels']:
                        failures.append(f'{road}/{key}: option not enhanced')
                    if o['open']:
                        failures.append(f'{road}/{key}: panel open initially')
                    seen[o['key']] = len(o['tied'])
                    groups_seen[o['key']] = o['groups']
                    tied += len(o['tied'])
                    for line in o['tied']:
                        missing = nums(line) - nums(o['text'])
                        if missing:
                            failures.append(f"{road}/{key}: numbers {sorted(missing)} not in option text")
        for key, n in expected_rows.items():
            if seen.get(key) != n:
                failures.append(f'{key}: expected {n} option-tied rows, saw {seen.get(key)}')
        for key, links in reference_links.items():
            n = len(links)
            if groups_seen.get(key) != n:
                failures.append(f'{key}: expected {n} treatment-reference groups, saw {groups_seen.get(key)}')
        for slug in SLUGS:
            await page.goto(BASE + f'transplant/high-risk/{slug}/', wait_until='networkidle')
            await page.wait_for_timeout(400)
            r = await page.evaluate("""()=>({studies:document.querySelectorAll('article.hr-study').length,
              ready:document.querySelectorAll('article.hr-study[data-ct-ready]').length,
              results:[...document.querySelectorAll('.ct-study .ct-study-result')].length,
              openPanels:[...document.querySelectorAll('.ct-study-panels>.ct-panel')].filter(p=>!p.hidden).length,
              protocols:document.querySelectorAll('.hr-protocol').length,protocolRows:document.querySelectorAll('.hr-protocol>.ct-protocol-peers').length})""")
            if r['studies'] != r['ready'] or r['results'] != r['studies'] or r['openPanels'] or r['protocols'] != r['protocolRows']:
                failures.append(f'high-risk/{slug}: {r}')
        await page.goto(BASE + 'systemic/?tumor=all', wait_until='networkidle')
        r = await page.evaluate("""()=>{const c=document.querySelector('#crlm-other-targets');const b=c.querySelector('.st-peer-sources');b.click();
          const ok1=document.getElementById(b.getAttribute('aria-controls')).open&&b.getAttribute('aria-expanded')==='true';b.click();
          const chip=c.querySelector('a.pm');chip.click();const target=document.getElementById(chip.hash.slice(1));
          return {ok1,ok2:!!target&&target.closest('details').open,cards:document.querySelectorAll('.regimen-card').length}}""")
        if not (r['ok1'] and r['ok2'] and r['cards'] == 49):
            failures.append(f'systemic: {r}')
        phone = await browser.new_page(viewport={'width': 390, 'height': 844})
        phone.on('pageerror', lambda e: errors.append(str(e)))
        for url in ['icca/#decision-8', 'crlm/#decision-1', 'pcyst/#decision-1', 'transplant/high-risk/hcc/', 'systemic/?tumor=crlm', 'transplant/hcc/#allocation']:
            await phone.goto(BASE + url, wait_until='networkidle')
            await phone.wait_for_timeout(500)
            await phone.evaluate("()=>document.querySelectorAll('.ct-peer,.st-peer').forEach(b=>b.click())")
            await phone.wait_for_timeout(200)
            overflow = await phone.evaluate('()=>document.documentElement.scrollWidth-innerWidth')
            if overflow > 0:
                failures.append(f'phone {url}: horizontal overflow {overflow}px')
        await browser.close()
    failures += [f'page error: {e}' for e in errors]
    assert not failures, '\n'.join(failures[:40])
    print(f'PASS: {options} option views across 103 topics (with a revisit per roadmap); {tied} option-tied results rendered with numbers in their own option text; '
          f'{len(expected_rows)} mapped options and {len(reference_links)} treatment-reference links matched; 7 high-risk pages compacted; systemic peers and PMID anchors work; no phone overflow or page errors.')

asyncio.run(main())
