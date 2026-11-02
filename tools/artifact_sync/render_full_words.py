"""Render the 26 copied full-content Word outputs with bundled LibreOffice only."""
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

HERE=Path(__file__).resolve().parent
WEB=HERE.parents[1]
WORK=WEB.parent
OUT=WORK/'Artifact_Sync_2026-11-02/.build/word_full_renders'
RENDER=Path('/Users/haoliu/.codex/plugins/cache/openai-primary-runtime/documents/26.1020.11127/skills/documents/render_docx.py')
BINS=Path('/Users/haoliu/.cache/codex-runtimes/codex-primary-runtime/dependencies/bin')
env=os.environ.copy()
env['PATH']=os.pathsep.join([str(Path(sys.executable).parent),str(BINS/'override'),str(BINS/'fallback'),env.get('PATH','')])
env['TMPDIR']='/private/tmp'
manifest=json.loads((HERE/'word_sync_manifest.json').read_text())
inventory=json.loads((HERE/'current_artifact_inventory.json').read_text())
meta={d['source_master']:d for d in inventory['documents']}
mode=sys.argv[1] if len(sys.argv)>1 else 'all'
files=[x for x in manifest if x['status']=='synchronized']
if mode in ['stable','liver']:
    liver={'hcc','pcca','icca','crlm','nelm','hca','chcca'}
    def is_liver(x):
        d=meta[x['source']]
        return d['role']=='roadmap_info' and d['tumor'].lower() in liver
    files=[x for x in files if is_liver(x)==(mode=='liver')]
OUT.mkdir(parents=True,exist_ok=True)
status_path=OUT/'render_status.json'
results=json.loads(status_path.read_text()) if status_path.exists() else []
byfile={x['file']:x for x in results}

def job(item):
    path=Path(item['output']);digest=hashlib.sha256(path.read_bytes()).hexdigest()
    prior=byfile.get(str(path))
    if prior and prior.get('sha256')==digest and prior.get('returncode')==0:
        return prior
    folder=OUT/path.stem
    folder.mkdir(parents=True,exist_ok=True)
    # Remove only this renderer's previous page outputs to prevent stale tail pages.
    for p in folder.glob('page-*.png'):p.unlink()
    with (folder/'render.log').open('w') as log:
        q=subprocess.run([sys.executable,str(RENDER),str(path),'--output_dir',str(folder),'--emit_pdf'],
                         stdout=log,stderr=subprocess.STDOUT,env=env,timeout=900)
    return {'file':str(path),'sha256':digest,'returncode':q.returncode,
            'pages':len(list(folder.glob('page-*.png'))),'folder':str(folder),
            'rendered_utc':datetime.now(timezone.utc).isoformat(),
            'renderer':str(RENDER),'soffice':str(BINS/'override/soffice')}

done=0
with ThreadPoolExecutor(max_workers=2) as pool:
    futures={pool.submit(job,p):p for p in files}
    for f in as_completed(futures):
        try:r=f.result()
        except Exception as exc:r={'file':futures[f]['output'],'error':str(exc)}
        byfile[r['file']]=r;done+=1
        status_path.write_text(json.dumps(list(byfile.values()),indent=2)+'\n')
        print(f'{done}/{len(files)} {Path(r["file"]).name}: {r.get("pages",0)} pages / {r.get("returncode",r.get("error"))}',flush=True)
bad=[r for r in byfile.values() if r.get('returncode')!=0 or not r.get('pages')]
sys.exit(bool(bad))
