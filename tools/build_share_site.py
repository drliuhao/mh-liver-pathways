"""Build the share edition of the website: every page and tool, without the downloadable documents.

usage: python3 tools/build_share_site.py <output folder> [--base mh-liver-pathways-share]

Hao Liu, 31 October 2026: "a sharable version of the website where the downloadable documents are not available".
- Copies every published file (git ls-files) except tools/, docs/, the repository notes (*.md) and the site's own Word,
  PDF, PowerPoint and Excel files (documents/<tumor>/, evidence/2026-10-25/docs/, transplant/docs/,
  transplant/high-risk/docs/, transplant/protocols/, lrt/*.pdf), and the index of the high-risk protocol files.
- Serves under its own base path: every /mh-liver-pathways/ address, the absolute drliuhao.github.io address and the
  page-slug helper point at the share edition, so no page loads or links back to the full site.
- Marks every page data-edition="share" (assets/portal-navigation.js also sets it): the Documents menu is not built,
  notes that point to it are hidden, links to the site's own documents are removed here and, for anything a page
  renders later, by assets/portal-navigation.js.
- Drops the link to the repository history (the repository holds the documents).
- Checks the result: no document file, no link to one in a page, no address of the full site.
"""
import html, json, re, shutil, subprocess, sys
from pathlib import Path
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]
FULL = 'mh-liver-pathways'
DOC = re.compile(r'\.(?:docx?|pdf|pptx?|xlsx?)$', re.I)
SKIP_DIRS = ('tools/', 'docs/')
SKIP_FILES = {'transplant/high-risk/authored-documents.json'}  # assets/documents.json stays: it also drives the roadmaps' Questions for consensus
TEXT = ('.html', '.js', '.css', '.json', '.svg', '.txt', '.xml', '.webmanifest')
PRIVATE_LOCATION = re.compile(r'file://|/Users/|(?<![A-Za-z0-9])[A-Z]:[\\/]|Synology|V15_complete_evidence_libraries|PDF[_ -]?depot', re.I)
FULL_PATH = re.compile(r'(?<![\w/.-]github\.com/drliuhao)/' + FULL + r'(?=/|[?#\'"<>\s]|$)')
FULL_REPOSITORY = re.compile(r'https?://(?:github\.com|raw\.githubusercontent\.com)/drliuhao/' + FULL + r'(?=/|[?#\'"<>\s]|$)', re.I)


def published():
    files = subprocess.run(['git', '-C', str(ROOT), 'ls-files', '-z', '--cached', '--others', '--exclude-standard'], capture_output=True, text=True, check=True).stdout.split('\0')
    for f in files:
        if not f or f.startswith(SKIP_DIRS) or f in SKIP_FILES or DOC.search(f) or f.endswith('.md') or re.search(r'(^|/)(?:slides?|slide[_-]?previews?|ppt[_-]?previews?)/', f, re.I):
            continue
        if not (ROOT / f).exists():
            continue
        # The share edition is text-only. Unknown archives/binaries must not become
        # public merely because their extension was absent from the document list.
        if (ROOT / f).is_symlink() or (not f.endswith(TEXT) and f != '.nojekyll'):
            continue
        yield f


def local_doc(href, page, base):
    """True when the link opens one of the site's own document files."""
    href = unquote(html.unescape(href.strip()))
    parsed = urlsplit(href)
    if not DOC.search(parsed.path):
        return False
    if parsed.scheme in ('http', 'https') or parsed.netloc:
        host = (parsed.hostname or '').lower()
        if host == 'drliuhao.github.io':
            return parsed.path.startswith((f'/{base}/', f'/{FULL}/'))
        if host in ('github.com', 'raw.githubusercontent.com'):
            return parsed.path.startswith((f'/drliuhao/{base}/', f'/drliuhao/{FULL}/'))
        return False
    return True


ANCHOR = re.compile(r'<a\b[^>]*\bhref=(["\'])(.*?)\1[^>]*>(.*?)</a>', re.S)


