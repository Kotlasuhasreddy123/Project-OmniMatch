"""ClinicalTrials.gov sync router — REQ-05."""

from __future__ import annotations

import asyncio
import logging
import time
from datetime import datetime, timezone

from fastapi import APIRouter, BackgroundTasks, Depends, status

from app.auth.jwt_handler import require_role
from app.models.schemas import SyncResponse, TokenPayload, UserRole
from app.trials.clinicaltrials_client import ClinicalTrialsClient
from app.trials.qdrant_service import get_qdrant_service

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/trials", tags=["Trials"])


async def _run_sync() -> dict:
    """Execute the full ClinicalTrials.gov → Qdrant sync pipeline.

    Returns:
        Dict with synced_count, duration_seconds, timestamp, status.
    """
    start = time.perf_counter()
    qdrant = get_qdrant_service()
    await qdrant.ensure_collection()

    client = ClinicalTrialsClient()
    synced = 0
    errors = 0

    async for trial in client.iter_studies():
        try:
            await qdrant.upsert_trial(trial)
            synced += 1
        except Exception as exc:
            logger.warning("Failed to upsert trial %s: %s", trial.get("nct_id"), exc)
            errors += 1

    duration = time.perf_counter() - start
    sync_status = "success" if errors == 0 else ("partial" if synced > 0 else "failed")

    logger.info("Sync complete: %d studies in %.1fs (%d errors)", synced, duration, errors)
    return {
        "synced_count": synced,
        "duration_seconds": round(duration, 2),
        "timestamp": datetime.now(timezone.utc),
        "status": sync_status,
    }


@router.post("/sync", response_model=SyncResponse, status_code=status.HTTP_200_OK)
async def trigger_sync(
    current_user: TokenPayload = Depends(require_role([UserRole.ADMIN])),
) -> SyncResponse:
    """Manually trigger a ClinicalTrials.gov → Qdrant synchronization.

    Only ADMIN users may trigger a manual sync. The daily automated sync
    runs via APScheduler at 02:00 UTC.

    Args:
        current_user: Authenticated ADMIN user.

    Returns:
        SyncResponse with count, duration, and sync status.
    """
    result = await _run_sync()
    return SyncResponse(**result)
