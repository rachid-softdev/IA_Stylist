import json
import logging
from typing import Optional

from app.config import get_settings
from app.services.redis import get_redis
from app.services.ws_manager import manager

logger = logging.getLogger(__name__)

settings = get_settings()

CHANNEL_WS_EVENTS = "ws:events"


async def push_job_update(
    user_id: str,
    job_id: str,
    status: str,
    result_url: Optional[str] = None,
    error_message: Optional[str] = None,
    progress: Optional[float] = None,
) -> None:
    payload = {
        "type": "job_update",
        "job_id": job_id,
        "status": status,
        "result_url": result_url,
        "error_message": error_message,
        "progress": progress,
        "user_id": user_id,
    }

    sent = await manager.send_to_user(user_id, payload)

    if sent == 0:
        try:
            r = await get_redis()
            await r.publish(CHANNEL_WS_EVENTS, json.dumps(payload))
        except Exception as e:
            logger.warning(
                "Redis publish failed: user=%s job=%s error=%s",
                user_id, job_id, str(e),
            )


async def push_brand_update(
    brand_id: str,
    payload: dict,
) -> None:
    sent = await manager.send_to_room(f"brand_{brand_id}", payload)
    if sent == 0:
        try:
            r = await get_redis()
            await r.publish(CHANNEL_WS_EVENTS, json.dumps({
                **payload,
                "_brand_id": brand_id,
            }))
        except Exception as e:
            logger.warning(
                "Redis publish brand update failed: brand=%s error=%s",
                brand_id, str(e),
            )
