"""CSRF protection middleware using double-submit cookie pattern.

Sets a `csrf_token` cookie on every response. For state-changing requests
(POST, PUT, DELETE, PATCH), validates that the `X-CSRF-Token` request header
matches the cookie value. Uses timing-safe comparison.

Exempt routes:
- GET, HEAD, OPTIONS, TRACE (safe methods)
- /v1/auth/* (login/signup/refresh are idempotent or use Authorization header)
- /v1/webhooks/* (called by external services, not browsers)
- /health
"""
import logging
from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from app.config import get_settings
from app.services.csrf import make_csrf_cookie_value, validate_csrf_token

logger = logging.getLogger(__name__)

CSRF_COOKIE_NAME = "csrf_token"

# Routes exempt from CSRF validation
EXEMPT_PATHS = {
    "/health",
}
EXEMPT_PREFIXES = {
    "/v1/auth/",
    "/v1/webhooks/",
}
SAFE_METHODS = {"GET", "HEAD", "OPTIONS", "TRACE"}


class CSRFMiddleware(BaseHTTPMiddleware):
    """Protects against CSRF by validating a double-submit cookie pattern.
    
    For safe methods (GET, HEAD, OPTIONS, TRACE), sets the CSRF cookie
    if not already present. For state-changing methods, validates the
    X-CSRF-Token header against the csrf_token cookie.
    """
    
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint):
        # 1. VALIDATION CSRF AVANT handler (for state-changing methods)
        if request.method not in SAFE_METHODS and not self._is_exempt(request):
            cookie_token = request.cookies.get(CSRF_COOKIE_NAME)
            header_token = request.headers.get("X-CSRF-Token")
            if not validate_csrf_token(cookie_token or "", header_token or ""):
                logger.warning(
                    "CSRF validation failed: method=%s path=%s",
                    request.method, request.url.path,
                )
                return JSONResponse(
                    status_code=403,
                    content={
                        "data": None,
                        "error": {
                            "code": "CSRF_FAILED",
                            "message": "CSRF validation failed. Refresh the page and try again.",
                        },
                    },
                )
        
        # 2. Exécuter le handler
        response = await call_next(request)
        
        # 3. Set CSRF cookie UNIQUEMENT pour les safe methods, si pas déjà présent
        if request.method in SAFE_METHODS and not self._is_exempt(request):
            if CSRF_COOKIE_NAME not in request.cookies:
                self._set_csrf_cookie(response)
        
        return response
    
    def _set_csrf_cookie(self, response: Response) -> None:
        """Set the CSRF cookie on the response."""
        settings = get_settings()
        cookie_value = make_csrf_cookie_value()
        response.set_cookie(
            key=CSRF_COOKIE_NAME,
            value=cookie_value,
            max_age=86400,          # 24 hours
            httponly=False,         # Must be readable by JS for double-submit
            samesite="lax",
            secure=settings.ENVIRONMENT != "local",
        )
    
    def _is_exempt(self, request: Request) -> bool:
        """Check if the request path is exempt from CSRF validation."""
        path = request.url.path
        if path in EXEMPT_PATHS:
            return True
        for prefix in EXEMPT_PREFIXES:
            if path.startswith(prefix):
                return True
        return False
