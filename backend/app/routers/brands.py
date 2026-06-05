from datetime import datetime, timedelta
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.dependencies import get_current_user, get_current_brand_admin, get_current_brand_admin_me
from app.db.session import get_db
from app.models.user import User
from app.models.brand import Brand, BrandMember
from app.models.api_key import ApiKey
from app.models.job import GenerationJob
from app.services.security import generate_api_key, extract_key_prefix, extract_key_last4
from app.schemas.common import (
    BrandResponse,
    BrandMeResponse,
    BrandCreateRequest,
    BrandMemberCreateRequest,
    ApiKeyResponse,
    ApiKeyCreateResponse,
)


class ApiKeyCreateRequest(BaseModel):
    name: Optional[str] = Field(default=None, max_length=100)
    expires_in_days: Optional[int] = Field(default=None, ge=1, le=365)

router = APIRouter()


@router.post("/onboarding", response_model=BrandResponse)
async def create_brand(
    body: BrandCreateRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Create a new brand."""
    brand = Brand(
        name=body.name,
        shopify_url=body.shopify_url,
        plan="starter",
        credits=500,
    )
    db.add(brand)
    await db.flush()

    # Auto-add creator as admin
    member = BrandMember(brand_id=brand.id, user_id=user.id, role="admin")
    db.add(member)

    await db.commit()
    await db.refresh(brand)

    return brand


@router.get("/me", response_model=BrandMeResponse)
async def get_my_brand(
    user_brand: tuple[User, Brand] = Depends(get_current_brand_admin_me),
    db: AsyncSession = Depends(get_db),
):
    """Get current user's brand with enriched data."""
    brand = user_brand[1]

    member_count_result = await db.execute(
        select(func.count(BrandMember.brand_id)).where(BrandMember.brand_id == brand.id)
    )
    member_count = member_count_result.scalar() or 0

    last_job_result = await db.execute(
        select(GenerationJob.completed_at)
        .where(
            GenerationJob.brand_id == brand.id,
            GenerationJob.completed_at.isnot(None),
        )
        .order_by(GenerationJob.completed_at.desc())
        .limit(1)
    )
    last_job = last_job_result.scalar_one_or_none()

    monthly_credits = {"starter": 500, "growth": 2000, "enterprise": 10000}.get(brand.plan, 500)
    credits_usage_pct = round((1 - brand.credits / max(monthly_credits, 1)) * 100, 1)

    return {
        **brand.__dict__,
        "member_count": member_count,
        "last_generation_at": last_job,
        "credits_usage_pct": max(0, min(100, credits_usage_pct)),
        "monthly_credits": monthly_credits,
    }


@router.put("/me", response_model=BrandResponse)
async def update_brand(
    body: BrandCreateRequest,
    user_brand: tuple[User, Brand] = Depends(get_current_brand_admin_me),
    db: AsyncSession = Depends(get_db),
):
    """Update brand details."""
    brand = user_brand[1]
    if body.name:
        brand.name = body.name
    if body.shopify_url:
        brand.shopify_url = body.shopify_url
    await db.commit()
    await db.refresh(brand)
    return brand


@router.get("/{brand_id}/members")
async def list_members(
    brand_id: str,
    user: User = Depends(get_current_brand_admin),
    db: AsyncSession = Depends(get_db),
):
    """List brand members."""
    result = await db.execute(
        select(BrandMember).where(BrandMember.brand_id == brand_id)
    )
    members = result.scalars().all()
    return {"data": members}


@router.post("/{brand_id}/members")
async def add_member(
    body: BrandMemberCreateRequest,
    brand_id: str,
    user: User = Depends(get_current_brand_admin),
    db: AsyncSession = Depends(get_db),
):
    """Invite a member to the brand."""
    # Find user by email
    result = await db.execute(select(User).where(User.email == body.email))
    invited_user = result.scalar_one_or_none()

    if not invited_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "USER_NOT_FOUND", "message": "User not found"},
        )

    member = BrandMember(brand_id=brand_id, user_id=invited_user.id, role=body.role)
    db.add(member)
    await db.commit()

    return {"message": "Member added"}


@router.delete("/{brand_id}/members/{target_user_id}")
async def remove_member(
    brand_id: str,
    target_user_id: str,
    user: User = Depends(get_current_brand_admin),
    db: AsyncSession = Depends(get_db),
):
    """Remove a member from the brand."""
    result = await db.execute(
        select(BrandMember).where(
            BrandMember.brand_id == brand_id,
            BrandMember.user_id == target_user_id,
        )
    )
    member = result.scalar_one_or_none()

    if not member:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    await db.delete(member)
    await db.commit()

    return {"message": "Member removed"}


@router.post("/{brand_id}/api-keys", response_model=ApiKeyCreateResponse)
async def create_api_key(
    body: ApiKeyCreateRequest,
    brand_id: str,
    user: User = Depends(get_current_brand_admin),
    db: AsyncSession = Depends(get_db),
):
    """Generate a new API key for the brand."""

    raw_key, hashed_key = generate_api_key()
    prefix = extract_key_prefix(raw_key)
    last4 = extract_key_last4(raw_key)

    api_key = ApiKey(
        brand_id=brand_id,
        key_hash=hashed_key,
        prefix=prefix,
        last_four=last4,
        name=body.name or "Default",
        expires_at=datetime.utcnow() + timedelta(days=body.expires_in_days) if body.expires_in_days else None,
    )
    db.add(api_key)
    await db.commit()
    await db.refresh(api_key)

    return ApiKeyCreateResponse(api_key=raw_key, id=api_key.id)


@router.get("/{brand_id}/api-keys")
async def list_api_keys(
    brand_id: str,
    user: User = Depends(get_current_brand_admin),
    db: AsyncSession = Depends(get_db),
):
    """List API keys (masked)."""

    result = await db.execute(
        select(ApiKey).where(
            ApiKey.brand_id == brand_id,
            ApiKey.is_active == True,
        ).order_by(ApiKey.created_at.desc())
    )
    keys = result.scalars().all()

    return {
        "data": [
            ApiKeyResponse(
                id=key.id,
                prefix=key.prefix,
                last_four=key.last_four,
                created_at=key.created_at,
            )
            for key in keys
        ]
    }


@router.delete("/{brand_id}/api-keys/{key_id}")
async def delete_api_key(
    brand_id: str,
    key_id: str,
    user: User = Depends(get_current_brand_admin),
    db: AsyncSession = Depends(get_db),
):
    """Delete (deactivate) an API key."""

    result = await db.execute(
        select(ApiKey).where(
            ApiKey.id == key_id,
            ApiKey.brand_id == brand_id,
        )
    )
    api_key = result.scalar_one_or_none()

    if not api_key:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    # Soft delete: deactivate instead of hard delete
    api_key.is_active = False
    await db.commit()

    return {"message": "API key deactivated"}
