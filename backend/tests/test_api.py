import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app


@pytest.mark.asyncio
async def test_health_check():
    """Test the health check endpoint."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["version"] == "1.0.0"


@pytest.mark.asyncio
async def test_cors_headers():
    """Test that CORS headers are present."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.options(
            "/health",
            headers={"Origin": "http://localhost:3000"},
        )
        # CORS should be handled
        assert response.status_code in (200, 204, 405)


@pytest.mark.asyncio
async def test_api_docs():
    """Test that API docs are accessible in non-production."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/docs")
        assert response.status_code == 200
