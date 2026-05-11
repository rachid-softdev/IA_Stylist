from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.dependencies import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.models.job import GenerationJob
from app.models.garment import Garment
from app.schemas.common import AnalyticsOverviewResponse

router = APIRouter()


@router.get("/overview")
async def get_overview(
    brand_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get analytics overview KPIs."""
    # Total try-ons for this brand
    result = await db.execute(
        select(func.count(GenerationJob.id)).where(
            GenerationJob.brand_id == brand_id,
            GenerationJob.job_type == "image",
        )
    )
    total_tryons = result.scalar() or 0

    # Top SKUs
    result = await db.execute(
        select(GenerationJob.garment_id, func.count(GenerationJob.id).label("count"))
        .where(
            GenerationJob.brand_id == brand_id,
            GenerationJob.garment_id.isnot(None),
        )
        .group_by(GenerationJob.garment_id)
        .order_by(func.count(GenerationJob.id).desc())
        .limit(10)
    )
    top_skus = [
        {"garment_id": row.garment_id, "tryons": row.count}
        for row in result.all()
    ]

    return {
        "data": {
            "total_tryons": total_tryons,
            "tryons_delta": 0.0,
            "conversion_rate": 0.0,
            "conversion_delta": 0.0,
            "returns_saved": max(0, int(total_tryons * 0.25)),
            "returns_delta": 0.0,
            "cost_savings": total_tryons * 150.0,
            "savings_delta": 0.0,
        },
        "top_skus": top_skus,
    }
