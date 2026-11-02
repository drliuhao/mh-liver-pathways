import json,os,subprocess,time
from pathlib import Path
R=Path(__file__).resolve().parents[2]
py=str(R.parent/'tmp/website-audit-venv/bin/python')
node='/Users/haoliu/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node'
env=dict(os.environ,PATH=str(Path(node).parent)+os.pathsep+os.environ['PATH'])
results=[]
for p in sorted((R/'tools').glob('test_*')):
 if p.suffix not in ['.py','.cjs'] or 'browser' in p.name:continue
 start=time.monotonic()
 try:
  r=subprocess.run([node if p.suffix=='.cjs' else py,str(p)],cwd=R,env=env,capture_output=True,text=True,timeout=180)
  text=r.stdout+r.stderr;status=r.returncode
 except subprocess.TimeoutExpired as e:status=-1;text='TIMEOUT '+str(e)
 (R/'tools/audit_revision'/('release_'+p.stem+'.log')).write_text(text)
 results.append(dict(test=p.name,status=status,seconds=round(time.monotonic()-start,2)))
 print(('PASS ' if status==0 else 'FAIL ')+p.name,flush=True)
(R/'tools/audit_revision/release_checks.json').write_text(json.dumps(results,indent=2)+'\n')
print(f'{sum(x["status"]==0 for x in results)}/{len(results)} passed')
