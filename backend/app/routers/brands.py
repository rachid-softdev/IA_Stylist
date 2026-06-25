from datetime import datetime, timedelta
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, cast, Date

from app.dependencies import get_current_user, get_current_brand_admin, get_current_brand_admin_me
from app.db.session import get_db
from app.models.user import User
from app.models.brand import Brand, BrandMember
from app.models.api_key import ApiKey
from app.models.job import GenerationJob
from app.services.security import generate_api_key, extract_key_prefix, extract_key_last4
from app.services.conversion import get_conversion_data
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


@router.get("/me/dashboard")
async def get_dashboard(
    user_brand: tuple[User, Brand] = Depends(get_current_brand_admin_me),
    db: AsyncSession = Depends(get_db),
):
    """Get brand dashboard data (KPIs, charts, top SKUs)."""
    brand = user_brand[1]
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    sixty_days_ago = datetime.utcnow() - timedelta(days=60)

    # Current period try-ons
    current_result = await db.execute(
        select(func.count(GenerationJob.id)).where(
            GenerationJob.brand_id == brand.id,
            GenerationJob.job_type == "image",
            GenerationJob.created_at >= thirty_days_ago,
        )
    )
    current_tryons = current_result.scalar() or 0

    # Previous period try-ons
    prev_result = await db.execute(
        select(func.count(GenerationJob.id)).where(
            GenerationJob.brand_id == brand.id,
            GenerationJob.job_type == "image",
            GenerationJob.created_at >= sixty_days_ago,
            GenerationJob.created_at < thirty_days_ago,
        )
    )
    prev_tryons = prev_result.scalar() or 0

    # Try-on history (daily counts for chart)
    history_result = await db.execute(
        select(
            cast(GenerationJob.created_at, Date).label("date"),
            func.count(GenerationJob.id).label("count"),
        ).where(
            GenerationJob.brand_id == brand.id,
            GenerationJob.job_type == "image",
            GenerationJob.created_at >= thirty_days_ago,
        ).group_by(cast(GenerationJob.created_at, Date))
        .order_by(cast(GenerationJob.created_at, Date))
    )
    tryon_history = [
        {"date": str(row.date), "count": row.count}
        for row in history_result.all()
    ]

    # Top SKUs
    top_result = await db.execute(
        select(
            GenerationJob.garment_id,
            func.count(GenerationJob.id).label("tryons"),
        ).where(
            GenerationJob.brand_id == brand.id,
            GenerationJob.job_type == "image",
            GenerationJob.garment_id.isnot(None),
            GenerationJob.created_at >= thirty_days_ago,
        ).group_by(GenerationJob.garment_id)
        .order_by(func.count(GenerationJob.id).desc())
        .limit(10)
    )
    top_garment_ids = {row.garment_id: row.tryons for row in top_result.all()}

    # Get garment names
    top_skus = []
    if top_garment_ids:
        from app.models.garment import Garment
        garment_result = await db.execute(
            select(Garment).where(Garment.id.in_(list(top_garment_ids.keys())))
        )
        garments = garment_result.scalars().all()
        for g in garments:
            top_skus.append({
                "sku": g.sku or g.id[:8],
                "name": g.name or g.sku or "Unknown",
                "tryons": top_garment_ids[g.id],
            })

    # Calculate deltas
    def delta_str(current: int, previous: int) -> str:
        if previous == 0:
            return "+100%" if current > 0 else "0%"
        pct = round(((current - previous) / previous) * 100)
        return f"+{pct}%" if pct >= 0 else f"{pct}%"

    # Try to get real conversion data
    real_data, is_estimate = await get_conversion_data(db, brand.id, days=30)
    if real_data:
        orders = real_data["orders"]
        returns = real_data["returns"]
        # Conversion rate = orders / tryons (capped at 100%)
        conversion_rate = round(min((orders / max(current_tryons, 1)) * 100, 100), 1)
        returns_prevented = max(0, orders - returns)
        savings = returns * 150  # 150€ saved per prevented return
    else:
        conversion_rate = 0.0
        returns_prevented = round(current_tryons * 0.25)
        savings = current_tryons * 150

    return {
        "metrics": {
            "tryons": current_tryons,
            "conversion": conversion_rate,
            "returns_prevented": returns_prevented,
            "savings": savings,
        },
        "deltas": {
            "tryons": delta_str(current_tryons, prev_tryons),
            "conversion": "0%",
            "returns": "0%",
            "savings": delta_str(savings, prev_tryons * 150),
        },
        "tryon_history": tryon_history,
        "top_skus": top_skus,
        "is_estimate": is_estimate,
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
