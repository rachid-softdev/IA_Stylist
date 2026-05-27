"""Tests for brands API endpoints."""
import pytest
from app.main import app


@pytest.mark.asyncio
async def test_brands_endpoints_exist():
    """Verify new route paths work."""
    # Can't do full integration test without DB
    # Just verify the routes are registered
    routes = [route.path for route in app.routes]

    # Old paths should NOT exist anymore
    old_paths = [
        "/v1/brands/api-keys",
        "/v1/brands/members",
    ]
    for path in old_paths:
        assert path not in routes, f"Old path {path} should not exist"

    # New paths SHOULD exist
    new_paths = [
        "/v1/brands/{brand_id}/api-keys",
        "/v1/brands/{brand_id}/members",
        "/v1/brands/{brand_id}/api-keys/{key_id}",
        "/v1/brands/{brand_id}/members/{target_user_id}",
    ]
    for path in new_paths:
        assert path in routes, f"New path {path} should exist"
