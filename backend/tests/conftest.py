"""Shared pytest fixtures for OmniMatch backend tests."""

from __future__ import annotations

import asyncio
import io
import sqlite3
import tempfile
from typing import AsyncGenerator

import pytest
import pytest_asyncio
from fastapi import FastAPI
from httpx import AsyncClient, ASGITransport
# ---------------------------------------------------------------------------
# Temporary database
# ---------------------------------------------------------------------------

@pytest.fixture(autouse=True)
def isolate_rate_limits():
    """Keep in-process IP counters from leaking between independent tests."""
    from app.security.middleware import _rate_store
    _rate_store.clear()

@pytest.fixture
def tmp_db_path(tmp_path):
    """Return a path to a fresh temporary SQLite database."""
    return str(tmp_path / "test_omni.db")


# ---------------------------------------------------------------------------
# App with overridden settings
# ---------------------------------------------------------------------------

@pytest_asyncio.fixture
async def app(tmp_db_path: str, monkeypatch, identity_key) -> FastAPI:
    """Return a configured FastAPI test app with a temporary database."""
    import os
    # Set env var BEFORE importing app modules so pydantic-settings picks it up
    os.environ["SQLITE_DB_PATH"] = tmp_db_path

    # Re-import to pick up new env values (or patch settings directly)
    from app import config as cfg
    cfg.settings.sqlite_db_path = tmp_db_path

    from app.main import app as _app
    from app.models.database import init_db
    import app.models.database as db_mod
    db_mod.DB_PATH = tmp_db_path

    await init_db()
    import time
    from app.auth import workos_verifier as verifier
    monkeypatch.setattr(cfg.settings, "workos_client_id", "client_test")
    monkeypatch.setattr(cfg.settings, "workos_organization_id", "org_test")
    monkeypatch.setattr(verifier, "_client_id", "client_test")
    monkeypatch.setattr(verifier, "_keys", {"test-key": identity_key[1]})
    monkeypatch.setattr(verifier, "_expires", time.monotonic() + 3600)
    return _app


@pytest_asyncio.fixture
async def client(app: FastAPI) -> AsyncGenerator[AsyncClient, None]:
    """Yield an async HTTP test client."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        yield ac


# ---------------------------------------------------------------------------
# Auth helpers
# ---------------------------------------------------------------------------

@pytest.fixture(scope="session")
def identity_key():
    from cryptography.hazmat.primitives.asymmetric import rsa
    from cryptography.hazmat.primitives import serialization
    from jose import jwk
    private = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    pem = private.private_bytes(serialization.Encoding.PEM, serialization.PrivateFormat.PKCS8, serialization.NoEncryption())
    public = private.public_key().public_bytes(serialization.Encoding.PEM, serialization.PublicFormat.SubjectPublicKeyInfo)
    key = jwk.construct(public, "RS256").to_dict()
    key["kid"] = "test-key"
    return pem, key


def test_identity_token(identity_key, admin=False):
    """Locally signed test-provider token; no live account or production bypass."""
    import time
    from jose import jwt
    permissions = ["omnimatch:access"] + (["omnimatch:admin"] if admin else [])
    return jwt.encode(dict(sub="test_admin" if admin else "test_staff", sid="test_session",
        client_id="client_test", org_id="org_test", iss="https://api.workos.com",
        iat=int(time.time()), exp=int(time.time()) + 3600, permissions=permissions),
        identity_key[0], algorithm="RS256", headers={"kid": "test-key"})


@pytest.fixture
def staff_token(identity_key):
    return test_identity_token(identity_key)


@pytest.fixture
def admin_token(identity_key):
    return test_identity_token(identity_key, admin=True)


@pytest.fixture
def auth_headers(staff_token: str) -> dict:
    """Return Authorization headers for clinical_staff."""
    return {"Authorization": f"Bearer {staff_token}"}


@pytest.fixture
def admin_headers(admin_token: str) -> dict:
    """Return Authorization headers for admin user."""
    return {"Authorization": f"Bearer {admin_token}"}


# ---------------------------------------------------------------------------
# Sample audio blob (silent WAV — 1 second, 16kHz, 16-bit mono)
# ---------------------------------------------------------------------------

@pytest.fixture
def silent_wav_bytes() -> bytes:
    """Return a minimal valid WAV file (1s silence, 16kHz mono 16-bit)."""
    import struct
    import wave

    buf = io.BytesIO()
    with wave.open(buf, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(16000)
        wf.writeframes(b"\x00\x00" * 16000)  # 1 second of silence
    return buf.getvalue()


# ---------------------------------------------------------------------------
# Mock transcripts for NLP pipeline testing (TEST-02)
# ---------------------------------------------------------------------------

MOCK_TRANSCRIPTS = [
    # Affirmed conditions
    ("The patient has type 2 diabetes and hypertension.", {"diabetes", "hypertension"}, set()),
    ("Patient presents with asthma and chronic fatigue.", {"asthma", "fatigue"}, set()),
    ("She has been diagnosed with breast cancer and is on chemotherapy.", {"cancer", "chemotherapy"}, set()),
    ("He reports chest pain and shortness of breath.", {"chest pain", "shortness of breath"}, set()),
    ("Patient suffers from depression and insomnia.", {"depression", "insomnia"}, set()),

    # Negated conditions — must be detected as negated
    ("The patient denies diabetes.", set(), {"diabetes"}),
    ("No history of hypertension.", set(), {"hypertension"}),
    ("Patient is without chest pain.", set(), {"chest pain"}),
    ("Rules out asthma at this time.", set(), {"asthma"}),
    ("Negative for cancer.", set(), {"cancer"}),
    ("The patient has no evidence of kidney disease.", set(), {"kidney disease"}),
    ("Patient denies history of stroke.", set(), {"stroke"}),
    ("Never had epilepsy.", set(), {"epilepsy"}),
    ("Free of heart disease.", set(), {"heart disease"}),
    ("Absence of depression noted.", set(), {"depression"}),

    # Family history — must be tagged as family context
    ("Family history of diabetes.", set(), set()),  # family context, not patient
    ("Mother had breast cancer.", set(), set()),
    ("Father had hypertension.", set(), set()),

    # Mixed — affirmed + negated in same transcript
    ("Patient has diabetes but denies hypertension.", {"diabetes"}, {"hypertension"}),
    ("She has asthma but no history of COPD.", {"asthma"}, {"copd"}),
    ("He has fatigue and chest pain, but no fever.", {"fatigue", "chest pain"}, {"fever"}),
]

@pytest.fixture
def mock_transcripts():
    """Return the 20 mock transcripts for pipeline accuracy testing (TEST-02)."""
    return MOCK_TRANSCRIPTS
