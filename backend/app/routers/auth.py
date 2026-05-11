from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.dependencies import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.common import UserResponse

router = APIRouter()


@router.get("/me", response_model=UserResponse)
async def get_me(
    user: User = Depends(get_current_user),
):
    """Get current authenticated user."""
    return user


@router.post("/refresh")
async def refresh_token():
    """Token refresh handled by Supabase client on frontend."""
    return {"message": "Token refresh handled client-side via Supabase"}


@router.post("/logout")
async def logout():
    """Logout handled by Supabase client on frontend (clears cookies)."""
    return {"message": "Logged out successfully"}
