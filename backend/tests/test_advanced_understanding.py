"""Deterministic integration contracts; real checkpoint evaluation is separate."""
import hashlib
import json
from pathlib import Path
from unittest.mock import AsyncMock
import pytest
from app.understanding.analysis_service import analyze, span_context
from app.understanding.rag_service import answer, passages_from_trials
from app.understanding.runtime import ModelUnavailable

TRIALS = json.loads((Path(__file__).resolve().parents[1]/'app/data/demo_trials.json').read_bytes())


class FakeRuntime:
    """Dependency stub, never reported as a learned model accuracy result."""
    def ner(self, text):
        term = 'dysautonomia'
        if term not in text:
            return []
        start = text.index(term)
        return [dict(start=start, end=start+len(term), category='DISEASE_DISORDER', score=.9)]

    def sentiment(self, text):
        return {'scores': {'positive': .1, 'neutral': .2, 'negative': .7}, 'token_truncated': False}

    def assertions(self, text, term):
        return dict(patient=.1, negated=.8, family=.05, hypothetical=.05)

    def embeddings(self, texts):
        return [[1., 0.] for _ in texts]

    def rerank(self, question, passages):
        return [5. if 'albuterol' in passage.lower() else -2. for passage in passages]

    def generate(self, prompt):
        return 'Invented claim: this patient is definitely eligible and cured.'


def test_neural_terms_stay_pending_and_sentiment_does_not_change_context():
    result = analyze('The fictional patient has dysautonomia. No asthma.', FakeRuntime())
    term = next(entity for entity in result['entities'] if entity['term'] == 'dysautonomia')
    assert term['source'] == 'biomedical_transformer'
    assert term['status'] == 'pending' and term['context'] == 'patient' and not term['negated']
    assert next(item for item in result['assertion_reviews'] if item['term'] == 'dysautonomia')['disagreement']
    assert all(entity['status'] == 'pending' for entity in result['entities'])


@pytest.mark.parametrize('text,context,negative', [
    ('The patient denies dysautonomia.', 'patient', True),
    ('Mother had dysautonomia.', 'family', False),
    ('Possible dysautonomia needs review.', 'hypothetical', False),
    ('We cannot rule out dysautonomia.', 'hypothetical', False),
])
def test_novel_terms_receive_context_guards(text, context, negative):
    start = text.index('dysautonomia')
    assert span_context(text, start, start+len('dysautonomia')) == (context, negative)


def test_long_note_reports_partial_tone_and_nli_coverage():
    text = ' '.join(f'The patient has {term}.' for term in ['diabetes', 'hypertension', 'asthma', 'copd', 'stroke', 'depression', 'anxiety', 'epilepsy', 'obesity', 'anemia', 'lupus', 'psoriasis', 'eczema', 'pneumonia']) + ' More fictional history.'*100
    result = analyze(text, FakeRuntime())
    assert result['sentiment']['partial'] is True
    assert result['assertion_reviewed_count'] == 12
    assert result['assertion_unreviewed_count'] > 0


def test_source_offsets_and_hashes_match_original_fields():
    passages, _ = passages_from_trials(TRIALS)
    for passage in passages:
        trial = next(trial for trial in TRIALS if trial['nct_id'] == passage['nct_id'])
        assert trial[passage['field']][passage['start']:passage['end']] == passage['quote']
        assert hashlib.sha256(passage['quote'].encode()).hexdigest() == passage['quote_sha256']


def test_unsupported_generation_is_replaced_with_cited_excerpts():
    response = answer('What treatment is mentioned in the asthma study?', ['asthma'], TRIALS, FakeRuntime())
    assert response['generation_mode'] == 'extractive_grounding_fallback'
    assert 'definitely eligible' not in response['answer']
    assert response['sources'] and all(item['quote'] in response['answer'] for item in response['sources'])


