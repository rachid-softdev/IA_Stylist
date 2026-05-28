import hashlib
import uuid
import structlog
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
import time

logger = structlog.get_logger()


def _anonymize_id(user_id: str | None) -> str | None:
    """Anonymize user ID for logging: one-way SHA-256 hash, truncated to 12 chars."""
    if not user_id:
        return None
    return hashlib.sha256(user_id.encode()).hexdigest()[:12]


class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        request_id = str(uuid.uuid4())
        start_time = time.time()

        # Attach request ID
        request.state.request_id = request_id

        response = await call_next(request)

        duration_ms = int((time.time() - start_time) * 1000)

        logger.info(
            "request.completed",
            request_id=request_id,
            method=request.method,
            path=request.url.path,
            status_code=response.status_code,
            duration_ms=duration_ms,
            user_hash=_anonymize_id(getattr(getattr(request.state, "current_user", None), "id", None)),
        )

        response.headers["X-Request-ID"] = request_id
        return response
