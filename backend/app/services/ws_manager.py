import logging
from fastapi import WebSocket

logger = logging.getLogger(__name__)


class ConnectionManager:
    def __init__(self) -> None:
        self._connections: dict[str, set[WebSocket]] = {}
        self._rooms: dict[str, set[WebSocket]] = {}

    async def connect(self, user_id: str, ws: WebSocket) -> None:
        await ws.accept()
        self._connections.setdefault(user_id, set()).add(ws)

    def disconnect(self, user_id: str, ws: WebSocket) -> None:
        self._connections.get(user_id, set()).discard(ws)
        if not self._connections.get(user_id):
            self._connections.pop(user_id, None)
        for room_sockets in self._rooms.values():
            room_sockets.discard(ws)

    def join_room(self, room: str, ws: WebSocket) -> None:
        self._rooms.setdefault(room, set()).add(ws)

    def leave_room(self, room: str, ws: WebSocket) -> None:
        self._rooms.get(room, set()).discard(ws)

    async def send_to_user(self, user_id: str, payload: dict) -> int:
        count = 0
        for ws in self._connections.get(user_id, set()):
            try:
                await ws.send_json(payload)
                count += 1
            except Exception:
                self.disconnect(user_id, ws)
        return count

    async def send_to_room(self, room: str, payload: dict) -> int:
        count = 0
        for ws in self._rooms.get(room, set()):
            try:
                await ws.send_json(payload)
                count += 1
            except Exception:
                self.leave_room(room, ws)
        return count

    async def broadcast(self, payload: dict) -> int:
        count = 0
        for user_id in list(self._connections):
            count += await self.send_to_user(user_id, payload)
        return count

    def get_user_connection_count(self, user_id: str) -> int:
        return len(self._connections.get(user_id, set()))

    @property
    def active_connections(self) -> int:
        return sum(len(sockets) for sockets in self._connections.values())

    @property
    def active_users(self) -> int:
        return len(self._connections)


manager = ConnectionManager()
