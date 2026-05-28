"""API Key authentication middleware for brand-scoped API access."""
import logging
from datetime import datetime, timezone
from typing import Optional

from fastapi import Request, HTTPException, status
from sqlalchemy import select, and_, or_, func
from starlette.middleware.base import BaseHTTPMiddleware

from app.config import get_settings
from app.db.session import async_session
from app.models.api_key import ApiKey
from app.models.brand import Brand
from app.services.security import verify_api_key, extract_key_prefix

logger = logging.getLogger(__name__)

API_KEY_ROUTE_PREFIXES = ("/v1/brands/", "/v1/catalog/")
DUAL_AUTH_ROUTE_PREFIXES = ("/v1/generate/",)


class ApiKeyMiddleware(BaseHTTPMiddleware):
    """Authenticate requests via X-API-Key header for brand-scoped routes."""

    async def dispatch(self, request: Request, call_next):
        if not request.url.path.startswith("/v1") or request.method == "OPTIONS":
            return await call_next(request)

        path = request.url.path
        is_api_key_primary = path.startswith(API_KEY_ROUTE_PREFIXES)
        is_dual_auth = path.startswith(DUAL_AUTH_ROUTE_PREFIXES)

        if not is_api_key_primary and not is_dual_auth:
            return await call_next(request)

        raw_key = request.headers.get("X-API-Key")

        if not raw_key:
            if is_dual_auth:
                return await call_next(request)
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={
                    "code": "API_KEY_REQUIRED",
                    "message": "X-API-Key header is required for this endpoint",
                },
            )

        auth_result = await self._authenticate(raw_key)
        if auth_result is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={
                    "code": "INVALID_API_KEY",
                    "message": "Invalid or expired API key",
                },
            )

        brand_id, brand_plan = auth_result

        request.state.current_user_id = brand_id
        request.state.current_user_plan = brand_plan
        request.state.brand_id = brand_id
        request.state.auth_method = "api_key"

        return await call_next(request)

    async def _authenticate(self, raw_key: str) -> Optional[tuple[str, str]]:
        prefix = extract_key_prefix(raw_key)
        async with async_session() as db:
            try:
                stmt = (
                    select(ApiKey)
                    .where(
                        ApiKey.prefix == prefix,
                        ApiKey.is_active == True,
                        and_(
                            or_(
                                ApiKey.expires_at.is_(None),
                                ApiKey.expires_at > func.now(),
                            )
                        ),
                    )
                )
                result = await db.execute(stmt)
                candidates: list[ApiKey] = list(result.scalars().all())

                if not candidates:
                    return None

                for candidate in candidates:
                    if verify_api_key(raw_key, candidate.key_hash):
                        candidate.last_used_at = datetime.now(timezone.utc)
                        await db.commit()

                        brand_result = await db.execute(
                            select(Brand).where(Brand.id == candidate.brand_id)
                        )
                        brand = brand_result.scalar_one_or_none()
                        plan = brand.plan if brand else "free"

                        return (candidate.brand_id, plan)

                return None

            except Exception as e:
                logger.error("API key authentication error: %s", str(e))
                await db.rollback()
                return None