def strip_links(html, page, base):
    def rep(m):
        if not local_doc(m.group(2), page, base):
            return m.group(0)
        inner = m.group(3)
        return inner if re.search(r'<(img|svg|picture)\b', inner) else '\x00'
    html = ANCHOR.sub(rep, html)
    # the separator that joined a removed link to its neighbour, then an element the removal left empty (only
    # those: empty elements elsewhere are mount points that scripts fill)
    html = re.sub(r'\s*[·|]\s*\x00|\x00\s*[·|]\s*', '\x00', html)
    for _ in range(3):
        html = re.sub(r'<(p|li|span|small|div)(\s[^>]*)?>\s*\x00\s*</\1>', '\x00', html)
    return html.replace('\x00', '')


PRIVATE_FIELDS = {'ppt_filename', 'local_folder', 'pdf_file', 'pdf_path', 'pdf_files',
                  'local_path', 'source_path', 'docx', 'pptx', 'download_url', 'preview_path',
                  'slides', 'slide_numbers', 'slide_count', 'pdf_available', 'matched_pdfs',
                  'missing_pdfs', 'matched_publication_pdfs', 'missing_publication_pdfs',
                  'unchecked_publication_pdfs', 'no_slide_entries', 'no_slide_count', 'appraisals_pending'}
LIBRARY_PRIVATE_FIELDS = {'coverage', 'family', 'document', 'document_only', 'inclusion'}
_REMOVE = object()  # Authored JSON null is clinical data, not a removal signal.

def clean_data(value, key='', base='mh-liver-pathways-share', library=False):
    """Remove download destinations from data too, keeping clinical question data."""
    if key in PRIVATE_FIELDS or (library and key in LIBRARY_PRIVATE_FIELDS):
        return _REMOVE
    if isinstance(value, dict):
        out = {}
        for k, v in value.items():
            cleaned = clean_data(v, k, base, library)
            if cleaned is not _REMOVE: out[k] = cleaned
        return out
    if isinstance(value, list):
        return [v for item in value if (v := clean_data(item, base=base, library=library)) is not _REMOVE]
    if isinstance(value, str):
        if re.search(r'\.(?:docx?|pptx?|xlsx?)(?:$|[?#])', value, re.I):
            return _REMOVE
        if PRIVATE_LOCATION.search(value):
            return _REMOVE
        if FULL_REPOSITORY.search(value):
            return _REMOVE
        if local_doc(value, '', base):
            return _REMOVE
        return value
    return value


def share_library_script():
    """The public library keeps literature access, without local file/slide metadata."""
    return ''''use strict';
(async()=>{
 const e=s=>String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
 const out=document.getElementById('results'),select=document.getElementById('library'),search=document.getElementById('search');
 try{
 const [a,b]=await Promise.all(['catalog.json','document-index.json'].map(u=>fetch(u).then(r=>{if(!r.ok)throw Error(u);return r.json()})));
 const data=LibraryDocumentIndex.merge(a,b);
 document.getElementById('census').textContent=data.libraries.length+' libraries · '+data.unique_publications+' publications';
 for(const lib of data.libraries){const o=document.createElement('option');o.value=lib.key;o.textContent=lib.title;select.append(o)}
 function render(){const key=decodeURIComponent(location.hash.slice(1));select.value=key;const q=search.value.toLowerCase(),lib=data.libraries.find(x=>x.key===key);
 if(!lib){out.innerHTML='<div class="library-grid">'+data.libraries.filter(l=>l.title.toLowerCase().includes(q)).map(l=>'<article class="library-card"><h2><a href="#'+e(l.key)+'">'+e(l.title)+'</a></h2><p>'+l.publication_count+' publications</p></article>').join('')+'</div>';return}
 const publications=lib.papers.map(r=>data.publications[r.id]).filter(Boolean).filter(p=>[p.title,p.pmid,p.doi].join(' ').toLowerCase().includes(q));
 out.innerHTML='<p><a href="#">← All evidence libraries</a></p><h2>'+e(lib.title)+'</h2><ul class="records">'+publications.map(p=>'<li class="record"><h3>'+e(p.title)+'</h3><p>'+e(p.year)+' · PMID '+e(p.pmid||'not indexed')+' · DOI '+e(p.doi||'not recorded')+'</p><div class="access">'+(p.url?'<a href="'+e(p.url)+'" target="_blank" rel="noopener">Publication / full text ↗</a>':'')+(p.tmc?'<a href="'+e(p.tmc)+'" target="_blank" rel="noopener">TMC full-text access ↗</a>':'')+'</div></li>').join('')+'</ul>';
 }
 select.addEventListener('change',()=>{location.hash=select.value});search.addEventListener('input',render);window.addEventListener('hashchange',render);render();
 }catch(err){out.textContent='The evidence index could not load. Please reload.';console.error(err)}
})();'''


