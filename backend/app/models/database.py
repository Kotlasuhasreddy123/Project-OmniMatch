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
        # Additive migration: retain all existing demo inbox data.
        async with db.execute("PRAGMA table_info(inbox_items)") as cur:
            columns = {row[1] for row in await cur.fetchall()}
        if "patient_pseudo" not in columns:
            await db.execute("ALTER TABLE inbox_items ADD COLUMN patient_pseudo TEXT")
        if "archived_at" not in columns:
            await db.execute("ALTER TABLE inbox_items ADD COLUMN archived_at TEXT")
        if "owner_id" not in columns:
            await db.execute("ALTER TABLE inbox_items ADD COLUMN owner_id TEXT")
        if "entity_details_json" not in columns:
            await db.execute("ALTER TABLE inbox_items ADD COLUMN entity_details_json TEXT")
        await db.execute("CREATE TABLE IF NOT EXISTS session_owners (session_id TEXT PRIMARY KEY, user_id TEXT NOT NULL)")
        # Recover ownership only from unambiguous historical audit evidence.
        # Unattributed records remain preserved but invisible to all accounts.
        await db.execute("""INSERT OR IGNORE INTO session_owners (session_id, user_id)
            SELECT session_id, MIN(user_id) FROM audit_log
            GROUP BY session_id HAVING COUNT(DISTINCT user_id) = 1""")
        await db.execute("""UPDATE inbox_items SET owner_id =
            (SELECT user_id FROM session_owners WHERE session_id = inbox_items.session_id)
            WHERE owner_id IS NULL""")
        await db.execute("CREATE INDEX IF NOT EXISTS idx_inbox_owner ON inbox_items(owner_id, created_at)")
        await db.commit()
