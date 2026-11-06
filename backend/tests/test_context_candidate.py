"""Test data separation, label alignment and portable candidate inference."""
import json
from pathlib import Path
import pytest
from app.nlp.context_candidate import ContextCandidate, context_features
from train_context_candidate import prepare

ROOT = Path(__file__).resolve().parents[1]


def test_records_and_classes_are_separated():
    samples, excluded, groups = prepare(json.loads((ROOT/'app/data/training_transcripts.json').read_bytes()))
    assert not set(groups['train']) & set(groups['test'])
    assert not set(groups['validation']) & set(groups['test'])
    assert not set(groups['train']) & set(groups['validation'])
    for split in groups:
        assert {s['label'] for s in samples if s['split'] == split} == {'affirmed', 'negated', 'family'}
    assert excluded  # Ambiguous/nonliteral source labels are surfaced, not guessed.


def test_duplicate_records_fail_validation():
    records = json.loads((ROOT/'app/data/training_transcripts.json').read_bytes())
    records[1]['transcript'] = records[0]['transcript']
    with pytest.raises(ValueError, match='Duplicate transcripts'):
        prepare(records)


def test_target_word_is_not_a_feature():
    text = 'Patient denies pneumonia.'
    start = text.index('pneumonia')
    features = context_features(text, start, start + len('pneumonia'))
    assert 'pneumonia' not in features
    assert 'l_denies' in features


def test_invalid_span_rejected():
    with pytest.raises(ValueError):
        context_features('note', 0, 99)


def test_exported_model_reproduces_all_saved_test_predictions():
    folder = ROOT/'experiments/context-candidate-v2'
    report = json.loads((folder/'training_report.json').read_bytes())
    model = ContextCandidate(folder/'context_candidate.json')
    for example in report['test_predictions']:
        result = model.predict(example['text'], example['start'], example['end'])
        assert result['label'] == example['prediction']
        assert result['experimental'] is True
    assert report['eligible_for_live_promotion'] is False
    assert report['overall_medical_98_percent_validated'] is False
