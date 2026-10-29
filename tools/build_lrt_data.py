"""Regenerate the standalone LRT page's embedded data from the shared source.

The roadmaps and pathway folds read lrt/matrix.json directly. Older per-roadmap
data/lrt_matrix.json files are retained for historical source audits only.
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
page = ROOT / 'lrt/index.html'
prefix, rest = page.read_text().split('const DATA =', 1)
_, length = json.JSONDecoder().raw_decode(rest.lstrip())
data = json.loads((ROOT / 'lrt/matrix.json').read_text())
page.write_text(prefix + 'const DATA = ' + json.dumps(data, ensure_ascii=False) + rest.lstrip()[length:])
print('LRT page and shared matrix data synchronized.')
