"""Export the existing transplant review site to the shared GitHub Pages portal.

Clinical data are preserved except for hosting/access URLs. Licensed depot PDFs
are intentionally excluded; each evidence button resolves to its official source.
"""
import argparse
import hashlib
import json
import re
import shutil
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = '/mh-liver-pathways'
TP = BASE + '/transplant'
STAMP = '2026-10-24'
ROADMAPS = [
    ('Liver', 'hcc', 'HCC', 'Hepatocellular carcinoma', 'Diagnosis, liver reserve, locoregional and systemic treatment'),
    ('Liver', 'crlm', 'CRLM', 'Colorectal liver metastases', 'Resectability, conversion treatment, liver-directed options'),
    ('Liver', 'nelm', 'NETLM', 'Neuroendocrine liver metastases', 'Grade, distribution, functional imaging and disease control'),
    ('Liver', 'adenoma', 'HCA', 'Hepatocellular adenoma', 'Subtype, bleeding risk and treatment selection'),
    ('Liver', 'incidental', 'Liver mass', 'Incidental liver mass', 'Characterize the lesion and choose the appropriate work-up'),
    ('Bile duct', 'icca', 'iCCA', 'Intrahepatic cholangiocarcinoma', 'Staging, resectability, molecular profiling and treatment'),
    ('Bile duct', 'hilar', 'pCCA', 'Perihilar cholangiocarcinoma', 'Diagnosis, drainage, staging and curative-intent routes'),
    ('Bile duct', 'chcca', 'cHCC-CCA', 'Combined HCC–cholangiocarcinoma', 'Confirm mixed histology and select a disease-specific route'),
    ('Pancreas', 'pdac', 'PDAC', 'Pancreatic ductal adenocarcinoma', 'Stage, assess operability and sequence treatment'),
    ('Pancreas', 'pnet', 'PNET', 'Pancreatic neuroendocrine tumor', 'Grade, functional status, surgery and systemic therapy'),
    ('Pancreas', 'pcyst', 'Cysts', 'Pancreatic cystic neoplasms', 'Risk features, diagnostic testing and surveillance'),
    ('Pancreas', 'ampullary', 'Ampullary', 'Ampullary tumors', 'Histology, staging, resection and adjuvant treatment'),
]

def transform(value):
    if isinstance(value, dict):
        out = {k: transform(v) for k, v in value.items()}
        if {'short', 'title', 'kind', 'url', 'pdf'} <= value.keys():
            out['pdf'] = value['url']
        return out
    if isinstance(value, list):
        return [transform(v) for v in value]
    if isinstance(value, str) and value.startswith('/'):
        return TP + value
    return value

def card(url, code, name, detail, keywords=''):
    return f'<a class="portal-card" href="{escape(url)}" data-search="{escape((code+" "+name+" "+detail+" "+keywords).lower())}"><span class="portal-code">{escape(code)}</span><span class="portal-card-body"><strong>{escape(name)}</strong><span>{escape(detail)}</span></span><span class="portal-arrow" aria-hidden="true">→</span></a>'

