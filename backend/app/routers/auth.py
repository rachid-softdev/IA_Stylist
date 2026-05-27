from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from app.config import get_settings
from app.dependencies import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.common import UserResponse
from app.services.csrf import make_csrf_cookie_value

router = APIRouter()


@router.get("/me", response_model=UserResponse)
async def get_me(
    user: User = Depends(get_current_user),
):
    """Get current authenticated user."""
    return user


@router.get("/csrf-token")
async def get_csrf_token(request: Request):
    """Get a fresh CSRF token (set as cookie + returned in body).
    
    The frontend should read the `csrf_token` cookie and include
    its value in the `X-CSRF-Token` header for state-changing requests.
    """
    settings = get_settings()
    cookie_value = make_csrf_cookie_value()
    response = JSONResponse(content={"token": cookie_value.split(".", 1)[0]})
    response.set_cookie(
        key="csrf_token",
        value=cookie_value,
        max_age=86400,
        httponly=False,
        samesite="lax",
        secure=settings.ENVIRONMENT != "local",
    )
    return response


@router.post("/refresh")
async def refresh_token():
    """Token refresh handled by Supabase client on frontend."""
    return {"message": "Token refresh handled client-side via Supabase"}


@router.post("/logout")
async def logout():
    """Logout handled by Supabase client on frontend (clears cookies)."""
    return {"message": "Logged out successfully"}
