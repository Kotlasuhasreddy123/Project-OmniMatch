"""Opt-in real CPU model/API checks; index transport is explicitly stubbed.

Run with OMNIMATCH_REAL_MODEL_TESTS=1 after caching the pinned weights.
This is not an external clinical evaluation or a live Qdrant integration test.
"""
import os
import json
from pathlib import Path
from unittest.mock import AsyncMock, Mock
import pytest

pytestmark = pytest.mark.skipif(os.environ.get('OMNIMATCH_REAL_MODEL_TESTS') != '1', reason='Opt-in cached real-model integration check')


@pytest.mark.asyncio
async def test_real_models_through_authenticated_api(client, auth_headers, monkeypatch):
    from app.config import settings
    from app.understanding import router as module
    monkeypatch.setattr(settings, 'advanced_nlp_enabled', True)
    runtime = module.get_runtime()
    real_ner = Mock(wraps=runtime.ner)
    monkeypatch.setattr(runtime, 'ner', real_ner)
    response = await client.post('/api/v1/understanding/analyze', headers=auth_headers,
                                 json={'text': 'The fictional patient has bronchiectasis and uses albuterol. No diabetes.', 'synthetic_only': True})
    assert response.status_code == 200, response.text
    entities = response.json()['entities']
    assert all(entity['status'] == 'pending' for entity in entities)
    # The ontology may now recognize this term before neural proposal merging.
    # Still verify that actual transformer inference ran, rather than replacing
    # this integration check with a dictionary-only test.
    assert any(entity['term'] == 'bronchiectasis' and entity['source'] in ['rules', 'biomedical_transformer'] for entity in entities)
    real_ner.assert_called_once_with('The fictional patient has bronchiectasis and uses albuterol. No diabetes.')
    trials = json.loads((Path(__file__).resolve().parents[1]/'app/data/demo_trials.json').read_bytes())
    search = AsyncMock(return_value=trials)
    monkeypatch.setattr(module, 'get_qdrant_service', lambda: type('Index', (), {'search': search})())
    response = await client.post('/api/v1/understanding/answer', headers=auth_headers, json={
        'question': 'Which condition is excluded in the asthma study?', 'synthetic_only': True,
        'approved_entities': [dict(term='asthma', entity_type='DISEASE', status='approved', context='patient', negated=False, confidence=.8)]})
    assert response.status_code == 200, response.text
    assert any(source['nct_id'] == 'DEMO-ASTHMA-003' and 'COPD' in source['quote'] for source in response.json()['sources'])
    search.assert_awaited_once_with(['asthma'], top_k=20)
