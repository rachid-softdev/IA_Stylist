"""Tests for logging middleware PII anonymization (H-05).

Covers the _anonymize_id function in app.middleware.logging.
"""
import hashlib
import pytest
from app.middleware.logging import _anonymize_id


class TestAnonymizeId:
    """Test _anonymize_id(user_id) PII protection."""

    def test_none_input_returns_none(self):
        """None input must return None."""
        assert _anonymize_id(None) is None

    def test_empty_string_returns_none(self):
        """Empty string input must return None (falsy)."""
        assert _anonymize_id("") is None

    def test_valid_input_returns_12_char_string(self):
        """Valid user_id must return a 12-character hex string."""
        result = _anonymize_id("user-abc-123")
        assert result is not None
        assert isinstance(result, str)
        assert len(result) == 12
        # Must be hex characters
        int(result, 16)  # raises ValueError if not hex

    def test_deterministic_same_input(self):
        """Same input multiple times must produce same output."""
        user_id = "test-user-001"
        result1 = _anonymize_id(user_id)
        result2 = _anonymize_id(user_id)
        assert result1 == result2

    def test_different_inputs_different_outputs(self):
        """Different inputs must produce different hashes."""
        result1 = _anonymize_id("user-001")
        result2 = _anonymize_id("user-002")
        assert result1 != result2

    def test_output_is_sha256_truncated(self):
        """Output must be first 12 chars of SHA-256 hex digest."""
        user_id = "test-user-abc"
        expected_prefix = hashlib.sha256(user_id.encode()).hexdigest()[:12]
        assert _anonymize_id(user_id) == expected_prefix

    def test_long_user_id_still_hashed(self):
        """Long user IDs must still produce 12-char hash."""
        long_id = "a" * 1000
        result = _anonymize_id(long_id)
        assert len(result) == 12

    def test_unicode_user_id(self):
        """Unicode user IDs must work without error."""
        result = _anonymize_id("user-émoji-🔥")
        assert result is not None
        assert len(result) == 12
