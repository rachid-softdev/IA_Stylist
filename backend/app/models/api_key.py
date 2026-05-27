from typing import Optional
from datetime import datetime
from sqlalchemy import String, Boolean, ForeignKey, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import BaseModel


class ApiKey(BaseModel):
    __tablename__ = "api_keys"

    brand_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("brands.id", ondelete="CASCADE"), nullable=False, index=True
    )
    key_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    prefix: Mapped[str] = mapped_column(String(20), nullable=False, default="vfs_live_")
    last_four: Mapped[str] = mapped_column(String(4), nullable=False)
    name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    last_used_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    brand: Mapped["Brand"] = relationship("Brand", back_populates="api_keys")
