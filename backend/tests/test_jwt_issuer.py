"""Tests for JWT issuer verification (H-01).

Covers:
- Valid issuer (matches SUPABASE_URL prefix) passes through
- Missing iss field falls back to None
- Wrong iss (different domain) falls back to None
- Empty string iss falls back to None
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi import Request

from app.middleware.auth_middleware import AuthMiddleware


@pytest.fixture
def middleware():
    return AuthMiddleware(MagicMock())


@pytest.fixture
def mock_settings():
    """Return a settings object with a known SUPABASE_URL."""
    settings = MagicMock()
    settings.SUPABASE_URL = "https://supabase.vfs.ai"
    settings.JWT_SECRET = "test-secret"
    return settings


def _make_request(token: str = "fake-jwt-token", path: str = "/v1/generate/try-on") -> MagicMock:
    """Helper to build a mock request with a cookie token."""
    request = MagicMock(spec=Request)
    request.url.path = path
    request.method = "POST"
    request.state = MagicMock()
    request.state.auth_method = None
    request.cookies = {"vfs_access_token": token}
    request.headers = {}
    request.client = MagicMock()
    request.client.host = "1.2.3.4"
    return request


class TestJWTIssuer:

    @pytest.mark.asyncio
    async def test_valid_issuer_passes(self, middleware, mock_settings):
        """JWT with correct iss matching SUPABASE_URL must decode and set state."""
        request = _make_request()
        call_next = AsyncMock()
        call_next.return_value = "response"

        with patch("app.middleware.auth_middleware.get_settings", return_value=mock_settings), \
             patch("app.middleware.auth_middleware.jose_jwt.decode") as mock_decode:

            mock_decode.return_value = {
                "iss": "https://supabase.vfs.ai/auth/v1",
                "sub": "user-123",
                "plan": "pro",
            }

            result = await middleware.dispatch(request, call_next)

            assert result == "response"
            assert request.state.current_user_id == "user-123"
            assert request.state.current_user_plan == "pro"
            mock_decode.assert_called_once()

    @pytest.mark.asyncio
    async def test_missing_issuer_falls_back(self, middleware, mock_settings):
        """JWT with no iss field must raise ValueError caught by except block → current_user_id = None."""
        request = _make_request()
        call_next = AsyncMock()
        call_next.return_value = "response"

        with patch("app.middleware.auth_middleware.get_settings", return_value=mock_settings), \
             patch("app.middleware.auth_middleware.jose_jwt.decode") as mock_decode:

            mock_decode.return_value = {
                "sub": "user-123",
                "plan": "pro",
                # No "iss" key
            }

            result = await middleware.dispatch(request, call_next)

            assert result == "response"
            assert request.state.current_user_id is None
            assert request.state.current_user_plan == "free"

    @pytest.mark.asyncio
    async def test_wrong_issuer_falls_back(self, middleware, mock_settings):
        """JWT with iss not matching SUPABASE_URL prefix must fall back to None."""
        request = _make_request()
        call_next = AsyncMock()
        call_next.return_value = "response"

        with patch("app.middleware.auth_middleware.get_settings", return_value=mock_settings), \
             patch("app.middleware.auth_middleware.jose_jwt.decode") as mock_decode:

            mock_decode.return_value = {
                "iss": "https://evil-attacker.com",
                "sub": "user-999",
                "plan": "pro",
            }

            result = await middleware.dispatch(request, call_next)

            assert result == "response"
            assert request.state.current_user_id is None
            assert request.state.current_user_plan == "free"

    @pytest.mark.asyncio
    async def test_issuer_empty_string_falls_back(self, middleware, mock_settings):
        """JWT with iss='' must be treated as missing → fall back to None."""
        request = _make_request()
        call_next = AsyncMock()
        call_next.return_value = "response"

        with patch("app.middleware.auth_middleware.get_settings", return_value=mock_settings), \
             patch("app.middleware.auth_middleware.jose_jwt.decode") as mock_decode:

            mock_decode.return_value = {
                "iss": "",
                "sub": "user-123",
                "plan": "pro",
            }

            result = await middleware.dispatch(request, call_next)

            assert result == "response"
            assert request.state.current_user_id is None
            assert request.state.current_user_plan == "free"
