"""Guard the concise evidence lines used by the compact treatment layer.

Every number in a concise line (label, n, result, caution) must occur in that PMID's
verified source text already on the site: roadmap critique bottom lines and sample
descriptions, liver-directed matrix rows, systemic matrix evidence, high-risk study
summaries or outcome cards. The generated asset must match its source.
"""
from pathlib import Path
import glob, json, re

ROOT = Path(__file__).resolve().parents[1]
NUM = re.compile(r'(?<![A-Za-z0-9.])\d+(?:[.,·]\d+)*')
norm = lambda s: s.replace(',', '').replace('·', '.')
nums = lambda s: {norm(m) for m in NUM.findall(s or '')}
DESIGNS = {'RCT', 'Phase 3 RCT', 'Phase 2 RCT', 'Randomized phase 2', 'Single-arm trial', 'Single-arm phase 2', 'Phase 1/2',
           'Prospective cohort', 'Retrospective cohort', 'Registry cohort', 'Cohort', 'Case series', 'Case-control',
           'Meta-analysis', 'Systematic review', 'Pooled analysis', 'Secondary analysis', 'Guideline', 'Consensus', 'Review',
           'Modelling study', 'Diagnostic study', 'Cross-sectional', 'Translational study', 'Other'}

text = {}
def add(pmid, *parts):
    text.setdefault(str(pmid), []).extend(p for p in parts if p)

for f in glob.glob(str(ROOT / '*/data/critique.json')):
    for pmid, c in json.loads(Path(f).read_text()).items():
        add(pmid, c.get('n') if isinstance(c.get('n'), str) else None, c.get('bottom_line'))
def cells(model):
    for cell in model['cells'].values():
        for role in cell['roles']:
            for ev in role['ev']:
                if len(ev) >= 3:
                    add(ev[1], ev[0], ev[2], role['when'])
for f in glob.glob(str(ROOT / '*/data/lrt_matrix.json')):
    cells(json.loads(Path(f).read_text()))
page = (ROOT / 'lrt/index.html').read_text()
cells(json.loads(re.search(r'const DATA = (\{.*?\});\n', page, re.S).group(1)))
matrix = json.loads((ROOT / 'systemic/matrix.json').read_text())
for card in matrix['cards']:
    for pmid in card['refs']:
        add(pmid, card['title'], card['evidence'])
hr = json.loads((ROOT / 'tools/decision_assistant_source/high_risk_data.json').read_text())
def studies():
    for p in hr['pathways'].values():
        for r in p['reviews']:
            yield from r['evidence']['studies']
    for r in hr['readiness']:
        yield from r['evidence']['studies']
for s in studies():
    pmid = hr['sources'].get(s['key'], {}).get('pmid')
    if pmid:
        add(pmid, s['design_population'], s['results'])
prog = json.loads((ROOT / 'tools/prognosis_cards.json').read_text())
for card in prog['cards'].values():
    pmid = prog['sources'].get(card.get('source'), {}).get('pmid')
    if pmid:
        add(pmid, json.dumps(card, ensure_ascii=False))

labels = {}
for f in glob.glob(str(ROOT / '*/data/pathway.json')):
    for key, ref in json.loads(Path(f).read_text()).get('refs', {}).items():
        labels.setdefault(key, []).append(ref[0])
for key, label in re.findall(r'"(\d{6,9})":\["([^"]*)"', (ROOT / 'hcc/index.html').read_text()):
    labels.setdefault(key, []).append(label)

src = json.loads((ROOT / 'tools/compact_evidence_source.json').read_text())
errors, numeric = [], 0
for pmid, s in src['studies'].items():
    assert re.fullmatch(r'\d{6,9}', pmid), pmid
    available = nums(' '.join(text.get(pmid, [])))
    for field in ['label', 'n', 'result', 'caution']:
        allowed = available | (nums(' '.join(labels.get(pmid, []))) if field == 'label' else set())
        bad = sorted(nums(s.get(field)) - allowed)
        if bad:
            errors.append(f'{pmid} {field}: {bad}')
    if s.get('design') and s['design'] not in DESIGNS:
        errors.append(f"{pmid} design {s['design']}")
    if s.get('result') and len(s['result']) > 170:
        errors.append(f'{pmid} result too long')
    if s.get('numeric'):
        numeric += 1
        assert nums(s.get('result')), (pmid, 'numeric line without a number')
    if s.get('result') and not text.get(pmid):
        errors.append(f'{pmid}: concise line without verified source text')
