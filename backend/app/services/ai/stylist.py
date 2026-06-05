import logging
from typing import Optional
from app.services.llm_client import LLMClient
from app.services.redis import get_redis

logger = logging.getLogger(__name__)


class StylistAI:
    """AI Stylist — analyzes user profile and provides fashion advice using LLM."""

    MORPHOLOGY_PROMPT = """Tu es un styliste expert. Analyse la photo de l'utilisateur et détermine:
1. Morphologie (athletic, slim, standard, plus-size, pear, hourglass, rectangle)
2. Teint (clair, medium, olive, foncé, dark)
3. Style préféré (casual, chic, sportswear, bohème, classique, streetwear)
4. Couleurs recommandées (2-3 couleurs qui devraient aller à son teint)

Réponds en JSON strict avec les clés: morphologie, teint, style_preference, colors"""

    FIT_PROMPT = """Tu es un styliste expert. Analyse la morphologie de l'utilisateur et le vêtement choisi, puis donne:
1. Un conseil de taille et coupe (fit_advice) — précis et personnalisé
2. Un conseil style (style_tip) — comment porter ce vêtement
3. Un score de compatibilité (fit_score) de 1 à 10

Morphologie: {morphology}
Catégorie vêtement: {garment_category}
Type de coupe: {garment_fit}

Réponds en JSON strict avec les clés: fit_advice, style_tip, fit_score"""

    OUTFIT_PROMPT = """Tu es un styliste expert. Basé sur la morphologie de l'utilisateur et sa garde-robe, 
suggère 3 tenues complètes adaptées à différentes occasions.

Morphologie: {morphology}
Garde-robe disponible: {wardrobe}

Pour chaque tenue, fournis:
- description: description détaillée de la tenue
- occasion: daily, work, evening, sport, weekend
- color_palette: liste de 2-3 couleurs clés
- items: liste des vêtements qui composent la tenue

Réponds en JSON strict avec une clé 'outfits' contenant un tableau."""

    def __init__(self) -> None:
        self.llm = LLMClient()

    async def _get_cache(self, key: str) -> Optional[dict]:
        try:
            r = await get_redis()
            data = await r.get(key)
            if data:
                import json
                return json.loads(data)
        except Exception:
            pass
        return None

    async def _set_cache(self, key: str, value: dict, ttl: int = 86400) -> None:
        try:
            r = await get_redis()
            import json
            await r.setex(key, ttl, json.dumps(value))
        except Exception:
            pass

    async def analyze_morphology(self, photo_url: str, user_id: str) -> dict:
        cache_key = f"stylist:morphology:{user_id}"
        cached = await self._get_cache(cache_key)
        if cached:
            return cached

        try:
            result = await self.llm.chat_vision(
                system=self.MORPHOLOGY_PROMPT,
                image_url=photo_url,
                user="Analyse cette photo et détermine ma morphologie.",
            )
            await self._set_cache(cache_key, result)
            return result
        except Exception as e:
            logger.warning("Morphology analysis failed for %s: %s", user_id, str(e))
            return {
                "morphologie": "standard",
                "teint": "medium",
                "style_preference": "casual",
                "colors": ["neutre", "bleu", "gris"],
            }

    async def recommend_fit(
        self,
        morphology: str,
        garment_category: str,
        garment_fit: str,
        user_id: str,
        garment_id: str,
    ) -> dict:
        cache_key = f"stylist:fit:{user_id}:{garment_id}"
        cached = await self._get_cache(cache_key)
        if cached:
            return cached

        try:
            prompt = self.FIT_PROMPT.format(
                morphology=morphology,
                garment_category=garment_category,
                garment_fit=garment_fit,
            )
            result = await self.llm.chat_json(
                system="Tu es un styliste expert. Réponds en JSON strict.",
                user=prompt,
            )
            await self._set_cache(cache_key, result)
            return result
        except Exception as e:
            logger.warning("Fit recommendation failed: %s", str(e))
            return {
                "fit_advice": "Cette coupe devrait convenir à votre morphologie.",
                "style_tip": "Associez avec des pièces neutres pour un look équilibré.",
                "fit_score": 8,
            }

    async def suggest_outfits(
        self,
        morphology: str,
        wardrobe: list[dict],
        user_id: str,
    ) -> list[dict]:
        cache_key = f"stylist:outfits:{user_id}"
        cached = await self._get_cache(cache_key)
        if cached:
            return cached.get("outfits", [])

        try:
            wardrobe_str = ", ".join([f"{w.get('name','')} ({w.get('category','')})" for w in wardrobe])
            prompt = self.OUTFIT_PROMPT.format(
                morphology=morphology,
                wardrobe=wardrobe_str or "Garde-robe vide",
            )
            result = await self.llm.chat_json(
                system="Tu es un styliste expert. Réponds en JSON strict.",
                user=prompt,
            )
            outfits = result.get("outfits", [])
            await self._set_cache(cache_key, {"outfits": outfits})
            return outfits
        except Exception as e:
            logger.warning("Outfit suggestion failed: %s", str(e))
            return []
