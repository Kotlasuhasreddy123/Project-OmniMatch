"""Asynchronous Clinical Trial Inbox router — REQ-07, REQ-10."""

from __future__ import annotations

import json
import logging
import uuid
from datetime import datetime, timezone

import aiosqlite
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Response, status

from app.auth.jwt_handler import get_current_user, require_role
from app.models.database import get_db
from app.models.schemas import (
    ClinicalEntity,
    EntityStatus,
    EvidenceSpan,
    InboxItem,
    InboxListResponse,
    InboxStatus,
    MatchSearchRequest,
    SessionCompleteRequest,
    SessionCompleteResponse,
    TokenPayload,
    TrialMatch,
    UserRole,
)
from app.matching.router import search_trials

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1", tags=["Inbox"])

# Roles permitted to read the inbox
INBOX_ROLES = [UserRole.CLINICAL_STAFF, UserRole.ADMIN]


async def _run_matching_and_store(
    session_id: str,
    approved_entities: list[ClinicalEntity],
    evidence_spans: list[EvidenceSpan],
    db_path: str,
) -> None:
    """Background task: run trial matching and write results to the inbox.

    This runs after session completion so it never blocks the UI.
    Inbox must be populated within 60 seconds (REQ-07).

    Args:
        session_id: The completed visit session ID.
        approved_entities: Approved entities from human verification.
        db_path: Path to the SQLite database.
    """
    from app.evidence.ledger_service import approved_evidence_spans, link_criterion_evidence
    from app.eligibility.criterion_engine import evaluate_trial_eligibility
    from app.matching.router import _generate_missing_variables
    from app.trials.freshness_service import evaluate_trial_freshness
    from app.trials.qdrant_service import get_qdrant_service

    try:
        approved_terms = [
            e.term for e in approved_entities
            if e.status == EntityStatus.APPROVED
            and not e.negated
            and e.context == "patient"
        ]

        if not approved_terms:
            logger.warning("Session %s: no approved entities to match.", session_id)
            return

        qdrant = get_qdrant_service()
        raw_matches = await qdrant.search(approved_terms)
        approved_lower = [t.lower() for t in approved_terms]
        approved_spans = approved_evidence_spans(approved_entities, evidence_spans)

        trial_matches = []
        for m in raw_matches:
            missing = _generate_missing_variables(
                m.get("eligibility_criteria", ""), approved_lower
            )
            breakdown = evaluate_trial_eligibility(
                nct_id=m["nct_id"],
                title=m["title"],
                eligibility_text=m.get("eligibility_criteria", ""),
                similarity_score=m["score"],
                approved_terms=approved_lower,
                negated_terms=[],
                all_terms=approved_lower,
            )
            criterion_breakdown = [
                {
                    "criterion_text": result.criterion_text,
                    "verdict": result.verdict.value,
                    "matched_entity": result.matched_entity,
                    "confidence": result.confidence,
                    "is_inclusion": result.is_inclusion,
                    "explanation": result.explanation,
                }
                for result in breakdown.criteria_results
            ]
            locations = m.get("locations", [])
            trial_matches.append(TrialMatch(
                nct_id=m["nct_id"],
                title=m["title"],
                score=m["score"],
                phase=m["phase"],
                status=m["status"],
                brief_summary=m["brief_summary"],
                conditions=m["conditions"],
                sponsor=m["sponsor"],
                missing_variables=missing,
                criterion_breakdown=criterion_breakdown,
                enrollment_readiness_score=breakdown.enrollment_readiness_score,
                score_explanation=breakdown.score_explanation,
                locations=locations,
                criterion_evidence=link_criterion_evidence(criterion_breakdown, approved_spans),
                freshness=evaluate_trial_freshness(
                    status=m["status"],
                    last_updated=m.get("last_updated", ""),
                    locations=locations,
                ),
            ))

        inbox_id = str(uuid.uuid4())
        now = datetime.now(timezone.utc).isoformat()
        matches_json = json.dumps([m.model_dump() for m in trial_matches])
        entities_json = json.dumps([e.term for e in approved_entities
                                    if e.status == EntityStatus.APPROVED])

        async with aiosqlite.connect(db_path) as db:
            await db.execute(
                """
                INSERT INTO inbox_items
                    (id, session_id, created_at, status, matches_json, approved_entities)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (inbox_id, session_id, now, InboxStatus.UNREAD.value,
                 matches_json, entities_json),
            )
            await db.commit()

        logger.info(
            "Inbox item %s created for session %s with %d matches.",
            inbox_id, session_id, len(trial_matches),
        )

    except Exception as exc:
        logger.error("Background matching failed for session %s: %s", session_id, exc)


# ---------------------------------------------------------------------------
# Session completion endpoint (triggers background matching)
# ---------------------------------------------------------------------------

@router.post(
    "/sessions/{session_id}/complete",
    response_model=SessionCompleteResponse,
    status_code=status.HTTP_202_ACCEPTED,
)
async def complete_session(
    session_id: str,
    body: SessionCompleteRequest,
    background_tasks: BackgroundTasks,
    current_user: TokenPayload = Depends(get_current_user),
) -> SessionCompleteResponse:
    """Mark a visit session as complete and trigger asynchronous trial matching.

    The matching pipeline runs in the background — the UI is not blocked.
    Inbox results appear within 60 seconds (REQ-07).

    Args:
        session_id: URL path session ID.
        body: SessionCompleteRequest with approved entities.
        background_tasks: FastAPI background task queue.
        current_user: Authenticated user from JWT.

    Returns:
        SessionCompleteResponse confirming background task triggered.
    """
    from app.config import settings as app_settings

    background_tasks.add_task(
        _run_matching_and_store,
        session_id=session_id,
        approved_entities=body.approved_entities,
        evidence_spans=body.evidence_spans,
        db_path=app_settings.sqlite_db_path,
    )

    return SessionCompleteResponse(
        session_id=session_id,
        matching_triggered=True,
        message="Session completed. Trial matching is running in the background.",
    )


# ---------------------------------------------------------------------------
# Inbox read endpoints — RBAC enforced (REQ-10)
# ---------------------------------------------------------------------------

@router.get(
    "/inbox",
    response_model=InboxListResponse,
    status_code=status.HTTP_200_OK,
)
async def list_inbox(
    current_user: TokenPayload = Depends(require_role(INBOX_ROLES)),
    db: aiosqlite.Connection = Depends(get_db),
) -> InboxListResponse:
    """Return all inbox items for authorized clinical staff.

    Requires CLINICAL_STAFF or ADMIN role — unauthenticated → 401, wrong role → 403.

    Args:
        current_user: Authenticated user with required role.
        db: Async SQLite connection.

    Returns:
        InboxListResponse with items sorted by created_at descending.
    """
    async with db.execute(
        "SELECT * FROM inbox_items ORDER BY created_at DESC"
    ) as cur:
        rows = await cur.fetchall()

    items: list[InboxItem] = []
    for row in rows:
        matches_data = json.loads(row["matches_json"])
        entities_data = json.loads(row["approved_entities"])
        items.append(InboxItem(
            id=row["id"],
            session_id=row["session_id"],
            created_at=datetime.fromisoformat(row["created_at"]),
            status=InboxStatus(row["status"]),
            matches=[TrialMatch(**m) for m in matches_data],
            approved_entities=entities_data,
        ))

    unread = sum(1 for i in items if i.status == InboxStatus.UNREAD)
    return InboxListResponse(items=items, total=len(items), unread_count=unread)


@router.get(
    "/inbox/{item_id}",
    response_model=InboxItem,
    status_code=status.HTTP_200_OK,
)
async def get_inbox_item(
    item_id: str,
    current_user: TokenPayload = Depends(require_role(INBOX_ROLES)),
    db: aiosqlite.Connection = Depends(get_db),
) -> InboxItem:
    """Return a single inbox item by ID.

    Args:
        item_id: UUID of the inbox item.
        current_user: Authenticated user with required role.
        db: Async SQLite connection.

    Returns:
        InboxItem with full match details and missing variables.
    """
    async with db.execute(
        "SELECT * FROM inbox_items WHERE id = ?", (item_id,)
    ) as cur:
        row = await cur.fetchone()

    if row is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Inbox item '{item_id}' not found.",
        )

    matches_data = json.loads(row["matches_json"])
    entities_data = json.loads(row["approved_entities"])
    return InboxItem(
        id=row["id"],
        session_id=row["session_id"],
        created_at=datetime.fromisoformat(row["created_at"]),
        status=InboxStatus(row["status"]),
        matches=[TrialMatch(**m) for m in matches_data],
        approved_entities=entities_data,
    )


@router.delete(
    "/inbox/{item_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def mark_reviewed(
    item_id: str,
    current_user: TokenPayload = Depends(require_role(INBOX_ROLES)),
    db: aiosqlite.Connection = Depends(get_db),
) -> Response:
    """Mark an inbox item as reviewed.

    Args:
        item_id: UUID of the inbox item to mark reviewed.
        current_user: Authenticated user with required role.
        db: Async SQLite connection.
    """
    async with db.execute(
        "SELECT id FROM inbox_items WHERE id = ?", (item_id,)
    ) as cur:
        row = await cur.fetchone()

    if row is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Inbox item '{item_id}' not found.",
        )

    await db.execute(
        "UPDATE inbox_items SET status = ? WHERE id = ?",
        (InboxStatus.REVIEWED.value, item_id),
    )
    await db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
