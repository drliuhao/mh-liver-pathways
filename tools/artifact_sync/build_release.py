"""Index the verified local V18 artifacts and record a portable publication manifest.

Run after sync_words.py --publish and presentation finalization. Inputs and source
PDFs stay local; the public manifest contains relative names and hashes only.
"""
from pathlib import Path
import hashlib, html, json, shutil, zipfile
from xml.etree import ElementTree as ET

R = Path(__file__).resolve().parents[2]
W = R.parent
H = R / 'tools/artifact_sync'
B = W / 'Artifact_Sync_2026-11-02/.build'
O = W / 'V18_consistent_release_2026-11-02'
RELEASE = 'V18_consistent_release_2026-11-02'
read = lambda p: json.loads(Path(p).read_text())
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
write = lambda p, d: Path(p).write_text(json.dumps(d, ensure_ascii=False, indent=2)+'\n')

plan = read(H/'ppt_sync_plan.json')
words = read(H/'word_sync_manifest.json')
cards = read(H/'source_card_additions.json')
assert len(plan)==34 and len(words)==65

# Only two newly indexed reports have verified full publisher-layout PDFs here.
# FIGHT-302 and RTOG0848 were read from XML; do not mark their PDF as available.
new_pdfs = {
 '37230894': W/'Full_Text_Review_2026-10-31/Analyst_A_Full_Reaudit_2026-11-01/reviews/pancreatic_ampullary/sources/37230894.pdf',
 '36871765': W/'Full_Text_Review_2026-10-31/Analyst_A_Full_Reaudit_2026-11-01/reviews/pancreatic_ampullary/downloads/Crino36871765.pdf',
}
titles = {
 '37230894':'Predictive ability of pancreatic cyst fluid biomarkers: a systematic review and meta-analysis.',
 '36871765':'Endoscopic ultrasound-guided radiofrequency ablation versus surgical resection for treatment of pancreatic insulinoma.',
 '42456089':'Adjuvant chemotherapy with or without chemoradiotherapy for adenocarcinoma of the pancreatic head: radiotherapy randomization of NRG Oncology/RTOG 0848.',
 '42223137':'Pemigatinib versus gemcitabine and cisplatin in FGFR2-rearranged advanced cholangiocarcinoma (FIGHT-302).',
}

catalog = read(R/'evidence-libraries/catalog.json')
if catalog.get('artifact_release') != RELEASE:
 for d in plan:
  lib=next(x for x in catalog['libraries'] if x['key']==d['key'])
  additions=sorted(d['additions'],key=lambda a:a['insert_after_active_slide'])
  for row in lib['papers']+lib['policy_records']:
   row['slides']=[s+sum(a['insert_after_active_slide']<s for a in additions) for s in row['slides']]
  lib['slides']=d['active_slides']+len(additions)
  for i,a in enumerate(additions):
   n=a['new']; pmid=n['pmid']; slide=a['insert_after_active_slide']+i+1
   pid=next((k for k,v in catalog['publications'].items() if v.get('pmid')==pmid), 'doi:'+n['doi'].lower())
   if pid not in catalog['publications']:
    catalog['publications'][pid]={
     'title':titles[pmid], 'author':n['author'], 'journal':n['journal'], 'year':str(n['year']),
     'doi':n['doi'],'pmid':pmid,'publication_type':'Journal publication',
     'url':'https://doi.org/'+n['doi'],'tmc':'https://libkey.io/libraries/480/pmid/'+pmid,
     'pdf_available':pmid in new_pdfs,'coverage':'Focused main-report review',
     'coverage_notes':n['limitations'],
    }
   row=next((p for p in lib['papers'] if p['id']==pid),None)
   if row:row['slides'].append(slide);row['slides'].sort()
   else:lib['papers'].append({'id':pid,'slides':[slide],'inclusion':['Source supporting the accepted clinical correction; focused evidence card with explicit limitations.']})
  lib['publication_count']=len(lib['papers'])
  lib['matched_pdfs']=sum(bool(catalog['publications'][p['id']]['pdf_available']) for p in lib['papers'])
 catalog['unique_publications']=len(catalog['publications'])
 catalog['matched_publication_pdfs']=sum(bool(p['pdf_available']) for p in catalog['publications'].values())
 catalog['missing_publication_pdfs']=catalog['unique_publications']-catalog['matched_publication_pdfs']
 catalog['updated']='1 November 2026 · V18 synchronized artifacts'
 catalog['artifact_release']=RELEASE
 write(R/'evidence-libraries/catalog.json',catalog)

