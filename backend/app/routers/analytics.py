from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, cast, Date

from app.dependencies import verify_brand_admin_access
from app.db.session import get_db
from app.models.job import GenerationJob
from app.models.garment import Garment
from app.services.conversion import get_conversion_data

router = APIRouter()


@router.get("/{brand_id}/overview")
async def get_overview(
    brand_id: str = Depends(verify_brand_admin_access),
    days: int = Query(default=30, ge=1, le=365),
    db: AsyncSession = Depends(get_db),
):
    """Get analytics overview KPIs."""
    now = datetime.utcnow()
    current_start = now - timedelta(days=days)
    previous_start = current_start - timedelta(days=days)

    async def count_in_range(start: datetime, end: datetime) -> int:
        r = await db.execute(
            select(func.count(GenerationJob.id)).where(
                GenerationJob.brand_id == brand_id,
                GenerationJob.job_type == "image",
                GenerationJob.created_at >= start,
                GenerationJob.created_at < end,
            )
        )
        return r.scalar() or 0

    total_tryons = await count_in_range(current_start, now)
    previous_tryons = await count_in_range(previous_start, current_start)
    tryons_delta = ((total_tryons - previous_tryons) / max(previous_tryons, 1)) * 100

    # Time series by day
    time_series_result = await db.execute(
        select(
            cast(GenerationJob.created_at, Date).label("date"),
            func.count(GenerationJob.id).label("count"),
        )
        .where(
            GenerationJob.brand_id == brand_id,
            GenerationJob.job_type == "image",
            GenerationJob.created_at >= current_start,
        )
        .group_by(cast(GenerationJob.created_at, Date))
        .order_by(cast(GenerationJob.created_at, Date))
    )
    time_series = [
        {"date": str(row.date), "count": row.count}
        for row in time_series_result.all()
    ]

    # Top SKUs with garment names
    top_result = await db.execute(
        select(
            GenerationJob.garment_id,
            Garment.name,
            Garment.sku,
            func.count(GenerationJob.id).label("count"),
        )
        .join(Garment, GenerationJob.garment_id == Garment.id, isouter=True)
        .where(
            GenerationJob.brand_id == brand_id,
            GenerationJob.garment_id.isnot(None),
            GenerationJob.created_at >= current_start,
        )
        .group_by(GenerationJob.garment_id, Garment.name, Garment.sku)
        .order_by(func.count(GenerationJob.id).desc())
        .limit(10)
    )
    top_skus = [
        {
            "garment_id": row.garment_id,
            "name": row.name or "Unknown",
            "sku": row.sku or "",
            "tryons": row.count,
        }
        for row in top_result.all()
    ]

    # Total try-ons overall
    total_all_result = await db.execute(
        select(func.count(GenerationJob.id)).where(
            GenerationJob.brand_id == brand_id,
            GenerationJob.job_type == "image",
        )
    )
    total_all = total_all_result.scalar() or 0

    # Try to get real conversion data
    real_data, is_estimate = await get_conversion_data(db, brand_id, days=days)
    if real_data:
        orders = real_data["orders"]
        returns = real_data["returns"]
        conversion_rate = round(min((orders / max(total_tryons, 1)) * 100, 100), 1)
        returns_saved = max(0, int(orders - returns))
        cost_savings = float(returns * 150)
    else:
        conversion_rate = 0.0
        returns_saved = max(0, int(total_all * 0.25))
        cost_savings = total_all * 150.0

    return {
        "data": {
            "total_tryons": total_tryons,
            "tryons_delta": round(tryons_delta, 1),
            "conversion_rate": conversion_rate,
            "conversion_delta": 0.0,
            "returns_saved": returns_saved,
            "returns_delta": 0.0,
            "cost_savings": cost_savings,
            "savings_delta": 0.0,
            "is_estimate": is_estimate,
        },
        "time_series": time_series,
        "top_skus": top_skus,
    }
