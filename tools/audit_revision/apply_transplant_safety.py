from pathlib import Path
import json,copy
ROOT=Path(__file__).resolve().parents[2]
rev={'id':'2026-11-02-transplant-safety','date':'2026-11-02','summary':'Resolve precedence and branch-transition regressions, separate recipient follow-up from pretransplant selection, and finish reviewed source synchronization.','edits':[],'files':[]}
regfile=ROOT/'tools/audit_revision/transplant_change_register.json';reg=json.loads(regfile.read_text());D=json.loads((ROOT/'transplant/assets/content.json').read_text());texts={}
def f(file,old,new,fid,loc):
 s=texts.get(file,(ROOT/file).read_text());assert s.count(old)==1,(file,old[:90],s.count(old));texts[file]=s.replace(old,new,1);rev['files'].append({'file':file,'old':old,'new':new});reg['changes'].append({'finding_id':fid,'source_locator':loc,'files':[file],'old':old,'new':new})
def v(path,new,fid,loc):
 h=D
 for k in path[:-1]:h=h[k]
 old=copy.deepcopy(h[path[-1]]);assert old!=new
 rev['edits'].append({'op':'replace_value','path':path,'old':old,'new':new});h[path[-1]]=copy.deepcopy(new);reg['changes'].append({'finding_id':fid,'source_locator':loc,'files':['transplant/assets/content.json','tools/v12_content_snapshot.json','transplant/*/index.html'],'content_path':path,'old':old,'new':new})
