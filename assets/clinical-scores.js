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
  const OPTN = 'https://www.hrsa.gov/sites/default/files/hrsa/optn/optn_policies.pdf';

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
    if (v.biliUnit === 'mgdl') bili *= 17.1;
    if (v.albUnit === 'gdl') alb *= 10;
    const score = Math.log10(bili) * 0.66 + alb * -0.085;
    return {ok: true, score: round(score), grade: score <= -2.6 ? 1 : score <= -1.39 ? 2 : 3, bilirubinUmol: round(bili, 1), albuminGl: round(alb, 1)};
  }

  // HCC tumor burden: Milan, T2, UNOS downstaging and UCSF from qualifying lesion diameters (cm).
  function hccBurden(v) {
    const sizes = (v.sizes || []).map(num).filter(x => x !== null && x > 0);
    if (!sizes.length) return fail('Enter the diameter of each qualifying lesion.');
    const n = sizes.length, max = Math.max(...sizes), sum = round(sizes.reduce((a, b) => a + b, 0), 2), spread = !!v.spread;
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

  const points = (v, keys) => keys.reduce((a, k) => a + (v[k] ? 1 : 0), 0);
  // Fong clinical risk score: five factors, one point each (Fong 1999).
  const fong = v => ({ok: true, score: points(v, ['node', 'dfi', 'multiple', 'size', 'cea'])});
  // Oslo score: four factors, one point each (Dueland 2020).
  const oslo = v => ({ok: true, score: points(v, ['size', 'cea', 'interval', 'progression'])});

  // Standardized future liver remnant: FLR volume / total liver volume, TLV = −794.41 + 1267.28 × BSA (Vauthey 2002).
  function futureRemnant(v) {
    const flr = num(v.flr), height = num(v.height), weight = num(v.weight), measured = num(v.tlv);
    if (flr === null || flr <= 0) return fail('Enter the future liver remnant volume (mL).');
    let tlv = measured, bsa = null;
    if (tlv === null || tlv <= 0) {
      if (height === null || weight === null || height <= 0 || weight <= 0) return fail('Enter height and weight, or a measured total liver volume.');
      bsa = Math.sqrt(height * weight / 3600);
      tlv = -794.41 + 1267.28 * bsa;
    }
    return {ok: true, bsa: bsa === null ? null : round(bsa), tlv: Math.round(tlv), percent: round(flr / tlv * 100, 1), estimated: bsa !== null};
  }

  // WHO 2019 grade of a well-differentiated NET; the higher grade wins when Ki-67 and mitoses disagree.
  function netGrade(v) {
    if (v.diff === 'poor') return {ok: true, grade: 'NEC', text: 'Neuroendocrine carcinoma: high grade by definition, not graded G1–G3'};
    const ki = num(v.ki67), mit = num(v.mitoses);
    if (ki === null && mit === null) return fail('Enter Ki-67 and/or the mitotic count.');
    const g = (x, low, high) => x === null ? 0 : x < low ? 1 : x <= high ? 2 : 3;
    const grade = Math.max(g(ki, 3, 20), g(mit, 2, 20));
    return {ok: true, grade: 'G' + grade, byKi: g(ki, 3, 20) || null, byMitoses: g(mit, 2, 20) || null, needsDiff: v.diff !== 'well'};
  }

  // Spigelman stage of duodenal polyposis: number, size, histology, dysplasia (Spigelman 1989).
  function spigelman(v) {
    const keys = ['number', 'size', 'histology', 'dysplasia'];
    if (keys.some(k => !['1', '2', '3'].includes(String(v[k])))) return fail('Choose all four features.');
    const score = keys.reduce((a, k) => a + Number(v[k]), 0);
    return {ok: true, score, stage: score <= 4 ? 'I' : score <= 6 ? 'II' : score <= 8 ? 'III' : 'IV'};
  }

  /* ---------- Calculator forms: fields and how a result reads ---------- */
  const yes = (id, label) => ({id, label, type: 'check'});
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
    ], run: albi, read: r => `ALBI ${r.score.toFixed(2)} · grade ${r.grade}`},
    hccburden: {fields: [
      ...[1, 2, 3, 4, 5, 6].map(i => ({id: 'size' + i, label: 'Lesion ' + i, unit: 'cm', type: 'number', step: '0.1'})),
      yes('spread', 'Macrovascular invasion or extrahepatic disease')
    ], collect: v => ({sizes: [1, 2, 3, 4, 5, 6].map(i => v['size' + i]), spread: v.spread}), run: hccBurden,
    read: r => [`${r.n} lesion${r.n > 1 ? 's' : ''}, largest ${r.max} cm, sum ${r.sum} cm`,
      `Milan: ${r.milan ? 'within' : 'outside'}`,
      `T2: ${r.t2 === 'met' ? 'size criteria met' : r.t2 === 'T1' ? 'T1 (single 1 to <2 cm)' : 'not met'}`,
      `UNOS downstaging (pretreatment): ${r.milan ? 'not needed (within Milan)' : r.downstaging ? 'within' : 'outside'}`,
      `UCSF: ${r.ucsf ? 'within' : 'outside'}`,
      `Tumor burden score: ${r.tbs.toFixed(2)}`].concat(r.under1 ? ['A lesion under 1 cm is not a qualifying Class 5 lesion; remove it unless it qualifies.'] : [])},
    tbs: {fields: [{id: 'max', label: 'Largest tumor', unit: 'cm', type: 'number', step: '0.1'}, {id: 'n', label: 'Number of tumors', type: 'number', step: '1'}],
      run: tumorBurden, read: r => `Tumor burden score ${r.score.toFixed(2)}`},
    fong: {fields: [yes('node', 'Node-positive primary'), yes('dfi', 'Disease-free interval under 12 months'), yes('multiple', 'More than one hepatic tumor'), yes('size', 'Largest tumor over 5 cm'), yes('cea', 'CEA over 200 ng/mL')],
      run: fong, read: r => [`Clinical risk score ${r.score} of 5`, 'Scores 0–2 are usually reported as low risk and 3–5 as high risk.']},
    oslo: {fields: [yes('size', 'Largest lesion over 5.5 cm'), yes('cea', 'CEA over 80 µg/L'), yes('interval', 'Under 2 years from primary resection to transplant'), yes('progression', 'Progressive disease on chemotherapy at transplant')],
      run: oslo, read: r => [`Oslo score ${r.score} of 4`, 'Prognostic only: a low score does not relax an eligibility requirement.']},
    flr: {fields: [
      {id: 'flr', label: 'Future liver remnant', unit: 'mL', type: 'number', step: '1'},
      {id: 'height', label: 'Height', unit: 'cm', type: 'number', step: '1'},
      {id: 'weight', label: 'Weight', unit: 'kg', type: 'number', step: '0.1'},
      {id: 'tlv', label: 'Measured total liver volume (optional)', unit: 'mL', type: 'number', step: '1'}
    ], run: futureRemnant, read: r => [`Future liver remnant ${r.percent}% of ${r.estimated ? 'estimated' : 'measured'} total liver volume (${r.tlv} mL${r.bsa ? `; BSA ${r.bsa} m²` : ''})`,
      'Resection benchmarks often used: about 20% normal liver, 30% after chemotherapy injury, 40% cirrhosis. Not transplant criteria.']},
    netgrade: {fields: [
      {id: 'diff', label: 'Differentiation', type: 'select', options: [['', 'Not stated'], ['well', 'Well differentiated (NET)'], ['poor', 'Poorly differentiated (NEC)']]},
      {id: 'ki67', label: 'Ki-67', unit: '%', type: 'number', step: '0.1'},
      {id: 'mitoses', label: 'Mitoses', unit: 'per 2 mm²', type: 'number', step: '1'}
    ], run: netGrade, read: r => r.grade === 'NEC' ? r.text : [`WHO 2019 grade ${r.grade}${r.byKi && r.byMitoses && r.byKi !== r.byMitoses ? ' (indices disagree: the higher grade is assigned)' : ''}`].concat(r.needsDiff ? ['State differentiation: a well-differentiated G3 NET and a carcinoma share Ki-67 above 20%.'] : [])},
    spigelman: {fields: [
      {id: 'number', label: 'Polyp number', type: 'select', options: [['', 'Choose'], ['1', '1–4'], ['2', '5–20'], ['3', 'More than 20']]},
      {id: 'size', label: 'Largest polyp', type: 'select', options: [['', 'Choose'], ['1', '1–4 mm'], ['2', '5–10 mm'], ['3', 'More than 10 mm']]},
      {id: 'histology', label: 'Histology', type: 'select', options: [['', 'Choose'], ['1', 'Tubular'], ['2', 'Tubulovillous'], ['3', 'Villous']]},
      {id: 'dysplasia', label: 'Dysplasia', type: 'select', options: [['', 'Choose'], ['1', 'Mild (low grade)'], ['2', 'Moderate'], ['3', 'Severe (high grade)']]}
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
    {id: 'lirads', name: 'LI-RADS categories', kind: 'Classification', match: /\bLI-?RADS\b|\bLR-(?:[1-5]|M|TR)\b|\bClass 5\b/, html: () => term('lr5')},
    {id: 'hccburden', name: 'Milan, T2, UNOS downstaging and UCSF', kind: 'Calculator', pages: ['hcc', 'chcca', 'T:hcc'],
      match: /\bMilan\b(?![- ]NET| consensus)|\bUCSF\b|\bT2 (?:criteria|exception|size|tumou?r|burden)|[Dd]ownstag/,
      html: () => `<p><b>Milan:</b> one HCC ≤5 cm, or 2–3 HCCs each ≤3 cm; no macrovascular invasion or extrahepatic spread. Milan is a selection rule, not the T2 exception definition.</p><p><b>T2 (OPTN standard exception):</b> one qualifying Class 5 lesion 2–5 cm, or 2–3 qualifying lesions each 1–3 cm. A single 1 to &lt;2 cm HCC is T1.</p><p><b>UNOS downstaging, pretreatment inclusion:</b> one lesion &gt;5 to ≤8 cm; or 2–3 lesions, at least one &gt;3 cm, each ≤5 cm, summed diameters ≤8 cm; or 4–5 lesions each &lt;3 cm, summed diameters ≤8 cm. No macrovascular invasion or extrahepatic disease. After treatment the viable tumor must meet T2 size; AFP and observation requirements also apply.</p><p><b>UCSF:</b> one tumor ≤6.5 cm, or 2–3 tumors with the largest ≤4.5 cm and summed diameters ≤8 cm; no macrovascular invasion.</p><p>Enter qualifying lesions only. AFP, response, observation time and the policy version in force still apply.</p>${src(web(OPTN, 'OPTN Policy 9.5'), pm('8594428', 'Mazzaferro 1996'), pm('11391528', 'Yao 2001'), pm('25689978', 'Yao 2015'))}`},
    {id: 'vp', name: 'Portal vein tumor invasion (Vp)', kind: 'Classification', pages: ['hcc', 'chcca', 'T:hcc'], match: /\bVp ?[0-4]\b|\bPVTT\b|portal[- ]vein tumou?r/i,
      html: () => `<p>Liver Cancer Study Group of Japan grades: <b>Vp0</b> no portal invasion; <b>Vp1</b> distal to the second-order branches; <b>Vp2</b> second-order branch; <b>Vp3</b> first-order branch; <b>Vp4</b> main trunk or contralateral branch.</p><p>Record the original extent before treatment; response does not reset it.</p>${src(pm('27266618', 'Kokudo 2016'))}`},
    {id: 'tbs', name: 'Tumor burden score', kind: 'Calculator', match: /[Tt]umou?r burden score|\bTBS\b/,
      html: () => `<p><b>TBS = √(largest tumor diameter in cm² + number of tumors²)</b>, the distance from the origin on a size-by-number plot. A prognostic measure; it carries no eligibility threshold on its own.</p>${src(pm('27763897', 'Sasaki 2018'))}`},
    {id: 'fong', name: 'Fong risk score', kind: 'Calculator', pages: ['crlm', 'T:crlm'], match: /\bFong\b|[Cc]linical risk score|\bCRS ?[0-5]/,
      html: () => `<p>Five preoperative factors, one point each: node-positive primary; disease-free interval under 12 months; more than one hepatic tumor; largest tumor over 5 cm; CEA over 200 ng/mL. It stratifies outcome after resection; it does not decide operability.</p>${src(pm('10493478', 'Fong 1999'))}`},
    {id: 'oslo', name: 'Oslo score', kind: 'Calculator', pages: ['crlm', 'T:crlm'], match: /\bOslo\b/,
      html: () => `<p>Four factors, one point each: largest lesion over 5.5 cm; CEA over 80 µg/L; under 2 years from primary resection to transplant; progressive disease on chemotherapy at transplant. Prognostic only: keep it apart from the eligibility decision points.</p>${src(pm('31188200', 'Dueland 2020'), pm('31674105', 'Dueland 2020'))}`},
    {id: 'hehelt', name: 'HEHE-LT score', kind: 'Score', pages: ['T:hehe'], match: /\bH?EHE-LT\b/,
      html: () => `<p>Registry prognostic score for recurrence after transplant for HEHE, built from macrovascular invasion, a pre-transplant waiting time of 120 days or less and hilar lymph-node invasion. Five-year disease-free survival was 93.9% with a score of 2 or less against 38.5% with 6 or more.</p><p>Use it for counseling, not as a MELD score or a qualification test: some components are known only from pathology.</p>${src(pm('28212256', 'Lai 2017'))}`},
    {id: 'netgrade', name: 'WHO 2019 NET grade (Ki-67)', kind: 'Calculator', pages: ['nelm', 'pnet', 'T:nelm'], match: /\bKi-?67\b|\bWHO (?:2019 )?grade\b/,
      html: () => `<p><b>Well-differentiated NET:</b> G1 under 2 mitoses/2 mm² and Ki-67 under 3%; G2 2–20 mitoses/2 mm² and/or Ki-67 3–20%; G3 over 20 mitoses/2 mm² and/or Ki-67 over 20%. <b>Poorly differentiated carcinoma (NEC)</b> is high grade by definition. When the two indices disagree, assign the higher grade.</p>${src(pm('31433515', 'WHO 2019 classification'))}`},
    {id: 'krenning', name: 'Krenning score (SSTR uptake)', kind: 'Scale', pages: ['nelm', 'pnet', 'T:nelm'], match: /\bKrenning\b|[Uu]ptake score|\bSSTR\b|DOTATATE/,
      html: () => `<p>Modified Krenning score of somatostatin-receptor uptake: <b>0</b> none; <b>1</b> very low; <b>2</b> at or below liver; <b>3</b> above liver; <b>4</b> above spleen. A lesion counts as receptor-positive when uptake exceeds liver.</p>${src(pm('8404961', 'Krenning 1993'))}`},
    {id: 'spigelman', name: 'Spigelman stage', kind: 'Calculator', pages: ['ampullary'], match: /\bSpigelman\b/,
      html: () => `<p>Duodenal polyposis in familial adenomatous polyposis. One to three points each for polyp number (1–4, 5–20, over 20), size (1–4, 5–10, over 10 mm), histology (tubular, tubulovillous, villous) and dysplasia (mild, moderate, severe). Stage 0 = 0 points, I = 1–4, II = 5–6, III = 7–8, IV = 9–12.</p>${src(pm('2571019', 'Spigelman 1989'))}`},
    {id: 'mrecist', name: 'mRECIST response', kind: 'Response criteria', pages: ['hcc', 'chcca', 'T:hcc'], match: /\bmRECIST\b/,
      html: () => `<p>Measures viable (arterially enhancing) tumor. <b>Complete response:</b> no intratumoral arterial enhancement in any target lesion. <b>Partial response:</b> at least 30% decrease in the sum of viable diameters. <b>Progression:</b> at least 20% increase from the smallest recorded sum, or a new lesion. <b>Stable disease:</b> neither.</p>${src(pm('20175033', 'Lencioni 2010'))}`},
    {id: 'recist', name: 'RECIST 1.1 response', kind: 'Response criteria', match: /(?:^|[^A-Za-z])RECIST\b/,
      html: () => `<p>Up to five target lesions, two per organ. <b>Complete response:</b> all target lesions gone and nodes under 10 mm short axis. <b>Partial response:</b> at least 30% decrease in the sum of diameters from baseline. <b>Progression:</b> at least 20% increase from the smallest sum and at least 5 mm absolute, or a new lesion. <b>Stable disease:</b> neither.</p>${src(pm('19097774', 'Eisenhauer 2009'))}`},
    {id: 'flr', name: 'Future liver remnant', kind: 'Calculator', match: /\bFLR\b|future liver remnant|liver remnant/i,
      html: () => `<p><b>Standardized FLR = FLR volume ÷ total liver volume.</b> Total liver volume can be estimated as −794.41 + 1267.28 × body-surface area (m²). Resection benchmarks often used: about 20% in normal liver, 30% after chemotherapy injury and 40% in cirrhosis. They come from hepatectomy planning and are not transplant criteria.</p>${src(pm('11910568', 'Vauthey 2002'))}`},
    {id: 'phlf', name: 'Post-hepatectomy liver failure (ISGLS)', kind: 'Grade', match: /\bISGLS\b|post-?hepatectomy liver failure|\bPHLF\b/i,
      html: () => `<p>Increased INR and hyperbilirubinemia on or after postoperative day 5. <b>Grade A:</b> no change in clinical management. <b>Grade B:</b> management changes without invasive treatment. <b>Grade C:</b> invasive treatment needed.</p>${src(pm('21236455', 'Rahbari 2011'))}`},
    {id: 'clavien', name: 'Clavien–Dindo complication grade', kind: 'Classification', match: /\bClavien\b/,
      html: () => `<p><b>I</b> any deviation from the normal course without specific treatment; <b>II</b> needs drugs, transfusion or parenteral nutrition; <b>IIIa/IIIb</b> needs surgical, endoscopic or radiological intervention without/with general anesthesia; <b>IVa/IVb</b> life-threatening single/multiple organ dysfunction needing intensive care; <b>V</b> death.</p>${src(pm('15273542', 'Dindo 2004'))}`},
    {id: 'mmat', name: 'Exception score (MMaT)', kind: 'Allocation', match: /\bMMaT\b/,
      html: () => `<p>MMaT is the median MELD at transplant for the transplant hospital's area. Approved exceptions are scored against it, for example MMaT−3 for a standardized adult exception; the protocol for each disease states which value applies. Verify the policy in force when filing.</p>${src(web(OPTN, 'OPTN Policy 9'))}`},
    {id: 'bclc', name: 'BCLC stage', kind: 'Classification', pages: ['chcca', 'T:hcc'], match: /\bBCLC\b/,
      html: () => `<p>Barcelona Clinic Liver Cancer staging links tumor burden, liver function and performance status to treatment: 0 very early, A early, B intermediate, C advanced, D terminal. The HCC roadmap is organized by these stages and follows the 2026 update.</p>${src(`<a href="${esc(new URL('hcc/', ROOT_URL()).href)}">HCC roadmap · stages 0–D</a>`)}`}
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
  const ORDER = ['meld', 'child', 'albi', 'ecog', 'lirads', 'hccburden', 'bclc', 'vp', 'tbs', 'fong', 'oslo', 'hehelt', 'netgrade', 'krenning', 'milannet', 'spigelman',
    'bismuth', 'ajcc', 'multifocal', 'whodx', 'hcasub', 'kyoto', 'acr', 'mrecist', 'recist', 'flr', 'phlf', 'clavien', 'mmat'];

  // Items central to a decision that its text does not name (page → decision → items).
  const EXTRA = {
    'T:hcc': {'curative-route': ['albi', 'flr'], treatment: ['mrecist'], waitlist: ['mrecist']},
    'T:crlm': {'map-disease': ['fong'], biology: ['fong', 'oslo'], unresectability: ['flr', 'fong'], control: ['recist'], restaging: ['recist', 'oslo'], review: ['oslo']},
    'T:nelm': {options: ['netgrade', 'krenning'], exposure: ['krenning'], observation: ['recist']},
    crlm: {3: ['flr'], 4: ['oslo']}
  };
  // Items a decision's own text names. `page` is a roadmap slug ('crlm') or 'T:' + transplant slug.
  function detect(text, page) {
    return ITEMS.filter(i => (!i.pages || i.pages.includes(page)) && i.match.test(text)).map(i => i.id);
  }
  const byId = Object.fromEntries(ITEMS.map(i => [i.id, i]));
  const API = {items: byId, forms: FORMS, detect, extra: EXTRA, quickref: QUICKREF, quickrefKind: QUICKREF_KIND, order: ORDER, esc,
    setRoot(url) { rootUrl = url; },
    calculators: {childPugh, albi, hccBurden, tumorBurden, fong, oslo, futureRemnant, netGrade, spigelman}};
  if (typeof module === 'object' && module.exports) module.exports = API; else root.ClinicalScores = API;
})(typeof window === 'undefined' ? {} : window);
