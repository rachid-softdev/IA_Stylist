import hashlib
import hmac
import uuid
from datetime import datetime, timedelta

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
    """Verify an API key against its stored hash."""
    return hmac.compare_digest(_hash_key(raw_key), hashed_key)


def _hash_key(key: str) -> str:
    return hashlib.sha256(key.encode("utf-8")).hexdigest()


def extract_key_prefix(raw_key: str) -> str:
    parts = raw_key.split("_")
    if len(parts) >= 2:
        return f"{parts[0]}_{parts[1]}"
    return raw_key[:10]


def extract_key_last4(raw_key: str) -> str:
    return raw_key[-4:] if len(raw_key) >= 4 else raw_key


def generate_share_token() -> str:
    return uuid.uuid4().hex[:12]
