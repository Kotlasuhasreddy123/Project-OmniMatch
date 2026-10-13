"""Patient timeline router — NEW FEATURE 3."""

from __future__ import annotations

import logging
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, status

from app.auth.jwt_handler import require_role
from app.models.schemas import (
    PatientTimelineResponse,
    TimelineEntry,
    TokenPayload,
    UserRole,
)
from app.timeline.timeline_service import get_patient_timeline

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
) -> PatientTimelineResponse:
    """Return the longitudinal entity timeline for a pseudonymized patient.

    Aggregates approved entities across all visit sessions for this patient.
    Enables multi-visit eligibility accumulation — not possible with any
    single-session ambient system.

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

    return PatientTimelineResponse(
        patient_pseudo=patient_pseudo,
        entries=entries,
        total_entities=len(entries),
    )
