"""
System management endpoints
"""
from fastapi import APIRouter, WebSocket
import logging
import asyncio
from app.core.config import settings

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/system",
    tags=["system"]
)


# ==================== CONFIG ENDPOINT ====================

@router.get("/config")
async def get_system_config():
    """
    Get current system configuration for Dashboard
    """
    try:
        from app.services.camera_manager import camera_manager
        
        connected_cameras = len(camera_manager.cameras)
        
        return {
            "status": "success",
            "config": {
                "connected_cameras": connected_cameras,
                "algorithm": "RandomForest",
                "confidence_threshold": int(settings.MIN_DETECTION_CONFIDENCE * 100),
                "model_version": settings.VERSION,
                "max_cameras": settings.MAX_CAMERAS,
            }
        }
    except Exception as e:
        logger.error(f"Error fetching system config: {e}", exc_info=True)
        return {
            "status": "error",
            "config": {
                "connected_cameras": 0,
                "algorithm": "RandomForest",
                "confidence_threshold": 70,
                "model_version": settings.VERSION,
                "max_cameras": settings.MAX_CAMERAS,
            }
        }


# ==================== WEBSOCKET (OPCJONALNY) ====================

@router.websocket("/ws/health")
async def websocket_health(websocket: WebSocket):
    """WebSocket endpoint dla real-time health updates"""
    await websocket.accept()
    try:
        while True:
            await websocket.send_json({
                "status": "online"
            })
            await asyncio.sleep(3)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