def home(data):
    left = ['<section class="portal-group" id="therapy-matrices"><h3>Therapy matrices</h3>'+card('lrt/', 'Local', 'Liver-directed therapy matrix', 'Compare modalities, clinical evidence, feasibility and contraindications')+card('systemic/', 'Systemic', 'Systemic therapy matrix', 'Treatment setting, biomarkers, key trials, safety and transplant implications', 'chemotherapy immunotherapy targeted HCC pCCA iCCA CRLM NELM')+'</section>']
    for group in ('Liver', 'Bile duct', 'Pancreas'):
        rows = ''.join(card(slug+'/', code, name, detail) for g, slug, code, name, detail in ROADMAPS if g == group)
        left.append(f'<section class="portal-group"><h3>{group}</h3>{rows}</section>')
    right = ''.join(card('transplant/'+p['slug']+'/', p['code'], p['name'], f'{len(p["steps"])} decisions · {p["route"]}', p['entry']) for p in data['index'])
    return '''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="robots" content="noindex">
<title>Memorial Hermann · HPB Oncology & Transplant Pathways</title>
<meta name="description" content="A shared clinical review portal: HPB oncology treatment roadmaps and guidance-aligned liver transplant pathways.">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Source+Sans+3:wght@400;600;700&family=Source+Serif+4:opsz,wght@8..60,400;8..60,700&display=swap">
<link rel="stylesheet" href="assets/portal.css"><script src="assets/portal.js" defer></script></head>
<body class="portal-home"><a class="portal-skip" href="#pathways">Skip to pathways</a>
<div class="portal-draft">Clinical review draft · Not approved institutional policy · Not an automated eligibility tool.</div>
<header class="portal-masthead"><a href="./" class="portal-wordmark">Memorial Hermann <span>/ UTHealth Houston</span></a><span>HPB & transplant oncology</span></header>
<main class="portal-wrap"><section class="portal-intro"><p class="portal-eyebrow">One site. Two connected clinical journeys.</p><h1>From cancer treatment<br>to transplant selection.</h1><p>Start with a tumor’s treatment roadmap, compare liver-directed and systemic options, or enter its transplant pathway. Follow the decisions and review the evidence for standard and selected high-risk approaches.</p></section>
<div class="portal-search"><label for="portal-search">Find a tumor or pathway</label><input type="search" id="portal-search" placeholder="HCC, colorectal, perihilar, neuroendocrine…" autocomplete="off"><span id="portal-count" aria-live="polite">12 roadmaps · 2 therapy matrices · integrated transplant pathways</span></div>
<div class="portal-columns" id="pathways"><section class="portal-lane" id="hpb-roadmaps" aria-labelledby="hpb-heading"><div class="portal-lane-head"><p class="portal-eyebrow">01 / Cancer treatment</p><h2 id="hpb-heading">HPB oncology roadmaps</h2><p>Diagnosis → staging → treatment → reassessment</p><span class="portal-pill">12 tumor & diagnostic roadmaps</span></div>''' + ''.join(left) + '''<p class="portal-empty" hidden>No matching oncology roadmap.</p></section>
<section class="portal-lane transplant-lane" id="transplant-protocols" aria-labelledby="transplant-heading"><div class="portal-lane-head"><p class="portal-eyebrow">02 / Transplant selection</p><h2 id="transplant-heading">Liver transplant<br>assessment pathways</h2><p>Required tests → eligibility review → treatment and reassessment</p><span class="portal-pill">7 pathways · integrated high-risk protocols</span></div><div class="portal-lane-note"><strong>Clinical suitability and allocation eligibility are separate.</strong> Some pathways use nonstandard NLRB review. These pathways do not estimate an individual patient’s risk or guarantee exception approval.</div>''' + right + '<section class="portal-group"><h3>High-risk protocols within each pathway</h3>'+card('transplant/high-risk/','High risk','High-risk protocol index','Orange-labeled options within each standard protocol, with selection criteria, study results and full-text PDF access.','HCC pCCA iCCA colorectal CRLM neuroendocrine NELM HEHE HCA')+'''</section><p class="portal-empty" hidden>No matching transplant pathway.</p><a class="portal-all" href="transplant/">Search all standard decisions & meeting questions →</a><div class="portal-how"><h3>At every transplant decision</h3><ol><li>See the tests and information to obtain.</li><li>Use the findings to proceed, obtain more information, or select another treatment pathway.</li><li>Open the supporting source beside the criterion.</li><li>Review orange-labeled high-risk protocols at the relevant decision, including the evidence, limits and approval requirements.</li></ol></div></section></div>
<section class="portal-boundary"><h2>Working material for multidisciplinary review</h2><p>These roadmaps and protocols are discussion drafts, not approved clinical policy. Source authority, evidence strength and local proposals are distinct. Recheck current allocation policy, guidance and drug/device requirements before clinical use.</p><p>Journal sources open on publisher, DOI, TMC Library or official full-text pages; institutional access may be required. Licensed PDFs remain in the local reference depots. Orange-labeled sections integrate proposed high-risk protocols and their limits. Author-created V7 protocol PDFs are available; publication does not activate a transplant protocol or study.</p></section>
<footer class="portal-footer">Clinical source/version dates remain on the individual pathways. · <a href="changes/">Change log</a></footer></main></body></html>'''

