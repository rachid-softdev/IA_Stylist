"""Auth middleware that decodes JWT and sets request state for downstream middleware."""
import logging
from jose import jwt as jose_jwt
from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from app.config import get_settings

logger = logging.getLogger(__name__)


class AuthMiddleware(BaseHTTPMiddleware):
    """Decode JWT from cookie or Authorization header and set request.state.
    
    This runs BEFORE RateLimitMiddleware so the rate limiter can access
    the user's plan for tier-based rate limiting.
    """
    
    async def dispatch(self, request: Request, call_next):
        # Skip auth for non-API routes and OPTIONS preflight
        if not request.url.path.startswith("/v1") or request.method == "OPTIONS":
            return await call_next(request)
        
        # Skip auth for public endpoints
        public_paths = ["/v1/auth/login", "/v1/auth/signup", "/v1/auth/refresh", "/v1/auth/csrf-token"]
        if request.url.path in public_paths:
            return await call_next(request)
        
        # Try to extract and decode JWT
        token = None
        
        # Try httpOnly cookie first
        token = request.cookies.get("vfs_access_token")
        
        # Fallback to Authorization header
        if not token:
            auth_header = request.headers.get("Authorization")
            if auth_header and auth_header.startswith("Bearer "):
                token = auth_header.replace("Bearer ", "")
        
        if token:
            try:
                settings = get_settings()
                payload = jose_jwt.decode(
                    token,
                    settings.JWT_SECRET,
                    algorithms=["HS256"],
                    options={"verify_aud": False},
                )
                
                request.state.current_user_id = payload.get("sub")
                request.state.current_user_plan = payload.get("plan", "free")
                
            except Exception as e:
                # Token invalid or expired — don't block, rate limiter will use "free"
                # The route dependency will properly validate later
                logger.warning("AuthMiddleware: JWT decode failed: %s", str(e))
                request.state.current_user_id = None
                request.state.current_user_plan = "free"
        else:
            request.state.current_user_id = None
            request.state.current_user_plan = "free"
        
        return await call_next(request)
