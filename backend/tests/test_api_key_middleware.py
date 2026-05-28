"""Tests for ApiKeyMiddleware (H-06).

Covers:
- Missing X-API-Key on /v1/brands/* returns 401
- Missing X-API-Key on /v1/catalog/* returns 401
- Missing X-API-Key on /v1/generate/* passes through (dual auth)
- Invalid API key returns 401
- Expired API key detection
- Valid API key sets request.state correctly
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi import Request, HTTPException, status
from starlette.middleware.base import RequestResponseEndpoint

from app.middleware.api_key import ApiKeyMiddleware, API_KEY_ROUTE_PREFIXES, DUAL_AUTH_ROUTE_PREFIXES


# ─── Route classification tests ──────────────────────────────────────────


class TestRouteClassification:
    """Verify API_KEY_ROUTE_PREFIXES and DUAL_AUTH_ROUTE_PREFIXES constants."""

    def test_brands_route_is_api_key_primary(self):
        assert "/v1/brands/" in API_KEY_ROUTE_PREFIXES

    def test_catalog_route_is_api_key_primary(self):
        assert "/v1/catalog/" in API_KEY_ROUTE_PREFIXES

    def test_generate_route_is_dual_auth(self):
        assert "/v1/generate/" in DUAL_AUTH_ROUTE_PREFIXES


# ─── Middleware dispatch tests (mocked _authenticate) ───────────────────


@pytest.mark.asyncio
async def test_missing_api_key_on_brands_returns_401():
    """GET /v1/brands/ without X-API-Key must return 401."""
    middleware = ApiKeyMiddleware(MagicMock())

    request = MagicMock(spec=Request)
    request.url.path = "/v1/brands/some-brand/members"
    request.method = "GET"
    request.headers = {}  # No X-API-Key
    request.state = MagicMock()

    # _authenticate is never called when key is missing
    with patch.object(middleware, "_authenticate") as mock_auth:
        with pytest.raises(HTTPException) as exc:
            await middleware.dispatch(request, AsyncMock())
        assert exc.value.status_code == status.HTTP_401_UNAUTHORIZED
        assert exc.value.detail["code"] == "API_KEY_REQUIRED"
        mock_auth.assert_not_called()


@pytest.mark.asyncio
async def test_missing_api_key_on_catalog_returns_401():
    """GET /v1/catalog/ without X-API-Key must return 401."""
    middleware = ApiKeyMiddleware(MagicMock())

    request = MagicMock(spec=Request)
    request.url.path = "/v1/catalog/brand-001/garments"
    request.method = "GET"
    request.headers = {}
    request.state = MagicMock()

    with patch.object(middleware, "_authenticate") as mock_auth:
        with pytest.raises(HTTPException) as exc:
            await middleware.dispatch(request, AsyncMock())
        assert exc.value.status_code == status.HTTP_401_UNAUTHORIZED
        assert exc.value.detail["code"] == "API_KEY_REQUIRED"
        mock_auth.assert_not_called()


@pytest.mark.asyncio
async def test_missing_api_key_on_generate_passes_through():
    """GET /v1/generate/ without X-API-Key must pass through (dual auth)."""
    middleware = ApiKeyMiddleware(MagicMock())

    request = MagicMock(spec=Request)
    request.url.path = "/v1/generate/try-on"
    request.method = "GET"
    request.headers = {}
    request.state = MagicMock()

    call_next = AsyncMock()
    call_next.return_value = "response"

    with patch.object(middleware, "_authenticate") as mock_auth:
        result = await middleware.dispatch(request, call_next)
        assert result == "response"
        mock_auth.assert_not_called()


@pytest.mark.asyncio
async def test_non_v1_route_passes_through():
    """Routes outside /v1/ must pass through without API key check."""
    middleware = ApiKeyMiddleware(MagicMock())

    request = MagicMock(spec=Request)
    request.url.path = "/health"
    request.method = "GET"
    request.state = MagicMock()

    call_next = AsyncMock()
    call_next.return_value = "response"

    with patch.object(middleware, "_authenticate") as mock_auth:
        result = await middleware.dispatch(request, call_next)
        assert result == "response"
        mock_auth.assert_not_called()


@pytest.mark.asyncio
async def test_options_preflight_passes_through():
    """OPTIONS preflight must bypass API key check."""
    middleware = ApiKeyMiddleware(MagicMock())

    request = MagicMock(spec=Request)
    request.url.path = "/v1/brands/something"
    request.method = "OPTIONS"
    request.state = MagicMock()

    call_next = AsyncMock()
    call_next.return_value = "response"

    with patch.object(middleware, "_authenticate") as mock_auth:
        result = await middleware.dispatch(request, call_next)
        assert result == "response"
        mock_auth.assert_not_called()


@pytest.mark.asyncio
async def test_invalid_api_key_returns_401():
    """X-API-Key that fails authentication must return 401."""
    middleware = ApiKeyMiddleware(MagicMock())

    request = MagicMock(spec=Request)
    request.url.path = "/v1/brands/some-brand/members"
    request.method = "GET"
    request.headers = {"X-API-Key": "vfs_live_invalidkey"}
    request.state = MagicMock()

    with patch.object(middleware, "_authenticate", new_callable=AsyncMock) as mock_auth:
        mock_auth.return_value = None  # Authentication failed
        with pytest.raises(HTTPException) as exc:
            await middleware.dispatch(request, AsyncMock())
        assert exc.value.status_code == status.HTTP_401_UNAUTHORIZED
        assert exc.value.detail["code"] == "INVALID_API_KEY"


@pytest.mark.asyncio
async def test_valid_api_key_sets_request_state():
    """Valid API key must set request.state fields and call next."""
    middleware = ApiKeyMiddleware(MagicMock())

    request = MagicMock(spec=Request)
    request.url.path = "/v1/brands/brand-001/members"
    request.method = "GET"
    request.headers = {"X-API-Key": "vfs_live_validkey123"}
    request.state = MagicMock()

    call_next = AsyncMock()
    call_next.return_value = "response"

    with patch.object(middleware, "_authenticate", new_callable=AsyncMock) as mock_auth:
        mock_auth.return_value = ("brand-001", "starter")

        result = await middleware.dispatch(request, call_next)

        assert result == "response"
        assert request.state.current_user_id == "brand-001"
        assert request.state.current_user_plan == "starter"
        assert request.state.brand_id == "brand-001"
        assert request.state.auth_method == "api_key"
        mock_auth.assert_called_once_with("vfs_live_validkey123")


# ─── _authenticate method tests (mocked DB) ────────────────────────────


@pytest.mark.asyncio
async def test_authenticate_no_candidates():
    """_authenticate must return None when no API keys match the prefix."""
    middleware = ApiKeyMiddleware(MagicMock())

    with patch("app.middleware.api_key.async_session") as mock_session_factory:
        mock_session = AsyncMock()
        mock_session_factory.return_value.__aenter__.return_value = mock_session

        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = []  # No candidates
        mock_session.execute.return_value = mock_result

        result = await middleware._authenticate("vfs_live_unknownkey")
        assert result is None


@pytest.mark.asyncio
async def test_authenticate_candidates_no_match():
    """_authenticate must return None when no candidate key matches."""
    middleware = ApiKeyMiddleware(MagicMock())

    with patch("app.middleware.api_key.async_session") as mock_session_factory:
        mock_session = AsyncMock()
        mock_session_factory.return_value.__aenter__.return_value = mock_session

        # One candidate that doesn't match
        mock_candidate = MagicMock()
        mock_candidate.key_hash = "$2b$12$differenthashthatwontmatch"
        mock_candidate.brand_id = "brand-001"

        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [mock_candidate]
        mock_session.execute.return_value = mock_result

        # verify_api_key will try to parse the hash and fail -> return None
        result = await middleware._authenticate("vfs_live_somekey")
        assert result is None


@pytest.mark.asyncio
async def test_authenticate_matching_key():
    """_authenticate must return (brand_id, plan) for matching key."""
    middleware = ApiKeyMiddleware(MagicMock())

    with patch("app.middleware.api_key.async_session") as mock_session_factory, \
         patch("app.middleware.api_key.verify_api_key") as mock_verify:

        mock_verify.return_value = True  # Key matches

        mock_session = AsyncMock()
        mock_session_factory.return_value.__aenter__.return_value = mock_session

        # API key candidate
        mock_candidate = MagicMock()
        mock_candidate.key_hash = "somehash"
        mock_candidate.brand_id = "brand-001"

        mock_result_keys = MagicMock()
        mock_result_keys.scalars.return_value.all.return_value = [mock_candidate]
        mock_session.execute.return_value = mock_result_keys

        # Brand lookup
        mock_brand = MagicMock()
        mock_brand.plan = "growth"
        mock_result_brand = MagicMock()
        mock_result_brand.scalar_one_or_none.return_value = mock_brand

        # Second call to execute returns the brand
        mock_session.execute.side_effect = [mock_result_keys, mock_result_brand]

        result = await middleware._authenticate("vfs_live_validkey")
        assert result == ("brand-001", "growth")
        mock_candidate.last_used_at is not None  # Was updated
        mock_session.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_authenticate_brand_not_found_fallback_plan():
    """_authenticate must fall back to 'free' when brand not found."""
    middleware = ApiKeyMiddleware(MagicMock())

    with patch("app.middleware.api_key.async_session") as mock_session_factory, \
         patch("app.middleware.api_key.verify_api_key") as mock_verify:

        mock_verify.return_value = True

        mock_session = AsyncMock()
        mock_session_factory.return_value.__aenter__.return_value = mock_session

        mock_candidate = MagicMock()
        mock_candidate.key_hash = "hash"
        mock_candidate.brand_id = "brand-001"

        mock_result_keys = MagicMock()
        mock_result_keys.scalars.return_value.all.return_value = [mock_candidate]
        mock_session.execute.return_value = mock_result_keys

        # Brand not found
        mock_result_brand = MagicMock()
        mock_result_brand.scalar_one_or_none.return_value = None

        mock_session.execute.side_effect = [mock_result_keys, mock_result_brand]

        result = await middleware._authenticate("vfs_live_validkey")
        assert result == ("brand-001", "free")


@pytest.mark.asyncio
async def test_authenticate_expired_key():
    """Expired API key must not match (DB query excludes expired keys)."""
    middleware = ApiKeyMiddleware(MagicMock())

    with patch("app.middleware.api_key.async_session") as mock_session_factory:
        mock_session = AsyncMock()
        mock_session_factory.return_value.__aenter__.return_value = mock_session

        # No candidates returned because the query filters expired keys
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = []
        mock_session.execute.return_value = mock_result

        result = await middleware._authenticate("vfs_live_expiredkey")
        assert result is None


@pytest.mark.asyncio
async def test_authenticate_db_error_returns_none():
    """Database error during authentication must return None (not crash)."""
    middleware = ApiKeyMiddleware(MagicMock())

    with patch("app.middleware.api_key.async_session") as mock_session_factory:
        mock_session = AsyncMock()
        mock_session_factory.return_value.__aenter__.return_value = mock_session
        mock_session.execute.side_effect = Exception("DB connection error")

        result = await middleware._authenticate("vfs_live_errorkey")
        assert result is None
        mock_session.rollback.assert_awaited_once()
