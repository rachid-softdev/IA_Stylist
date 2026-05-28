"""CSRF token generation and validation for cookie-based auth."""
import secrets
import hashlib
import hmac

from app.config import get_settings


def generate_csrf_token() -> str:
    """Generate a cryptographically secure CSRF token."""
    return secrets.token_urlsafe(32)


def sign_csrf_token(token: str) -> str:
    """Sign a CSRF token with the server secret to prevent tampering."""
    settings = get_settings()
    # CSRF_SECRET must be set independently of JWT_SECRET
    if not settings.CSRF_SECRET:
        raise RuntimeError("CSRF_SECRET must be configured independently of JWT_SECRET")
    secret = settings.CSRF_SECRET
    key = secret.encode("utf-8")
    return hmac.new(key, token.encode("utf-8"), hashlib.sha256).hexdigest()


def validate_csrf_token(cookie_token: str, header_token: str) -> bool:
    """Validate that the header CSRF token matches the signed cookie token.
    
    Uses timing-safe comparison to prevent timing attacks.
    
    Returns True if valid, False otherwise.
    """
    if not cookie_token or not header_token:
        return False
    
    # The cookie contains "raw_token.signed_token"
    # The header should contain just the raw_token
    parts = cookie_token.split(".", 1)
    if len(parts) != 2:
        return False
    
    raw_token, expected_sig = parts
    
    # Verify header_token matches raw_token
    if not hmac.compare_digest(raw_token, header_token):
        return False
    
    # Verify the signature
    actual_sig = sign_csrf_token(raw_token)
    return hmac.compare_digest(actual_sig, expected_sig)


def make_csrf_cookie_value() -> str:
    """Create a CSRF cookie value: raw_token.signed_token."""
    raw = generate_csrf_token()
    sig = sign_csrf_token(raw)
    return f"{raw}.{sig}"
