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
const hb = sizes => c.hccBurden({sizes, spread: false});
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
const f = c.futureRemnant({method: 'estimated', flr: 400, height: 175, weight: 80});
eq([f.bsa, f.tlv, f.percent], [1.97, 1705, 23.5]);
eq(c.futureRemnant({method: 'measured', flr: 500, tlv: 2000}).percent, 25);
eq(c.futureRemnant({flr: 500}).ok, false);

// WHO 2019 NET grade (the pNET roadmap's table): higher index wins; NEC is not graded.
eq(c.netGrade({ki67: 2.9, mitoses: 1, diff: 'well'}).grade, 'G1');
eq(c.netGrade({ki67: 3, diff: 'well'}).grade, 'G2');
eq(c.netGrade({ki67: 20, mitoses: 2, diff: 'well'}).grade, 'G2');
eq(c.netGrade({ki67: 15, mitoses: 21, diff: 'well'}).grade, 'G3');
eq(c.netGrade({ki67: 25}).ok, false);
eq(c.netGrade({diff: 'poor'}).grade, 'NEC');

// Spigelman (1989): I 1–4, II 5–6, III 7–8, IV 9–12.
const sp = (a, b, h, d) => c.spigelman({number: a, size: b, histology: h, dysplasia: d}).stage;
eq([sp('1', '1', '1', '1'), sp('2', '1', '1', '1'), sp('2', '2', '2', '1'), sp('3', '2', '2', '2'), sp('3', '3', '3', '3')], ['I', 'II', 'III', 'IV', 'IV']);

// Unknown values must not silently score as favorable; reject impossible entries.
eq(c.fong({}).ok, false);
eq(c.oslo({size: 'no', cea: 'no', interval: 'no', progression: ''}).ok, false);
eq(c.oslo({size: 'no', cea: 'no', interval: 'no', progression: 'no'}).score, 0);
eq(c.hccBurden({sizes: [3]}).ok, false);
eq(hb([3, -1]).ok, false);
eq(hb([0]).ok, false);
eq(hb([3, 'invalid']).ok, false);
eq(hb([5, 2, 1.0001]).downstaging, false); // No rounding into eligibility.
eq(hb([4.5, 2.5, 1.0001]).ucsf, false);
eq(c.albi({bilirubin: 1, albumin: 4}).ok, false);
eq(c.futureRemnant({method: 'estimated', flr: 400, height: 10, weight: 1}).ok, false);
eq(c.futureRemnant({method: 'measured', flr: 500, tlv: -1}).ok, false);
eq(c.futureRemnant({method: 'measured', flr: 2100, tlv: 2000}).ok, false);
eq(c.netGrade({ki67: -1, mitoses: 2, diff: 'well'}).ok, false);
eq(c.netGrade({ki67: 'invalid', mitoses: 2, diff: 'well'}).ok, false);
eq(c.netGrade({ki67: 101, diff: 'well'}).ok, false);
eq(c.netGrade({ki67: 2, mitoses: -1, diff: 'well'}).ok, false);
eq(c.netGrade({ki67: 2, diff: 'well'}).partial, true);
eq(c.netGrade({ki67: 2, mitoses: 2.5, diff: 'well'}).grade, 'G2');
eq(sp('0','0','0','0'), '0');
eq(c.spigelman({number: '0', size: '1', histology: '1', dysplasia: '1'}).ok, false);

