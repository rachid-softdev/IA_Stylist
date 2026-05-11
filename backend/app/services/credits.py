from datetime import datetime
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from sqlalchemy.dialects.postgresql import insert

from app.models.user import User
from app.models.credit import CreditTransaction


class CreditService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_balance(self, user_id: str) -> int:
        result = await self.db.execute(select(User.credits).where(User.id == user_id))
        balance = result.scalar_one_or_none()
        return balance or 0

    async def check_and_reserve(self, user_id: str, amount: int) -> bool:
        """Atomically check and reserve credits. Returns True if sufficient."""
        user = await self.db.execute(
            select(User).where(User.id == user_id).with_for_update()
        )
        user = user.scalar_one_or_none()
        if not user or user.credits < amount:
            return False
        return True

    async def deduct(
        self,
        user_id: str,
        amount: int,
        transaction_type: str = "generation",
        job_id: Optional[str] = None,
        description: Optional[str] = None,
    ) -> bool:
        """Deduct credits and log transaction. Returns True on success."""
        # Atomic deduction
        result = await self.db.execute(
            update(User)
            .where(User.id == user_id, User.credits >= amount)
            .values(credits=User.credits - amount)
            .returning(User.credits)
        )
        new_balance = result.scalar_one_or_none()

        if new_balance is None:
            return False

        # Log transaction
        transaction = CreditTransaction(
            user_id=user_id,
            amount=-amount,
            type=transaction_type,
            job_id=job_id,
            description=description or f"{transaction_type}: {amount} credit(s)",
        )
        self.db.add(transaction)
        await self.db.commit()

        return True

    async def refund(
        self,
        user_id: str,
        amount: int,
        transaction_type: str = "refund",
        job_id: Optional[str] = None,
        description: Optional[str] = None,
    ) -> None:
        """Refund credits to user."""
        await self.db.execute(
            update(User).where(User.id == user_id).values(credits=User.credits + amount)
        )

        transaction = CreditTransaction(
            user_id=user_id,
            amount=amount,
            type=transaction_type,
            job_id=job_id,
            description=description or f"Refund: {amount} credit(s)",
        )
        self.db.add(transaction)
        await self.db.commit()

    async def add_credits(
        self,
        user_id: str,
        amount: int,
        transaction_type: str = "purchase",
        description: Optional[str] = None,
    ) -> None:
        """Add credits to user."""
        await self.db.execute(
            update(User).where(User.id == user_id).values(credits=User.credits + amount)
        )

        transaction = CreditTransaction(
            user_id=user_id,
            amount=amount,
            type=transaction_type,
            description=description or f"Credit {transaction_type}: +{amount}",
        )
        self.db.add(transaction)
        await self.db.commit()

    async def get_transaction_history(
        self,
        user_id: str,
        page: int = 1,
        page_size: int = 20,
    ) -> list[CreditTransaction]:
        offset = (page - 1) * page_size
        result = await self.db.execute(
            select(CreditTransaction)
            .where(CreditTransaction.user_id == user_id)
            .order_by(CreditTransaction.created_at.desc())
            .offset(offset)
            .limit(page_size)
        )
        return list(result.scalars().all())
