"""Browser check of the transplant pathway layout (requires Python Playwright and a local server).

usage: python3 tools/test_transplant_workspace_browser.py [base-url]
Every decision of the seven transplant pathways, on desktop: the decision is one card; the middle
column reads findings → criteria → result group (result, reasons to reassess, other results) →
outcome evidence; the strip shows the pathway phases and every decision button; recording the first
finding still produces a result and its next-step link still moves to the next decision. Phone: no
horizontal overflow. No page errors.
"""
import asyncio, sys
from playwright.async_api import async_playwright

BASE = sys.argv[1] if len(sys.argv) > 1 else 'http://127.0.0.1:8884/mh-liver-pathways/'
SLUGS = ['hcc', 'pcca', 'icca', 'crlm', 'nelm', 'hehe', 'hca']
LAYOUT = """()=>{const d=document.querySelector('.decision.dw-protocol');if(!d)return {missing:true};
 const m=d.querySelector('.dw-criteria');const order=[...m.children].map(c=>c.id||c.className.split(' ')[0]);
 const g=m.querySelector(':scope>.tw-outcome');const inG=g?[...g.children].map(c=>c.id||c.className.split(' ')[0]):[];
 const j=JSON.parse(document.getElementById('protocol-data').textContent);
 return {card:d.classList.contains('tw-decision'),order,inG,kind:g?.dataset.kind,
  phases:document.querySelectorAll('.tw-phase').length,journey:j.journeys[j.pathway.slug].length,
  buttons:document.querySelectorAll('.dw-protocol-topic').length,stops:d.querySelectorAll('.stops').length,
  select:!!d.querySelector('#layer-current select'),result:!!d.querySelector('#current-result>.branch')}}"""

def check(slug, step, r, failures, fresh=True):
    where = f'{slug}/{step}'
    if r.get('missing'):
        failures.append(f'{where}: no decision'); return
    if not r['card']:
        failures.append(f'{where}: decision is not a card')
    seq = [x for x in r['order'] if x in ('tw-findings', 'tw-criteria', 'tw-outcome', 'outcome-evidence')]
    want = ['tw-findings', 'tw-criteria', 'tw-outcome'] + (['outcome-evidence'] if 'outcome-evidence' in r['order'] else [])
    if seq != want:
        failures.append(f'{where}: middle column order {r["order"]}')
    g = [x for x in r['inG'] if x in ('decision-results', 'stops', 'other-results')]
    if not g or g[0] != 'decision-results' or (r['stops'] and 'stops' not in g) or g != sorted(g, key=['decision-results', 'stops', 'other-results'].index):
        failures.append(f'{where}: result group {r["inG"]}')
    if r['phases'] != r['journey']:
        failures.append(f'{where}: {r["phases"]} phase groups for {r["journey"]} journey phases')
    if (fresh and not r['select']) or not r['result']:
        failures.append(f'{where}: finding selector or result missing')

async def main():
    failures, views, moves = [], 0, 0
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page(viewport={'width': 1280, 'height': 900})
        errors = []
        page.on('pageerror', lambda e: errors.append(str(e)))
        for slug in SLUGS:
            await page.goto(BASE + f'transplant/{slug}/', wait_until='networkidle')
            await page.wait_for_timeout(500)
            steps = await page.evaluate("()=>[...document.querySelectorAll('.dw-protocol-topic')].map(b=>b.dataset.step)")
            for step in steps:
                await page.evaluate(f"()=>document.querySelector('.dw-protocol-topic[data-step=\"{step}\"]').click()")
                await page.wait_for_timeout(450)
                r = await page.evaluate(LAYOUT)
                check(slug, step, r, failures)
                views += 1
            # Recording a finding still works through the regrouped column, and its next step still routes.
            await page.goto(BASE + f'transplant/{slug}/', wait_until='networkidle')
            await page.wait_for_timeout(500)
            before = await page.evaluate("()=>document.querySelector('.decision .permalink')?.getAttribute('href')")
            await page.evaluate("""async()=>{const s=document.querySelector('#layer-current select');s.value=[...s.options].find(o=>o.value&&o.value!=='unknown').value;
              s.dispatchEvent(new Event('change',{bubbles:true}));await new Promise(r=>setTimeout(r,200));document.querySelector('.layer-apply').click();}""")
            await page.wait_for_timeout(700)
            r = await page.evaluate(LAYOUT)
            check(slug, 'after-finding', r, failures, fresh=False)
            link = await page.evaluate("""()=>{const here=(document.querySelector('.decision .permalink')?.getAttribute('href')||'').slice(1);
              const a=[...document.querySelectorAll('#current-result .route-button[data-step]')].find(x=>x.dataset.step!==here);if(!a)return null;a.click();return a.dataset.step}""")
            if link:
                await page.wait_for_timeout(700)
                after = await page.evaluate("()=>document.querySelector('.decision .permalink')?.getAttribute('href')")
                if after == before:
                    failures.append(f'{slug}: next-step link did not move from {before}')
                else:
                    moves += 1
                r = await page.evaluate(LAYOUT)
                check(slug, 'after-move', r, failures, fresh=False)
        phone = await browser.new_page(viewport={'width': 390, 'height': 844})
        phone.on('pageerror', lambda e: errors.append(str(e)))
        for slug in SLUGS:
            await phone.goto(BASE + f'transplant/{slug}/', wait_until='networkidle')
            await phone.wait_for_timeout(500)
            overflow = await phone.evaluate('()=>document.documentElement.scrollWidth-innerWidth')
            if overflow > 0:
                failures.append(f'phone {slug}: horizontal overflow {overflow}px')
        await browser.close()
    failures += [f'page error: {e}' for e in errors]
    assert not failures, '\n'.join(failures[:40])
    print(f'PASS: {views} transplant decisions laid out as one card with findings → criteria → result group → evidence and phase-labelled strips; '
          f'finding recorded on all 7 pathways with {moves} next-step moves intact; no phone overflow or page errors.')

asyncio.run(main())
