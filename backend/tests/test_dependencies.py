"""Tests for security dependencies: verify_brand_membership and verify_brand_admin_access.

Covers H-02: Catalog route restructuring with dual-mode (API key + JWT) auth.
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


# ─── verify_brand_membership — JWT path ────────────────────────────────


class TestVerifyBrandMembershipJWT:
    """JWT authentication path for verify_brand_membership."""

    @pytest.mark.asyncio
    async def test_valid_member(self):
        """Valid brand member must return brand_id."""
        req = _mock_request("brand-001")
        user = MagicMock()
        user.id = "user-001"

        mock_member = MagicMock()
        mock_member.role = "member"

        db = _make_mock_db(mock_member)

        result = await verify_brand_membership(req, user, db)
        assert result == "brand-001"

    @pytest.mark.asyncio
    async def test_valid_admin(self):
        """Brand admin must also pass membership check."""
        req = _mock_request("brand-001")
        user = MagicMock()
        user.id = "user-001"

        mock_member = MagicMock()
        mock_member.role = "admin"

        db = _make_mock_db(mock_member)

        result = await verify_brand_membership(req, user, db)
        assert result == "brand-001"

    @pytest.mark.asyncio
    async def test_non_member_raises_403(self):
        """User not in BrandMember table must get 403."""
        req = _mock_request("brand-001")
        user = MagicMock()
        user.id = "user-999"

        db = _make_mock_db(None)  # No membership found

        with pytest.raises(HTTPException) as exc:
            await verify_brand_membership(req, user, db)
        assert exc.value.status_code == status.HTTP_403_FORBIDDEN

    @pytest.mark.asyncio
    async def test_no_user_raises_401(self):
        """No authenticated user must get 401."""
        req = _mock_request("brand-001")
        user = None
        db = AsyncMock()

        with pytest.raises(HTTPException) as exc:
            await verify_brand_membership(req, user, db)
        assert exc.value.status_code == status.HTTP_401_UNAUTHORIZED

    @pytest.mark.asyncio
    async def test_missing_brand_id_raises_400(self):
        """Missing brand_id in path must get 400."""
        req = MagicMock()
        req.path_params = {}
        user = MagicMock()
        db = AsyncMock()

        with pytest.raises(HTTPException) as exc:
            await verify_brand_membership(req, user, db)
        assert exc.value.status_code == status.HTTP_400_BAD_REQUEST


# ─── verify_brand_membership — API key path ────────────────────────────


class TestVerifyBrandMembershipApiKey:
    """API key authentication path for verify_brand_membership."""

    @pytest.mark.asyncio
    async def test_api_key_valid(self):
        """API key for the correct brand must return brand_id."""
        req = _mock_request(
            brand_id="brand-001",
            auth_method="api_key",
            stored_brand_id="brand-001",
        )
        db = AsyncMock()  # No DB call expected in API key path

        result = await verify_brand_membership(req, user=None, db=db)
        assert result == "brand-001"

    @pytest.mark.asyncio
    async def test_api_key_wrong_brand_raises_403(self):
        """API key for a different brand must get 403."""
        req = _mock_request(
            brand_id="brand-001",
            auth_method="api_key",
            stored_brand_id="brand-002",  # Mismatch
        )
        db = AsyncMock()

        with pytest.raises(HTTPException) as exc:
            await verify_brand_membership(req, user=None, db=db)
        assert exc.value.status_code == status.HTTP_403_FORBIDDEN

    @pytest.mark.asyncio
    async def test_api_key_no_stored_brand_raises_403(self):
        """API key with no stored brand_id must get 403."""
        req = _mock_request(
            brand_id="brand-001",
            auth_method="api_key",
            stored_brand_id=None,  # Not set
        )
        db = AsyncMock()

        with pytest.raises(HTTPException) as exc:
            await verify_brand_membership(req, user=None, db=db)
        assert exc.value.status_code == status.HTTP_403_FORBIDDEN


# ─── verify_brand_admin_access — JWT path ──────────────────────────────


class TestVerifyBrandAdminAccessJWT:
    """JWT authentication path for verify_brand_admin_access."""

    @pytest.mark.asyncio
    async def test_admin_success(self):
        """Brand admin must return brand_id."""
        req = _mock_request("brand-001")
        user = MagicMock()
        user.id = "user-001"

        mock_member = MagicMock()
        mock_member.role = "admin"

        db = _make_mock_db(mock_member)

        result = await verify_brand_admin_access(req, user, db)
        assert result == "brand-001"

    @pytest.mark.asyncio
    async def test_non_admin_member_raises_403(self):
        """Non-admin brand member must get 403.
        
        The SQL query filters by role='admin', so a non-admin member's
        record doesn't match the query → scalar_one_or_none returns None.
        """
        req = _mock_request("brand-001")
        user = MagicMock()
        user.id = "user-001"

        # The query includes role='admin' filter, so a member with
        # role='member' won't be returned by the actual DB query.
        db = _make_mock_db(None)

        with pytest.raises(HTTPException) as exc:
            await verify_brand_admin_access(req, user, db)
        assert exc.value.status_code == status.HTTP_403_FORBIDDEN

    @pytest.mark.asyncio
    async def test_no_member_record_raises_403(self):
        """User with no BrandMember record must get 403."""
        req = _mock_request("brand-001")
        user = MagicMock()
        user.id = "user-999"

        db = _make_mock_db(None)

        with pytest.raises(HTTPException) as exc:
            await verify_brand_admin_access(req, user, db)
        assert exc.value.status_code == status.HTTP_403_FORBIDDEN

    @pytest.mark.asyncio
    async def test_no_user_raises_401(self):
        """No authenticated user must get 401."""
        req = _mock_request("brand-001")
        user = None
        db = AsyncMock()

        with pytest.raises(HTTPException) as exc:
            await verify_brand_admin_access(req, user, db)
        assert exc.value.status_code == status.HTTP_401_UNAUTHORIZED

    @pytest.mark.asyncio
    async def test_missing_brand_id_raises_400(self):
        """Missing brand_id in path must get 400."""
        req = MagicMock()
        req.path_params = {}
        user = MagicMock()
        db = AsyncMock()

        with pytest.raises(HTTPException) as exc:
            await verify_brand_admin_access(req, user, db)
        assert exc.value.status_code == status.HTTP_400_BAD_REQUEST


# ─── verify_brand_admin_access — API key path ──────────────────────────


class TestVerifyBrandAdminAccessApiKey:
    """API key authentication path for verify_brand_admin_access."""

    @pytest.mark.asyncio
    async def test_api_key_valid(self):
        """API key for the correct brand must return brand_id."""
        req = _mock_request(
            brand_id="brand-001",
            auth_method="api_key",
            stored_brand_id="brand-001",
        )
        db = AsyncMock()

        result = await verify_brand_admin_access(req, user=None, db=db)
        assert result == "brand-001"

    @pytest.mark.asyncio
    async def test_api_key_wrong_brand_raises_403(self):
        """API key for a different brand must get 403."""
        req = _mock_request(
            brand_id="brand-001",
            auth_method="api_key",
            stored_brand_id="brand-002",
        )
        db = AsyncMock()

        with pytest.raises(HTTPException) as exc:
            await verify_brand_admin_access(req, user=None, db=db)
        assert exc.value.status_code == status.HTTP_403_FORBIDDEN

    @pytest.mark.asyncio
    async def test_api_key_no_stored_brand_raises_403(self):
        """API key with no stored brand_id must get 403."""
        req = _mock_request(
            brand_id="brand-001",
            auth_method="api_key",
            stored_brand_id=None,
        )
        db = AsyncMock()

        with pytest.raises(HTTPException) as exc:
            await verify_brand_admin_access(req, user=None, db=db)
        assert exc.value.status_code == status.HTTP_403_FORBIDDEN