assert not errors, '\n'.join(errors[:40])
asset = (ROOT / 'assets/compact-evidence-data.js').read_text()
payload = json.loads(asset[asset.index('=') + 1:].rstrip().rstrip(';'))
assert payload['version'] == src['version'] and set(payload['studies']) == set(src['studies'])
for pmid, s in src['studies'].items():
    assert 'r' not in payload['studies'][pmid], 'Study-level results are not published'

# Option-tied rows: each number must occur in that roadmap's own clinical text, and the study must be cited there.
road_text = {}
for f in glob.glob(str(ROOT / '*/data/pathway.json')):
    road_text[Path(f).parent.parent.name] = Path(f).read_text()
road_text['hcc'] = (ROOT / 'hcc/index.html').read_text()
rows = 0
for key, option in src['options'].items():
    slug = key.split(':')[0]
    assert slug in road_text, key
    available = nums(road_text[slug])
    for row in option['rows']:
        rows += 1
        assert row['pmid'] in road_text[slug], (key, row['pmid'])
        for field in ['result', 'caution']:
            bad = sorted(nums(row.get(field)) - available)
            assert not bad, (key, row['pmid'], field, bad)
        assert nums(row['result']), (key, 'option row without a number')
        assert len(row['result']) <= 170 and len(row.get('caution') or '') <= 100, key
published = payload['options']
assert set(published) == {k for k, o in src['options'].items() if o['rows']}
for key, option in published.items():
    assert [r['p'] for r in option['rows']] == [r['pmid'] for r in src['options'][key]['rows']]
    assert [r['r'] for r in option['rows']] == [r['result'] for r in src['options'][key]['rows']]
# Reviewed source-study evidence groups: every number traced to the study's verified text or an exact quoted passage.
cards = {c['id']: c for c in matrix['cards']}
def quoted(q):
    assert q['text'] in (ROOT / q['file']).read_text(), ('quote not found', q['file'], q['text'][:60])
    return nums(q['text'])
groups = 0
for gid, g in src['reference_groups'].items():
    pool = set()
    for row in g['rows']:
        allowed = nums(' '.join(t for p in row['pmids'] for t in text.get(p, []))) | (quoted(row['quote']) if row.get('quote') else set())
        pool |= allowed
        for field in ['result', 'caution', 'arms']:
            bad = sorted(nums(row.get(field)) - allowed)
            assert not bad, (gid, row['trial'], field, bad)
        for p in row['pmids']:
            assert re.fullmatch(r'\d{6,9}', p)
    ctx_allowed = pool | (quoted(g['context_quote']) if g.get('context_quote') else set())
    if g['kind'] == 'systemic':
        ctx_allowed |= nums(cards[g['card']]['who'] + ' ' + cards[g['card']]['evidence'])
    bad = sorted(nums(g['context']) - ctx_allowed)
    assert not bad, (gid, 'context', bad)
    groups += 1
assert set(payload['references']) == set(src['reference_links'])
for key, ids in src['reference_links'].items():
    assert key.split(':')[0] == 'hcc' and all(i in src['reference_groups'] for i in ids), key
    assert [g['id'] for g in payload['references'][key]] == ids, key
    for g in payload['references'][key]:
        if g['k'] == 'systemic':
            assert g['l'] == cards[g['card']]['limits'], key
print(f"PASS: {len(src['studies'])} cited studies ({numeric} curated numeric lines traced to verified site text, not published); "
      f"{rows} option-tied results across {len(published)} options, every number present in that roadmap's clinical text; "
      f"{groups} reviewed source-study groups (numbers traced) on {len(payload['references'])} HCC options; asset in sync.")
