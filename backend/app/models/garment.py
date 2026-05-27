import uuid
from typing import Optional
from sqlalchemy import String, Integer, ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import BaseModel


class Garment(BaseModel):
    __tablename__ = "garments"
    __table_args__ = (UniqueConstraint("brand_id", "sku"),)

    brand_id: Mapped[str] = mapped_column(String(36), ForeignKey("brands.id", ondelete="CASCADE"))
    sku: Mapped[str] = mapped_column(String(255), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    category: Mapped[str] = mapped_column(String(50), nullable=False)
    image_url: Mapped[str] = mapped_column(String(500), nullable=False)
    garment_metadata: Mapped[Optional[dict]] = mapped_column("metadata", JSONB, nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="active")

    brand: Mapped["Brand"] = relationship("Brand", back_populates="garments")
    jobs: Mapped[list["GenerationJob"]] = relationship("GenerationJob", back_populates="garment")