p='transplant/assets/risk-routing.js'
f(p,"const hard=[...stops].reverse().find(s=>s.clinical)||stops[stops.length-1];", "const hard=[...stops].reverse().find(s=>s.clinical&&!s.local)||[...stops].reverse().find(s=>s.clinical)||stops[stops.length-1];",'B08-R7-02,03,05,18','Active clinical exclusion precedes a local expansion-status note; both remain recorded')
f(p,"if(post.has(key))return {options:[],clarify:[],questions:[],guard:null,route:null};", "if(post.has(key)||session.answers[key]?.phase==='after')return {options:[],clarify:[],questions:[],guard:null,route:null,postTransplant:true};",'A2-SH-005; B08-R7-01/10','Explicit recipient context at mixed final decisions; prior selection findings do not substitute for recurrence care. AASLD2023 statement49; disease-specific follow-up references')
# A benign transformation assessment may precede standard-care review; after those checks, do not create a loop.
p=['continuations','hca/transformation','branches','0'];x=copy.deepcopy(D['continuations']['hca/transformation']['branches']['0']);x[0]['detail']='Use this route if the conventional-treatment and exception-route assessments have not been completed.'
x.append({'label':'Continue to final HCA review after the earlier assessments are complete','detail':'Confirm that standard nontransplant options and the specific exception-guidance alternative were assessed; unresolved earlier findings remain a hold.','step':'review','care':None,'url':None});v(p,x,'B08-R7-08','NLRB adenoma alternatives p11; standard-care and exception-route cannot be skipped')
p=['continuations','hca/transformation','branches','1'];x=copy.deepcopy(D['continuations']['hca/transformation']['branches']['1']);x.insert(0,{'label':'If HCC is confirmed, open HCC diagnosis and staging','detail':'Confirm the malignant diagnosis first. Transformation does not itself establish standardized HCC exception eligibility.','step':None,'care':None,'url':'/mh-liver-pathways/transplant/hcc/#diagnosis'});v(p,x,'A2-SH-006; B08-R7-10','HCA assistant source help; NLRB adenoma p11 and HCC policy9.5.I')
# Keep the fixed 46 decisions, but give the five mixed final decisions an explicit clinical phase.
copyfile='assets/contextual-copy.js';copytext=(ROOT/copyfile).read_text()
for slug,step in [('icca','follow-up'),('crlm','transplant'),('nelm','follow-up'),('hehe','follow-up'),('hca','follow-up')]:
 key=slug+'/'+step;c=copy.deepcopy(D['assistants'][key]);refs=c['questions'][0]['refs'];plan=next(q for q in c['questions'] if q['id']=='plan');oldlabel=plan['label'];newlabel='Clinical plan and follow-up responsibilities agreed for this stage of care?';plan['label']=newlabel
 phase={'id':'phase','label':'Is this assessment before or after liver transplantation?','options':[{'value':'before','label':'Before transplantation: final selection and care planning','details':[]},{'value':'after','label':'After transplantation: recipient follow-up','details':[]},{'value':'unknown','label':'Uncertain / not yet assessed','details':[]}],'refs':refs,'help':'Before transplantation, all earlier selection findings remain relevant. After transplantation, assess the recipient, graft, recurrence and ongoing care; a prior selection boundary does not prevent follow-up.','criteria':[]}
 c['questions'].insert(0,phase);c['example']['phase']='before'
 for r in c['rules']:r['when']['phase']='before'
 post=[{'when':{'phase':'after','concern':'concern'},'branch':None,'kind':'hold','title':'Assess the new finding in the transplant recipient','text':'Review recurrence, graft function, immunosuppression and treatment safety with the disease-specific oncology and transplant teams.','refs':refs}, {'when':{'phase':'after','plan':'no'},'branch':None,'kind':'hold','title':'Complete the recipient follow-up plan','text':'Assign surveillance and responsibility for suspected recurrence, graft care and the underlying condition.','refs':refs}, {'when':{'phase':'after','plan':'yes','concern':'none'},'branch':None,'kind':'advance','title':'Continue recipient follow-up','text':'Continue the agreed oncology and transplant follow-up plan. This is a post-transplant care result.','refs':refs}]
 c['rules']=post+c['rules'];v(['assistants',key],c,'A2-SH-005; B08-R7-01/10','Disease-specific source-linked final-step follow-up; AASLD2023 statement49 for post-LT ICI safety')
 onward=copy.deepcopy(D['continuations'][key]);onward['rules']={str(int(i)+3):actions for i,actions in onward['rules'].items()};onward['rules'].update({'0':[{'label':'Evaluate possible recurrence after transplantation','detail':'Use the recipient-specific oncology and transplant assessment.','step':None,'care':'post-transplant-recurrence','url':None}], '1':[{'label':'Open the recipient continuing-care plan','detail':'','step':None,'care':'follow-up','url':None}], '2':[{'label':'Open the recipient continuing-care plan','detail':'','step':None,'care':'follow-up','url':None}]});v(['continuations',key],onward,'A2-SH-005; B08-R7-10','Separate pre-LT eligibility and post-LT care actions')
 # Exact title guard and display label retain the existing source help, rather than silently stale concise copy.
 old='"title": '+json.dumps(oldlabel,ensure_ascii=False)
 new='"title": '+json.dumps(newlabel,ensure_ascii=False)
 # Several original titles may repeat; use the full existing plan entry as unique replacement.
 import re
 pat=re.compile(r'("'+re.escape(key+'/plan')+r'": \{)(.*?)(\n    \})',re.S);m=pat.search(copytext);assert m
 block=m.group(0);newblock=block.replace(old,new);assert block!=newblock
 newblock=re.sub(r'"label": "[^\n]*"', '"label": "Stage-specific plan and follow-up agreed?"',newblock)
 f(copyfile,block,newblock,'A2-SH-005','Exact source-guarded display copy matches revised plan prompt');copytext=copytext.replace(block,newblock)
# Preserve canonical reviewed JSON and runtime copies in the source package.
for name in ['app.js','risk-routing.js','assistant.js','high-risk.js']:
 src='tools/decision_assistant_source/'+name;live='transplant/assets/'+name;old=(ROOT/src).read_text();new=texts.get(live,(ROOT/live).read_text())
 if old!=new:f(src,old,new,'B08-R7-11','Source/runtime synchronization after clinical correction')
p='tools/decision_assistant_source/high_risk_data.json';old=(ROOT/p).read_text();new=json.dumps(D['high_risk'],ensure_ascii=False,indent=2)+'\n'
if old!=new:f(p,old,new,'B08-R7-11; B26-R1-F01','Reviewed current high-risk data; provenance and older baselines retained in git/revision records')
(ROOT/'tools/clinical_revisions'/f"{rev['id']}.json").write_text(json.dumps(rev,ensure_ascii=False,indent=2)+'\n');reg['revision_ids'].append(rev['id']);regfile.write_text(json.dumps(reg,ensure_ascii=False,indent=2)+'\n');print('Prepared',len(rev['files']),'script records',len(rev['edits']),'content edits')
