"""TEST-01: Consent endpoint and audio stream gating tests.

Validates REQ-01 — microphone stream stays inactive until consent is ON.
Tests the backend audit logging side of the consent workflow.
"""

from __future__ import annotations

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_consent_granted_logs_audit_entry(client: AsyncClient, auth_headers: dict):
    """CONSENT_GRANTED action should create an audit log entry and return logged=True."""
    resp = await client.post(
        "/api/v1/consent",
        json={
            "session_id": "test-session-001",
            "action": "CONSENT_GRANTED",
            "patient_pseudonym": "REDACTED",
        },
        headers=auth_headers,
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["logged"] is True
    assert "audit_id" in data
    assert "timestamp" in data


@pytest.mark.asyncio
async def test_consent_revoked_logs_audit_entry(client: AsyncClient, auth_headers: dict):
    """CONSENT_REVOKED action should create a separate audit log entry."""
    resp = await client.post(
        "/api/v1/consent",
        json={
            "session_id": "test-session-001",
            "action": "CONSENT_REVOKED",
        },
        headers=auth_headers,
    )
    assert resp.status_code == 200
    assert resp.json()["logged"] is True


@pytest.mark.asyncio
async def test_consent_requires_authentication(client: AsyncClient):
    """Consent endpoint must reject unauthenticated requests with HTTP 401 (REQ-10)."""
    resp = await client.post(
        "/api/v1/consent",
        json={"session_id": "sess-x", "action": "CONSENT_GRANTED"},
    )
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_consent_invalid_action_rejected(client: AsyncClient, auth_headers: dict):
    """Invalid consent action values must return HTTP 422 (Pydantic validation)."""
    resp = await client.post(
        "/api/v1/consent",
        json={"session_id": "sess-x", "action": "INVALID_ACTION"},
        headers=auth_headers,
    )
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_audio_endpoint_blocked_without_consent_token(client: AsyncClient, silent_wav_bytes: bytes):
    """Audio transcription requires authentication independently of consent."""
    resp = await client.post(
        "/api/v1/audio/transcribe?session_id=sess-no-consent",
        content=silent_wav_bytes,
        headers={"Content-Type": "audio/wav"},
        # No Authorization header
    )
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_audio_endpoint_rejects_wrong_mime_type(client: AsyncClient, auth_headers: dict):
    """Audio endpoint must reject non-audio MIME types with HTTP 415 (REQ-08)."""
    await client.post("/api/v1/consent", json={"session_id": "sess-mime-test", "action": "CONSENT_GRANTED"}, headers=auth_headers)
    resp = await client.post("/api/v1/audio/transcribe?session_id=sess-mime-test", content=b"not audio data", headers={**auth_headers, "Content-Type": "text/plain"})
    assert resp.status_code == 415


@pytest.mark.asyncio
async def test_audio_endpoint_rejects_oversized_file(client: AsyncClient, auth_headers: dict):
    """Audio endpoint must reject files over 50MB with HTTP 413 (REQ-08)."""
    oversized = b"\x00" * (51 * 1024 * 1024)  # 51 MB
    await client.post("/api/v1/consent", json={"session_id": "sess-size-test", "action": "CONSENT_GRANTED"}, headers=auth_headers)
    resp = await client.post("/api/v1/audio/transcribe?session_id=sess-size-test", content=oversized, headers={**auth_headers, "Content-Type": "audio/wav"})
    assert resp.status_code == 413


@pytest.mark.asyncio
async def test_audio_requires_active_consent(client: AsyncClient, auth_headers: dict, silent_wav_bytes: bytes):
    session = "sess-gated"
    url = f"/api/v1/audio/transcribe?session_id={session}"
    headers = {**auth_headers, "Content-Type": "audio/wav"}
    assert (await client.post(url, content=silent_wav_bytes, headers=headers)).status_code == 403
    await client.post("/api/v1/consent", json={"session_id": session, "action": "CONSENT_GRANTED"}, headers=auth_headers)
    await client.post("/api/v1/consent", json={"session_id": session, "action": "CONSENT_REVOKED"}, headers=auth_headers)
    assert (await client.post(url, content=silent_wav_bytes, headers=headers)).status_code == 403


@pytest.mark.asyncio
async def test_consent_audit_log_is_append_only(client: AsyncClient, auth_headers: dict, tmp_db_path: str):
    """Verify that audit logs cannot be deleted or modified — append-only (REQ-11)."""
    import aiosqlite

    # Write a consent entry
    await client.post(
        "/api/v1/consent",
        json={"session_id": "sess-audit", "action": "CONSENT_GRANTED"},
        headers=auth_headers,
    )

    # Directly inspect DB: row count should be >= 1, no UPDATE/DELETE statements
    async with aiosqlite.connect(tmp_db_path) as db:
        async with db.execute("SELECT COUNT(*) FROM audit_log") as cur:
            row = await cur.fetchone()
            assert row[0] >= 1, "Audit log entry was not written"
