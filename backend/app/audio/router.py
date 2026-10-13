"""Audio ingestion router — RAM-only audio processing (REQ-08).

SECURITY: Audio bytes are NEVER written to disk. All processing uses io.BytesIO.
"""

from __future__ import annotations

import io
import aiosqlite
from fastapi import APIRouter, Depends, HTTPException, Request, status

from app.auth.jwt_handler import get_current_user
from app.config import settings
from app.models.database import get_db
from app.models.schemas import TokenPayload, TranscriptionResponse
from app.transcription.whisper_service import get_transcription_service

router = APIRouter(prefix="/api/v1/audio", tags=["Audio"])

# Constraints — REQ-08
MAX_AUDIO_SIZE_BYTES = 50 * 1024 * 1024  # 50 MB
ALLOWED_MIME_TYPES = {"audio/wav", "audio/webm", "audio/ogg", "audio/mp4", "audio/mpeg"}


@router.post("/transcribe", response_model=TranscriptionResponse, status_code=status.HTTP_200_OK)
async def transcribe_audio(
    session_id: str,
    request: Request,
    current_user: TokenPayload = Depends(get_current_user),
    db: aiosqlite.Connection = Depends(get_db),
) -> TranscriptionResponse:
    """Transcribe an in-memory audio buffer using Whisper ASR.

    Accept a raw audio request body. Multipart UploadFile may spool to disk,
    so it is deliberately not used for this privacy-sensitive endpoint.

    Args:
        session_id: The visit session this audio belongs to.
        request: Raw audio request (audio/wav or audio/webm).
        current_user: Authenticated user from JWT.

    Returns:
        TranscriptionResponse with transcription text, duration, and detected language.
    """
    # The latest event for this user and session must be an active grant.
    # Authentication alone is never evidence of consent.
    if not session_id.strip():
        raise HTTPException(status_code=422, detail="session_id is required")
    async with db.execute(
        """SELECT action FROM audit_log WHERE session_id = ? AND user_id = ?
           AND action IN ('CONSENT_GRANTED', 'CONSENT_REVOKED')
           ORDER BY rowid DESC LIMIT 1""",
        (session_id, current_user.sub),
    ) as cursor:
        latest = await cursor.fetchone()
    if latest is None or latest["action"] != "CONSENT_GRANTED":
        raise HTTPException(status_code=403, detail="Active session consent is required")

    content_type = (request.headers.get("content-type") or "").split(";", 1)[0].lower()
    if content_type not in ALLOWED_MIME_TYPES:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=f"Unsupported audio format: '{content_type}'. Accepted: {sorted(ALLOWED_MIME_TYPES)}",
        )

    audio_buffer = io.BytesIO()
    async for chunk in request.stream():
        if audio_buffer.tell() + len(chunk) > MAX_AUDIO_SIZE_BYTES:
            audio_buffer.close()
            raise HTTPException(status_code=413, detail="Audio exceeds the 50MB limit")
        audio_buffer.write(chunk)
    if audio_buffer.tell() == 0:
        audio_buffer.close()
        raise HTTPException(status_code=422, detail="Audio body is empty")
    audio_buffer.seek(0)

    try:
        service = get_transcription_service(settings.whisper_model)
        result = service.transcribe_buffer(audio_buffer)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Transcription failed: {str(exc)}",
        )
    finally:
        # Release buffer from memory whether transcription succeeded or failed
        audio_buffer.close()

    return TranscriptionResponse(
        transcription=result["transcription"],
        duration_seconds=result["duration_seconds"],
        language=result["language"],
        session_id=session_id,
        word_confidences=result.get("word_confidences", []),
    )
