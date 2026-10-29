"""Browser check of the Tools & resources column and the folded treatment matrices (requires Python Playwright and a local server).

usage: python3 tools/test_tools_column_browser.py [base-url]

Every roadmap decision: the column reads Decision team · Scores & classifications · Treatment resources ·
Decision references · Evidence & documents, in that order, with nothing outside those sections; the
treatment resources link to the same matrices on every decision of a tumor (systemic and liver-directed
wherever the tumor has them); every score row has a kind tag; no duplicate rows. Every calculator returns
a result from example values. The roadmap's treatment matrices are folded and load when opened. The
chip after a guideline or policy source carries no grey type label. Phone: no horizontal overflow.
"""
import asyncio, sys
from playwright.async_api import async_playwright

BASE = sys.argv[1] if len(sys.argv) > 1 else 'http://127.0.0.1:8884/mh-liver-pathways/'
ROADMAPS = {'hcc': 2, 'crlm': 2, 'icca': 2, 'hilar': 2, 'nelm': 2, 'chcca': 1, 'pdac': 1, 'pnet': 1, 'ampullary': 1,
            'adenoma': 0, 'incidental': 0, 'pcyst': 0}
ORDER = ['Scores & classifications', 'Treatment resources', 'Decision references', 'Evidence & documents']
COLUMN = """()=>{const t=document.querySelector('#answer.dw-ready .dw-tools');if(!t)return null;
 const rows=[...t.querySelectorAll('.tc-row')];const ids=rows.map(r=>r.dataset.tc).filter(Boolean);
 return {heads:[...t.querySelectorAll('.tc-section:not([hidden])>h4')].map(h=>h.textContent),
  matrix:[...t.querySelectorAll('.tc-mx-links>a')].map(a=>a.getAttribute('href').replace(/^.*mh-liver-pathways\\//,'')),
  stray:[...t.querySelectorAll('.dw-tool-list>:not(.tc-section)')].length+[...t.querySelectorAll('.dw-tool-list .clinical-button:not(.tc-link):not([data-clinical-calculator])')].length,
  untagged:rows.filter(r=>!r.querySelector(':scope>summary .tc-kind')).length,dups:ids.length-new Set(ids).size,
  calcs:[...t.querySelectorAll('.tc-calc')].map(f=>f.closest('[data-tc]')?.dataset.tc)}}"""
FILL = {
    'child': {'bilirubin': '1.2', 'albumin': '3.6', 'inr': '1.1', 'ascites': '1', 'enceph': '1'},
    'albi': {'bilirubin': '1', 'albumin': '4'},
    'hccburden': {'size1': '3', 'size2': '2', 'spread': 'no'},
    'tbs': {'max': '3', 'n': '4'},
    'recist': {'baseline': '100', 'current': '60', 'gone': 'no', 'nontarget': 'non', 'newLesion': 'no'},
    'mrecist': {'baseline': '100', 'current': '60', 'gone': 'no', 'nontarget': 'non', 'newLesion': 'no'},
    'afpmodel': {'largest': '4', 'number': '2', 'afp': '50'},
    'metroticket': {'afp': '50', 'number': '2', 'largest': '3'},
    'netgrade': {'diff': 'well', 'ki67': '5'},
    'spigelman': {'number': '2', 'size': '2', 'histology': '2', 'dysplasia': '1'},
    'fong': {'node': 'yes', 'dfi': 'no', 'multiple': 'no', 'size': 'no', 'cea': 'no'},
    'oslo': {'size': 'no', 'cea': 'yes', 'interval': 'no', 'progression': 'no'},
}
CALC = """async([id,values])=>{const f=[...document.querySelectorAll('#answer.dw-ready .tc-row[data-tc="'+id+'"] .tc-calc')][0];if(!f)return null;
 const row=f.closest('details');row.open=true;
 for(const [k,v] of Object.entries(values)){const x=f.querySelector('[name="'+k+'"]');if(!x)return 'missing field '+k;if(x.type==='checkbox')x.checked=v;else x.value=v;x.dispatchEvent(new Event('input',{bubbles:true}));}
 await new Promise(r=>setTimeout(r,50));const out=f.querySelector('.tc-result');row.open=false;return out.classList.contains('has-result')?out.querySelector('strong').textContent:'no result: '+out.textContent}"""


