"""Reproduce the legacy broad synthetic negation metric, including its limits."""
import argparse
import hashlib
import json
from pathlib import Path
from app.nlp.negex_pipeline import extract_entities

ROOT = Path(__file__).resolve().parent


def evaluate():
    source = ROOT / 'app/data/training_transcripts.json'
    records = json.loads(source.read_bytes().replace(b'\r\n', b'\n'))
    tp = fp = fn = 0
    failures = []
    for record in records:
        expected = {value.lower() for value in record.get('expected_negated', [])}
        detected = {entity['term'] for entity in extract_entities(record['transcript']) if entity['negated']}
        missing = [term for term in expected if not any(term in item or item in term for item in detected)]
        extra = [item for item in detected if not any(term in item or item in term for term in expected)]
        tp += len(expected) - len(missing)
        fn += len(missing)
        fp += len(extra)
        if missing or extra:
            failures.append({'id': record['id'], 'missing': sorted(missing), 'extra': sorted(extra)})
    precision, recall = tp / max(1, tp + fp), tp / max(1, tp + fn)
    return {'dataset_sha256': hashlib.sha256(source.read_bytes().replace(b'\r\n', b'\n')).hexdigest(),
            'rules_sha256': hashlib.sha256((ROOT/'app/nlp/negex_pipeline.py').read_bytes().replace(b'\r\n', b'\n')).hexdigest(),
            'vocabulary_sha256': hashlib.sha256((ROOT/'app/nlp/vocabulary.py').read_bytes().replace(b'\r\n', b'\n')).hexdigest(),
            'ontology_sha256': hashlib.sha256((ROOT/'app/data/disease_ontology_lexicon.json').read_bytes().replace(b'\r\n', b'\n')).hexdigest(),
            'record_count': len(records), 'true_positive': tp, 'false_positive': fp, 'false_negative': fn,
            'precision': precision, 'recall': recall, 'f1': 2*precision*recall/max(1e-9, precision+recall),
            'legacy_95_recall_target_met': recall >= .95, 'failures': failures,
            'limits': 'Previously inspected synthetic development corpus. Legacy substring term matching can credit partial matches and annotations may be incomplete. Not clinical accuracy, full NER F1 or independent validation.'}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    report = evaluate()
    rendered = json.dumps(report, indent=2) + '\n'
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding='utf-8')
    print(rendered)
