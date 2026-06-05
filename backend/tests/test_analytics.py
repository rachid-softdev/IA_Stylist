"""Tests for analytics API endpoints."""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime

from app.main import app


@pytest.mark.asyncio
async def test_get_overview_returns_kpis():
    mock_db = AsyncMock()

    mock_count = MagicMock()
    mock_count.scalar.return_value = 42

    mock_time = MagicMock()
    mock_time.all.return_value = [
        MagicMock(date="2025-01-01", count=10),
        MagicMock(date="2025-01-02", count=15),
    ]

    mock_top = MagicMock()
    mock_top.all.return_value = [
        MagicMock(garment_id="g-1", name="T-shirt", sku="TS-001", count=20),
    ]

    mock_db.execute.side_effect = [
        mock_count,  # total_tryons current
        mock_count,  # previous tryons
        mock_time,   # time series
        mock_top,    # top skus
        mock_count,  # total all
    ]

    with patch("app.routers.analytics.verify_brand_admin_access", return_value="brand-001"):
        from app.routers.analytics import get_overview

        result = await get_overview(brand_id="brand-001", db=mock_db, days=30)
        assert "data" in result
        assert result["data"]["total_tryons"] == 42
        assert result["data"]["returns_saved"] > 0
        assert result["data"]["cost_savings"] > 0


@pytest.mark.asyncio
async def test_get_overview_empty():
    mock_db = AsyncMock()

    mock_zero = MagicMock()
    mock_zero.scalar.return_value = 0

    mock_empty = MagicMock()
    mock_empty.all.return_value = []

    mock_db.execute.side_effect = [
        mock_zero,
        mock_zero,
        mock_empty,
        mock_empty,
        mock_zero,
    ]

    with patch("app.routers.analytics.verify_brand_admin_access", return_value="brand-001"):
        from app.routers.analytics import get_overview

        result = await get_overview(brand_id="brand-001", db=mock_db, days=30)
        assert result["data"]["total_tryons"] == 0
        assert result["time_series"] == []
        assert result["top_skus"] == []


def test_analytics_routes_registered():
    routes = [route.path for route in app.routes]
    assert "/v1/analytics/{brand_id}/overview" in routes
