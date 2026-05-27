from typing import Optional
from sqlalchemy import String, Integer, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import BaseModel


class User(BaseModel):
    __tablename__ = "users"

    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    plan: Mapped[str] = mapped_column(String(20), default="free")
    credits: Mapped[int] = mapped_column(Integer, default=10)

    profile: Mapped[Optional["UserProfile"]] = relationship(
        "UserProfile", back_populates="user", uselist=False
    )
    jobs: Mapped[list["GenerationJob"]] = relationship(
        "GenerationJob", back_populates="user", foreign_keys="GenerationJob.user_id"
    )
    transactions: Mapped[list["CreditTransaction"]] = relationship(
        "CreditTransaction", back_populates="user", foreign_keys="CreditTransaction.user_id"
    )
    collections: Mapped[list["Collection"]] = relationship("Collection", back_populates="user")


class UserProfile(BaseModel):
    __tablename__ = "user_profiles"

    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="CASCADE"), unique=True
    )
    photos: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    profile_metadata: Mapped[Optional[dict]] = mapped_column("metadata", JSONB, nullable=True)

    user: Mapped["User"] = relationship("User", back_populates="profile")
