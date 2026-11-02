"""Reduce exact patches to unique local context while retaining replay order and provenance."""
from pathlib import Path
import json,subprocess
r=Path(__file__).resolve().parents[2];p=r/'tools/clinical_revisions/2026-11-02-liver-roadmap-audit.json';d=json.loads(p.read_text());states={};patches=[]
for e in d['files']:
 f=e['file']
 if f not in states:states[f]=subprocess.check_output(['git','show','30039fe:'+f],cwd=r,text=True)
 text=states[f];old,new=e['old'],e['new'];assert text.count(old)==1,(f,old[:80]);at=text.index(old)
 pre=0
 while pre<min(len(old),len(new)) and old[pre]==new[pre]:pre+=1
 suf=0
 while suf<min(len(old)-pre,len(new)-pre) and old[-1-suf]==new[-1-suf]:suf+=1
 i=at+pre;j=at+len(old)-suf
 value=new[pre:len(new)-suf if suf else len(new)]
 lo=max(0,i-80);hi=min(len(text),j+80)
 while text.count(text[lo:hi])!=1:
  lo=max(0,lo-80);hi=min(len(text),hi+80)
 eo=text[lo:hi];en=text[lo:i]+value+text[j:hi]
 patches.append({**e,'old':eo,'new':en})
 states[f]=text.replace(old,new,1)
for f,t in states.items():assert t==(r/f).read_text(),f
# No protected file mutation; only compact the exact revision records.
d['files']=patches;p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
regs=[{'change_id':f'LIVER-{i+1:03d}','finding_id':e['why'].split('; ')[0],'source_locator':e['why'],'file':e['file'],'old':e['old'],'new':e['new']} for i,e in enumerate(patches)]
(r/'tools/audit_revision/liver_change_register.json').write_text(json.dumps(regs,ensure_ascii=False,indent=2)+'\n')
print('PASS exact baseline replay:',len(patches),'patches in',len(states),'files')
