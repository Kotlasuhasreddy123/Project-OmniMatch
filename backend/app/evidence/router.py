"""Evidence Ledger API routes."""

from fastapi import APIRouter, Depends, status

import aiosqlite
from app.config import settings
from app.auth.ownership import claim_session
from app.auth.jwt_handler import get_current_user
from app.evidence.ledger_service import record_evidence_ledger
from app.models.schemas import EvidenceLedgerRequest, EvidenceLedgerResponse, TokenPayload

router = APIRouter(prefix="/api/v1/evidence", tags=["Evidence Ledger"])


@router.post("/ledger", response_model=EvidenceLedgerResponse, status_code=status.HTTP_201_CREATED)
async def create_evidence_ledger(
    body: EvidenceLedgerRequest,
    current_user: TokenPayload = Depends(get_current_user),
) -> EvidenceLedgerResponse:
    """Record an approved evidence event without storing the raw transcript."""
    async with aiosqlite.connect(settings.sqlite_db_path) as db:
        await claim_session(db, body.session_id, current_user.sub)
    return await record_evidence_ledger(body)
