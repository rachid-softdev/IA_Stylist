"""Tests for API key failure rate limiter (H-03).

Tests the ApiKeyFailureRateLimiter class directly:
- Tracks failures per IP
- Enforces max_failures threshold (default 10)
- Resets on successful authentication
- TTL-based expiry of failure records
- Independent counters per IP
"""
import time
from unittest.mock import patch

from app.services.api_key_rate_limiter import ApiKeyFailureRateLimiter


class TestApiKeyFailureRateLimiter:

    def test_rate_limiter_tracks_failures(self):
        """Recording 10 failures from same IP must trigger rate limit."""
        limiter = ApiKeyFailureRateLimiter(max_failures=10, window_seconds=3600)
        ip = "192.168.1.1"

        for _ in range(10):
            limiter.record_failure(ip)

        assert limiter.is_rate_limited(ip) is True

    def test_rate_limiter_allows_below_threshold(self):
        """Recording 9 failures (below threshold) must not trigger rate limit."""
        limiter = ApiKeyFailureRateLimiter(max_failures=10, window_seconds=3600)
        ip = "192.168.1.1"

        for _ in range(9):
            limiter.record_failure(ip)

        assert limiter.is_rate_limited(ip) is False

    def test_rate_limiter_resets_on_success(self):
        """After failures, record_success must clear the counter."""
        limiter = ApiKeyFailureRateLimiter(max_failures=10, window_seconds=3600)
        ip = "192.168.1.1"

        for _ in range(10):
            limiter.record_failure(ip)

        assert limiter.is_rate_limited(ip) is True

        limiter.record_success(ip)
        assert limiter.is_rate_limited(ip) is False

    def test_rate_limiter_ttl_expiry(self):
        """Failures older than window_seconds must be pruned and not count toward limit."""
        limiter = ApiKeyFailureRateLimiter(max_failures=5, window_seconds=60)
        ip = "10.0.0.1"

        # Record 5 failures at time 0
        with patch("time.time", return_value=0.0):
            for _ in range(5):
                limiter.record_failure(ip)
            assert limiter.is_rate_limited(ip) is True

        # Advance time past the TTL window (61 seconds later)
        with patch("time.time", return_value=61.0):
            # is_rate_limited prunes expired entries
            assert limiter.is_rate_limited(ip) is False

    def test_different_ips_separate_counters(self):
        """Two different IPs must maintain independent counters."""
        limiter = ApiKeyFailureRateLimiter(max_failures=5, window_seconds=3600)
        ip_a = "10.0.0.1"
        ip_b = "10.0.0.2"

        # Overload IP_A
        for _ in range(5):
            limiter.record_failure(ip_a)

        assert limiter.is_rate_limited(ip_a) is True
        # IP_B has no failures → not limited
        assert limiter.is_rate_limited(ip_b) is False

        # Now overload IP_B too
        for _ in range(5):
            limiter.record_failure(ip_b)

        assert limiter.is_rate_limited(ip_b) is True
        assert limiter.is_rate_limited(ip_a) is True
