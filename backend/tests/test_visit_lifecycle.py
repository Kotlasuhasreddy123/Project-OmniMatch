"""Visit linkage and archive retention against a real temporary SQLite database."""
import json
import sqlite3
from unittest.mock import AsyncMock
import pytest
from app.trials import qdrant_service


def test_research_approval_preserves_neural_source():
    from app.understanding.router import EvidenceRequest
    request = EvidenceRequest(question='Which study?', synthetic_only=True, approved_entities=[
        dict(term='asthma', entity_type='DISEASE', confidence=.9, status='approved', source='biomedical_transformer')])
    assert request.approved_entities[0].source == 'biomedical_transformer'


@pytest.mark.asyncio
async def test_repeat_visit_archive_restore_and_retry(client, auth_headers, tmp_db_path, monkeypatch):
    search = AsyncMock(return_value=[])
    monkeypatch.setattr(qdrant_service, 'get_qdrant_service', lambda: type('Index', (), {'search': search})())
    entity = dict(term='asthma', entity_type='DISEASE', confidence=.9, status='approved')
    for session in ['visit-one', 'visit-two', 'visit-two']:
        result = await client.post(f'/api/v1/sessions/{session}/complete', headers=auth_headers,
            json=dict(session_id=session, patient_pseudo='DEMO-TEST', approved_entities=[entity]))
        assert result.status_code == 202
    inbox = (await client.get('/api/v1/inbox', headers=auth_headers)).json()
    assert inbox['total'] == 2
    item = inbox['items'][0]
    base = '/api/v1/inbox/' + item['id']
    assert (await client.post(base+'/archive', headers=auth_headers)).status_code == 409
    assert (await client.delete(base, headers=auth_headers)).status_code == 204
    assert (await client.post(base+'/archive', headers=auth_headers)).status_code == 204
    assert (await client.get('/api/v1/inbox', headers=auth_headers)).json()['total'] == 1
    assert (await client.get('/api/v1/inbox?include_archived=true', headers=auth_headers)).json()['total'] == 2
    history = (await client.get('/api/v1/timeline/DEMO-TEST', headers=auth_headers)).json()
    assert len(history['visits']) == 2
    assert history['entries'][0]['mention_count'] == 2
    assert any(visit['archived'] for visit in history['visits'])
    with sqlite3.connect(tmp_db_path) as db:
        assert db.execute('SELECT count(*) FROM inbox_items').fetchone()[0] == 2
    assert (await client.post(base+'/restore', headers=auth_headers)).status_code == 204
    assert (await client.get('/api/v1/inbox', headers=auth_headers)).json()['total'] == 2


@pytest.mark.asyncio
async def test_completion_rejects_id_mismatch_and_excludes_nonpatient(client, auth_headers, monkeypatch):
    search = AsyncMock(return_value=[])
    monkeypatch.setattr(qdrant_service, 'get_qdrant_service', lambda: type('Index', (), {'search': search})())
    body = dict(session_id='different', approved_entities=[])
    assert (await client.post('/api/v1/sessions/visit/complete', headers=auth_headers, json=body)).status_code == 400
    body = dict(session_id='visit', approved_entities=[dict(term='asthma', entity_type='DISEASE', confidence=.9, status='approved', context='family')])
    assert (await client.post('/api/v1/sessions/visit/complete', headers=auth_headers, json=body)).status_code == 202
    search.assert_not_awaited()
    item = (await client.get('/api/v1/inbox', headers=auth_headers)).json()['items'][0]
    assert item['approved_entities'] == [] and item['matches'] == []


@pytest.mark.asyncio
async def test_archive_needs_authentication(client):
    assert (await client.post('/api/v1/inbox/anything/archive')).status_code == 401


@pytest.mark.asyncio
async def test_existing_inbox_migrates_without_losing_records(tmp_path, monkeypatch):
    from app.models import database
    path = str(tmp_path/'old.db')
    with sqlite3.connect(path) as db:
        db.execute(database.CREATE_INBOX_TABLE)
        db.execute("INSERT INTO inbox_items VALUES ('old', 'old-visit', '2026-10-20T12:00:00+00:00', 'reviewed', '[]', '[\"asthma\"]')")
    monkeypatch.setattr(database, 'DB_PATH', path)
    await database.init_db()
    await database.init_db()  # Repeated startup must be safe too.
    with sqlite3.connect(path) as db:
        row = db.execute('SELECT id, approved_entities, patient_pseudo, archived_at FROM inbox_items').fetchone()
    assert row == ('old', '["asthma"]', None, None)
