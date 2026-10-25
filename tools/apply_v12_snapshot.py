"""Restore the complete V12 evidence payload after a legacy transplant build.

This does not restore JavaScript, new pages or documents; keep those V12 assets.
Run only when V12 is the intended release, not over a later evidence revision.
"""
from pathlib import Path
import json,re

ROOT=Path(__file__).resolve().parents[1]
data=json.loads((ROOT/'tools/v12_content_snapshot.json').read_text())
(ROOT/'transplant/assets/content.json').write_text(json.dumps(data,ensure_ascii=False,indent=2))
count=0
for path in (ROOT/'transplant').rglob('*.html'):
 text=path.read_text()
 match=re.search(r'(<script[^>]*id="protocol-data"[^>]*>)(.*?)(</script>)',text,re.S)
 if not match:continue
 old=json.loads(match.group(2));slug=(old.get('pathway') or {}).get('slug')
 payload={**data,'pathway':next((x for x in data['index'] if x['slug']==slug),None),'mode':old.get('mode')}
 value=json.dumps(payload,ensure_ascii=False).replace('</','<\\/')
 path.write_text(text[:match.start(2)]+value+text[match.end(2):]);count+=1
print('Restored V12 content and',count,'embedded payloads. Run the clinical routing and release tests.')
