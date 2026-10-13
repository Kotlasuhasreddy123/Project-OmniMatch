"""Longitudinal Patient Visit Timeline — NEW FEATURE differentiating OmniMatch.

ALL existing ambient systems (Nuance DAX, Abridge, TrialMatchAI, PRISM) operate
on single-session data. OmniMatch accumulates approved entities across multiple
visits for the same pseudonymized patient, enabling:

  1. Cross-visit entity merging (entity mentioned in visit 1 persists to visit 3)
  2. "Eligibility Unlock" detection — when a new visit fills a previously-missing
     criterion for an already-matched trial
  3. A timeline view in the Inbox showing when each condition was first mentioned

This is a capability gap identified in all reviewed literature as of 2025.
"""

from __future__ import annotations

import json
import logging
from datetime import datetime, timezone

import aiosqlite

from app.config import settings

logger = logging.getLogger(__name__)

CREATE_TIMELINE_TABLE = """
CREATE TABLE IF NOT EXISTS patient_timeline (
    id              TEXT PRIMARY KEY,
    patient_pseudo  TEXT NOT NULL,
    session_id      TEXT NOT NULL,
    entity_term     TEXT NOT NULL,
    entity_type     TEXT NOT NULL,
    confidence      REAL NOT NULL,
    first_seen      TEXT NOT NULL,
    last_seen       TEXT NOT NULL,
    mention_count   INTEGER NOT NULL DEFAULT 1
);
"""

CREATE_TIMELINE_INDEX = """
CREATE INDEX IF NOT EXISTS idx_timeline_patient
ON patient_timeline (patient_pseudo, entity_term);
"""


async def ensure_timeline_table() -> None:
    """Create the patient_timeline table if it doesn't exist."""
    async with aiosqlite.connect(settings.sqlite_db_path) as db:
        await db.execute(CREATE_TIMELINE_TABLE)
        await db.execute(CREATE_TIMELINE_INDEX)
        await db.commit()


async def upsert_patient_entities(
    patient_pseudo: str,
    session_id: str,
    approved_entities: list[dict],
) -> None:
    """Merge new session entities into the patient's longitudinal timeline.

    If an entity already exists for this patient, update last_seen and
    increment mention_count. Otherwise insert as a new entry.

    Args:
        patient_pseudo: Pseudonymized patient identifier (no real PHI).
        session_id: The current visit session ID.
        approved_entities: List of approved entity dicts with term, entity_type, confidence.
    """
    now = datetime.now(timezone.utc).isoformat()

    async with aiosqlite.connect(settings.sqlite_db_path) as db:
        for entity in approved_entities:
            term = entity.get("term", "").lower().strip()
            if not term:
                continue

            async with db.execute(
                "SELECT id, mention_count FROM patient_timeline "
                "WHERE patient_pseudo = ? AND entity_term = ?",
                (patient_pseudo, term),
            ) as cur:
                row = await cur.fetchone()

            if row:
                await db.execute(
                    "UPDATE patient_timeline "
                    "SET last_seen = ?, mention_count = mention_count + 1 "
                    "WHERE id = ?",
                    (now, row[0]),
                )
            else:
                import uuid
                await db.execute(
                    """
                    INSERT INTO patient_timeline
                        (id, patient_pseudo, session_id, entity_term, entity_type,
                         confidence, first_seen, last_seen, mention_count)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, 1)
                    """,
                    (
                        str(uuid.uuid4()),
                        patient_pseudo,
                        session_id,
                        term,
                        entity.get("entity_type", "UNKNOWN"),
                        entity.get("confidence", 0.0),
                        now,
                        now,
                    ),
                )

        await db.commit()


async def get_patient_timeline(patient_pseudo: str) -> list[dict]:
    """Return the full entity timeline for a patient across all visits.

    Args:
        patient_pseudo: Pseudonymized patient identifier.

    Returns:
        List of timeline entry dicts sorted by first_seen ascending.
    """
    async with aiosqlite.connect(settings.sqlite_db_path) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT * FROM patient_timeline WHERE patient_pseudo = ? "
            "ORDER BY first_seen ASC",
            (patient_pseudo,),
        ) as cur:
            rows = await cur.fetchall()

    return [dict(row) for row in rows]


async def get_cumulative_entities(patient_pseudo: str) -> list[str]:
    """Return all entity terms ever approved for this patient across all visits.

    Used by the match engine to query Qdrant with a richer entity set than
    a single session provides.

    Args:
        patient_pseudo: Pseudonymized patient identifier.

    Returns:
        Sorted list of unique entity term strings.
    """
    timeline = await get_patient_timeline(patient_pseudo)
    return sorted({entry["entity_term"] for entry in timeline})


async def detect_eligibility_unlocks(
    patient_pseudo: str,
    new_session_terms: list[str],
    previous_missing_variables: dict[str, list[str]],
) -> list[dict]:
    """Detect if new session entities fill previously-missing trial criteria.

    This is the "Eligibility Unlock" feature — when a new visit session
    adds an entity that was previously listed as MISSING for a matched trial,
    an unlock event is generated and shown in the inbox.

    Args:
        patient_pseudo: Pseudonymized patient identifier.
        new_session_terms: Newly approved entity terms from current session.
        previous_missing_variables: Dict mapping nct_id → list of missing variable strings.

    Returns:
        List of unlock event dicts: {nct_id, unlocked_criterion, entity_term}.
    """
    unlocks: list[dict] = []
    new_lower = {t.lower() for t in new_session_terms}

    for nct_id, missing_vars in previous_missing_variables.items():
        for missing_var in missing_vars:
            missing_lower = missing_var.lower()
            for term in new_lower:
                if term in missing_lower:
                    unlocks.append({
                        "nct_id": nct_id,
                        "unlocked_criterion": missing_var,
                        "entity_term": term,
                        "patient_pseudo": patient_pseudo,
                    })
                    break

    return unlocks
