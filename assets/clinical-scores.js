/* Scores, classifications and calculators for the Tools column (Analyst B, 28 October 2026).
   Reference only: nothing is stored, nothing is applied to a pathway, and no result establishes
   eligibility. Where a roadmap or transplant protocol already defines an item, the Tools column shows
   that page's own text and adds the calculator beside it (tools-column.js). Definitions here follow
   their cited source; the HCC tumor-burden rules use the wording of the transplant HCC protocol. */
(function (root) {
  'use strict';
  const ref = root.ClinicalReference || null;
  const esc = s => String(s ?? '').replace(/[&<>"']/g, c => ({'&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;'}[c]));
  const pm = (id, label) => `<a href="https://pubmed.ncbi.nlm.nih.gov/${id}/" target="_blank" rel="noopener">${esc(label)} · PMID ${id} ↗</a>`;
  const web = (url, label) => `<a href="${esc(url)}" target="_blank" rel="noopener">${esc(label)} ↗</a>`;
  const src = (...links) => `<p class="tc-src">${links.join(' · ')}</p>`;
  const num = x => (x === undefined || x === null || String(x).trim() === '' || !Number.isFinite(Number(x))) ? null : Number(x);
  const round = (x, d = 2) => Math.round(x * 10 ** d) / 10 ** d;
  const fail = message => ({ok: false, message});
  const answered = x => x === true || x === false || x === 'yes' || x === 'no';
  const positive = x => x === true || x === 'yes';
  const OPTN = 'https://www.hrsa.gov/sites/default/files/hrsa/optn/optn_policies.pdf';
  const NLRB = 'https://www.hrsa.gov/sites/default/files/hrsa/optn/adult-meld-exception-transplant-oncology-review-guidance.pdf';
  const NEVER = /$^/;
  const extLink = (url, label) => `<p class="tc-ext"><a class="tc-ext-link" href="${esc(url)}" target="_blank" rel="noopener">${esc(label)} ↗</a></p>`;
  // Exception scores, verified against OPTN Policy 9 (Tables 9-2, 9-10) and the NLRB transplant oncology guidance.
  const MELD_EXCEPTIONS = [
    ['hcc', 'HCC (T2, OPTN standardized)', 'Calculated MELD at the initial request and first extension; MMaT − 3 from the second extension', 'OPTN Policy 9.5 · Table 9-10'],
    ['pcca', 'Perihilar cholangiocarcinoma (OPTN standardized protocol)', 'MMaT − 3', 'OPTN Policy 9.5 · Table 9-2'],
    ['icca', 'Intrahepatic cholangiocarcinoma ≤3 cm in cirrhosis', 'MMaT − 3', 'NLRB guidance'],
    ['nelm', 'Neuroendocrine liver metastases', 'MMaT − 3', 'NLRB guidance'],
    ['crlm', 'Colorectal liver metastases', 'MMaT − 20; a result below 15 is set to 15', 'NLRB guidance'],
    ['hehe', 'Hepatic epithelioid hemangioendothelioma', 'MMaT − 3', 'NLRB guidance'],
    ['hca', 'Hepatocellular adenoma', 'MMaT − 3', 'NLRB guidance']];
  let pageSlug = '';

  /* ---------- Pure calculators (unit-tested in tools/test_clinical_scores.cjs) ---------- */

  // Child-Pugh: the standard table shown in ClinicalReference.terms.child.
  function childPugh(v) {
    const bili = num(v.bilirubin), alb = num(v.albumin), inr = num(v.inr);
    if (bili === null || alb === null || inr === null || bili <= 0 || alb <= 0 || inr <= 0) return fail('Enter bilirubin, albumin and INR.');
    if (!['1', '2', '3'].includes(String(v.ascites)) || !['1', '2', '3'].includes(String(v.enceph))) return fail('Choose ascites and encephalopathy.');
    const parts = {
      bilirubin: bili < 2 ? 1 : bili <= 3 ? 2 : 3,
      albumin: alb > 3.5 ? 1 : alb >= 2.8 ? 2 : 3,
      inr: inr < 1.7 ? 1 : inr <= 2.3 ? 2 : 3,
      ascites: Number(v.ascites), enceph: Number(v.enceph)
    };
    const score = Object.values(parts).reduce((a, b) => a + b, 0);
    return {ok: true, score, cls: score <= 6 ? 'A' : score <= 9 ? 'B' : 'C', parts};
  }

  // ALBI = log10(bilirubin µmol/L) × 0.66 + albumin g/L × −0.085 (Johnson 2015).
  function albi(v) {
    let bili = num(v.bilirubin), alb = num(v.albumin);
    if (bili === null || alb === null || bili <= 0 || alb <= 0) return fail('Enter bilirubin and albumin.');
    if (!['mgdl', 'umol'].includes(v.biliUnit) || !['gdl', 'gl'].includes(v.albUnit)) return fail('Choose both laboratory units.');
    if (v.biliUnit === 'mgdl') bili *= 17.1;
    if (v.albUnit === 'gdl') alb *= 10;
    const score = Math.log10(bili) * 0.66 + alb * -0.085;
    return {ok: true, score: round(score), grade: score <= -2.6 ? 1 : score <= -1.39 ? 2 : 3, bilirubinUmol: round(bili, 1), albuminGl: round(alb, 1)};
  }

  // HCC tumor burden: Milan, T2, UNOS downstaging and UCSF from qualifying lesion diameters (cm).
  function hccBurden(v) {
    const entered = (v.sizes || []).filter(x => x !== null && x !== undefined && String(x).trim() !== '');
    const sizes = entered.map(num);
    if (sizes.some(x => x === null || x <= 0)) return fail('Each entered lesion diameter must be a positive number. Leave unused fields blank.');
    if (!sizes.length) return fail('Enter the diameter of each qualifying lesion.');
    if (!answered(v.spread)) return fail('Confirm whether macrovascular invasion or extrahepatic disease is present.');
    const n = sizes.length, max = Math.max(...sizes), sum = sizes.reduce((a, b) => a + b, 0), spread = positive(v.spread);
    const milan = !spread && ((n === 1 && max <= 5) || (n >= 2 && n <= 3 && max <= 3));
    let t2 = 'not met';
    if (!spread && n === 1 && max >= 2 && max <= 5) t2 = 'met';
    else if (!spread && n === 1 && max >= 1 && max < 2) t2 = 'T1';
    else if (!spread && n >= 2 && n <= 3 && sizes.every(x => x >= 1 && x <= 3)) t2 = 'met';
    const downstaging = !spread && ((n === 1 && max > 5 && max <= 8) ||
      (n >= 2 && n <= 3 && max > 3 && max <= 5 && sum <= 8) ||
      (n >= 4 && n <= 5 && max < 3 && sum <= 8));
    const ucsf = !spread && ((n === 1 && max <= 6.5) || (n >= 2 && n <= 3 && max <= 4.5 && sum <= 8));
    return {ok: true, n, max, sum, milan, t2, downstaging, ucsf, tbs: round(Math.sqrt(max ** 2 + n ** 2)), under1: sizes.some(x => x < 1)};
  }

  // Tumor burden score: distance from the origin, largest diameter (cm) and number of tumors (Sasaki 2018).
  function tumorBurden(v) {
    const max = num(v.max), n = num(v.n);
    if (max === null || n === null || max <= 0 || n < 1 || !Number.isInteger(n)) return fail('Enter the largest diameter and a whole number of tumors.');
    return {ok: true, score: round(Math.sqrt(max ** 2 + n ** 2))};
  }

  const points = (v, keys) => keys.some(k => !answered(v[k])) ? fail('Choose Yes or No for every factor; an unanswered factor is not zero.') : {ok: true, score: keys.reduce((a, k) => a + (positive(v[k]) ? 1 : 0), 0)};
  // Fong clinical risk score: five factors, one point each (Fong 1999).
  const fong = v => points(v, ['node', 'dfi', 'multiple', 'size', 'cea']);
  // Oslo score: four factors, one point each (Dueland 2020).
  const oslo = v => points(v, ['size', 'cea', 'interval', 'progression']);

  // Standardized future liver remnant: FLR volume / total liver volume, TLV = −794.41 + 1267.28 × BSA (Vauthey 2002).
  function futureRemnant(v) {
    const flr = num(v.flr), height = num(v.height), weight = num(v.weight), measured = num(v.tlv);
    if (flr === null || flr <= 0) return fail('Enter the future liver remnant volume (mL).');
    if (!['estimated', 'measured'].includes(v.method)) return fail('Choose the liver-volume method.');
    let tlv = measured, bsa = null;
    if (v.method === 'estimated') {
      if (height === null || weight === null || height <= 0 || weight <= 0) return fail('Enter height and weight for the estimated-volume method.');
      bsa = Math.sqrt(height * weight / 3600);
      tlv = -794.41 + 1267.28 * bsa;
    }
    if (tlv === null || !Number.isFinite(tlv) || tlv <= 0) return fail('The denominator must be a positive liver volume. Check the inputs and units.');
    if (flr > tlv) return fail('The remnant exceeds the total liver volume. Check the measurements and method.');
    return {ok: true, bsa: bsa === null ? null : round(bsa), tlv: Math.round(tlv), percent: round(flr / tlv * 100, 1), estimated: bsa !== null};
  }

  // WHO 2019 grade of a well-differentiated NET; the higher grade wins when Ki-67 and mitoses disagree.
  function netGrade(v) {
    if (!['well', 'poor'].includes(v.diff)) return fail('Confirm differentiation before assigning NET grade.');
    if (v.diff === 'poor') return {ok: true, grade: 'NEC', text: 'Neuroendocrine carcinoma: high grade by definition, not graded G1–G3'};
    const ki = num(v.ki67), mit = num(v.mitoses);
    if ([[v.ki67, ki], [v.mitoses, mit]].some(([raw, value]) => raw != null && String(raw).trim() !== '' && value === null)) return fail('Enter numeric proliferation indices, or leave an unavailable index blank.');
    if ((ki !== null && (ki < 0 || ki > 100)) || (mit !== null && mit < 0)) return fail('Ki-67 must be 0–100%; mitoses per 2 mm² cannot be negative.');
    if (ki === null && mit === null) return fail('Enter Ki-67 and/or the mitotic count.');
    const g = (x, low, high) => x === null ? 0 : x < low ? 1 : x <= high ? 2 : 3;
    const grade = Math.max(g(ki, 3, 20), g(mit, 2, 20));
    return {ok: true, grade: 'G' + grade, byKi: g(ki, 3, 20) || null, byMitoses: g(mit, 2, 20) || null, partial: ki === null || mit === null};
  }

  // Spigelman stage of duodenal polyposis: number, size, histology, dysplasia (Spigelman 1989).
  function spigelman(v) {
    const keys = ['number', 'size', 'histology', 'dysplasia'];
    if (keys.every(k => String(v[k]) === '0')) return {ok: true, score: 0, stage: '0'};
    if (keys.some(k => !['1', '2', '3'].includes(String(v[k])))) return fail('Choose all four features.');
    const score = keys.reduce((a, k) => a + Number(v[k]), 0);
    return {ok: true, score, stage: score <= 4 ? 'I' : score <= 6 ? 'II' : score <= 8 ? 'III' : 'IV'};
  }

  // Overall response by RECIST 1.1 (Eisenhauer 2009) or mRECIST (Lencioni 2010) from sums of diameters (mm).
  // New lesions and unequivocal non-target progression are progression whatever the sums show.
  function response(v) {
    const c = v.criteria;
    if (!['recist', 'mrecist'].includes(c)) return fail('Choose RECIST 1.1 or mRECIST.');
    const base = num(v.baseline), cur = num(v.current);
    let nadir = num(v.nadir);
    if (base === null || base <= 0) return fail('Enter the baseline sum of target-lesion diameters (mm).');
    if (cur === null || cur < 0) return fail('Enter the current sum (mm); enter 0 when no measurable target disease remains.');
    if (v.nadir != null && String(v.nadir).trim() !== '' && (nadir === null || nadir < 0)) return fail('The smallest previous sum must be a number of mm, or left blank.');
    if (nadir === null) nadir = base;
    if (nadir > base) return fail('The smallest previous sum cannot exceed the baseline sum: the baseline is part of that comparison.');
    if (!answered(v.gone)) return fail(c === 'recist' ? 'Confirm whether every target lesion has disappeared (target nodes under 10 mm short axis).' : 'Confirm whether arterial enhancement has disappeared from every target lesion.');
    if (!['absent', 'cr', 'non', 'pd'].includes(v.nontarget)) return fail('Choose the non-target status.');
    if (!answered(v.newLesion)) return fail('Confirm whether an unequivocal new lesion is present.');
    const gone = positive(v.gone);
    if (gone && c === 'mrecist' && cur > 0) return fail('An mRECIST complete response leaves no viable (enhancing) target tumor: the current viable sum should be 0.');
    const fromBase = (cur - base) / base * 100, abs = cur - nadir, fromNadir = nadir > 0 ? abs / nadir * 100 : null;
    let target;
    if (gone) target = 'CR';
    else if (nadir === 0 && cur > 0) target = 'PD';
    else if (fromNadir !== null && fromNadir >= 20 && (c === 'mrecist' || abs >= 5)) target = 'PD';
    else if (fromBase <= -30) target = 'PR';
    else target = 'SD';
    let overall;
    if (positive(v.newLesion) || v.nontarget === 'pd' || target === 'PD') overall = 'PD';
    else if (target === 'CR') overall = ['absent', 'cr'].includes(v.nontarget) ? 'CR' : 'PR';
    else overall = target;
    return {ok: true, criteria: c, target, overall, fromBase: round(fromBase, 1), fromNadir: fromNadir === null ? null : round(fromNadir, 1), abs: round(abs, 1), nadir, reappeared: nadir === 0 && cur > 0};
  }

  // RETREAT (Mehta 2017, Table 3): AFP at transplant, explant microvascular invasion, largest viable diameter + number of viable tumors.
  function retreat(v) {
    const afp = num(v.afp), n = num(v.count), d = num(v.largest);
    if (afp === null || afp < 0) return fail('Enter AFP at transplant (ng/mL).');
    if (!answered(v.mvi)) return fail('Confirm microvascular invasion on the explant.');
    if (n === null || n < 0 || !Number.isInteger(n)) return fail('Enter the number of viable tumors on the explant (0 if none).');
    if (n > 0 && (d === null || d <= 0)) return fail('Enter the largest viable tumor diameter (cm).');
    if (n === 0 && d !== null && d > 0) return fail('With no viable tumor the largest viable diameter is 0. Check the explant entries.');
    const sum = n === 0 ? 0 : d + n;
    const pAfp = afp <= 20 ? 0 : afp < 100 ? 1 : afp < 1000 ? 2 : 3, pMvi = positive(v.mvi) ? 2 : 0, pSum = sum === 0 ? 0 : sum < 5 ? 1 : sum < 10 ? 2 : 3;
    return {ok: true, score: pAfp + pMvi + pSum, pAfp, pMvi, pSum, sum: round(sum, 1)};
  }

  // French AFP model (Duvoux 2012): largest diameter, number of tumors and AFP; a score above 2 is high risk.
  function afpModel(v) {
    const d = num(v.largest), n = num(v.number), afp = num(v.afp);
    if (d === null || d <= 0) return fail('Enter the largest tumor diameter (cm).');
    if (n === null || n < 1 || !Number.isInteger(n)) return fail('Enter the number of tumors (a whole number, at least 1).');
    if (afp === null || afp < 0) return fail('Enter AFP (ng/mL).');
    const pd = d <= 3 ? 0 : d <= 6 ? 1 : 4, pn = n <= 3 ? 0 : 2, pa = afp <= 100 ? 0 : afp <= 1000 ? 2 : 3;
    return {ok: true, score: pd + pn + pa, pd, pn, pa, high: pd + pn + pa > 2};
  }

  // Metroticket 2.0 (Mazzaferro 2018): number of viable tumors + largest viable diameter (cm) within an AFP-adjusted limit.
  function metroticket(v) {
    const afp = num(v.afp), n = num(v.number), d = num(v.largest);
    if (afp === null || afp < 0) return fail('Enter AFP (ng/mL).');
    if (n === null || n < 0 || !Number.isInteger(n)) return fail('Enter the number of viable tumors (0 after a complete response).');
    if (n > 0 && (d === null || d <= 0)) return fail('Enter the largest viable tumor diameter (cm).');
    if (n === 0 && d !== null && d > 0) return fail('With no viable tumor the size is 0. Check the entries.');
    const sum = n === 0 ? 0 : n + d, limit = afp < 200 ? 7 : afp < 400 ? 5 : afp <= 1000 ? 4 : null;
    return {ok: true, sum: round(sum, 1), limit, within: limit !== null && sum <= limit, sharedBoundary: afp === 400};
  }

  // Calendar intervals between two dates (yyyy-mm-dd). `today` is supplied by the form so the function stays pure.
  function parseDate(s) {
    if (!s || !/^\d{4}-\d{2}-\d{2}$/.test(String(s))) return null;
    const [y, m, d] = String(s).split('-').map(Number), t = Date.UTC(y, m - 1, d), dt = new Date(t);
    return dt.getUTCFullYear() === y && dt.getUTCMonth() === m - 1 && dt.getUTCDate() === d ? {y, m, d, t} : null;
  }
  const iso = t => new Date(t).toISOString().slice(0, 10);
  function addMonths(a, k) {
    const total = a.m - 1 + k, y = a.y + Math.floor(total / 12), m = ((total % 12) + 12) % 12;
    const last = new Date(Date.UTC(y, m + 1, 0)).getUTCDate();
    return Date.UTC(y, m, Math.min(a.d, last));
  }
  function interval(v) {
    const a = parseDate(v.start);
    if (!a) return fail('Enter the start date.');
    const b = String(v.end || '').trim() ? parseDate(v.end) : parseDate(v.today);
    if (!b) return fail('Enter a valid end date, or leave it blank to use today.');
    if (b.t < a.t) return fail('The end date is before the start date.');
    const days = Math.round((b.t - a.t) / 86400000);
    let months = (b.y - a.y) * 12 + (b.m - a.m);
    if (b.d < a.d) months--;
    const need = num(v.required);
    let reached = null;
    if (need) { const t = addMonths(a, need); reached = {months: need, date: iso(t), met: b.t >= t}; }
    return {ok: true, days, weeks: round(days / 7, 1), months, end: iso(b.t), endIsToday: !String(v.end || '').trim(), reached};
  }

  // Tumor-marker trend: change from first to last value, change per month and the log-linear doubling or halving time.
  function markerTrend(v) {
    const pts = [];
    for (const p of v.points || []) {
      const hasD = p.date && String(p.date).trim(), hasV = p.value != null && String(p.value).trim() !== '';
      if (!hasD && !hasV) continue;
      if (!hasD || !hasV) return fail('Each row needs both a date and a value.');
      const d = parseDate(p.date), x = num(p.value);
      if (!d) return fail('Enter valid dates.');
      if (x === null || x < 0) return fail('Values must be zero or positive numbers.');
      pts.push({t: d.t, date: iso(d.t), x});
    }
    if (pts.length < 2) return fail('Enter at least two dated values.');
    pts.sort((a, b) => a.t - b.t);
    if (new Set(pts.map(p => p.t)).size !== pts.length) return fail('Two values share a date; keep one value per date.');
    const first = pts[0], last = pts[pts.length - 1], days = (last.t - first.t) / 86400000;
    let doublingDays = null;
    if (pts.every(p => p.x > 0)) {
      const xs = pts.map(p => (p.t - first.t) / 86400000), ys = pts.map(p => Math.log(p.x));
      const mx = xs.reduce((a, b) => a + b, 0) / xs.length, my = ys.reduce((a, b) => a + b, 0) / ys.length;
      const k = xs.reduce((s, x, i) => s + (x - mx) * (ys[i] - my), 0) / xs.reduce((s, x) => s + (x - mx) ** 2, 0);
      if (Math.abs(k) > 1e-9) doublingDays = Math.round(Math.LN2 / k);
    }
    return {ok: true, n: pts.length, first, last, days: Math.round(days),
      change: first.x > 0 ? round((last.x - first.x) / first.x * 100, 1) : null,
      perMonth: round((last.x - first.x) / (days / 30.4375), 2), doublingDays, pts};
  }

  // Liver involvement and the treatable share of tumor, from volumes (mL).
  function liverInvolvement(v) {
    const total = num(v.total), tumor = num(v.tumor), treat = num(v.treatable);
    if (total === null || total <= 0) return fail('Enter the total liver volume including tumor (mL).');
    if (tumor === null || tumor < 0) return fail('Enter the total tumor volume (mL).');
    if (tumor > total) return fail('Tumor volume cannot exceed the total liver volume.');
    const rawT = v.treatable != null && String(v.treatable).trim() !== '';
    if (rawT && (treat === null || treat < 0 || treat > tumor)) return fail('Removable or treatable tumor volume must lie between 0 and the total tumor volume.');
    return {ok: true, involvement: round(tumor / total * 100, 1), treatable: rawT && tumor > 0 ? round(treat / tumor * 100, 1) : null};
  }

  /* ---------- Calculator forms: fields and how a result reads ---------- */
  const yes = (id, label) => ({id, label, type: 'select', options: [['', 'Choose'], ['no', 'No'], ['yes', 'Yes']]});
  const MARKER_NOTE = {
    afp: 'AFP can also rise with hepatitis activity or liver regeneration; read the trend with imaging.',
    cea: 'CEA can also rise with smoking and some benign conditions; read the trend with imaging.',
    ca199: 'Biliary obstruction or cholangitis can raise CA19-9: recheck after drainage. Lewis antigen-negative patients do not produce CA19-9.'};
  const RESPONSE = {CR: 'complete response', PR: 'partial response', SD: 'stable disease', PD: 'progressive disease'};
  function responseForm(criteria) {
    const m = criteria === 'mrecist';
    return {fields: [
      {id: 'baseline', label: m ? 'Baseline sum of viable diameters' : 'Baseline sum of diameters', unit: 'mm', type: 'number', step: '1'},
      {id: 'nadir', label: 'Smallest sum since, if lower', unit: 'mm', type: 'number', step: '1'},
      {id: 'current', label: m ? 'Current sum of viable diameters' : 'Current sum of diameters', unit: 'mm', type: 'number', step: '1'},
      yes('gone', m ? 'Arterial enhancement gone from every target lesion' : 'Every target lesion gone (target nodes under 10 mm short axis)'),
      {id: 'nontarget', label: 'Non-target lesions', type: 'select', options: [['', 'Choose'], ['absent', 'None present'], ['cr', 'All gone'], ['non', 'Persisting or not all assessed, no unequivocal progression'], ['pd', 'Unequivocal progression']]},
      yes('newLesion', m ? 'Unequivocal new lesion meeting mRECIST criteria' : 'Unequivocal new lesion')
    ], collect: v => ({...v, criteria}), run: response,
    read: r => [`${m ? 'mRECIST' : 'RECIST 1.1'} overall response: ${RESPONSE[r.overall]}`,
      `Target lesions: ${RESPONSE[r.target]} · ${r.fromBase > 0 ? '+' : ''}${r.fromBase}% from baseline${r.fromNadir === null ? '' : ` · ${r.fromNadir > 0 ? '+' : ''}${r.fromNadir}% (${r.abs > 0 ? '+' : ''}${r.abs} mm) from the smallest sum`}`]
      .concat(r.reappeared ? ['A target lesion reappeared after complete disappearance: progression.'] : [])
      .concat(r.overall === 'PD' && r.target !== 'PD' ? ['Progression is set by the new lesion or non-target finding, whatever the sums show.'] : [])
      .concat([m ? 'mRECIST measures viable (arterially enhancing) tumor; progression is a 20% increase from the smallest sum.' : 'Progression needs at least a 20% and 5 mm increase from the smallest sum; partial response a 30% decrease from baseline.'])};
  }
  function localToday() { const d = new Date(); return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`; }
  // A small inline chart of a marker series: dates on x, values on y from zero. Built from numbers only.
  function sparkline(r) {
    const W = 260, H = 96, P = 10, t0 = r.pts[0].t, t1 = r.pts[r.pts.length - 1].t, ymax = Math.max(...r.pts.map(p => p.x)) || 1;
    const X = t => P + (t1 === t0 ? 0 : (t - t0) / (t1 - t0)) * (W - 2 * P), Y = x => H - P - x / ymax * (H - 2 * P);
    const line = r.pts.map(p => `${X(p.t).toFixed(1)},${Y(p.x).toFixed(1)}`).join(' ');
    const dots = r.pts.map(p => `<circle cx="${X(p.t).toFixed(1)}" cy="${Y(p.x).toFixed(1)}" r="3"><title>${p.date}: ${p.x}</title></circle>`).join('');
    return `<svg class="tc-spark" viewBox="0 0 ${W} ${H}" role="img" aria-label="Marker values from ${r.first.date} to ${r.last.date}"><line x1="${P}" y1="${H - P}" x2="${W - P}" y2="${H - P}" class="tc-spark-axis"/><polyline points="${line}" class="tc-spark-line"/>${dots}<text x="${W - P}" y="${P}" text-anchor="end" class="tc-spark-label">highest ${ymax}</text></svg>`;
  }
  const FORMS = {
    child: {fields: [
      {id: 'bilirubin', label: 'Bilirubin', unit: 'mg/dL', type: 'number', step: '0.1'},
      {id: 'albumin', label: 'Albumin', unit: 'g/dL', type: 'number', step: '0.1'},
      {id: 'inr', label: 'INR', type: 'number', step: '0.1'},
      {id: 'ascites', label: 'Ascites', type: 'select', options: [['', 'Choose'], ['1', 'None'], ['2', 'Mild/moderate; responds to diuretics'], ['3', 'Severe; refractory to diuretics']]},
      {id: 'enceph', label: 'Encephalopathy', type: 'select', options: [['', 'Choose'], ['1', 'None'], ['2', 'Grade I–II'], ['3', 'Grade III–IV']]}
    ], run: childPugh, read: r => `Child-Pugh ${r.score} points · class ${r.cls}`},
    albi: {fields: [
      {id: 'bilirubin', label: 'Bilirubin', type: 'number', step: '0.1'},
      {id: 'biliUnit', label: 'Bilirubin unit', type: 'select', options: [['mgdl', 'mg/dL'], ['umol', 'µmol/L']]},
      {id: 'albumin', label: 'Albumin', type: 'number', step: '0.1'},
      {id: 'albUnit', label: 'Albumin unit', type: 'select', options: [['gdl', 'g/dL'], ['gl', 'g/L']]}
    ], run: albi, read: r => [`ALBI ${r.score.toFixed(2)} · grade ${r.grade}`, 'Grade uses the unrounded score.']},
    hccburden: {fields: [
      ...[1, 2, 3, 4, 5, 6].map(i => ({id: 'size' + i, label: 'Lesion ' + i, unit: 'cm', type: 'number', step: '0.1'})),
      yes('spread', 'Macrovascular invasion or extrahepatic disease')
    ], collect: v => ({sizes: [1, 2, 3, 4, 5, 6].map(i => v['size' + i]), spread: v.spread}), run: hccBurden,
    read: r => [`${r.n} lesion${r.n > 1 ? 's' : ''}, largest ${r.max} cm, sum ${round(r.sum, 4)} cm`,
      `Milan: ${r.milan ? 'within' : 'outside'}`,
      `T2: ${r.t2 === 'met' ? 'size criteria met' : r.t2 === 'T1' ? 'T1 (single 1 to <2 cm)' : 'not met'}`,
      `UNOS downstaging (pretreatment): ${r.milan ? 'not needed (within Milan)' : r.downstaging ? 'within' : 'outside'}`,
      `UCSF: ${r.ucsf ? 'within' : 'outside'}`,
      `Tumor burden score: ${r.tbs.toFixed(2)}`].concat(r.under1 ? ['Lesions under 1 cm do not satisfy the T2 minimum lesion size. Confirm which observations are qualifying HCCs.'] : [])},
    tbs: {fields: [{id: 'max', label: 'Largest tumor', unit: 'cm', type: 'number', step: '0.1'}, {id: 'n', label: 'Number of tumors', type: 'number', step: '1'}],
      run: tumorBurden, read: r => `Tumor burden score ${r.score.toFixed(2)}`},
    fong: {fields: [yes('node', 'Node-positive primary'), yes('dfi', 'Primary resection to liver metastasis diagnosis under 12 months'), yes('multiple', 'More than one hepatic tumor'), yes('size', 'Largest tumor over 5 cm'), yes('cea', 'CEA over 200 ng/mL')],
      run: fong, read: r => [`Clinical risk score ${r.score} of 5`, 'Scores 0–2 are usually reported as low risk and 3–5 as high risk.']},
    oslo: {fields: [yes('size', 'Largest lesion over 5.5 cm'), yes('cea', 'CEA over 80 µg/L'), yes('interval', 'Under 2 years from primary resection to transplant'), yes('progression', 'Progressive disease on chemotherapy at transplant')],
      run: oslo, read: r => [`Oslo score ${r.score} of 4`, 'Prognostic only: a low score does not relax an eligibility requirement.']},
    recist: responseForm('recist'),
    mrecist: responseForm('mrecist'),
    retreat: {fields: [
      {id: 'afp', label: 'AFP at transplant', unit: 'ng/mL', type: 'number', step: '0.1'},
      yes('mvi', 'Microvascular invasion on the explant'),
      {id: 'count', label: 'Number of viable tumors on the explant', type: 'number', step: '1'},
      {id: 'largest', label: 'Largest viable tumor diameter', unit: 'cm', type: 'number', step: '0.1'}
    ], run: retreat, read: r => [`RETREAT ${r.score} of 8 (AFP ${r.pAfp} + microvascular invasion ${r.pMvi} + viable tumor ${r.pSum}; viable sum ${r.sum})`,
      r.score === 0 ? 'Derivation paper: 5-year recurrence under 3% at 0; its authors proposed no routine surveillance.'
        : r.score <= 3 ? 'Surveillance proposed by the derivation paper: multiphasic CT or MRI, chest CT and AFP every 6 months for 2 years.'
        : r.score === 4 ? 'Surveillance proposed by the derivation paper: multiphasic CT or MRI, chest CT and AFP every 6 months for 5 years.'
        : 'Surveillance proposed by the derivation paper: every 3–4 months for 2 years, then every 6 months to year 5. 5-year recurrence exceeded 75% at 5 or more.',
      'Derived in recipients within Milan on imaging; an external cohort found weaker discrimination when the explant was beyond Milan.']},
    afpmodel: {fields: [
      {id: 'largest', label: 'Largest tumor diameter', unit: 'cm', type: 'number', step: '0.1'},
      {id: 'number', label: 'Number of tumors', type: 'number', step: '1'},
      {id: 'afp', label: 'AFP', unit: 'ng/mL', type: 'number', step: '0.1'}
    ], run: afpModel, read: r => [`AFP model ${r.score} (size ${r.pd} + number ${r.pn} + AFP ${r.pa})`,
      r.high ? 'Above 2: higher-risk group. Validation cohort 5-year recurrence 50.6% against 8.8% for 2 or less.' : '2 or less: lower-risk group. Validation cohort 5-year recurrence 8.8% against 50.6% above 2.',
      'A French selection model, separate from the OPTN exception rules.']},
    metroticket: {fields: [
      {id: 'afp', label: 'AFP', unit: 'ng/mL', type: 'number', step: '0.1'},
      {id: 'number', label: 'Number of viable tumors', type: 'number', step: '1'},
      {id: 'largest', label: 'Largest viable tumor diameter', unit: 'cm', type: 'number', step: '0.1'}
    ], run: metroticket, read: r => [r.limit === null ? 'AFP above 1000 ng/mL: outside the Metroticket 2.0 criteria' : `${r.within ? 'Within' : 'Outside'} the AFP-adjusted limit: ${r.sum} ${r.within ? '≤' : '>'} ${r.limit}`,
      'Sum = number of viable tumors + largest viable diameter (cm), on the last imaging before transplant; a complete response counts as 0.',
      'Criteria for an estimated 70% 5-year HCC-specific survival after transplant. Prognostic, not an allocation rule.'].concat(r.sharedBoundary ? ['The published AFP ranges share 400 ng/mL; this value is given the stricter limit.'] : [])},
    interval: {fields: [
      {id: 'purpose', label: 'Interval since', type: 'select', options: [['', 'Choose (optional)'], ['treatment', 'Last treatment'], ['control', 'Start of documented disease control'], ['progression', 'Last confirmed progression'], ['ici', 'Last checkpoint-inhibitor dose'], ['clearance', 'Clearance of extrahepatic disease'], ['other', 'Other']]},
      {id: 'start', label: 'Start date', type: 'date'},
      {id: 'end', label: 'End date (blank = today)', type: 'date'},
      {id: 'required', label: 'Interval to check', type: 'select', options: [['', 'None'], ['3', '3 months'], ['6', '6 months'], ['12', '12 months'], ['24', '24 months']]}
    ], collect: v => ({...v, today: localToday()}), run: interval,
    read: r => [`${r.days} days · ${r.weeks} weeks · ${r.months} complete month${r.months === 1 ? '' : 's'}`, `Counted to ${r.end}${r.endIsToday ? ' (today)' : ''}.`]
      .concat(r.reached ? [`${r.reached.months} months ${r.reached.met ? 'reached on' : 'will be reached on'} ${r.reached.date}.`] : [])},
    markers: {fields: [
      {id: 'marker', label: 'Marker', type: 'select', options: [['', 'Choose'], ['afp', 'AFP (ng/mL)'], ['cea', 'CEA (ng/mL)'], ['ca199', 'CA19-9 (U/mL)']]},
      ...[1, 2, 3, 4, 5].flatMap(i => [{id: 'date' + i, label: 'Date ' + i, type: 'date'}, {id: 'value' + i, label: 'Value ' + i, type: 'number', step: 'any'}])
    ], collect: v => ({marker: v.marker, points: [1, 2, 3, 4, 5].map(i => ({date: v['date' + i], value: v['value' + i]}))}),
    run: v => ['afp', 'cea', 'ca199'].includes(v.marker) ? Object.assign(markerTrend(v), {marker: v.marker}) : fail('Choose the marker.'),
    read: r => [`${r.first.x} → ${r.last.x} over ${r.days} days${r.change === null ? '' : ` (${r.change > 0 ? '+' : ''}${r.change}%)`}`,
      `Change per month: ${r.perMonth > 0 ? '+' : ''}${r.perMonth}`].concat(r.doublingDays ? [`${r.doublingDays > 0 ? 'Doubling' : 'Halving'} time about ${Math.abs(r.doublingDays)} days (log-linear fit of ${r.n} values)`] : [])
      .concat([MARKER_NOTE[r.marker]]),
    chart: sparkline},
    cytored: {fields: [
      {id: 'total', label: 'Total liver volume, including tumor', unit: 'mL', type: 'number', step: '1'},
      {id: 'tumor', label: 'Total tumor volume', unit: 'mL', type: 'number', step: '1'},
      {id: 'treatable', label: 'Tumor volume removable or treatable', unit: 'mL', type: 'number', step: '1'}
    ], run: liverInvolvement, read: r => [`Liver involvement ${r.involvement}%`,
      r.treatable === null ? 'Add the removable or treatable volume to see the cytoreduction share.' : `Removable or treatable: ${r.treatable}% of tumor volume`,
      'Record the volumetry method (CT or MRI). The thresholds and their evidence follow below.']},
    netgrade: {fields: [
      {id: 'diff', label: 'Differentiation', type: 'select', options: [['', 'Choose'], ['well', 'Well differentiated (NET)'], ['poor', 'Poorly differentiated (NEC)']]},
      {id: 'ki67', label: 'Ki-67', unit: '%', type: 'number', step: '0.1'},
      {id: 'mitoses', label: 'Mitoses', unit: 'per 2 mm²', type: 'number', step: 'any'}
    ], run: netGrade, read: r => r.grade === 'NEC' ? r.text : [`WHO 2019 grade ${r.grade}${r.byKi && r.byMitoses && r.byKi !== r.byMitoses ? ' (indices disagree: the higher grade is assigned)' : ''}`].concat(r.partial ? ['Based on the available proliferation index only; the missing index could increase the grade.'] : [])},
    spigelman: {fields: [
      {id: 'number', label: 'Polyp number', type: 'select', options: [['', 'Choose'], ['0', 'None'], ['1', '1–4'], ['2', '5–20'], ['3', 'More than 20']]},
      {id: 'size', label: 'Largest polyp', type: 'select', options: [['', 'Choose'], ['0', 'No polyps'], ['1', '1–4 mm'], ['2', '5–10 mm'], ['3', 'More than 10 mm']]},
      {id: 'histology', label: 'Histology', type: 'select', options: [['', 'Choose'], ['0', 'No adenomatous change'], ['1', 'Tubular'], ['2', 'Tubulovillous'], ['3', 'Villous']]},
      {id: 'dysplasia', label: 'Dysplasia', type: 'select', options: [['', 'Choose'], ['0', 'None'], ['1', 'Mild (low grade)'], ['2', 'Moderate'], ['3', 'Severe (high grade)']]}
    ], run: spigelman, read: r => `Spigelman ${r.score} points · stage ${r.stage}`}
  };

  /* ---------- Items: what each is, where it applies, how it is recognised in a decision ---------- */
  const term = key => ref?.terms?.[key]?.html || '';
  const ITEMS = [
    {id: 'meld', name: 'MELD 3.0', kind: 'Calculator', match: /\bMELD\b/, html: () => term('meld')},
    {id: 'child', name: 'Child-Pugh score', kind: 'Calculator', match: /\bChild[- –](?:Turcotte[- –])?Pugh\b|\bCTP\b/, html: () => term('child') + src(pm('4541913', 'Pugh 1973'))},
    {id: 'albi', name: 'ALBI grade', kind: 'Calculator', match: /\bALBI\b/,
      html: () => `<p><b>ALBI = log<sub>10</sub> bilirubin (µmol/L) × 0.66 + albumin (g/L) × −0.085.</b> Grade 1 ≤ −2.60; grade 2 above −2.60 to −1.39; grade 3 above −1.39.</p><p>An objective liver-function grade derived in HCC, without the subjective Child-Pugh items. It does not replace Child-Pugh where a protocol specifies Child-Pugh.</p>${src(pm('25512453', 'Johnson 2015'))}`},
    {id: 'ecog', name: 'ECOG performance status', kind: 'Scale', match: /\bECOG\b|\bperformance status\b/i, html: () => term('ecog')},
    {id: 'lirads', name: 'LI-RADS categories', kind: 'Classification', match: /\bLI-?RADS\b|\bLR-(?:[1-5]|M|TR)\b|\bClass 5\b/, html: () => term('lr5'), shared: ['incidental', 'CT/MRI LI-RADS v2018 — category, and what each one means']},
    {id: 'hccburden', name: 'Milan, T2, UNOS downstaging and UCSF', kind: 'Calculator', pages: ['hcc', 'chcca', 'T:hcc'],
      match: /\bMilan\b(?![- ]NET| consensus)|\bUCSF\b|\bT2 (?:criteria|exception|size|tumou?r|burden)|[Dd]ownstag/,
      html: () => `<p><b>Milan:</b> one HCC ≤5 cm, or 2–3 HCCs each ≤3 cm; no macrovascular invasion or extrahepatic spread. Milan is a selection rule, not the T2 exception definition.</p><p><b>T2 (OPTN standard exception):</b> one qualifying Class 5 lesion 2–5 cm, or 2–3 qualifying lesions each 1–3 cm. A single 1 to &lt;2 cm HCC is T1.</p><p><b>UNOS downstaging, pretreatment inclusion:</b> one lesion &gt;5 to ≤8 cm; or 2–3 lesions, at least one &gt;3 cm, each ≤5 cm, summed diameters ≤8 cm; or 4–5 lesions each &lt;3 cm, summed diameters ≤8 cm. No macrovascular invasion or extrahepatic disease. After treatment the viable tumor must meet T2 size; AFP and observation requirements also apply.</p><p><b>UCSF:</b> one tumor ≤6.5 cm, or 2–3 tumors with the largest ≤4.5 cm and summed diameters ≤8 cm; no macrovascular invasion.</p><p>Use pretreatment qualifying HCC lesion sizes; six fields are provided. This is a size-pattern check, not a post-treatment viability assessment. AFP, response, observation time and the policy version in force still apply.</p>${src(web(OPTN, 'OPTN Policy 9.5'), pm('8594428', 'Mazzaferro 1996'), pm('11391528', 'Yao 2001'), pm('25689978', 'Yao 2015'))}`},
    {id: 'vp', name: 'Portal vein tumor invasion (Vp)', kind: 'Classification', pages: ['hcc', 'chcca', 'T:hcc'], match: /\bVp ?[0-4]\b|\bPVTT\b|portal[- ]vein tumou?r/i,
      html: () => `<p>Liver Cancer Study Group of Japan grades: <b>Vp0</b> no portal invasion; <b>Vp1</b> distal to the second-order branches; <b>Vp2</b> second-order branch; <b>Vp3</b> first-order branch; <b>Vp4</b> main trunk or contralateral branch.</p><p>Record the original extent before treatment; response does not reset it.</p>${src(pm('27266618', 'Kokudo 2016'))}`},
    {id: 'tbs', name: 'Tumor burden score', kind: 'Calculator', match: /[Tt]umou?r burden score|\bTBS\b/,
      html: () => `<p><b>TBS = √[(largest diameter in cm)² + (number of tumors)²]</b>, the distance from the origin on a size-by-number plot. A prognostic measure; it carries no eligibility threshold on its own.</p>${src(pm('27763897', 'Sasaki 2018'))}`},
    {id: 'fong', name: 'Fong risk score', kind: 'Calculator', pages: ['crlm', 'T:crlm'], match: /\bFong\b|[Cc]linical risk score|\bCRS ?[0-5]/,
      html: () => `<p>Five preoperative factors, one point each: node-positive primary; under 12 months from primary resection to liver metastasis diagnosis; more than one hepatic tumor; largest tumor over 5 cm; CEA over 200 ng/mL. It stratifies outcome after resection; it does not decide operability.</p>${src(pm('10493478', 'Fong 1999'))}`},
    {id: 'oslo', name: 'Oslo score', kind: 'Calculator', pages: ['crlm', 'T:crlm'], match: /\bOslo\b/,
      html: () => `<p>Four factors, one point each: largest lesion over 5.5 cm; CEA over 80 µg/L; under 2 years from primary resection to transplant; progressive disease on chemotherapy at transplant. Prognostic only: keep it apart from the eligibility decision points.</p>${src(pm('31188200', 'Dueland 2020'), pm('31674105', 'Dueland 2020'))}`},
    {id: 'hehelt', name: 'HEHE-LT score', kind: 'Score', pages: ['T:hehe'], match: /\bH?EHE-LT\b/,
      html: () => `<p>Registry prognostic score for recurrence after transplant for HEHE, built from macrovascular invasion, a pre-transplant waiting time of 120 days or less and hilar lymph-node invasion. Five-year disease-free survival was 93.9% with a score of 2 or less against 38.5% with 6 or more.</p><p>Use it for counseling, not as a MELD score or a qualification test: some components are known only from pathology.</p>${src(pm('28212256', 'Lai 2017'))}`},
    {id: 'netgrade', name: 'WHO 2019 NET grade (Ki-67)', kind: 'Calculator', pages: ['nelm', 'pnet', 'T:nelm'], match: /\bKi-?67\b|\bWHO (?:2019 )?grade\b/,
      html: () => `<p><b>Well-differentiated NET:</b> G1 under 2 mitoses/2 mm² and Ki-67 under 3%; G2 2–20 mitoses/2 mm² and/or Ki-67 3–20%; G3 over 20 mitoses/2 mm² and/or Ki-67 over 20%. <b>Poorly differentiated carcinoma (NEC)</b> is high grade by definition. When the two indices disagree, assign the higher grade.</p>${src(pm('31433515', 'WHO 2019 classification'))}`},
    {id: 'krenning', name: 'Krenning score (SSTR uptake)', kind: 'Scale', pages: ['nelm', 'pnet', 'T:nelm'], match: /\bKrenning\b|[Uu]ptake score|\bSSTR\b|DOTATATE/,
      html: () => `<p>Modified Krenning score of somatostatin-receptor uptake: <b>0</b> none; <b>1</b> very low; <b>2</b> at or below liver; <b>3</b> above liver; <b>4</b> above spleen. Uptake above liver supports consideration of PRRT; suitability also depends on uptake across lesions, disease biology and organ reserve.</p>${src(pm('30850506', 'Hope 2019'), web('https://snmmi.org/common/Uploaded%20files/Web/Clinical%20Practice/Procedure%20Standards/2022/SSTR-PET%2003.11.22%20Final%20Clean.pdf', 'SNMMI/EANM SSTR-PET guidance'))}`},
    {id: 'spigelman', name: 'Spigelman stage', kind: 'Calculator', pages: ['ampullary'], match: /\bSpigelman\b/,
      html: () => `<p>Duodenal polyposis in familial adenomatous polyposis. One to three points each for polyp number (1–4, 5–20, over 20), size (1–4, 5–10, over 10 mm), histology (tubular, tubulovillous, villous) and dysplasia (mild, moderate, severe). Stage 0 = 0 points, I = 1–4, II = 5–6, III = 7–8, IV = 9–12. This uses the original three-tier dysplasia system; assess the ampulla separately.</p>${src(pm('2571019', 'Spigelman 1989'))}`},
    {id: 'mrecist', name: 'mRECIST response', kind: 'Response criteria', pages: ['hcc', 'chcca', 'T:hcc'], match: /\bmRECIST\b/,
      html: () => `<p>Measures viable (arterially enhancing) tumor. <b>Complete response:</b> no intratumoral arterial enhancement in any target lesion. <b>Partial response:</b> at least 30% decrease in the sum of viable diameters. <b>Progression:</b> at least 20% increase from the smallest recorded sum. Overall progression also includes unequivocal non-target progression or a new lesion meeting mRECIST diagnostic criteria; an indeterminate nodule alone does not establish progression. <b>Stable disease:</b> neither.</p>${src(pm('20175033', 'Lencioni 2010'))}`},
    {id: 'recist', name: 'RECIST 1.1 response', kind: 'Response criteria', match: /(?:^|[^A-Za-z])RECIST\b/,
      html: () => `<p>Up to five target lesions, two per organ. <b>Complete response:</b> all target lesions gone and nodes under 10 mm short axis. <b>Partial response:</b> at least 30% decrease in the sum of diameters from baseline. <b>Progression:</b> at least 20% increase from the smallest sum and at least 5 mm absolute. Overall progression also includes unequivocal non-target progression or an unequivocal new lesion. <b>Stable disease:</b> neither.</p>${src(pm('19097774', 'Eisenhauer 2009'))}`},
    {id: 'flr', name: 'Future liver remnant · LiverVolume.com', kind: 'External tool', match: /\bFLR\b|future liver remnant|liver remnant/i,
      html: () => `<p><b>Use LiverVolume.com</b> for liver volumetry and for growth of the future remnant after portal-vein embolization. Enter the measured volumes there; nothing is sent from this page, and that site's formulas are not reproduced here.</p>${extLink('https://livervolume.com/', 'Open LiverVolume.com')}<p><b>Standardized FLR</b> = remnant volume ÷ estimated normal liver volume (Vauthey: −794.41 + 1267.28 × BSA). A ratio using measured non-tumor liver volume uses a different denominator. Resection benchmarks often used: about 20% in normal liver, 30% after chemotherapy injury and 40% in cirrhosis. They come from hepatectomy planning and are not transplant criteria.</p>${src(pm('11910568', 'Vauthey 2002'))}`},
    {id: 'phlf', name: 'Post-hepatectomy liver failure (ISGLS)', kind: 'Grade', match: /\bISGLS\b|post-?hepatectomy liver failure|\bPHLF\b/i,
      html: () => `<p>Increased INR and hyperbilirubinemia on or after postoperative day 5. <b>Grade A:</b> no change in clinical management. <b>Grade B:</b> management changes without invasive treatment. <b>Grade C:</b> invasive treatment needed.</p>${src(pm('21236455', 'Rahbari 2011'))}`},
    {id: 'clavien', name: 'Clavien–Dindo complication grade', kind: 'Classification', match: /\bClavien\b/,
      html: () => `<p><b>I</b> any deviation from the normal course without specific treatment; <b>II</b> needs drugs, transfusion or parenteral nutrition; <b>IIIa/IIIb</b> needs surgical, endoscopic or radiological intervention without/with general anesthesia; <b>IVa/IVb</b> life-threatening single/multiple organ dysfunction needing intensive care; <b>V</b> death.</p>${src(pm('15273542', 'Dindo 2004'))}`},
    {id: 'mmat', name: 'Exception score (MMaT)', kind: 'Allocation', match: /\bMMaT\b/,
      html: () => `<p>MMaT is the median MELD at transplant for the cohort around the donor hospital. The donor-specific value is used on the match run. Approved exceptions are scored against it, for example MMaT−3 for an applicable adult exception; the protocol for each disease states which value applies. Verify the policy in force when filing.</p>${src(web(OPTN + '#page=189', 'OPTN Policy 9.4.D–E · PDF p.189'))}`},
    {id: 'bclc', name: 'BCLC stage', kind: 'Classification', pages: ['chcca', 'T:hcc'], match: /\bBCLC\b/,
      html: () => `<p>Barcelona Clinic Liver Cancer staging links tumor burden, liver function and performance status to treatment: 0 very early, A early, B intermediate, C advanced, D terminal. The HCC roadmap is organized by these stages and follows the 2026 update.</p>${src(`<a href="${esc(new URL('hcc/', ROOT_URL()).href)}">HCC roadmap · stages 0–D</a>`)}`},
    {id: 'lfi', name: 'Liver Frailty Index', kind: 'External tool', match: /[Ff]railty/,
      html: () => `<p>Three performance tests: grip strength (dominant hand, three trials), time for five chair stands, and balance held in three positions for up to 10 seconds each. Derived in 536 outpatients listed for transplant at UCSF; with MELDNa it ranked 3-month waitlist mortality better than MELDNa alone (C-statistic 0.82 against 0.80).</p><p>Calculate it with the UCSF tool, which applies the sex-adjusted grip formula; the formula is not reproduced here. The Harvard eFrailty tool page classifies 4.5 or more as frail.</p>${extLink('https://liverfrailtyindex.ucsf.edu/', 'Open the UCSF Liver Frailty Index calculator')}${src(pm('28422306', 'Lai 2017'), web('https://efrailty.hsl.harvard.edu/ToolLiverFrailtyIndex.html', 'eFrailty · Liver Frailty Index'))}`},
    {id: 'nsqip', name: 'Operative risk · ACS NSQIP', kind: 'External tool', match: NEVER,
      html: () => `<p>Procedure-specific estimates of complications and mortality from patient factors. Enter the details at the ACS site; nothing is sent from this page. It estimates surgical risk, not oncological benefit or liver-specific risk such as remnant function.</p>${extLink('https://riskcalculator.facs.org/RiskCalculator/', 'Open the ACS NSQIP risk calculator')}`},
    {id: 'isgls', name: 'Bile leak and bleeding after hepatectomy (ISGLS)', kind: 'Grade', match: /bile leak|biliary leak|post-?hepatectomy ha?emorrhage/i,
      html: () => `<p><b>Bile leak:</b> drain bilirubin at least 3 times the serum level on or after postoperative day 3, or radiological or operative intervention for a biliary collection or bile peritonitis. <b>Grade A</b> no change in management; <b>B</b> active intervention without relaparotomy; <b>C</b> relaparotomy.</p><p><b>Post-hepatectomy hemorrhage:</b> hemoglobin fall over 3 g/dL from the postoperative baseline, transfusion for a falling hemoglobin, or radiological or operative intervention to stop bleeding, with evidence of intra-abdominal bleeding. <b>Grade A</b> up to 2 units of red cells; <b>B</b> more than 2 units; <b>C</b> embolization or relaparotomy.</p>${src(pm('21316725', 'Koch 2011'), pm('21762295', 'Rahbari 2011'))}`},
    {id: 'retreat', name: 'RETREAT score (after transplant for HCC)', kind: 'Calculator', pages: ['T:hcc'], match: /\bRETREAT\b/,
      html: () => `<p>Recurrence risk after transplant for HCC from three findings. <b>AFP at transplant</b> (ng/mL): 0–20 = 0, 21–99 = 1, 100–999 = 2, 1000 or more = 3. <b>Microvascular invasion</b> on the explant = 2. <b>Largest viable tumor diameter (cm) plus number of viable tumors</b>: 0 = 0, 1.1–4.9 = 1, 5.0–9.9 = 2, 10 or more = 3. Completely necrotic tumors are not counted. Score 0–8.</p><p>A post-transplant tool for surveillance planning, not a pre-transplant eligibility test.</p>${src(pm('27838698', 'Mehta 2017'), pm('35158898', 'van Hooff 2022'))}`},
    {id: 'afpmodel', name: 'AFP model (French)', kind: 'Prognostic score', pages: ['hcc', 'T:hcc'], match: /AFP model|French model/i,
      html: () => `<p><b>Largest diameter</b>: 3 cm or less = 0, over 3 to 6 cm = 1, over 6 cm = 4. <b>Number of tumors</b>: 1–3 = 0, 4 or more = 2. <b>AFP</b> (ng/mL): 100 or less = 0, over 100 to 1000 = 2, over 1000 = 3. A score above 2 identified higher recurrence risk (validation cohort 5-year recurrence 50.6% against 8.8%).</p><p>A selection model used in France; separate from OPTN exception rules.</p>${src(pm('22750200', 'Duvoux 2012'))}`},
    {id: 'metroticket', name: 'Metroticket 2.0', kind: 'Prognostic score', pages: ['hcc', 'T:hcc'], match: /Metroticket|[Uu]p-to-7/,
      html: () => `<p>Sum of the number of viable tumors and the largest viable diameter (cm), on the last imaging before transplant, within an AFP-adjusted limit: <b>7 or less</b> with AFP under 200 ng/mL; <b>5 or less</b> with AFP 200–400; <b>4 or less</b> with AFP 400–1000. Inside these limits the model estimated at least 70% 5-year HCC-specific survival after transplant. A complete response counts as zero tumors.</p><p>Prognostic, from Italian training and Chinese validation cohorts; it is not an allocation rule.</p>${extLink('https://www.hcc-olt-metroticket.org/', 'Open the Metroticket 2.0 online calculator')}${src(pm('28989060', 'Mazzaferro 2018'))}`},
    {id: 'interval', name: 'Interval calculator', kind: 'Date calculator', match: NEVER,
      html: () => `<p>Days, weeks and complete calendar months between two dates, and the date a required interval is reached: for example 6 months of documented control, time since the last confirmed progression, or time since a checkpoint-inhibitor dose. Whether an interval satisfies a protocol, and what resets it, is stated in the decision itself. An interval alone does not establish transplant safety after immunotherapy.</p>`},
    {id: 'markers', name: 'Tumor-marker trend', kind: 'Calculator', match: NEVER,
      html: () => `<p>Up to five dated values of AFP, CEA or CA19-9: change from first to last, change per month, and the doubling or halving time from a log-linear fit when every value is above zero. Protocol thresholds stay in the decision itself (for example CEA under 80 ng/mL for CRLM, or AFP 500 and 1000 ng/mL for the HCC exception).</p>`},
    {id: 'cytored', name: 'Liver involvement and cytoreduction', kind: 'Calculator', pages: ['nelm', 'T:nelm'], match: NEVER, shared: ['nelm', 'Cytoreduction thresholds, and what supports them'],
      html: () => `<p>Percentage of the liver replaced by tumor, and the share of tumor volume that can be removed or treated, from volumetry.</p>`},
    {id: 'netpet', name: 'NETPET grade (SSTR and FDG PET)', kind: 'Classification', pages: ['nelm', 'pnet', 'T:nelm'], match: /\bNETPET\b|\bFDG\b/,
      html: () => `<p>Dual SSTR and FDG PET read on the lesion most FDG-avid relative to its SSTR uptake. <b>P0</b> no disease on either scan; <b>P1</b> SSTR-avid disease with no FDG uptake; <b>P2–P4</b> lesions avid on both, graded by relative FDG uptake and extent; <b>P5</b> significant FDG-positive, SSTR-negative disease.</p><p>In 62 patients, median survival was 11 months at P5 and not reached at P1 or P2–P4. The authors suggest P4b–P5 disease may not be controlled by PRRT alone, a hypothesis to test. Retrospective and single-center.</p>${src(pm('28435454', 'Chan 2017'))}`},
    {id: 'meldexc', name: 'MELD exception score by diagnosis', kind: 'Allocation', match: NEVER,
      html: () => `<table class="minitab tc-table"><tbody>${MELD_EXCEPTIONS.map(([slug, d, s, w]) => `<tr${slug === pageSlug ? ' class="tc-current"' : ''}><td>${esc(d)}</td><td>${esc(s)}<br><small>${esc(w)}</small></td></tr>`).join('')}</tbody></table><p>Adult candidates. NLRB guidance values are recommendations to the review board, not automatic awards. Confirm the policy version in force when filing.</p>${src(web(OPTN, 'OPTN Policy 9'), web(NLRB, 'NLRB transplant oncology guidance'))}`},
    {id: 'afpexc', name: 'AFP rules for the HCC exception', kind: 'Criteria', pages: ['hcc', 'T:hcc'], match: NEVER,
      html: () => `<p><b>T2 with AFP 1000 ng/mL or less:</b> eligible for the standardized exception.</p><p><b>AFP over 1000 at any time:</b> locoregional therapy may be given; the candidate becomes eligible if AFP falls below 500 and stays below 500. An AFP of 500 or more after locoregional therapy at any time means referral to the NLRB.</p><p><b>Extensions</b> are no longer automatic if the tumor progresses beyond T2, if AFP rises above 1000 after an initial value of 1000 or less, or if AFP rises to 500 or more after having fallen below 500.</p>${src(web(OPTN, 'OPTN Policy 9.5.I.ii, 9.5.I.iv and extensions'))}`},
    {id: 'csph', name: 'Clinically significant portal hypertension', kind: 'Criteria', pages: ['hcc', 'T:hcc', 'chcca'], match: /\bCSPH\b|portal hypertension/i,
      html: () => `<p><b>Reference standard:</b> HVPG 10 mmHg or more, in viral and alcohol-related cirrhosis. Varices, ascites or portosystemic collaterals are clinical signs of portal hypertension.</p><p><b>Noninvasive (compensated advanced chronic liver disease):</b> liver stiffness by transient elastography of 15 kPa or less with platelets 150 ×10⁹/L or more rules CSPH out; 25 kPa or more rules it in for viral, alcohol-related and non-obese NASH disease. Between these, ANTICIPATE estimates at least 60% risk at 20–25 kPa with platelets under 150, or 15–20 kPa with platelets under 110.</p><p>CSPH, by HVPG or clinical signs, raises the risk of decompensation and death after resection for HCC.</p><p>These are Baveno VII (2022) statements. The HCC roadmap follows the 2026 BCLC update; a later Baveno edition was not verified here.</p>${src(pm('35120736', 'de Franchis 2022 · Baveno VII'))}`},
    {id: 'lrtfeas', name: 'Treatment feasibility · liver-directed', kind: 'Table', match: NEVER, lrt: true,
      html: () => `<p>When each liver-directed treatment is unsuitable, from the published liver-directed therapy matrix.</p>`},
    {id: 'bismuth', name: 'Bismuth–Corlette classification', kind: 'Classification', pages: ['T:pcca'], match: NEVER, shared: ['hilar', 'Bismuth-Corlette type and the operation it implies'], html: () => ''},
    {id: 'pccadx', name: 'Tissue sampling: diagnostic yield', kind: 'Table', pages: ['T:pcca'], match: NEVER, shared: ['hilar', 'Diagnostic yield of the tissue options'], html: () => ''},
    {id: 'drainage', name: 'Biliary drainage targets and route', kind: 'Table', pages: ['T:pcca'], match: NEVER, shared: ['hilar', 'Drainage targets, and the route question'], html: () => ''},
    {id: 'multifocal', name: 'Multiple liver tumors: definitions', kind: 'Classification', pages: ['T:icca'], match: NEVER, shared: ['icca', 'Multiple liver tumors: multifocal disease, satellites, and intrahepatic metastases'], html: () => ''},
    {id: 'iccares', name: 'iCCA resectability criteria', kind: 'Criteria', pages: ['T:icca'], match: NEVER, shared: ['icca', 'Resectability, as the roadmap defines it'], html: () => ''},
    {id: 'ccamol', name: 'Molecular alterations that change treatment', kind: 'Table', pages: ['T:icca', 'hilar'], match: NEVER, shared: ['icca', 'Molecular alterations that change treatment'], html: () => ''},
    {id: 'crlmres', name: 'The three axes of unresectability', kind: 'Criteria', pages: ['T:crlm'], match: NEVER, shared: ['crlm', 'The three axes of unresectability'], html: () => ''},
    {id: 'crlmmol', name: 'Molecular groups that change first-line therapy', kind: 'Table', pages: ['T:crlm'], match: NEVER, shared: ['crlm', 'Molecular groups that change first-line therapy'], html: () => ''},
    {id: 'milannet', name: 'Milan-NET transplant criteria', kind: 'Criteria', pages: ['T:nelm'], match: NEVER, shared: ['nelm', 'Milan-NET transplant criteria'], html: () => ''},
    {id: 'crisis', name: 'Carcinoid crisis precautions', kind: 'Guide', pages: ['T:nelm'], match: NEVER, shared: ['nelm', 'Carcinoid crisis precautions'], html: () => ''},
    {id: 'hcasub', name: 'HCA subtypes', kind: 'Classification', pages: ['T:hca'], match: NEVER, shared: ['adenoma', 'HCA molecular subtypes — frequency, marker, and what each changes'], html: () => ''},
    {id: 'hca5', name: 'The 5 cm convention: evidence', kind: 'Table', pages: ['T:hca'], match: NEVER, shared: ['adenoma', 'The 5 cm convention — what the supporting series actually show, and what the direct tests found'], html: () => ''},
    {id: 'hcasurv', name: 'HCA surveillance intervals', kind: 'Schedule', pages: ['T:hca'], match: NEVER, shared: ['adenoma', 'Surveillance intervals, by source'], html: () => ''},
    {id: 'lipop', name: 'Who the liver imaging algorithms apply to', kind: 'Criteria', pages: ['T:hcc'], match: NEVER, shared: ['incidental', 'Who the at-risk algorithms apply to'], html: () => ''},
  ];
  let rootUrl = null;
  function ROOT_URL() { return rootUrl || 'https://drliuhao.github.io/mh-liver-pathways/'; }

  /* Items whose subject a page already defines: quick-reference label → item. The page's text is kept. */
  const QUICKREF = {
    'Fong risk score': 'fong', 'Oslo score and transplant criteria': 'oslo', 'Child-Pugh calculator': 'child', 'ECOG scale': 'ecog',
    'LI-RADS diagnostic and response criteria': 'lirads', 'LI-RADS categories': 'lirads', 'Grade and Ki-67 thresholds': 'netgrade',
    'Milan-NET transplant criteria': 'milannet', 'Bismuth–Corlette classification': 'bismuth', 'AJCC staging': 'ajcc',
    'High-risk stigmata and worrisome features': 'kyoto', 'HCA subtypes': 'hcasub', 'ACR incidental lesion algorithm': 'acr',
    'Multiple liver tumors: definitions and stage': 'multifocal', 'Diagnostic definition': 'whodx'
  };
  const QUICKREF_KIND = {milannet: 'Criteria', bismuth: 'Classification', ajcc: 'Staging', kyoto: 'Criteria', hcasub: 'Classification', acr: 'Algorithm', multifocal: 'Classification', whodx: 'Classification', lirads: 'Classification', netgrade: 'Calculator', ecog: 'Scale'};
  const ORDER = ['meld', 'child', 'albi', 'ecog', 'lfi', 'csph', 'lirads', 'lipop', 'hccburden', 'afpexc', 'meldexc', 'afpmodel', 'metroticket', 'retreat', 'bclc', 'vp',
    'tbs', 'fong', 'oslo', 'crlmres', 'crlmmol', 'hehelt', 'netgrade', 'netpet', 'krenning', 'milannet', 'cytored', 'crisis', 'spigelman',
    'bismuth', 'pccadx', 'drainage', 'multifocal', 'iccares', 'ccamol', 'ajcc', 'whodx', 'hcasub', 'hca5', 'hcasurv', 'kyoto', 'acr',
    'mrecist', 'recist', 'markers', 'interval', 'lrtfeas', 'flr', 'nsqip', 'phlf', 'isgls', 'clavien', 'mmat'];

  // Items central to a decision that its text does not name (page → decision → items).
  const SURGERY = ['flr', 'nsqip', 'isgls'];
  const EXTRA = {
    hcc: {0: ['csph', ...SURGERY], A: ['csph', ...SURGERY, 'lfi', 'afpexc', 'afpmodel', 'metroticket'], B: ['afpexc', 'metroticket', 'mrecist', 'markers', 'lrtfeas'], C: ['mrecist', 'markers', 'lrtfeas']},
    crlm: {1: ['tbs', 'markers'], 2: SURGERY, 3: ['flr', 'recist', 'markers'], 4: ['oslo', 'lfi', 'interval', 'meldexc'], 5: ['recist', 'markers', 'lrtfeas']},
    icca: {1: ['markers'], 3: SURGERY, 4: ['flr', 'recist', 'markers'], 5: ['recist', 'interval'], 7: ['lrtfeas'], 9: ['recist', 'markers'], 10: ['lfi', 'interval', 'meldexc']},
    hilar: {0: ['markers'], 2: ['markers'], 3: SURGERY, 4: ['lfi', 'meldexc'], 5: ['ccamol', 'recist']},
    nelm: {1: ['netpet'], 2: ['interval', 'recist'], 3: ['recist', 'netpet'], 4: ['netpet'], 5: ['cytored', ...SURGERY], 6: ['recist', 'netpet'], 7: ['lrtfeas', 'cytored'], 9: ['cytored', 'lfi', 'meldexc']},
    chcca: {2: ['markers'], 3: SURGERY, 5: ['lfi'], 7: ['recist'], 9: ['markers', 'interval']},
    adenoma: {2: ['interval'], 4: ['nsqip', 'interval'], 6: ['interval'], 10: ['lfi', 'meldexc']},
    pdac: {3: ['nsqip'], 4: ['recist', 'markers'], 6: ['markers', 'interval'], 7: ['recist', 'markers'], 8: ['recist', 'markers']},
    pnet: {1: ['netpet'], 2: ['netpet'], 4: ['interval'], 5: ['nsqip'], 8: ['netpet'], 9: ['interval']},
    pcyst: {6: ['nsqip'], 8: ['interval'], 10: ['interval']},
    ampullary: {4: ['nsqip'], 5: ['nsqip'], 8: ['recist'], 9: ['interval']},
    'T:hcc': {diagnosis: ['lipop'], 'curative-route': ['albi', 'csph', ...SURGERY, 'lrtfeas'], allocation: ['afpexc', 'meldexc', 'afpmodel', 'metroticket', 'markers'],
      treatment: ['mrecist', 'markers', 'interval', 'lrtfeas'], listing: ['meldexc', 'afpexc', 'lfi', 'interval'], waitlist: ['mrecist', 'markers', 'interval', 'lfi'], 'after-transplant': ['retreat']},
    'T:pcca': {localize: ['bismuth', 'drainage'], diagnosis: ['pccadx', 'markers'], phenotype: ['bismuth', 'meldexc'], neoadjuvant: ['interval'], listing: ['lfi', 'meldexc']},
    'T:icca': {diagnosis: ['ccamol'], phenotype: ['multifocal', 'iccares'], therapy: ['recist', 'markers', 'ccamol', 'lrtfeas'], stability: ['interval', 'recist', 'markers'], review: ['meldexc', 'lfi']},
    'T:crlm': {'map-disease': ['tbs', 'fong', 'markers'], biology: ['fong', 'oslo', 'markers', 'crlmmol'], unresectability: ['flr', 'fong', 'crlmres'], control: ['recist', 'markers', 'interval', 'lrtfeas'],
      clocks: ['interval'], restaging: ['recist', 'oslo', 'markers'], review: ['oslo', 'meldexc', 'lfi']},
    'T:nelm': {biology: ['netpet'], distribution: ['netpet', 'krenning'], options: ['netgrade', 'krenning', 'cytored', 'crisis', 'lrtfeas'], exposure: ['krenning', 'crisis'], observation: ['recist', 'interval'],
      review: ['milannet', 'meldexc', 'lfi']},
    'T:hehe': {risk: ['interval'], review: ['meldexc', 'lfi']},
    'T:hca': {characterize: ['hcasub'], 'standard-care': ['hca5', 'hcasurv', 'interval', 'nsqip'], 'exception-route': ['meldexc'], review: ['lfi']}
  };
  // Items a decision's own text names. `page` is a roadmap slug ('crlm') or 'T:' + transplant slug.
  function detect(text, page) {
    return ITEMS.filter(i => (!i.pages || i.pages.includes(page)) && i.match.test(text)).map(i => i.id);
  }
  const byId = Object.fromEntries(ITEMS.map(i => [i.id, i]));
  const ROADMAP_NAME = {hilar: 'perihilar cholangiocarcinoma', icca: 'intrahepatic cholangiocarcinoma', crlm: 'colorectal liver metastases', nelm: 'neuroendocrine liver metastases',
    adenoma: 'hepatocellular adenoma', incidental: 'incidental liver lesion'};
  // A roadmap's own quick reference, shown where another page needs it. Rendered as the roadmap renders it.
  function renderQuickref(q, slug) {
    if (!q) return '<p class="tc-note">This reference is no longer in the roadmap. Open the roadmap to find its current version.</p>';
    const pmids = [...new Set(JSON.stringify(q).match(/\b\d{8}\b/g) || [])];
    return (q.intro ? `<p class="small muted">${esc(q.intro)}</p>` : '') +
      `<table class="minitab"><tbody>${q.rows.map(r => `<tr><td>${esc(r[0])}</td><td>${esc(r[1])}</td></tr>`).join('')}</tbody></table>` +
      (q.foot ? `<p class="small">${esc(q.foot)}</p>` : '') + (q.src ? `<p class="small muted">Source: ${esc(q.src)}</p>` : '') +
      (pmids.length ? `<p class="tc-src">${pmids.map(id => `<a href="https://pubmed.ncbi.nlm.nih.gov/${id}/" target="_blank" rel="noopener">PMID ${id} ↗</a>`).join(' · ')}</p>` : '') +
      `<p class="tc-src"><a href="${esc(new URL(slug + '/', ROOT_URL()).href)}">From the ${esc(ROADMAP_NAME[slug] || slug)} roadmap →</a></p>`;
  }
  // When each liver-directed treatment is unsuitable, from the published matrix data.
  function renderLrtContra(data, tumor) {
    const rows = data.modalities.filter(([key]) => data.cells[tumor + '|' + key] && data.contra[key]);
    if (!rows.length) return '<p class="tc-note">No liver-directed treatment is listed for this tumor.</p>';
    return `<table class="minitab tc-table"><tbody>${rows.map(([key, name]) => {
      const c = data.contra[key], ref = c.ref || [];
      const cite = ref.filter(x => /^\d{7,8}$/.test(x)).map(id => `<a href="https://pubmed.ncbi.nlm.nih.gov/${id}/" target="_blank" rel="noopener">PMID ${id}</a>`).join(' · ');
      return `<tr><td>${esc(name)}</td><td><ul class="tc-list">${c.items.map(x => `<li>${esc(x)}</li>`).join('')}</ul>${ref.length ? `<small>${esc(ref.filter(x => !/^\d{7,8}$/.test(x)).join(' · '))}${cite ? ' · ' + cite : ''}</small>` : ''}</td></tr>`;
    }).join('')}</tbody></table><p class="tc-src"><a href="${esc(new URL('lrt/#' + tumor, ROOT_URL()).href)}">Open the liver-directed therapy matrix →</a></p>`;
  }
  const API = {items: byId, forms: FORMS, detect, extra: EXTRA, quickref: QUICKREF, quickrefKind: QUICKREF_KIND, order: ORDER, esc,
    setRoot(url) { rootUrl = url; }, setPage(slug) { pageSlug = slug || ''; }, renderQuickref, renderLrtContra,
    calculators: {childPugh, albi, hccBurden, tumorBurden, fong, oslo, futureRemnant, netGrade, spigelman, response, retreat, afpModel, metroticket, interval, markerTrend, liverInvolvement}};
  if (typeof module === 'object' && module.exports) module.exports = API; else root.ClinicalScores = API;
})(typeof window === 'undefined' ? {} : window);
