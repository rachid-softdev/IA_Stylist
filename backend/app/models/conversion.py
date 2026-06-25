from sqlalchemy import String, Integer, DateTime, func, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column
from app.models.base import BaseModel


class ShopifyConversion(BaseModel):
    """Monthly Shopify conversion data per brand.

    Brands can self-report or sync via webhook. The analytics endpoint
    uses this when available, falling back to estimates otherwise.
    """

    __tablename__ = "shopify_conversions"
    __table_args__ = (UniqueConstraint("brand_id", "period"),)

    brand_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("brands.id", ondelete="CASCADE"), nullable=False, index=True
    )
    period: Mapped[str] = mapped_column(
        String(7), nullable=False
    )  # YYYY-MM format
    orders: Mapped[int] = mapped_column(Integer, default=0)
    returns: Mapped[int] = mapped_column(Integer, default=0)
    updated_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )
