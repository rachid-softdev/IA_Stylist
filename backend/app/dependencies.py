from fastapi import Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional

from app.db.session import get_db
from app.config import get_settings, Settings
from app.models.user import User
from app.models.brand import BrandMember


async def get_settings_dep() -> Settings:
    return get_settings()


async def get_current_user_from_request(
    request: Request,
    db: AsyncSession = Depends(get_db),
    settings: Settings = Depends(get_settings_dep),
) -> User:
    """Extract and validate JWT from request cookie or Authorization header."""
    token = None

    # Try httpOnly cookie first
    token = request.cookies.get("vfs_access_token")

    # Fallback to Authorization header
    if not token:
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.replace("Bearer ", "")

    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"code": "MISSING_TOKEN", "message": "Authentication required"},
        )

    try:
        # Verify JWT with Supabase
        import httpx

        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{settings.SUPABASE_URL}/auth/v1/user",
                headers={
                    "Authorization": f"Bearer {token}",
                    "apikey": settings.SUPABASE_ANON_KEY,
                },
            )

            if response.status_code != 200:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail={"code": "INVALID_TOKEN", "message": "Invalid or expired token"},
                )

            supabase_user = response.json()
            user_id = supabase_user["id"]

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"code": "AUTH_ERROR", "message": f"Authentication failed: {str(e)}"},
        )

    # Get or create local user
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user:
        # Create local user (first login)
        user = User(
            id=user_id,
            email=supabase_user.get("email", ""),
            plan="free",
            credits=settings.CREDITS_FREE_PER_MONTH,
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)

    # Store user on request state for middleware access
    request.state.current_user = user
    request.state.current_user_id = user.id
    request.state.current_user_plan = user.plan

    return user


async def get_current_user(
    request: Request,
    user: User = Depends(get_current_user_from_request),
) -> User:
    """Dependency that returns the current authenticated user."""
    return user


async def get_optional_user(
    request: Request,
    db: AsyncSession = Depends(get_db),
    settings: Settings = Depends(get_settings_dep),
) -> Optional[User]:
    """Get current user if authenticated, otherwise None."""
    try:
        return await get_current_user_from_request(request, db, settings)
    except HTTPException:
        return None


async def require_plan(plan: str):
    """Factory to create a dependency that requires a specific plan tier."""

    async def _require_plan(user: User = Depends(get_current_user)) -> User:
        plan_hierarchy = {"free": 0, "pro": 1, "creator": 2, "starter": 3, "growth": 4, "enterprise": 5}
        required_level = plan_hierarchy.get(plan, 0)
        user_level = plan_hierarchy.get(user.plan, 0)

        if user_level < required_level:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "code": "UPGRADE_REQUIRED",
                    "message": f"This feature requires the {plan} plan",
                },
            )
        return user

    return _require_plan


async def get_current_brand_admin(
    request: Request,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> User:
    """Get current user and verify they are an admin of the brand.
    
    The brand_id is extracted from the request path parameters.
    """
    brand_id = request.path_params.get("brand_id")
    if not brand_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"code": "MISSING_BRAND_ID", "message": "Brand ID is required"},
        )

    result = await db.execute(
        select(BrandMember).where(
            BrandMember.brand_id == brand_id,
            BrandMember.user_id == user.id,
            BrandMember.role == "admin",
        )
    )
    member = result.scalar_one_or_none()

    if not member:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "code": "FORBIDDEN",
                "message": "Brand admin access required",
            },
        )
    return user


async def verify_brand_membership(
    request: Request,
    user: Optional[User] = Depends(get_optional_user),
    db: AsyncSession = Depends(get_db),
) -> str:
    """Dual-mode (API key + JWT) brand membership verification.

    Returns the brand_id if the request is authenticated as a member of the brand.
    For API key auth: verifies the key's brand_id matches the path brand_id.
    For JWT auth: queries BrandMember table for any role.
    """
    brand_id = request.path_params.get("brand_id")
    if not brand_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"code": "MISSING_BRAND_ID", "message": "Brand ID is required"},
        )

    # API key path — trust the brand_id set by ApiKeyMiddleware
    if getattr(request.state, "auth_method", None) == "api_key":
        stored_brand_id = getattr(request.state, "brand_id", None)
        if stored_brand_id != brand_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "code": "FORBIDDEN",
                    "message": "API key not authorized for this brand",
                },
            )
        return brand_id

    # JWT path — verify BrandMember record exists
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"code": "MISSING_TOKEN", "message": "Authentication required"},
        )

    result = await db.execute(
        select(BrandMember).where(
            BrandMember.brand_id == brand_id,
            BrandMember.user_id == user.id,
        )
    )
    member = result.scalar_one_or_none()

    if not member:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "code": "FORBIDDEN",
                "message": "Brand membership required",
            },
        )

    return brand_id


async def verify_brand_admin_access(
    request: Request,
    user: Optional[User] = Depends(get_optional_user),
    db: AsyncSession = Depends(get_db),
) -> str:
    """Dual-mode (API key + JWT) brand admin verification.

    Returns the brand_id if the request is authenticated as an admin of the brand.
    For API key auth: verifies the key's brand_id matches the path brand_id.
    For JWT auth: queries BrandMember table for admin role.
    """
    brand_id = request.path_params.get("brand_id")
    if not brand_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"code": "MISSING_BRAND_ID", "message": "Brand ID is required"},
        )

    # API key path — trust the brand_id set by ApiKeyMiddleware
    if getattr(request.state, "auth_method", None) == "api_key":
        stored_brand_id = getattr(request.state, "brand_id", None)
        if stored_brand_id != brand_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "code": "FORBIDDEN",
                    "message": "API key not authorized for this brand",
                },
            )
        return brand_id

    # JWT path — verify BrandMember record with admin role
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"code": "MISSING_TOKEN", "message": "Authentication required"},
        )

    result = await db.execute(
        select(BrandMember).where(
            BrandMember.brand_id == brand_id,
            BrandMember.user_id == user.id,
            BrandMember.role == "admin",
        )
    )
    member = result.scalar_one_or_none()

    if not member:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "code": "FORBIDDEN",
                "message": "Brand admin access required",
            },
        )

    return brand_id