def export(source, preserve_documents=False):
    original = json.loads((source/'assets/content.json').read_text())
    data = transform(original)
    dest = ROOT/'transplant'
    dest.mkdir(exist_ok=True)
    replacements = {r['pdf']: r['url'] for r in original['sources'].values() if r['pdf'].startswith('/')}
    html_files = [source/'index.html']
    html_files += sorted((source/'recording-templates').glob('*.html'))
    for p in original['index']:
        slug=p['slug']
        html_files += [source/slug/'index.html', source/slug/'clinical-roadmap.html', source/'alignment'/f'{slug}.html', source/'alignment'/slug/'index.html', source/'meeting-records'/f'{slug}.html']
    for file in html_files:
        text = file.read_text()
        match = re.search(r'(<script id="protocol-data" type="application/json">)(.*?)(</script>)', text, re.S)
        if match:
            payload = json.loads(match[2].replace('<\\/', '</'))
            new_payload = json.dumps(transform(payload), ensure_ascii=False).replace('</', '<\\/')
            text = text[:match.start(2)] + new_payload + text[match.end(2):]
        for old, new in replacements.items():
            text = text.replace(escape(old, quote=True), escape(new, quote=True))
        text = re.sub(r'(href|src)="/(?!mh-liver-pathways/)', r'\1="'+TP+'/', text)
        text = re.sub(r'content="0;url=/(?!mh-liver-pathways/)', 'content="0;url='+TP+'/', text)
        if '/evidence/' in text:
            raise ValueError(f'Private PDF reference survives in {file}')
        text = text.replace('</head>', f'<link rel="stylesheet" href="{BASE}/assets/portal-navigation.css"><script src="{BASE}/assets/portal-navigation.js" defer></script></head>')
        target = dest/file.relative_to(source); target.parent.mkdir(parents=True, exist_ok=True); target.write_text(text)
    assets = dest/'assets'; assets.mkdir(exist_ok=True)
    app = (source/'assets/app.js').read_text().replace('href="/', 'href="'+TP+'/')
    app = app.replace("${external(r.pdf,r.pdf.startsWith('/')?'Open deposited full-text PDF':'Open official full text','btn')}${external(r.url,r.kind==='Allocation policy'||r.kind==='NLRB guidance'?'Live official source':'Publisher / DOI','btn secondary')}", "${external(r.url,r.kind==='Allocation policy'||r.kind==='NLRB guidance'?'Open official source':'Publisher / full-text access','btn')}")
    app = app.replace('The presence of a PDF does not imply high-level or definitive evidence.', 'Publisher access may require an institutional sign-in. A source link does not imply high-level or definitive evidence.')
    app = app.replace('The linked source supports the adjacent statement.', 'Access through the publisher or official source; institutional sign-in may be required. The linked source supports the adjacent statement.')
    (assets/'app.js').write_text(app)
    shutil.copy2(source/'assets/style.css', assets/'style.css')
    for name in ['assistant.js','assistant.css','high-risk.js','high-risk.css']:
        shutil.copyfile(source/'assets'/name,assets/name)
    (assets/'content.json').write_text(json.dumps(data, ensure_ascii=False, indent=2))
    template_dest=dest/'recording-templates'; template_dest.mkdir(exist_ok=True)
    # Only redirects remain at old form URLs; retire data-entry/export downloads.
    for file in template_dest.iterdir():
        if file.is_file() and file.suffix in ('.md','.zip','.css','.js'):
            file.unlink()
    copied=[]
    for p in original['index']:
        for url in [p['protocol']] + [d['url'] for d in p['docs']]:
            rel=url.lstrip('/'); target=dest/rel; target.parent.mkdir(parents=True,exist_ok=True)
            if not (preserve_documents and target.exists()):
                shutil.copy2(source/rel, target)
            copied.append({'path':'transplant/'+rel,'sha256':hashlib.sha256(target.read_bytes()).hexdigest()})
    manifest={'hosting_export':STAMP,'clinical_source_date':'2026-10-23','pathways':len(data['index']),'steps':sum(len(p['steps']) for p in data['index']),'meeting_questions':sum(len(p['issues']) for p in data['index']),'evidence_sources':len(data['sources']),'licensed_pdfs_published':0,'documents':copied,'clinical_changes':'Source revised for plain clinical language and iCCA focality clarification; export preserves source content except hosting and evidence-access URLs.'}
    manifest.update(language_revision='2026-10-24',next_actions_revision='2026-10-24',decision_assistant_version=original['assistant_version'],decision_assistants=len(original['assistants']),recording_templates=0,research_data_kits=0,care_plans=sum(len(x) for x in original['care'].values()),documentation_changes='Reviewed all 46 transplant decisions and 45 linked discussion questions for explicit treatment, transplant-listing and MELD-exception language. Added next actions for every decision result, including conditional AFP treatment choices, reassessment after treatment, and best supportive care. NCCN sources cite original PDF pages. Existing selection thresholds and matching rules are retained; Word documents keep their separately dated wording. No recording, signatures, export or persistent storage.')
    manifest.update(interface_revision='2026-10-24',example_presets=len(original['assistants']),journey_overviews=len(original['journeys']),sticky_decision_navigation=True,
                    interface_changes='Each pathway opens with clearly labeled example choices toward transplantation. A four-stage overview and sticky step navigation show the full journey. Restore-example and clear-all controls are available. Changing a finding clears later examples; no automatic refill on navigation. No clinical criteria or matching rules changed.')
    manifest.update(high_risk_integration='2026-10-24',high_risk_reviews=21,high_risk_protocol_pdfs=7,high_risk_sources=105,high_risk_interface='Orange-labeled reviews at relevant standard decisions, with selection criteria, study evidence and PDF/TMC access. Standard matching rules unchanged.')
    manifest.update(evidence_organization_revision='2026-10-24',evidence_organization='Status, proposed position and next action precede open criteria. Searchable study summaries pair results with limitations and retain population and time-origin wording. One access record per source within each review; authority types, review coverage and approval limits are explicit. No selection criteria or matching rules changed.')
    (dest/'export-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    (ROOT/'index.html').write_text(home(data))
    for _,slug,_,_,_ in ROADMAPS:
        file=ROOT/slug/'index.html'; text=file.read_text()
        if 'portal-navigation.js' not in text:
            text=text.replace('</head>', '<link rel="stylesheet" href="../assets/portal-navigation.css"><script src="../assets/portal-navigation.js" defer></script></head>')
            file.write_text(text)
    assert len(copied)==21
    # Only the seven author-created V7 protocol PDFs may be published here.
    authored=json.loads((dest/'high-risk/authored-documents.json').read_text())
    allowed={x['path']:x['sha256'] for x in authored if x['path'].endswith('.pdf')}
    pdfs=list(dest.rglob('*.pdf'))
    assert len(pdfs)==len(allowed)==7
    for p in pdfs:assert hashlib.sha256(p.read_bytes()).hexdigest()==allowed[str(p.relative_to(ROOT))]
    print(json.dumps({k:v for k,v in manifest.items() if k!='documents'},indent=2))

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('transplant_dist',type=Path);parser.add_argument('--preserve-existing-documents',action='store_true');args=parser.parse_args();export(args.transplant_dist,args.preserve_existing_documents)
