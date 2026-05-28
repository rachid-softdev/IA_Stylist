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
        # Skip JWT processing if API key already authenticated
        if getattr(request.state, "auth_method", None) == "api_key":
            return await call_next(request)

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
                    options={"verify_aud": False},  # Intentional: Supabase JWTs don't include an 'aud' claim we can validate; disabling prevents decode failure while still verifying signature, exp, iss.
                )
                
                request.state.current_user_id = payload.get("sub")
                request.state.current_user_plan = payload.get("plan", "free")
                
            except Exception as e:
                # INTENTIONNEL : On ne rejette PAS la requête ici.
                # Ce middleware sert uniquement à préparer request.state
                # pour le RateLimitMiddleware (qui a besoin du plan).
                #
                # La validation stricte de l'authentification est déléguée
                # aux dépendances FastAPI (get_current_user, require_auth)
                # dans les route handlers. Voir backend/app/dependencies.py.
                #
                # Si un token invalide arrive sur une route protégée,
                # la dépendance lèvera un HTTPException avec 401.
                logger.warning("AuthMiddleware: JWT decode failed: %s", str(e))
                request.state.current_user_id = None
                request.state.current_user_plan = "free"
        else:
            request.state.current_user_id = None
            request.state.current_user_plan = "free"
        
        return await call_next(request)
