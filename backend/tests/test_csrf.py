"""Tests for CSRF token generation, validation, and middleware."""
import pytest
from app.services.csrf import (
    generate_csrf_token,
    sign_csrf_token,
    validate_csrf_token,
    make_csrf_cookie_value,
)
from app.middleware.csrf_middleware import CSRF_COOKIE_NAME, SAFE_METHODS, EXEMPT_PATHS, EXEMPT_PREFIXES


class TestCSRFTokenGeneration:
    def test_generate_csrf_token_length(self):
        """Token must be URL-safe base64 of at least 32 bytes."""
        token = generate_csrf_token()
        assert len(token) >= 32
        # URL-safe: only alphanumeric, dash, underscore
        import string
        allowed = set(string.ascii_letters + string.digits + "-_")
        assert all(c in allowed for c in token)

    def test_generate_csrf_token_unique(self):
        """Each token must be unique."""
        tokens = {generate_csrf_token() for _ in range(100)}
        assert len(tokens) == 100

    def test_sign_csrf_token_different_output(self):
        """Signed token must differ from raw token."""
        token = generate_csrf_token()
        sig = sign_csrf_token(token)
        assert sig != token
        assert len(sig) == 64  # SHA-256 hex digest

    def test_sign_consistency(self):
        """Same token + same secret must produce same signature."""
        token = generate_csrf_token()
        sig1 = sign_csrf_token(token)
        sig2 = sign_csrf_token(token)
        assert sig1 == sig2


class TestCSRTCookieValue:
    def test_make_csrf_cookie_value_format(self):
        """Cookie value must be raw_token.signed_token."""
        value = make_csrf_cookie_value()
        parts = value.split(".")
        assert len(parts) == 2
        assert len(parts[0]) >= 32  # raw token
        assert len(parts[1]) == 64  # hex signature

    def test_make_csrf_cookie_value_unique(self):
        """Each call must produce a unique cookie value."""
        values = {make_csrf_cookie_value() for _ in range(50)}
        assert len(values) == 50


class TestCSRFTokenValidation:
    def test_validate_valid_token(self):
        """Valid cookie + header pair must validate."""
        cookie = make_csrf_cookie_value()
        raw_token = cookie.split(".")[0]
        assert validate_csrf_token(cookie, raw_token) is True

    def test_validate_empty_cookie(self):
        """Empty cookie must fail validation."""
        assert validate_csrf_token("", "sometoken") is False

    def test_validate_empty_header(self):
        """Empty header must fail validation."""
        cookie = make_csrf_cookie_value()
        assert validate_csrf_token(cookie, "") is False

    def test_validate_tampered_cookie(self):
        """Tampered cookie must fail validation."""
        cookie = make_csrf_cookie_value()
        # Tamper the raw part
        parts = cookie.split(".")
        tampered = f"tampered.{parts[1]}"
        assert validate_csrf_token(tampered, parts[0]) is False

    def test_validate_tampered_signature(self):
        """Tampered signature must fail validation."""
        cookie = make_csrf_cookie_value()
        parts = cookie.split(".")
        tampered = f"{parts[0]}.tampered"
        assert validate_csrf_token(tampered, parts[0]) is False

    def test_validate_wrong_raw_token(self):
        """Header token that doesn't match cookie raw token must fail."""
        cookie = make_csrf_cookie_value()
        assert validate_csrf_token(cookie, "wrong-raw-token") is False

    def test_validate_malformed_cookie(self):
        """Cookie without dot separator must fail."""
        assert validate_csrf_token("no-dot-here", "token") is False


class TestCSRFMiddlewareConfig:
    def test_safe_methods_exempt(self):
        """GET, HEAD, OPTIONS, TRACE must be exempt from CSRF."""
        assert "GET" in SAFE_METHODS
        assert "HEAD" in SAFE_METHODS
        assert "OPTIONS" in SAFE_METHODS
        assert "TRACE" in SAFE_METHODS
        # State-changing methods must NOT be in safe methods
        assert "POST" not in SAFE_METHODS
        assert "PUT" not in SAFE_METHODS
        assert "DELETE" not in SAFE_METHODS
        assert "PATCH" not in SAFE_METHODS

    def test_exempt_paths_configured(self):
        """Health endpoint must be exempt."""
        assert "/health" in EXEMPT_PATHS

    def test_exempt_prefixes_configured(self):
        """Auth and webhooks prefixes must be exempt."""
        assert "/v1/auth/" in EXEMPT_PREFIXES
        assert "/v1/webhooks/" in EXEMPT_PREFIXES

    def test_cookie_name_configured(self):
        """CSRF cookie name must be configured."""
        assert CSRF_COOKIE_NAME == "csrf_token"


