"""Train an experimental classifier on aligned, synthetic term annotations.

No test-driven retraining, clinical recordings, external downloads or live model
replacement. The legacy synthetic corpus is development data, not external validation.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import platform
import re
from pathlib import Path
from app.nlp.context_candidate import context_features, ContextCandidate

ROOT = Path(__file__).resolve().parent
LABELS = {'expected_affirmed': 'affirmed', 'expected_negated': 'negated', 'expected_family': 'family'}


def prepare(records):
    ids = [record['id'] for record in records]
    if len(ids) != len(set(ids)) or len(records) < 20:
        raise ValueError('Need at least 20 uniquely identified synthetic records')
    normalized = [re.sub(r'\s+', ' ', record['transcript'].lower()).strip() for record in records]
    if len(normalized) != len(set(normalized)):
        raise ValueError('Duplicate transcripts would contaminate the record split')
    ordered = sorted(ids, key=lambda identifier: hashlib.sha256(('42:' + identifier).encode()).hexdigest())
    a, b = int(len(ids) * .70), int(len(ids) * .85)
    groups = {identifier: split for split, members in [('train', ordered[:a]), ('validation', ordered[a:b]), ('test', ordered[b:])] for identifier in members}
    samples, excluded = [], []
    for record in records:
        candidates = []
        for key, label in LABELS.items():
            for term in record.get(key, []):
                pattern = r'(?<!\w)' + re.escape(term).replace(r'\ ', r'\s+') + r'(?!\w)'
                occurrences = list(re.finditer(pattern, record['transcript'], re.I))
                if len(occurrences) != 1:
                    excluded.append({'record': record['id'], 'term': term, 'reason': 'missing literal span or ambiguous repeated occurrence', 'occurrences': len(occurrences)})
                    continue
                match = occurrences[0]
                candidates.append(dict(record_id=record['id'], text=record['transcript'], term=term,
                                       start=match.start(), end=match.end(), label=label, split=groups[record['id']]))
        for sample in candidates:
            conflicts = [other for other in candidates if other is not sample and
                         max(sample['start'], other['start']) < min(sample['end'], other['end'])]
            if conflicts:
                excluded.append({'record': record['id'], 'term': sample['term'], 'reason': 'overlapping annotation spans require manual review'})
            else:
                samples.append(sample)
    # Stratify the rare family-history RECORDS without splitting their mentions.
    # The original hash-only experiment omitted family from validation/test.
    family_ids = {sample['record_id'] for sample in samples if sample['label'] == 'family'}
    for members in [[identifier for identifier in ordered if identifier in family_ids],
                    [identifier for identifier in ordered if identifier not in family_ids]]:
        if len(members) < 3:
            raise ValueError('Need at least three family records and three other records for group-separated evaluation')
        a, b = int(len(members)*.70), max(int(len(members)*.70)+1, int(len(members)*.85))
        for split, identifiers in [('train', members[:a]), ('validation', members[a:b]), ('test', members[b:])]:
            for identifier in identifiers:
                groups[identifier] = split
    for sample in samples:
        sample['split'] = groups[sample['record_id']]
    return samples, excluded, {split: [identifier for identifier in ordered if groups[identifier] == split] for split in ['train', 'validation', 'test']}


def metrics(truth, predicted):
    from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
    labels = ['affirmed', 'family', 'negated']
    n, correct = len(truth), sum(a == b for a, b in zip(truth, predicted))
    p, z = correct / n, 1.96
    center = (p + z*z/(2*n)) / (1 + z*z/n)
    radius = z*((p*(1-p)/n + z*z/(4*n*n))**.5) / (1+z*z/n)
    return {'correct': correct, 'total': n, 'accuracy': accuracy_score(truth, predicted),
            'wilson_95_interval': [center-radius, center+radius],
            'interval_limit': 'Term observations are clustered within records; this simple interval may understate uncertainty.',
            'classification_report': classification_report(truth, predicted, labels=labels, output_dict=True, zero_division=0),
            'confusion_matrix_labels': labels, 'confusion_matrix': confusion_matrix(truth, predicted, labels=labels).tolist()}


def train(dataset: Path, output: Path):
    if (output / 'context_candidate.json').exists():
        raise ValueError('Choose a new output directory; existing candidate weights are preserved')
    import sklearn
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.linear_model import LogisticRegression
    from sklearn.pipeline import make_pipeline
    raw = dataset.read_bytes().replace(b'\r\n', b'\n')
    samples, excluded, split_ids = prepare(json.loads(raw))
    partitions = {split: [sample for sample in samples if sample['split'] == split] for split in split_ids}
    if any(not values for values in partitions.values()):
        raise ValueError('Every partition needs aligned labels')
    train_samples = partitions['train']
    x = lambda values: [context_features(item['text'], item['start'], item['end']) for item in values]
    y = lambda values: [item['label'] for item in values]
    if set(y(train_samples)) != set(LABELS.values()):
        raise ValueError('Training needs all three assertion classes')
    candidates = []
    for c in [.1, 1., 10.]:
        model = make_pipeline(TfidfVectorizer(ngram_range=(1, 2), lowercase=False),
                              LogisticRegression(C=c, class_weight='balanced', max_iter=1000, random_state=42))
        model.fit(x(train_samples), y(train_samples))
        result = metrics(y(partitions['validation']), model.predict(x(partitions['validation'])))
        candidates.append((result['classification_report']['macro avg']['f1-score'], c, model, result))
    # Choose using validation only; test predictions are computed exactly once below.
    _, selected_c, selected, _ = max(candidates, key=lambda item: (item[0], -item[1]))
    vectorizer, classifier = selected.steps[0][1], selected.steps[1][1]
    artifact = {'format': 'omnimatch-context-tfidf-logistic-v1', 'classes': classifier.classes_.tolist(),
                'vocabulary': {key: int(value) for key, value in vectorizer.vocabulary_.items()},
                'idf': vectorizer.idf_.tolist(), 'coefficients': classifier.coef_.tolist(),
                'intercepts': classifier.intercept_.tolist(), 'selected_C': selected_c,
                'dataset_sha256': hashlib.sha256(raw).hexdigest(), 'seed': 42, 'deployment': 'experimental only; not connected to API'}
    output.mkdir(parents=True, exist_ok=True)
    model_path = output / 'context_candidate.json'
    model_path.write_text(json.dumps(artifact, sort_keys=True, indent=2) + '\n', encoding='utf-8')
    portable = ContextCandidate(model_path)
    test = partitions['test']
    predicted = selected.predict(x(test)).tolist()
    portable_predictions = [portable.predict(item['text'], item['start'], item['end'])['label'] for item in test]
    if predicted != portable_predictions:
        raise AssertionError('Exported model does not match training-library predictions')
    result = metrics(y(test), predicted)
    majority = max(set(y(train_samples)), key=y(train_samples).count)
    report = {'model': 'TF-IDF + balanced logistic regression assertion candidate', 'active_in_application': False,
              'provenance': 'Repository-authored synthetic classroom transcripts. Previously used for rule development; not independent clinical validation.',
              'task': 'Classify affirmed/family/negated context GIVEN a known, unambiguous entity span. Does not detect entities.',
              'dataset_sha256': artifact['dataset_sha256'], 'model_sha256': hashlib.sha256(model_path.read_bytes().replace(b'\r\n', b'\n')).hexdigest(),
              'python': platform.python_version(), 'scikit_learn': sklearn.__version__, 'split_record_ids': split_ids,
              'split_method': 'Record-separated fixed SHA-256 seed order, stratified by presence of aligned family labels. Internal synthetic development corpus only.',
              'training_script_sha256': hashlib.sha256(Path(__file__).read_bytes().replace(b'\r\n', b'\n')).hexdigest(),
              'feature_code_sha256': hashlib.sha256((ROOT/'app/nlp/context_candidate.py').read_bytes().replace(b'\r\n', b'\n')).hexdigest(),
              'split_annotation_counts': {key: len(values) for key, values in partitions.items()},
              'split_class_counts': {key: {label: y(values).count(label) for label in LABELS.values()} for key, values in partitions.items()},
              'parameters': {'seed': 42, 'context_words_each_side': 12, 'ngrams': [1, 2], 'class_weight': 'balanced',
                             'C_candidates': [.1, 1., 10.], 'selected_C': selected_c, 'max_iter': 1000},
              'validation_candidates': [{'C': c, 'metrics': m} for _, c, _, m in candidates],
              'test': result, 'majority_baseline_test': metrics(y(test), [majority]*len(test)),
              'requested_98_percent_met_on_this_internal_test': result['accuracy'] >= .98,
              'overall_medical_98_percent_validated': False,
              'eligible_for_live_promotion': False,
              'excluded_annotations': excluded,
              'test_predictions': [{**item, 'prediction': label} for item, label in zip(test, predicted)],
              'limits': ['English synthetic development corpus only; no patient data.',
                         'The source has ambiguous or nonliteral annotations, listed as excluded.',
                         'Known entity spans bypass entity discovery. Results are not end-to-end extraction accuracy.',
                         'No uncertainty, hypothetical, temporal or multilingual validation for this classifier.',
                         'No Whisper or MiniLM weight changes. No disease forecasting or prescribing.']}
    (output / 'training_report.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({key: report[key] for key in ['split_annotation_counts', 'parameters', 'test', 'requested_98_percent_met_on_this_internal_test', 'overall_medical_98_percent_validated']}, indent=2))
    return report


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--dataset', type=Path, default=ROOT / 'app/data/training_transcripts.json')
    parser.add_argument('--output-dir', type=Path, default=ROOT / 'experiments/context-candidate-v2')
    args = parser.parse_args()
    train(args.dataset, args.output_dir)
