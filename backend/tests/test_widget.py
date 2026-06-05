"""Tests for widget API endpoints."""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi import HTTPException, status

from app.main import app


@pytest.mark.asyncio
async def test_widget_auth_invalid_key():
    mock_db = AsyncMock()

    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = []

    mock_db.execute.return_value = mock_result

    with patch("app.dependencies.get_db", return_value=mock_db):
        from app.routers.widget import widget_auth

        with pytest.raises(HTTPException) as exc:
            await widget_auth(api_key="invalid_key", db=mock_db)
        assert exc.value.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.asyncio
async def test_widget_track_returns_ok():
    mock_request = AsyncMock()
    mock_request.json.return_value = {"event": "widget_loaded"}

    from app.routers.widget import widget_track

    result = await widget_track(request=mock_request)
    assert result["status"] == "ok"


def test_widget_routes_registered():
    routes = [route.path for route in app.routes]
    assert "/v1/widget/auth" in routes
    assert "/v1/widget/generate" in routes
    assert "/v1/widget/track" in routes
