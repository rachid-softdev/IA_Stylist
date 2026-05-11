import pytest
from unittest.mock import patch, AsyncMock
from app.services.ai.stylist import StylistAI


@pytest.mark.asyncio
async def test_analyze_morphology():
    stylist = StylistAI()
    result = await stylist.analyze_morphology("https://photo.url")

    assert "morphologie" in result
    assert "teint" in result
    assert result["morphologie"] in ["athletic", "slim", "curvy", "petite", "tall"]


@pytest.mark.asyncio
async def test_recommend_fit():
    stylist = StylistAI()
    result = await stylist.recommend_fit("athletic", "top", "regular")

    assert "fit_advice" in result
    assert "fit_score" in result
    assert 1 <= result["fit_score"] <= 10


@pytest.mark.asyncio
async def test_suggest_outfits():
    stylist = StylistAI()
    result = await stylist.suggest_outfits("athletic", [])

    assert isinstance(result, list)
    assert len(result) > 0
    assert "description" in result[0]
