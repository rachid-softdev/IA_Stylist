import random
import httpx
from typing import Optional
from app.config import get_settings

settings = get_settings()


class FalClient:
    """Client for fal.ai — IDM-VTON, CatVTON, FLUX models."""

    def __init__(self):
        self.base_url = "https://fal.run"
        self.api_key = settings.FAL_KEY

    async def generate_tryon(
        self,
        model_photo_url: str,
        garment_image_url: str,
        category: str = "upper_body",
        steps: int = 30,
        seed: Optional[int] = None,
    ) -> Optional[str]:
        """Submit a try-on generation job to fal.ai."""
        endpoint = f"{self.base_url}/fal-ai/idm-vton"

        payload = {
            "human_image_url": model_photo_url,
            "garment_image_url": garment_image_url,
            "category": category,
            "num_inference_steps": steps,
            "seed": seed or random.randint(1, 2**31 - 1),
        }

        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(
                endpoint,
                json=payload,
                headers={
                    "Authorization": f"Key {self.api_key}",
                    "Content-Type": "application/json",
                },
            )

            if response.status_code == 200:
                data = response.json()
                # Extract result URL
                images = data.get("images", [])
                if images and len(images) > 0:
                    return images[0].get("url", "")

            response.raise_for_status()

        return None

    async def health_check(self) -> bool:
        """Check if fal.ai API is available."""
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(
                    "https://fal.run/fal-ai/idm-vton",
                    headers={"Authorization": f"Key {self.api_key}"},
                )
                return response.status_code < 500
        except Exception:
            return False
