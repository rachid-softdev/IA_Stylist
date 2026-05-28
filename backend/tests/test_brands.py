"""Tests for brands API endpoints and H-01 brand member authorization."""
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from fastapi import HTTPException, status
from app.main import app
from app.dependencies import get_current_brand_admin


@pytest.mark.asyncio
async def test_brands_endpoints_exist():
    """Verify new route paths work."""
    # Can't do full integration test without DB
    # Just verify the routes are registered
    routes = [route.path for route in app.routes]

    # Old paths should NOT exist anymore
    old_paths = [
        "/v1/brands/api-keys",
        "/v1/brands/members",
    ]
    for path in old_paths:
        assert path not in routes, f"Old path {path} should not exist"

    # New paths SHOULD exist
    new_paths = [
        "/v1/brands/{brand_id}/api-keys",
        "/v1/brands/{brand_id}/members",
        "/v1/brands/{brand_id}/api-keys/{key_id}",
        "/v1/brands/{brand_id}/members/{target_user_id}",
    ]
    for path in new_paths:
        assert path in routes, f"New path {path} should exist"


# ─── H-01: Brand admin authorization tests (mocked) ─────────────────────


def _make_mock_request(brand_id: str) -> MagicMock:
    """Create a mock Request with path_params."""
    req = MagicMock()
    req.path_params = {"brand_id": brand_id}
    req.state = MagicMock()
    return req


@pytest.mark.asyncio
async def test_get_current_brand_admin_success():
    """Brand admin user must pass get_current_brand_admin."""
    req = _make_mock_request("brand-001")
    user = MagicMock()
    user.id = "user-001"

    mock_member = MagicMock()
    mock_member.role = "admin"

    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = mock_member

    mock_db = AsyncMock()
    mock_db.execute.return_value = mock_result

    result = await get_current_brand_admin(req, user, mock_db)
    assert result == user


@pytest.mark.asyncio
async def test_get_current_brand_admin_forbidden_non_admin():
    """Non-admin brand member must be rejected with 403."""
    req = _make_mock_request("brand-001")
    user = MagicMock()
    user.id = "user-002"

    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None  # Not an admin

    mock_db = AsyncMock()
    mock_db.execute.return_value = mock_result

    with pytest.raises(HTTPException) as exc:
        await get_current_brand_admin(req, user, mock_db)
    assert exc.value.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.asyncio
async def test_get_current_brand_admin_missing_brand_id():
    """Missing brand_id in path must raise 400."""
    req = MagicMock()
    req.path_params = {}  # No brand_id
    user = MagicMock()
    mock_db = AsyncMock()

    with pytest.raises(HTTPException) as exc:
        await get_current_brand_admin(req, user, mock_db)
    assert exc.value.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.asyncio
async def test_get_current_brand_admin_not_member():
    """User with no BrandMember record must be rejected with 403."""
    req = _make_mock_request("brand-001")
    user = MagicMock()
    user.id = "user-003"

    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None

    mock_db = AsyncMock()
    mock_db.execute.return_value = mock_result

    with pytest.raises(HTTPException) as exc:
        await get_current_brand_admin(req, user, mock_db)
    assert exc.value.status_code == status.HTTP_403_FORBIDDEN
