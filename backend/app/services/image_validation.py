import logging
from typing import Optional
import httpx

logger = logging.getLogger(__name__)


async def validate_garment_image(image_url: str) -> dict:
    """Validate a garment image for quality and suitability.
    
    Returns:
        dict with keys: valid (bool), score (int), reasons (list[str])
    """
    reasons = []
    score = 100

    # Check resolution via HTTP HEAD
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.head(image_url, timeout=10)
            content_type = resp.headers.get("content-type", "")
            content_length = int(resp.headers.get("content-length", 0))

            if "image" not in content_type:
                reasons.append(f"Invalid content type: {content_type}")
                score -= 30

            if content_length < 1024:
                reasons.append("Image too small (< 1KB)")
                score -= 20

            if content_length > 20 * 1024 * 1024:
                reasons.append("Image too large (> 20MB)")
                score -= 10

    except Exception as e:
        reasons.append(f"Cannot access image URL: {str(e)}")
        score -= 40

    # For now, we do basic checks. In production, add:
    # - Background detection (white/transparent)
    # - Garment detection via object detection model
    # - Resolution check via PIL (would require downloading)

    valid = score >= 60 and len(reasons) == 0

    if not valid and not reasons:
        reasons.append("Quality check failed")

    return {
        "valid": valid,
        "score": max(0, score),
        "reasons": reasons,
    }


async def validate_batch_garments(image_urls: list[str]) -> list[dict]:
    import asyncio
    results = await asyncio.gather(
        *[validate_garment_image(url) for url in image_urls],
        return_exceptions=True,
    )
    return [
        r if isinstance(r, dict) else {"valid": False, "score": 0, "reasons": [str(r)]}
        for r in results
    ]
