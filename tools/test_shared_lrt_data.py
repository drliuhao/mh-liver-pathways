"""All current LRT views must read the same reviewed source, with complete citations."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
data = json.loads((ROOT / 'lrt/matrix.json').read_text())
page = (ROOT / 'lrt/index.html').read_text()
embedded = json.JSONDecoder().raw_decode(page.split('const DATA =', 1)[1].lstrip())[0]
assert data == embedded, 'Run tools/build_lrt_data.py after editing lrt/matrix.json'
for slug in ['hcc', 'crlm', 'icca', 'nelm']:
    html = (ROOT / slug / 'index.html').read_text()
    assert 'fetch("../lrt/matrix.json?' in html, slug
    assert 'fetch("data/lrt_matrix.json' not in html, slug
    refs = {r['pmid'] for r in json.loads((ROOT / slug / 'data/lrt_refs.json').read_text())}
    pmids = {e[1] for key, cell in data['cells'].items() if key.startswith(slug + '|')
             for role in cell['roles'] for e in role['ev'] if len(e) > 1 and e[1]}
    assert pmids <= refs, (slug, pmids - refs)
loader = (ROOT / 'assets/tools-column.js').read_text()
assert "new URL('lrt/matrix.json?" in loader
assert "fetch(new URL('lrt/index.html'" not in loader
assert len(data['cells']) == 30
assert 'No significant RFS difference' in data['cells']['hcc|abl']['roles'][0]['ev'][0][2]
assert '95% CI 0.69–1.58' in data['cells']['crlm|abl']['roles'][0]['ev'][0][2]
print('PASS: standalone, four roadmaps and pathway matrix folds share 30 reviewed LRT cells; citations complete; trial uncertainty retained.')
