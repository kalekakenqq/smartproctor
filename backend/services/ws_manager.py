from fastapi import WebSocket


class ConnectionManager:
    def __init__(self):
        self.connections: dict[int, list[WebSocket]] = {}

    async def connect(self, session_id: int, websocket: WebSocket):
        await websocket.accept()
        self.connections.setdefault(session_id, []).append(websocket)

    def disconnect(self, session_id: int, websocket: WebSocket):
        if session_id in self.connections:
            if websocket in self.connections[session_id]:
                self.connections[session_id].remove(websocket)
            if not self.connections[session_id]:
                del self.connections[session_id]

    async def broadcast(self, session_id: int, message: dict):
        for ws in list(self.connections.get(session_id, [])):
            try:
                await ws.send_json(message)
            except Exception:
                self.disconnect(session_id, ws)


manager = ConnectionManager()
