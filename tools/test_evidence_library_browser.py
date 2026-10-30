"""Browser check: one evidence-library format, with a one-line summary for every source.

usage: python3 tools/test_evidence_library_browser.py http://127.0.0.1:8885/mh-liver-pathways/

- The 12 roadmap libraries and the 7 transplant pathway libraries draw the same row (assets/roadmap-evidence.js:
  tag, citation, one-line summary, access links, "How far this one goes") with search, category tabs and a count.
- Every row shows its one-line summary (a PubMed paper's compact study line, otherwise the source's line in
  tools/source_summaries.json), including rows drawn before the summary data loaded.
- Transplant pathways: the former card-grid evidence view is gone; the "Evidence library" tab, the right-column link
  and #evidence all open the closing library on the pathway view and bring it into view; search and tabs filter it.
- A roadmap's right-column link still opens its own library.
"""
import asyncio, sys
from playwright.async_api import async_playwright

BASE = sys.argv[1] if len(sys.argv) > 1 else 'http://127.0.0.1:8885/mh-liver-pathways/'
ROADMAPS = ['adenoma', 'ampullary', 'chcca', 'crlm', 'hcc', 'hilar', 'icca', 'incidental', 'nelm', 'pcyst', 'pdac', 'pnet']
PATHWAYS = ['hcc', 'pcca', 'icca', 'crlm', 'nelm', 'hehe', 'hca']
ROWS = '''(sel)=>{const ev=[...document.querySelectorAll(sel+' .ev')];
  const parts=e=>['.evtag','.evcit','.evlinks'].every(c=>e.querySelector(':scope>'+c));
  const sum=e=>{const p=e.querySelector(':scope>.evcit>.evsum');return !!p&&!p.hidden&&p.textContent.trim().length>20};
  return {n:ev.length,format:ev.filter(parts).length,sum:ev.filter(sum).length,
    missing:ev.filter(e=>!sum(e)).slice(0,5).map(e=>e.id),
    tools:!!document.querySelector(sel+' input[type=search]')&&document.querySelectorAll(sel+' .tabs .tab').length>1&&/\\d+ of \\d+ sources/.test(document.querySelector(sel+' .evcount')?.textContent||'')}}'''
OPENED = '''()=>{const s=document.getElementById('pw-evidence');const r=s&&s.getBoundingClientRect();
  return {hash:location.hash,view:document.body.dataset.pathwayView,open:!!s&&!s.querySelector('.pw-body').hidden,
    inView:!!r&&r.top>=0&&r.top<innerHeight*0.5,grid:!!document.querySelector('.evidencegrid,.evidencecard,[data-evidence-search]')}}'''


async def main():
    fail, n_road, n_path = [], 0, 0
    async with async_playwright() as p:
        b = await p.chromium.launch()
        pg = await b.new_page(viewport={'width': 1400, 'height': 900})
        errors = []
        pg.on('pageerror', lambda e: errors.append(str(e)))
        for slug in ROADMAPS:
            await pg.goto(BASE + f'{slug}/', wait_until='networkidle'); await pg.wait_for_timeout(700)
            r = await pg.evaluate(ROWS, '#evidence')
            if not r['n'] or r['format'] != r['n'] or r['sum'] != r['n'] or not r['tools']:
                fail.append(f'{slug} roadmap library: {r}')
            n_road += r['n']
            # The right-column link opens the roadmap's own library.
            link = await pg.query_selector('.dw-tools a[href="#evidence"]')
            if link:
                await link.scroll_into_view_if_needed(); await link.click(); await pg.wait_for_timeout(500)
                if not await pg.evaluate("()=>!document.getElementById('evBody').hidden"):
                    fail.append(f'{slug}: right-column link did not open the library')
        for slug in PATHWAYS:
            await pg.goto(BASE + f'transplant/{slug}/#evidence', wait_until='networkidle'); await pg.wait_for_timeout(800)
            o = await pg.evaluate(OPENED)
            if o != {'hash': '#evidence', 'view': 'pathway', 'open': True, 'inView': True, 'grid': False}:
                fail.append(f'transplant/{slug}#evidence: {o}')
            r = await pg.evaluate(ROWS, '#pw-evidence')
            if not r['n'] or r['format'] != r['n'] or r['sum'] != r['n'] or not r['tools']:
                fail.append(f'transplant/{slug} library: {r}')
            n_path += r['n']
            # Search and category tabs filter the rows.
            f = await pg.evaluate('''async()=>{const i=document.getElementById('pw-ev-search');const all=document.querySelectorAll('#pw-ev-list .ev').length;
              i.value='zz-no-such-source';i.dispatchEvent(new Event('input'));const none=document.querySelectorAll('#pw-ev-list .ev').length;
              i.value='';i.dispatchEvent(new Event('input'));const t=[...document.querySelectorAll('#pw-ev-groups .tab')].find(x=>x.dataset.group==='Studies');t.click();
              const studies=document.querySelectorAll('#pw-ev-list .ev').length;document.querySelector('#pw-ev-groups .tab').click();
              return {all,none,studies,back:document.querySelectorAll('#pw-ev-list .ev').length}}''')
            if not (f['none'] == 0 and 0 < f['studies'] < f['all'] and f['back'] == f['all']):
                fail.append(f'transplant/{slug} search/tabs: {f}')
            # The right-column link on the pathway view, then the tab from another view.
            await pg.goto(BASE + f'transplant/{slug}/', wait_until='networkidle'); await pg.wait_for_timeout(900)
            link = await pg.query_selector('.decision .dw-tools [data-evidence-jump]')
            if not link:
                fail.append(f'transplant/{slug}: no right-column evidence link')
            else:
                await link.scroll_into_view_if_needed(); await link.click(); await pg.wait_for_timeout(600)
                o = await pg.evaluate(OPENED)
                if not (o['view'] == 'pathway' and o['open'] and o['inView'] and o['hash'] == '#evidence'):
                    fail.append(f'transplant/{slug} right-column link: {o}')
            await pg.evaluate("()=>{location.hash='#meeting'}"); await pg.wait_for_timeout(500)
            await pg.click('.viewbar [data-evidence-jump]'); await pg.wait_for_timeout(600)
            o = await pg.evaluate(OPENED)
            if not (o['view'] == 'pathway' and o['open'] and o['inView'] and not o['grid']):
                fail.append(f'transplant/{slug} tab: {o}')
        if errors:
            fail.append('page errors: ' + '; '.join(errors[:3]))
        await b.close()
    if fail:
        print('FAIL:\n- ' + '\n- '.join(fail)); sys.exit(1)
    print(f'PASS: one library format on 12 roadmaps ({n_road} sources) and 7 transplant pathways ({n_path} sources), every row with '
          f'its one-line summary; search, tabs and counts on both; the transplant tab, right-column link and #evidence open the '
          f'closing library (no separate card grid).')

asyncio.run(main())