def test_exact_whole_source_quote_can_pass_generation_gate():
    runtime = FakeRuntime()
    runtime.generate = lambda prompt: '* Albuterol treatment'
    # Use a dedicated fictional record so the expected whole passage is explicit.
    trials = [{'nct_id': 'DEMO-X-001', 'title': 'Fictional study', 'brief_summary': '', 'eligibility_criteria': 'Inclusion Criteria:\n* Albuterol treatment'}]
    response = answer('What treatment is listed?', ['asthma'], trials, runtime)
    assert response['generation_mode'] == 'generated_quote_verified'
    assert response['sources'][0]['quote'] == '* Albuterol treatment'


def test_generation_gate_never_drops_negation_or_numeric_signs():
    from app.understanding.rag_service import normalized
    assert normalized('* No kidney disease') != normalized('Kidney disease')
    assert normalized('-3 mg') != normalized('3 mg')
    assert normalized('* Albuterol treatment') == normalized('Albuterol treatment')


def test_low_relevance_abstains_before_generation():
    runtime = FakeRuntime()
    runtime.rerank = lambda question, passages: [-1.]*len(passages)
    runtime.generate = lambda prompt: pytest.fail('Generation must not run without evidence')
    response = answer('What does the record say?', ['asthma'], TRIALS, runtime)
    assert response['abstained'] and not response['generator_used']


@pytest.mark.parametrize('question', ['Predict my next disease.', 'Will I develop cancer?', 'Prescribe a treatment.'])
def test_clinical_decision_requests_are_out_of_scope(question):
    response = answer(question, ['asthma'], TRIALS, object())
    assert response['abstained'] and response['generation_mode'] == 'out_of_scope'


@pytest.mark.asyncio
async def test_advanced_api_requires_sign_in(client):
    response = await client.post('/api/v1/understanding/analyze', json={'text': 'Fictional note', 'synthetic_only': True})
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_disabled_feature_is_explicit(client, auth_headers, monkeypatch):
    from app.config import settings
    monkeypatch.setattr(settings, 'advanced_nlp_enabled', False)
    response = await client.post('/api/v1/understanding/analyze', headers=auth_headers, json={'text': 'Fictional note', 'synthetic_only': True})
    assert response.status_code == 503


@pytest.mark.asyncio
async def test_answer_queries_only_explicitly_approved_patient_terms(client, auth_headers, monkeypatch):
    from app.config import settings
    from app.understanding import router as module
    monkeypatch.setattr(settings, 'advanced_nlp_enabled', True)
    search = AsyncMock(return_value=TRIALS)
    monkeypatch.setattr(module, 'get_qdrant_service', lambda: type('Index', (), {'search': search})())
    monkeypatch.setattr(module, 'get_runtime', lambda: FakeRuntime())
    base = dict(entity_type='DISEASE', confidence=.8, negated=False, context='patient', status='approved')
    entities = [dict(base, term='asthma'), dict(base, term='diabetes', status='pending'), dict(base, term='cancer', context='family'), dict(base, term='stroke', negated=True)]
    response = await client.post('/api/v1/understanding/answer', headers=auth_headers,
                                 json={'question': 'What treatment is listed?', 'approved_entities': entities, 'synthetic_only': True})
    assert response.status_code == 200
    search.assert_awaited_once_with(['asthma'], top_k=20)


@pytest.mark.asyncio
async def test_empty_approval_does_not_query_index(client, auth_headers, monkeypatch):
    from app.config import settings
    monkeypatch.setattr(settings, 'advanced_nlp_enabled', True)
    response = await client.post('/api/v1/understanding/answer', headers=auth_headers, json={
        'question': 'Which studies?', 'synthetic_only': True, 'approved_entities': [
            dict(term='asthma', entity_type='DISEASE', confidence=.8, context='patient', negated=False, status='pending')]})
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_missing_models_never_return_mock_predictions(client, auth_headers, monkeypatch):
    from app.config import settings
    from app.understanding import router as module
    monkeypatch.setattr(settings, 'advanced_nlp_enabled', True)
    def unavailable(*args):
        raise ModelUnavailable('Install the local models')
    monkeypatch.setattr(module, 'analyze', unavailable)
    response = await client.post('/api/v1/understanding/analyze', headers=auth_headers,
                                 json={'text': 'Patient has asthma.', 'synthetic_only': True})
    assert response.status_code == 503
    assert 'entities' not in response.json()
