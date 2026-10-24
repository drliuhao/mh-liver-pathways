"""Accessible browser form renderer; no server submission endpoint."""
from html import escape as e
import json

def label(value):
    return value.replace('_',' ')

def options(values, placeholder='Choose…'):
    return '<option value="">'+e(placeholder)+'</option>'+''.join(f'<option value="{e(v,quote=True)}">{e(label(v))}</option>' for v in values)

def field_html(f, instance):
    key=f['id']; uid=instance+'-'+key.replace('.','-'); control=''
    attrs=f'id="{uid}" data-value data-field-id="{key}"'
    if f['type']=='choice':
        control=f'<select {attrs}>{options(f["choices"])}</select>'
    elif f['type'] in ('number','integer'):
        limits=''.join(f' {k}="{f[k]}"' for k in ('min','max') if k in f)
        control=f'<div class="number-input"><input {attrs} type="number" step="{1 if f["type"]=="integer" else "any"}" inputmode="decimal"{limits}><span>{e(f["unit"])}</span></div>'
    elif f['type']=='date':
        control=f'<div class="date-input"><input {attrs} type="date"><select data-precision aria-label="Date precision: {e(f["label"],quote=True)}"><option value="day">Exact date</option><option value="month">Month known</option><option value="year">Year known</option></select></div>'
    elif key in ('record.record_id','record.assessment_id','decision.signoff') or key.endswith('_id'):
        control=f'<input {attrs} type="text" maxlength="10000">'
    else:
        control=f'<textarea {attrs} rows="2" maxlength="10000"></textarea>'
    helptext=f'<p class="field-help" id="{uid}-help">{e(f["help"])}</p>' if f['help'] else ''
    if helptext:control=control.replace('data-value ',f'aria-describedby="{uid}-help" data-value ',1)
    more=f'''<details class="field-detail"><summary>Notes / missing value</summary><div class="detail-grid"><label>Missing-value status<select data-missing>{options(['pending','not_done','not_applicable','unknown','not_documented'],'Use entered value')}</select></label><label>Notes / other value<textarea data-notes rows="2" maxlength="10000"></textarea></label><label>Different source, if needed<input type="text" data-source maxlength="10000"></label><label>Different observation date, if needed<input type="date" data-observed></label></div></details>'''
    if f.get('signoff'):more=''
    return f'<div class="field" data-field="{key}" data-type="{f["type"]}"><label for="{uid}">{e(f["label"])}</label>{helptext}{control}{more}</div>'

def instance_html(g, num=1):
    instance=g['id']+'-'+str(num)
    fields=''.join(field_html(f,instance) for f in g['fields'] if not f.get('signoff'))
    heading=f'<div class="entry-head"><h3>Entry <span data-instance-number>{num}</span></h3><button type="button" data-remove>Remove entry</button></div>' if g['repeat'] else ''
    return f'''<div class="module-instance" data-instance="{instance}">{heading}<div class="fields-grid">{fields}</div><details class="section-source"><summary>Source and date for this section</summary><div class="detail-grid"><label>Source report / section<input type="text" data-module-source maxlength="10000"></label><label>Observation date<input type="date" data-module-date></label></div></details></div>'''

