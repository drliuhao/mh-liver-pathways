"""Verify current serving downloads and immutable legacy archive provenance."""
from pathlib import Path
import hashlib
import json
import current_downloads as D

ROOT=D.ROOT
manifest=json.loads(D.MANIFEST.read_text())
rows=manifest['files']
assert len(rows)==len({x['old_path'] for x in rows})==54
assert sum(x['old_path'].endswith('.docx') for x in rows)==manifest['word_files']==45
assert sum(x['old_path'].endswith('.pdf') for x in rows)==manifest['authored_pdf_files']==9
assert next(x['current_target'] for x in rows if x['old_path']=='lrt/pcca-decision-chart.pdf')=='hilar/'
archive=ROOT.parent/manifest['archive_directory']
for row in rows:
    assert not (ROOT/row['old_path']).exists(),row['old_path']
    assert len(row['sha256'])==64 and row['bytes']>0,row
    assert (ROOT/row['current_target'].split('#')[0]).exists(),row['current_target']
    assert D.canonical_url(D.BASE+row['old_path'])==D.BASE+row['current_target']
    # Private archives are not deployed. Where present, require the actual bytes;
    # CI also retains the original immutable hash evidence in the public manifest.
    if archive.exists():
        saved=archive/row['archive_path']
        assert saved.stat().st_size==row['bytes'],saved
        assert hashlib.sha256(saved.read_bytes()).hexdigest()==row['sha256'],saved
if archive.exists():assert json.loads((archive/'hash_manifest.json').read_text())==manifest

canonical=set(D.canonical_files())
assert len(canonical)==65
assert {str(p.relative_to(ROOT)) for p in (ROOT/'documents').glob('*/*.docx')}==canonical
assert all((ROOT/rel).is_file() for rel in canonical)
binary_suffixes={'.doc','.docx','.pdf','.ppt','.pptx'}
served_binaries={str(p.relative_to(ROOT)) for p in ROOT.rglob('*')
                 if p.is_file() and p.suffix.lower() in binary_suffixes
                 and not any(x in p.parts for x in ('.git','node_modules'))}
assert served_binaries==canonical,sorted(served_binaries-canonical)

active_generators={'tools/build_portal.py','tools/build_high_risk.py','tools/integrate_high_risk.py',
                   'tools/decision_assistant_source/build.py','tools/decision_assistant_source/content.py',
                   'tools/decision_assistant_source/high_risk_data.json'}
retired_names={Path(x['old_path']).name for x in rows}
for f in ROOT.rglob('*'):
    if not f.is_file() or f.suffix not in ('.html','.js','.json','.py'):continue
    rel=f.relative_to(ROOT).as_posix()
    if any(x in f.parts for x in ('.git','node_modules')):continue
    if rel.startswith(('tools/','docs/')) and rel not in active_generators:continue
    text=f.read_text()
    assert not (retired_names & {name for name in retired_names if name in text}),(rel,'retired download reference')

catalog=json.loads((ROOT/'evidence-libraries/catalog.json').read_text())
assert len(catalog['libraries'])==34
for lib in catalog['libraries']:
    assert lib['local_folder'].startswith('V20_consistent_release_2026-11-04/Evidence_Libraries/'),lib['key']
    assert lib['ppt_filename']=='Evidence_Summaries_v20.pptx',lib['key']
    assert (ROOT/lib['document'].split('#')[0]).exists(),lib['key']
print('PASS: 45 Word + 9 authored PDF originals archived; all retired serving files/links absent; '
      '65 canonical Word downloads and 34 V20 package records resolve; original pCCA chart routes to hilar/.')
