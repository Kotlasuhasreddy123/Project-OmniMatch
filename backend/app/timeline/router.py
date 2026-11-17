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
    # Build history only from this account's saved visits. The older shared
    # aggregate table is retained for recovery but never exposed by this API.
    async with db.execute("SELECT * FROM inbox_items WHERE patient_pseudo = ? AND owner_id = ? ORDER BY created_at ASC, id ASC", (patient_pseudo, current_user.sub)) as cur:
        rows = await cur.fetchall()
    history = {}
    for row in rows:
        details = {e["term"].lower().strip(): e for e in json.loads(row["entity_details_json"] or "[]")}
        for term in set(json.loads(row["approved_entities"])):
            key = term.lower().strip()
            if key in history:
                history[key].last_seen = datetime.fromisoformat(row["created_at"])
                history[key].mention_count += 1
            else:
                history[key] = TimelineEntry(entity_term=term, entity_type=details.get(key, {}).get("entity_type", "UNKNOWN"),
                    confidence=details.get(key, {}).get("confidence", 0.0), first_seen=datetime.fromisoformat(row["created_at"]),
                    last_seen=datetime.fromisoformat(row["created_at"]), mention_count=1,
                    session_id=row["session_id"])
    entries = list(history.values())
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
