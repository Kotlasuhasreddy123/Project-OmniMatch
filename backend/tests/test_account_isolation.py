"""Two real signed identities must never share visits, even with ADMIN access."""
import sqlite3
from unittest.mock import AsyncMock

import pytest
from app.trials import qdrant_service


@pytest.mark.asyncio
async def test_accounts_cannot_read_modify_or_reuse_each_others_visits(
    client, auth_headers, admin_headers, monkeypatch, tmp_db_path,
):
    monkeypatch.setattr(qdrant_service, "get_qdrant_service", lambda: type("Index", (), {"search": AsyncMock(return_value=[])})())
    for headers, session, term in [(auth_headers, "staff-visit", "asthma"), (admin_headers, "owner-visit", "diabetes")]:
        response = await client.post(f"/api/v1/sessions/{session}/complete", headers=headers,
            json={"session_id": session, "patient_pseudo": "DEMO-SAME", "approved_entities": [
                {"term": term, "entity_type": "DISEASE", "confidence": .9, "status": "approved"}]})
        assert response.status_code == 202
    staff = (await client.get("/api/v1/inbox", headers=auth_headers)).json()
    owner = (await client.get("/api/v1/inbox", headers=admin_headers)).json()
    assert staff["total"] == owner["total"] == 1
    assert staff["items"][0]["approved_entities"] == ["asthma"]
    assert owner["items"][0]["approved_entities"] == ["diabetes"]
    for headers, other in [(auth_headers, owner["items"][0]), (admin_headers, staff["items"][0])]:
        url = "/api/v1/inbox/" + other["id"]
        assert (await client.get(url, headers=headers)).status_code == 404
        assert (await client.delete(url, headers=headers)).status_code == 404
        assert (await client.post(url + "/archive", headers=headers)).status_code == 404
        assert (await client.post(url + "/restore", headers=headers)).status_code == 404
        assert (await client.post("/api/v1/consent", headers=headers,
            json={"session_id": other["session_id"], "action": "CONSENT_GRANTED"})).status_code == 404
        assert (await client.post(f'/api/v1/sessions/{other["session_id"]}/complete', headers=headers,
            json={"session_id": other["session_id"], "approved_entities": []})).status_code == 404
        assert (await client.post("/api/v1/referrals", headers=headers, json={
            "inbox_item_id": other["id"], "session_id": other["session_id"], "nct_id": "DEMO-ONE",
            "trial_title": "Synthetic", "met_criteria": [], "patient_pseudo": "DEMO-SAME"})).status_code == 404
    for headers, term in [(auth_headers, "asthma"), (admin_headers, "diabetes")]:
        history = (await client.get("/api/v1/timeline/DEMO-SAME", headers=headers)).json()
        assert len(history["visits"]) == 1
        assert [e["entity_term"] for e in history["entries"]] == [term]
        assert history["entries"][0]["confidence"] == .9
    with sqlite3.connect(tmp_db_path) as db:
        db.execute("INSERT INTO inbox_items (id,session_id,created_at,status,matches_json,approved_entities) VALUES ('legacy','legacy','2026-11-17','unread','[]','[]')")
    assert (await client.get("/api/v1/inbox", headers=auth_headers)).json()["total"] == 1
    assert (await client.get("/api/v1/inbox", headers=admin_headers)).json()["total"] == 1
    assert (await client.post('/api/v1/sessions/legacy/complete', headers=admin_headers,
        json={"session_id": "legacy", "approved_entities": []})).status_code == 404


@pytest.mark.asyncio
async def test_migration_preserves_unattributed_records_and_recovers_only_unique_owners(tmp_path, monkeypatch):
    from app.models import database
    path = str(tmp_path / 'migration.db')
    monkeypatch.setattr(database, 'DB_PATH', path)
    await database.init_db()
    with sqlite3.connect(path) as db:
        for session in ['known', 'ambiguous', 'unknown']:
            db.execute("INSERT INTO inbox_items (id,session_id,created_at,status,matches_json,approved_entities) VALUES (?,?,?,'unread','[]','[]')", (session, session, '2026-11-17'))
        for ident, session, user in [('1','known','user-a'), ('2','ambiguous','user-a'), ('3','ambiguous','user-b')]:
            db.execute("INSERT INTO audit_log VALUES (?,?,?,'CONSENT_GRANTED','2026-11-17','test')", (ident,session,user))
    await database.init_db()
    await database.init_db()
    with sqlite3.connect(path) as db:
        assert dict(db.execute('SELECT id,owner_id FROM inbox_items')) == {'known':'user-a', 'ambiguous':None, 'unknown':None}
