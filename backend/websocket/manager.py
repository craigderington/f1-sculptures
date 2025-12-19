"""
WebSocket connection manager for real-time task progress updates.
"""

from fastapi import WebSocket, WebSocketDisconnect
from typing import Dict, Set
import logging
import json
import asyncio

logger = logging.getLogger(__name__)


class WebSocketManager:
    """Manages WebSocket connections for task progress updates."""

    def __init__(self):
        # Map of task_id -> set of WebSocket connections
        self.active_connections: Dict[str, Set[WebSocket]] = {}
        self._lock = asyncio.Lock()

    async def connect(self, websocket: WebSocket, task_id: str):
        """
        Accept a new WebSocket connection for a specific task.

        Args:
            websocket: WebSocket connection object
            task_id: Task ID to subscribe to
        """
        await websocket.accept()

        async with self._lock:
            if task_id not in self.active_connections:
                self.active_connections[task_id] = set()

            self.active_connections[task_id].add(websocket)

        logger.info(f"WebSocket connected for task {task_id}. Total connections: {len(self.active_connections[task_id])}")

    async def disconnect(self, websocket: WebSocket, task_id: str):
        """
        Remove a WebSocket connection.

        Args:
            websocket: WebSocket connection object
            task_id: Task ID
        """
        async with self._lock:
            if task_id in self.active_connections:
                self.active_connections[task_id].discard(websocket)

                # Clean up empty task connections
                if not self.active_connections[task_id]:
                    del self.active_connections[task_id]

        logger.info(f"WebSocket disconnected for task {task_id}")

    async def send_message(self, task_id: str, message: Dict):
        """
        Send a message to all connections subscribed to a task.

        Args:
            task_id: Task ID
            message: Message dictionary to send
        """
        if task_id not in self.active_connections:
            logger.debug(f"No active connections for task {task_id}")
            return

        # Get connections (copy to avoid modification during iteration)
        connections = list(self.active_connections[task_id])

        if connections:
            message_json = json.dumps(message)
            logger.debug(f"Sending message to {len(connections)} connections for task {task_id}")

            # Send to all connections
            disconnected = []
            for connection in connections:
                try:
                    await connection.send_text(message_json)
                except Exception as e:
                    logger.error(f"Error sending message to WebSocket: {e}")
                    disconnected.append(connection)

            # Clean up disconnected sockets
            if disconnected:
                async with self._lock:
                    for connection in disconnected:
                        if task_id in self.active_connections:
                            self.active_connections[task_id].discard(connection)

    async def broadcast_progress(self, task_id: str, stage: str, progress: int, message: str):
        """
        Broadcast a progress update to all connections for a task.

        Args:
            task_id: Task ID
            stage: Current stage identifier
            progress: Progress percentage (0-100)
            message: Human-readable progress message
        """
        await self.send_message(task_id, {
            'type': 'progress',
            'task_id': task_id,
            'stage': stage,
            'progress': progress,
            'message': message
        })

    async def broadcast_success(self, task_id: str, result: Dict):
        """
        Broadcast task completion success.

        Args:
            task_id: Task ID
            result: Task result data
        """
        await self.send_message(task_id, {
            'type': 'success',
            'task_id': task_id,
            'result': result
        })

    async def broadcast_error(self, task_id: str, error: str):
        """
        Broadcast task failure.

        Args:
            task_id: Task ID
            error: Error message
        """
        await self.send_message(task_id, {
            'type': 'error',
            'task_id': task_id,
            'error': error
        })

    async def get_connection_count(self, task_id: str) -> int:
        """Get number of active connections for a task."""
        if task_id in self.active_connections:
            return len(self.active_connections[task_id])
        return 0

    async def get_total_connections(self) -> int:
        """Get total number of active WebSocket connections across all tasks."""
        total = 0
        async with self._lock:
            for connections in self.active_connections.values():
                total += len(connections)
        return total

    async def get_active_tasks(self) -> list:
        """Get list of task IDs with active WebSocket connections."""
        async with self._lock:
            return list(self.active_connections.keys())


# Global WebSocket manager instance
ws_manager = WebSocketManager()