manifest={'release':RELEASE,'scope':'Current editions; historical local archives are preserved.',
 'word_documents':[],'presentations':[], 'clinical_source_sha256':{},
 'verification_limits':'Word: all 65 rendered, sampled visual inspection. PowerPoint: accepted corrections propagated, every package checked, selected changed slides and all five new source cards visually inspected. This is not a new full-text audit of every paper or a visual read of every page/slide.'}
for d in words:
 p=Path(d['published_path']); assert sha(p)==d['published_sha256']
 local=Path(d['output']); assert sha(local)==d['sha256']
 manifest['word_documents'].append({'path':str(p.relative_to(R)),'sha256':sha(p),'local_master':str(local.relative_to(O)),'local_sha256':sha(local)})

for d in plan:
 p=Path(d['target']); v=read(B/'ppt_validation'/f"{d['key']}.json"); q=read(B/'ppt_candidates'/f"{d['key']}.json")
 assert v['finalSha256']==sha(p) and v['firstPartyImport']['passed']
 assert v['packageIntegrity']['status']=='pass' and not v['presentationLayout']['findingCount']
 assert q['all_original_media_and_workbooks_byte_identical']
 assert q['native_charts_preserved']==d['objects']['native_charts_on_active_slides']
 assert q['native_tables_preserved']==d['objects']['native_tables_on_active_slides']
 with zipfile.ZipFile(p) as z:
  slides=len(ET.fromstring(z.read('ppt/presentation.xml')).find('{http://schemas.openxmlformats.org/presentationml/2006/main}sldIdLst'))
 assert slides==d['active_slides']+len(d['additions'])
 manifest['presentations'].append({'key':d['key'],'title':d['title'],'path':str(p.relative_to(O)),'sha256':sha(p),'slides':slides,'native_charts':q['native_charts_preserved'],'native_tables':q['native_tables_preserved'],'changed_paragraphs':len(d['changes']),'added_cards':len(d['additions'])})
 # Preserve working relative publication links without copying or altering old depots.
 for folder in ['PDF_depot','Policy_and_guideline_PDFs']:
  source=Path(d['current_master']).parent/folder; dest=p.parent/folder
  if not source.exists():continue
  dest.mkdir(exist_ok=True)
  for item in source.iterdir():
   link=dest/item.name
   if not link.exists():link.symlink_to(item)
 for a in d['additions']:
  pmid=a['new']['pmid']
  if pmid in new_pdfs:
   source=new_pdfs[pmid];assert source.read_bytes()[:5]==b'%PDF-'
   dest=p.parent/'PDF_depot'/f'PMID{pmid}.pdf';dest.parent.mkdir(exist_ok=True)
   if not dest.exists():dest.symlink_to(source)

source_paths=set()
for disease in ['hcc','hilar','icca','chcca','crlm','nelm','adenoma','incidental','pdac','pcyst','pnet','ampullary']:
 source_paths.update(p for p in (R/disease/'data').glob('*.json'))
source_paths.update(R/p for p in ['hcc/index.html','transplant/assets/content.json','transplant/assets/assistant.js','transplant/assets/risk-routing.js','systemic/matrix.json','systemic/references.json','lrt/index.html','lrt/matrix.json','assets/clinical-scores.js','assets/clinical-reference.js','tools/compact_evidence_source.json'])
for p in sorted(source_paths):
 assert p.is_file(),p
 manifest['clinical_source_sha256'][str(p.relative_to(R))]=sha(p)
