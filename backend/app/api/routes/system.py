# backend/app/api/routes/system.py
"""
System management endpoints - MINIMAL VERSION
Ponieważ usunęliśmy przyciski, nie potrzebujemy shutdown/restart
"""

from fastapi import APIRouter, WebSocket
import logging
import json
import asyncio

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/system",
    tags=["system"]
)

# WebSocket endpoint - opcjonalnie, na razie pusty
@router.websocket("/ws/health")
async def websocket_health(websocket: WebSocket):
    """WebSocket endpoint dla real-time health updates (opcjonalny)"""
    await websocket.accept()
    try:
        while True:
            await websocket.send_json({
                "status": "online"
            })
            await asyncio.sleep(3)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")