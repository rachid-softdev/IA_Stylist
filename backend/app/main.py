from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import sentry_sdk

from app.config import get_settings
from app.middleware.logging import LoggingMiddleware
from app.middleware.auth_middleware import AuthMiddleware
from app.middleware.rate_limit import RateLimitMiddleware
from app.routers import auth, upload, generate, credits, dressing, brands, catalog, analytics, webhooks, stylist

settings = get_settings()

# Sentry
if settings.SENTRY_DSN:
    sentry_sdk.init(
        dsn=settings.SENTRY_DSN,
        environment=settings.ENVIRONMENT,
        traces_sample_rate=0.1,
    )


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    from app.services.storage import ensure_bucket_exists

    try:
        ensure_bucket_exists()
    except Exception:
        pass
    yield
    # Shutdown
    from app.services.redis import close_redis
    await close_redis()


app = FastAPI(
    title="Virtual Fashion Studio API",
    version="1.0.0",
    description="AI Fashion Visualization Platform — Try-On, Video, AI Stylist",
    docs_url="/api/docs" if settings.ENVIRONMENT != "production" else None,
    redoc_url=None,
    lifespan=lifespan,
)

# Middleware — Starlette wraps inside-out, so LAST registered = outermost = runs FIRST
# Desired execution: CORS → Auth → RateLimit → Logging → handler
# So register in reverse: Logging (innermost) → RateLimit → Auth → CORS (outermost)
app.add_middleware(LoggingMiddleware)

app.add_middleware(RateLimitMiddleware)

app.add_middleware(AuthMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH"],
    allow_headers=["Content-Type", "Authorization", "X-Request-ID", "X-CSRF-Token", "X-Requested-With"],
)

# Routers
app.include_router(auth.router, prefix="/v1/auth", tags=["Auth"])
app.include_router(upload.router, prefix="/v1/upload", tags=["Upload"])
app.include_router(generate.router, prefix="/v1/generate", tags=["Generate"])
app.include_router(credits.router, prefix="/v1/credits", tags=["Credits"])
app.include_router(dressing.router, prefix="/v1/dressing", tags=["Dressing"])
app.include_router(brands.router, prefix="/v1/brands", tags=["Brands"])
app.include_router(catalog.router, prefix="/v1/catalog", tags=["Catalog"])
app.include_router(analytics.router, prefix="/v1/analytics", tags=["Analytics"])
app.include_router(webhooks.router, prefix="/v1/webhooks", tags=["Webhooks"])
app.include_router(stylist.router, prefix="/v1/stylist", tags=["AI Stylist"])


@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring."""
    import time

    return {
        "status": "healthy",
        "version": "1.0.0",
        "environment": settings.ENVIRONMENT,
        "timestamp": int(time.time()),
    }


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={
            "data": None,
            "error": {
                "code": "INTERNAL_ERROR",
                "message": "An unexpected error occurred",
            },
        },
    )