async def main():
    failures, decisions, calculators = [], 0, set()
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page(viewport={'width': 1400, 'height': 900})
        errors = []
        page.on('pageerror', lambda e: errors.append(str(e)))
        for slug, n_matrix in ROADMAPS.items():
            await page.goto(BASE + slug + '/', wait_until='networkidle')
            ids = await page.evaluate("s=>Object.keys(window.DecisionWorkspaceData.topics).filter(k=>k.startsWith(s+'/')).map(k=>k.split('/')[1])", slug)
            matrix_sets = set()
            for i in ids:
                await page.evaluate(f"()=>{{location.hash='#decision-{i}'}}")
                await page.wait_for_timeout(700)
                c = await page.evaluate(COLUMN)
                if not c:
                    failures.append(f'{slug}/{i}: no tools column'); continue
                decisions += 1
                if [h for h in c['heads']] != sorted(c['heads'], key=ORDER.index) or 'Evidence & documents' not in c['heads']:
                    failures.append(f'{slug}/{i}: sections {c["heads"]}')
                if len(c['matrix']) != n_matrix or c['stray'] or c['untagged'] or c['dups']:
                    failures.append(f'{slug}/{i}: matrix {c["matrix"]}, stray {c["stray"]}, untagged {c["untagged"]}, duplicates {c["dups"]}')
                matrix_sets.add(tuple(c['matrix']))
                for calc in c['calcs']:
                    if calc in calculators or calc not in FILL:
                        continue
                    r = await page.evaluate(CALC, [calc, FILL[calc]])
                    if not r or r.startswith('no result') or r.startswith('missing'):
                        failures.append(f'{slug}/{i}: calculator {calc}: {r}')
                    else:
                        calculators.add(calc)
            if len(matrix_sets) > 1:
                failures.append(f'{slug}: matrix links differ between decisions {matrix_sets}')
            # Treatment matrices at the foot of the roadmap: folded, and the systemic one loads when opened.
            if n_matrix:
                r = await page.evaluate("""async()=>{const folds=[...document.querySelectorAll('.tc-fold')].filter(d=>!d.closest('.dw-tools'));
                  const open=folds.filter(d=>d.open).length;const sys=folds.find(d=>d.classList.contains('tc-fold-systemic'));if(!sys)return {folds:folds.length,open,rows:-1};
                  sys.open=true;for(let i=0;i<40&&sys.dataset.loaded!=='true';i++)await new Promise(r=>setTimeout(r,100));
                  const rows=sys.querySelectorAll('.tc-mx-list li').length;sys.open=false;return {folds:folds.length,open,rows}}""")
                if r['folds'] != n_matrix or r['open'] or r['rows'] < 1:
                    failures.append(f'{slug}: roadmap matrices {r}')
            # Guideline and policy chips name their source; no grey type label after them.
            r = await page.evaluate("""()=>[...document.querySelectorAll('.refchip[data-ref]+.ct-chip-meta .ct-chip-what')].filter(w=>!w.closest('.ct-chip-meta').querySelector('.ct-pm')&&CompactTreatment.namesItself(w.closest('.ct-chip-meta').previousElementSibling.textContent)).length""")
            if r:
                failures.append(f'{slug}: {r} guideline chips still followed by a type label')
        phone = await browser.new_page(viewport={'width': 390, 'height': 844})
        phone.on('pageerror', lambda e: errors.append(str(e)))
        for slug in ['hcc', 'crlm', 'pnet', 'ampullary']:
            await phone.goto(BASE + slug + '/#decision-' + ('B' if slug == 'hcc' else '1'), wait_until='networkidle')
            await phone.wait_for_timeout(600)
            await phone.evaluate("()=>{document.getElementById('dw-tab-tools')?.click();document.querySelectorAll('#answer .tc-row').forEach(d=>d.open=true)}")
            await phone.wait_for_timeout(300)
            overflow = await phone.evaluate('()=>document.documentElement.scrollWidth-innerWidth')
            if overflow > 0:
                failures.append(f'phone {slug}: horizontal overflow {overflow}px')
        await browser.close()
    failures += [f'page error: {e}' for e in errors]
    missing = set(FILL) - calculators
    assert not failures, '\n'.join(failures[:40])
    print(f'PASS: {decisions} roadmap decisions show one Tools hierarchy with the same matrix links per tumor and tagged, unduplicated rows; '
          f'{len(calculators)} calculators return results ({", ".join(sorted(calculators))}){"; not reached on roadmaps: " + ", ".join(sorted(missing)) if missing else ""}; '
          f'roadmap matrices folded and loading; guideline chips without repeated labels; no phone overflow or page errors.')

asyncio.run(main())
