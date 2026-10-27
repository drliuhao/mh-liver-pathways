/* Display summaries; original cutoffs, recommendations and evidence stay in the source topic. */
window.DecisionWorkspaceData={
  "topics": {
    "crlm/1": {
      "title": "1 · Complete staging and molecular testing",
      "criteria": [
        "Contrast CT of chest, abdomen and pelvis, plus liver MRI with hepatocyte-specific or diffusion-weighted sequences whenever local therapy is contemplated",
        "PET/CT and colonoscopy added whenever transplantation is a possibility",
        "RAS, BRAF, MMR/MSI and HER2 resulted before the first-line systemic decision",
        "Primary tumour status recorded, with pelvic MRI and baseline bowel, urinary and sexual function for a rectal primary",
        "Future liver remnant, prior treatment map including previous ablation zones, and the clinical risk score recorded"
      ],
      "team": "HPB surgery · Colorectal surgery · Medical oncology · Abdominal radiology · Molecular pathology",
      "inputs": [
        "CT chest/abdomen/pelvis and liver MRI",
        "Primary status; colonoscopy and PET/CT if considering transplant",
        "RAS, BRAF, MMR/MSI and HER2",
        "Future liver remnant, prior treatment map and clinical risk score"
      ],
      "tools": [
        "ecog",
        "systemic"
      ]
    },
    "crlm/2": {
      "title": "2 · Resection or ablation feasible now",
      "criteria": [
        "Every original site of hepatic disease treatable by resection, margin-verified thermal ablation, or the two combined",
        "Adequate future liver remnant with preserved inflow, outflow and biliary drainage",
        "No progression on an appropriate systemic regimen",
        "No extrahepatic disease, or disease that is limited, controllable and itself completely treatable",
        "Patient fit for the operation that clearance actually requires"
      ],
      "team": "HPB surgery · Interventional radiology · Medical oncology · Abdominal radiology",
      "inputs": [
        "Map of every original liver disease site",
        "Future remnant, inflow, outflow and drainage",
        "Systemic response and extrahepatic disease",
        "Operative fitness"
      ],
      "tools": [
        "ecog",
        "lrt"
      ]
    },
    "crlm/3": {
      "title": "3 · Treat and reassess for resection or ablation",
      "criteria": [
        "Anatomic unresectability only — remnant too small or vascular and biliary relations prohibitive — with biology controlled",
        "Liver-dominant or liver-only disease where a high hepatic response could convert to clearance",
        "Functional limitation from parenchymal quality or reserve that may recover with a chemotherapy holiday and nutritional recovery",
        "Hepatic burden drives the risk and liver-first sequencing would bring clearance forward",
        "Disease in the planned future remnant that a defined course of therapy could clear"
      ],
      "team": "HPB surgery · Medical oncology · Interventional radiology · Abdominal radiology",
      "inputs": [
        "Reason complete liver clearance is not yet feasible",
        "Future remnant and parenchymal quality",
        "Disease distribution and response",
        "Nutrition, reserve and recovery potential"
      ],
      "tools": [
        "ecog",
        "lrt",
        "systemic"
      ]
    },
    "crlm/4": {
      "title": "4 · Assess transplant eligibility",
      "criteria": [
        "Permanent unresectability formally determined, with a written record of why resection, margin-verified ablation, portal vein embolisation or liver venous deprivation, staged hepatectomy, ALPPS and hepatic arterial infusion each cannot clear the liver at acceptable functional risk",
        "Unequivocally liver-only on CT/MRI and PET/CT, with no extrahepatic, nodal or peritoneal disease at any time",
        "Histologically confirmed colorectal adenocarcinoma, BRAF wild type and microsatellite stable, with R0 primary resection and colonoscopy within 12 months excluding local recurrence",
        "At least 12 months from CRLM diagnosis and at least six months of stability or regression on systemic or locoregional therapy; CEA not above 80 µg/L; no hepatic lesion above 10 cm before treatment",
        "ECOG 0–1 with adequate organ function and low frailty, under a written protocol with a transplant-oncology MDT, a defined graft strategy, a prospective registry and an agreed recurrence plan"
      ],
      "team": "Liver transplant surgery · HPB surgery · Colorectal surgery · Medical oncology",
      "inputs": [
        "Formal unresectability review and alternative local treatments",
        "CT/MRI, PET/CT and history of extrahepatic disease",
        "Primary pathology/resection, BRAF, MSI and colonoscopy",
        "Treatment-response timeline, CEA, baseline size and fitness"
      ],
      "tools": [
        "ecog",
        "meld"
      ]
    },
    "crlm/5": {
      "title": "5 · Disease control when complete removal is not feasible",
      "criteria": [
        "Progression despite an appropriate systemic regimen — biologic unresectability, which surgery cannot correct",
        "Liver-dominant refractory disease after at least one systemic line, where hepatic control rather than clearance is the goal",
        "Oligoprogression in a patient otherwise controlled on systemic therapy",
        "Reserve, parenchymal quality or frailty makes any clearance operation intolerable and recovery is not expected"
      ],
      "team": "Medical oncology · Interventional radiology · Radiation oncology · Palliative care",
      "inputs": [
        "Prior systemic regimens and response",
        "Liver-dominant progression or oligoprogression",
        "Liver reserve, frailty and patient goals"
      ],
      "tools": [
        "ecog",
        "lrt",
        "systemic"
      ]
    },
    "icca/1": {
      "title": "1 · Confirm diagnosis and stage disease",
      "criteria": [
        "Histology consistent with intrahepatic cholangiocarcinoma, or a high-suspicion mass accepted for direct resection after multidisciplinary HPB review",
        "Multiphase CT of chest, abdomen and pelvis plus liver MRI with cholangiographic (MRCP) sequences, completed before any stent is placed",
        "Another primary excluded — colonoscopy, age-appropriate breast imaging and a CK7/CK20/CDX2-type panel as indicated",
        "Perihilar and distal cholangiocarcinoma and gallbladder cancer require their own treatment assessment. Mixed HCC-iCCA has a separate combined-tumor roadmap; NLRB transplant guidance groups it with iCCA (see clinical decision 10).",
        "Recorded: tumour number and size, vascular and biliary involvement, nodal status, extrahepatic sites, ECOG, Child-Pugh and bilirubin, CA 19-9 and CEA, hepatitis serology"
      ],
      "team": "HPB surgery · Abdominal radiology · Pathology · Hepatology",
      "inputs": [
        "Histology or documented multidisciplinary diagnostic assessment",
        "CT chest/abdomen/pelvis and liver MRI/MRCP",
        "Lesion number, size, distribution, vessels, ducts, nodes and distant sites",
        "ECOG, liver function, bilirubin, CA 19-9, CEA and hepatitis status"
      ],
      "tools": [
        "ecog",
        "child"
      ]
    },
    "icca/2": {
      "title": "2 · Request molecular profiling",
      "criteria": [
        "Unresectable or metastatic disease at diagnosis — order now, not at the point of second-line progression",
        "Borderline or locally advanced disease where systemic therapy is the first step",
        "Recurrence after resection that will be treated systemically",
        "Adequate tissue preserved from the diagnostic core, or plasma where tissue is inadequate or a biopsy would delay treatment"
      ],
      "team": "Medical oncology · Molecular pathology",
      "inputs": [
        "Disease extent and intended systemic treatment",
        "Available diagnostic tissue and specimen adequacy",
        "Existing molecular results; plasma testing feasibility if needed"
      ],
      "tools": [
        "systemic"
      ]
    },
    "icca/3": {
      "title": "3 · Assess resection",
      "criteria": [
        "An R0 resection appears feasible with adequate remaining liver function. For limited multifocal disease, consider surgery only in highly selected patients after multidisciplinary review; proximity of nodules alone does not establish suitability.",
        "Inflow, outflow and biliary drainage preservable or reconstructable",
        "No nodal disease beyond the regional basin — no retroperitoneal or coeliac stations",
        "No extrahepatic disease",
        "Adequate reserve and performance status for the operation the anatomy requires"
      ],
      "team": "HPB surgery · Abdominal radiology · Hepatology",
      "inputs": [
        "Tumor map and feasibility of negative margins",
        "Future remnant, inflow, outflow and drainage",
        "Regional versus distant nodes and extrahepatic sites",
        "Liver reserve and operative fitness"
      ],
      "tools": [
        "ecog",
        "child",
        "meld"
      ]
    },
    "icca/4": {
      "title": "4 · Treat and reassess for resection",
      "criteria": [
        "Not R0 now, and the specific obstacle to R0 is recorded",
        "No extrahepatic disease",
        "What would have to change for resection to become possible is recorded alongside the plan",
        "A reassessment date at 2–3 months is declared before treatment starts",
        "Fit for the systemic regimen that is the backbone of any conversion attempt"
      ],
      "team": "Medical oncology · HPB surgery · Abdominal radiology · Interventional radiology",
      "inputs": [
        "Specific barrier to complete resection",
        "Extrahepatic staging",
        "Treatment fitness and intended conversion target",
        "Planned response imaging and surgical reassessment"
      ],
      "tools": [
        "ecog",
        "lrt",
        "systemic"
      ]
    },
    "icca/5": {
      "title": "5 · Unresectable disease confined to the liver",
      "criteria": [
        "Not convertible at formal surgical re-review, not on an imaging report alone",
        "No extrahepatic disease",
        "Liver function and performance status adequate for systemic therapy",
        "Biliary obstruction relieved, or a drainage plan agreed with the hepatobiliary surgeon"
      ],
      "team": "Medical oncology · HPB surgery · Interventional radiology · Advanced gastroenterology",
      "inputs": [
        "Surgical reassessment of convertibility",
        "Extrahepatic staging",
        "Liver function, ECOG and biliary drainage"
      ],
      "tools": [
        "ecog",
        "child",
        "lrt",
        "systemic"
      ]
    },
    "icca/6": {
      "title": "6 · Distant metastatic disease",
      "criteria": [
        "Any extrahepatic disease on staging imaging",
        "Nodal disease beyond the regional basin, including retroperitoneal or coeliac stations",
        "A new extrahepatic site found at reassessment",
        "Distant metastatic disease at recurrence after resection"
      ],
      "team": "Medical oncology · Abdominal radiology · Palliative care",
      "inputs": [
        "Distant sites on staging or reassessment",
        "Regional versus nonregional nodes",
        "Recurrence pattern and treatment history"
      ],
      "tools": [
        "ecog",
        "systemic"
      ]
    },
    "icca/7": {
      "title": "7 · Select liver-directed therapy",
      "criteria": [
        "Treatment intent assigned before a device is chosen — cure, conversion or bridge, or hepatic control",
        "Target geometry, liver reserve and biliary drainage assessed, not described from a report",
        "What this institution can actually deliver confirmed — pump, personalised dosimetry, device and radiopharmaceutical availability, payer authorisation",
        "Resection, local ablation and transplant compared at multidisciplinary review where appropriate",
        "Intended outcome, why the alternatives do not fit, the systemic plan, the reassessment date and the next action all recorded"
      ],
      "team": "Interventional radiology · Radiation oncology · HPB surgery · Medical oncology",
      "inputs": [
        "Treatment goal and alternatives",
        "Target geometry, liver reserve and biliary drainage",
        "Local modality expertise and availability",
        "Systemic plan and response assessment"
      ],
      "tools": [
        "ecog",
        "child",
        "lrt"
      ]
    },
    "icca/8": {
      "title": "8 · Adjuvant treatment after resection",
      "criteria": [
        "Macroscopically complete resection with curative intent, R0 or R1",
        "Recovered enough to start within 16 weeks of surgery, with performance status and organ function to match",
        "Node-positive or R1 disease, where the discussion carries most weight",
        "A patient who wants to know what the trial actually showed before deciding"
      ],
      "team": "Medical oncology · HPB surgery · Pathology",
      "inputs": [
        "Resection pathology, margins and nodes",
        "Postoperative recovery and time from surgery",
        "ECOG, organ function and patient preference"
      ],
      "tools": [
        "ecog",
        "systemic"
      ]
    },
    "icca/9": {
      "title": "9 · Systemic treatment for advanced disease",
      "criteria": [
        "Unresectable or metastatic disease, treated with systemic intent",
        "Performance status, renal and hepatic function and contraindications to checkpoint inhibition assessed, including any prior adjuvant therapy",
        "Progression on first-line gemcitabine–platinum, with the molecular result already in hand",
        "Trial eligibility checked — at diagnosis and again at each progression"
      ],
      "team": "Medical oncology · Molecular pathology · Hepatology",
      "inputs": [
        "Disease extent, prior therapy and progression",
        "ECOG, renal and hepatic function",
        "Checkpoint-inhibitor contraindications",
        "Molecular results and trial eligibility"
      ],
      "tools": [
        "ecog",
        "child",
        "systemic"
      ]
    },
    "icca/10": {
      "title": "10 · Assess transplant eligibility",
      "criteria": [
        "Biopsy-proven solitary unresectable iCCA or mixed HCC-iCCA",
        "Tumour 3 cm or less, with underlying cirrhosis",
        "Locoregional or systemic therapy received",
        "Six months from diagnosis or last treatment with tumour stability on serial scans — still 3 cm or less, no new lesions, no extrahepatic disease",
        "A formally approved trial or prospective registry protocol open, with review-board approval and registry entry"
      ],
      "team": "Liver transplant surgery · Transplant hepatology · HPB surgery · Medical oncology",
      "inputs": [
        "Biopsy diagnosis, lesion count and diameter",
        "Cirrhosis and formal unresectability review",
        "Treatment and serial stability timeline",
        "New lesions, distant disease and protocol availability"
      ],
      "tools": [
        "meld",
        "child"
      ]
    },
    "hilar/0": {
      "title": "0 · Assess the need for biliary drainage",
      "criteria": [
        "Cholangitis, or a bilirubin that is rising",
        "Jaundice in a patient whose planned operation is a major hepatectomy with a predicted future liver remnant of 30% or less",
        "Portal vein embolisation planned — hypertrophy is poor while the remnant stays cholestatic",
        "Neoadjuvant chemoradiation, radiotherapy or systemic therapy planned",
        "Malnutrition, or hepatic or renal insufficiency from prolonged jaundice",
        "Note that routine preoperative drainage of every jaundiced patient is not what the guidelines say: this is an indication list, not a default"
      ],
      "team": "Advanced gastroenterology · HPB surgery · Interventional radiology · Abdominal radiology",
      "inputs": [
        "Cholangitis assessment and bilirubin trend",
        "Future liver remnant and intended drainage sectors",
        "Planned surgery, embolization or anticancer treatment",
        "Nutrition, liver and renal function"
      ],
      "tools": [
        "ecog"
      ]
    },
    "hilar/1": {
      "title": "1 · Define tumor extent",
      "criteria": [
        "Multiphase CT of chest, abdomen and pelvis plus MRI with MRCP, obtained before stenting where the clinical situation allows",
        "Biliary extent recorded by sector, with portal venous and hepatic arterial involvement and lobar atrophy",
        "Future liver remnant volume, regional and distant nodal status, peritoneal findings",
        "Bilirubin trajectory and performance status",
        "Whether the patient has primary sclerosing cholangitis — it changes both the differential and the transplant discussion"
      ],
      "team": "Abdominal radiology · HPB surgery · Advanced gastroenterology",
      "inputs": [
        "CT chest/abdomen/pelvis and MRI/MRCP",
        "Ductal extent, arterial/portal involvement and lobar atrophy",
        "Future remnant, nodes and peritoneal staging",
        "Bilirubin trend, performance status and PSC history"
      ],
      "tools": [
        "ecog"
      ]
    },
    "hilar/2": {
      "title": "2 · Plan tissue sampling",
      "criteria": [
        "Discuss the intended treatment before biopsy: resection, a transplant protocol, or systemic therapy",
        "Do not use a transperitoneal approach to biopsy the primary tumor (percutaneous, operative, or EUS-guided) when transplantation remains an option",
        "Tissue is taken at the index ERCP, before or at the time the first stent is placed",
        "A separate specimen from the same ERCP goes for molecular testing where it is available",
        "Nodal sampling and sampling of the primary are treated as different decisions"
      ],
      "team": "Advanced gastroenterology · HPB surgery · Liver transplant surgery · Pathology",
      "inputs": [
        "Intended treatment and transplant suitability before biopsy",
        "Prior primary-tumor sampling route",
        "ERCP tissue and molecular specimen plan",
        "Separate primary-stricture and lymph-node sampling plans"
      ],
      "tools": []
    },
    "hilar/3": {
      "title": "3 · Assess resection",
      "criteria": [
        "Biliary and vascular extent that permits a technically achievable R0 resection",
        "Contralateral liver with intact arterial and portal inflow as well as biliary drainage",
        "Future liver remnant adequate, or made adequate by embolisation after the remnant has been drained",
        "No intrahepatic, extrahepatic, nodal or peritoneal metastases on the staging package",
        "Patient fit for extended hepatectomy with biliary reconstruction, at a center with appropriate surgical expertise"
      ],
      "team": "HPB surgery · Abdominal radiology · Hepatology",
      "inputs": [
        "Ductal and vascular extent; negative-margin feasibility",
        "Future remnant volume, function and drainage",
        "Liver, nodes, peritoneal and distant staging",
        "Fitness for major hepatectomy and reconstruction"
      ],
      "tools": [
        "ecog",
        "child"
      ]
    },
    "hilar/4": {
      "title": "4 · Assess transplant eligibility",
      "criteria": [
        "Unresectable for technical reasons or because of underlying liver disease, including primary sclerosing cholangitis; assess clinical candidacy and OPTN exception criteria separately",
        "If a mass is present, a single mass under 3 cm in radial diameter — longitudinal duct extension is not the measured criterion",
        "No intrahepatic or extrahepatic metastases on chest and abdominal imaging within 90 days of the initial request, and no regional nodal disease",
        "Diagnosis established by the accepted OPTN criteria; avoid transperitoneal biopsy of the primary tumor",
        "A centre holding an OPTN-committee-approved written patient-care protocol, with operative staging before transplantation"
      ],
      "team": "Liver transplant surgery · Transplant hepatology · HPB surgery · Advanced gastroenterology",
      "inputs": [
        "Reason for unresectability and underlying liver disease",
        "Radial mass diameter and staging imaging",
        "Accepted diagnostic evidence and biopsy history",
        "Nodal status and approved transplant protocol"
      ],
      "tools": [
        "meld"
      ]
    },
    "hilar/5": {
      "title": "5 · Unresectable disease outside a transplant protocol",
      "criteria": [
        "Regional nodal disease, or a mass of 3 cm or more in radial diameter: these do not meet the standardized exception criteria. Confirm borderline measurements and clinical options with the transplant team before excluding transplantation",
        "Intrahepatic or extrahepatic metastases",
        "Comorbidity or performance status that rules out transplantation",
        "No OPTN-approved protocol available, or the patient declines that route"
      ],
      "team": "Medical oncology · HPB surgery · Liver transplant team · Advanced gastroenterology",
      "inputs": [
        "Mass diameter and regional nodes",
        "Intrahepatic and extrahepatic metastases",
        "Transplant review, medical fitness and patient preference",
        "Protocol availability"
      ],
      "tools": [
        "ecog",
        "systemic"
      ]
    },
    "hilar/6": {
      "title": "6 · Supportive and symptom-directed care",
      "criteria": [
        "Poor performance status that is not explained by jaundice or sepsis",
        "Uncontrolled sepsis",
        "Patient choice"
      ],
      "team": "Palliative care · Medical oncology · Advanced gastroenterology · Hepatology",
      "inputs": [
        "Performance status and reversible jaundice or sepsis",
        "Infection control and symptom burden",
        "Patient priorities"
      ],
      "tools": [
        "ecog"
      ]
    },
    "nelm/1": {
      "title": "1 · Confirm differentiation and grade",
      "criteria": [
        "Biopsy reporting differentiation, an exact Ki-67 index and a mitotic count",
        "Somatostatin-receptor PET/CT for receptor status and whole-body staging",
        "Functional syndrome recorded explicitly, confirmed with directed tests",
        "Hepatic burden and distribution: unilobar versus bilobar, resectable versus diffuse-miliary",
        "Primary site, whether it is resected, and the extrahepatic sites"
      ],
      "team": "NET medical oncology · Pathology · Nuclear medicine · Abdominal radiology",
      "inputs": [
        "Differentiation, exact Ki-67 and mitotic count",
        "Somatostatin-receptor PET/CT",
        "Functional syndrome and directed biochemical tests",
        "Liver distribution, primary status and extrahepatic sites"
      ],
      "tools": []
    },
    "nelm/2": {
      "title": "2 · Low-volume G1–G2 disease",
      "criteria": [
        "Well-differentiated NET, grade 1 or grade 2",
        "Low hepatic tumour burden, resectable or ablatable",
        "Radiologically stable or slowly progressive",
        "Asymptomatic, or symptoms attributable to a hormonal syndrome rather than to bulk"
      ],
      "team": "NET medical oncology · HPB surgery · Interventional radiology",
      "inputs": [
        "Differentiation and grade",
        "Liver burden and local treatment feasibility",
        "Serial growth and symptom cause"
      ],
      "tools": [
        "lrt",
        "systemic"
      ]
    },
    "nelm/3": {
      "title": "3 · High-volume or progressing G1–G2 disease",
      "criteria": [
        "Diffuse or bilobar hepatic disease",
        "Progression on a somatostatin analogue",
        "Clinically significant hepatic burden driving the picture",
        "Hormonal symptoms poorly controlled on an analogue"
      ],
      "team": "NET medical oncology · Interventional radiology · Nuclear medicine",
      "inputs": [
        "Liver burden and distribution",
        "Response to somatostatin analogue",
        "Hepatic and hormone-related symptoms"
      ],
      "tools": [
        "lrt",
        "systemic"
      ]
    },
    "nelm/4": {
      "title": "4 · G3 NET versus neuroendocrine carcinoma",
      "criteria": [
        "Ki-67 above 20%",
        "Poorly differentiated small-cell or large-cell morphology",
        "Grade progression from a prior G1 or G2 tumour",
        "A mixed neuroendocrine–non-neuroendocrine neoplasm"
      ],
      "team": "NET medical oncology · Expert pathology",
      "inputs": [
        "Exact Ki-67 and morphology",
        "Prior grade and interval change",
        "Mixed histologic components"
      ],
      "tools": [
        "systemic"
      ]
    },
    "nelm/5": {
      "title": "5 · Assess surgical cytoreduction",
      "criteria": [
        "Well-differentiated NET, not poorly differentiated carcinoma",
        "A substantial fraction of the hepatic burden can be cleared — the target and the expected residual named before operating",
        "No diffuse-miliary pattern and no uncontrolled extrahepatic progression",
        "Adequate performance status and hepatic reserve, with significant carcinoid heart disease addressed first",
        "Demonstrated local experience with parenchymal-sparing hepatic surgery"
      ],
      "team": "HPB surgery · NET medical oncology · Cardiology · Anesthesiology",
      "inputs": [
        "Differentiation and distribution",
        "Expected cytoreduction and residual disease",
        "Extrahepatic response, liver reserve and performance status",
        "Carcinoid heart assessment"
      ],
      "tools": [
        "ecog",
        "child",
        "lrt"
      ]
    },
    "nelm/6": {
      "title": "6 · Select systemic therapy",
      "criteria": [
        "Progression on a somatostatin analogue",
        "Unresectable disease with no liver-directed goal to serve",
        "Receptor-positive disease being considered for PRRT",
        "A pancreatic primary needing a sequencing decision"
      ],
      "team": "NET medical oncology · Nuclear medicine",
      "inputs": [
        "Prior somatostatin analogue and response",
        "Resectability and liver-directed treatment goal",
        "Receptor imaging and primary site"
      ],
      "tools": [
        "ecog",
        "systemic"
      ]
    },
    "nelm/7": {
      "title": "7 · Select liver-directed therapy",
      "criteria": [
        "Bulky or symptomatic liver-dominant disease",
        "Hepatic progression with a stated hepatic goal",
        "Hormonal symptoms poorly controlled on a somatostatin analogue",
        "Lobar or segmental distribution, or prior Whipple or biliary instrumentation"
      ],
      "team": "Interventional radiology · HPB surgery · NET medical oncology · Nuclear medicine",
      "inputs": [
        "Liver burden, progression and symptom goal",
        "Lobar or segmental distribution",
        "Prior Whipple, biliary instrumentation and liver-directed treatment"
      ],
      "tools": [
        "child",
        "lrt"
      ]
    },
    "nelm/8": {
      "title": "8 · Hormone-related symptoms and crisis prevention",
      "criteria": [
        "Carcinoid syndrome or any other documented functional syndrome",
        "Markedly raised 5-HIAA or chromogranin A",
        "Any planned hepatic procedure, ablation or PRRT course in functional disease",
        "Signs or symptoms of carcinoid heart disease"
      ],
      "team": "NET medical oncology · Endocrinology · Cardiology · Anesthesiology",
      "inputs": [
        "Functional syndrome and directed markers",
        "5-HIAA/chromogranin A in clinical context",
        "Carcinoid heart signs and planned procedure/PRRT"
      ],
      "tools": []
    },
    "nelm/9": {
      "title": "9 · Assess transplant eligibility",
      "criteria": [
        "Well or moderately differentiated G1/G2 NET, Ki-67 under 20% and mitotic rate under 20 per 10 high-power fields",
        "Gastroenteropancreatic primary with portal venous drainage, resected together with all extrahepatic disease, no recurrence for at least six months",
        "Unresectable disease limited to the liver, with no extrahepatic disease on functional imaging",
        "Approved local protocol, registry entry and a nonstandard review-board submission",
        "Significant carcinoid heart disease and functional syndrome assessed"
      ],
      "team": "Liver transplant surgery · NET medical oncology · Transplant hepatology · Nuclear medicine",
      "inputs": [
        "Differentiation, Ki-67 and mitotic rate",
        "Primary site, resection and extrahepatic disease history",
        "Functional imaging and observation timeline",
        "Cardiac/functional syndrome assessment and protocol"
      ],
      "tools": [
        "meld",
        "ecog"
      ]
    },
    "chcca/0": {
      "title": "0 · Assess the suspected diagnosis",
      "criteria": [
        "A liver mass whose enhancement carries both hepatocellular and non-hepatocellular features, or an LR-M observation in an at-risk liver",
        "AFP and CA 19-9 both raised, or one raised against an enhancement pattern that does not match it",
        "Imaging that reads LR-5 in a patient with no cirrhosis, no chronic hepatitis B and no prior HCC",
        "A biopsy or specimen already reporting one component with features of the other",
        "A tumour already resected or transplanted whose pathology reports both differentiations"
      ],
      "team": "Abdominal radiology · Hepatology · Expert liver pathology",
      "inputs": [
        "Enhancement pattern and liver-risk background",
        "AFP and CA 19-9",
        "Existing biopsy or operative pathology"
      ],
      "tools": [
        "lr5"
      ]
    },
    "chcca/1": {
      "title": "1 · Plan tissue sampling",
      "criteria": [
        "The destination is named before the needle: resection, the transplant pathway, or systemic therapy",
        "Core needle biopsy rather than fine-needle aspiration wherever tissue is needed",
        "Pathology told in advance that cHCC-CCA is the question, so both components are looked for and reported",
        "Enough tissue preserved for multigene panel testing in advanced or recurrent disease",
        "The report states which component predominates, and the margin, vascular and nodal findings"
      ],
      "team": "HPB surgery · Liver transplant team · Interventional radiology · Pathology",
      "inputs": [
        "Intended treatment before biopsy",
        "Core specimen adequacy and both histologic components",
        "Molecular tissue needs",
        "Margins, vascular and nodal findings if resected"
      ],
      "tools": []
    },
    "chcca/2": {
      "title": "2 · Stage the disease",
      "criteria": [
        "Multiphase CT or MRI of the liver and abdomen, plus CT of the chest",
        "Regional nodal status recorded explicitly — porta hepatis, gastrohepatic, periduodenal and peripancreatic stations",
        "AJCC 8th edition intrahepatic bile duct T, N and M categories assigned, not a BCLC stage alone",
        "Which component predominates, stated as a proportion where the specimen allows it",
        "Baseline AFP and CA 19-9, with the date and clinical state at which each was drawn"
      ],
      "team": "Abdominal radiology · HPB surgery · Pathology",
      "inputs": [
        "Liver/abdominal imaging and chest CT",
        "Regional nodes and distant sites",
        "AJCC intrahepatic bile-duct staging and component proportions",
        "Baseline AFP and CA 19-9"
      ],
      "tools": []
    },
    "chcca/3": {
      "title": "3 · Assess resection",
      "criteria": [
        "A single tumour, or limited multifocal disease in a highly selected patient, with a technically achievable negative margin",
        "No nodal disease beyond the porta hepatis, no peritoneal disease, no distant metastasis",
        "Future liver remnant and hepatic reserve adequate for the resection the margin requires",
        "Patient fit for an anatomical hepatectomy with regional lymphadenectomy, at a centre that performs them",
        "The patient has been told what the recurrence figures in this histology actually are"
      ],
      "team": "HPB surgery · Hepatology · Abdominal radiology",
      "inputs": [
        "Tumor map and negative-margin feasibility",
        "Nodal, peritoneal and distant staging",
        "Future liver remnant, reserve and operative fitness"
      ],
      "tools": [
        "ecog",
        "child",
        "meld"
      ]
    },
    "chcca/4": {
      "title": "4 · Plan regional lymph-node assessment",
      "criteria": [
        "cHCC-CCA known or suspected before the operation, on histology, markers or imaging",
        "A pre-operative diagnosis of HCC in a patient whose CA 19-9, CEA or enhancement pattern raises cholangiocytic differentiation",
        "Radiologically suspicious porta hepatis nodes",
        "An intra-operative finding — a firm, pale or desmoplastic tumour — that does not look like HCC"
      ],
      "team": "HPB surgery · Abdominal radiology · Pathology",
      "inputs": [
        "Histology, markers and diagnostic uncertainty",
        "Porta hepatis nodes on imaging",
        "Intraoperative appearance and nodal plan"
      ],
      "tools": []
    },
    "chcca/5": {
      "title": "5 · Assess transplant eligibility",
      "criteria": [
        "Cirrhosis, with disease unresectable on technical grounds or because of the underlying liver",
        "Biopsy-proven cHCC-CCA or mixed HCC-iCCA, solitary and 3 cm or less, to meet the OPTN review-board criteria",
        "Six months of documented stability on locoregional or systemic therapy, no new lesions, no extrahepatic disease",
        "Well or moderately differentiated, with no macrovascular invasion and no nodal disease",
        "A programme that has written down which criteria it is using, and a registry that records every case"
      ],
      "team": "Liver transplant surgery · Transplant hepatology · Medical oncology · Pathology",
      "inputs": [
        "Cirrhosis and unresectability",
        "Biopsy, differentiation, tumor count and size",
        "Treatment and stability timeline",
        "Vascular, nodal and distant staging; protocol criteria"
      ],
      "tools": [
        "meld",
        "child"
      ]
    },
    "chcca/6": {
      "title": "6 · Unexpected diagnosis after surgery",
      "criteria": [
        "A liver transplanted for presumed HCC whose explant shows a cholangiocytic component",
        "A resection for presumed HCC or iCCA whose specimen shows both differentiations",
        "A specimen in which the predominant component differs from the pre-operative biopsy",
        "A margin, nodal, vascular or perineural finding that was not anticipated pre-operatively"
      ],
      "team": "Pathology · HPB or liver transplant surgery · Hepatology · Medical oncology",
      "inputs": [
        "Complete resection or explant review",
        "Component proportions and diagnostic discordance",
        "Margins, nodes, vascular and perineural invasion"
      ],
      "tools": []
    },
    "chcca/7": {
      "title": "7 · Select systemic therapy",
      "criteria": [
        "Unresectable, metastatic or recurrent disease, with no transplant pathway available or the patient declining it",
        "A histological diagnosis, with the predominant component recorded where the specimen allows it",
        "Multigene panel results in hand or requested",
        "Performance status and hepatic reserve that will tolerate a platinum doublet"
      ],
      "team": "Medical oncology · Molecular pathology · Hepatology",
      "inputs": [
        "Disease extent and available treatment routes",
        "Histology and predominant component",
        "Molecular panel, performance status and liver reserve"
      ],
      "tools": [
        "ecog",
        "child",
        "systemic"
      ]
    },
    "chcca/8": {
      "title": "8 · Consider liver-directed therapy",
      "criteria": [
        "Liver-confined unresectable disease, or bridging or downstaging on a transplant pathway",
        "A tumour with an arterialised component, where an embolic response is mechanistically plausible",
        "Preserved liver function, a patent portal vein, and no extrahepatic disease driving the prognosis",
        "Explicit acknowledgement that no trial of any liver-directed modality has been conducted in this disease"
      ],
      "team": "Interventional radiology · Radiation oncology · HPB surgery · Medical oncology",
      "inputs": [
        "Liver distribution and intended treatment goal",
        "Arterial enhancement and portal patency",
        "Liver function and extrahepatic disease"
      ],
      "tools": [
        "child",
        "lrt"
      ]
    },
    "chcca/9": {
      "title": "9 · Surveillance and recurrent disease",
      "criteria": [
        "A resected or transplanted patient under surveillance",
        "A new liver lesion, a rising AFP, or a rising CA 19-9",
        "Nodal recurrence at the porta hepatis or portal vein–vena cava region",
        "An isolated recurrence that local re-treatment could address"
      ],
      "team": "HPB or liver transplant surgery · Medical oncology · Abdominal radiology",
      "inputs": [
        "Prior operation and surveillance imaging",
        "AFP and CA 19-9 trends",
        "Recurrence sites and local retreatment feasibility"
      ],
      "tools": [
        "lrt",
        "systemic"
      ]
    },
    "adenoma/1": {
      "title": "1 · Confirm diagnosis and subtype",
      "criteria": [
        "Contrast-enhanced MRI, preferably with a hepatobiliary agent, including fat-sensitive and chemical-shift sequences",
        "Every measurable lesion counted, with dominant diameter, exophytic protrusion, segment and vascular relationships recorded",
        "Risk-factor history taken explicitly: oestrogen, anabolic androgens, BMI, alcohol, glycogen storage disease, vascular liver disease, family history",
        "Subtype assigned where imaging allows it, and recorded as unassigned where it does not",
        "An at-risk liver excluded — cirrhosis, chronic hepatitis B or prior HCC puts this on the HCC pathway, not this one"
      ],
      "team": "Abdominal radiology · Hepatology · Expert liver pathology",
      "inputs": [
        "Hepatobiliary-contrast MRI and lesion map",
        "Hormone/androgen exposure, metabolic and family history",
        "Imaging subtype and background liver disease"
      ],
      "tools": [
        "lr5"
      ]
    },
    "adenoma/2": {
      "title": "2 · Risk-factor modification and reassessment",
      "criteria": [
        "Oestrogen-containing contraception, a hormone-containing intrauterine device, or any other oestrogen exposure",
        "Anabolic-androgenic steroid or androgen therapy exposure, including non-prescribed use",
        "Overweight, obesity, type 2 diabetes or other features of the metabolic syndrome",
        "Alcohol intake of 30 g a day or more",
        "A woman whose adenoma is not yet an indication for operation on size, growth, subtype or sex"
      ],
      "team": "Hepatology · Primary care · Endocrinology",
      "inputs": [
        "Hormone and androgen exposure",
        "Weight, diabetes and metabolic risk",
        "Alcohol history",
        "Serial lesion size, growth and subtype"
      ],
      "tools": []
    },
    "adenoma/3": {
      "title": "3 · Adenoma in a male patient",
      "criteria": [
        "Male patient with a hepatocellular adenoma of any size",
        "Androgen or anabolic-steroid exposure, current or past",
        "Nuclear beta-catenin or strong diffuse glutamine synthetase staining, or a confirmed CTNNB1 mutation",
        "Cellular atypia, pseudoglandular formation or cholestasis on biopsy",
        "A diagnosis of adenoma made outside an expert liver pathology service"
      ],
      "team": "HPB surgery · Hepatology · Expert liver pathology",
      "inputs": [
        "Sex and androgen exposure",
        "Expert pathology and subtype markers",
        "CTNNB1 findings and cellular atypia if sampled"
      ],
      "tools": []
    },
    "adenoma/4": {
      "title": "4 · Size, growth, and intervention",
      "criteria": [
        "Adenoma still larger than 5 cm after an adequate trial of risk-factor modification — and an explicit note of how long that trial has run, because six months is too early",
        "Diameter increase of 20% or more on comparable imaging — EASL's RECIST-based growth trigger, never validated in a benign liver lesion",
        "Exophytic protrusion from the liver surface, or lesional arteries visible on imaging",
        "Lesion in segment II or III",
        "Symptoms attributable to the lesion",
        "Subtype, where it is known — a beta-catenin exon 3 or sonic hedgehog result changes the decision more than a centimetre of diameter does"
      ],
      "team": "HPB surgery · Abdominal radiology · Hepatology · Interventional radiology",
      "inputs": [
        "Serial diameter on comparable imaging",
        "Duration and response to risk-factor modification",
        "Exophytic position, segment and lesional arteries",
        "Symptoms and molecular subtype"
      ],
      "tools": []
    },
    "adenoma/5": {
      "title": "5 · Acute bleeding or rupture",
      "criteria": [
        "Sudden severe upper abdominal pain in a patient with a known or suspected adenoma",
        "Haemodynamic instability, or a falling haemoglobin",
        "Intrahepatic or intraperitoneal haemorrhage on contrast-enhanced CT",
        "Pregnancy or the early puerperium",
        "An exophytic adenoma, or one 5 cm or larger"
      ],
      "team": "HPB surgery · Interventional radiology · Critical care",
      "inputs": [
        "Hemodynamics, pain and hemoglobin trend",
        "Contrast CT for hemorrhage and lesion anatomy",
        "Pregnancy/postpartum status"
      ],
      "tools": []
    },
    "adenoma/6": {
      "title": "6 · Pregnancy planning and surveillance",
      "criteria": [
        "Pregnant, or planning a pregnancy, with a known or suspected adenoma",
        "Adenoma under 5 cm, not exophytic and not growing",
        "Adenoma 5 cm or larger, or any lesion that has grown",
        "A previous pregnancy complicated by the adenoma",
        "The diagnosis has not been confirmed on MRI with a hepatobiliary contrast agent"
      ],
      "team": "Maternal-fetal medicine · Hepatology · HPB surgery · Abdominal radiology",
      "inputs": [
        "Pregnancy plans or gestational status",
        "Confirmed diagnosis, size, growth and exophytic position",
        "Prior pregnancy-related complications"
      ],
      "tools": []
    },
    "adenoma/7": {
      "title": "7 · Multiple adenomas and adenomatosis",
      "criteria": [
        "More than one adenoma on hepatobiliary-contrast MRI",
        "Ten or more adenomas",
        "Bilobar distribution that no single resection can clear",
        "A germline HNF1A mutation, MODY3 diabetes, or a family history of liver adenoma",
        "A male patient, glycogen storage disease, or microadenomas on a previous specimen"
      ],
      "team": "Hepatology · HPB surgery · Abdominal radiology · Genetics",
      "inputs": [
        "MRI lesion count, dominant size and lobar distribution",
        "HNF1A/MODY3, family and metabolic history",
        "Prior pathology and resection feasibility"
      ],
      "tools": []
    },
    "adenoma/8": {
      "title": "8 · Genetic, metabolic, and vascular conditions",
      "criteria": [
        "Glycogen storage disease type I, III or IV",
        "Abernethy malformation or another congenital portosystemic shunt",
        "Budd-Chiari syndrome, portal vein thrombosis or another vascular liver disease",
        "Beta-thalassaemia, haemochromatosis or another iron-overload state",
        "McCune-Albright syndrome, or a paediatric or adolescent presentation"
      ],
      "team": "Hepatology · Genetics/metabolic medicine · HPB surgery",
      "inputs": [
        "Metabolic or genetic diagnosis",
        "Vascular liver anatomy and disease",
        "Iron-overload history and age at presentation"
      ],
      "tools": []
    },
    "adenoma/9": {
      "title": "9 · Suspected malignant transformation",
      "criteria": [
        "Male patient, or a confirmed CTNNB1 exon 3 mutation",
        "Growth despite adequate risk-factor modification, or a lesion of 8 cm or more",
        "Cellular atypia, pseudoglandular formation, cholestasis, nuclear beta-catenin or strong diffuse glutamine synthetase on biopsy",
        "A TERT promoter mutation, where sequencing has been done",
        "A borderline lesion, or a hepatocellular neoplasm of uncertain malignant potential, on pathology review"
      ],
      "team": "HPB surgery · Expert liver pathology · Abdominal radiology · Hepatology",
      "inputs": [
        "Sex, growth and risk-factor response",
        "Expert histology and immunostains",
        "CTNNB1/TERT results if tested",
        "Diagnostic uncertainty and staging"
      ],
      "tools": [
        "lr5"
      ]
    },
    "adenoma/10": {
      "title": "10 · Assess transplant eligibility",
      "criteria": [
        "A qualifying guidance route named explicitly in the narrative: syndromic, molecular, adenomatosis, or progressive and complicated",
        "Unresectable after expert hepatobiliary surgical review, with embolisation and ablation exhausted, infeasible or contraindicated",
        "At least 6 months of adequate risk-factor modification documented for non-urgent oestrogen- or weight-associated disease",
        "Multidisciplinary confirmation that non-transplant options are unsafe, infeasible or inadequate and that expected benefit justifies lifelong immunosuppression and graft use",
        "No extrahepatic metastasis and no macrovascular invasion where transformation is confirmed"
      ],
      "team": "Liver transplant surgery · Transplant hepatology · HPB surgery · Interventional radiology",
      "inputs": [
        "Applicable exception-guidance category",
        "Resection, ablation and embolization feasibility",
        "Risk-factor modification and complication history",
        "Staging if transformation is confirmed"
      ],
      "tools": [
        "meld",
        "child"
      ]
    },
    "incidental/0": {
      "title": "0 · Assess background liver disease",
      "criteria": [
        "Cirrhosis of any aetiology",
        "Chronic hepatitis B infection, with or without cirrhosis",
        "Current or prior hepatocellular carcinoma, including a liver transplant candidate or recipient",
        "None of the above — a liver with no risk factor for primary liver cancer",
        "A vascular liver disorder, congenital hepatic fibrosis, or age under 18 — a separate category in which LI-RADS does not apply at all"
      ],
      "team": "Hepatology · Abdominal radiology",
      "inputs": [
        "Cirrhosis, chronic hepatitis B and HCC history",
        "Age and vascular or congenital liver disease"
      ],
      "tools": [
        "lr5"
      ]
    },
    "incidental/1": {
      "title": "1 · Known cancer outside the liver",
      "criteria": [
        "An active or previously treated extrahepatic primary with a propensity to metastasise to the liver",
        "Colorectal, breast, lung, pancreatic, gastro-oesophageal, neuroendocrine, melanoma, sarcoma or renal primary",
        "On, or recently off, systemic therapy — which changes both the parenchyma and the appearance of the lesion",
        "No known primary — in which case the pre-test probability of malignancy in a small lesion is close to nil"
      ],
      "team": "Medical oncology · Abdominal radiology",
      "inputs": [
        "Current or previous primary cancer",
        "Prior and current systemic treatment",
        "Available baseline imaging"
      ],
      "tools": []
    },
    "incidental/2": {
      "title": "2 · Characterize a cystic lesion",
      "criteria": [
        "Homogeneous water attenuation, roughly −10 to +20 HU, sharply marginated, no wall thickening, no septation, no mural nodule, no enhancement",
        "Multiple sub-15 mm cystic foci scattered through both lobes, no biliary communication on MRCP — biliary hamartomas",
        "Fever, rigors, raised inflammatory markers, a rim-enhancing collection with surrounding oedema — abscess",
        "Any septation, mural nodularity, wall thickening, enhancing component, or a daughter-cyst or membrane pattern — not a simple cyst",
        "Measured enhancement greater than 20 HU between pre- and post-contrast phases, with pseudoenhancement excluded"
      ],
      "team": "Abdominal radiology · Hepatology · HPB surgery",
      "inputs": [
        "Attenuation, enhancement and cyst morphology",
        "MRCP relationship to bile ducts",
        "Infectious symptoms and inflammatory markers"
      ],
      "tools": []
    },
    "incidental/3": {
      "title": "3 · Select the next imaging test",
      "criteria": [
        "The lesion is solid and not resolved by the study in front of you",
        "The available study lacked arterial-phase or delayed-phase imaging, or lacked contrast altogether",
        "The question is a hepatocellular one — adenoma versus focal nodular hyperplasia, or HCC in an at-risk liver",
        "The question is whether there is a second lesion anywhere else — a staging question, not a characterising one",
        "The patient cannot have the obvious test: renal function, claustrophobia, pacemaker, pregnancy, body habitus"
      ],
      "team": "Abdominal radiology · Hepatology",
      "inputs": [
        "Available imaging phases and contrast quality",
        "Characterization versus whole-disease staging question",
        "Renal function and MRI/contrast limitations"
      ],
      "tools": [
        "lr5"
      ]
    },
    "incidental/4": {
      "title": "4 · Hemangioma or focal nodular hyperplasia",
      "criteria": [
        "Haemangioma on ultrasound: homogeneously hyperechoic, sharp margin, posterior acoustic enhancement, no halo sign, under 3 cm, in a normal liver",
        "Haemangioma on contrast imaging: peripheral globular arterial enhancement with progressive central fill-in on delayed phases; strongly hyperintense on heavily T2-weighted MRI with a high apparent diffusion coefficient",
        "Focal nodular hyperplasia: homogeneous except for a central scar, near-isodense before contrast, strong homogeneous arterial enhancement becoming isodense on portal venous and delayed phases, no capsule, lobulated contour",
        "Central scar hyperintense on T2 and enhancing on delayed phase with an extracellular agent",
        "No underlying vascular liver disease, and no feature on the suspicious list"
      ],
      "team": "Abdominal radiology · Hepatology",
      "inputs": [
        "Ultrasound and contrast-enhancement pattern",
        "MRI T2, diffusion and central scar features",
        "Background vascular liver disease"
      ],
      "tools": []
    },
    "incidental/5": {
      "title": "5 · Pseudolesions and benign liver nodules",
      "criteria": [
        "Focal fat or focal fat sparing in a characteristic site — adjacent to the falciform ligament or ligamentum venosum, the gallbladder fossa, the porta hepatis, or subcapsular",
        "Geometric or straight-edged margin, no displacement of traversing vessels, no mass effect",
        "A transient hepatic attenuation or intensity difference — peripheral, wedge-shaped, present on one phase only",
        "A regenerative nodule in a cirrhotic liver with no major feature and nothing suspicious",
        "A regenerative or focal-nodular-hyperplasia-like nodule in a liver with a vascular disorder"
      ],
      "team": "Abdominal radiology · Hepatology",
      "inputs": [
        "Lesion shape, location, vessels and mass effect",
        "Phase-specific enhancement",
        "Cirrhosis or vascular liver disorder"
      ],
      "tools": [
        "lr5"
      ]
    },
    "incidental/6": {
      "title": "6 · Indeterminate liver lesion",
      "criteria": [
        "Under 10 mm, and reported as too small to characterise",
        "Seen on one modality and not on another, with no explanation for the discrepancy",
        "Indeterminate after an adequate multiphase MRI",
        "LR-3 or LR-4 in an at-risk liver, where the category is itself a statement of uncertainty",
        "Indeterminate in a patient whose treatment decision cannot wait for an interval"
      ],
      "team": "Abdominal radiology · Hepatology · Relevant oncology specialty",
      "inputs": [
        "Lesion size and imaging quality",
        "Cross-modality or interval comparison",
        "LI-RADS category when applicable",
        "Urgency of the treatment decision"
      ],
      "tools": [
        "lr5"
      ]
    },
    "incidental/7": {
      "title": "7 · Decide whether and how to biopsy",
      "criteria": [
        "The destination is named before any needle is passed: resection, transplant pathway, systemic therapy, or discharge",
        "The result will change management — not merely confirm what the plan already assumes",
        "The lesion is not a resectable colorectal metastasis, and the patient is not a candidate for a perihilar transplant protocol",
        "Suspected perihilar cholangiocarcinoma has been excluded, or the transplant pathway has been reviewed first",
        "Core biopsy rather than fine-needle aspiration, with the route and the specimen priorities agreed in advance"
      ],
      "team": "HPB surgery · Liver transplant team · Interventional radiology · Pathology",
      "inputs": [
        "Intended treatment and whether tissue will change it",
        "Transplant review before sampling suspected pCCA",
        "Safest route and specimen priorities"
      ],
      "tools": []
    },
    "incidental/8": {
      "title": "8 · Select the disease-specific roadmap",
      "criteria": [
        "LR-5, or LR-4 after board discussion, in an at-risk liver",
        "An LR-M or targetoid observation, or a peripheral mass with capsular retraction and delayed central enhancement",
        "A confirmed colorectal or neuroendocrine primary",
        "A hepatocellular lesion in a normal liver that is not focal nodular hyperplasia",
        "A lesion carrying both hepatocellular and cholangiocytic phenotypes, or discordant markers"
      ],
      "team": "Abdominal radiology · Hepatology · HPB surgery · Medical oncology",
      "inputs": [
        "Imaging phenotype and background liver disease",
        "Known primary cancer",
        "Histology and discordant tumor markers"
      ],
      "tools": [
        "lr5"
      ]
    },
    "pdac/0": {
      "title": "0 · Obtain adequate staging imaging",
      "criteria": [
        "Pancreas-protocol multiphase CT with a pancreatic parenchymal phase at 40–50 seconds and a portal venous phase at 65–70 seconds",
        "Chest and pelvis CT in the same episode, for complete staging",
        "CA 19-9 and liver function drawn after biliary decompression, not before",
        "Genetic counselling and germline testing offered to every patient, whatever the stage",
        "High-quality imaging no more than 4 weeks old at the time of the operation"
      ],
      "team": "Abdominal radiology · HPB surgery · Medical oncology · Genetics",
      "inputs": [
        "Pancreas-protocol CT and chest/pelvis staging",
        "Imaging date and adequate enhancement phases",
        "CA 19-9 and liver tests after decompression",
        "Germline testing status"
      ],
      "tools": []
    },
    "pdac/1": {
      "title": "1 · Classify resectability",
      "criteria": [
        "Arterial contact stated in degrees against the celiac axis, superior mesenteric artery and common hepatic artery",
        "Venous contact stated in degrees against the SMV and portal vein, with contour irregularity and thrombosis recorded separately",
        "Variant arterial anatomy named, with the degree of contact if present",
        "No distant metastasis, including non-regional nodal metastasis",
        "The category agreed by consensus at a multidisciplinary meeting, not assigned by one reader",
        "Someone has asked whether this scan would survive a central review, because roughly a third of patients called resectable by their own centres do not"
      ],
      "team": "HPB surgery · Abdominal radiology · Medical oncology",
      "inputs": [
        "Arterial and venous contact by named vessel",
        "Contact angle, contour change and thrombosis",
        "Variant arteries and distant staging",
        "Multidisciplinary resectability review"
      ],
      "tools": []
    },
    "pdac/2": {
      "title": "2 · Plan tissue sampling and biliary drainage",
      "criteria": [
        "Obstructive jaundice with cholangitis, fever, or intense pruritus",
        "Neoadjuvant therapy planned, or the operation delayed for any reason",
        "A tissue diagnosis is required because the next treatment is not an operation",
        "The diagnosis is uncertain and a removable stent would preserve the option of re-biopsy",
        "Metastatic disease, where enough tissue for next-generation sequencing is itself an indication"
      ],
      "team": "Advanced gastroenterology · HPB surgery · Medical oncology · Pathology",
      "inputs": [
        "Jaundice, cholangitis and symptom severity",
        "Timing of surgery or neoadjuvant treatment",
        "Tissue diagnosis and molecular specimen needs"
      ],
      "tools": []
    },
    "pdac/3": {
      "title": "3 · Resectable disease: surgery or neoadjuvant treatment",
      "criteria": [
        "No arterial tumour contact with the celiac axis, superior mesenteric artery or common hepatic artery",
        "No SMV or portal vein contact, or contact of ≤180° without vein contour irregularity",
        "No distant metastasis, including non-regional nodes",
        "Fit for pancreatoduodenectomy or distal pancreatectomy at a high-volume centre",
        "High-risk features either absent, or present and named in the note"
      ],
      "team": "HPB surgery · Medical oncology · Abdominal radiology",
      "inputs": [
        "Vessel contact and venous contour",
        "Distant and nonregional nodal staging",
        "Operative fitness and high-risk features"
      ],
      "tools": [
        "ecog"
      ]
    },
    "pdac/4": {
      "title": "4 · Borderline resectable disease: treat and reassess",
      "criteria": [
        "Head or uncinate: solid tumour contact with the SMA of ≤180°, or with the common hepatic artery without extension to the celiac axis or hepatic artery bifurcation",
        "Body or tail: solid tumour contact with the celiac axis of ≤180°",
        "SMV or portal vein contact of >180°, or ≤180° with contour irregularity, or vein thrombosis with suitable vessel above and below for reconstruction",
        "Solid tumour contact with the inferior vena cava",
        "Solid tumour contact with variant arterial anatomy, with the degree of contact recorded"
      ],
      "team": "HPB surgery · Medical oncology · Abdominal radiology · Radiation oncology",
      "inputs": [
        "Tumor location and arterial contact",
        "Venous contact, thrombosis and reconstructable segments",
        "Variant arterial anatomy and IVC contact"
      ],
      "tools": [
        "ecog"
      ]
    },
    "pdac/5": {
      "title": "5 · Resection margins and lymph-node staging",
      "criteria": [
        "Pancreatoduodenectomy for head and uncinate tumours; distal pancreatectomy for body and tail",
        "Standard, not extended, lymphadenectomy",
        "Peritoneal washings sent, and the result recorded in the operative note",
        "Specimen inked and sliced to a protocol that allows millimetre reporting of every margin",
        "Done at a high-volume centre, by a surgeon who does them"
      ],
      "team": "HPB surgery · Pathology",
      "inputs": [
        "Tumor location and planned operation",
        "Lymph-node plan and peritoneal cytology",
        "Specimen orientation and measured margins"
      ],
      "tools": []
    },
    "pdac/6": {
      "title": "6 · Adjuvant therapy and surveillance",
      "criteria": [
        "A macroscopically complete resection has been performed",
        "Restaging before adjuvant therapy shows no recurrence",
        "Performance status and recovery allow a multiagent regimen, or do not",
        "No neoadjuvant therapy was given — or it was, and the response is known",
        "Germline and somatic results are back, or have been chased"
      ],
      "team": "Medical oncology · HPB surgery · Abdominal radiology",
      "inputs": [
        "Resection pathology and postoperative restaging",
        "Recovery, performance status and prior treatment response",
        "Germline and somatic results"
      ],
      "tools": [
        "ecog"
      ]
    },
    "pdac/7": {
      "title": "7 · Locally advanced disease: treatment and reassessment",
      "criteria": [
        "Head or uncinate: solid tumour contact of >180° with the SMA or celiac axis",
        "Body or tail: solid tumour contact of >180° with the SMA or celiac axis, or contact with the celiac axis and aortic involvement",
        "Complete occlusion of the SMV or portal vein not amenable to resection and primary reconstruction",
        "No distant metastasis",
        "Performance status and biliary drainage adequate for multiagent therapy, or not"
      ],
      "team": "Medical oncology · HPB surgery · Abdominal radiology · Radiation oncology",
      "inputs": [
        "Arterial/venous involvement and reconstructability",
        "Distant staging",
        "Performance status and biliary drainage"
      ],
      "tools": [
        "ecog"
      ]
    },
    "pdac/8": {
      "title": "8 · Metastatic disease: systemic treatment",
      "criteria": [
        "Distant metastasis on imaging, or positive peritoneal cytology",
        "A tissue diagnosis with enough material banked for next-generation sequencing",
        "Performance status graded: ECOG 0–1 with good biliary drainage and nutrition, ECOG 2, or poor",
        "Germline testing and comprehensive genomic profiling ordered, with HER2 immunohistochemistry",
        "Biliary and gastric outlet patency, pain, nutrition and thrombosis addressed as treatment, not afterthoughts"
      ],
      "team": "Medical oncology · Advanced gastroenterology · Palliative care · Genetics",
      "inputs": [
        "Metastatic sites, cytology and tissue diagnosis",
        "ECOG, nutrition and biliary/gastric outlet patency",
        "Genomic, germline and HER2 results",
        "Pain and thrombosis assessment"
      ],
      "tools": [
        "ecog"
      ]
    },
    "pnet/1": {
      "title": "1 · Confirm differentiation and grade",
      "criteria": [
        "Well-differentiated neuroendocrine tumour, not a poorly differentiated neuroendocrine carcinoma",
        "An exact Ki-67 proliferative index reported as a number, not a range, with the mitotic count per 2 mm²",
        "Two of synaptophysin, chromogranin A and INSM1 positive, with a broad-spectrum keratin",
        "Acinar cell carcinoma and the other neuroendocrine-marker mimics excluded where the morphology is unusual",
        "Functional status recorded as a clinical and biochemical judgement, not an immunohistochemical one"
      ],
      "team": "Expert pathology · NET medical oncology · Endocrinology",
      "inputs": [
        "Differentiation, Ki-67 and mitotic count",
        "Neuroendocrine immunostains and diagnostic mimics",
        "Clinical and biochemical functional status"
      ],
      "tools": []
    },
    "pnet/2": {
      "title": "2 · Stage the disease",
      "criteria": [
        "Multiphasic CT or MRI of the abdomen, with arterial and portal venous phases, covering the whole pancreas",
        "Somatostatin-receptor PET/CT or PET/MRI where receptor status or occult metastatic disease would change the plan",
        "Chest CT, and FDG-PET where the tumour is G2 or higher",
        "Main pancreatic duct calibre, tumour calcification and cystic morphology recorded explicitly",
        "Liver and nodal status stated before any operation is booked"
      ],
      "team": "Abdominal radiology · Nuclear medicine · HPB surgery · NET medical oncology",
      "inputs": [
        "Multiphase pancreas/abdominal imaging and chest CT",
        "Receptor imaging and FDG-PET when indicated",
        "Duct caliber, morphology, liver and nodal status"
      ],
      "tools": []
    },
    "pnet/3": {
      "title": "3 · Control hormone-related symptoms",
      "criteria": [
        "Insulinoma — neuroglycopenic symptoms with raised insulin, pro-insulin and C-peptide during concurrent hypoglycaemia",
        "Gastrinoma — Zollinger-Ellison syndrome with a raised fasting gastrin, interpreted against proton-pump inhibitor use",
        "Glucagonoma — glucagon excess with diabetes or necrolytic migratory erythema",
        "VIPoma — watery diarrhoea, hypokalaemia and achlorhydria with a raised VIP",
        "Any other documented syndrome: somatostatinoma, ACTHoma, PTHrPoma, calcitoninoma, GHRHoma"
      ],
      "team": "Endocrinology · NET medical oncology · HPB surgery",
      "inputs": [
        "Syndrome-specific symptoms and biochemical testing",
        "Concurrent glucose and insulin-related tests when relevant",
        "Medication effects on hormone results"
      ],
      "tools": []
    },
    "pnet/4": {
      "title": "4 · Small nonfunctional tumor: surveillance or resection",
      "criteria": [
        "Incidentally discovered, sporadic and non-functional, with no hormonal syndrome",
        "2 cm or smaller on the index multiphasic CT or MRI, and low grade",
        "No radiological nodal or distant disease, no vascular invasion",
        "Main pancreatic duct not dilated",
        "A patient who will actually come back for imaging, with the surgical risk and comorbidity burden stated"
      ],
      "team": "HPB surgery · NET medical oncology · Abdominal radiology",
      "inputs": [
        "Functional status, size and grade",
        "Duct caliber, vascular invasion and nodal/distant staging",
        "Comorbidity, surgical risk and follow-up feasibility"
      ],
      "tools": [
        "ecog"
      ]
    },
    "pnet/5": {
      "title": "5 · Select the operation",
      "criteria": [
        "Nonfunctional tumour larger than 2 cm, or invasive, or node-positive on imaging",
        "Malignant-appearing tumour of any size",
        "A functional tumour that has been localised",
        "A 1–2 cm tumour where the board has decided to resect",
        "Patient fit for the operation that the tumour's position actually requires"
      ],
      "team": "HPB surgery · NET medical oncology · Abdominal radiology",
      "inputs": [
        "Size, location and invasive/nodal features",
        "Functional syndrome and localization",
        "Fitness for the required operation"
      ],
      "tools": [
        "ecog"
      ]
    },
    "pnet/6": {
      "title": "6 · Plan lymph-node assessment",
      "criteria": [
        "A formal pancreatoduodenectomy or distal pancreatectomy is planned",
        "Tumour larger than 1.5 cm, or in the head of the pancreas",
        "Ki-67 above 20%, or lymphovascular invasion on biopsy",
        "Suspicious nodes on preoperative imaging or at exploration",
        "A parenchyma-sparing operation is planned for a tumour of 2 cm or less"
      ],
      "team": "HPB surgery · Abdominal radiology · Pathology",
      "inputs": [
        "Planned operation, size and location",
        "Ki-67 and lymphovascular invasion",
        "Suspicious nodes on imaging or exploration"
      ],
      "tools": []
    },
    "pnet/7": {
      "title": "7 · Assess hereditary disease",
      "criteria": [
        "Gastrinoma of the duodenum or pancreas, or a type 2 gastric NET",
        "Multifocal pancreatic neuroendocrine tumours",
        "Known or clinically suspected MEN1, MEN4, von Hippel-Lindau, NF1 or tuberous sclerosis",
        "Primary hyperparathyroidism before age 30, multiple parathyroid adenomas, or recurrent hyperparathyroidism",
        "A young patient, or a family history of any MEN1-associated tumour"
      ],
      "team": "Genetics · Endocrinology · NET medical oncology",
      "inputs": [
        "Primary site and multifocality",
        "Known or suspected hereditary syndrome",
        "Age, parathyroid disease and family history"
      ],
      "tools": []
    },
    "pnet/8": {
      "title": "8 · G3 NET versus neuroendocrine carcinoma",
      "criteria": [
        "Ki-67 above 20% or more than 20 mitoses per 2 mm²",
        "Well-differentiated morphology with a high proliferative index — a G3 NET",
        "Small-cell or large-cell poorly differentiated morphology — a neuroendocrine carcinoma",
        "A mixed neuroendocrine–non-neuroendocrine neoplasm, each component at least 30%",
        "Grade progression in a tumour previously called G1 or G2"
      ],
      "team": "Expert pathology · NET medical oncology",
      "inputs": [
        "Ki-67, mitotic count and differentiation",
        "Mixed histology and component proportions",
        "Prior grade and progression"
      ],
      "tools": []
    },
    "pnet/9": {
      "title": "9 · Follow-up after resection",
      "criteria": [
        "A completely resected primary tumour",
        "An observed tumour being followed on the same schedule",
        "Grade, nodal status and perineural invasion known from the specimen",
        "Functional syndrome status, for biochemical follow-up",
        "Recurrence found — local, pancreatic remnant, or hepatic"
      ],
      "team": "HPB surgery · NET medical oncology · Abdominal radiology · Endocrinology",
      "inputs": [
        "Resection status and surveillance imaging",
        "Grade, nodes and perineural invasion",
        "Functional syndrome markers and recurrence sites"
      ],
      "tools": []
    },
    "pcyst/1": {
      "title": "1 · Identify the cyst type",
      "criteria": [
        "MRI with MRCP, or pancreas-protocol CT where MRI is contraindicated, reviewed with the cyst's relation to the main duct established",
        "Main pancreatic duct diameter recorded in millimetres, not as the word 'dilated'",
        "History of pancreatitis, alcohol or trauma taken — a pseudocyst does not belong on an oncological pathway",
        "Septation, mural nodule with its height in millimetres, wall calcification, central scar, solid component and location all recorded",
        "Whether a prior study exists, on which modality, and over what interval"
      ],
      "team": "Advanced gastroenterology · Abdominal radiology · HPB surgery",
      "inputs": [
        "MRI/MRCP or pancreas-protocol CT",
        "Duct communication and measured duct diameter",
        "Cyst morphology, nodule height and prior imaging",
        "Pancreatitis, alcohol and trauma history"
      ],
      "tools": []
    },
    "pcyst/2": {
      "title": "2 · Assess high-risk features",
      "criteria": [
        "Obstructive jaundice in a patient with a cystic lesion of the head of the pancreas",
        "Enhancing mural nodule of 5 mm or more, or a solid component",
        "Main pancreatic duct of 10 mm or more",
        "Cytology suspicious or positive for high-grade dysplasia or invasive carcinoma, where cytology was obtained"
      ],
      "team": "Advanced gastroenterology · HPB surgery · Abdominal radiology",
      "inputs": [
        "Obstructive jaundice",
        "Enhancing nodule/solid component and duct diameter",
        "Cytology when obtained"
      ],
      "tools": []
    },
    "pcyst/3": {
      "title": "3 · Assess worrisome features",
      "criteria": [
        "Cyst of 30 mm or more, or growth of 2.5 mm per year or faster",
        "Enhancing mural nodule under 5 mm, or thickened or enhancing cyst walls",
        "Main pancreatic duct 5 to 9 mm, or an abrupt change in duct calibre with distal atrophy",
        "Acute pancreatitis, new-onset or worsening diabetes, or a raised serum CA 19-9",
        "Regional lymphadenopathy"
      ],
      "team": "Advanced gastroenterology · Abdominal radiology · HPB surgery",
      "inputs": [
        "Cyst size and interval growth",
        "Mural nodules, wall and duct features",
        "Pancreatitis, diabetes and CA 19-9",
        "Regional nodes"
      ],
      "tools": []
    },
    "pcyst/4": {
      "title": "4 · Select cyst-fluid testing",
      "criteria": [
        "Enough fluid aspirated to allocate between chemistry, cytology and molecular testing before any tube is sent",
        "The question the aspirate is meant to answer stated first — is it mucinous, or does it harbour advanced neoplasia?",
        "Glucose and CEA on the same specimen where volume allows",
        "Cytology sent in every case",
        "Molecular panel sent only where the result would change management and where funding is confirmed"
      ],
      "team": "Advanced gastroenterology · Pathology · Molecular pathology",
      "inputs": [
        "Clinical question and aspirate volume",
        "Cyst-fluid glucose, CEA and cytology",
        "Need and feasibility of molecular testing"
      ],
      "tools": []
    },
    "pcyst/5": {
      "title": "5 · Manage cysts other than IPMN",
      "criteria": [
        "Mucinous cystic neoplasm — non-communicating, usually body or tail, ovarian-type stroma on histology",
        "Serous cystadenoma — microcystic or honeycomb, central scar or calcification, no duct communication",
        "Solid pseudopapillary neoplasm — young woman, solid and cystic, often large",
        "Cystic neuroendocrine tumour — enhancing rim, often in a hereditary syndrome",
        "Pseudocyst or walled-off collection — a pancreatitis history, high amylase, no epithelium"
      ],
      "team": "Advanced gastroenterology · Abdominal radiology · HPB surgery · Pathology",
      "inputs": [
        "Duct communication and cyst morphology",
        "Clinical context and pancreatitis history",
        "Fluid analysis or histology when available"
      ],
      "tools": []
    },
    "pcyst/6": {
      "title": "6 · Assess surgical fitness and expected benefit",
      "criteria": [
        "Fitness for the specific operation the lesion's position requires, assessed before any threshold is quoted",
        "Life expectancy from competing causes estimated and written down alongside the cyst's risk",
        "Age, comorbidity and the patient's own preference recorded, as Kyoto 2024 requires",
        "The operation's own morbidity and mortality quoted to the patient in numbers",
        "A high-volume pancreatic service available to do it"
      ],
      "team": "HPB surgery · Anesthesiology · Advanced gastroenterology",
      "inputs": [
        "Fitness for the proposed operation",
        "Age, comorbidity and competing life expectancy",
        "Patient preference and procedure-specific risk"
      ],
      "tools": [
        "ecog"
      ]
    },
    "pcyst/7": {
      "title": "7 · Plan the extent of resection",
      "criteria": [
        "Whether invasive carcinoma is suspected, because that decides oncological versus parenchyma-sparing resection",
        "Length of main-duct involvement, and whether a total pancreatectomy is foreseeable",
        "The possibility of total pancreatectomy discussed with the patient before the operation, whatever the plan",
        "Intraoperative frozen section of the duct transection margin available",
        "Lymphadenectomy planned where invasive carcinoma is suspected, omitted where it is not"
      ],
      "team": "HPB surgery · Pathology · Advanced gastroenterology",
      "inputs": [
        "Suspicion of invasion and duct involvement",
        "Extent of resection and total-pancreatectomy implications",
        "Frozen-section and lymph-node plan"
      ],
      "tools": []
    },
    "pcyst/8": {
      "title": "8 · Surveillance without resection",
      "criteria": [
        "A named interval schedule, chosen from one guideline and written down, not assembled case by case",
        "The same modality each time, with MRI and MRCP preferred where available",
        "A named owner for the recall, and a system that will actually recall",
        "Size, main duct diameter and nodule status recorded at every visit so growth rate can be computed",
        "A review date at which the interval itself is reassessed, not only the cyst"
      ],
      "team": "Advanced gastroenterology · Abdominal radiology · HPB surgery",
      "inputs": [
        "Chosen guideline and surveillance interval",
        "Comparable imaging, size, duct and nodule measurements",
        "Growth calculation and recall plan"
      ],
      "tools": []
    },
    "pcyst/9": {
      "title": "9 · Consider stopping surveillance",
      "criteria": [
        "No longer a candidate for pancreatectomy, on fitness or on the patient's own decision — the one trigger all four guidelines share",
        "Five years of documented stability with no worrisome feature, in a cyst under the programme's stated size threshold",
        "Age and size meeting the programme's stated age-and-size rule, where it has adopted one",
        "Competing-risk estimate short enough that the cyst cannot become the cause of death"
      ],
      "team": "Advanced gastroenterology · HPB surgery · Primary care",
      "inputs": [
        "Current operative fitness and patient preference",
        "Duration of stability and prior risk features",
        "Age, cyst size and competing life expectancy"
      ],
      "tools": [
        "ecog"
      ]
    },
    "pcyst/10": {
      "title": "10 · Surveillance after resection",
      "criteria": [
        "Final histology, with the highest grade in the specimen and the margin status including whether the margin was denuded",
        "Whether any residual cyst was knowingly left in the remnant, and where",
        "Family history of pancreatic cancer established, because it changes the interval in Kyoto 2024",
        "A surveillance schedule assigned at discharge, not at the first outpatient visit",
        "Whether the patient remains fit for a second operation, because that is what the surveillance is for"
      ],
      "team": "HPB surgery · Advanced gastroenterology · Pathology · Abdominal radiology",
      "inputs": [
        "Final histology, highest grade and margin status",
        "Residual cyst map and family history",
        "Follow-up schedule and fitness for repeat surgery"
      ],
      "tools": []
    },
    "ampullary/0": {
      "title": "0 · Define tumor origin and extent",
      "criteria": [
        "Pancreatic-protocol CT of the abdomen and pelvis plus CT chest, before elective instrumentation",
        "Duodenoscopy with a side-viewing instrument, with targeted biopsies, and colonoscopy if not already done",
        "EUS and MRI with MRCP where an endoscopic resection is being considered or intraductal extension is in question",
        "Liver function tests, baseline CA 19-9 and CEA",
        "The epicentre recorded — ampulla, non-ampullary duodenum or distal bile duct — because that is what sets the prognosis"
      ],
      "team": "Advanced gastroenterology · HPB surgery · Abdominal radiology",
      "inputs": [
        "Pancreas-protocol CT and chest staging",
        "Side-viewing duodenoscopy, biopsies and colonoscopy",
        "EUS/MRCP when indicated",
        "Tumor epicenter, liver tests, CA 19-9 and CEA"
      ],
      "tools": []
    },
    "ampullary/1": {
      "title": "1 · Assess the limitations of an adenoma biopsy",
      "criteria": [
        "High-grade dysplasia anywhere in the biopsy",
        "Bile duct or pancreatic duct dilatation on imaging",
        "Symptoms — jaundice, pancreatitis, weight loss, pain",
        "Age 65 or over",
        "Villous architecture, an ulcerated or firm papilla, or a markedly raised CA 19-9 or CEA"
      ],
      "team": "Advanced gastroenterology · Pathology · HPB surgery",
      "inputs": [
        "Biopsy grade and architecture",
        "Duct dilation and endoscopic appearance",
        "Symptoms, age and tumor markers"
      ],
      "tools": []
    },
    "ampullary/2": {
      "title": "2 · Assess endoscopic papillectomy",
      "criteria": [
        "Adenoma proven on biopsy, with no suspicion of invasive carcinoma — high-grade dysplasia alone does not exclude the operation",
        "No intraductal extension, or extension short enough that the resection can clear it",
        "Size that can be taken en bloc — ESGE sets 20 to 30 mm as the ceiling for an en bloc intent",
        "Duodenal anatomy that permits access, with no diverticulum preventing it",
        "A high-volume centre, and a patient who will attend surveillance for at least five years"
      ],
      "team": "Advanced gastroenterology · HPB surgery · Abdominal radiology",
      "inputs": [
        "Adenoma pathology and suspicion of invasion",
        "Lesion size and intraductal extension",
        "Duodenal access and surveillance feasibility"
      ],
      "tools": []
    },
    "ampullary/3": {
      "title": "3 · Review the papillectomy pathology",
      "criteria": [
        "Deep or lateral margin positive, or indeterminate",
        "Invasive carcinoma in the specimen that was not expected",
        "Resection was piecemeal, so no margin can be assessed",
        "Lymphovascular or perineural invasion, poor differentiation, or high tumour budding",
        "Specimen orientation was not agreed with the pathologist before it was sent"
      ],
      "team": "Pathology · Advanced gastroenterology · HPB surgery",
      "inputs": [
        "Margin status, orientation and en-bloc/piecemeal resection",
        "Invasion, differentiation and tumor budding",
        "Lymphovascular and perineural invasion"
      ],
      "tools": []
    },
    "ampullary/4": {
      "title": "4 · Select local surgical excision or pancreaticoduodenectomy",
      "criteria": [
        "Adenoma not clearable endoscopically — size, diverticulum, intraductal extension over 20 mm, or repeated positive margins",
        "No invasive carcinoma demonstrated, and a malignancy risk score that is not high",
        "Patient fit for a transduodenal operation, at a centre that performs them",
        "An ampullary neuroendocrine tumour — which is a different decision and belongs with resection",
        "Familial adenomatous polyposis with Spigelman stage IV disease unsuitable for endoscopic therapy"
      ],
      "team": "HPB surgery · Advanced gastroenterology · Pathology",
      "inputs": [
        "Endoscopic clearance feasibility and duct extension",
        "Histology and malignancy risk",
        "Operative fitness and polyposis status"
      ],
      "tools": [
        "ecog"
      ]
    },
    "ampullary/5": {
      "title": "5 · Pancreaticoduodenectomy for invasive carcinoma",
      "criteria": [
        "Invasive ampullary adenocarcinoma, or a lesion whose malignancy risk makes a cancer operation correct",
        "No peritoneal, hepatic or distant nodal metastases on staging or at operation",
        "Patient fit for pancreatoduodenectomy with reconstruction",
        "High-volume centre, with a pathologist briefed on orientation and margins",
        "Biliary stent only where clinical decision 0's indications were met"
      ],
      "team": "HPB surgery · Abdominal radiology · Pathology · Anesthesiology",
      "inputs": [
        "Invasion or malignancy risk",
        "Peritoneal, liver and distant nodal staging",
        "Operative fitness and reconstruction plan"
      ],
      "tools": [
        "ecog"
      ]
    },
    "ampullary/6": {
      "title": "6 · Histologic subtype and molecular testing",
      "criteria": [
        "Subtype assigned on the invasive component, not on the precursor lesion",
        "Mixed subtype used only when the lesser component is at least 30% of the tumour",
        "Tubular-NOS used where a confident call cannot be made, with the favoured lineage stated",
        "Mismatch-repair testing done as a reflex, independent of subtype",
        "Somatic profiling where metastatic disease and anticancer therapy are both in prospect"
      ],
      "team": "Pathology · Molecular pathology · Medical oncology",
      "inputs": [
        "Invasive-component subtype and proportions",
        "Mismatch-repair testing",
        "Advanced-disease molecular profiling"
      ],
      "tools": []
    },
    "ampullary/7": {
      "title": "7 · Adjuvant treatment after resection",
      "criteria": [
        "Stage II or III resected ampullary adenocarcinoma",
        "Node-positive disease, or a close or positive margin",
        "Medically fit, and within 12 weeks of surgery",
        "Subtype reported on the invasive component, with the mismatch-repair result available",
        "Stage I disease — where observation is an explicit NCCN option"
      ],
      "team": "Medical oncology · HPB surgery · Pathology",
      "inputs": [
        "Stage, nodes and margin status",
        "Recovery, fitness and time from surgery",
        "Invasive subtype and mismatch-repair result"
      ],
      "tools": [
        "ecog"
      ]
    },
    "ampullary/8": {
      "title": "8 · Locally advanced or metastatic disease",
      "criteria": [
        "Distant metastases on staging, with biopsy confirmation preferably from a metastatic site",
        "Locally advanced disease, after a second opinion on unresectability",
        "Performance status recorded as ECOG, with biliary drainage and nutrition assessed",
        "Somatic molecular profiling and germline testing done or ordered",
        "Recurrence after resection"
      ],
      "team": "Medical oncology · HPB surgery · Advanced gastroenterology · Palliative care",
      "inputs": [
        "Stage, tissue diagnosis and unresectability review",
        "ECOG, nutrition and drainage",
        "Somatic/germline results and recurrence history"
      ],
      "tools": [
        "ecog"
      ]
    },
    "ampullary/9": {
      "title": "9 · Surveillance and hereditary disease",
      "criteria": [
        "Endoscopic papillectomy or surgical ampullectomy performed — surveillance is mandatory either way",
        "Pancreatoduodenectomy for adenoma — NCCN requires no surveillance",
        "Resected ampullary adenocarcinoma — oncological surveillance for 5 years",
        "Familial adenomatous polyposis, attenuated FAP or MUTYH-associated polyposis",
        "An abnormal-looking ampulla in a polyposis patient, at any Spigelman stage"
      ],
      "team": "Advanced gastroenterology · HPB surgery · Genetics · Medical oncology",
      "inputs": [
        "Prior operation and final diagnosis",
        "Polyposis status and family history",
        "Endoscopic findings and surveillance schedule"
      ],
      "tools": []
    },
    "hcc/0": {
      "title": "0 · Very early",
      "criteria": [
        "Single lesion ≤2 cm",
        "ECOG 0",
        "Child-Pugh A",
        "No clinically significant portal hypertension"
      ],
      "team": "Hepatology · HPB surgery · Interventional radiology",
      "inputs": [
        "Liver imaging: lesion number and diameter",
        "ECOG performance status",
        "Child-Pugh class and portal hypertension"
      ],
      "tools": [
        "lr5",
        "ecog",
        "child",
        "meld"
      ]
    },
    "hcc/A": {
      "title": "A · Early",
      "criteria": [
        "Solitary of any size, or ≤3 nodules each ≤3 cm",
        "ECOG 0",
        "Preserved liver function",
        "No macrovascular invasion or extrahepatic spread"
      ],
      "team": "HPB surgery · Liver transplant surgery · Hepatology · Interventional radiology",
      "inputs": [
        "Liver imaging: lesion number and diameters",
        "Vascular invasion and extrahepatic staging",
        "ECOG, liver reserve and resection feasibility"
      ],
      "tools": [
        "lr5",
        "ecog",
        "child",
        "meld"
      ]
    },
    "hcc/B": {
      "title": "B · Intermediate",
      "criteria": [
        "Multinodular, beyond stage A",
        "Liver-confined",
        "ECOG 0",
        "Preserved liver function"
      ],
      "team": "Hepatology · Interventional radiology · Medical oncology · Liver transplant surgery",
      "inputs": [
        "Tumor distribution and total liver burden",
        "Extrahepatic staging",
        "ECOG and liver reserve"
      ],
      "tools": [
        "ecog",
        "child",
        "meld",
        "lrt",
        "systemic"
      ]
    },
    "hcc/C": {
      "title": "C · Advanced",
      "criteria": [
        "Macrovascular invasion",
        "Extrahepatic spread",
        "Cancer-related ECOG 1–2"
      ],
      "team": "Medical oncology · Hepatology · Interventional radiology · Radiation oncology",
      "inputs": [
        "Vascular invasion and extrahepatic staging",
        "ECOG and cause of functional impairment",
        "Liver function and treatment history"
      ],
      "tools": [
        "ecog",
        "child",
        "systemic"
      ]
    },
    "hcc/D": {
      "title": "D · Terminal",
      "criteria": [
        "ECOG 3–4",
        "Child-Pugh C not correctable by transplant"
      ],
      "team": "Hepatology · Palliative care · Liver transplant team",
      "inputs": [
        "ECOG and reversible causes of impairment",
        "Child-Pugh class",
        "Transplant suitability and patient goals"
      ],
      "tools": [
        "ecog",
        "child",
        "meld"
      ]
    }
  }
};
