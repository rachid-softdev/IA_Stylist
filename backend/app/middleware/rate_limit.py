import time
from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from app.config import get_settings

settings = get_settings()

# Simple in-memory rate limiter (production: use Redis)
_rate_store: dict[str, list[float]] = {}


def _get_rate_limit_key(plan: str, endpoint: str) -> str:
    return f"{plan}:{endpoint}"


def _is_rate_limited(plan: str) -> bool:
    """Check if the plan has exceeded its rate limit using a sliding window."""
    now = time.time()
    window = 3600  # 1 hour
    key = f"rate_{plan}"

    if key not in _rate_store:
        _rate_store[key] = []

    # Clean old entries
    _rate_store[key] = [t for t in _rate_store[key] if now - t < window]

    limit = settings.rate_limits.get(plan, 10)
    if len(_rate_store[key]) >= limit:
        return True

    _rate_store[key].append(now)
    return False


class RateLimitMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Skip rate limiting for non-API routes
        if not request.url.path.startswith("/v1") and not request.url.path.startswith("/generate"):
            return await call_next(request)

        # Determine plan from request state (set by auth middleware)
        user = getattr(request.state, "current_user", None)
        plan = user.plan if user else "free"

        if _is_rate_limited(plan):
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail={
                    "code": "RATE_LIMITED",
                    "message": "Rate limit exceeded. Please wait before trying again.",
                    "details": {"plan": plan, "retry_after": 60},
                },
            )

        return await call_next(request)
