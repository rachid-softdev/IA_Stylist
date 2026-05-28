"""In-memory rate limiter for API key authentication failures."""
import time
import logging
from collections import defaultdict

logger = logging.getLogger(__name__)


class ApiKeyFailureRateLimiter:
    """Per-IP rate limiter for API key auth failures.

    Uses in-memory dict with TTL-based pruning (no Redis dependency).
    Each uvicorn worker maintains its own state.
    """

    def __init__(self, max_failures: int = 10, window_seconds: int = 3600):
        self.max_failures = max_failures
        self.window_seconds = window_seconds
        self._store: dict[str, list[float]] = defaultdict(list)

    def _prune(self, ip: str) -> None:
        """Remove expired entries."""
        now = time.time()
        self._store[ip] = [
            t for t in self._store[ip]
            if now - t < self.window_seconds
        ]

    def is_rate_limited(self, ip: str) -> bool:
        self._prune(ip)
        return len(self._store[ip]) >= self.max_failures

    def record_failure(self, ip: str) -> int:
        self._store[ip].append(time.time())
        self._prune(ip)
        return len(self._store[ip])

    def record_success(self, ip: str) -> None:
        self._store.pop(ip, None)

    def cleanup_expired(self) -> None:
        """Periodic cleanup of stale IPs. Call from background task if desired."""
        now = time.time()
        expired = [
            ip for ip, timestamps in self._store.items()
            if timestamps and now - max(timestamps) > self.window_seconds * 2
        ]
        for ip in expired:
            del self._store[ip]
