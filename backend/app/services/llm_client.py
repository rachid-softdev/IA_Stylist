import json
import logging
from typing import Optional
from app.config import get_settings

logger = logging.getLogger(__name__)

settings = get_settings()


class LLMClient:
    """Provider-agnostic LLM client (OpenAI-compatible)."""

    def __init__(self) -> None:
        self.api_key = settings.FAL_KEY or settings.KLING_API_KEY or ""
        self.api_url = "https://api.openai.com/v1/chat/completions"
        self.model = "gpt-4o"
        self.timeout = 30.0

    async def chat(
        self,
        system: str,
        user: str,
        temperature: float = 0.3,
        response_format: Optional[dict] = None,
    ) -> str:
        """Send a chat completion request."""
        import httpx

        messages = [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ]

        body = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": 1024,
        }

        if response_format:
            body["response_format"] = response_format

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                resp = await client.post(self.api_url, json=body, headers=headers)
                resp.raise_for_status()
                data = resp.json()
                return data["choices"][0]["message"]["content"]
        except Exception as e:
            logger.warning("LLM call failed: %s", str(e))
            raise

    async def chat_json(
        self,
        system: str,
        user: str,
        temperature: float = 0.3,
    ) -> dict:
        """Send a chat completion request and parse JSON response."""
        content = await self.chat(
            system=system,
            user=user,
            temperature=temperature,
            response_format={"type": "json_object"},
        )
        return json.loads(content)

    async def chat_vision(
        self,
        system: str,
        image_url: str,
        user: str,
        temperature: float = 0.3,
    ) -> dict:
        """Send a vision request with an image."""
        import httpx

        messages = [
            {"role": "system", "content": system},
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": user},
                    {"type": "image_url", "image_url": {"url": image_url}},
                ],
            },
        ]

        body = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": 1024,
            "response_format": {"type": "json_object"},
        }

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                resp = await client.post(self.api_url, json=body, headers=headers)
                resp.raise_for_status()
                data = resp.json()
                return json.loads(data["choices"][0]["message"]["content"])
        except Exception as e:
            logger.warning("LLM vision call failed: %s", str(e))
            raise
