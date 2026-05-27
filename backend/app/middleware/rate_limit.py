"""Rate limiting middleware backed by Redis."""
import logging
from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from app.config import get_settings
from app.services.redis import get_redis

logger = logging.getLogger(__name__)
settings = get_settings()


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Rate limits requests using a fixed window counter in Redis.
    
    Uses INCR + EXPIRE pattern. This is a fixed window algorithm,
    which is acceptable for this application. The window resets
    every hour, so there may be bursts at window boundaries.
    
    Requires AuthMiddleware to run first so request.state.current_user_plan is set.
    Falls back to 'free' plan if no auth info is available.
    """
    
    async def dispatch(self, request: Request, call_next):
        # Only rate limit API routes
        if not request.url.path.startswith("/v1"):
            return await call_next(request)
        
        plan = getattr(request.state, "current_user_plan", "free")
        limit = settings.rate_limits.get(plan, 10)
        
        try:
            redis_conn = await get_redis()
            # Fixed window: hourly bucket, format: "rate:{plan}:{YYYYMMDDHH}"
            import datetime
            now = datetime.datetime.utcnow()
            window_key = f"rate:{plan}:{now.strftime('%Y%m%d%H')}"
            
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
            # If Redis is unavailable, log and allow the request
            logger.error("Rate limiter error (allowing request): %s", str(e))
        
        return await call_next(request)
