"""Opt-in local rehearsal with real Qdrant, embeddings, RAG and Whisper.

Uses the test-only identity fixture and a temporary SQLite database. It does
not verify live WorkOS email delivery or clinical accuracy. Existing study
collections and inbox records are not modified.
"""
import os
import time
import uuid
import pytest

pytestmark = pytest.mark.skipif(os.environ.get('OMNIMATCH_LOCAL_STACK_TESTS') != '1',
                               reason='Requires running local Qdrant and cached real models')


@pytest.mark.asyncio
async def test_real_index_visit_and_cited_research(client, auth_headers, monkeypatch):
    from app.config import settings
    from app.trials import qdrant_service as module
    name = 'omnimatch_rehearsal_' + uuid.uuid4().hex
    monkeypatch.setattr(settings, 'demo_mode', True)
    monkeypatch.setattr(settings, 'advanced_nlp_enabled', True)
    monkeypatch.setattr(settings, 'qdrant_collection', name)
    monkeypatch.setattr(module, '_qdrant_client', None)
    service = module.QdrantService()
    monkeypatch.setattr(module, '_qdrant_service', service)
    try:
        assert await service.seed_demo_trials_if_empty() == 3
        result = await service.search(['asthma', 'albuterol'])
        assert any(row['nct_id'] == 'DEMO-ASTHMA-003' for row in result)
        base = dict(entity_type='DISEASE', confidence=.9, status='approved')
        entities = [dict(base, term='asthma'), dict(base, term='albuterol', entity_type='MEDICATION'),
                    dict(base, term='diabetes', negated=True), dict(base, term='COPD', context='family')]
        started = time.perf_counter()
        completed = await client.post('/api/v1/sessions/local-stack/complete', headers=auth_headers,
            json=dict(session_id='local-stack', patient_pseudo='DEMO-LOCAL-STACK', approved_entities=entities))
        assert completed.status_code == 202, completed.text
        inbox = (await client.get('/api/v1/inbox', headers=auth_headers)).json()
        elapsed = time.perf_counter() - started
        assert len(inbox['items']) == 1 and elapsed < 60
        item = inbox['items'][0]
        assert item['approved_entities'] == ['asthma', 'albuterol']
        assert any(match['nct_id'] == 'DEMO-ASTHMA-003' for match in item['matches'])
        history = (await client.get('/api/v1/timeline/DEMO-LOCAL-STACK', headers=auth_headers)).json()
        assert len(history['visits']) == 1 and history['total_entities'] == 2
        response = await client.post('/api/v1/understanding/answer', headers=auth_headers, json={
            'question': 'Which condition is excluded in the asthma study?', 'synthetic_only': True,
            'approved_entities': entities})
        assert response.status_code == 200, response.text
        assert any(source['nct_id'] == 'DEMO-ASTHMA-003' and 'COPD' in source['quote']
                   for source in response.json()['sources'])
        print(f'Real index to inbox: {elapsed:.3f}s; cited fictional study returned.')
    finally:
        # Delete only the randomly named collection created by this test.
        assert service.collection == name and name.startswith('omnimatch_rehearsal_')
        if await service.client.collection_exists(name):
            await service.client.delete_collection(name)
        await service.client.close()


@pytest.mark.asyncio
async def test_real_whisper_requires_consent_and_accepts_ram_audio(client, auth_headers, silent_wav_bytes):
    url = '/api/v1/audio/transcribe?session_id=local-speech'
    headers = {**auth_headers, 'Content-Type': 'audio/wav'}
    assert (await client.post(url, headers=headers, content=silent_wav_bytes)).status_code == 403
    consent = await client.post('/api/v1/consent', headers=auth_headers,
        json={'session_id': 'local-speech', 'action': 'CONSENT_GRANTED', 'patient_pseudonym': 'DEMO-SPEECH'})
    assert consent.status_code == 200, consent.text
    response = await client.post(url, headers=headers, content=silent_wav_bytes)
    assert response.status_code == 200, response.text
    body = response.json()
    assert body['session_id'] == 'local-speech' and isinstance(body['transcription'], str)
    assert isinstance(body['word_confidences'], list)
    print('Real Whisper decoded a one-second in-memory silent WAV. This is a pipeline check, not speech accuracy.')