def share_library_index_script():
    """Merge public citations without depending on removed private metadata."""
    return ''''use strict';
(function(root){
 function merge(catalog,supplement){
  const data=JSON.parse(JSON.stringify(catalog));
  Object.assign(data.publications,supplement.publications);
  for(const lib of data.libraries){
   const extra=supplement.libraries[lib.key]||{papers:[],policy_records:[]};
   const ids=new Set(lib.papers.map(r=>r.id));
   for(const row of extra.papers){if(!ids.has(row.id)){lib.papers.push(row);ids.add(row.id)}}
   const titles=new Set(lib.policy_records.map(r=>r.title));
   for(const row of extra.policy_records){if(!titles.has(row.title)){lib.policy_records.push(row);titles.add(row.title)}}
   lib.publication_count=lib.papers.length;
  }
  data.unique_publications=Object.keys(data.publications).length;
  return data;
 }
 if(typeof module==='object'&&module.exports)module.exports={merge};else root.LibraryDocumentIndex={merge};
})(typeof window==='undefined'?globalThis:window);'''


def build(out, base):
    out = Path(out)
    if out.resolve() == ROOT or ROOT.is_relative_to(out.resolve()):
        raise SystemExit('Output must not contain or replace the full website checkout.')
    if out.exists():
        for child in out.iterdir():
            if child.name == '.git':
                continue
            shutil.rmtree(child) if child.is_dir() else child.unlink()
    out.mkdir(parents=True, exist_ok=True)
    n = 0
    for f in published():
        src, dst = ROOT / f, out / f
        dst.parent.mkdir(parents=True, exist_ok=True)
        if not f.endswith(TEXT):
            shutil.copyfile(src, dst); n += 1
            continue
        s = src.read_text(encoding='utf8')
        # every address of the full site -> the share edition (the repository history link is removed below)
        s = FULL_PATH.sub(f'/{base}', s)
        s = s.replace(f"parts.indexOf('{FULL}')", f"parts.indexOf('{base}')")
        if f.endswith('.json'):
            is_library = f in ('evidence-libraries/catalog.json', 'evidence-libraries/document-index.json')
            obj=clean_data(json.loads(s),base=base,library=is_library)
            if f == 'evidence-libraries/document-index.json':
                obj['about']='Additional publication and guidance citations supporting the clinical topics.'
            if f == 'transplant/export-manifest.json': obj['documents']=[]
            if f == 'assets/documents.json':
                # On-page question rendering uses the disease and questions metadata.
                pass
            s=json.dumps(obj,ensure_ascii=False,indent=2)+'\n'
        if f.endswith('.html'):
            s = re.sub(r'<p>\s*<a href="https://github\.com/drliuhao/[^"]*">[^<]*</a>\s*</p>', '', s)
            s = re.sub(r'<a href="https://github\.com/drliuhao/[^"]*">([^<]*)</a>', r'\1', s)
            s = re.sub(r'<html\b(?![^>]*data-edition)', '<html data-edition="share"', s, count=1)
            s = strip_links(s, f, base)
            # Embedded data is another possible source of generated document links.
            s=re.sub(r'(<script\b[^>]*type=["\']application/json["\'][^>]*>)(.*?)(</script>)',
                     lambda m:m[1]+json.dumps(clean_data(json.loads(m[2]),base=base),ensure_ascii=False)+m[3],s,flags=re.S)
            s=re.sub(r'<[^>]+\bdownload(?:=[^>]*)?>.*?</a>', '',s,flags=re.S)
            s=s.replace('Evidence, PDFs and summary slides','Evidence libraries')
            s=s.replace('Shared papers belong in every library that needs them. Find a publication, see its full-text access links, and identify its summary slides in the corresponding local PPT.',
                        'Find the publications supporting each clinical topic, with publisher and TMC Library access links.')
            s=s.replace('Publication metadata and institutional full-text links are public. Deposited journal PDFs and the figure-containing PPTs remain in the private Synology package; they are not uploaded here. Availability does not establish evidence quality or institutional approval.',
                        'Publication metadata and literature access links support review of the clinical content. Document and slide downloads are not included in this edition.')
        if f == 'evidence-libraries/library.js': s=share_library_script()
        if f == 'evidence-libraries/document-index.js': s=share_library_index_script()
        if f == 'assets/portal-navigation.js':
            s = s.replace('(() => {', "(() => {\n  document.documentElement.dataset.edition='share';", 1)
            assert "dataset.edition='share';" in s, 'portal-navigation.js entry point changed'
        dst.write_text(s, encoding='utf8'); n += 1
    (out / 'robots.txt').write_text('User-agent: *\nDisallow: /\n')
    check(out, base)
    print(f'Share edition: {n} files in {out} (base /{base}/); no document files, no links to them, no address of the full site.')


