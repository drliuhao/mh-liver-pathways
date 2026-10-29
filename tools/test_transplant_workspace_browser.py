"""Browser check of the transplant pathway layout (requires Python Playwright and a local server).

usage: python3 tools/test_transplant_workspace_browser.py [base-url]

Default view, every decision of the seven transplant pathways, desktop: the decision is one card; the
strip shows the pathway phases; the middle column lists every possible result of the decision as a
roadmap option (grouped by kind), with its title and action verbatim from the page's protocol data, its
criteria and its sources (one matrix-style line per source, studies with their result); reasons to
reassess and the high-risk reviews that cover the decision are listed; the step-by-step panels are
hidden. A next-step link in an option moves to that decision. The optional "Record findings step by
step" mode still records a finding and shows its result. The other views of the page (meeting record,
treatment reference, high-risk protocols, evidence library, one high-risk review) do not repeat the decision
tools ("Preview decisions", calculators, term buttons) or the "Return to decision choices" bar; the tab bar
is shown. A discussion link opens the meeting record on the same page at that question, and the retired
alignment and high-risk URLs land on the same page. Phone: no horizontal overflow; the open section's tab
is in view. Tools column: Scores & classifications · Treatment resources · Decision references · Evidence &
documents in that order, both matrix links on every decision of a tumor that has them; treatment decisions end
with the matrices folded beside the decision's evidence, and an opened fold loads its rows. No page errors.
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

SECONDARY = """()=>{const v=n=>!!n&&n.getClientRects().length>0;return {view:document.body.dataset.pathwayView,
 toolbar:v(document.querySelector('.clinical-tool-bar')),layer:v(document.getElementById('layer-current')),
 tabs:[...document.querySelectorAll('.viewbar [role=tab]')].filter(v).length}}"""

TOOLS = """()=>{const t=document.querySelector('.decision .dw-tools');const more=document.querySelector('.decision .tw-more');
 return {heads:[...t.querySelectorAll('.tc-section:not([hidden])>h4')].map(h=>h.textContent),matrixLinks:t.querySelectorAll('.tc-mx-links>a').length,
  stray:[...t.querySelectorAll('.dw-tool-list>:not(.tc-section)')].length,
  folds:more?more.querySelectorAll(':scope>.tc-fold:not(.tw-evidence-fold)').length:0,openFolds:more?more.querySelectorAll(':scope>details[open]').length:0}}"""
SECTION_ORDER = ['Scores & classifications', 'Treatment resources', 'Decision references', 'Evidence & documents']
MATRIX_TUMORS = {'hcc', 'pcca', 'icca', 'crlm', 'nelm'}
TREATMENT_STEPS = {'hcc': ['curative-route', 'treatment', 'waitlist'], 'pcca': ['neoadjuvant'], 'icca': ['therapy', 'stability'],
                   'crlm': ['unresectability', 'control'], 'nelm': ['options', 'exposure']}

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
    failures, views, moves, secondary, redirects, tools_checked, folds_loaded = [], 0, 0, 0, 0, 0, {}
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
            # Tools column: one hierarchy; both matrices wherever the tumor has them. Treatment decisions carry
            # the matrices folded at the bottom, beside the decision's evidence; a fold loads its rows when opened.
            for step in steps:
                await page.evaluate(f"()=>{{location.hash='#{step}'}}")
                await page.wait_for_timeout(350)
                t = await page.evaluate(TOOLS)
                heads = [h for h in t['heads'] if h in SECTION_ORDER]
                if heads != sorted(heads, key=SECTION_ORDER.index) or 'Evidence & documents' not in heads:
                    failures.append(f'{slug}/{step}: tools sections {t["heads"]}')
                if t['matrixLinks'] != (2 if slug in MATRIX_TUMORS else 0) or t['stray']:
                    failures.append(f'{slug}/{step}: matrix links {t["matrixLinks"]}, stray {t["stray"]}')
                if t['folds'] != (2 if step in TREATMENT_STEPS.get(slug, []) else 0) or t['openFolds']:
                    failures.append(f'{slug}/{step}: bottom folds {t["folds"]} open {t["openFolds"]}')
                tools_checked += 1
                if t['folds'] and not folds_loaded.get(slug):
                    rows = await page.evaluate("""async()=>{const f=[...document.querySelectorAll('.decision .tw-more>.tc-fold:not(.tw-evidence-fold)')];
                      f.forEach(d=>d.open=true);for(let i=0;i<40&&f.some(d=>d.dataset.loaded!=='true');i++)await new Promise(r=>setTimeout(r,100));
                      const n=f.map(d=>d.querySelectorAll('.tc-mx-list li').length);f.forEach(d=>d.open=false);return n}""")
                    if not all(rows):
                        failures.append(f'{slug}/{step}: matrix folds empty {rows}')
                    folds_loaded[slug] = True
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
            # Other views of the page: no decision toolbar, no "Return to decision choices" bar, tabs shown.
            hashes = await page.evaluate("""()=>{const j=JSON.parse(document.getElementById('protocol-data').textContent),s=j.pathway.slug;
              const r=(j.high_risk?.pathways?.[s]?.reviews||[])[0];return ['meeting','high-risk','evidence','care-'+j.care[s][0].id].concat(r?['high-risk-'+r.anchor]:[])}""")
            for h in hashes:
                await page.evaluate(f"()=>{{location.hash='#{h}'}}")
                await page.wait_for_timeout(350)
                r = await page.evaluate(SECONDARY)
                if r['toolbar'] or (r['layer'] and r['view'] != 'care') or r['tabs'] < 5 or r['view'] == 'pathway':
                    failures.append(f'{slug}#{h}: {r}')
                else:
                    secondary += 1
            # A discussion link opens the meeting record on this page, at that question.
            await page.goto(BASE + f'transplant/{slug}/', wait_until='networkidle')
            await page.wait_for_timeout(400)
            r = await page.evaluate("""async()=>{const j=JSON.parse(document.getElementById('protocol-data').textContent);
              const step=j.pathway.steps.find(s=>s.issues.length);location.hash='#'+step.id;await new Promise(r=>setTimeout(r,450));
              const links=[...document.querySelectorAll('a.issue-link')];const a=links.find(x=>x.getClientRects().length);if(!a)return {missing:true};
              const id=a.getAttribute('href').slice(9);a.click();await new Promise(r=>setTimeout(r,600));const t=document.getElementById(id),top=t?t.getBoundingClientRect().top:null;
              return {sameDoc:links.every(x=>x.getAttribute('href').startsWith('#meeting-')),view:document.body.dataset.pathwayView,path:location.pathname,found:!!t,inView:top!==null&&top>=0&&top<innerHeight}}""")
            if r.get('missing') or not (r['sameDoc'] and r['view'] == 'meeting' and r['path'].endswith(f'/transplant/{slug}/') and r['found'] and r['inView']):
                failures.append(f'{slug}: discussion link {r}')
            # Retired URLs land on this page.
            issue = await page.evaluate("()=>JSON.parse(document.getElementById('protocol-data').textContent).pathway.issues[0].id")
            for old_url, want_hash, want_view in [(f'transplant/alignment/{slug}.html', '#meeting', 'meeting'),
                                                  (f'transplant/alignment/{slug}/#{issue}', '#meeting-' + issue, 'meeting'),
                                                  (f'transplant/high-risk/{slug}/', '#high-risk', 'high-risk')]:
                await page.goto(BASE + old_url, wait_until='networkidle')
                await page.wait_for_timeout(400)
                r = await page.evaluate("()=>[location.pathname,location.hash,document.body.dataset.pathwayView]")
                if r != [f'/mh-liver-pathways/transplant/{slug}/', want_hash, want_view]:
                    failures.append(f'{old_url} landed on {r}')
                else:
                    redirects += 1
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
            await phone.goto(BASE + f'transplant/{slug}/#high-risk', wait_until='networkidle')
            await phone.wait_for_timeout(500)
            r = await phone.evaluate("""()=>{const bar=document.querySelector('.viewbar'),t=bar.querySelector('[aria-selected="true"]').getBoundingClientRect(),b=bar.getBoundingClientRect();
              return {toolbar:!!document.querySelector('.clinical-tool-bar')?.getClientRects().length,tabInView:t.left>=b.left-1&&t.right<=b.right+1,overflow:document.documentElement.scrollWidth-innerWidth}}""")
            if r['toolbar'] or not r['tabInView'] or r['overflow'] > 0:
                failures.append(f'phone {slug}#high-risk: {r}')
        await browser.close()
    failures += [f'page error: {e}' for e in errors]
    assert not failures, '\n'.join(failures[:30])
    print(f'PASS: {views} transplant decisions show every possible result as roadmap-style options matching the protocol data '
          f'(titles, actions, kinds, sources, reasons to reassess, high-risk reviews); {moves} next-step links moved correctly; '
          f'step-by-step mode works on all 7 pathways; {tools_checked} tools columns in one order with both matrices where the tumor has them, '
          f'treatment decisions with folded matrices that load; {secondary} other views show the tab bar without the decision toolbar; '
          f'discussion links open the meeting record on the same page; {redirects} retired URLs land on the pathway page; '
          f'no phone overflow or page errors.')

asyncio.run(main())
