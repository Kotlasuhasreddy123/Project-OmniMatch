"""
Security middleware — rate limiting, input sanitization, request validation.

This prototype provides local rate limiting and response headers. Other
security controls are implemented in their respective modules or remain
deployment requirements. In particular, this module does not establish
AES-256 storage encryption, TLS 1.3, or HIPAA compliance.
"""

from __future__ import annotations

import re
import time
from collections import defaultdict
from typing import Callable

from fastapi import HTTPException, Request, Response, status
from starlette.middleware.base import BaseHTTPMiddleware

# ---------------------------------------------------------------------------
# In-process rate limiter (production: use Redis via fastapi-limiter)
# ---------------------------------------------------------------------------

_rate_store: dict[str, list[float]] = defaultdict(list)

RATE_LIMITS = {
    "/api/v1/auth/login": (5, 60),       # 5 requests per 60 seconds
    "/api/v1/audio/transcribe": (10, 60), # 10 requests per 60 seconds
    "/api/v1/nlp/extract": (20, 60),      # 20 requests per 60 seconds
    "/api/v1/match/search": (20, 60),     # 20 requests per 60 seconds
    "default": (60, 60),                  # 60 requests per 60 seconds default
}


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Simple in-process sliding-window rate limiter.

    Note: In multi-worker production deployments, replace with
    fastapi-limiter backed by Redis for cross-worker coordination.
    """

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Apply rate limiting based on client IP + path."""
        # Skip rate limiting for health checks and static assets
        if request.url.path in ("/api/v1/health", "/favicon.ico"):
            return await call_next(request)

        client_ip = request.client.host if request.client else "unknown"
        path = request.url.path

        # Find applicable rate limit
        limit, window = RATE_LIMITS.get(path, RATE_LIMITS["default"])
        key = f"{client_ip}:{path}"
        now = time.time()

        # Sliding window: keep only timestamps within the window
        _rate_store[key] = [t for t in _rate_store[key] if now - t < window]

        if len(_rate_store[key]) >= limit:
            return Response(
                content=f"Rate limit exceeded. Max {limit} requests per {window}s.",
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                headers={"Retry-After": str(window)},
            )

        _rate_store[key].append(now)
        return await call_next(request)


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Add security headers to every response."""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "microphone=(self)"
        response.headers["Cache-Control"] = "no-store"
        # Remove server version disclosure
        if "server" in response.headers:
            del response.headers["server"]
        return response


# ---------------------------------------------------------------------------
# Input sanitization for clinical text
# ---------------------------------------------------------------------------

# Characters that have no place in clinical transcriptions
_DANGEROUS_CHARS = re.compile(r"[<>\"'%;()&+\-\-]")
_SQL_KEYWORDS = re.compile(
    r"\b(SELECT|INSERT|UPDATE|DELETE|DROP|CREATE|ALTER|EXEC|UNION|SCRIPT)\b",
    re.IGNORECASE,
)
_HTML_TAGS = re.compile(r"<[^>]+>")
_CONTROL_CHARS = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]")

# Max lengths
MAX_TRANSCRIPTION_LENGTH = 50_000
MAX_SESSION_ID_LENGTH = 128
MAX_ENTITY_TERM_LENGTH = 200


def sanitize_clinical_text(text: str) -> str:
    """Sanitize clinical transcription text for safe NLP processing.

    Removes control characters and HTML tags while preserving
    all legitimate clinical language including punctuation needed
    for negation detection (commas, periods, apostrophes in "doesn't").

    Args:
        text: Raw clinical transcription text.

    Returns:
        Sanitized text safe for NLP processing.
    """
    if not text:
        return ""

    # Remove control characters (keep newlines and tabs)
    text = _CONTROL_CHARS.sub("", text)

    # Strip HTML tags (shouldn't be in audio transcriptions)
    text = _HTML_TAGS.sub("", text)

    # Truncate to max length
    return text[:MAX_TRANSCRIPTION_LENGTH]


def sanitize_session_id(session_id: str) -> str:
    """Sanitize a session ID to prevent injection.

    Args:
        session_id: Raw session ID string.

    Returns:
        Sanitized session ID (alphanumeric + hyphens only).
    """
    # Allow only safe characters in session IDs
    sanitized = re.sub(r"[^a-zA-Z0-9\-_]", "", session_id)
    return sanitized[:MAX_SESSION_ID_LENGTH]


def sanitize_entity_term(term: str) -> str:
    """Sanitize a clinical entity term.

    Args:
        term: Raw entity term string.

    Returns:
        Sanitized term.
    """
    term = _CONTROL_CHARS.sub("", term)
    term = _HTML_TAGS.sub("", term)
    return term[:MAX_ENTITY_TERM_LENGTH].strip()


def validate_no_sql_injection(text: str) -> bool:
    """Check if text contains SQL injection patterns.

    Args:
        text: Input text to check.

    Returns:
        True if text appears safe, False if injection detected.
    """
    return not bool(_SQL_KEYWORDS.search(text))
