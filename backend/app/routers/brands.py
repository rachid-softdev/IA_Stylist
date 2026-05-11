from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.dependencies import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.models.brand import Brand, BrandMember
from app.services.security import generate_api_key, hash_api_key, extract_key_prefix, extract_key_last4
from app.schemas.common import (
    BrandResponse,
    BrandCreateRequest,
    BrandMemberResponse,
    BrandMemberCreateRequest,
    ApiKeyResponse,
    ApiKeyCreateResponse,
)

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


@router.get("/me", response_model=BrandResponse)
async def get_my_brand(
    brand_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get current user's brand."""
    # Find brand where user is member
    result = await db.execute(
        select(Brand)
        .join(BrandMember, Brand.id == BrandMember.brand_id)
        .where(BrandMember.user_id == user.id)
        .limit(1)
    )
    brand = result.scalar_one_or_none()

    if not brand:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "NO_BRAND", "message": "No brand associated with this account"},
        )

    return brand


@router.put("/me", response_model=BrandResponse)
async def update_brand(
    body: BrandCreateRequest,
    brand_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Update brand details."""
    result = await db.execute(select(Brand).where(Brand.id == brand_id))
    brand = result.scalar_one_or_none()

    if not brand:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    if body.name:
        brand.name = body.name
    if body.shopify_url:
        brand.shopify_url = body.shopify_url

    await db.commit()
    await db.refresh(brand)

    return brand


@router.get("/members")
async def list_members(
    brand_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List brand members."""
    result = await db.execute(
        select(BrandMember).where(BrandMember.brand_id == brand_id)
    )
    members = result.scalars().all()
    return {"data": members}


@router.post("/members")
async def add_member(
    body: BrandMemberCreateRequest,
    brand_id: str,
    user: User = Depends(get_current_user),
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


@router.delete("/members/{target_user_id}")
async def remove_member(
    brand_id: str,
    target_user_id: str,
    user: User = Depends(get_current_user),
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


@router.post("/api-keys", response_model=ApiKeyCreateResponse)
async def create_api_key(
    brand_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Generate a new API key for the brand."""
    raw_key, hashed_key = generate_api_key()

    result = await db.execute(select(Brand).where(Brand.id == brand_id))
    brand = result.scalar_one_or_none()

    if not brand:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    brand.api_key_hash = hashed_key
    api_key_id = hashed_key[:16]
    await db.commit()

    return ApiKeyCreateResponse(api_key=raw_key, id=api_key_id)


@router.get("/api-keys")
async def list_api_keys(
    brand_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List API keys (masked)."""
    result = await db.execute(select(Brand).where(Brand.id == brand_id))
    brand = result.scalar_one_or_none()

    if not brand:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    keys = []
    if brand.api_key_hash:
        keys.append(
            ApiKeyResponse(
                id=brand.api_key_hash[:16],
                prefix="vfs_live_",
                last_four="****",
                created_at=brand.created_at,
            )
        )

    return {"data": keys}


@router.delete("/api-keys/{key_id}")
async def delete_api_key(
    brand_id: str,
    key_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Delete an API key."""
    result = await db.execute(select(Brand).where(Brand.id == brand_id))
    brand = result.scalar_one_or_none()

    if not brand:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    brand.api_key_hash = None
    await db.commit()

    return {"message": "API key deleted"}
