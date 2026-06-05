import asyncio
import json
import logging
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query, status
from sqlalchemy import select
from app.services.ws_manager import manager
from app.services.security import verify_ws_token
from app.db.session import async_session
from app.models.brand import BrandMember

logger = logging.getLogger(__name__)

router = APIRouter()

MAX_CONNECTIONS_PER_USER = 5


async def verify_brand_membership(user_id: str, brand_id: str) -> bool:
    try:
        async with async_session() as db:
            result = await db.execute(
                select(BrandMember).where(
                    BrandMember.brand_id == brand_id,
                    BrandMember.user_id == user_id,
                )
            )
            return result.scalar_one_or_none() is not None
    except Exception:
        return False


@router.websocket("/ws")
async def websocket_endpoint(
    ws: WebSocket,
    token: str = Query(...),
    brand_id: str = Query(default=None),
):
    user_id = await verify_ws_token(token)
    if not user_id:
        await ws.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    if manager.get_user_connection_count(user_id) >= MAX_CONNECTIONS_PER_USER:
        await ws.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    await manager.connect(user_id, ws)

    if brand_id:
        if await verify_brand_membership(user_id, brand_id):
            manager.join_room(f"brand_{brand_id}", ws)

    await manager.send_to_user(user_id, {
        "type": "connected",
        "user_id": user_id,
    })

    heartbeat_task = None

    async def heartbeat():
        while True:
            await asyncio.sleep(25)
            try:
                await ws.send_json({"type": "ping"})
            except Exception:
                break

    heartbeat_task = asyncio.create_task(heartbeat())

    try:
        while True:
            data = await ws.receive_text()
            try:
                msg = json.loads(data)
            except json.JSONDecodeError:
                continue

            msg_type = msg.get("type")

            if msg_type == "pong":
                continue

            if msg_type == "subscribe_brand" and "brand_id" in msg:
                sub_brand_id = msg["brand_id"]
                if await verify_brand_membership(user_id, sub_brand_id):
                    manager.join_room(f"brand_{sub_brand_id}", ws)
                    await manager.send_to_user(user_id, {
                        "type": "subscribed",
                        "brand_id": sub_brand_id,
                    })
                else:
                    await manager.send_to_user(user_id, {
                        "type": "error",
                        "message": "Not a member of this brand",
                    })
                continue

            if msg_type == "unsubscribe_brand" and "brand_id" in msg:
                manager.leave_room(f"brand_{msg['brand_id']}", ws)
                continue

    except WebSocketDisconnect:
        pass
    except Exception as e:
        logger.warning("WebSocket error user=%s: %s", user_id, str(e))
    finally:
        if heartbeat_task:
            heartbeat_task.cancel()
        manager.disconnect(user_id, ws)
