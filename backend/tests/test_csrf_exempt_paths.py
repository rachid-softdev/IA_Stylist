"""Tests for narrow CSRF webhook exemption (M-02).

Verifies that only the exact path /v1/webhooks/stripe is exempt from CSRF
validation (not a generic /v1/webhooks/* prefix). Auth /v1/auth/ prefix
remains exempt.
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi import Request

from app.middleware.csrf_middleware import CSRFMiddleware, EXEMPT_PATHS, EXEMPT_PREFIXES


class TestCSRFExemptConfig:
    """Verify EXEMPT_PATHS and EXEMPT_PREFIXES configuration."""

    def test_webhook_stripe_exact_path_is_exempt(self):
        """Stripe webhook exact path must be in EXEMPT_PATHS."""
        assert "/v1/webhooks/stripe" in EXEMPT_PATHS

    def test_webhooks_prefix_not_in_exempt_prefixes(self):
        """Generic /v1/webhooks/ prefix must NOT be in EXEMPT_PREFIXES (M-02)."""
        assert "/v1/webhooks/" not in EXEMPT_PREFIXES

    def test_auth_prefix_still_exempt(self):
        """Auth prefix must remain in EXEMPT_PREFIXES."""
        assert "/v1/auth/" in EXEMPT_PREFIXES

    def test_health_still_exempt(self):
        """Health endpoint must remain in EXEMPT_PATHS."""
        assert "/health" in EXEMPT_PATHS


@pytest.fixture
def middleware():
    """Create a CSRFMiddleware instance for dispatch testing."""
    return CSRFMiddleware(MagicMock())


class TestCSRFExemptDispatch:
    """Test dispatch logic for exempt vs non-exempt paths."""

    @pytest.mark.asyncio
    async def test_webhook_stripe_exempt(self, middleware):
        """POST to /v1/webhooks/stripe must skip CSRF validation.

        validate_csrf_token must NOT be called for this exact path.
        """
        request = MagicMock(spec=Request)
        request.url.path = "/v1/webhooks/stripe"
        request.method = "POST"
        request.headers = {}
        request.cookies = {}

        call_next = AsyncMock()
        call_next.return_value = "response"

        with patch("app.middleware.csrf_middleware.validate_csrf_token") as mock_validate:
            result = await middleware.dispatch(request, call_next)
            assert result == "response"
            mock_validate.assert_not_called()

    @pytest.mark.asyncio
    async def test_other_webhook_not_exempt(self, middleware):
        """POST to /v1/webhooks/other must NOT skip CSRF validation.

        Without /v1/webhooks/ prefix exemption, non-stripe webhook paths
        require CSRF validation.
        """
        request = MagicMock(spec=Request)
        request.url.path = "/v1/webhooks/other"
        request.method = "POST"
        request.headers = {}
        request.cookies = {}

        call_next = AsyncMock()

        with patch("app.middleware.csrf_middleware.validate_csrf_token") as mock_validate:
            mock_validate.return_value = False
            result = await middleware.dispatch(request, call_next)
            assert result.status_code == 403
            mock_validate.assert_called_once()

    @pytest.mark.asyncio
    async def test_other_webhook_with_valid_csrf_passes(self, middleware):
        """POST to /v1/webhooks/other with valid CSRF token must pass."""
        request = MagicMock(spec=Request)
        request.url.path = "/v1/webhooks/other"
        request.method = "POST"
        request.headers = {}
        request.cookies = {}

        call_next = AsyncMock()
        call_next.return_value = "response"

        with patch("app.middleware.csrf_middleware.validate_csrf_token") as mock_validate:
            mock_validate.return_value = True
            result = await middleware.dispatch(request, call_next)
            assert result == "response"
            mock_validate.assert_called_once()

    @pytest.mark.asyncio
    async def test_auth_exempt_still_works(self, middleware):
        """POST to /v1/auth/login must still skip CSRF validation (prefix exempt).

        The auth prefix exemption must remain functional alongside
        the new narrow webhook exemption.
        """
        request = MagicMock(spec=Request)
        request.url.path = "/v1/auth/login"
        request.method = "POST"
        request.headers = {}
        request.cookies = {}

        call_next = AsyncMock()
        call_next.return_value = "response"

        with patch("app.middleware.csrf_middleware.validate_csrf_token") as mock_validate:
            result = await middleware.dispatch(request, call_next)
            assert result == "response"
            mock_validate.assert_not_called()

    @pytest.mark.asyncio
    async def test_health_exempt(self, middleware):
        """POST to /health must skip CSRF validation."""
        request = MagicMock(spec=Request)
        request.url.path = "/health"
        request.method = "POST"
        request.headers = {}
        request.cookies = {}

        call_next = AsyncMock()
        call_next.return_value = "response"

        with patch("app.middleware.csrf_middleware.validate_csrf_token") as mock_validate:
            result = await middleware.dispatch(request, call_next)
            assert result == "response"
            mock_validate.assert_not_called()

    @pytest.mark.asyncio
    async def test_non_exempt_path_still_blocks(self, middleware):
        """POST to a non-exempt path without CSRF must be blocked.

        Verifies that only specific paths are exempt — all others still
        require CSRF validation.
        """
        request = MagicMock(spec=Request)
        request.url.path = "/v1/brands/me"
        request.method = "POST"
        request.headers = {}
        request.cookies = {}

        call_next = AsyncMock()

        with patch("app.middleware.csrf_middleware.validate_csrf_token") as mock_validate:
            mock_validate.return_value = False
            result = await middleware.dispatch(request, call_next)
            assert result.status_code == 403