def check(out, base):
    fail = []
    for p in out.rglob('*'):
        if p.is_dir() or '.git' in p.parts:
            continue
        rel = p.relative_to(out).as_posix()
        if DOC.search(rel):
            fail.append(f'document file published: {rel}')
            continue
        if not rel.endswith(TEXT):
            if rel != '.nojekyll' or p.stat().st_size:
                fail.append(f'non-text or unknown file published: {rel}')
            continue
        s = p.read_text(encoding='utf8', errors='ignore')
        if FULL_PATH.search(s):
            fail.append(f'{rel}: still addresses the full site')
        if FULL_REPOSITORY.search(s):
            fail.append(f'{rel}: links to the repository')
        if rel.endswith('.html'):
            for m in ANCHOR.finditer(s):
                if local_doc(m.group(2), rel, base):
                    fail.append(f'{rel}: links to a document ({m.group(2)[:80]})')
            if 'data-edition="share"' not in s[:400]:
                fail.append(f'{rel}: not marked as the share edition')
        if rel.endswith('.json'):
            if re.search(r'\.(?:docx?|pptx?|xlsx?)(?:["?#]|$)',s,re.I):
                fail.append(f'{rel}: contains a document/slide destination')
            if PRIVATE_LOCATION.search(s):
                fail.append(f'{rel}: contains internal file metadata')
            def check_fields(value):
                if isinstance(value, dict):
                    for key, item in value.items():
                        if key in PRIVATE_FIELDS or (rel.startswith('evidence-libraries/') and key in LIBRARY_PRIVATE_FIELDS):
                            fail.append(f'{rel}: contains private metadata field {key}')
                        check_fields(item)
                elif isinstance(value, list):
                    for item in value: check_fields(item)
                elif isinstance(value, str) and local_doc(value, rel, base):
                    fail.append(f'{rel}: contains a local document destination')
            check_fields(json.loads(s))
    nav = (out / 'assets/portal-navigation.js').read_text()
    if "dataset.edition='share'" not in nav or "edition==='share'" not in nav:
        fail.append('portal-navigation.js does not run the share edition')
    if "edition === 'share') return" not in (out / 'assets/document-corner.js').read_text():
        fail.append('document-corner.js would still build the Documents menu')
    if fail:
        raise SystemExit('FAIL:\n- ' + '\n- '.join(fail[:40]))


if __name__ == '__main__':
    args = sys.argv[1:]
    if not args:
        raise SystemExit(__doc__)
    base = 'mh-liver-pathways-share'
    if '--base' in args:
        base = args[args.index('--base') + 1]
    build(args[0], base)
