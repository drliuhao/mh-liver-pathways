"""Browser check: transplant pathway closing sections and the aligned shared top bar.

usage: python3 tools/test_pathway_sections_browser.py http://127.0.0.1:8885/mh-liver-pathways/

- Each of the 7 pathway pages ends with the four roadmap-style sections, in order, closed until Show; a question link
  opens the meeting record (and the sections leave that view); the high-risk view keeps them.
- Roadmap pages keep their four sections with one heading style (Questions for consensus included).
- The shared top bar: items vertically centred within 1 px, edges on the page's content column, no inset.
"""
import asyncio, sys
from playwright.async_api import async_playwright

BASE = sys.argv[1] if len(sys.argv) > 1 else 'http://127.0.0.1:8885/mh-liver-pathways/'
TITLES = ['Practice choices with limited evidence', 'Questions for consensus', 'Team responsibilities and quality monitoring', 'Evidence library']
NAV = '''()=>{const n=document.querySelector('nav.shared-portal-nav');const r=n.getBoundingClientRect();
const mids=[...n.querySelectorAll(':scope>a,:scope>details>summary')].filter(e=>e.offsetParent).map(el=>{const g=document.createRange();g.selectNodeContents(el);const t=g.getBoundingClientRect();return (t.top+t.bottom)/2});
const a=document.querySelector('.topin')||document.querySelector('#app header.top')||document.querySelector('body>main,body>.wrap,#app main');const cs=getComputedStyle(a),ar=a.getBoundingClientRect();
const first=n.querySelector(':scope>a').getBoundingClientRect().left;return {top:r.top+window.scrollY,left:r.left,width:r.width,vw:document.documentElement.clientWidth,spread:Math.max(...mids)-Math.min(...mids),first,anchor:ar.left+parseFloat(cs.paddingLeft)}}'''


async def main():
    fail = []
    async with async_playwright() as p:
        b = await p.chromium.launch()
        pg = await b.new_page(viewport={'width': 1400, 'height': 900})
        errors = []
        pg.on('pageerror', lambda e: errors.append(str(e)))
        for slug in ['hcc', 'pcca', 'icca', 'crlm', 'nelm', 'hehe', 'hca']:
            await pg.goto(BASE + f'transplant/{slug}/', wait_until='networkidle'); await pg.wait_for_timeout(900)
            r = await pg.evaluate('''()=>({titles:[...document.querySelectorAll('#pathway-closing .pw-head h3')].map(h=>h.textContent),
              hidden:[...document.querySelectorAll('#pathway-closing .pw-body')].every(b=>b.hidden)})''')
            if r['titles'] != TITLES or not r['hidden']:
                fail.append(f'{slug}: sections {r}')
            await pg.evaluate("()=>document.querySelectorAll('#pathway-closing .pw-toggle').forEach(b=>b.click())")
            r = await pg.evaluate('''()=>({open:[...document.querySelectorAll('#pathway-closing .pw-body')].every(b=>!b.hidden),
              rows:document.querySelectorAll('#pw-limited tbody tr').length,owners:document.querySelectorAll('#pw-team tbody tr').length,
              q:document.querySelectorAll('#pw-questions .pw-list a').length,src:document.querySelectorAll('#pw-evidence tbody tr').length})''')
            if not (r['open'] and r['rows'] and r['owners'] and r['q'] and r['src']):
                fail.append(f'{slug}: section bodies {r}')
            await pg.click('#pw-questions .pw-list a'); await pg.wait_for_timeout(500)
            r = await pg.evaluate("()=>({view:document.body.dataset.pathwayView,hash:location.hash,closing:!!document.getElementById('pathway-closing')})")
            if r['view'] != 'meeting' or not r['hash'].startswith('#meeting-') or r['closing']:
                fail.append(f'{slug}: question link {r}')
            await pg.goto(BASE + f'transplant/{slug}/#high-risk', wait_until='networkidle'); await pg.wait_for_timeout(700)
            if not await pg.evaluate("()=>!!document.getElementById('pathway-closing')"):
                fail.append(f'{slug}: sections missing on the high-risk view')
            n = await pg.evaluate(NAV)
            if n['top'] != 0 or n['left'] != 0 or n['width'] != n['vw'] or n['spread'] > 1 or abs(n['first'] - n['anchor']) > 1:
                fail.append(f'transplant/{slug}: top bar {n}')
        for slug in ['ampullary', 'hcc', 'pdac']:
            await pg.goto(BASE + f'{slug}/', wait_until='networkidle'); await pg.wait_for_timeout(1200)
            r = await pg.evaluate('''()=>['honest','questions','ops','evidence'].map(id=>{const h=document.querySelector('#'+id+' .sechead > :first-child');return h?[h.tagName,h.className,h.textContent]:null})''')
            if any(x is None or x[0] != 'H3' or x[1] != 'ch-background-title' for x in r):
                fail.append(f'{slug}: section headings {r}')
            n = await pg.evaluate(NAV)
            if n['top'] != 0 or n['left'] != 0 or n['spread'] > 1 or abs(n['first'] - n['anchor']) > 1:
                fail.append(f'{slug}: top bar {n}')
        for path in ['lrt/', 'systemic/', 'evidence-libraries/', 'transplant/', 'transplant/high-risk/', 'extrahepatic-disease/', 'transplant/waiting/']:
            await pg.goto(BASE + path, wait_until='networkidle'); await pg.wait_for_timeout(800)
            n = await pg.evaluate(NAV)
            if n['top'] != 0 or n['spread'] > 1 or abs(n['first'] - n['anchor']) > 1:
                fail.append(f'{path}: top bar {n}')
        if errors:
            fail.append('page errors: ' + '; '.join(errors[:3]))
        await b.close()
    if fail:
        print('FAIL:\n- ' + '\n- '.join(fail)); sys.exit(1)
    print('PASS: 7 pathway pages end with the four roadmap-style sections (closed until Show; questions open the meeting record; '
          'kept on the high-risk view); roadmap section headings share one style; the top bar is flush, centred within 1 px and '
          'aligned with the content column on 17 pages.')

asyncio.run(main())
