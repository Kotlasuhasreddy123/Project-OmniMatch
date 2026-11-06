"""Safety regressions beyond the original known-vocabulary examples."""
import pytest
from app.nlp.negex_pipeline import extract_entities


@pytest.mark.parametrize('text', [
    'Possible pneumonia needs investigation.',
    'Pneumonia cannot be excluded.',
    'We cannot rule out pneumonia.',
    'Pneumonia is not yet ruled out.',
    'There is concern for pneumonia.',
])
def test_uncertainty_never_becomes_confirmed_or_denied(text):
    findings = [e for e in extract_entities(text) if e['term'] == 'pneumonia']
    assert findings
    assert all(e['context'] == 'hypothetical' and not e['negated'] and e['status'] == 'pending' for e in findings)


def test_negation_covers_coordinated_list():
    entities = extract_entities('Patient denies chest pain, shortness of breath, palpitations, and dizziness.')
    for term in ['chest pain', 'shortness of breath', 'palpitations', 'dizziness']:
        assert any(e['term'] == term and e['negated'] for e in entities)


@pytest.mark.parametrize('text,term', [
    ('Patient denies asthma and uses albuterol.', 'albuterol'),
    ('Patient denies pneumonia and has diabetes.', 'diabetes'),
    ('Asthma was ruled out; the patient has diabetes.', 'diabetes'),
])
def test_positive_statement_ends_negation_scope(text, term):
    assert any(e['term'] == term and not e['negated'] and e['context'] == 'patient' for e in extract_entities(text))


@pytest.mark.parametrize('term', ['pneumonia', 'atrial fibrillation', 'pulmonary fibrosis', 'carvedilol', 'tacrolimus'])
def test_extended_vocabulary_still_requires_human_review(term):
    assert any(e['term'] == term and e['status'] == 'pending' for e in extract_entities('The patient has ' + term + '.'))
