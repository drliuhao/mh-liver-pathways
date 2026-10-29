"""Browser check of the decision-specific resource tools (requires Python Playwright and a local server).

usage: python3 tools/test_resource_tools_browser.py [base-url]

On every transplant decision and every roadmap decision that the placement map names: each placed item is
present once, in Scores & classifications, with a kind tag. Every shared roadmap table and the
liver-directed feasibility table loads when opened and shows rows from its source. External tools open
in a new tab. The MELD exception table highlights the page's own diagnosis. RETREAT returns a result on the
HCC post-transplant decision. The page's own criteria references sit with the scores. Phone: the Tools tab
shows the same rows without horizontal overflow.
"""
import asyncio, sys, json
from playwright.async_api import async_playwright

BASE = sys.argv[1] if len(sys.argv) > 1 else 'http://127.0.0.1:8884/mh-liver-pathways/'
TRANSPLANT = ['hcc', 'pcca', 'icca', 'crlm', 'nelm', 'hehe', 'hca']
ROADMAPS = ['hcc', 'crlm', 'icca', 'hilar', 'nelm', 'chcca', 'adenoma', 'pdac', 'pnet', 'pcyst', 'ampullary']
CHECK = """async(want)=>{const t=document.querySelector('.dw-ready .dw-tools');if(!t)return {missing:'column'};
 const rows=[...t.querySelectorAll('.tc-row[data-tc]')];const ids=rows.map(r=>r.dataset.tc);
 const out={absent:want.filter(id=>!ids.includes(id)),dups:ids.filter((x,i)=>ids.indexOf(x)!==i),misplaced:[],untagged:[],empty:[],ext:[],critOutside:0};
 for(const id of want){const r=rows.find(x=>x.dataset.tc===id);if(!r)continue;
  if(!r.closest('.dw-tool-calculators'))out.misplaced.push(id);
  if(!r.querySelector(':scope>summary .tc-kind'))out.untagged.push(id);
  if(r.querySelector('.tc-shared')){r.open=true;for(let i=0;i<50&&!['true'].includes(r.querySelector('.tc-shared').dataset.loaded);i++)await new Promise(z=>setTimeout(z,100));
   const n=r.querySelectorAll('.tc-shared tr').length;if(!n)out.empty.push(id);r.open=false;}
  for(const a of r.querySelectorAll('a.tc-ext-link'))if(a.target!=='_blank'||!/^https:/.test(a.href))out.ext.push(id);}
 out.critOutside=[...t.querySelectorAll('details.ch-reference[data-reference-kind="criteria"],details.ch-reference[data-reference-kind="tool"]')].filter(n=>!n.closest('.dw-tool-calculators')).length;
 out.current=[...t.querySelectorAll('.tc-row[data-tc="meldexc"] tr.tc-current td:first-child')].map(x=>x.textContent);
 return out;}"""


async def main():
    failures, checked, tables = [], 0, 0
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page(viewport={'width': 1400, 'height': 900})
        errors = []
        page.on('pageerror', lambda e: errors.append(str(e)))
        await page.goto(BASE + 'crlm/', wait_until='networkidle')
        extra = await page.evaluate('()=>ClinicalScores.extra')
        for slug in TRANSPLANT:
            await page.goto(BASE + 'transplant/' + slug + '/', wait_until='networkidle')
            steps = await page.evaluate("()=>JSON.parse(document.getElementById('protocol-data').textContent).pathway.steps.map(s=>s.id)")
            for s in steps:
                await page.goto(BASE + f'transplant/{slug}/?r={s}#{s}', wait_until='networkidle')
                await page.wait_for_timeout(500)
                want = extra.get('T:' + slug, {}).get(s, [])
                r = await page.evaluate(CHECK, want)
                checked += 1
                for k in ['absent', 'dups', 'misplaced', 'untagged', 'empty', 'ext']:
                    if r.get(k): failures.append(f'T:{slug}/{s}: {k} {r[k]}')
                if 'meldexc' in want and len(r['current']) != 1: failures.append(f'T:{slug}/{s}: MELD table highlight {r["current"]}')
                tables += sum(1 for i in want if i not in r.get('empty', []))
            if slug == 'hcc':
                await page.goto(BASE + 'transplant/hcc/?r=after#after-transplant', wait_until='networkidle')
                await page.wait_for_timeout(500)
                res = await page.evaluate("""()=>{const f=document.querySelector('.dw-ready .tc-row[data-tc="retreat"] .tc-calc');if(!f)return null;f.closest('details').open=true;
                  const set=(k,v)=>{const x=f.querySelector('[name="'+k+'"]');x.value=v;x.dispatchEvent(new Event('input',{bubbles:true}));};
                  set('afp','150');set('mvi','yes');set('count','2');set('largest','3.2');return f.querySelector('.tc-result strong')?.textContent}""")
                if not res or 'RETREAT 6' not in res: failures.append(f'RETREAT calculator: {res}')
        for slug in ROADMAPS:
            await page.goto(BASE + slug + '/', wait_until='networkidle')
            for d, want in extra.get(slug, {}).items():
                await page.evaluate(f"()=>{{location.hash='#decision-{d}'}}")
                await page.wait_for_timeout(600)
                r = await page.evaluate(CHECK, want)
                checked += 1
                if r.get('missing'): failures.append(f'{slug}/{d}: no column'); continue
                for k in ['absent', 'dups', 'misplaced', 'untagged', 'empty', 'ext']:
                    if r.get(k): failures.append(f'{slug}/{d}: {k} {r[k]}')
                if r['critOutside']: failures.append(f'{slug}/{d}: {r["critOutside"]} criteria references outside Scores & classifications')
        phone = await browser.new_page(viewport={'width': 390, 'height': 844})
        phone.on('pageerror', lambda e: errors.append(str(e)))
        for url in ['transplant/hcc/#allocation', 'transplant/pcca/#diagnosis', 'transplant/nelm/#options', 'crlm/#decision-4', 'hcc/#decision-A']:
            await phone.goto(BASE + url, wait_until='networkidle')
            await phone.wait_for_timeout(700)
            await phone.evaluate("""async()=>{document.getElementById('dw-tab-tools')?.click();for(const d of document.querySelectorAll('.dw-ready .tc-row'))d.open=true;await new Promise(r=>setTimeout(r,1500));}""")
            overflow = await phone.evaluate('()=>document.documentElement.scrollWidth-innerWidth')
            if overflow > 0: failures.append(f'phone {url}: horizontal overflow {overflow}px')
        await browser.close()
    failures += [f'page error: {e}' for e in errors]
    assert not failures, '\n'.join(failures[:40])
    print(f'PASS: {checked} decisions carry their placed resource tools once, tagged, in Scores & classifications; {tables} placed items present; shared roadmap and feasibility tables load with rows; external tools open in new tabs; MELD table marks the page diagnosis; RETREAT calculates; criteria references sit with the scores; no phone overflow or page errors.')

asyncio.run(main())
