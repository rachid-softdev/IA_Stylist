"""Tests for in-memory rate limiter fallback (H-06).

Tests the InMemoryRateLimiter class directly:
- Allows requests within the limit
- Blocks at the limit
- Sliding window expiry (old requests pruned)
- Independent counters per key
- Pruning removes empty keys from store
"""
import time
from unittest.mock import patch

from app.middleware.rate_limit import InMemoryRateLimiter


class TestInMemoryRateLimiter:

    def test_allows_within_limit(self):
        """30 requests (default limit) must all return True."""
        limiter = InMemoryRateLimiter(default_limit=30, window_seconds=60)
        key = "test:user:free"

        results = [limiter.check(key, limit=30) for _ in range(30)]
        assert all(results) is True

    def test_blocks_at_limit(self):
        """31st request must return False (rate limited)."""
        limiter = InMemoryRateLimiter(default_limit=30, window_seconds=60)
        key = "test:user:free"

        for _ in range(30):
            assert limiter.check(key, limit=30) is True

        # 31st request is blocked
        assert limiter.check(key, limit=30) is False

    def test_sliding_window_expiry(self):
        """Requests older than window_seconds must be pruned, allowing new requests."""
        limiter = InMemoryRateLimiter(default_limit=5, window_seconds=60)
        key = "sliding:test"

        # Fill the window at time 0
        with patch("time.time", return_value=0.0):
            for _ in range(5):
                assert limiter.check(key, limit=5) is True
            # Window is full
            assert limiter.check(key, limit=5) is False

        # Advance time past the window (61 seconds later)
        # The old timestamps get pruned, so we can make new requests
        with patch("time.time", return_value=61.0):
            # First request prunes the old ones, adds a new one
            assert limiter.check(key, limit=5) is True
            # We can make 4 more (total 5 in new window)
            for _ in range(4):
                assert limiter.check(key, limit=5) is True
            # Now window is full again
            assert limiter.check(key, limit=5) is False

    def test_different_keys_independent(self):
        """Two different keys must have separate counters."""
        limiter = InMemoryRateLimiter(default_limit=3, window_seconds=60)
        key_a = "user:alpha"
        key_b = "user:beta"

        # Exhaust key_a
        for _ in range(3):
            assert limiter.check(key_a, limit=3) is True
        assert limiter.check(key_a, limit=3) is False

        # key_b should still be able to make requests
        assert limiter.check(key_b, limit=3) is True
        assert limiter.check(key_b, limit=3) is True
        assert limiter.check(key_b, limit=3) is True
        assert limiter.check(key_b, limit=3) is False

    def test_prune_empty_keys(self):
        """After all timestamps for a key expire via _prune, the key must be removed from _store."""
        limiter = InMemoryRateLimiter(default_limit=5, window_seconds=60)
        key = "temp:key"

        # Manually add an expired timestamp
        limiter._store[key] = [0.0]  # timestamp at epoch

        # Prune with time far past the window
        limiter._prune(key, now=120.0)

        # Key should have been removed (only expired timestamp existed)
        assert key not in limiter._store
