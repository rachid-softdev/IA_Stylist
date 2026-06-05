import asyncio
import json
import logging

from app.services.redis import get_redis
from app.services.ws_manager import manager
from app.services.websocket import CHANNEL_WS_EVENTS

logger = logging.getLogger(__name__)


async def listen_redis_events() -> None:
    try:
        r = await get_redis()
        pubsub = r.pubsub()
        await pubsub.subscribe(CHANNEL_WS_EVENTS)
        logger.info("Redis pub/sub listener started on channel: %s", CHANNEL_WS_EVENTS)

        async for message in pubsub.listen():
            if message["type"] != "message":
                continue
            try:
                data = json.loads(message["data"])
            except json.JSONDecodeError:
                continue

            brand_id = data.pop("_brand_id", None)
            user_id = data.get("user_id")

            if brand_id:
                await manager.send_to_room(f"brand_{brand_id}", data)
            elif user_id:
                await manager.send_to_user(user_id, data)
    except asyncio.CancelledError:
        logger.info("Redis pub/sub listener cancelled")
    except Exception as e:
        logger.error("Redis pub/sub listener error: %s", str(e))
