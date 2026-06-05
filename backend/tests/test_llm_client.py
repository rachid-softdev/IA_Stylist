"""Tests for LLM client."""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch


@pytest.mark.asyncio
async def test_chat_success():
    mock_response = AsyncMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "choices": [{"message": {"content": "Hello!"}}]
    }

    with patch("httpx.AsyncClient") as mock_client:
        mock_ctx = AsyncMock()
        mock_ctx.__aenter__.return_value.post = AsyncMock(return_value=mock_response)
        mock_client.return_value = mock_ctx

        from app.services.llm_client import LLMClient
        client = LLMClient()
        result = await client.chat(system="Be helpful", user="Say hello")

        assert result == "Hello!"


@pytest.mark.asyncio
async def test_chat_json_success():
    mock_response = AsyncMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "choices": [{"message": {"content": '{"answer": 42}'}}]
    }

    with patch("httpx.AsyncClient") as mock_client:
        mock_ctx = AsyncMock()
        mock_ctx.__aenter__.return_value.post = AsyncMock(return_value=mock_response)
        mock_client.return_value = mock_ctx

        from app.services.llm_client import LLMClient
        client = LLMClient()
        result = await client.chat_json(system="Be precise", user="What is 6*7?")

        assert result == {"answer": 42}


@pytest.mark.asyncio
async def test_chat_failure():
    with patch("httpx.AsyncClient") as mock_client:
        mock_ctx = AsyncMock()
        mock_ctx.__aenter__.return_value.post = AsyncMock(
            side_effect=Exception("API unavailable")
        )
        mock_client.return_value = mock_ctx

        from app.services.llm_client import LLMClient
        client = LLMClient()

        with pytest.raises(Exception):
            await client.chat(system="Test", user="Test")


@pytest.mark.asyncio
async def test_stylist_analyze_fallback():
    from app.services.ai.stylist import StylistAI

    ai = StylistAI()

    with patch.object(ai.llm, "chat_vision", side_effect=Exception("LLM down")):
        result = await ai.analyze_morphology(
            photo_url="https://example.com/photo.jpg",
            user_id="user-test",
        )

        assert result["morphologie"] == "standard"
        assert result["teint"] == "medium"


@pytest.mark.asyncio
async def test_stylist_recommend_fallback():
    from app.services.ai.stylist import StylistAI

    ai = StylistAI()

    with patch.object(ai.llm, "chat_json", side_effect=Exception("LLM down")):
        result = await ai.recommend_fit(
            morphology="athletic",
            garment_category="top",
            garment_fit="regular",
            user_id="user-test",
            garment_id="garment-test",
        )

        assert result["fit_score"] == 8
