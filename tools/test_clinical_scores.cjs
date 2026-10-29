// Calculators and score definitions in assets/clinical-scores.js (Tools column).
// usage: node tools/test_clinical_scores.cjs
const assert = require('assert');
const path = require('path');
global.window = {};
const ref = require(path.join(__dirname, '../assets/clinical-reference.js'));
global.window.ClinicalReference = ref;
delete require.cache[require.resolve(path.join(__dirname, '../assets/clinical-scores.js'))];
const S = require(path.join(__dirname, '../assets/clinical-scores.js'));
const c = S.calculators;
let n = 0;
const eq = (a, b, m) => { assert.deepStrictEqual(a, b, m); n++; };

// Child-Pugh: the table in ClinicalReference.terms.child (A 5–6, B 7–9, C 10–15; boundaries as printed).
eq(c.childPugh({bilirubin: 1.9, albumin: 3.6, inr: 1.6, ascites: '1', enceph: '1'}).cls, 'A');
eq(c.childPugh({bilirubin: 2, albumin: 3.5, inr: 1.7, ascites: '1', enceph: '1'}).score, 8);
eq(c.childPugh({bilirubin: 3, albumin: 2.8, inr: 2.3, ascites: '2', enceph: '2'}).score, 10);
eq(c.childPugh({bilirubin: 3.1, albumin: 2.7, inr: 2.4, ascites: '3', enceph: '3'}), {ok: true, score: 15, cls: 'C', parts: {bilirubin: 3, albumin: 3, inr: 3, ascites: 3, enceph: 3}});
eq(c.childPugh({bilirubin: '', albumin: 3, inr: 1}).ok, false);
assert(/&lt;2/.test(ref.terms.child.html) && /2–3/.test(ref.terms.child.html) && /&gt;3\.5/.test(ref.terms.child.html), 'calculator follows the displayed Child-Pugh table');

// ALBI (Johnson 2015): unit conversion and cut-offs −2.60 / −1.39.
eq(c.albi({bilirubin: 1, biliUnit: 'mgdl', albumin: 4, albUnit: 'gdl'}).score, -2.59);
eq(c.albi({bilirubin: 17.1, biliUnit: 'umol', albumin: 40, albUnit: 'gl'}).grade, 2);
eq(c.albi({bilirubin: 0.5, biliUnit: 'mgdl', albumin: 4.5, albUnit: 'gdl'}).grade, 1);
eq(c.albi({bilirubin: 4, biliUnit: 'mgdl', albumin: 2.5, albUnit: 'gdl'}).grade, 3);

// HCC tumor burden: the transplant HCC protocol's Milan, T2 and UNOS-downstaging wording; UCSF (Yao 2001).
const hb = sizes => c.hccBurden({sizes});
eq([hb([5]).milan, hb([5]).t2], [true, 'met']);
eq([hb([1.5]).milan, hb([1.5]).t2], [true, 'T1']);
eq([hb([3, 3, 3]).milan, hb([3, 3, 3]).t2], [true, 'met']);
eq([hb([3.1, 2]).milan, hb([3.1, 2]).downstaging], [false, true]);
eq(hb([8]).downstaging, true); eq(hb([8.1]).downstaging, false);
eq(hb([5, 2, 1]).downstaging, true); eq(hb([5, 2, 1.1]).downstaging, false);        // sum ≤8
eq(hb([2.9, 2.9, 1, 1]).downstaging, true); eq(hb([3, 2, 2, 1]).downstaging, false); // 4–5 lesions each <3 cm (strict)
eq(hb([2, 2, 2, 2, 1]).downstaging, false);                                            // sum 9
eq(hb([2, 2, 2, 2, 2, 1]).downstaging, false);                                         // six lesions
eq([hb([6.5]).ucsf, hb([6.6]).ucsf, hb([4.5, 2, 1.5]).ucsf, hb([4.6, 1]).ucsf, hb([4, 2.5, 2]).ucsf], [true, false, true, false, false]);
eq(c.hccBurden({sizes: [3], spread: true}).milan, false);
eq(hb([4, 4, 4]).tbs, 5);

eq(c.tumorBurden({max: 3, n: 4}).score, 5);
eq(c.fong({node: true, dfi: true, multiple: false, size: true, cea: true}).score, 4);
eq(c.oslo({size: true, cea: false, interval: true, progression: false}).score, 2);

// Standardized FLR (Vauthey 2002): TLV = −794.41 + 1267.28 × BSA (Mosteller).
const f = c.futureRemnant({flr: 400, height: 175, weight: 80});
eq([f.bsa, f.tlv, f.percent], [1.97, 1705, 23.5]);
eq(c.futureRemnant({flr: 500, tlv: 2000}).percent, 25);
eq(c.futureRemnant({flr: 500}).ok, false);

// WHO 2019 NET grade (the pNET roadmap's table): higher index wins; NEC is not graded.
eq(c.netGrade({ki67: 2.9, mitoses: 1, diff: 'well'}).grade, 'G1');
eq(c.netGrade({ki67: 3, diff: 'well'}).grade, 'G2');
eq(c.netGrade({ki67: 20, mitoses: 2, diff: 'well'}).grade, 'G2');
eq(c.netGrade({ki67: 15, mitoses: 21, diff: 'well'}).grade, 'G3');
eq(c.netGrade({ki67: 25}).needsDiff, true);
eq(c.netGrade({diff: 'poor'}).grade, 'NEC');

// Spigelman (1989): I 1–4, II 5–6, III 7–8, IV 9–12.
const sp = (a, b, h, d) => c.spigelman({number: a, size: b, histology: h, dysplasia: d}).stage;
eq([sp('1', '1', '1', '1'), sp('2', '1', '1', '1'), sp('2', '2', '2', '1'), sp('3', '2', '2', '2'), sp('3', '3', '3', '3')], ['I', 'II', 'III', 'IV', 'IV']);

// Every item: a name, a kind, a definition with a source, and a place in the display order.
for (const [id, item] of Object.entries(S.items)) {
  const html = item.html();
  assert(item.name && item.kind && html.length > 80, id + ' definition');
  assert(/PMID \d{6,9}|OPTN|hcc\/|acr\.org/.test(html), id + ' cites a source');
  assert(S.order.includes(id), id + ' ordered');
  if (S.forms[id]) assert(item.kind === 'Calculator' || id === 'netgrade', id + ' kind');
  n++;
}
for (const id of Object.values(S.quickref)) assert(S.order.includes(id), id + ' ordered');

// Detection: named items only, and page restrictions hold.
eq(S.detect('Child-Pugh A, ECOG 0, MELD 12, Milan criteria and T2 exception', 'T:hcc'), ['meld', 'child', 'ecog', 'hccburden']);
eq(S.detect('T2-weighted MRI and the Milan consensus', 'hilar'), []);
eq(S.detect('mRECIST and RECIST 1.1', 'hcc'), ['mrecist', 'recist']);
eq(S.detect('Oslo score and Fong', 'icca'), []);
eq(S.detect('HEHE-LT registry risk', 'T:hehe'), ['hehelt']);

console.log(`PASS: ${n} checks — Child-Pugh, ALBI, Milan/T2/UNOS-downstaging/UCSF, tumor burden, Fong, Oslo, FLR, NET grade and Spigelman calculators; ${Object.keys(S.items).length} sourced definitions; detection and page limits.`);
