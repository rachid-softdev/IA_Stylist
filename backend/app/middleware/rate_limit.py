"""Rate limiting middleware backed by Redis with in-memory fallback."""
import datetime
import logging
import time
from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from app.config import get_settings
from app.services.redis import get_redis

logger = logging.getLogger(__name__)
settings = get_settings()


class InMemoryRateLimiter:
    """Fallback rate limiter when Redis is unavailable.

    Per-worker in-memory store with sliding window per user.
    Less strict than Redis mode (each worker has independent state),
    but provides essential protection during Redis outages.
    """

    def __init__(self, default_limit: int = 30, window_seconds: int = 60):
        self.default_limit = default_limit
        self.window_seconds = window_seconds
        self._store: dict[str, list[float]] = {}

    def _prune(self, key: str, now: float) -> None:
        if key in self._store:
            self._store[key] = [
                t for t in self._store[key]
                if now - t < self.window_seconds
            ]
            if not self._store[key]:
                del self._store[key]

    def check(self, key: str, limit: int) -> bool:
        """Returns True if request is allowed, False if rate limited."""
        now = time.time()
        self._prune(key, now)
        if key not in self._store:
            self._store[key] = []
        if len(self._store[key]) >= limit:
            return False
        self._store[key].append(now)
        return True


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Rate limits requests using a fixed window counter in Redis.

    Uses INCR + EXPIRE pattern (fixed window algorithm).
    This is a deliberate trade-off: simpler than sliding window, but
    allows up to 2x the limit at window boundaries (burst at HH:59 + HH:00).

    If stricter rate limiting is needed, migrate to a sliding window
    using Redis sorted sets (ZADD + ZREMRANGEBYSCORE + ZCARD).

    Requires AuthMiddleware to run first so request.state.current_user_plan is set.
    Falls back to 'free' plan if no auth info is available.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._fallback = InMemoryRateLimiter()

    async def dispatch(self, request: Request, call_next):
        # Only rate limit API routes
        if not request.url.path.startswith("/v1"):
            return await call_next(request)

        plan = getattr(request.state, "current_user_plan", "free")
        limit = settings.rate_limits.get(plan, 10)

        try:
            redis_conn = await get_redis()
            # Fixed window: hourly bucket, format: "rate:{user_id}:{plan}:{YYYYMMDDHH}"
            now = datetime.datetime.utcnow()

            # Use current_user_id if available, otherwise fall back to IP
            user_id = getattr(request.state, "current_user_id", None)
            if not user_id:
                forwarded_for = request.headers.get("X-Forwarded-For", "")
                user_id = (
                    forwarded_for.split(",")[0].strip()
                    if forwarded_for
                    else (request.client.host or "unknown")
                )
            window_key = f"rate:{user_id}:{plan}:{now.strftime('%Y%m%d%H')}"

            current = await redis_conn.incr(window_key)
            if current == 1:
                await redis_conn.expire(window_key, 3600)

            if current > limit:
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail={
                        "code": "RATE_LIMITED",
                        "message": "Rate limit exceeded. Please wait before trying again.",
                        "details": {"plan": plan, "retry_after": 60, "limit": limit},
                    },
                )
        except HTTPException:
            raise
        except Exception as e:
            # 🔒 Fallback : rate limiting en mémoire quand Redis est indisponible
            logger.error("Rate limiter fallback (Redis unavailable): %s", str(e))

            user_id = getattr(request.state, "current_user_id", None)
            if not user_id:
                forwarded_for = request.headers.get("X-Forwarded-For", "")
                user_id = (
                    forwarded_for.split(",")[0].strip()
                    if forwarded_for
                    else (request.client.host or "unknown")
                )
            fallback_key = f"fallback:{user_id}:{plan}"

            if not self._fallback.check(fallback_key, limit):
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail={
                        "code": "RATE_LIMITED",
                        "message": "Rate limit exceeded (degraded mode). Please wait.",
                        "details": {"retry_after": 60, "limit": limit},
                    },
                )

        return await call_next(request)
