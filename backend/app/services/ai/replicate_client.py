import httpx
from typing import Optional
from app.config import get_settings

settings = get_settings()


class ReplicateClient:
    """Client for Replicate — fallback try-on models."""

    def __init__(self):
        self.api_token = settings.REPLICATE_API_TOKEN

    async def generate_tryon(
        self,
        model_photo_url: str,
        garment_image_url: str,
        category: str = "upper_body",
    ) -> Optional[str]:
        """Submit a try-on generation to Replicate (Kolors VTON)."""
        async with httpx.AsyncClient(timeout=120.0) as client:
            # Create prediction
            response = await client.post(
                "https://api.replicate.com/v1/predictions",
                json={
                    "version": "kolors-virtual-try-on",
                    "input": {
                        "human_image": model_photo_url,
                        "garment_image": garment_image_url,
                        "category": category,
                    },
                },
                headers={
                    "Authorization": f"Token {self.api_token}",
                    "Content-Type": "application/json",
                },
            )

            if response.status_code != 201:
                response.raise_for_status()

            prediction = response.json()
            prediction_id = prediction["id"]

            # Poll for completion
            while True:
                poll_response = await client.get(
                    f"https://api.replicate.com/v1/predictions/{prediction_id}",
                    headers={"Authorization": f"Token {self.api_token}"},
                )

                if poll_response.status_code != 200:
                    break

                poll_data = poll_response.json()
                status = poll_data.get("status")

                if status == "succeeded":
                    output = poll_data.get("output")
                    if isinstance(output, list) and len(output) > 0:
                        return output[0]
                    elif isinstance(output, str):
                        return output
                    break
                elif status in ("failed", "canceled"):
                    break

                # Wait before polling again
                import asyncio
                await asyncio.sleep(2)

        return None

    async def health_check(self) -> bool:
        """Check if Replicate API is available."""
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(
                    "https://api.replicate.com/v1/models",
                    headers={"Authorization": f"Token {self.api_token}"},
                )
                return response.status_code < 500
        except Exception:
            return False
