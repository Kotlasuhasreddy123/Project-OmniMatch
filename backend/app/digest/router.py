"""Referral and digest routers — NEW FEATURES 5 & 7."""

from __future__ import annotations

import logging
import json

import aiosqlite

from fastapi import APIRouter, Depends, HTTPException, status

from app.auth.jwt_handler import get_current_user, require_role
from app.digest.digest_service import initiate_referral, send_daily_digest
from app.models.database import get_db
from app.config import settings
from app.models.schemas import (
    ReferralRequest,
    ReferralResponse,
    TokenPayload,
    UserRole,
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1", tags=["Referral & Digest"])

INBOX_ROLES = [UserRole.CLINICAL_STAFF, UserRole.ADMIN]


@router.post(
    "/referrals",
    response_model=ReferralResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_referral(
    body: ReferralRequest,
    current_user: TokenPayload = Depends(require_role(INBOX_ROLES)),
    db: aiosqlite.Connection = Depends(get_db),
) -> ReferralResponse:
    """Initiate a sponsor referral for a matched clinical trial.

    Logs the referral action in the audit trail and optionally fires
    a webhook to an EHR, Slack, or email gateway. No real PHI is included.

    Args:
        body: ReferralRequest with NCT ID, session ID, and optional webhook.
        current_user: Authenticated CLINICAL_STAFF or ADMIN user.

    Returns:
        ReferralResponse with referral_id, status, and webhook_fired flag.
    """
    if body.webhook_url:
        raise HTTPException(400, 'Webhook destinations must be configured by the installation owner.')
    async with db.execute(
        "SELECT session_id, matches_json, patient_pseudo FROM inbox_items WHERE id = ?", (body.inbox_item_id,)
    ) as cur:
        item = await cur.fetchone()
    if item is None or item["session_id"] != body.session_id:
        raise HTTPException(status_code=404, detail="Matching inbox item not found")
    match = next(
        (m for m in json.loads(item["matches_json"]) if m.get("nct_id") == body.nct_id),
        None,
    )
    if match is None:
        raise HTTPException(status_code=404, detail="Trial is not in this inbox item")
    if match.get("freshness", {}).get("recommended_action") != "ROUTE_TO_COORDINATOR":
        raise HTTPException(status_code=409, detail="Trial status requires verification before referral")

    result = await initiate_referral(
        inbox_item_id=body.inbox_item_id,
        nct_id=body.nct_id,
        session_id=body.session_id,
        initiated_by=current_user.sub,
        patient_pseudo=item['patient_pseudo'] or 'REDACTED',
        trial_title=match.get('title', ''),
        met_criteria=[row.get('criterion_text', '') for row in match.get('criterion_breakdown', []) if row.get('verdict') == 'MET'],
        webhook_url=settings.referral_webhook_url or None,
    )
    return ReferralResponse(
        referral_id=result["referral_id"],
        status=result["status"],
        webhook_fired=result["webhook_fired"],
    )
