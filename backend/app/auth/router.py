"""Authentication router — login endpoint returning JWT tokens."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

import aiosqlite
from fastapi import APIRouter, Depends, HTTPException, status
from passlib.context import CryptContext

from app.auth.jwt_handler import create_access_token
from app.config import settings
from app.models.database import get_db
from app.models.schemas import LoginRequest, TokenResponse, UserRole

router = APIRouter(prefix="/api/v1/auth", tags=["Authentication"])

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# ---------------------------------------------------------------------------
# Seed data — demo users created on first login if not present
# ---------------------------------------------------------------------------
DEMO_USERS = [
    {
        "id": str(uuid.uuid4()),
        "username": "clinical_staff",
        "password": "Staff@12345",
        "role": UserRole.CLINICAL_STAFF,
    },
    {
        "id": str(uuid.uuid4()),
        "username": "admin",
        "password": "Admin@12345",
        "role": UserRole.ADMIN,
    },
]


async def _ensure_demo_users(db: aiosqlite.Connection) -> None:
    """Insert demo users if the users table is empty (first run only)."""
    async with db.execute("SELECT COUNT(*) FROM users") as cur:
        row = await cur.fetchone()
        if row and row[0] > 0:
            return

    for u in DEMO_USERS:
        hashed = pwd_context.hash(u["password"])
        await db.execute(
            "INSERT INTO users (id, username, hashed_pw, role, created_at) VALUES (?,?,?,?,?)",
            (u["id"], u["username"], hashed, u["role"].value, datetime.now(timezone.utc).isoformat()),
        )
    await db.commit()


@router.post("/login", response_model=TokenResponse, status_code=status.HTTP_200_OK)
async def login(body: LoginRequest, db: aiosqlite.Connection = Depends(get_db)) -> TokenResponse:
    """Authenticate a user and return a JWT access token.

    Args:
        body: LoginRequest with username and password.
        db: Async SQLite connection.

    Returns:
        TokenResponse containing the JWT.
    """
    await _ensure_demo_users(db)

    async with db.execute(
        "SELECT hashed_pw, role FROM users WHERE username = ?", (body.username,)
    ) as cur:
        row = await cur.fetchone()

    if row is None or not pwd_context.verify(body.password, row["hashed_pw"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    role = UserRole(row["role"])
    token = create_access_token(body.username, role)
    return TokenResponse(
        access_token=token,
        expires_in_seconds=settings.jwt_expire_hours * 3600,
    )
