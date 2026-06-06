"""Tests for config validation across all environments (L-03).

Verifies that validate_critical_settings raises ValueError in production
but only warns in non-production environments when critical settings
(DATABASE_URL, JWT_SECRET, CSRF_SECRET) are missing.
"""
import warnings
import pytest
from pydantic import ValidationError

from app.config import Settings


class TestConfigValidationProduction:
    """In production, missing critical settings must raise ValueError."""

    def test_production_fails_on_missing_jwt(self):
        """ENV=production with empty JWT_SECRET must raise ValueError."""
        with pytest.raises(ValueError, match="Missing required settings"):
            Settings(
                ENVIRONMENT="production",
                DATABASE_URL="postgresql://localhost:5432/db",
                JWT_SECRET="",
                CSRF_SECRET="test-csrf-secret",
            )

    def test_production_fails_on_missing_csrf_secret(self):
        """ENV=production with empty CSRF_SECRET must raise ValueError."""
        with pytest.raises(ValueError, match="Missing required settings"):
            Settings(
                ENVIRONMENT="production",
                DATABASE_URL="postgresql://localhost:5432/db",
                JWT_SECRET="test-jwt-secret",
                CSRF_SECRET="",
            )

    def test_production_fails_on_missing_database_url(self):
        """ENV=production with empty DATABASE_URL must raise ValueError."""
        with pytest.raises(ValueError, match="Missing required settings"):
            Settings(
                ENVIRONMENT="production",
                DATABASE_URL="",
                JWT_SECRET="test-jwt-secret",
                CSRF_SECRET="test-csrf-secret",
            )

    def test_production_fails_on_all_missing(self):
        """ENV=production with all critical settings empty must raise ValueError with all names."""
        with pytest.raises(ValueError) as exc_info:
            Settings(
                ENVIRONMENT="production",
                DATABASE_URL="",
                JWT_SECRET="",
                CSRF_SECRET="",
            )
        msg = str(exc_info.value)
        assert "DATABASE_URL" in msg
        assert "JWT_SECRET" in msg
        assert "CSRF_SECRET" in msg


class TestConfigValidationNonProduction:
    """In non-production, missing critical settings must emit warnings, not errors."""

    def test_local_warns_on_missing_jwt(self):
        """ENV=local with empty JWT_SECRET must emit a warning (no error)."""
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            settings = Settings(
                ENVIRONMENT="local",
                DATABASE_URL="postgresql://localhost:5432/db",
                JWT_SECRET="",
                CSRF_SECRET="test-csrf-secret",
            )
        assert len(w) >= 1
        assert any("Missing required settings" in str(warning.message) for warning in w)
        assert "JWT_SECRET" in str(w[-1].message)

    def test_local_warns_on_missing_csrf_secret(self):
        """ENV=local with empty CSRF_SECRET must emit a warning (no error)."""
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            settings = Settings(
                ENVIRONMENT="local",
                DATABASE_URL="postgresql://localhost:5432/db",
                JWT_SECRET="test-jwt-secret",
                CSRF_SECRET="",
            )
        assert len(w) >= 1
        assert any("Missing required settings" in str(warning.message) for warning in w)
        assert "CSRF_SECRET" in str(w[-1].message)

    def test_local_warns_on_missing_all(self):
        """ENV=local with all critical settings empty must emit warning with all names."""
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            settings = Settings(
                ENVIRONMENT="local",
                DATABASE_URL="",
                JWT_SECRET="",
                CSRF_SECRET="",
            )
        assert len(w) >= 1
        msg = str(w[-1].message)
        assert "DATABASE_URL" in msg
        assert "JWT_SECRET" in msg
        assert "CSRF_SECRET" in msg

    def test_test_env_warns_on_missing(self):
        """ENV=test with missing settings must also warn (not fail)."""
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            settings = Settings(
                ENVIRONMENT="test",
                DATABASE_URL="postgresql://localhost:5432/db",
                JWT_SECRET="",
                CSRF_SECRET="test-csrf-secret",
            )
        assert len(w) >= 1
        assert any("Missing required settings" in str(warning.message) for warning in w)


class TestConfigValidationPass:
    """When all critical settings are provided, no error or warning should occur."""

    def test_all_set_passes(self):
        """All required settings provided → no error."""
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            settings = Settings(
                ENVIRONMENT="production",
                DATABASE_URL="postgresql://localhost:5432/db",
                JWT_SECRET="test-jwt-secret",
                CSRF_SECRET="test-csrf-secret",
            )
        assert settings.JWT_SECRET == "test-jwt-secret"
        assert settings.CSRF_SECRET == "test-csrf-secret"
        # No warnings about missing settings
        missing_warnings = [x for x in w if "Missing required settings" in str(x.message)]
        assert len(missing_warnings) == 0

    def test_all_set_non_production_passes(self):
        """All required settings in non-production → no warning or error."""
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            settings = Settings(
                ENVIRONMENT="local",
                DATABASE_URL="postgresql://localhost:5432/db",
                JWT_SECRET="test-jwt-secret",
                CSRF_SECRET="test-csrf-secret",
            )
        missing_warnings = [x for x in w if "Missing required settings" in str(x.message)]
        assert len(missing_warnings) == 0