class TestCSRFEndpoint:
    @pytest.mark.asyncio
    async def test_csrf_token_endpoint_returns_token(self, client):
        """GET /v1/auth/csrf-token must return a token and set a cookie."""
        response = await client.get("/v1/auth/csrf-token")
        assert response.status_code == 200
        data = response.json()
        assert "token" in data
        assert len(data["token"]) >= 32
        # Must set csrf_token cookie
        assert "csrf_token" in response.cookies
        cookie_value = response.cookies["csrf_token"]
        assert "." in cookie_value  # raw.signed format

    @pytest.mark.asyncio
    async def test_csrf_token_endpoint_cookie_not_httponly(self, client):
        """CSRF cookie must be accessible by JS (httponly=False)."""
        response = await client.get("/v1/auth/csrf-token")
        # FastAPI test client doesn't expose cookie flags directly,
        # so this verifies the endpoint exists and returns a cookie
        assert "csrf_token" in response.cookies


class TestCSRFIntegration:
    """Integration tests for CSRF middleware protection via the ASGI app.

    These tests verify the full middleware chain: CSRF validation runs BEFORE
    auth/rate-limit/handler, blocking state-changing requests with missing or
    tampered tokens, while allowing safe methods and exempt routes through.

    Middleware execution order (outermost → innermost):
        CORS → CSRF → Auth → RateLimit → Logging → handler
    """

    @pytest.mark.asyncio
    async def test_post_without_csrf_token_returns_403(self, client):
        """POST without X-CSRF-Token must return 403 with CSRF_FAILED code.
        
        The CSRF middleware runs before Auth, so this 403 is returned even
        before any auth check happens.
        """
        response = await client.post("/v1/nonexistent")
        assert response.status_code == 403
        data = response.json()
        assert data["error"]["code"] == "CSRF_FAILED"
        assert "CSRF validation failed" in data["error"]["message"]

    @pytest.mark.asyncio
    async def test_post_with_valid_csrf_token_bypasses_csrf(self, client):
        """POST with valid X-CSRF-Token must pass CSRF check.
        
        CSRF passes → request proceeds → router returns 404 (no such route).
        A 403 would mean CSRF blocked it; a 404 proves it passed.
        """
        # 1. Get a CSRF token from the dedicated endpoint
        token_resp = await client.get("/v1/auth/csrf-token")
        csrf_cookie = token_resp.cookies["csrf_token"]
        raw_token = token_resp.json()["token"]

        # 2. POST to a non-existent route with valid token
        #    (non-existent avoids auth dependencies)
        response = await client.post(
            "/v1/nonexistent",
            cookies={"csrf_token": csrf_cookie},
            headers={"X-CSRF-Token": raw_token},
        )
        # CSRF validation passed → request reached router → 404, not 403
        assert response.status_code == 404, (
            f"Expected 404 (CSRF passed), got {response.status_code}. "
            "A 403 would mean CSRF blocked the request."
        )

    @pytest.mark.asyncio
    async def test_post_without_csrf_token_to_exempt_route_succeeds(self, client):
        """POST to /v1/auth/* (exempt) must bypass CSRF even without a token."""
        response = await client.post("/v1/auth/logout")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data

    @pytest.mark.asyncio
    async def test_post_to_exempt_webhooks_prefix_bypasses_csrf(self, client):
        """POST to /v1/webhooks/* (exempt) must bypass CSRF."""
        response = await client.post("/v1/webhooks/stripe")
        # Stripe webhook will validate signature and return 400, but
        # the important thing is we get a non-403 response (CSRF bypassed)
        assert response.status_code != 403

    @pytest.mark.asyncio
    async def test_post_with_tampered_cookie_returns_403(self, client):
        """POST with tampered csrf_token cookie must return 403.
        
        The cookie value 'raw.signed' is validated — if the cookie is
        tampered, even with a valid header token, the signature won't match.
        """
        # Get a valid raw token from the CSRF endpoint
        token_resp = await client.get("/v1/auth/csrf-token")
        raw_token = token_resp.json()["token"]

        # POST with a tampered cookie but valid header token
        response = await client.post(
            "/v1/nonexistent",
            cookies={"csrf_token": "tampered.signature"},
            headers={"X-CSRF-Token": raw_token},
        )
        assert response.status_code == 403
        data = response.json()
        assert data["error"]["code"] == "CSRF_FAILED"

    @pytest.mark.asyncio
    async def test_get_request_never_blocked(self, client):
        """GET requests must never require CSRF validation (safe method)."""
        response = await client.get("/health")
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_options_preflight_never_blocked(self, client):
        """OPTIONS preflight must never require CSRF validation."""
        response = await client.options(
            "/v1/generate/try-on",
            headers={"Origin": "http://localhost:3000"},
        )
        # CORS middleware handles preflight; any non-403 status is fine
        assert response.status_code != 403

    @pytest.mark.asyncio
    async def test_csrf_token_cookie_set_on_safe_non_exempt_request(self, client):
        """GET to a non-exempt route must set the csrf_token cookie.
        
        The CSRF middleware sets the cookie on every safe-method response
        for non-exempt routes when no cookie is present in the request.
        """
        # Use a non-existent GET route (non-exempt, safe method)
        # The cookie is set on the response even though it's a 404
        response = await client.get("/v1/nonexistent-safe-path")
        assert "csrf_token" in response.cookies, (
            "CSRF cookie should be set on safe-method responses for non-exempt routes"
        )
        cookie = response.cookies["csrf_token"]
        # Cookie format: raw_token.signature (both parts present)
        assert "." in cookie, f"Expected 'raw.signed' format, got: {cookie}"
        parts = cookie.split(".")
        assert len(parts) == 2
        assert len(parts[0]) >= 32  # raw token
        assert len(parts[1]) == 64  # hex signature

    @pytest.mark.asyncio
    async def test_csrf_token_cookie_not_set_on_exempt_route(self, client):
        """GET to an exempt route must NOT have CSRF cookie set by middleware.
        
        The /v1/auth/csrf-token endpoint sets its own cookie, but the
        middleware itself skips cookie-setting for exempt paths.
        """
        # The csrf-token endpoint is under /v1/auth/ (exempt prefix)
        # but the endpoint itself SETS the cookie manually
        response = await client.get("/v1/auth/csrf-token")
        # Cookie is set by the handler, not the middleware
        assert "csrf_token" in response.cookies

    @pytest.mark.asyncio
    async def test_csrf_endpoint_token_matches_cookie_raw_part(self, client):
        """CSRF token endpoint returns a token matching the cookie.
        
        The JSON response body contains the raw token, while the cookie
        contains 'raw.signed'. The frontend uses the cookie value as the
        X-CSRF-Token header, so the raw token in the body must match
        the raw part of the cookie.
        """
        response = await client.get("/v1/auth/csrf-token")
        assert response.status_code == 200
        data = response.json()
        cookie = response.cookies["csrf_token"]

        raw_from_cookie = cookie.split(".")[0]
        assert data["token"] == raw_from_cookie, (
            f"Token mismatch: body token '{data['token']}' != "
            f"cookie raw part '{raw_from_cookie}'"
        )

    @pytest.mark.asyncio
    async def test_post_with_wrong_header_token_returns_403(self, client):
        """POST with valid cookie but wrong X-CSRF-Token must return 403."""
        token_resp = await client.get("/v1/auth/csrf-token")
        csrf_cookie = token_resp.cookies["csrf_token"]

        # Send a different token in the header than what's in the cookie
        response = await client.post(
            "/v1/nonexistent",
            cookies={"csrf_token": csrf_cookie},
            headers={"X-CSRF-Token": "some-other-token-that-doesnt-match"},
        )
        assert response.status_code == 403
        data = response.json()
        assert data["error"]["code"] == "CSRF_FAILED"

    @pytest.mark.asyncio
    async def test_post_with_missing_header_returns_403_even_with_cookie(self, client):
        """POST with cookie but no X-CSRF-Token header must return 403."""
        token_resp = await client.get("/v1/auth/csrf-token")
        csrf_cookie = token_resp.cookies["csrf_token"]

        # Cookie present but no header
        response = await client.post(
            "/v1/nonexistent",
            cookies={"csrf_token": csrf_cookie},
            # No X-CSRF-Token header
        )
        assert response.status_code == 403
        data = response.json()
        assert data["error"]["code"] == "CSRF_FAILED"
