"""Build a reproducible, CC0 English terminology snapshot, not model weights.

Only the operator runs this script. The application never downloads an ontology
while handling a visit. Obsolete concepts are excluded; ambiguous aliases retain
all concept IDs so no disease subtype is silently assigned.
"""
import hashlib
import json
import re
from collections import defaultdict
from pathlib import Path
from urllib.request import urlopen

REVISION = 'bd7dcdf405e03d3f896089ece856209861946e56'
BASE = f'https://raw.githubusercontent.com/DiseaseOntology/HumanDiseaseOntology/{REVISION}'
SOURCE = BASE + '/src/ontology/doid.obo'
ROOT = Path(__file__).resolve().parents[1]
GENERIC = {'disease', 'diseases', 'syndrome', 'disorder', 'illness', 'disease of anatomical entity',
           'disease by infectious agent', 'genetic disease', 'physical disorder', 'condition'}


def download(url):
    with urlopen(url, timeout=60) as response:
        content = response.read(20_000_001)
    if len(content) > 20_000_000:
        raise ValueError('Terminology download exceeds the expected size')
    return content


def terms_from_obo(text):
    aliases = defaultdict(set)
    concepts = 0
    for block in text.split('\n[Term]\n')[1:]:
        block = block.split('\n[', 1)[0]
        identifier = re.search(r'^id: (DOID:\d+)$', block, re.M)
        label = re.search(r'^name: (.+)$', block, re.M)
        if not identifier or not label or re.search(r'^is_obsolete: true$', block, re.M):
            continue
        concepts += 1
        names = [label[1]] + re.findall(r'^synonym: "([^"\\]+)" EXACT ', block, re.M)
        for name in names:
            name = re.sub(r'\s+', ' ', name.lower()).strip()
            # Do not turn short, ambiguous acronyms or generic ontology roots
            # into patient findings. Existing reviewed abbreviations stay in
            # the hand-maintained vocabulary.
            if name in GENERIC or not re.fullmatch(r"[a-z][a-z0-9 ()',/+-]{2,119}", name):
                continue
            if len(name.split()) == 1 and len(name) < 5:
                continue
            variants = {name}
            if "'s " in name:
                variants.update({name.replace("'s ", ' '), name.replace("'s ", 's ')})
            for variant in variants:
                aliases[variant].add(identifier[1])
    entries = [[term, next(iter(ids))] for term, ids in sorted(aliases.items()) if len(ids) == 1]
    ambiguous = [[term, sorted(ids)] for term, ids in sorted(aliases.items()) if len(ids) > 1]
    return entries, concepts, ambiguous


def main():
    raw = download(SOURCE)
    entries, concepts, ambiguous = terms_from_obo(raw.decode('utf-8'))
    if len(entries) < 1_000:
        raise ValueError('Unexpectedly small terminology snapshot')
    report = dict(source=SOURCE, revision=REVISION, license='CC0-1.0',
                  license_url=BASE+'/LICENSE', source_sha256=hashlib.sha256(raw).hexdigest(),
                  purpose='English literal terminology grounding. Not training, diagnosis or specialty validation.',
                  transformation='Active labels and EXACT synonyms; short/generic filtering; possessive variants; ambiguous aliases keep all IDs.',
                  active_concepts=concepts, ambiguous_entries=ambiguous, entries=entries)
    path = ROOT/'backend/app/data/disease_ontology_lexicon.json'
    path.write_text(json.dumps(report, ensure_ascii=True, separators=(',', ':'))+'\n', encoding='utf-8')
    (ROOT/'backend/app/data/DISEASE_ONTOLOGY_LICENSE.txt').write_bytes(download(BASE+'/LICENSE'))
    summary = {key: report[key] for key in ['source', 'revision', 'license', 'source_sha256', 'active_concepts']}
    summary.update(unambiguous_terms=len(entries), ambiguous_terms=len(ambiguous))
    (ROOT/'frontend/src/data/terminologyEvidence.json').write_text(json.dumps(summary, indent=2)+'\n', encoding='utf-8')
    print(f'Imported {len(entries)} terms from {concepts} active concepts; {len(ambiguous)} ambiguous aliases require review.')


if __name__ == '__main__':
    main()
