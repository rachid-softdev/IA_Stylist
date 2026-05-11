import httpx
import time
from typing import Optional
from app.config import get_settings

settings = get_settings()


class KlingClient:
    """Client for Kling API — video generation."""

    def __init__(self):
        self.api_key = settings.KLING_API_KEY

    async def generate_video(
        self,
        image_url: str,
        video_type: str = "runway_walk",
    ) -> Optional[str]:
        """Generate a fashion video from a still image."""
        async with httpx.AsyncClient(timeout=300.0) as client:
            response = await client.post(
                "https://api.kling.kuaishou.com/v1/videos/image2video",
                json={
                    "image": image_url,
                    "mode": "std",
                    "duration": 6,
                    "cfg_scale": 0.5,
                },
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                },
            )

            if response.status_code != 200:
                return None

            data = response.json()
            task_id = data.get("data", {}).get("task_id")

            if not task_id:
                return None

            # Poll for completion
            for _ in range(60):  # Max 300 seconds (5 min)
                poll_response = await client.get(
                    f"https://api.kling.kuaishou.com/v1/videos/image2video/{task_id}",
                    headers={"Authorization": f"Bearer {self.api_key}"},
                )

                if poll_response.status_code != 200:
                    break

                poll_data = poll_response.json()
                task_status = poll_data.get("data", {}).get("task_status")

                if task_status == "succeed":
                    videos = poll_data.get("data", {}).get("task_result", {}).get("videos", [])
                    if videos and len(videos) > 0:
                        return videos[0].get("url", "")
                    break
                elif task_status == "failed":
                    break

                import asyncio
                await asyncio.sleep(5)

        return None