// RECIST 1.1 / mRECIST overall response (Eisenhauer 2009; Lencioni 2010).
const resp = (o) => c.response({criteria: 'recist', baseline: 100, nadir: '', current: 100, gone: 'no', nontarget: 'non', newLesion: 'no', ...o});
eq(resp({current: 70}).overall, 'PR');                                   // −30% from baseline
eq(resp({current: 71}).overall, 'SD');
eq(resp({baseline: 30, nadir: 20, current: 24}).target, 'SD');           // +20% from the smallest sum but only 4 mm
eq(resp({nadir: 20, current: 24}).target, 'PR');                         // still 76% below baseline and not progression
eq(resp({baseline: 30, nadir: 20, current: 25}).target, 'PD');           // +25% and 5 mm
eq(resp({criteria: 'mrecist', baseline: 30, nadir: 20, current: 24}).target, 'PD'); // mRECIST: 20% without the 5 mm rule
eq(resp({nadir: 0, current: 5}).target, 'PD');                           // reappearance after complete response
eq(resp({current: 0, gone: 'yes', nontarget: 'absent'}).overall, 'CR');
eq(resp({current: 0, gone: 'yes', nontarget: 'non'}).overall, 'PR');      // RECIST table: target CR, non-target persisting
eq(resp({current: 50, newLesion: 'yes'}).overall, 'PD');                  // a new lesion overrides the sums
eq(resp({current: 50, nontarget: 'pd'}).overall, 'PD');
eq(resp({criteria: 'mrecist', current: 3, gone: 'yes', nontarget: 'absent'}).ok, false); // mRECIST CR leaves no viable tumor
eq(resp({nadir: 120}).ok, false); eq(resp({gone: ''}).ok, false); eq(resp({nontarget: ''}).ok, false); eq(resp({newLesion: ''}).ok, false);

// RETREAT (Mehta 2017, Table 3).
eq(c.retreat({afp: 20, mvi: 'no', count: 0, largest: ''}).score, 0);
eq(c.retreat({afp: 21, mvi: 'no', count: 0}).pAfp, 1);
eq(c.retreat({afp: 999, mvi: 'no', count: 0}).pAfp, 2);
eq(c.retreat({afp: 1000, mvi: 'yes', count: 3, largest: 7}), {ok: true, score: 8, pAfp: 3, pMvi: 2, pSum: 3, sum: 10});
eq(c.retreat({afp: 5, mvi: 'no', count: 1, largest: 3.9}).pSum, 1);       // 4.9
eq(c.retreat({afp: 5, mvi: 'no', count: 2, largest: 3}).pSum, 2);         // 5.0
eq(c.retreat({afp: 5, mvi: '', count: 1, largest: 2}).ok, false);
eq(c.retreat({afp: 5, mvi: 'no', count: 0, largest: 2}).ok, false);

// French AFP model (Duvoux 2012) and Metroticket 2.0 (Mazzaferro 2018).
eq(c.afpModel({largest: 3, number: 3, afp: 100}).score, 0);
eq(c.afpModel({largest: 6, number: 4, afp: 1000}).score, 5);
eq(c.afpModel({largest: 6.1, number: 1, afp: 1001}), {ok: true, score: 7, pd: 4, pn: 0, pa: 3, high: true});
eq(c.afpModel({largest: 2, number: 0, afp: 5}).ok, false);
eq([c.metroticket({afp: 199, number: 2, largest: 5}).within, c.metroticket({afp: 199, number: 2, largest: 5.1}).within], [true, false]);
eq([c.metroticket({afp: 200, number: 2, largest: 3}).limit, c.metroticket({afp: 400, number: 1, largest: 3}).limit, c.metroticket({afp: 1000, number: 1, largest: 3}).limit], [5, 4, 4]);
eq(c.metroticket({afp: 1001, number: 1, largest: 1}).within, false);
eq(c.metroticket({afp: 50, number: 0, largest: ''}).sum, 0);

// Intervals: complete calendar months, end-of-month targets, no negative intervals.
eq(c.interval({start: '2026-04-30', end: '2026-10-29', required: '6'}).months, 5);
eq(c.interval({start: '2026-04-30', end: '2026-10-30', required: '6'}).reached, {months: 6, date: '2026-10-30', met: true});
eq(c.interval({start: '2026-08-31', end: '2027-02-28', required: '6'}).reached.date, '2027-02-28');
eq(c.interval({start: '2026-01-01', end: '', today: '2026-01-15'}).days, 14);
eq(c.interval({start: '2026-02-30', end: '2026-03-01'}).ok, false);
eq(c.interval({start: '2026-05-01', end: '2026-04-01'}).ok, false);

