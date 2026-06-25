from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.dependencies import get_current_brand_admin_me
from app.db.session import get_db
from app.models.brand import Brand
from app.models.conversion import ShopifyConversion
from app.models.user import User as UserModel

router = APIRouter()


class ShopifyConversionRequest(BaseModel):
    period: str = Field(
        ...,
        pattern=r"^\d{4}-\d{2}$",
        description="Period in YYYY-MM format",
    )
    orders: int = Field(default=0, ge=0, description="Number of orders in this period")
    returns: int = Field(default=0, ge=0, description="Number of returns in this period")


class ShopifyConversionResponse(BaseModel):
    period: str
    orders: int
    returns: int
    updated_at: str | None = None


@router.get("/me/shopify/conversion")
async def get_shopify_conversion(
    user_brand: tuple[UserModel, Brand] = Depends(get_current_brand_admin_me),
    db: AsyncSession = Depends(get_db),
):
    """Get Shopify conversion data for the current brand.

    Returns the most recent monthly entry, or a default zero entry.
    """
    brand = user_brand[1]
    result = await db.execute(
        select(ShopifyConversion)
        .where(ShopifyConversion.brand_id == brand.id)
        .order_by(ShopifyConversion.period.desc())
        .limit(12)  # Last 12 months
    )
    rows = result.scalars().all()

    return {
        "data": [
            ShopifyConversionResponse(
                period=r.period,
                orders=r.orders,
                returns=r.returns,
                updated_at=r.updated_at.isoformat() if r.updated_at else None,
            )
            for r in rows
        ]
    }


@router.put("/me/shopify/conversion")
async def update_shopify_conversion(
    body: ShopifyConversionRequest,
    user_brand: tuple[UserModel, Brand] = Depends(get_current_brand_admin_me),
    db: AsyncSession = Depends(get_db),
):
    """Create or update Shopify conversion data for a given period.

    Brands can self-report their monthly order and return counts
    so the dashboard shows real (not estimated) metrics.
    """
    brand = user_brand[1]

    # Check if entry exists for this period
    result = await db.execute(
        select(ShopifyConversion).where(
            ShopifyConversion.brand_id == brand.id,
            ShopifyConversion.period == body.period,
        )
    )
    existing = result.scalar_one_or_none()

    if existing:
        existing.orders = body.orders
        existing.returns = body.returns
    else:
        entry = ShopifyConversion(
            brand_id=brand.id,
            period=body.period,
            orders=body.orders,
            returns=body.returns,
        )
        db.add(entry)

    await db.commit()

    return {
        "data": ShopifyConversionResponse(
            period=body.period,
            orders=body.orders,
            returns=body.returns,
        )
    }
