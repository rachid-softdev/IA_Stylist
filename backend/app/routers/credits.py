from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.dependencies import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.services.credits import CreditService
from app.schemas.common import CreditBalanceResponse, CreditTransactionResponse

router = APIRouter()


@router.get("/balance", response_model=CreditBalanceResponse)
async def get_balance(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get current credit balance."""
    service = CreditService(db)
    balance = await service.get_balance(user.id)

    return CreditBalanceResponse(balance=balance, plan=user.plan)


@router.get("/transactions")
async def get_transactions(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get credit transaction history."""
    service = CreditService(db)
    transactions = await service.get_transaction_history(user.id, page, page_size)

    return {
        "data": transactions,
        "meta": {"page": page, "page_size": page_size},
    }
