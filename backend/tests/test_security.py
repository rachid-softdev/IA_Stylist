"""Tests for security utilities (bcrypt-based API key hashing)."""
import pytest
from app.services.security import (
    generate_api_key,
    verify_api_key,
    hash_api_key,
    extract_key_prefix,
    extract_key_last4,
    generate_share_token,
)

# A string that has valid bcrypt format but will never match any key
_VALID_BCRYPT_HASH = "$2b$12$LJ3m4ys3Lk0TSwHnbfOTiO7jRXYqFv7H1YqQ8nYZhZ9x5XvZ5q"


def test_generate_api_key():
    raw_key, hashed_key = generate_api_key()

    assert raw_key.startswith("vfs_live_")
    assert len(raw_key) > 20
    assert hashed_key != raw_key
    # Verify bcrypt output
    assert hashed_key.startswith("$2b$"), "bcrypt hash must start with $2b$"


def test_verify_api_key():
    raw_key, hashed_key = generate_api_key()

    assert verify_api_key(raw_key, hashed_key) is True
    assert verify_api_key("wrong_key", hashed_key) is False
    # wrong_hash must be a valid bcrypt string (not arbitrary text),
    # otherwise bcrypt.checkpw raises ValueError
    assert verify_api_key(raw_key, _VALID_BCRYPT_HASH) is False


def test_verify_api_key_wrong_key_format():
    """Passing an invalid bcrypt hash should raise ValueError."""
    raw_key, _ = generate_api_key()
    with pytest.raises(ValueError, match="Invalid salt"):
        verify_api_key(raw_key, "not-a-bcrypt-hash")


def test_hash_api_key():
    """hash_api_key must produce a bcrypt hash."""
    raw = "vfs_live_testkey1234567890"
    hashed = hash_api_key(raw)
    assert hashed.startswith("$2b$"), "bcrypt hash must start with $2b$"
    # Verify it round-trips
    assert verify_api_key(raw, hashed) is True


def test_bcrypt_hash_prefix():
    """All bcrypt hashes must start with $2b$."""
    _, hashed = generate_api_key()
    assert hashed.startswith("$2b$")
    # Verify length: $2b$12$ + 53 chars = 60 total
    assert len(hashed) == 60, "bcrypt hash should be 60 characters"


def test_bcrypt_is_deterministic_with_salt():
    """Same key must produce different hashes each time (unique salt)."""
    key = "vfs_live_testkey1234567890"
    hash1 = hash_api_key(key)
    hash2 = hash_api_key(key)
    assert hash1 != hash2, "unique salt should produce different hashes"
    # Both must verify correctly
    assert verify_api_key(key, hash1) is True
    assert verify_api_key(key, hash2) is True


def test_extract_key_prefix():
    raw_key, _ = generate_api_key()
    prefix = extract_key_prefix(raw_key)
    assert prefix == "vfs_live"


def test_extract_key_last4():
    raw_key, _ = generate_api_key()
    last4 = extract_key_last4(raw_key)
    assert len(last4) == 4
    assert last4 == raw_key[-4:]


def test_generate_share_token():
    token = generate_share_token()
    assert len(token) == 12
    assert isinstance(token, str)
