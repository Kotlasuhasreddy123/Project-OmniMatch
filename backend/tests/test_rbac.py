"""TEST-08: RBAC and authentication tests.

Validates REQ-10 — unauthenticated → 401, unauthorized role → 403.
All inbox endpoints must enforce role-based access control.
"""

from __future__ import annotations

import pytest
from httpx import AsyncClient


# ---------------------------------------------------------------------------
# TEST-08: Unauthenticated access to inbox endpoints → HTTP 401
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_inbox_list_unauthenticated_returns_401(client: AsyncClient):
    """GET /api/v1/inbox without token must return HTTP 401 (REQ-10, TEST-08)."""
    resp = await client.get("/api/v1/inbox")
    assert resp.status_code == 401, (
        f"Expected 401, got {resp.status_code}. Unauthenticated inbox access must be denied."
    )


@pytest.mark.asyncio
async def test_inbox_item_unauthenticated_returns_401(client: AsyncClient):
    """GET /api/v1/inbox/{id} without token must return HTTP 401."""
    resp = await client.get("/api/v1/inbox/nonexistent-id")
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_inbox_delete_unauthenticated_returns_401(client: AsyncClient):
    """DELETE /api/v1/inbox/{id} without token must return HTTP 401."""
    resp = await client.delete("/api/v1/inbox/nonexistent-id")
    assert resp.status_code == 401


# ---------------------------------------------------------------------------
# Authenticated with valid role → access granted
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_inbox_list_clinical_staff_gets_200(client: AsyncClient, auth_headers: dict):
    """GET /api/v1/inbox with CLINICAL_STAFF token must return HTTP 200."""
    resp = await client.get("/api/v1/inbox", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert "items" in data
    assert "total" in data
    assert "unread_count" in data


@pytest.mark.asyncio
async def test_inbox_list_admin_gets_200(client: AsyncClient, admin_headers: dict):
    """GET /api/v1/inbox with ADMIN token must return HTTP 200."""
    resp = await client.get("/api/v1/inbox", headers=admin_headers)
    assert resp.status_code == 200


# ---------------------------------------------------------------------------
# Invalid / expired tokens
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_inbox_with_invalid_token_returns_401(client: AsyncClient):
    """Inbox endpoint with a malformed token must return HTTP 401."""
    resp = await client.get(
        "/api/v1/inbox",
        headers={"Authorization": "Bearer this.is.not.a.valid.jwt"},
    )
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_inbox_with_tampered_token_returns_401(client: AsyncClient, staff_token: str):
    """Inbox endpoint with a tampered (invalid signature) token must return HTTP 401."""
    # Tamper with the signature portion of the JWT
    parts = staff_token.split(".")
    tampered = parts[0] + "." + parts[1] + ".invalidsignature"
    resp = await client.get(
        "/api/v1/inbox",
        headers={"Authorization": f"Bearer {tampered}"},
    )
    assert resp.status_code == 401


# ---------------------------------------------------------------------------
# Auth login endpoint tests
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_login_with_valid_credentials_returns_token(client: AsyncClient):
    """POST /api/v1/auth/login with valid credentials returns a JWT token."""
    resp = await client.post(
        "/api/v1/auth/login",
        json={"username": "clinical_staff", "password": "Staff@12345"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert data["expires_in_seconds"] > 0


@pytest.mark.asyncio
async def test_login_with_wrong_password_returns_401(client: AsyncClient):
    """POST /api/v1/auth/login with wrong password must return HTTP 401."""
    resp = await client.post(
        "/api/v1/auth/login",
        json={"username": "clinical_staff", "password": "WrongPassword!"},
    )
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_login_with_nonexistent_user_returns_401(client: AsyncClient):
    """POST /api/v1/auth/login with unknown username must return HTTP 401."""
    resp = await client.post(
        "/api/v1/auth/login",
        json={"username": "ghost_user", "password": "SomePass@123"},
    )
    assert resp.status_code == 401


# ---------------------------------------------------------------------------
# Trials sync requires ADMIN role
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_trials_sync_requires_admin(client: AsyncClient, auth_headers: dict):
    """POST /api/v1/trials/sync with CLINICAL_STAFF token must return HTTP 403."""
    resp = await client.post("/api/v1/trials/sync", headers=auth_headers)
    assert resp.status_code == 403, (
        "Trial sync must be restricted to ADMIN role only."
    )


# ---------------------------------------------------------------------------
# Health check is public
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_health_check_is_public(client: AsyncClient):
    """GET /api/v1/health must be accessible without authentication."""
    resp = await client.get("/api/v1/health")
    # May be 200 (ok) or 200 degraded if Qdrant not running in test env
    assert resp.status_code == 200
    data = resp.json()
    assert "status" in data
