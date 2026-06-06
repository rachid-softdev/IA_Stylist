"""Tests for brand auth guard None checks (M-04).

Verifies that verify_brand_membership and verify_brand_admin_access
raise HTTPException with 500 when auth_method is "api_key" but
brand_id is None (defense-in-depth guard against corrupted auth state).
"""
import pytest
from unittest.mock import AsyncMock, MagicMock
from fastapi import HTTPException, status

from app.dependencies import verify_brand_membership, verify_brand_admin_access


# ─── Helpers ────────────────────────────────────────────────────────────


def _mock_request(
    brand_id: str,
    auth_method: str | None = None,
    stored_brand_id: str | None = None,
) -> MagicMock:
    """Create a mock Request with path_params and state."""
    req = MagicMock()
    req.path_params = {"brand_id": brand_id}
    req.state.auth_method = auth_method
    req.state.brand_id = stored_brand_id
    return req


def _make_mock_db(expected_member=None) -> AsyncMock:
    """Create a mock async DB session."""
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = expected_member
    mock_db = AsyncMock()
    mock_db.execute.return_value = mock_result
    return mock_db


# ─── verify_brand_membership — API key path ───────────────────────────


class TestVerifyBrandMembershipApiKeyNoneGuard:
    """M-04: Defense-in-depth guard for None brand_id in API key path."""

    @pytest.mark.asyncio
    async def test_brand_id_none_raises_500(self):
        """auth_method=api_key but brand_id is None → 500 INTERNAL_ERROR.

        This represents a corrupted auth state where ApiKeyMiddleware
        set auth_method but failed to set brand_id. The guard catches
        this and returns 500 instead of silently proceeding.
        """
        req = _mock_request(
            brand_id="brand-001",
            auth_method="api_key",
            stored_brand_id=None,  # Corrupted state
        )
        db = AsyncMock()

        with pytest.raises(HTTPException) as exc:
            await verify_brand_membership(req, user=None, db=db)

        assert exc.value.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert exc.value.detail["code"] == "INTERNAL_ERROR"
        assert "Authentication state corrupted" in exc.value.detail["message"]
        # DB must NOT be called when it's an API key corruption
        db.execute.assert_not_called()

    @pytest.mark.asyncio
    async def test_brand_id_set_does_not_raise_500(self):
        """auth_method=api_key with valid brand_id → normal flow (returns brand_id)."""
        req = _mock_request(
            brand_id="brand-001",
            auth_method="api_key",
            stored_brand_id="brand-001",  # Valid state
        )
        db = AsyncMock()

        result = await verify_brand_membership(req, user=None, db=db)
        assert result == "brand-001"


# ─── verify_brand_admin_access — API key path ─────────────────────────


class TestVerifyBrandAdminAccessApiKeyNoneGuard:
    """M-04: Defense-in-depth guard for None brand_id in admin API key path."""

    @pytest.mark.asyncio
    async def test_admin_brand_id_none_raises_500(self):
        """auth_method=api_key but brand_id is None → 500 for admin check too."""
        req = _mock_request(
            brand_id="brand-001",
            auth_method="api_key",
            stored_brand_id=None,
        )
        db = AsyncMock()

        with pytest.raises(HTTPException) as exc:
            await verify_brand_admin_access(req, user=None, db=db)

        assert exc.value.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert "Authentication state corrupted" in exc.value.detail["message"]
        db.execute.assert_not_called()

    @pytest.mark.asyncio
    async def test_admin_brand_id_set_success(self):
        """auth_method=api_key with valid brand_id → admin check returns brand_id."""
        req = _mock_request(
            brand_id="brand-001",
            auth_method="api_key",
            stored_brand_id="brand-001",
        )
        db = AsyncMock()

        result = await verify_brand_admin_access(req, user=None, db=db)
        assert result == "brand-001"


# ─── M-04 does NOT affect JWT path (no False positives) ────────────────


class TestVerifyBrandMembershipJwtStillWorks:
    """M-04 guard must not affect normal JWT authentication flow."""

    @pytest.mark.asyncio
    async def test_jwt_without_api_key_still_works(self):
        """JWT path without API key must still function normally."""
        req = _mock_request(
            brand_id="brand-001",
            auth_method=None,  # Not API key auth
            stored_brand_id=None,
        )
        user = MagicMock()
        user.id = "user-001"
        member = MagicMock()
        member.role = "member"
        db = _make_mock_db(member)

        result = await verify_brand_membership(req, user, db)
        assert result == "brand-001"

    @pytest.mark.asyncio
    async def test_jwt_no_user_raises_401(self):
        """JWT path with no user must still raise 401."""
        req = _mock_request("brand-001")
        db = AsyncMock()

        with pytest.raises(HTTPException) as exc:
            await verify_brand_membership(req, user=None, db=db)
        assert exc.value.status_code == status.HTTP_401_UNAUTHORIZED
