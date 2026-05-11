import structlog
from typing import Optional

logger = structlog.get_logger()


class StylistAI:
    """AI Stylist — analyzes user profile and provides fashion advice."""

    SYSTEM_PROMPT = """Tu es un styliste expert. Analyse la morphologie 
et donne des conseils précis, directs, personnalisés.
Format JSON strict."""

    async def analyze_morphology(self, photo_url: str) -> dict:
        """
        Analyze user morphology from photos.
        In production: calls vision LLM (GPT-4o / Claude).
        """
        # Placeholder — would use GPT-4o Vision API
        return {
            "morphologie": "athletic",
            "teint": "medium",
            "style_preference": "casual",
            "colors": ["neutre", "terracotta", "sauge"],
        }

    async def recommend_fit(
        self,
        morphology: str,
        garment_category: str,
        garment_fit: str,
    ) -> dict:
        """Recommend fit and style for a specific garment."""
        # Placeholder
        return {
            "fit_advice": "La coupe regular conviendra bien.",
            "style_tip": "Portez-le avec un pantalon fluide.",
            "fit_score": 8,
        }

    async def suggest_outfits(
        self,
        morphology: str,
        wardrobe: list[dict],
    ) -> list[dict]:
        """Suggest complete outfits from a wardrobe."""
        # Placeholder
        return [
            {
                "description": "Look casual chic pour le quotidien",
                "occasion": "daily",
                "color_palette": ["sable", "brun", "terracotta"],
            }
        ]
