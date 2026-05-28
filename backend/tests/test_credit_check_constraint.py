"""Tests for credits CHECK constraint enforcement (H-04).

Covers:
- IntegrityError from negative credits is caught and returns False
- db.rollback() is called on IntegrityError
- Normal deduction flow still works
- logger.critical is called with error context on IntegrityError
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from sqlalchemy.exc import IntegrityError

from app.services.credits import CreditService


@pytest.fixture
def mock_db():
    """Create a mock async session."""
    return AsyncMock()


@pytest.fixture
def service(mock_db):
    """Create a CreditService with mocked DB."""
    return CreditService(mock_db)


def _make_user(credits: int = 10):
    """Create a mock user with a given credit balance."""
    user = MagicMock()
    user.id = "user-001"
    user.credits = credits
    return user


def _make_result(user):
    """Create a mock DB result that returns the given user via scalar_one_or_none."""
    result = MagicMock()
    result.scalar_one_or_none.return_value = user
    return result


class TestCreditCheckConstraint:

    @pytest.mark.asyncio
    async def test_integrity_error_caught(self, service, mock_db):
        """When UPDATE raises IntegrityError, check_and_deduct must return False."""
        mock_user = _make_user(credits=10)
        mock_db.execute.side_effect = [
            _make_result(mock_user),  # First call: SELECT returns user
            IntegrityError("UPDATE", None, None),  # Second call: UPDATE raises
        ]

        result = await service.check_and_deduct("user-001", 5, "generation")
        assert result is False

    @pytest.mark.asyncio
    async def test_rollback_called_on_integrity_error(self, service, mock_db):
        """When IntegrityError occurs, db.rollback() must be called."""
        mock_user = _make_user(credits=10)
        mock_db.execute.side_effect = [
            _make_result(mock_user),  # First call: SELECT
            IntegrityError("UPDATE", None, None),  # Second call: UPDATE raises
        ]

        await service.check_and_deduct("user-001", 5, "generation")

        mock_db.rollback.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_normal_deduction_unaffected(self, service, mock_db):
        """Normal deduction flow must still return True and call db.execute."""
        mock_user = _make_user(credits=10)
        mock_db.execute.side_effect = [
            _make_result(mock_user),  # First call: SELECT
            MagicMock(),  # Second call: UPDATE succeeds
        ]

        result = await service.check_and_deduct("user-001", 5, "generation")
        assert result is True

        # db.add should have been called for the CreditTransaction
        mock_db.add.assert_called_once()

    @pytest.mark.asyncio
    async def test_logger_called_on_integrity_error(self, service, mock_db):
        """logger.critical must be called with user_id and amount on IntegrityError."""
        mock_user = _make_user(credits=10)
        mock_db.execute.side_effect = [
            _make_result(mock_user),  # SELECT
            IntegrityError("UPDATE", None, None),  # UPDATE raises
        ]

        with patch("app.services.credits.logger") as mock_logger:
            await service.check_and_deduct("user-001", 5, "generation")

            mock_logger.critical.assert_called_once()
            args, _ = mock_logger.critical.call_args
            assert "user-001" in str(args)
            assert "5" in str(args)
