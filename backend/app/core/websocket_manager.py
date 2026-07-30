from fastapi import WebSocket
from typing import Dict, List

class WebSocketManager:
    def __init__(self):
        # Maps user_id -> List of active WebSocket connections
        self.active_connections: Dict[int, List[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, user_id: int):
        await websocket.accept()
        if user_id not in self.active_connections:
            self.active_connections[user_id] = []
        self.active_connections[user_id].append(websocket)
        print(f"[WS] User {user_id} connected. Total connections for user: {len(self.active_connections[user_id])}")

    def disconnect(self, websocket: WebSocket, user_id: int):
        if user_id in self.active_connections:
            self.active_connections[user_id].remove(websocket)
            if not self.active_connections[user_id]:
                del self.active_connections[user_id]

    async def send_personal_message(self, message: dict, user_id: int):
        """Send a JSON message to a specific user's active connections."""
        print(f"[WS] Attempting to send message to user {user_id}. Active users: {list(self.active_connections.keys())}")
        if user_id in self.active_connections:
            for connection in self.active_connections[user_id]:
                try:
                    await connection.send_json(message)
                    print(f"[WS] Successfully sent message to user {user_id}")
                except Exception as e:
                    # Ignore closed connections or errors
                    print(f"Error sending to user {user_id}: {e}")

    async def broadcast(self, message: dict):
        """Send a JSON message to everyone."""
        for user_id, connections in self.active_connections.items():
            for connection in connections:
                try:
                    await connection.send_json(message)
                except Exception:
                    pass

ws_manager = WebSocketManager()
