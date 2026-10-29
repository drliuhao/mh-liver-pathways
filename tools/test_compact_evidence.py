"""Guard the concise evidence lines used by the compact treatment layer.

Every number in a study line (label, arms, result, caution) must occur in a quoted passage for that
PMID, and each passage must be verbatim in the site's verified text (roadmap critique bottom lines and
sample descriptions, liver-directed matrix rows, systemic matrix evidence, high-risk study summaries or
outcome cards) or in the team's V15 evidence-summary decks (tools/compact_evidence_ppt_quotes.json, checked
against the decks by tools/check_compact_evidence_ppt.py). The generated asset must match its source.
"""
from pathlib import Path
import glob, json, re

ROOT = Path(__file__).resolve().parents[1]
# Decimal points as printed: '.', Lancet '·' (U+00B7) and BJS '⋅' (U+22C5).
NUM = re.compile(r'(?<![A-Za-z0-9.])\d+(?:[.,·⋅]\d+)*')
norm = lambda s: s.replace(',', '').replace('·', '.').replace('⋅', '.')
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
# Transplant pathway source records (title, locator, note) and the site's bibliographic citations.
for f in glob.glob(str(ROOT / 'transplant/*/index.html')):
    m = re.search(r'<script[^>]*id="protocol-data"[^>]*>(.*?)</script>', Path(f).read_text(), re.S)
    for v in (json.loads(m.group(1)).get('sources', {}).values() if m else []):
        if v.get('pmid'):
            add(v['pmid'], v.get('title'), v.get('locator'), v.get('note'))
for f in glob.glob(str(ROOT / '*/data/pathway.json')):
    for key, ref in json.loads(Path(f).read_text()).get('refs', {}).items():
        if len(ref) > 2:
            add(key, ref[2])
_hcc = (ROOT / 'hcc/index.html').read_text()
_blk = _hcc[_hcc.index('const REF = {') + 12:]
for key, ref in json.loads(_blk[:_blk.index('};') + 1]).items():
    if len(ref) > 2:
        add(key, ref[2])
for pmid, r in json.loads((ROOT / 'systemic/references.json').read_text()).items():
    add(pmid, r.get('title'))
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
for f in glob.glob(str(ROOT / 'transplant/*/index.html')):
    m = re.search(r'<script[^>]*id="protocol-data"[^>]*>(.*?)</script>', Path(f).read_text(), re.S)
    for v in (json.loads(m.group(1)).get('sources', {}).values() if m else []):
        if v.get('pmid'):
            labels.setdefault(str(v['pmid']), []).append(v['short'])
for pmid, r in json.loads((ROOT / 'systemic/references.json').read_text()).items():
    labels.setdefault(pmid, []).append(r.get('trial') or '')

src = json.loads((ROOT / 'tools/compact_evidence_source.json').read_text())
deck = json.loads((ROOT / 'tools/compact_evidence_ppt_quotes.json').read_text())['quotes']
# Short verbatim passages from papers read in full after V15 (each under 15 words; checked against the PDFs by
# tools/check_compact_evidence_fulltext.py).
fulltext = json.loads((ROOT / 'tools/compact_evidence_fulltext_quotes.json').read_text())['quotes']
for pmid, quotes in fulltext.items():
    for q in quotes:
        assert len(q['quote'].split()) < 15 and re.fullmatch(r'[0-9a-f]{64}', q['sha256']), (pmid, q['quote'][:60])
errors, site_q, deck_q, full_q = [], 0, 0, 0
for pmid, s in src['studies'].items():
    assert re.fullmatch(r'\d{6,9}', pmid), pmid
    # PREMIERE-format line: every number in arms, result and caution comes from a quoted passage, and every quoted
    # passage is verbatim in the site's verified text for that PMID or in the team's V15 deck text (checked separately).
    site = '\n'.join(text.get(pmid, []))
    from_deck = {q['quote'] for q in deck.get(pmid, [])}
    from_full = {q['quote'] for q in fulltext.get(pmid, [])}
    pool = set()
    for q in s.get('quotes') or []:
        if q in site:
            site_q += 1
        elif q in from_deck:
            deck_q += 1
        elif q in from_full:
            full_q += 1
        else:
            errors.append(f'{pmid}: quote without provenance: {q[:70]}')
        pool |= nums(q)
    for field in ['label', 'arms', 'result', 'caution']:
        allowed = pool | (nums(' '.join(labels.get(pmid, []))) if field == 'label' else set())
        bad = sorted(nums(s.get(field)) - allowed)
        if bad:
            errors.append(f'{pmid} {field}: {bad}')
    if s.get('design') and s['design'] not in DESIGNS:
        errors.append(f"{pmid} design {s['design']}")
    if not s.get('arms') or not s.get('result'):
        errors.append(f'{pmid}: arms and result are required')
    for field, limit in [('label', 32), ('arms', 70), ('result', 160), ('caution', 110)]:
        if len(s.get(field) or '') > limit:
            errors.append(f'{pmid} {field} longer than {limit}')
assert not errors, '\n'.join(errors[:40])
asset = (ROOT / 'assets/compact-evidence-data.js').read_text()
payload = json.loads(asset[asset.index('=') + 1:].rstrip().rstrip(';'))
assert payload['version'] == src['version'] and set(payload['studies']) == set(src['studies'])
for pmid, s in src['studies'].items():
    pub = payload['studies'][pmid]
    assert (pub.get('a'), pub.get('r'), pub.get('c')) == (s.get('arms'), s.get('result'), s.get('caution') or None), pmid
# Non-PMID sources: category and the opening of the page's own citation text, unchanged.
nonpm_src = {}
for f in glob.glob(str(ROOT / '*/data/pathway.json')):
    nonpm_src[Path(f).parent.parent.name] = json.loads(Path(f).read_text()).get('nonpm', {})
hcc_page = (ROOT / 'hcc/index.html').read_text()
block = hcc_page[hcc_page.index('const NONPM =') + 13:]
nonpm_src['hcc'] = json.loads(block[:block.index('};') + 1])
assert set(payload['nonpm']) == {k for k, v in nonpm_src.items() if v}
for slug, entries in nonpm_src.items():
    for key, (label, cat, cite, *rest) in entries.items():
        pub = payload['nonpm'][slug][key]
        assert pub['l'] == label and pub['c'] == cat and pub['x'].rstrip('…') in cite, (slug, key)
nonpm_n = sum(map(len, payload['nonpm'].values()))

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
print(f"PASS: {len(src['studies'])} PREMIERE-format study lines, every number in a quoted passage ({site_q} quotes on the site, {deck_q} from V15 decks, {full_q} from full texts); "
      f"{nonpm_n} non-PMID sources; "
      f"{rows} option-tied results across {len(published)} options, every number present in that roadmap's clinical text; "
      f"{groups} reviewed source-study groups (numbers traced) on {len(payload['references'])} HCC options; asset in sync.")
