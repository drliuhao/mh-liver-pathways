"""Browser check of the transplant pathway layout (requires Python Playwright and a local server).

usage: python3 tools/test_transplant_workspace_browser.py [base-url]

Default view, every decision of the seven transplant pathways, desktop: the decision is one card; the
strip shows the pathway phases; the middle column lists every possible result of the decision as a
roadmap option (grouped by kind), with its title and action verbatim from the page's protocol data, its
criteria and its sources (one matrix-style line per source, studies with their result); reasons to
reassess and the high-risk reviews that cover the decision are listed; the step-by-step panels are
hidden. A next-step link in an option moves to that decision. The optional "Record findings step by
step" mode still records a finding and shows its result. Phone: no horizontal overflow. No page errors.
"""
import asyncio, json, sys
from playwright.async_api import async_playwright

BASE = sys.argv[1] if len(sys.argv) > 1 else 'http://127.0.0.1:8884/mh-liver-pathways/'
SLUGS = ['hcc', 'pcca', 'icca', 'crlm', 'nelm', 'hehe', 'hca']
VIEW = """()=>{const d=document.querySelector('.decision.dw-protocol');if(!d)return {missing:true};
 const j=JSON.parse(document.getElementById('protocol-data').textContent);const id=d.querySelector('.permalink').getAttribute('href').slice(1);
 const step=j.pathway.steps.find(s=>s.id===id);const m=d.querySelector('.dw-criteria');const vis=n=>!!n&&n.getClientRects().length>0;
 const opts=[...m.querySelectorAll('.tw-options .tw-option:not(.tw-k-risk)')];
 const reviews=(j.high_risk?.pathways?.[j.pathway.slug]?.reviews||[]).filter(r=>(r.steps||[]).includes(id)).length;
 const refs=b=>{const out=[];const walk=a=>(a||[]).forEach(x=>{out.push(...(x.refs||[]));walk(x.children);});walk(b.criteria);out.push(...(b.refs||[]));return [...new Set(out)].filter(r=>j.sources[r]).length};
 return {card:d.classList.contains('tw-decision'),phases:document.querySelectorAll('.tw-phase').length,journey:j.journeys[j.pathway.slug].length,
  hiddenOld:['.tw-findings','.tw-criteria','.tw-outcome'].every(s=>!vis(m.querySelector(s))),shown:vis(m.querySelector('.tw-options')),
  titles:opts.map(o=>o.querySelector('.tw-option-title').textContent),want:step.branches.map(b=>b.title),
  actions:opts.map(o=>o.querySelector('.tw-option-action')?.textContent||''),wantActions:step.branches.map(b=>b.action||''),
  kinds:opts.map(o=>[...o.classList].find(c=>c.startsWith('tw-k-')).slice(5)),wantKinds:step.branches.map(b=>b.kind),
  evidence:opts.map(o=>o.querySelectorAll('.ct-evidence .ct-ev-row').length),wantEvidence:step.branches.map(refs),
  noResult:[...m.querySelectorAll('.tw-options .ct-ev-row,.tw-static-criteria .ct-ev-row')].filter(li=>li.querySelector('.ct-pm')&&!li.querySelector('.ct-ev-result')).length,
  stops:m.querySelectorAll('.tw-k-reassess li').length,wantStops:step.stops.length,
  risk:m.querySelectorAll('.tw-options .tw-option.tw-k-risk').length,wantRisk:reviews,
  order:[...m.children].filter(vis).map(c=>c.id||c.className.split(' ')[0])}}"""

