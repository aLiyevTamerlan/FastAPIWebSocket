from typing import Dict, List
from fastapi import WebSocket


class ConnectionManager:
    """Class defining socket events"""
    def __init__(self):
        """init method, keeping track of connections"""
        self.active_connections: Dict[int, List[WebSocket]] = {}
    
    async def connect(self, user_id: int, websocket: WebSocket):
        """connect event"""
        await websocket.accept()
        if user_id not in self.active_connections:
            self.active_connections[user_id] = []
        self.active_connections[user_id].append(websocket)

    async def send_personal_message(self,receiver_id:int, message: str):
        print(self.active_connections)
        if receiver_id in self.active_connections:
            for connection in self.active_connections[receiver_id]:
                await connection.send_text(message)
    
    def disconnect(self, user_id: int, websocket: WebSocket):
        """Remove the WebSocket connection for a specific user"""
        if user_id in self.active_connections:
            self.active_connections[user_id].remove(websocket)
            # If there are no more connections for the user, remove the user ID
            if not self.active_connections[user_id]:
                del self.active_connections[user_id]