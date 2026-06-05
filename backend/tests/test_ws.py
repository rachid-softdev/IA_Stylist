import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from fastapi import WebSocket
from app.services.ws_manager import ConnectionManager


@pytest.fixture
def manager():
    return ConnectionManager()


@pytest.mark.asyncio
async def test_connect_and_disconnect(manager):
    ws = AsyncMock(spec=WebSocket)
    ws.send_json = AsyncMock()

    await manager.connect("user_1", ws)
    assert manager.active_users == 1
    assert manager.active_connections == 1

    manager.disconnect("user_1", ws)
    assert manager.active_users == 0
    assert manager.active_connections == 0


@pytest.mark.asyncio
async def test_send_to_user(manager):
    ws = AsyncMock(spec=WebSocket)
    ws.send_json = AsyncMock()
    payload = {"type": "test", "data": "hello"}

    await manager.connect("user_1", ws)
    count = await manager.send_to_user("user_1", payload)
    assert count == 1
    ws.send_json.assert_called_once_with(payload)


@pytest.mark.asyncio
async def test_send_to_user_no_connection(manager):
    count = await manager.send_to_user("nonexistent", {"type": "test"})
    assert count == 0


@pytest.mark.asyncio
async def test_room_join_and_leave(manager):
    ws = AsyncMock(spec=WebSocket)
    ws.send_json = AsyncMock()
    payload = {"type": "brand_update"}

    await manager.connect("user_1", ws)
    manager.join_room("brand_abc", ws)

    count = await manager.send_to_room("brand_abc", payload)
    assert count == 1
    ws.send_json.assert_called_with(payload)

    manager.leave_room("brand_abc", ws)
    count = await manager.send_to_room("brand_abc", payload)
    assert count == 0


@pytest.mark.asyncio
async def test_broadcast(manager):
    ws1 = AsyncMock(spec=WebSocket)
    ws2 = AsyncMock(spec=WebSocket)
    ws1.send_json = AsyncMock()
    ws2.send_json = AsyncMock()
    payload = {"type": "broadcast"}

    await manager.connect("user_1", ws1)
    await manager.connect("user_2", ws2)

    count = await manager.broadcast(payload)
    assert count == 2
    ws1.send_json.assert_called_with(payload)
    ws2.send_json.assert_called_with(payload)


@pytest.mark.asyncio
async def test_disconnect_removes_from_rooms(manager):
    ws = AsyncMock(spec=WebSocket)
    ws.send_json = AsyncMock()

    await manager.connect("user_1", ws)
    manager.join_room("brand_abc", ws)
    manager.disconnect("user_1", ws)

    assert manager.active_users == 0
    count = await manager.send_to_room("brand_abc", {"type": "test"})
    assert count == 0


@pytest.mark.asyncio
async def test_multiple_connections_same_user(manager):
    ws1 = AsyncMock(spec=WebSocket)
    ws2 = AsyncMock(spec=WebSocket)
    ws1.send_json = AsyncMock()
    ws2.send_json = AsyncMock()
    payload = {"type": "multi"}

    await manager.connect("user_1", ws1)
    await manager.connect("user_1", ws2)

    assert manager.active_users == 1
    assert manager.active_connections == 2

    count = await manager.send_to_user("user_1", payload)
    assert count == 2


@pytest.mark.asyncio
async def test_send_to_brand_room(manager):
    ws = AsyncMock(spec=WebSocket)
    ws.send_json = AsyncMock()
    payload = {"type": "catalog_update"}

    await manager.connect("user_1", ws)
    manager.join_room("brand_xyz", ws)

    count = await manager.send_to_room("brand_xyz", payload)
    assert count == 1
    ws.send_json.assert_called_with(payload)


@pytest.mark.asyncio
async def test_websocket_push_job_update():
    with patch("app.services.ws_manager.manager.send_to_user", new_callable=AsyncMock) as mock_send:
        mock_send.return_value = 1

        from app.services.websocket import push_job_update
        await push_job_update(
            user_id="user_1",
            job_id="job_123",
            status="processing",
            progress=0.5,
        )

        mock_send.assert_called_once()
        args = mock_send.call_args
        assert args[0][0] == "user_1"
        payload = args[0][1]
        assert payload["type"] == "job_update"
        assert payload["job_id"] == "job_123"
        assert payload["status"] == "processing"
        assert payload["progress"] == 0.5


@pytest.mark.asyncio
async def test_websocket_push_job_update_fallback_redis():
    with patch("app.services.ws_manager.manager.send_to_user", new_callable=AsyncMock) as mock_send:
        mock_send.return_value = 0

        mock_redis = AsyncMock()
        mock_redis.publish = AsyncMock()
        with patch("app.services.websocket.get_redis", new_callable=AsyncMock) as mock_get_redis:
            mock_get_redis.return_value = mock_redis

            from app.services.websocket import push_job_update
            await push_job_update(
                user_id="user_1",
                job_id="job_123",
                status="done",
                result_url="https://example.com/result.jpg",
            )

            mock_redis.publish.assert_called_once()
            args = mock_redis.publish.call_args
            assert args[0][0] == "ws:events"


@pytest.mark.asyncio
async def test_verify_ws_token_valid():
    mock_response = AsyncMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"id": "user_abc"}

    with patch("httpx.AsyncClient") as mock_client:
        mock_client.return_value.__aenter__.return_value.get = AsyncMock(return_value=mock_response)

        from app.services.security import verify_ws_token
        user_id = await verify_ws_token("valid_token")
        assert user_id == "user_abc"


@pytest.mark.asyncio
async def test_verify_ws_token_invalid():
    mock_response = AsyncMock()
    mock_response.status_code = 401

    with patch("httpx.AsyncClient") as mock_client:
        mock_client.return_value.__aenter__.return_value.get = AsyncMock(return_value=mock_response)

        from app.services.security import verify_ws_token
        user_id = await verify_ws_token("invalid_token")
        assert user_id is None
