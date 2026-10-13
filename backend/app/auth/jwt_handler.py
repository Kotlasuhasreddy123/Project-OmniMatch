"""JWT creation and verification utilities."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.config import settings
from app.models.schemas import TokenPayload, UserRole

bearer_scheme = HTTPBearer(auto_error=False)


def create_access_token(username: str, role: UserRole) -> str:
    """Create a signed JWT access token.

    Args:
        username: The authenticated user's username.
        role: The user's role (ADMIN or CLINICAL_STAFF).

    Returns:
        A signed JWT string valid for jwt_expire_hours.
    """
    expire = datetime.now(timezone.utc) + timedelta(hours=settings.jwt_expire_hours)
    payload = {
        "sub": username,
        "role": role.value,
        "exp": int(expire.timestamp()),
    }
    return jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


def decode_token(token: str) -> TokenPayload:
    """Decode and validate a JWT token.

    Args:
        token: The raw JWT string.

    Returns:
        TokenPayload with sub, role, and exp fields.

    Raises:
        HTTPException 401 if token is invalid or expired.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials.",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        data = jwt.decode(
            token,
            settings.jwt_secret_key,
            algorithms=[settings.jwt_algorithm],
        )
        return TokenPayload(sub=data["sub"], role=UserRole(data["role"]), exp=data["exp"])
    except (JWTError, KeyError, ValueError):
        raise credentials_exception


async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
) -> TokenPayload:
    """FastAPI dependency that extracts and validates the current user from a Bearer token.

    Args:
        credentials: HTTP Bearer credentials from the Authorization header.

    Returns:
        TokenPayload for the authenticated user.
    """
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return decode_token(credentials.credentials)


def require_role(allowed_roles: list[UserRole]):
    """FastAPI dependency factory that enforces role-based access control.

    Args:
        allowed_roles: List of roles permitted to access the endpoint.

    Returns:
        A dependency function that raises HTTP 403 if the user's role is not in allowed_roles.
    """
    async def _check(current_user: TokenPayload = Depends(get_current_user)) -> TokenPayload:
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Role '{current_user.role}' is not authorized for this resource.",
            )
        return current_user
    return _check
