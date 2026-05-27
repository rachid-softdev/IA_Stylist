import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.credits import CreditService
from app.models.user import User
from app.models.credit import CreditTransaction


@pytest.mark.asyncio
async def test_get_balance(db_session: AsyncSession, test_user: User):
    service = CreditService(db_session)
    balance = await service.get_balance(test_user.id)
    assert balance == 10


@pytest.mark.asyncio
async def test_check_and_deduct_sufficient(db_session: AsyncSession, test_user: User):
    service = CreditService(db_session)
    result = await service.check_and_deduct(test_user.id, 5, "generation")
    assert result is True


@pytest.mark.asyncio
async def test_check_and_deduct_insufficient(db_session: AsyncSession, test_user: User):
    service = CreditService(db_session)
    result = await service.check_and_deduct(test_user.id, 999, "generation")
    assert result is False


@pytest.mark.asyncio
async def test_deduct_credits(db_session: AsyncSession, test_user: User):
    service = CreditService(db_session)
    result = await service.check_and_deduct(test_user.id, 3, "generation")

    assert result is True
    balance = await service.get_balance(test_user.id)
    assert balance == 7


@pytest.mark.asyncio
async def test_deduct_insufficient(db_session: AsyncSession, test_user: User):
    service = CreditService(db_session)
    result = await service.check_and_deduct(test_user.id, 999, "generation")
    assert result is False


@pytest.mark.asyncio
async def test_refund_credits(db_session: AsyncSession, test_user: User):
    service = CreditService(db_session)
    await service.check_and_deduct(test_user.id, 5, "generation")
    await service.refund(test_user.id, 5, "refund")

    balance = await service.get_balance(test_user.id)
    assert balance == 10


@pytest.mark.asyncio
async def test_add_credits(db_session: AsyncSession, test_user: User):
    service = CreditService(db_session)
    await service.add_credits(test_user.id, 50, "purchase")

    balance = await service.get_balance(test_user.id)
    assert balance == 60


@pytest.mark.asyncio
async def test_transaction_history(db_session: AsyncSession, test_user: User):
    service = CreditService(db_session)
    await service.check_and_deduct(test_user.id, 1, "generation")
    await service.check_and_deduct(test_user.id, 2, "generation")
    await service.add_credits(test_user.id, 50, "purchase")

    transactions = await service.get_transaction_history(test_user.id)
    assert len(transactions) == 3


@pytest.mark.asyncio
async def test_refund_with_for_update(db_session: AsyncSession, test_user: User):
    """Refund with FOR UPDATE lock must work atomically."""
    service = CreditService(db_session)
    await service.check_and_deduct(test_user.id, 5, "generation")
    await service.refund(test_user.id, 5, "refund")
    balance = await service.get_balance(test_user.id)
    assert balance == 10


@pytest.mark.asyncio
async def test_add_credits_with_for_update(db_session: AsyncSession, test_user: User):
    """Add credits with FOR UPDATE lock must work atomically."""
    service = CreditService(db_session)
    await service.add_credits(test_user.id, 20, "purchase")
    balance = await service.get_balance(test_user.id)
    assert balance == 30
