from pydantic_settings import BaseSettings
from pydantic import model_validator
from typing import Optional
from functools import lru_cache


class Settings(BaseSettings):
    # Environment
    ENVIRONMENT: str = "local"

    # Database
    DATABASE_URL: str = ""  # Must be set via .env
    DATABASE_URL_SYNC: str = ""  # Must be set via .env

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # Supabase Auth
    SUPABASE_URL: str = ""
    SUPABASE_ANON_KEY: str = ""
    SUPABASE_SERVICE_ROLE_KEY: str = ""
    SUPABASE_REALTIME_KEY: str = ""  # Optional; falls back to SERVICE_ROLE_KEY

    # JWT
    JWT_SECRET: str = ""  # Must be set via .env
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 30

    # CSRF
    CSRF_SECRET: str = ""  # Must be set independently from JWT_SECRET

    # Cloudflare R2
    R2_ACCESS_KEY: str = ""
    R2_SECRET_KEY: str = ""
    R2_ENDPOINT: str = ""
    R2_BUCKET: str = "vfs-storage"
    R2_PUBLIC_URL: str = ""  # Must be set via .env (e.g. https://cdn.vfs.ai)

    # AI Services
    FAL_KEY: str = ""
    REPLICATE_API_TOKEN: str = ""
    KLING_API_KEY: str = ""

    # Stripe
    STRIPE_SECRET_KEY: str = ""
    STRIPE_WEBHOOK_SECRET: str = ""

    # Monitoring
    SENTRY_DSN: Optional[str] = None
    AXIOM_TOKEN: Optional[str] = None
    POSTHOG_KEY: Optional[str] = None

    # Security
    CORS_ORIGINS: str = "http://localhost:3000,http://localhost:5173"
    RATE_LIMIT_FREE: int = 10
    RATE_LIMIT_PRO: int = 100
    RATE_LIMIT_BRAND: int = 1000

    # Business
    CREDITS_FREE_PER_MONTH: int = 10
    CREDITS_PRO_PER_MONTH: int = 100
    CREDITS_CREATOR_PER_MONTH: int = 500
    MAX_UPLOAD_SIZE_MB: int = 10
    MIN_RESOLUTION_PX: int = 512

    # Job queue
    CELERY_BROKER_URL: Optional[str] = None
    CELERY_RESULT_BACKEND: Optional[str] = None

    @model_validator(mode="after")
    def validate_critical_settings(self):
        """Validate critical settings across all environments.

        In production: fail hard on missing settings.
        In non-production: warn only (to avoid breaking local dev).
        """
        critical_settings = {
            "DATABASE_URL": self.DATABASE_URL,
            "JWT_SECRET": self.JWT_SECRET,
            "CSRF_SECRET": self.CSRF_SECRET,
        }
        missing = [name for name, value in critical_settings.items() if not value]

        if not missing:
            return self

        msg = f"Missing required settings: {', '.join(missing)}. Set them via .env or environment variables."

        if self.ENVIRONMENT == "production":
            raise ValueError(msg)

        import warnings
        warnings.warn(f"{msg} — app may fail at runtime")
        return self

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": True,
    }

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]

    @property
    def allowed_image_types(self) -> list[str]:
        return ["image/jpeg", "image/png", "image/webp"]

    @property
    def rate_limits(self) -> dict[str, int]:
        return {
            "free": self.RATE_LIMIT_FREE,
            "pro": self.RATE_LIMIT_PRO,
            "brand": self.RATE_LIMIT_BRAND,
        }

    @property
    def r2_endpoint_url(self) -> str:
        ep = self.R2_ENDPOINT.strip()
        if ep.startswith("https://") or ep.startswith("http://"):
            return ep
        return f"https://{ep}"


@lru_cache()
def get_settings() -> Settings:
    return Settings()
