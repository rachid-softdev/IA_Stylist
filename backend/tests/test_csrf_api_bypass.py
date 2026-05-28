"""Tests for CSRF API key bypass (C-04).

Covers:
- X-API-Key header skips CSRF validation for state-changing methods
- No X-API-Key still requires CSRF validation (POST blocked)
- GET methods pass CSRF regardless of API key presence
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi import Request

from app.middleware.csrf_middleware import CSRFMiddleware


@pytest.fixture
def middleware():
    return CSRFMiddleware(MagicMock())


class TestCSRFApiBypass:
    """CSRF middleware skips validation when X-API-Key is present."""

    @pytest.mark.asyncio
    async def test_api_key_bypasses_csrf(self, middleware):
        """Request with X-API-Key header skips CSRF validation
        even for state-changing methods (POST, PUT, etc)."""
        request = MagicMock(spec=Request)
        request.url.path = "/v1/brands/me"
        request.method = "PUT"
        request.headers = {"X-API-Key": "vfs_live_testkey123"}
        request.cookies = {}

        call_next = AsyncMock()
        call_next.return_value = "response"

        with patch("app.middleware.csrf_middleware.validate_csrf_token") as mock_validate:
            result = await middleware.dispatch(request, call_next)
            assert result == "response"
            # validate_csrf_token must NOT be called (bypassed)
            mock_validate.assert_not_called()

    @pytest.mark.asyncio
    async def test_no_api_key_still_requires_csrf(self, middleware):
        """POST without X-API-Key still requires CSRF validation.
        Without valid CSRF, the request is blocked with 403."""
        request = MagicMock(spec=Request)
        request.url.path = "/v1/brands/me"
        request.method = "POST"
        request.headers = {}  # No API key
        request.cookies = {}

        call_next = AsyncMock()

        # When no CSRF token is present, validate_csrf_token("", "") returns False
        result = await middleware.dispatch(request, call_next)
        assert result.status_code == 403
        content = result.body
        assert "CSRF_FAILED" in str(content)
        call_next.assert_not_called()

    @pytest.mark.asyncio
    async def test_get_methods_not_affected(self, middleware):
        """GET requests pass CSRF regardless of API key presence."""
        # Without API key
        request = MagicMock(spec=Request)
        request.url.path = "/v1/brands/me"
        request.method = "GET"
        request.headers = {}
        request.cookies = {}

        call_next = AsyncMock()
        response_mock = MagicMock()
        call_next.return_value = response_mock

        # GET is safe, so CSRF is skipped
        result = await middleware.dispatch(request, call_next)
        assert result == response_mock

        # With API key
        request2 = MagicMock(spec=Request)
        request2.url.path = "/v1/brands/me"
        request2.method = "GET"
        request2.headers = {"X-API-Key": "vfs_live_testkey"}
        request2.cookies = {}

        call_next2 = AsyncMock()
        response_mock2 = MagicMock()
        call_next2.return_value = response_mock2

        result2 = await middleware.dispatch(request2, call_next2)
        assert result2 == response_mock2

    @pytest.mark.asyncio
    async def test_api_key_bypass_with_valid_csrf_still_bypasses(self, middleware):
        """Even if valid CSRF tokens exist, X-API-Key still bypasses CSRF.
        The bypass happens before any CSRF validation."""
        request = MagicMock(spec=Request)
        request.url.path = "/v1/brands/me"
        request.method = "DELETE"
        request.headers = {"X-API-Key": "vfs_live_testkey"}
        # Even with invalid CSRF, API key bypasses
        request.cookies = {"csrf_token": "invalid.signed"}
        request.headers = {"X-API-Key": "vfs_live_testkey", "X-CSRF-Token": "wrong-token"}

        call_next = AsyncMock()
        call_next.return_value = "response"

        with patch("app.middleware.csrf_middleware.validate_csrf_token") as mock_validate:
            result = await middleware.dispatch(request, call_next)
            assert result == "response"
            mock_validate.assert_not_called()

    @pytest.mark.asyncio
    async def test_exempt_routes_still_exempt_without_api_key(self, middleware):
        """Exempt routes (like /v1/webhooks/) pass CSRF without API key."""
        request = MagicMock(spec=Request)
        request.url.path = "/v1/webhooks/stripe"
        request.method = "POST"
        request.headers = {}  # No API key
        request.cookies = {}

        call_next = AsyncMock()
        call_next.return_value = "response"

        result = await middleware.dispatch(request, call_next)
        assert result == "response"
