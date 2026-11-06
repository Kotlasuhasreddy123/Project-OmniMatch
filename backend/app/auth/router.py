"""Password authentication was retired; WorkOS verifies passwordless identities."""
from fastapi import APIRouter, Depends, HTTPException
from app.auth.jwt_handler import get_current_user
from app.config import settings
from app.models.schemas import TokenPayload

router = APIRouter(prefix="/api/v1/auth", tags=["Authentication"])

@router.post("/login", deprecated=True)
async def retired_password_login():
    raise HTTPException(410, "Password sign-in has been removed. Use approved email-code access.")

@router.get("/me")
async def current_identity(user: TokenPayload = Depends(get_current_user)):
    return {"subject": user.sub, "role": user.role, "expires_at": user.exp}

@router.get("/config")
async def authentication_config():
    return {"configured": bool(settings.workos_client_id and settings.workos_organization_id),
            "method": "WorkOS Magic Auth", "password_login_enabled": False,
            "approval_required": True}