// Marker trend: first-to-last change, doubling time by log-linear fit, incomplete rows rejected.
const mt = c.markerTrend({points: [{date: '2026-01-01', value: '10'}, {date: '2026-01-31', value: '20'}, {date: '2026-03-02', value: '40'}]});
eq([mt.change, mt.doublingDays, mt.days], [300, 30, 60]);
eq(c.markerTrend({points: [{date: '2026-01-01', value: '40'}, {date: '2026-01-31', value: '20'}]}).doublingDays, -30);
eq(c.markerTrend({points: [{date: '2026-01-01', value: '4'}, {date: '', value: '5'}]}).ok, false);
eq(c.markerTrend({points: [{date: '2026-01-01', value: '4'}, {date: '2026-01-01', value: '5'}]}).ok, false);

// Liver involvement and treatable share.
eq(c.liverInvolvement({total: 2000, tumor: 500, treatable: 450}), {ok: true, involvement: 25, treatable: 90});
eq(c.liverInvolvement({total: 2000, tumor: 500, treatable: ''}).treatable, null);
eq(c.liverInvolvement({total: 2000, tumor: 2500}).ok, false);
eq(c.liverInvolvement({total: 2000, tumor: 500, treatable: 600}).ok, false);

// Every item: a name, a kind, a definition with a source (or the roadmap table it shows), and a place in the display order.
const FORM_KINDS = ['Calculator', 'Response criteria', 'Prognostic score', 'Date calculator'];
for (const [id, item] of Object.entries(S.items)) {
  const html = item.html();
  assert(item.name && item.kind && (item.shared || html.length > 80), id + ' definition');
  assert(item.shared || item.lrt || ['interval', 'markers'].includes(id) || /PMID \d{6,9}|OPTN|hcc\/|acr\.org|livervolume\.com|facs\.org/.test(html), id + ' cites a source');
  assert(S.order.includes(id), id + ' ordered');
  if (S.forms[id]) assert(FORM_KINDS.includes(item.kind) || id === 'netgrade', id + ' kind');
  n++;
}
assert(!S.forms.flr, 'LiverVolume.com replaces the local FLR calculator');
for (const [page, map] of Object.entries(S.extra)) for (const ids of Object.values(map)) for (const id of ids) assert(S.items[id], page + ' places unknown item ' + id);
const shared = S.renderQuickref({title: 't', intro: 'i', rows: [['a', 'b <c>']], foot: 'PMID 12345678'}, 'hilar');
assert(shared.includes('b &lt;c&gt;') && shared.includes('PMID 12345678') && shared.includes('hilar/'), 'shared tables escape text and keep PMIDs and the roadmap link');
for (const id of Object.values(S.quickref)) assert(S.order.includes(id), id + ' ordered');

// Detection: named items only, and page restrictions hold.
eq(S.detect('Child-Pugh A, ECOG 0, MELD 12, Milan criteria and T2 exception', 'T:hcc'), ['meld', 'child', 'ecog', 'hccburden']);
eq(S.detect('T2-weighted MRI and the Milan consensus', 'hilar'), []);
eq(S.detect('mRECIST and RECIST 1.1', 'hcc'), ['mrecist', 'recist']);
eq(S.detect('Oslo score and Fong', 'icca'), []);
eq(S.detect('HEHE-LT registry risk', 'T:hehe'), ['hehelt']);

console.log(`PASS: ${n} checks — Child-Pugh, ALBI, Milan/T2/UNOS-downstaging/UCSF, tumor burden, Fong, Oslo, FLR, NET grade, Spigelman, RECIST/mRECIST response, RETREAT, AFP model, Metroticket 2.0, interval, marker-trend and liver-involvement calculators; ${Object.keys(S.items).length} sourced definitions; detection and page limits.`);
