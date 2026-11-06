"""Manually maintained English vocabulary for synthetic research conversations.

Ordinary medical terms, not a trained NER model or complete medical ontology.
This extension was developed after inspecting the development corpus; evaluation
on that corpus is regression evidence, never unseen validation.
"""
DISEASES = [
    'pneumonia', 'tuberculosis', 'infection', 'infections', 'pulmonary embolism',
    'atrial fibrillation', 'coronary artery disease', 'cardiac disease',
    'cardiomyopathy', 'hypertrophic cardiomyopathy', 'obstructive sleep apnea',
    'sleep apnea', 'rheumatoid arthritis', 'psoriatic arthritis',
    'breast cancer', 'prostate cancer', 'lung cancer', 'thyroid cancer',
    'colorectal cancer', 'esophageal adenocarcinoma', 'pancreatic adenocarcinoma',
    'hepatocellular carcinoma', 'metastatic disease', 'brain metastases',
    'metastasis', 'metastases', 'diabetic retinopathy', 'macular degeneration',
    'glaucoma', 'cataracts', 'gout', 'osteoporosis', 'nephropathy',
    'pulmonary fibrosis', 'sarcoidosis', 'hypercalcemia', 'hypoglycemia',
    'ketoacidosis', 'endocarditis', 'pericarditis', 'pleuritis',
    'pericardial effusion', 'trigeminal neuralgia', 'radiculopathy',
    'narcolepsy', 'restless leg syndrome', 'alcohol dependence',
    'opioid use disorder', 'inflammatory bowel disease', 'ulcerative colitis',
    'huntington disease', 'wilson disease', 'porphyria', 'otosclerosis',
]
SYMPTOMS = [
    'weakness', 'cognitive decline', 'memory loss', 'suicidal ideation',
    'syncope', 'presyncope', 'dysarthria', 'dysphagia', 'tinnitus',
    'hematuria', 'proteinuria', 'hemoptysis', 'hematemesis', 'melena',
    'ascites', 'jaundice', 'neuropathy', 'cluster headaches',
    'wall motion abnormalities', 'lymph node involvement', 'lymphadenopathy',
    'herniation', 'renal involvement', 'cardiac involvement', 'ocular involvement',
    'neurological symptoms', 'bowel changes', 'recurrence', 'anastomotic leak',
    'exocrine insufficiency', 'acute exacerbation', 'current attack',
    'cardiac iron deposition', 'rejection', 'illicit drug use',
]
MEDICATIONS = [
    'carvedilol', 'spironolactone', 'furosemide', 'methotrexate',
    'hydroxychloroquine', 'levodopa', 'carbidopa', 'carboplatin',
    'paclitaxel', 'tamoxifen', 'letrozole', 'anastrozole', 'adalimumab',
    'infliximab', 'tacrolimus', 'mycophenolate', 'buprenorphine',
    'topiramate', 'sumatriptan', 'latanoprost', 'celecoxib', 'alendronate',
    'nintedanib', 'pirfenidone', 'trientine', 'deferasirox',
]
