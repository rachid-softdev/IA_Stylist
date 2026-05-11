import pytest
from unittest.mock import patch, AsyncMock
from app.services.ai.fal_client import FalClient
from app.services.ai.replicate_client import ReplicateClient
from app.services.ai.router import AIRouter


@pytest.mark.asyncio
async def test_router_fal_primary():
    """Test that router uses fal.ai as primary provider."""
    router = AIRouter()

    with patch.object(router.fal, 'generate_tryon', new_callable=AsyncMock) as mock_fal:
        mock_fal.return_value = "https://result.url/image.webp"

        result, provider = await router.generate_tryon(
            model_photo="https://photo.url",
            garment_image="https://garment.url",
            category="upper_body",
        )

        assert result == "https://result.url/image.webp"
        assert provider == "fal"
        mock_fal.assert_called_once()


@pytest.mark.asyncio
async def test_router_fallback_to_replicate():
    """Test that router falls back to Replicate when fal fails."""
    router = AIRouter()

    with patch.object(router.fal, 'generate_tryon', new_callable=AsyncMock) as mock_fal, \
         patch.object(router.replicate, 'generate_tryon', new_callable=AsyncMock) as mock_rep:

        mock_fal.return_value = None
        mock_rep.return_value = "https://replicate.result/image.webp"

        result, provider = await router.generate_tryon(
            model_photo="https://photo.url",
            garment_image="https://garment.url",
            category="upper_body",
        )

        assert result == "https://replicate.result/image.webp"
        assert provider == "replicate"


@pytest.mark.asyncio
async def test_circuit_breaker_opens():
    """Test that circuit breaker opens after repeated failures."""
    router = AIRouter()

    with patch.object(router.fal, 'generate_tryon', new_callable=AsyncMock) as mock_fal, \
         patch.object(router.replicate, 'generate_tryon', new_callable=AsyncMock) as mock_rep:

        mock_fal.return_value = None
        mock_rep.return_value = "https://replicate.result/image.webp"

        # Cause repeated failures
        for _ in range(6):
            await router.generate_tryon("photo", "garment", "upper_body")

        # Circuit should be open after threshold
        assert router._circuit_open is True
