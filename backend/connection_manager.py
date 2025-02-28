from fastapi import WebSocket, WebSocketDisconnect
from typing import List


class ConnectionManager:
    def __init__(self):
        self.connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def send_session_message(self, message: str, websockets: []):
        for websocket in websockets:
            try:
                await websocket.send_text(message)
            except WebSocketDisconnect:
                self.disconnect(websocket)

    async def broadcast(self, message: str):
        for connection in self.connections:
            try:
                await connection.send_text(message)
            except WebSocketDisconnect:
                self.disconnect(connection)


manager = ConnectionManager()
