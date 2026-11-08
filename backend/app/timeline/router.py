"""Patient timeline router — NEW FEATURE 3."""

from __future__ import annotations

import logging
import json
import aiosqlite
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, status

from app.auth.jwt_handler import require_role
from app.models.schemas import (
    PatientTimelineResponse,
    TimelineEntry,
    TimelineVisit,
    TokenPayload,
    UserRole,
)
from app.timeline.timeline_service import get_patient_timeline
from app.models.database import get_db

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/timeline", tags=["Timeline"])

INBOX_ROLES = [UserRole.CLINICAL_STAFF, UserRole.ADMIN]


@router.get(
    "/{patient_pseudo}",
    response_model=PatientTimelineResponse,
    status_code=status.HTTP_200_OK,
)
async def get_timeline(
    patient_pseudo: str,
    current_user: TokenPayload = Depends(require_role(INBOX_ROLES)),
    db: aiosqlite.Connection = Depends(get_db),
) -> PatientTimelineResponse:
    """Return the longitudinal entity timeline for a pseudonymized patient.

    Aggregates approved entities across all visit sessions for this patient.
    History is for review only; it does not establish a current diagnosis or
    automatically merge old terms into the matching query.

    Args:
        patient_pseudo: Pseudonymized patient identifier (no real PHI).
        current_user: Authenticated CLINICAL_STAFF or ADMIN user.

    Returns:
        PatientTimelineResponse with entity history and mention counts.
    """
    entries_raw = await get_patient_timeline(patient_pseudo)

    entries = [
        TimelineEntry(
            entity_term=e["entity_term"],
            entity_type=e["entity_type"],
            confidence=e["confidence"],
            first_seen=datetime.fromisoformat(e["first_seen"]),
            last_seen=datetime.fromisoformat(e["last_seen"]),
            mention_count=e["mention_count"],
            session_id=e["session_id"],
        )
        for e in entries_raw
    ]

    # Saved visit results provide a truthful visit-by-visit view, even after archive.
    async with db.execute("SELECT * FROM inbox_items WHERE patient_pseudo = ? ORDER BY created_at ASC, id ASC", (patient_pseudo,)) as cur:
        rows = await cur.fetchall()
    visits = []
    seen_sessions = set()
    for row in rows:
        if row["session_id"] in seen_sessions:
            continue  # Older completion retries must not count as new visits.
        seen_sessions.add(row["session_id"])
        visits.append(TimelineVisit(session_id=row["session_id"], created_at=row["created_at"],
                                    approved_terms=json.loads(row["approved_entities"]),
                                    study_count=len(json.loads(row["matches_json"])),
                                    reviewed=row["status"] == "reviewed", archived=row["archived_at"] is not None))
    return PatientTimelineResponse(
        patient_pseudo=patient_pseudo,
        entries=entries,
        total_entities=len(entries),
        visits=visits,
    )
