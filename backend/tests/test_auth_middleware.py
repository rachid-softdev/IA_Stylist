"""Tests for auth middleware."""
import pytest


def test_auth_middleware_imports():
    """Verify jose is importable at module level."""
    from jose import jwt
    assert jwt is not None
