"""Generate website metrics from saved evidence, rather than hand-written scores."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def export():
    load = lambda path: json.loads((ROOT/path).read_text(encoding='utf-8'))
    before = load('docs/broad-negation-before.json')
    after = load('docs/broad-negation-after.json')
    training = load('backend/experiments/context-candidate-v2/training_report.json')
    extra = load('backend/experiments/context-candidate-v2/extra_corpus_report.json')
    model = ROOT/'backend/experiments/context-candidate-v2/context_candidate.json'
    assert hashlib.sha256(model.read_bytes().replace(b'\r\n', b'\n')).hexdigest() == training['model_sha256']
    assert extra['model_sha256'] == training['model_sha256']
    assert before['dataset_sha256'] == after['dataset_sha256'] == training['dataset_sha256']
    assert hashlib.sha256((ROOT/'backend/app/nlp/negex_pipeline.py').read_bytes().replace(b'\r\n', b'\n')).hexdigest() == after['rules_sha256']
    assert hashlib.sha256((ROOT/'backend/app/nlp/vocabulary.py').read_bytes().replace(b'\r\n', b'\n')).hexdigest() == after['vocabulary_sha256']
    assert hashlib.sha256((ROOT/'backend/app/data/disease_ontology_lexicon.json').read_bytes().replace(b'\r\n', b'\n')).hexdigest() == after['ontology_sha256']
    report = {'broad_records': after['record_count'],
              'broad_before': {key: before[key] for key in ['precision', 'recall', 'f1']},
              'broad_after': {key: after[key] for key in ['precision', 'recall', 'f1']},
              'candidate_accuracy': training['test']['accuracy'], 'candidate_correct': training['test']['correct'],
              'candidate_total': training['test']['total'],
              'candidate_macro_f1': training['test']['classification_report']['macro avg']['f1-score'],
              'candidate_family_test_count': training['split_class_counts']['test']['family'],
              'candidate_active': False, 'medical_accuracy_98_validated': False,
              'extra_accuracy': extra['accuracy'], 'extra_correct': extra['correct'],
              'extra_total': extra['total'], 'extra_records': extra['evaluated_records'],
              'split_annotation_counts': training['split_annotation_counts'],
              'split_record_counts': {key: len(values) for key, values in training['split_record_ids'].items()},
              'excluded_annotations': len(training['excluded_annotations'])}
    target = ROOT/'frontend/src/data/modelEvidence.json'
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(report, indent=2)+'\n', encoding='utf-8')
    print('Updated website evidence from verified report and model hashes.')


if __name__ == '__main__':
    export()
