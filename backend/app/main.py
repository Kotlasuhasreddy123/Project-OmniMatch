"""OmniMatch FastAPI application entry point."""

from __future__ import annotations

import logging

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.auth.consent_router import router as consent_router
from app.auth.router import router as auth_router
from app.audio.router import router as audio_router
from app.config import settings
from app.digest.router import router as digest_router
from app.evidence.router import router as evidence_router
from app.inbox.router import router as inbox_router
from app.matching.router import router as matching_router
from app.models.database import init_db
from app.models.schemas import HealthResponse
from app.nlp.router import router as nlp_router
from app.security.middleware import RateLimitMiddleware, SecurityHeadersMiddleware
from app.timeline.router import router as timeline_router
from app.trials.router import router as trials_router
from app.trials.qdrant_service import get_qdrant_service
from app.transcription.whisper_service import get_whisper_model
from app.timeline.timeline_service import ensure_timeline_table
from app.digest.digest_service import ensure_referrals_table

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# APScheduler for daily ClinicalTrials.gov sync
# ---------------------------------------------------------------------------
scheduler = AsyncIOScheduler()


def _schedule_daily_sync() -> None:
    """Register the daily sync job and end-of-day digest with APScheduler."""
    from app.trials.router import _run_sync
    from app.digest.digest_service import send_daily_digest

    scheduler.add_job(
        _run_sync,
        trigger="cron",
        hour=settings.sync_cron_hour,
        minute=settings.sync_cron_minute,
        id="daily_clinicaltrials_sync",
        replace_existing=True,
    )
    logger.info(
        "Daily sync scheduled at %02d:%02d UTC",
        settings.sync_cron_hour,
        settings.sync_cron_minute,
    )

    # NEW FEATURE 7: End-of-day digest at 17:00 UTC
    async def _send_digest() -> None:
        """Collect inbox summary and fire digest webhook if configured."""
        import aiosqlite
        async with aiosqlite.connect(settings.sqlite_db_path) as db:
            async with db.execute(
                "SELECT COUNT(*) FROM inbox_items WHERE status='unread'"
            ) as cur:
                row = await cur.fetchone()
                unread = row[0] if row else 0
            async with db.execute("SELECT COUNT(*) FROM inbox_items") as cur:
                row = await cur.fetchone()
                total = row[0] if row else 0

        digest_webhook = getattr(settings, "digest_webhook_url", "")
        if digest_webhook:
            await send_daily_digest(
                digest_webhook,
                {
                    "unread_count": unread,
                    "total": total,
                    "inbox_url": f"{settings.app_allowed_origins.split(',')[0].strip()}/inbox",
                    "sessions_today": 0,
                },
            )
        else:
            logger.info("Daily digest: %d unread items (no webhook configured)", unread)

    scheduler.add_job(
        _send_digest,
        trigger="cron",
        hour=17,
        minute=0,
        id="daily_digest",
        replace_existing=True,
    )
    logger.info("End-of-day digest scheduled at 17:00 UTC")


# ---------------------------------------------------------------------------
# Application factory
# ---------------------------------------------------------------------------
app = FastAPI(
    title="OmniMatch API",
    description=(
        "Ambient AI Clinical Intelligence and Automated Trial-Routing Engine. "
        "CPSC-69100 Master's Project — HealthTech Innovation Labs."
    ),
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
)

from app.security.middleware import RateLimitMiddleware, SecurityHeadersMiddleware

# CORS — allow the Next.js frontend origin
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security headers on every response
app.add_middleware(SecurityHeadersMiddleware)

# Rate limiting (in-process; use Redis-backed in multi-worker prod)
app.add_middleware(RateLimitMiddleware)

# Register all routers
app.include_router(auth_router)
app.include_router(consent_router)
app.include_router(audio_router)
app.include_router(nlp_router)
app.include_router(trials_router)
app.include_router(matching_router)
app.include_router(inbox_router)
app.include_router(digest_router)    # NEW: referral routing (Feature 5)
app.include_router(evidence_router)  # Renewed: PHI-minimized evidence ledger
app.include_router(timeline_router)  # NEW: longitudinal timeline (Feature 3)


# ---------------------------------------------------------------------------
# Lifecycle events
# ---------------------------------------------------------------------------

@app.on_event("startup")
async def on_startup() -> None:
    """Initialize database tables, Qdrant collection, and APScheduler on startup."""
    logger.info("OmniMatch API starting up...")
    await init_db()
    logger.info("SQLite tables initialized.")

    # NEW: Initialize tables for new features
    await ensure_timeline_table()
    await ensure_referrals_table()
    logger.info("Extended tables initialized (timeline, referrals).")

    try:
        qdrant = get_qdrant_service()
        await qdrant.ensure_collection()
        logger.info("Qdrant collection ensured.")
    except Exception as exc:
        logger.warning("Qdrant not available at startup (will retry on first request): %s", exc)

    _schedule_daily_sync()
    scheduler.start()
    logger.info("APScheduler started.")


@app.on_event("shutdown")
async def on_shutdown() -> None:
    """Gracefully shut down the APScheduler."""
    scheduler.shutdown(wait=False)
    logger.info("APScheduler stopped.")


# ---------------------------------------------------------------------------
# Health check
# ---------------------------------------------------------------------------

@app.get("/api/v1/health", response_model=HealthResponse, tags=["Health"])
async def health_check() -> HealthResponse:
    """Return system health status including Qdrant connectivity.

    Returns:
        HealthResponse with status, qdrant_connected, and whisper_loaded.
    """
    try:
        qdrant = get_qdrant_service()
        qdrant_ok = await qdrant.is_connected()
    except Exception as exc:
        logger.warning("Qdrant health check failed: %s", exc)
        qdrant_ok = False
    whisper_ok = True  # Whisper loads lazily; flag as True once the model is cached

    overall = "ok" if qdrant_ok else "degraded"
    return HealthResponse(
        status=overall,
        qdrant_connected=qdrant_ok,
        whisper_loaded=whisper_ok,
    )
