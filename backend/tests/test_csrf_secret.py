"""Tests for CSRF_SECRET key separation (M-01).

Verifies that CSRF_SECRET must be set independently of JWT_SECRET.
The fallback from CSRF_SECRET to JWT_SECRET was removed — sign_csrf_token
must raise RuntimeError when CSRF_SECRET is empty, regardless of JWT_SECRET.
"""
import pytest
from unittest.mock import patch

from app.services.csrf import sign_csrf_token, generate_csrf_token


class TestCSRFSecretRequired:
    """CSRF_SECRET must be set independently — no fallback to JWT_SECRET."""

    def test_csrf_secret_required(self):
        """When CSRF_SECRET is empty, sign_csrf_token must raise RuntimeError."""
        token = generate_csrf_token()
        with patch("app.services.csrf.get_settings") as mock_get_settings:
            mock_settings = mock_get_settings.return_value
            mock_settings.CSRF_SECRET = ""

            with pytest.raises(RuntimeError, match="CSRF_SECRET must be configured"):
                sign_csrf_token(token)

    def test_csrf_secret_no_fallback_to_jwt(self):
        """Even when JWT_SECRET is set but CSRF_SECRET is not, must raise RuntimeError.

        This verifies there is no fallback from CSRF_SECRET to JWT_SECRET
        (the original security issue M-01).
        """
        token = generate_csrf_token()
        with patch("app.services.csrf.get_settings") as mock_get_settings:
            mock_settings = mock_get_settings.return_value
            mock_settings.CSRF_SECRET = ""
            mock_settings.JWT_SECRET = "valid-jwt-secret"

            with pytest.raises(RuntimeError, match="CSRF_SECRET must be configured"):
                sign_csrf_token(token)


class TestCSRFSecretWorks:
    """When CSRF_SECRET is set, signing works normally."""

    def test_csrf_secret_set_success(self):
        """When CSRF_SECRET is set, sign_csrf_token must return a signature."""
        token = generate_csrf_token()
        with patch("app.services.csrf.get_settings") as mock_get_settings:
            mock_settings = mock_get_settings.return_value
            mock_settings.CSRF_SECRET = "test-csrf-secret"

            sig = sign_csrf_token(token)
            assert sig != token
            assert len(sig) == 64  # SHA-256 hex digest
