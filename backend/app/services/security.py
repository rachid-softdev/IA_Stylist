import bcrypt
import uuid

from app.config import get_settings
from app.models.brand import Brand

settings = get_settings()


def generate_api_key() -> tuple[str, str]:
    """Generate an API key. Returns (raw_key, hashed_key)."""
    raw = f"vfs_live_{uuid.uuid4().hex}"
    hashed = _hash_key(raw)
    return raw, hashed


def hash_api_key(raw_key: str) -> str:
    return _hash_key(raw_key)


def verify_api_key(raw_key: str, hashed_key: str) -> bool:
    """Verify an API key against its stored bcrypt hash."""
    return bcrypt.checkpw(raw_key.encode("utf-8"), hashed_key.encode("utf-8"))


def _hash_key(key: str) -> str:
    return bcrypt.hashpw(key.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def extract_key_prefix(raw_key: str) -> str:
    parts = raw_key.split("_")
    if len(parts) >= 2:
        return f"{parts[0]}_{parts[1]}"
    return raw_key[:10]


def extract_key_last4(raw_key: str) -> str:
    return raw_key[-4:] if len(raw_key) >= 4 else raw_key


def generate_share_token() -> str:
    return uuid.uuid4().hex[:12]


async def verify_ws_token(token: str) -> str | None:
    """Verify a JWT token for WebSocket connections.
    
    Supports both Supabase JWT and API key authentication.
    Returns the user_id if valid, None otherwise.
    """
    import httpx
    
    settings = get_settings()
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"{settings.SUPABASE_URL}/auth/v1/user",
                headers={
                    "Authorization": f"Bearer {token}",
                    "apikey": settings.SUPABASE_ANON_KEY,
                },
                timeout=5.0,
            )
            if resp.status_code == 200:
                return resp.json().get("id")
    except Exception:
        pass
    return None
