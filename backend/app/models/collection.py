from typing import Optional
from sqlalchemy import String, Boolean, ForeignKey, DateTime, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import BaseModel
from datetime import datetime


class Collection(BaseModel):
    __tablename__ = "collections"

    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    is_public: Mapped[bool] = mapped_column(Boolean, default=False)
    share_token: Mapped[Optional[str]] = mapped_column(String(50), unique=True, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    user: Mapped["User"] = relationship("User", back_populates="collections")
    items: Mapped[list["CollectionItem"]] = relationship(
        "CollectionItem", back_populates="collection", cascade="all, delete-orphan"
    )


class CollectionItem(BaseModel):
    __tablename__ = "collection_items"
    __table_args__ = (UniqueConstraint("collection_id", "job_id"),)

    collection_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("collections.id", ondelete="CASCADE"), primary_key=True
    )
    job_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("generation_jobs.id", ondelete="CASCADE"), primary_key=True
    )
    added_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    collection: Mapped["Collection"] = relationship("Collection", back_populates="items")
    job: Mapped["GenerationJob"] = relationship("GenerationJob")
