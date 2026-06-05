"""Tests for AI Stylist service."""
import pytest
from unittest.mock import patch, AsyncMock
from app.services.ai.stylist import StylistAI


@pytest.mark.asyncio
async def test_analyze_morphology():
    stylist = StylistAI()

    with patch.object(stylist.llm, "chat_vision", new_callable=AsyncMock) as mock_vision:
        mock_vision.return_value = {
            "morphologie": "athletic",
            "teint": "medium",
            "style_preference": "casual",
            "colors": ["bleu", "gris"],
        }

        result = await stylist.analyze_morphology(
            photo_url="https://photo.url",
            user_id="user-001",
        )

        assert result["morphologie"] == "athletic"
        assert result["teint"] == "medium"


@pytest.mark.asyncio
async def test_recommend_fit():
    stylist = StylistAI()

    with patch.object(stylist.llm, "chat_json", new_callable=AsyncMock) as mock_json:
        mock_json.return_value = {
            "fit_advice": "Coupe regular parfaite.",
            "style_tip": "Portez avec un jean.",
            "fit_score": 8,
        }

        result = await stylist.recommend_fit(
            morphology="athletic",
            garment_category="top",
            garment_fit="regular",
            user_id="user-001",
            garment_id="garment-001",
        )

        assert result["fit_score"] == 8
        assert "fit_advice" in result


@pytest.mark.asyncio
async def test_suggest_outfits():
    stylist = StylistAI()
    wardrobe = [
        {"name": "T-shirt Blanc", "category": "top", "id": "g-1"},
        {"name": "Jean Slim", "category": "bottom", "id": "g-2"},
    ]

    with patch.object(stylist.llm, "chat_json", new_callable=AsyncMock) as mock_json:
        mock_json.return_value = {
            "outfits": [
                {
                    "description": "Look casual chic",
                    "occasion": "daily",
                    "color_palette": ["blanc", "bleu"],
                    "items": ["T-shirt Blanc", "Jean Slim"],
                }
            ]
        }

        result = await stylist.suggest_outfits(
            morphology="athletic",
            wardrobe=wardrobe,
            user_id="user-001",
        )

        assert isinstance(result, list)
        assert len(result) > 0
        assert result[0]["occasion"] == "daily"


@pytest.mark.asyncio
async def test_analyze_morphology_cached():
    stylist = StylistAI()

    with patch.object(stylist, "_get_cache", new_callable=AsyncMock) as mock_cache:
        mock_cache.return_value = {
            "morphologie": "cached_value",
            "teint": "clair",
            "style_preference": "chic",
            "colors": ["noir"],
        }

        result = await stylist.analyze_morphology(
            photo_url="https://photo.url",
            user_id="user-cached",
        )

        assert result["morphologie"] == "cached_value"


@pytest.mark.asyncio
async def test_recommend_fit_fallback():
    stylist = StylistAI()

    with patch.object(stylist.llm, "chat_json", side_effect=Exception("API error")):
        result = await stylist.recommend_fit(
            morphology="slim",
            garment_category="dress",
            garment_fit="fitted",
            user_id="user-001",
            garment_id="garment-001",
        )

        assert result["fit_score"] == 8
