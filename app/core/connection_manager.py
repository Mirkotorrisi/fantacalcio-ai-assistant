from typing import Dict, Set
from fastapi import WebSocket
import asyncio


class ConnectionManager:
    """Manages websocket connections per session_id and broadcasts roster updates."""

    def __init__(self):
        # session_id -> set of websockets
        self.active_connections: Dict[str, Set[WebSocket]] = {}
        # simple lock to avoid race conditions when mutating connection sets
        self._lock = asyncio.Lock()

    async def connect(self, session_id: str, websocket: WebSocket):
        await websocket.accept()
        async with self._lock:
            self.active_connections.setdefault(session_id, set()).add(websocket)

    def disconnect(self, session_id: str, websocket: WebSocket):
        # best effort removal (no await needed)
        if session_id in self.active_connections:
            self.active_connections[session_id].discard(websocket)
            if not self.active_connections[session_id]:
                del self.active_connections[session_id]

    async def send_personal_roster(self, websocket: WebSocket, roster_dict):
        await websocket.send_json({"type": "roster", "data": roster_dict})

    async def broadcast_roster(self, session_id: str, roster_dict):
        connections = list(self.active_connections.get(session_id, []))
        if not connections:
            return
        message = {"type": "roster", "data": roster_dict}
        to_remove = []
        for ws in connections:
            try:
                await ws.send_json(message)
            except Exception:
                # mark broken connections for removal
                to_remove.append(ws)
        if to_remove:
            async with self._lock:
                for ws in to_remove:
                    self.active_connections.get(session_id, set()).discard(ws)
                if session_id in self.active_connections and not self.active_connections[session_id]:
                    del self.active_connections[session_id]


# Singleton manager instance
manager = ConnectionManager()
