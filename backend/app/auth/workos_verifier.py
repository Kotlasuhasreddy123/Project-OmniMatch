"""Verify provider signatures and application/organization permissions; never trust UI claims."""
from __future__ import annotations

import re
import time
import math
import asyncio
import logging
import httpx
from fastapi import HTTPException
import jwt
from jwt.exceptions import PyJWTError as JWTError
from app.config import settings
from app.models.schemas import TokenPayload, UserRole

_keys: dict = {}
_expires = 0.0
_client_id = ""
_refresh_lock = asyncio.Lock()
_logger = logging.getLogger(__name__)


async def refresh_keys(client):
    global _keys, _expires, _client_id
    async with _refresh_lock:
        if time.monotonic() < _expires and _client_id == client:
            return
        try:
            async with httpx.AsyncClient(timeout=10, trust_env=False, follow_redirects=False) as session:
                response = await session.get(f'https://api.workos.com/sso/jwks/{client}')
                response.raise_for_status()
                if len(response.content) > 65_536:
                    raise ValueError('Oversized signing-key response')
                body = response.json()
            _keys = {key['kid']: key for key in body['keys'] if key.get('kty') == 'RSA' and key.get('use', 'sig') == 'sig' and key.get('alg', 'RS256') == 'RS256'}
            _expires = time.monotonic() + 300
            _client_id = client
        except (httpx.HTTPError, ValueError, KeyError, TypeError):
            raise HTTPException(503, 'The identity provider could not be reached. Try again later.')


async def verify_workos_token(token: str) -> TokenPayload:
    global _keys, _expires, _client_id
    if not isinstance(token, str) or len(token) > 16_384:
        raise HTTPException(401, 'Invalid sign-in token.')
    client = settings.workos_client_id
    if not re.fullmatch(r"client_[A-Za-z0-9]+", client) or not settings.workos_organization_id:
        raise HTTPException(503, "Passwordless access is not configured by the installation owner.")
    try:
        header = jwt.get_unverified_header(token)
        if header.get("alg") != "RS256" or not isinstance(header.get("kid"), str) or not re.fullmatch(r'[A-Za-z0-9._-]{1,128}', header['kid']):
            raise JWTError("Unsupported signature")
    except (JWTError, ValueError, TypeError):
        raise HTTPException(401, "Invalid sign-in token.")
    if time.monotonic() >= _expires or _client_id != client:
        await refresh_keys(client)
    try:
        key = _keys.get(header["kid"])
        if not key:
            raise JWTError("Unknown signing key")
        issuer = (settings.workos_issuer or f"https://api.workos.com/user_management/{client}").rstrip("/")
        data = jwt.decode(token, jwt.PyJWK.from_dict(key).key, algorithms=["RS256"], issuer=[issuer, issuer + "/"], options={
            "verify_aud": False, "require": ['exp', 'iat', 'sub'],
        })
        # AuthKit session JWTs do not require a client_id claim. Application
        # binding comes from the configured client's JWKS, followed by org and
        # permission checks. Validate explicit client/audience claims if present.
        if (("client_id" in data and data["client_id"] != client)
                or ("aud" in data and data["aud"] != client
                    and data["aud"] != [client])
                or not isinstance(data.get("sid"), str)):
            raise JWTError("Wrong application or missing session")
        if not isinstance(data["exp"], (int, float)) or not isinstance(data["sub"], str):
            raise JWTError("Malformed claims")
        if (not data['sub'].strip() or len(data['sub']) > 256 or not data['sid'].strip()
                or len(data['sid']) > 256 or not isinstance(data.get('iat'), (int, float))
                or not math.isfinite(data['iat']) or not math.isfinite(data['exp'])
                or data['iat'] > time.time() + 60 or data['exp'] <= data['iat']):
            raise JWTError('Malformed lifetime or identity')
    except (JWTError, ValueError, KeyError, TypeError) as error:
        # Never log credentials, claims, emails or exception messages.
        _logger.warning("Session verification rejected (%s)", type(error).__name__)
        raise HTTPException(401, "Invalid or expired sign-in token.")
    permissions = data.get("permissions", [])
    if (data.get("org_id") != settings.workos_organization_id
            or not isinstance(permissions, list)
            or settings.workos_access_permission not in permissions):
        raise HTTPException(403, "Your account needs approval and an OmniMatch organization role.")
    role = UserRole.ADMIN if settings.workos_admin_permission in permissions else UserRole.CLINICAL_STAFF
    return TokenPayload(sub=data["sub"], role=role, exp=int(data["exp"]))
