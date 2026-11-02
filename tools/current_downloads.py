"""Canonical serving destinations for retired author-created downloads.

Publication PDFs and their original V15 depot metadata are outside this mapping.
"""
from pathlib import Path
from urllib.parse import unquote, urlsplit
import json, re

ROOT=Path(__file__).resolve().parents[1]
BASE='/mh-liver-pathways/'
MANIFEST=ROOT/'tools/download_archive_manifest.json'

def rows():
    return json.loads(MANIFEST.read_text())['files']

def canonical_url(value):
    if not isinstance(value,str):return value
    parsed=urlsplit(value)
    if parsed.scheme and parsed.netloc not in ('drliuhao.github.io','localhost','127.0.0.1'):return value
    path=unquote(parsed.path)
    candidates=[path.removeprefix(BASE).lstrip('/')]
    if path.startswith('/') and not path.startswith(BASE):candidates.append('transplant/'+path.lstrip('/'))
    for row in rows():
        if row['old_path'] in candidates:
            return BASE+row['current_target']+('?' + parsed.query if parsed.query else '')+('#'+parsed.fragment if parsed.fragment else '')
    return value

def rewrite_data(value):
    if isinstance(value,dict):return {k:rewrite_data(v) for k,v in value.items()}
    if isinstance(value,list):return [rewrite_data(v) for v in value]
    return canonical_url(value) if isinstance(value,str) else value

def rewrite_text(text):
    """Rewrite explicit serving URL tokens, including old relative HTML hrefs."""
    for row in rows():
        name=Path(row['old_path']).name
        if name not in text:continue
        pattern=re.compile(r'(["\'])([^"\'<>\s]*'+re.escape(name)+r')\1')
        text=pattern.sub(lambda m: m[1]+BASE+row['current_target']+m[1],text)
    return text

def canonical_files():
    manifest=json.loads((ROOT/'assets/documents.json').read_text())
    return sorted('documents/'+key+'/'+name for key,t in manifest['tumors'].items() for name in t['files'].values())

def high_risk_document(slug):
    data=json.loads((ROOT/'assets/documents.json').read_text())['tumors'][slug]
    return 'documents/'+slug+'/'+data['files']['highrisk_info']
