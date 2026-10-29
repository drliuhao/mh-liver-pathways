/* Approved clinical revisions, applied as recorded data.
 *
 * Each file in tools/clinical_revisions/ lists exact additions and replacements to the transplant
 * content (sources, reviews, rules, evidence) and to the routing/presentation scripts. The guard test
 * (test_contextual_info.cjs) applies the same records to the pinned original before comparing, so a
 * clinical change is accepted only when it is written down here, and nothing else may change.
 *
 *   node tools/apply_clinical_revisions.cjs --write <revision-id>
 *     applies one revision to content.json, the V12 snapshot, every embedded protocol-data payload
 *     and the listed scripts. It refuses to run twice.
 */
'use strict';
const fs = require('node:fs'), path = require('node:path');
const root = path.resolve(__dirname, '..');
const dir = path.join(root, 'tools/clinical_revisions');

function revisions() {
  if (!fs.existsSync(dir)) return [];
  return fs.readdirSync(dir).filter(f => f.endsWith('.json')).sort().map(f => JSON.parse(fs.readFileSync(path.join(dir, f), 'utf8')));
}
function once(text, old, label) {
  const at = text.indexOf(old);
  if (at < 0 || text.indexOf(old, at + 1) >= 0) throw new Error(`${label}: expected exactly one match for ${JSON.stringify(old.slice(0, 80))}`);
  return at;
}
function replaceOnce(text, old, value, label) { const at = once(text, old, label); return text.slice(0, at) + value + text.slice(at + old.length); }
function findReview(hr, id) {
  for (const p of Object.values(hr.pathways)) { const r = p.reviews.find(x => x.id === id); if (r) return r; }
  throw new Error('review not found: ' + id);
}
// Field paths: "title", "rules.0", "evidence.synthesis", "evidence.studies.<key>.results".
function locate(review, field) {
  const parts = field.split('.');
  let holder = review;
  for (let i = 0; i < parts.length - 1; i++) {
    const k = parts[i];
    if (Array.isArray(holder) && k !== '' && isNaN(Number(k))) holder = holder.find(s => s.key === k);
    else holder = holder[Array.isArray(holder) ? Number(k) : k];
    if (holder === undefined) throw new Error(`${review.id}: no field ${field}`);
  }
  const last = parts[parts.length - 1];
  return [holder, Array.isArray(holder) ? Number(last) : last];
}
function addRef(review, key) { if (!review.references.includes(key)) review.references.push(key); }

function applyOne(data, rev) {
  const hr = data.high_risk, label = rev.id;
  for (const s of rev.sources || []) {
    if (hr.sources[s.key]) throw new Error(`${label}: source ${s.key} already exists`);
    hr.sources[s.key] = s;
  }
  for (const e of rev.edits || []) {
    if (e.op === 'add_review') {
      const list = hr.pathways[e.pathway].reviews;
      if (list.some(r => r.id === e.review.id)) throw new Error(`${label}: ${e.review.id} already present`);
      list.push(JSON.parse(JSON.stringify(e.review)));
      continue;
    }
    if (e.op === 'replace_option') {
      const q = data.assistants[e.key].questions.find(x => x.id === e.question);
      const o = q && q.options.find(x => x.value === e.value);
      if (!o) throw new Error(`${label}: no option ${e.key}/${e.question}/${e.value}`);
      o.label = replaceOnce(o.label, e.old, e.new, `${label} ${e.key}/${e.question}/${e.value}`);
      continue;
    }
    const review = findReview(hr, e.review);
    if (e.op === 'replace') {
      const [holder, k] = locate(review, e.field);
      holder[k] = replaceOnce(holder[k], e.old, e.new, `${label} ${e.review}.${e.field}`);
    } else if (e.op === 'append_rule') review.rules.push(e.rule);
    else if (e.op === 'append_item') { const [holder, k] = locate(review, e.field); holder[k].push(e.item); }
    else if (e.op === 'add_study') { review.evidence.studies.push(JSON.parse(JSON.stringify(e.study))); addRef(review, e.study.key); }
    else throw new Error(`${label}: unknown op ${e.op}`);
  }
  for (const p of Object.values(hr.pathways)) for (const r of p.reviews) for (const k of r.references) if (!hr.sources[k]) throw new Error(`${label}: ${r.id} cites missing source ${k}`);
  return data;
}
function applyContent(data, list = revisions()) { for (const rev of list) applyOne(data, rev); return data; }
function applyText(file, text, list = revisions()) {
  for (const rev of list) for (const f of rev.files || []) if (f.file === file) text = replaceOnce(text, f.old, f.new, `${rev.id} ${file}`);
  return text;
}

function write(id) {
  const rev = revisions().find(r => r.id === id);
  if (!rev) throw new Error('unknown revision ' + id);
  const contentFile = path.join(root, 'transplant/assets/content.json');
  const data = JSON.parse(fs.readFileSync(contentFile, 'utf8'));
  const firstNew = (rev.edits || []).find(e => e.op === 'add_review');
  if (firstNew && Object.values(data.high_risk.pathways).some(p => p.reviews.some(r => r.id === firstNew.review.id))) throw new Error(id + ' is already applied');
  applyOne(data, rev);
  const text = JSON.stringify(data, null, 2);
  fs.writeFileSync(contentFile, text);
  fs.writeFileSync(path.join(root, 'tools/v12_content_snapshot.json'), text);
  let payloads = 0;
  const walk = d => fs.readdirSync(d, { withFileTypes: true }).flatMap(x => x.isDirectory() ? walk(path.join(d, x.name)) : x.name.endsWith('.html') ? [path.join(d, x.name)] : []);
  for (const file of walk(path.join(root, 'transplant'))) {
    const html = fs.readFileSync(file, 'utf8');
    const m = html.match(/(<script[^>]*id="protocol-data"[^>]*>)([\s\S]*?)(<\/script>)/);
    if (!m) continue;
    const old = JSON.parse(m[2]); const slug = (old.pathway || {}).slug;
    const payload = { ...data, pathway: data.index.find(x => x.slug === slug) || null, mode: old.mode };
    const value = JSON.stringify(payload).replace(/<\//g, '<\\/');
    const start = m.index + m[1].length;
    fs.writeFileSync(file, html.slice(0, start) + value + html.slice(start + m[2].length));
    payloads++;
  }
  const scripts = [...new Set((rev.files || []).map(f => f.file))];
  for (const f of scripts) {
    const p = path.join(root, f);
    fs.writeFileSync(p, applyText(f, fs.readFileSync(p, 'utf8'), [rev]));
  }
  console.log(`Applied ${id}: ${(rev.sources || []).length} sources, ${(rev.edits || []).length} content edits, ${payloads} embedded payloads, ${scripts.length} scripts.`);
}

module.exports = { revisions, applyContent, applyText };
if (require.main === module) {
  const i = process.argv.indexOf('--write');
  if (i < 0 || !process.argv[i + 1]) { console.error('usage: node tools/apply_clinical_revisions.cjs --write <revision-id>'); process.exit(2); }
  write(process.argv[i + 1]);
}
