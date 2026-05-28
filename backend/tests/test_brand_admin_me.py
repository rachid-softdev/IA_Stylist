"""Tests for Brand GET/PUT /me admin authorization (H-02).

Covers:
- GET /me requires admin role (member → 403)
- GET /me allows admin role (admin → 200)
- PUT /me requires admin role (member → 403)
- PUT /me allows admin update (admin → 200, brand updated)
- No brand membership returns 403
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi import HTTPException, status
from datetime import datetime

from app.dependencies import get_current_brand_admin_me


class TestGetCurrentBrandAdminMeFunction:
    """Direct unit tests for get_current_brand_admin_me dependency logic."""

    @pytest.mark.asyncio
    async def test_get_current_brand_admin_me_success(self):
        """Brand admin user must return (user, brand) tuple."""
        request = MagicMock()
        request.path_params = {}

        user = MagicMock()
        user.id = "user-admin-001"

        mock_brand = MagicMock()
        mock_brand.id = "brand-001"
        mock_brand.name = "Test Brand"

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_brand

        mock_db = AsyncMock()
        mock_db.execute.return_value = mock_result

        result = await get_current_brand_admin_me(request, user, mock_db)
        assert result == (user, mock_brand)

    @pytest.mark.asyncio
    async def test_get_current_brand_admin_me_non_admin(self):
        """Non-admin brand member must be rejected with 403."""
        request = MagicMock()
        request.path_params = {}

        user = MagicMock()
        user.id = "user-member-001"

        # No admin membership found
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None

        mock_db = AsyncMock()
        mock_db.execute.return_value = mock_result

        with pytest.raises(HTTPException) as exc:
            await get_current_brand_admin_me(request, user, mock_db)
        assert exc.value.status_code == status.HTTP_403_FORBIDDEN

    @pytest.mark.asyncio
    async def test_get_current_brand_admin_me_no_brand(self):
        """User with no brand membership at all must get 403."""
        request = MagicMock()
        request.path_params = {}

        user = MagicMock()
        user.id = "user-nobrand-001"

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None

        mock_db = AsyncMock()
        mock_db.execute.return_value = mock_result

        with pytest.raises(HTTPException) as exc:
            await get_current_brand_admin_me(request, user, mock_db)
        assert exc.value.status_code == status.HTTP_403_FORBIDDEN
        assert exc.value.detail["code"] == "FORBIDDEN"


class TestBrandMeEndpoints:
    """Integration tests for GET/PUT /v1/brands/me via TestClient.

    NOTE: ApiKeyMiddleware blocks /v1/brands/* routes without X-API-Key.
    We patch _authenticate to always succeed and include X-API-Key in headers.
    When X-API-Key is present, CSRF middleware skips validation (C-04),
    so PUT requests don't need CSRF tokens.
    """

    TEST_API_KEY = "vfs_live_test_admin_key_001"

    @pytest.fixture(autouse=True)
    def setup_overrides(self):
        """Clear dependency overrides before and after each test."""
        from app.main import app
        from app.dependencies import get_current_brand_admin_me, get_current_user

        self._app = app
        yield
        app.dependency_overrides.clear()

    def _make_admin_override(self):
        """Create override that returns (user, brand) for admin."""
        from app.models.user import User

        mock_user = MagicMock(spec=User)
        mock_user.id = "admin-user-001"
        mock_user.email = "admin@test.com"
        mock_user.plan = "starter"
        mock_user.credits = 500

        mock_brand = MagicMock()
        mock_brand.id = "brand-admin-001"
        mock_brand.name = "Admin Brand"
        mock_brand.plan = "starter"
        mock_brand.credits = 500
        mock_brand.tenant_id = "tenant-001"
        mock_brand.created_at = datetime(2025, 1, 1)
        mock_brand.shopify_url = None

        return mock_user, mock_brand

    def _make_forbidden_override(self):
        """Create override that raises 403."""
        async def _raise():
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "code": "FORBIDDEN",
                    "message": "Brand admin access required",
                },
            )
        return _raise

    async def _make_request(self, client, method, path, **kwargs):
        """Make an HTTP request with X-API-Key header and patched auth."""
        from app.middleware.api_key import ApiKeyMiddleware

        headers = kwargs.pop("headers", {})
        headers.setdefault("X-API-Key", self.TEST_API_KEY)

        with patch.object(
            ApiKeyMiddleware, "_authenticate",
            new_callable=AsyncMock,
            return_value=("brand-admin-001", "starter"),
        ):
            response = await client.request(method, path, headers=headers, **kwargs)
        return response

    @pytest.mark.asyncio
    async def test_get_me_requires_admin(self, client):
        """A brand member with role='member' gets 403."""
        from app.dependencies import get_current_brand_admin_me

        self._app.dependency_overrides[get_current_brand_admin_me] = self._make_forbidden_override()

        try:
            response = await self._make_request(client, "GET", "/v1/brands/me")
            assert response.status_code == 403
            data = response.json()
            # FastAPI formats HTTPException detail as {"detail": {...}}
            detail = data.get("detail", data.get("error", {}))
            assert detail["code"] == "FORBIDDEN"
        finally:
            self._app.dependency_overrides.clear()

    @pytest.mark.asyncio
    async def test_get_me_allows_admin(self, client):
        """A brand member with role='admin' gets 200."""
        from app.dependencies import get_current_brand_admin_me

        mock_user, mock_brand = self._make_admin_override()
        self._app.dependency_overrides[get_current_brand_admin_me] = lambda: (mock_user, mock_brand)

        try:
            response = await self._make_request(client, "GET", "/v1/brands/me")
            assert response.status_code == 200
            data = response.json()
            assert data["name"] == "Admin Brand"
        finally:
            self._app.dependency_overrides.clear()

    @pytest.mark.asyncio
    async def test_put_me_requires_admin(self, client):
        """A member tries to update brand -> 403."""
        from app.dependencies import get_current_brand_admin_me

        self._app.dependency_overrides[get_current_brand_admin_me] = self._make_forbidden_override()

        try:
            response = await self._make_request(
                client, "PUT", "/v1/brands/me",
                json={"name": "Hacked Brand Name"},
            )
            assert response.status_code == 403
            data = response.json()
            # FastAPI formats HTTPException detail as {"detail": {...}}
            detail = data.get("detail", data.get("error", {}))
            assert detail["code"] == "FORBIDDEN"
        finally:
            self._app.dependency_overrides.clear()

    @pytest.mark.asyncio
    async def test_put_me_allows_admin(self, client):
        """An admin updates brand name -> 200 and brand updated."""
        from app.dependencies import get_current_brand_admin_me, get_db

        mock_user, mock_brand = self._make_admin_override()

        # Mock DB for the commit/refresh in the handler
        mock_db = AsyncMock()
        mock_db.commit.return_value = None
        mock_db.refresh.return_value = None

        async def _override_db():
            yield mock_db

        self._app.dependency_overrides[get_current_brand_admin_me] = lambda: (mock_user, mock_brand)
        self._app.dependency_overrides[get_db] = _override_db

        try:
            response = await self._make_request(
                client, "PUT", "/v1/brands/me",
                json={"name": "Updated Brand Name"},
            )
            assert response.status_code == 200
            data = response.json()
            # The mock brand was updated in-place by the handler
            assert mock_brand.name == "Updated Brand Name"
        finally:
            self._app.dependency_overrides.clear()

    @pytest.mark.asyncio
    async def test_no_brand_returns_403(self, client):
        """A user with no brand membership gets 403.
        Note: get_current_brand_admin_me returns 403 for no brand found,
        which is the current implementation."""
        from app.dependencies import get_current_brand_admin_me

        self._app.dependency_overrides[get_current_brand_admin_me] = self._make_forbidden_override()

        try:
            response = await self._make_request(client, "GET", "/v1/brands/me")
            assert response.status_code == 403
            data = response.json()
            # FastAPI formats HTTPException detail as {"detail": {...}}
            detail = data.get("detail", data.get("error", {}))
            assert detail["code"] == "FORBIDDEN"
        finally:
            self._app.dependency_overrides.clear()
