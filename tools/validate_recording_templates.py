"""Compatibility check: old form URLs now redirect to decision assistants."""
import json
from pathlib import Path
root=Path(__file__).resolve().parents[1]
data=json.loads((root/'transplant/assets/content.json').read_text())
assert len(data['assistants'])==46
folder=root/'transplant/recording-templates'
assert len(list(folder.glob('*--*.html')))==46
assert not any(p.suffix in ('.zip','.js','.css','.md') for p in folder.iterdir())
for key in data['assistants']:
    p,s=key.split('/')
    html=(folder/f'{p}--{s}.html').read_text()
    assert f'content="0;url=/mh-liver-pathways/transplant/{p}/#{s}"' in html
    assert '<form' not in html
print('PASS: 46 retired form URLs redirect to their decision; no recording kits remain. Run node tools/test_decision_assistants.cjs for current logic checks.')
