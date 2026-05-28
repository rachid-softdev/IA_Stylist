from datetime import datetime
from typing import Optional
from sqlalchemy import String, Integer, ForeignKey, DateTime, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import BaseModel


class GenerationJob(BaseModel):
    __tablename__ = "generation_jobs"

    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    brand_id: Mapped[Optional[str]] = mapped_column(
        String(36), ForeignKey("brands.id", ondelete="SET NULL"), nullable=True, index=True
    )
    job_type: Mapped[str] = mapped_column(String(20), nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="queued", index=True)
    idempotency_key: Mapped[Optional[str]] = mapped_column(
        String(64), unique=True, nullable=True, index=True
    )
    garment_id: Mapped[Optional[str]] = mapped_column(
        String(36), ForeignKey("garments.id", ondelete="SET NULL"), nullable=True
    )
    input_params: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    result_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    result_metadata: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    credits_used: Mapped[int] = mapped_column(Integer, default=1)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    ai_provider: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    duration_ms: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    user: Mapped["User"] = relationship(
        "User", back_populates="jobs", foreign_keys=[user_id]
    )
    brand: Mapped[Optional["Brand"]] = relationship(
        "Brand", back_populates="jobs", foreign_keys=[brand_id]
    )
    garment: Mapped[Optional["Garment"]] = relationship("Garment", back_populates="jobs")
    transactions: Mapped[list["CreditTransaction"]] = relationship(
        "CreditTransaction", back_populates="job"
    )
