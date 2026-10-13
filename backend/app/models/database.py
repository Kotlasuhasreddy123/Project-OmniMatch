"""Async SQLite database setup for audit logs and inbox storage."""

from __future__ import annotations

import aiosqlite

from app.config import settings

DB_PATH = settings.sqlite_db_path

CREATE_AUDIT_LOG_TABLE = """
CREATE TABLE IF NOT EXISTS audit_log (
    id          TEXT PRIMARY KEY,
    session_id  TEXT NOT NULL,
    user_id     TEXT NOT NULL,
    action      TEXT NOT NULL,
    timestamp   TEXT NOT NULL,
    ip_address  TEXT NOT NULL
);
"""

CREATE_USERS_TABLE = """
CREATE TABLE IF NOT EXISTS users (
    id           TEXT PRIMARY KEY,
    username     TEXT UNIQUE NOT NULL,
    hashed_pw    TEXT NOT NULL,
    role         TEXT NOT NULL DEFAULT 'CLINICAL_STAFF',
    created_at   TEXT NOT NULL
);
"""

CREATE_INBOX_TABLE = """
CREATE TABLE IF NOT EXISTS inbox_items (
    id                  TEXT PRIMARY KEY,
    session_id          TEXT NOT NULL,
    created_at          TEXT NOT NULL,
    status              TEXT NOT NULL DEFAULT 'unread',
    matches_json        TEXT NOT NULL,
    approved_entities   TEXT NOT NULL
);
"""

CREATE_SESSIONS_TABLE = """
CREATE TABLE IF NOT EXISTS visit_sessions (
    id              TEXT PRIMARY KEY,
    created_at      TEXT NOT NULL,
    completed_at    TEXT,
    status          TEXT NOT NULL DEFAULT 'active'
);
"""

CREATE_EVIDENCE_LEDGER_TABLE = """
CREATE TABLE IF NOT EXISTS evidence_ledger (
    id              TEXT PRIMARY KEY,
    session_id      TEXT NOT NULL,
    event_hash      TEXT NOT NULL,
    payload_json    TEXT NOT NULL,
    created_at      TEXT NOT NULL
);
"""


async def get_db() -> aiosqlite.Connection:
    """Open and return a database connection for use as a FastAPI dependency."""
    db = await aiosqlite.connect(DB_PATH)
    db.row_factory = aiosqlite.Row
    try:
        yield db
    finally:
        await db.close()


async def init_db() -> None:
    """Create all tables on application startup if they don't exist."""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(CREATE_AUDIT_LOG_TABLE)
        await db.execute(CREATE_USERS_TABLE)
        await db.execute(CREATE_INBOX_TABLE)
        await db.execute(CREATE_SESSIONS_TABLE)
        await db.execute(CREATE_EVIDENCE_LEDGER_TABLE)
        await db.commit()