def check(where, r, failures):
    if r.get('missing'):
        failures.append(f'{where}: no decision'); return
    if not r['card'] or r['phases'] != r['journey']:
        failures.append(f'{where}: card {r["card"]}, phases {r["phases"]}/{r["journey"]}')
    if not r['shown'] or not r['hiddenOld']:
        failures.append(f'{where}: options shown {r["shown"]}, step-by-step panels hidden {r["hiddenOld"]}')
    # Options are grouped by kind, so compare as multisets of (kind, title, action).
    got = sorted(zip(r['kinds'], r['titles'], r['actions'], r['evidence']))
    want = sorted(zip(r['wantKinds'], r['want'], r['wantActions'], r['wantEvidence']))
    if got != want:
        failures.append(f'{where}: options differ from protocol data\n  got  {got}\n  want {want}')
    if r['noResult']:
        failures.append(f'{where}: {r["noResult"]} study lines without a result')
    if r['stops'] != r['wantStops'] or r['risk'] != r['wantRisk']:
        failures.append(f'{where}: reassess {r["stops"]}/{r["wantStops"]}, high-risk {r["risk"]}/{r["wantRisk"]}')
    seq = [x for x in r['order'] if x in ('tw-static-criteria', 'tw-options', 'outcome-evidence')]
    if 'tw-options' not in seq or seq != sorted(seq, key=['tw-static-criteria', 'tw-options', 'outcome-evidence'].index):
        failures.append(f'{where}: middle column order {r["order"]}')

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
            steps = await page.evaluate("()=>JSON.parse(document.getElementById('protocol-data').textContent).pathway.steps.map(s=>s.id)")
            for step in steps:
                await page.evaluate(f"()=>{{location.hash='#{step}'}}")
                await page.wait_for_timeout(450)
                check(f'{slug}/{step}', await page.evaluate(VIEW), failures)
                views += 1
            # A next-step link inside an option still moves to its decision.
            await page.goto(BASE + f'transplant/{slug}/', wait_until='networkidle')
            await page.wait_for_timeout(500)
            moved = await page.evaluate("""async()=>{const here=document.querySelector('.decision .permalink').getAttribute('href').slice(1);
              const b=[...document.querySelectorAll('.tw-options .tw-next .route-button[data-step]')].find(x=>x.dataset.step!==here);if(!b)return null;
              b.click();await new Promise(r=>setTimeout(r,600));return [b.dataset.step,document.querySelector('.decision .permalink').getAttribute('href').slice(1)]}""")
            if moved:
                if moved[0] != moved[1]:
                    failures.append(f'{slug}: next-step link to {moved[0]} landed on {moved[1]}')
                else:
                    moves += 1
            # Optional step-by-step mode still records a finding and shows its result.
            r = await page.evaluate("""async()=>{location.hash='#'+JSON.parse(document.getElementById('protocol-data').textContent).pathway.steps[0].id;await new Promise(r=>setTimeout(r,400));
              document.querySelector('.tw-mode-button').click();await new Promise(r=>setTimeout(r,300));
              const s=document.querySelector('#layer-current select');const visible=!!s&&s.getClientRects().length>0;
              s.value=[...s.options].find(o=>o.value&&o.value!=='unknown').value;s.dispatchEvent(new Event('change',{bubbles:true}));
              await new Promise(r=>setTimeout(r,200));document.querySelector('.layer-apply').click();await new Promise(r=>setTimeout(r,600));
              const shown=[...document.querySelectorAll('#current-result>.branch')].some(n=>n.getClientRects().length>0);
              document.querySelector('.tw-mode-button').click();await new Promise(r=>setTimeout(r,200));
              return {visible,shown,back:!document.documentElement.classList.contains('tw-interactive')}}""")
            if not (r['visible'] and r['shown'] and r['back']):
                failures.append(f'{slug}: step-by-step mode {r}')
        phone = await browser.new_page(viewport={'width': 390, 'height': 844})
        phone.on('pageerror', lambda e: errors.append(str(e)))
        for slug in SLUGS:
            await phone.goto(BASE + f'transplant/{slug}/', wait_until='networkidle')
            await phone.wait_for_timeout(500)
            await phone.evaluate("()=>document.querySelectorAll('.tw-options .ct-peer,.tw-static-criteria .ct-peer').forEach(b=>b.click())")
            await phone.wait_for_timeout(200)
            overflow = await phone.evaluate('()=>document.documentElement.scrollWidth-innerWidth')
            if overflow > 0:
                failures.append(f'phone {slug}: horizontal overflow {overflow}px')
        await browser.close()
    failures += [f'page error: {e}' for e in errors]
    assert not failures, '\n'.join(failures[:30])
    print(f'PASS: {views} transplant decisions show every possible result as roadmap-style options matching the protocol data '
          f'(titles, actions, kinds, sources, reasons to reassess, high-risk reviews); {moves} next-step links moved correctly; '
          f'step-by-step mode works on all 7 pathways; no phone overflow or page errors.')

asyncio.run(main())
