"""JWT generation and validation for widget sessions.

Widgets use short-lived JWTs (15 min) so the raw API key is not transmitted
on every request. The SDK calls /auth once, gets a JWT, and uses it for
subsequent /generate and /jobs calls.
"""

import uuid
from datetime import datetime, timedelta, timezone

from fastapi import HTTPException, Request, status
from jose import jwt, JWTError

from app.config import get_settings

ALGORITHM = "HS256"
WIDGET_TOKEN_EXPIRE_MINUTES = 15


def create_widget_token(brand_id: str) -> dict:
    """Create a short-lived JWT for a widget session.

    Returns the token data including access_token and expiry.
    """
    settings = get_settings()
    now = datetime.now(timezone.utc)
    payload = {
        "sub": brand_id,
        "iss": "vfs-widget",
        "aud": "vfs-widget-api",
        "iat": now,
        "exp": now + timedelta(minutes=WIDGET_TOKEN_EXPIRE_MINUTES),
        "jti": uuid.uuid4().hex,
        "type": "widget",
    }
    token = jwt.encode(payload, settings.JWT_SECRET, algorithm=ALGORITHM)
    return {
        "access_token": token,
        "token_type": "Bearer",
        "expires_in": WIDGET_TOKEN_EXPIRE_MINUTES * 60,
        "brand_id": brand_id,
    }


def decode_widget_token(token: str) -> str | None:
    """Validate a widget JWT and return the brand_id, or None if invalid."""
    settings = get_settings()
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET,
            algorithms=[ALGORITHM],
            audience="vfs-widget-api",
            issuer="vfs-widget",
        )
        if payload.get("type") != "widget":
            return None
        return payload.get("sub")
    except JWTError:
        return None


async def get_widget_brand_id(request: Request) -> str:
    """FastAPI dependency: extract brand_id from widget JWT in Authorization header."""
    auth = request.headers.get("Authorization", "")
    if not auth.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"code": "MISSING_TOKEN", "message": "Missing widget token"},
        )
    token = auth.replace("Bearer ", "")
    brand_id = decode_widget_token(token)
    if not brand_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"code": "INVALID_TOKEN", "message": "Invalid or expired widget token"},
        )
    return brand_id
