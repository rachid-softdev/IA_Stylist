import pytest
from app.services.security import (
    generate_api_key,
    verify_api_key,
    extract_key_prefix,
    extract_key_last4,
    generate_share_token,
)


def test_generate_api_key():
    raw_key, hashed_key = generate_api_key()

    assert raw_key.startswith("vfs_live_")
    assert len(raw_key) > 20
    assert hashed_key != raw_key


def test_verify_api_key():
    raw_key, hashed_key = generate_api_key()

    assert verify_api_key(raw_key, hashed_key) is True
    assert verify_api_key("wrong_key", hashed_key) is False
    assert verify_api_key(raw_key, "wrong_hash") is False


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
