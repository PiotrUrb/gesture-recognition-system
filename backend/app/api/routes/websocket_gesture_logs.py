"""
WebSocket for real-time gesture log streaming to Frontend
"""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from datetime import datetime, timedelta
import asyncio
import logging

logger = logging.getLogger(__name__)
router = APIRouter(tags=["websocket"])

active_connections = []

@router.websocket("/ws/gesture-logs")
async def websocket_gesture_logs(websocket: WebSocket):
    """WebSocket for real-time gesture log streaming"""
    await websocket.accept()
    active_connections.append(websocket)
    logger.info(f"✅ WebSocket connected for gesture logs. Active connections: {len(active_connections)}")
    
    try:
        while True:
            await asyncio.sleep(0.1)
    except WebSocketDisconnect:
        active_connections.remove(websocket)
        logger.info(f"❌ WebSocket disconnected. Active connections: {len(active_connections)}")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        if websocket in active_connections:
            active_connections.remove(websocket)

async def broadcast_gesture_log(log_data: dict):
    """Broadcast new gesture log to all connected WebSocket clients"""
    disconnected = []
    for connection in active_connections:
        try:
            await connection.send_json(log_data)
        except Exception as e:
            logger.warning(f"Error broadcasting to WebSocket: {e}")
            disconnected.append(connection)
    
    for conn in disconnected:
        if conn in active_connections:
            active_connections.remove(conn)
