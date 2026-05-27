import json
import logging
from typing import Optional
import httpx
from app.config import get_settings

logger = logging.getLogger(__name__)

settings = get_settings()


async def push_job_update(
    user_id: str,
    job_id: str,
    status: str,
    result_url: Optional[str] = None,
    error_message: Optional[str] = None,
    progress: Optional[float] = None,
) -> None:
    """
    Push a job status update via Supabase Realtime.
    Falls back to no-op if Realtime is not configured.
    """
    payload = {
        "type": "job_update",
        "job_id": job_id,
        "status": status,
        "result_url": result_url,
        "error_message": error_message,
        "progress": progress,
        "user_id": user_id,
    }

    try:
        # Publish via Supabase Realtime REST API
        async with httpx.AsyncClient() as client:
            await client.post(
                f"{settings.SUPABASE_URL}/rest/v1/rpc/publish",
                headers={
                    "apikey": settings.SUPABASE_SERVICE_ROLE_KEY,
                    "Authorization": f"Bearer {settings.SUPABASE_SERVICE_ROLE_KEY}",
                    "Content-Type": "application/json",
                },
                json={
                    "channel": f"user_{user_id}",
                    "payload": json.dumps(payload),
                },
                timeout=5.0,
            )
    except Exception as e:
        logger.warning(
            "WebSocket push failed: user=%s job=%s status=%s error=%s",
            user_id, job_id, status, str(e),
        )
