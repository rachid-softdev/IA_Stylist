import uuid
from typing import TYPE_CHECKING, Optional
from sqlalchemy import String, Integer, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import BaseModel

if TYPE_CHECKING:
    from app.models.api_key import ApiKey


class Brand(BaseModel):
    __tablename__ = "brands"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    plan: Mapped[str] = mapped_column(String(20), default="starter")
    credits: Mapped[int] = mapped_column(Integer, default=100)
    shopify_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    api_key_hash: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    tenant_id: Mapped[str] = mapped_column(
        String(36), unique=True, nullable=False, default=lambda: str(uuid.uuid4())
    )

    members: Mapped[list["BrandMember"]] = relationship("BrandMember", back_populates="brand")
    garments: Mapped[list["Garment"]] = relationship("Garment", back_populates="brand")
    jobs: Mapped[list["GenerationJob"]] = relationship(
        "GenerationJob", back_populates="brand", foreign_keys="GenerationJob.brand_id"
    )
    api_keys: Mapped[list["ApiKey"]] = relationship(
        "ApiKey", back_populates="brand", cascade="all, delete-orphan"
    )


class BrandMember(BaseModel):
    __tablename__ = "brand_members"
    __table_args__ = (UniqueConstraint("brand_id", "user_id"),)

    brand_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("brands.id", ondelete="CASCADE"), primary_key=True
    )
    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="CASCADE"), primary_key=True
    )
    role: Mapped[str] = mapped_column(String(20), default="member")

    brand: Mapped["Brand"] = relationship("Brand", back_populates="members")
    user: Mapped["User"] = relationship("User")
