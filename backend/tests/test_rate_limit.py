"""Tests for per-user rate limiting (C-01).

Covers:
- Per-user Redis key format (rate:{user_id}:{plan}:{hour})
- IP fallback when user_id is None
- X-Forwarded-For header fallback
- Separate counters for different users
- HTTP 429 when limit exceeded
- Non-API routes skipped
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi import Request, HTTPException, status

from app.middleware.rate_limit import RateLimitMiddleware


@pytest.fixture
def middleware():
    return RateLimitMiddleware(MagicMock())


class TestRateLimitKey:
    """Verify Redis key construction uses correct user identifier."""

    @pytest.mark.asyncio
    async def test_per_user_rate_limit_key(self, middleware):
        """Mock request.state.current_user_id to 'user_123',
        verify the Redis key contains 'user_123'."""
        request = MagicMock(spec=Request)
        request.url.path = "/v1/generate/try-on"
        request.method = "POST"
        request.state.current_user_id = "user_123"
        request.state.current_user_plan = "free"
        request.headers = {}
        request.client = MagicMock()
        request.client.host = "1.2.3.4"

        mock_redis = AsyncMock()
        mock_redis.incr.return_value = 1

        call_next = AsyncMock()

        with patch("app.middleware.rate_limit.get_redis", return_value=mock_redis):
            await middleware.dispatch(request, call_next)

        call_args = mock_redis.incr.call_args
        assert call_args is not None
        key = call_args[0][0]
        assert "user_123" in key, f"Expected key to contain 'user_123', got: {key}"
        assert key.startswith("rate:user_123:")

    @pytest.mark.asyncio
    async def test_rate_limit_key_without_user_id(self, middleware):
        """When current_user_id is None, verify fallback uses IP."""
        request = MagicMock(spec=Request)
        request.url.path = "/v1/generate/try-on"
        request.method = "POST"
        request.state.current_user_id = None
        request.state.current_user_plan = "free"
        request.headers = {}
        request.client = MagicMock()
        request.client.host = "10.0.0.5"

        mock_redis = AsyncMock()
        mock_redis.incr.return_value = 1

        call_next = AsyncMock()

        with patch("app.middleware.rate_limit.get_redis", return_value=mock_redis):
            await middleware.dispatch(request, call_next)

        call_args = mock_redis.incr.call_args
        assert call_args is not None
        key = call_args[0][0]
        assert "10.0.0.5" in key, f"Expected key to contain IP, got: {key}"
        assert key.startswith("rate:10.0.0.5:")

    @pytest.mark.asyncio
    async def test_rate_limit_key_forwarded_for(self, middleware):
        """When X-Forwarded-For header is present, verify it's used."""
        request = MagicMock(spec=Request)
        request.url.path = "/v1/generate/try-on"
        request.method = "POST"
        request.state.current_user_id = None
        request.state.current_user_plan = "free"
        request.headers = {"X-Forwarded-For": "203.0.113.5, 10.0.0.1"}
        request.client = MagicMock()
        request.client.host = "10.0.0.2"

        mock_redis = AsyncMock()
        mock_redis.incr.return_value = 1

        call_next = AsyncMock()

        with patch("app.middleware.rate_limit.get_redis", return_value=mock_redis):
            await middleware.dispatch(request, call_next)

        call_args = mock_redis.incr.call_args
        assert call_args is not None
        key = call_args[0][0]
        assert "203.0.113.5" in key, f"Expected key to contain X-Forwarded-For IP, got: {key}"
        assert key.startswith("rate:203.0.113.5:")

    @pytest.mark.asyncio
    async def test_different_users_have_separate_counters(self, middleware):
        """Simulate two different user_ids, verify they get different keys."""
        mock_redis = AsyncMock()
        mock_redis.incr.side_effect = [1, 1]

        call_next = AsyncMock()

        keys = []
        user_ids = ["user_alpha", "user_beta"]

        with patch("app.middleware.rate_limit.get_redis", return_value=mock_redis):
            for uid in user_ids:
                request = MagicMock(spec=Request)
                request.url.path = "/v1/generate/try-on"
                request.method = "POST"
                request.state.current_user_id = uid
                request.state.current_user_plan = "free"
                request.headers = {}
                request.client = MagicMock()
                request.client.host = "1.2.3.4"

                await middleware.dispatch(request, call_next)

                call_args = mock_redis.incr.call_args
                assert call_args is not None
                keys.append(call_args[0][0])

        assert keys[0] != keys[1], f"Expected different keys, got same: {keys[0]}"
        assert "user_alpha" in keys[0]
        assert "user_beta" in keys[1]

    @pytest.mark.asyncio
    async def test_rate_limit_blocking(self, middleware):
        """When counter exceeds limit, verify HTTP 429 is raised."""
        request = MagicMock(spec=Request)
        request.url.path = "/v1/generate/try-on"
        request.method = "POST"
        request.state.current_user_id = "user_123"
        request.state.current_user_plan = "free"
        request.headers = {}
        request.client = MagicMock()
        request.client.host = "1.2.3.4"

        mock_redis = AsyncMock()
        mock_redis.incr.return_value = 999

        call_next = AsyncMock()

        with patch("app.middleware.rate_limit.get_redis", return_value=mock_redis):
            with pytest.raises(HTTPException) as exc:
                await middleware.dispatch(request, call_next)

            assert exc.value.status_code == status.HTTP_429_TOO_MANY_REQUESTS
            detail = exc.value.detail
            assert detail["code"] == "RATE_LIMITED"

    @pytest.mark.asyncio
    async def test_non_api_route_skips_rate_limit(self, middleware):
        """Non-/v1 routes must skip rate limiting entirely."""
        request = MagicMock(spec=Request)
        request.url.path = "/health"
        request.method = "GET"

        call_next = AsyncMock()
        call_next.return_value = "response"

        with patch("app.middleware.rate_limit.get_redis") as mock_get_redis:
            result = await middleware.dispatch(request, call_next)
            assert result == "response"
            mock_get_redis.assert_not_called()
