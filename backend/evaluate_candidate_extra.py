"""Evaluate the frozen candidate on the existing second synthetic corpus.

No fitting or parameter selection. This previously used classroom corpus is
additional development evidence, not an independent clinical evaluation.
"""
import argparse
import hashlib
import json
import re
from pathlib import Path
from app.nlp.context_candidate import ContextCandidate

ROOT = Path(__file__).resolve().parent


def evaluate():
    folder = ROOT/'experiments/context-candidate-v2'
    model_path = folder/'context_candidate.json'
    model = ContextCandidate(model_path)
    source = ROOT/'app/data/mock_transcripts.json'
    records = json.loads(source.read_bytes())
    normalize = lambda value: re.sub(r'\s+', ' ', value.lower()).strip()
    training_texts = {normalize(row['transcript']) for row in json.loads((ROOT/'app/data/training_transcripts.json').read_bytes())}
    seen, duplicates, excluded, samples = set(), [], [], []
    for record in records:
        text = record['transcript']
        normalized = normalize(text)
        if normalized in training_texts or normalized in seen:
            duplicates.append(record['id'])
            continue
        seen.add(normalized)
        candidates = []
        for key, label in [('expected_affirmed', 'affirmed'), ('expected_negated', 'negated'), ('expected_family', 'family')]:
            for term in record.get(key, []):
                matches = list(re.finditer(r'(?<!\w)' + re.escape(term).replace(r'\ ', r'\s+') + r'(?!\w)', text, re.I))
                if len(matches) != 1:
                    excluded.append({'id': record['id'], 'term': term, 'reason': 'missing literal span or ambiguous repeated occurrence'})
                    continue
                hit = matches[0]
                candidates.append({'id': record['id'], 'text': text, 'term': term, 'label': label, 'start': hit.start(), 'end': hit.end()})
        for sample in candidates:
            if any(other is not sample and max(other['start'], sample['start']) < min(other['end'], sample['end']) for other in candidates):
                excluded.append({'id': record['id'], 'term': sample['term'], 'reason': 'overlapping annotations require review'})
                continue
            sample['prediction'] = model.predict(text, sample['start'], sample['end'])['label']
            samples.append(sample)
    if not samples:
        raise ValueError('No unambiguous, nonduplicate evaluation labels')
    correct = sum(s['label'] == s['prediction'] for s in samples)
    per_class = {label: {'correct': sum(s['label'] == label and s['prediction'] == label for s in samples),
                         'total': sum(s['label'] == label for s in samples)} for label in ['affirmed', 'negated', 'family']}
    return {'model_sha256': hashlib.sha256(model_path.read_bytes().replace(b'\r\n', b'\n')).hexdigest(),
            'dataset_sha256': hashlib.sha256(source.read_bytes().replace(b'\r\n', b'\n')).hexdigest(),
            'provenance': 'Existing 20-note synthetic classroom corpus, previously used in rule experiments; not independent clinical validation.',
            'source_records': len(records), 'evaluated_records': len(seen), 'excluded_duplicate_records': duplicates,
            'correct': correct, 'total': len(samples), 'accuracy': correct/len(samples), 'per_class': per_class,
            'excluded_annotations': excluded, 'predictions': samples,
            'overall_medical_98_percent_validated': False,
            'limits': 'Known spans are supplied; no entity discovery is tested. The separate internal test remains 90%. Different difficulty and sparse family examples prevent an overall 98% claim. No retraining used this corpus.'}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=ROOT/'experiments/context-candidate-v2/extra_corpus_report.json')
    args = parser.parse_args()
    report = evaluate()
    args.output.write_text(json.dumps(report, indent=2)+'\n', encoding='utf-8', newline='\n')
    print(json.dumps({key: report[key] for key in ['evaluated_records', 'correct', 'total', 'accuracy', 'per_class', 'excluded_duplicate_records']}, indent=2))
