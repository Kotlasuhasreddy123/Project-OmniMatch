"""Verify provider signatures and application/organization permissions; never trust UI claims."""
from __future__ import annotations

import re
import time
import httpx
from fastapi import HTTPException
from jose import JWTError, jwt
from app.config import settings
from app.models.schemas import TokenPayload, UserRole

_keys: dict = {}
_expires = 0.0
_client_id = ""


async def verify_workos_token(token: str) -> TokenPayload:
    global _keys, _expires, _client_id
    client = settings.workos_client_id
    if not re.fullmatch(r"client_[A-Za-z0-9]+", client) or not settings.workos_organization_id:
        raise HTTPException(503, "Passwordless access is not configured by the installation owner.")
    try:
        header = jwt.get_unverified_header(token)
        if header.get("alg") != "RS256" or not isinstance(header.get("kid"), str):
            raise JWTError("Unsupported signature")
    except (JWTError, ValueError, TypeError):
        raise HTTPException(401, "Invalid sign-in token.")
    if time.monotonic() >= _expires or _client_id != client:
        try:
            async with httpx.AsyncClient(timeout=10) as session:
                response = await session.get(f"https://api.workos.com/sso/jwks/{client}")
                response.raise_for_status()
                body = response.json()
            _keys = {key["kid"]: key for key in body["keys"] if key.get("kty") == "RSA"}
            _expires = time.monotonic() + 300
            _client_id = client
        except (httpx.HTTPError, ValueError, KeyError, TypeError):
            raise HTTPException(503, "The identity provider could not be reached. Try again later.")
    try:
        key = _keys.get(header["kid"])
        if not key:
            raise JWTError("Unknown signing key")
        issuer = settings.workos_issuer.rstrip("/")
        data = jwt.decode(token, key, algorithms=["RS256"], issuer=[issuer, issuer + "/"], options={
            "verify_aud": False, "require_exp": True, "require_iat": True, "require_sub": True,
        })
        if data.get("client_id") != client or not isinstance(data.get("sid"), str):
            raise JWTError("Wrong application or missing session")
        if not isinstance(data["exp"], (int, float)) or not isinstance(data["sub"], str):
            raise JWTError("Malformed claims")
    except (JWTError, ValueError, KeyError, TypeError):
        raise HTTPException(401, "Invalid or expired sign-in token.")
    permissions = data.get("permissions", [])
    if (data.get("org_id") != settings.workos_organization_id
            or not isinstance(permissions, list)
            or settings.workos_access_permission not in permissions):
        raise HTTPException(403, "Your account needs approval and an OmniMatch organization role.")
    role = UserRole.ADMIN if settings.workos_admin_permission in permissions else UserRole.CLINICAL_STAFF
    return TokenPayload(sub=data["sub"], role=role, exp=int(data["exp"]))
