"""Real-time WebSocket Connection Manager for Smiota AI & Customer Chat."""
import asyncio
from typing import Any, Dict, Optional, Set
from fastapi import WebSocket
from smiota.core.logging import logger


class WebSocketConnectionManager:
    """Manages active WebSocket connections, multi-tab routing, and RabbitMQ push broadcasts."""

    def __init__(self):
        # session_id -> WebSocket instance
        self.active_sessions: Dict[str, WebSocket] = {}
        # resident_id -> set of session_ids
        self.resident_sessions: Dict[str, Set[str]] = {}
        self._lock = asyncio.Lock()

    async def connect(self, session_id: str, websocket: WebSocket, resident_id: Optional[str] = None) -> None:
        """Register and accept an incoming WebSocket connection."""
        await websocket.accept()
        async with self._lock:
            self.active_sessions[session_id] = websocket
            if resident_id:
                if resident_id not in self.resident_sessions:
                    self.resident_sessions[resident_id] = set()
                self.resident_sessions[resident_id].add(session_id)

        logger.info(f"WebSocket client connected. Active sessions: {len(self.active_sessions)} (Session: {session_id}, Resident: {resident_id})")

    async def disconnect(self, session_id: str) -> None:
        """Remove a disconnected session."""
        async with self._lock:
            self.active_sessions.pop(session_id, None)
            for res_id, sess_set in list(self.resident_sessions.items()):
                sess_set.discard(session_id)
                if not sess_set:
                    self.resident_sessions.pop(res_id, None)

        logger.info(f"WebSocket client disconnected: {session_id}. Remaining: {len(self.active_sessions)}")

    async def send_to_session(self, session_id: str, message: Dict[str, Any]) -> bool:
        """Send message directly to a specific chat session."""
        ws = self.active_sessions.get(session_id)
        if ws:
            try:
                await ws.send_json(message)
                return True
            except Exception as e:
                logger.warning(f"Failed to send to session {session_id}: {e}")
                await self.disconnect(session_id)
        return False

    async def send_to_resident(self, resident_id: str, message: Dict[str, Any]) -> int:
        """Send message to all open tabs/devices for a given resident."""
        session_ids = self.resident_sessions.get(resident_id, set()).copy()
        count = 0
        for s_id in session_ids:
            if await self.send_to_session(s_id, message):
                count += 1
        return count

    async def broadcast(self, message: Dict[str, Any]) -> int:
        """Broadcast a message to all connected clients."""
        sessions = list(self.active_sessions.keys())
        count = 0
        for s_id in sessions:
            if await self.send_to_session(s_id, message):
                count += 1
        return count


# Singleton instance
ws_manager = WebSocketConnectionManager()