manifest['counts']={'word_documents':len(words),'presentations':len(plan),'slides':sum(p['slides'] for p in manifest['presentations']),'native_charts':sum(p['native_charts'] for p in manifest['presentations']),'native_tables':sum(p['native_tables'] for p in manifest['presentations'])}
write(R/'tools/artifact_release_manifest.json',manifest)
write(O/'release_manifest.json',manifest)
doc_rows=''.join(f'<li><a href="{html.escape(d["local_master"],quote=True)}">{html.escape(Path(d["local_master"]).stem.replace("_"," "))}</a></li>' for d in manifest['word_documents'])
deck_rows=''.join(f'<li><a href="{html.escape(d["path"],quote=True)}">{html.escape(d["title"])}</a> · {d["slides"]} slides</li>' for d in manifest['presentations'])
page=f'''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>V18 clinical documents and evidence slides</title><style>body{{max-width:1100px;margin:40px auto;padding:0 20px;font:17px/1.55 system-ui;color:#173c46;background:#f7faf9}}a{{color:#006d77}}h1{{font-size:30px}}.grid{{display:grid;grid-template-columns:1fr 1fr;gap:36px}}li{{margin-bottom:8px}}@media(max-width:700px){{.grid{{display:block}}}}</style><h1>Clinical documents and evidence slides · V18</h1><p>65 Word documents and 34 PowerPoint libraries. Current clinical corrections are aligned with the website. Drafts for multidisciplinary review; institutional approval status remains in each document.</p><p><a href="https://drliuhao.github.io/mh-liver-pathways/">Full website</a> · <a href="https://drliuhao.github.io/mh-liver-pathways-share/">Sharing website</a> · <a href="README.md">Release notes</a></p><div class="grid"><section><h2>Documents</h2><ul>{doc_rows}</ul></section><section><h2>Evidence slides</h2><ul>{deck_rows}</ul></section></div></html>'''
(O/'index.html').write_text(page)
(O/'README.md').write_text('''# V18 synchronized clinical release

The 65 current Word documents and 34 evidence PowerPoint libraries incorporate the accepted source corrections used by the revised full and sharing websites. Previous V17 Word and V15 PowerPoint masters are preserved unchanged. Institutional approval status has not changed.

This release propagates the accepted A/B/C findings and reconciled dispositions. It does not claim to complete unread supplements, inaccessible texts or unresolved reviews. Five source cards were added with their evidence limits. Existing media, native charts, tables and embedded workbooks were preserved. Local publication-depot links point to the retained source PDFs; licensed papers and decks are not uploaded to either website.

The full website serves current public-safe Word copies. The sharing website omits institutional document and slide downloads while keeping clinical decisions and publication access links. Open index.html for the local Word/PPT collection.

Verification: all 65 Word documents were rendered (2,590 pages), with automated package/page checks and sampled visual inspection. All 34 PPT packages were validated and re-imported; selected changed slides and all five added cards were visually checked. This is not an exhaustive new paper audit or a visual inspection of every page and slide. Hashes and counts are recorded in release_manifest.json.
''')
(H/'README.md').write_text('''# Artifact synchronization

Current Word and PowerPoint masters are held in the sibling V18_consistent_release_2026-11-02 directory. The exact private inventories, frozen review proposals, authoring receipts and validation reports remain in this local directory and Artifact_Sync_2026-11-02; they are excluded from Git. Source methods: sync_words.py, prepare_decks.py, package_deck.py and build_release.py. PowerPoint text and added cards were authored with the presentation artifact API and merged into original packages to preserve native objects.

Run tools/test_artifact_sync.py before publishing. Clinical source changes require updating affected current artifacts and renewing tools/artifact_release_manifest.json; the test does not substitute for clinical reconciliation.
''')
print(json.dumps(manifest['counts']))
