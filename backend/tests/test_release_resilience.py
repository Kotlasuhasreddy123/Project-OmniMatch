"""Additional failure, retry and recovery checks using disposable databases."""
import asyncio
import sqlite3
from unittest.mock import AsyncMock
import pytest
from app.trials import qdrant_service


def payload(session='resilience-visit'):
    return dict(session_id=session, patient_pseudo='DEMO-RESILIENCE', approved_entities=[
        dict(term='asthma', entity_type='DISEASE', confidence=.9, status='approved')])


@pytest.mark.asyncio
async def test_invalid_completion_does_not_claim_session(client, auth_headers, tmp_db_path):
    response=await client.post('/api/v1/sessions/wrong-address/complete',headers=auth_headers,json=payload())
    assert response.status_code==400
    with sqlite3.connect(tmp_db_path) as db:
        assert db.execute("SELECT count(*) FROM session_owners WHERE session_id='wrong-address'").fetchone()[0]==0


@pytest.mark.asyncio
async def test_concurrent_completion_retries_store_one_visit(client, auth_headers, monkeypatch):
    search=AsyncMock(return_value=[])
    monkeypatch.setattr(qdrant_service,'get_qdrant_service',lambda:type('Index',(),{'search':search})())
    responses=await asyncio.gather(*[
        client.post('/api/v1/sessions/resilience-visit/complete',headers=auth_headers,json=payload())
        for _ in range(3)])
    assert all(response.status_code==202 for response in responses)
    inbox=(await client.get('/api/v1/inbox',headers=auth_headers)).json()
    history=(await client.get('/api/v1/timeline/DEMO-RESILIENCE',headers=auth_headers)).json()
    assert inbox['total']==len(history['visits'])==1
    assert history['entries'][0]['mention_count']==1


@pytest.mark.asyncio
async def test_legacy_completion_duplicates_do_not_inflate_history(client, auth_headers, monkeypatch, tmp_db_path):
    monkeypatch.setattr(qdrant_service,'get_qdrant_service',lambda:type('Index',(),{'search':AsyncMock(return_value=[])})())
    await client.post('/api/v1/sessions/resilience-visit/complete',headers=auth_headers,json=payload())
    with sqlite3.connect(tmp_db_path) as db:
        columns=[row[1] for row in db.execute('PRAGMA table_info(inbox_items)')]
        original=list(db.execute('SELECT * FROM inbox_items').fetchone())
        original[columns.index('id')]='old-completion-retry'
        db.execute('INSERT INTO inbox_items VALUES ('+','.join('?' for _ in original)+')',original)
    history=(await client.get('/api/v1/timeline/DEMO-RESILIENCE',headers=auth_headers)).json()
    assert len(history['visits'])==1
    assert history['entries'][0]['mention_count']==1


@pytest.mark.asyncio
async def test_transient_search_failure_is_private_and_retry_recovers(client, auth_headers, monkeypatch, caplog):
    search=AsyncMock(side_effect=[RuntimeError('PRIVATE_TEST_CONTENT_DO_NOT_LOG'),[]])
    monkeypatch.setattr(qdrant_service,'get_qdrant_service',lambda:type('Index',(),{'search':search})())
    assert (await client.post('/api/v1/sessions/resilience-visit/complete',headers=auth_headers,json=payload())).status_code==202
    assert (await client.get('/api/v1/inbox',headers=auth_headers)).json()['total']==0
    assert 'PRIVATE_TEST_CONTENT_DO_NOT_LOG' not in caplog.text
    assert (await client.post('/api/v1/sessions/resilience-visit/complete',headers=auth_headers,json=payload())).status_code==202
    assert (await client.get('/api/v1/inbox',headers=auth_headers)).json()['total']==1


@pytest.mark.asyncio
async def test_disposable_backup_restore_preserves_archive_and_ownership(client, auth_headers, admin_headers, monkeypatch, tmp_db_path, tmp_path):
    from app.models import database
    from app.config import settings
    monkeypatch.setattr(qdrant_service,'get_qdrant_service',lambda:type('Index',(),{'search':AsyncMock(return_value=[])})())
    await client.post('/api/v1/sessions/resilience-visit/complete',headers=auth_headers,json=payload())
    item=(await client.get('/api/v1/inbox',headers=auth_headers)).json()['items'][0]
    await client.delete('/api/v1/inbox/'+item['id'],headers=auth_headers)
    await client.post('/api/v1/inbox/'+item['id']+'/archive',headers=auth_headers)
    backup=tmp_path/'fixture-backup.db';restored=tmp_path/'fixture-restored.db'
    with sqlite3.connect(tmp_db_path) as source, sqlite3.connect(backup) as copy:
        source.backup(copy)
    with sqlite3.connect(backup) as source,sqlite3.connect(restored) as target:
        source.backup(target)
        assert target.execute('PRAGMA integrity_check').fetchone()[0]=='ok'
    monkeypatch.setattr(database,'DB_PATH',str(restored))
    monkeypatch.setattr(settings,'sqlite_db_path',str(restored))
    assert (await client.get('/api/v1/inbox',headers=auth_headers)).json()['total']==0
    saved=(await client.get('/api/v1/inbox?include_archived=true',headers=auth_headers)).json()
    assert saved['total']==1 and saved['items'][0]['archived_at'] is not None
    assert (await client.get('/api/v1/inbox?include_archived=true',headers=admin_headers)).json()['total']==0
    assert (await client.get('/api/v1/inbox/'+item['id'],headers=admin_headers)).status_code==404
    assert (await client.post('/api/v1/inbox/'+item['id']+'/restore',headers=auth_headers)).status_code==204
    assert (await client.get('/api/v1/inbox',headers=auth_headers)).json()['total']==1
