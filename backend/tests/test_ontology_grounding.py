"""Coverage, ambiguity and context remain separate from approval."""
from app.nlp.negex_pipeline import extract_entities
from app.models.schemas import ClinicalEntity
import pytest


def test_ontology_term_keeps_negation_and_requires_approval():
    entity = next(row for row in extract_entities('The patient denies cystinuria.') if row['term'] == 'cystinuria')
    assert entity['negated'] and entity['context'] == 'patient'
    assert ClinicalEntity(**entity).status == 'pending'


def test_ambiguous_term_displays_subtype_review_without_choosing_one():
    entity = next(row for row in extract_entities('Possible scleroderma needs review.') if row['term'] == 'scleroderma')
    assert entity['context'] == 'hypothetical'
    assert 'subtype' in ClinicalEntity(**entity).terminology_note
    assert entity['status'] == 'pending'


def test_family_and_negation_do_not_cross_explicit_patient_subject():
    rows = {row['term']: row for row in extract_entities('Mother reports endometriosis, the patient denies asthma.')}
    assert rows['endometriosis']['context'] == 'family'
    assert rows['asthma']['context'] == 'patient' and rows['asthma']['negated']
    rows = {row['term']: row for row in extract_entities('No asthma, the patient reports migraine.')}
    assert rows['asthma']['negated'] and not rows['migraine']['negated']


@pytest.mark.parametrize('text', [
    'If the patient develops eczema, arrange review.',
    'Should the patient develop eczema, arrange review.',
    'It is possible that the patient has eczema.',
])
def test_initial_conditional_patient_keeps_uncertainty(text):
    row = next(row for row in extract_entities(text) if row['term'] == 'eczema')
    assert row['context'] == 'hypothetical' and not row['negated']
