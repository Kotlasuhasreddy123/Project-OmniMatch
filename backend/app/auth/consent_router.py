"""Consent audit logging router — REQ-01, REQ-11."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

import aiosqlite
from fastapi import APIRouter, Depends, Request, status

from app.auth.jwt_handler import get_current_user
from app.models.database import get_db
from app.models.schemas import ConsentRequest, ConsentResponse, TokenPayload

router = APIRouter(prefix="/api/v1/consent", tags=["Consent"])


@router.post("", response_model=ConsentResponse, status_code=status.HTTP_200_OK)
async def log_consent(
    body: ConsentRequest,
    request: Request,
    current_user: TokenPayload = Depends(get_current_user),
    db: aiosqlite.Connection = Depends(get_db),
) -> ConsentResponse:
    """Log a patient consent grant or revocation to the append-only audit log.

    This endpoint MUST be called before any audio capture begins (CONSENT_GRANTED)
    and immediately when audio capture stops (CONSENT_REVOKED).

    Args:
        body: ConsentRequest with session_id, action, and patient pseudonym.
        request: HTTP request object for IP address extraction.
        current_user: Authenticated user making the consent change.
        db: Async SQLite connection.

    Returns:
        ConsentResponse confirming the audit entry was written.
    """
    audit_id = str(uuid.uuid4())
    timestamp = datetime.now(timezone.utc)
    ip_address = request.client.host if request.client else "unknown"

    # Audit logs are append-only — no UPDATE or DELETE ever issued on this table
    await db.execute(
        """
        INSERT INTO audit_log (id, session_id, user_id, action, timestamp, ip_address)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (
            audit_id,
            body.session_id,
            current_user.sub,
            body.action.value,
            timestamp.isoformat(),
            ip_address,
        ),
    )
    await db.commit()

    return ConsentResponse(logged=True, audit_id=audit_id, timestamp=timestamp)