def render_template(pathway,step,sources,version,groups,checks):
    title=f'{pathway["code"]} · {step["title"]}'
    payload=dict(format='mh-transplant-assessment',format_version=1,template_version=version,pathway_id=pathway['slug'],decision_id=step['id'],title=title,question=step['question'],modules=groups,checklist=checks)
    encoded=json.dumps(payload,ensure_ascii=False).replace('</','<\\/')
    sections=[];templates=[]
    for g in groups:
        templates.append(f'<template id="repeat-{g["id"]}">{instance_html(g)}</template>')
        repeating=f'<button type="button" class="add-entry" data-add="{g["id"]}">+ Add another entry</button>' if g['repeat'] else ''
        opened=' open' if g['id'] in ('record',groups[1]['id'],'decision') else ''
        sections.append(f'<details class="form-section" id="{g["id"]}" data-module="{g["id"]}"{opened}><summary><span>{e(g["title"].replace(" and sign-off",""))}</span><span class="section-count" aria-hidden="true"></span></summary><div class="section-body"><div class="instances">{instance_html(g)}</div>{repeating}</div></details>')
    checkhtml=''.join(f'''<li data-checklist="{n}"><p class="small">{e(x['group'])}</p><p class="check-text">{e(x['text'])}</p><div class="check-fields"><label>Documentation status<select data-check="status">{options(['documented','pending','not_done','not_applicable','unknown'])}</select></label><label>Result / record reference<textarea data-check="result" rows="2" maxlength="10000"></textarea></label><label>Next action<textarea data-check="action" rows="2" maxlength="10000"></textarea></label><label>Responsible clinician<input data-check="owner" type="text" maxlength="10000"></label><label>Due date<input data-check="due" type="date"></label></div></li>''' for n,x in enumerate(checks))
    signoff=''.join(field_html(f,'signoff') for g in groups for f in g['fields'] if f.get('signoff'))
    ref_ids=list(dict.fromkeys(r for x in checks for r in x['refs']))
    reflinks=''.join(f'<li><a href="{e(sources[r]["url"],quote=True)}">{e(sources[r]["short"])}</a> · {e(sources[r]["locator"])}</li>' for r in ref_ids)
    slug=pathway['slug']; stem=slug+'--'+step['id']
    return f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="robots" content="noindex"><meta name="referrer" content="no-referrer"><meta http-equiv="Content-Security-Policy" content="default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self' data:; connect-src 'none'; form-action 'none'; base-uri 'none'; object-src 'none'"><title>{e(title)} · Electronic assessment</title><link rel="stylesheet" href="templates.css?v={version}"><script src="templates.js?v={version}" defer></script></head><body><main>
<nav><a href="../{slug}/#{step['id']}">← Return to this decision</a><a href="index.html">All electronic templates</a></nav>
<p class="eyebrow">Memorial Hermann · Transplant oncology</p><h1>{e(title)}</h1><p class="question">{e(step['question'])}</p><p class="local-note"><b>Electronic assessment · local to this tab.</b> Entries are not sent to a server or saved automatically. Download a JSON file to save and reopen your work in an approved location. Use a coded record ID.</p>
<div class="toolbar"><button type="button" class="primary" data-save>Save / download JSON</button><button type="button" data-load>Reopen saved JSON</button><input type="file" data-import accept="application/json,.json" aria-label="Saved assessment JSON file" hidden><button type="button" data-copy>Copy completed note</button><button type="button" data-csv>Export CSV</button><button type="button" data-md>Download note</button><button type="button" data-print>Print / PDF</button></div>
<div class="statusbar"><span id="save-status">New assessment · not saved</span><span id="completion">No fields entered</span></div><p id="message" role="status" aria-live="polite"></p><div id="errors" role="alert" hidden></div>
<div class="section-controls"><button type="button" data-expand>Expand all sections</button><button type="button" data-collapse>Collapse all sections</button><button type="button" data-new>Start a new blank assessment</button></div>
<form id="assessment" autocomplete="off" novalidate>
<details class="form-section checklist-section"><summary>Information checklist for this decision <span>({len(checks)} items)</span></summary><ol class="checklist">{checkhtml}</ol></details>
{''.join(sections)}
<section class="signoff" id="signoff"><h2>Assessment sign-off</h2><p>One optional review record for the whole assessment. Editing clinical fields returns the review status to Draft.</p><div class="fields-grid">{signoff}</div></section>
</form>
<details class="resources"><summary>Sources, instructions and research files</summary><p>Documentation draft. Field choices record findings and do not determine eligibility or add test requirements. A typed sign-off is not an authenticated EHR signature.</p><ul>{reflinks}</ul><p><a href="{slug}-recording-kit.zip" download>Research dictionary and blank data kit</a> · <a href="{stem}.md" download>Blank Markdown template</a> · <a href="README.md">Instructions and data model</a></p></details>
<footer>Template {version} · Clinical candidacy and allocation eligibility remain separate clinical assessments.</footer>
<pre id="copy-fallback" hidden tabindex="0"></pre><section id="print-note" hidden></section>
{''.join(templates)}<script type="application/json" id="form-schema">{encoded}</script><noscript>This electronic form requires JavaScript. The blank Markdown template remains available in the resources section.</noscript></main></body></html>'''
