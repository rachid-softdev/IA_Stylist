from datetime import datetime, timedelta
from typing import Optional
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.conversion import ShopifyConversion


async def get_conversion_data(
    db: AsyncSession,
    brand_id: str,
    days: int = 30,
) -> tuple[Optional[dict], bool]:
    """Get real Shopify conversion data for a brand period.

    Returns (data_dict, is_estimate) where data_dict contains:
        orders, returns, conversion_rate, returns_rate
    or None if no real data exists.

    Conversion rate = orders / tryons (computed by the caller)
    """
    # The current period in YYYY-MM format
    now = datetime.utcnow()
    period = now.strftime("%Y-%m")

    result = await db.execute(
        select(ShopifyConversion).where(
            ShopifyConversion.brand_id == brand_id,
            ShopifyConversion.period == period,
        )
    )
    entry = result.scalar_one_or_none()

    if entry is not None and (entry.orders > 0 or entry.returns > 0):
        return (
            {
                "orders": entry.orders,
                "returns": entry.returns,
            },
            False,
        )

    # Fall back to last 3 months average
    three_months_ago = (now - timedelta(days=90)).strftime("%Y-%m")
    agg_result = await db.execute(
        select(
            func.sum(ShopifyConversion.orders),
            func.sum(ShopifyConversion.returns),
        ).where(
            ShopifyConversion.brand_id == brand_id,
            ShopifyConversion.period >= three_months_ago,
        )
    )
    row = agg_result.one()
    total_orders = row[0] or 0
    total_returns = row[1] or 0

    if total_orders > 0:
        return (
            {
                "orders": total_orders,
                "returns": total_returns,
            },
            False,
        )

    return None, True
