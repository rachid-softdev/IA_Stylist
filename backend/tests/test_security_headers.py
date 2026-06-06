"""Tests for security headers middleware (L-02).

Verifies that the ASGI-native middleware adds HSTS, X-Content-Type-Options,
X-Frame-Options, and Referrer-Policy headers with correct values to all responses.
"""
import pytest
from fastapi.testclient import TestClient

from app.main import app


class TestSecurityHeaders:
    """Security headers added by @app.middleware("http")."""

    @pytest.fixture(autouse=True)
    def _client(self):
        """Create a synchronous test client per test."""
        with TestClient(app) as c:
            yield c

    def test_security_headers_present(self, _client):
        """All four security headers must be present in the response."""
        response = _client.get("/health")
        assert response.status_code == 200
        assert "Strict-Transport-Security" in response.headers
        assert "X-Content-Type-Options" in response.headers
        assert "X-Frame-Options" in response.headers
        assert "Referrer-Policy" in response.headers

    def test_hsts_value(self, _client):
        """HSTS header must have max-age=31536000 and includeSubDomains."""
        response = _client.get("/health")
        hsts = response.headers["Strict-Transport-Security"]
        assert "max-age=31536000" in hsts
        assert "includeSubDomains" in hsts

    def test_xcontent_type_options_value(self, _client):
        """X-Content-Type-Options must be 'nosniff'."""
        response = _client.get("/health")
        assert response.headers["X-Content-Type-Options"] == "nosniff"

    def test_xframe_options_value(self, _client):
        """X-Frame-Options must be 'DENY'."""
        response = _client.get("/health")
        assert response.headers["X-Frame-Options"] == "DENY"

    def test_referrer_policy_value(self, _client):
        """Referrer-Policy must be 'strict-origin-when-cross-origin'."""
        response = _client.get("/health")
        assert response.headers["Referrer-Policy"] == "strict-origin-when-cross-origin"

    def test_security_headers_on_404(self, _client):
        """Security headers must also appear on error responses."""
        response = _client.get("/nonexistent-route")
        assert response.status_code == 404
        assert "Strict-Transport-Security" in response.headers
        assert "X-Content-Type-Options" in response.headers
        assert "X-Frame-Options" in response.headers
        assert "Referrer-Policy" in response.headers

    def test_security_headers_on_405(self, _client):
        """Security headers must appear on method-not-allowed responses."""
        response = _client.post("/health")
        # POST to /health may be 405 or may go through — headers must be present regardless
        assert "Strict-Transport-Security" in response.headers
        assert "X-Content-Type-Options" in response.headers

    def test_headers_on_csrf_route(self, _client):
        """Security headers on the CSRF token endpoint."""
        response = _client.get("/v1/auth/csrf-token")
        assert response.status_code == 200
        assert "Strict-Transport-Security" in response.headers
        assert "X-Content-Type-Options" in response.headers
        assert "X-Frame-Options" in response.headers
        assert "Referrer-Policy" in response.headers
