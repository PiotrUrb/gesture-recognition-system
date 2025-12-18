"""
POPRAWKA #1: Backend - app/api/routes/cameras.py
ZMIANA: Parametry muszą być w body JSON, nie w query parameters
"""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, HTTPException, Query
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import cv2
import asyncio
import logging
from app.services.camera_manager import camera_manager
from app.services.hand_detector import hand_detector

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/cameras", tags=["cameras"])

# ============================================================================
# REQUEST MODELS
# ============================================================================

class AddCameraRequest(BaseModel):
    source: str
    camera_type: str = "usb"
    name: str = None

class UpdateSettingsRequest(BaseModel):
    brightness: float = None
    contrast: float = None
    saturation: float = None
    name: str = None
    fps: int = None
    width: int = None
    height: int = None

# ============================================================================
# VIDEO STREAMING ENDPOINTS
# ============================================================================

@router.get("/{camera_id}/stream")
async def stream_camera(camera_id: int, quality: str = Query("medium", regex="^(low|medium|high)$")):
    """Stream video from camera with quality optimization"""
    quality_map = {
        "low": (640, 480),
        "medium": (1024, 768),
        "high": (1920, 1080)
    }
    
    width, height = quality_map[quality]
    
    async def generate_frames():
        """Generate optimized video frames"""
        while True:
            try:
                frame = camera_manager.get_frame(camera_id)
                if frame is None:
                    await asyncio.sleep(0.01)
                    continue
                
                resized_frame = cv2.resize(frame, (width, height))
                _, buffer = cv2.imencode('.jpg', resized_frame, [cv2.IMWRITE_JPEG_QUALITY, 85])
                
                yield (
                    b'--frame\r\n'
                    b'Content-Type: image/jpeg\r\n'
                    b'Content-Length: ' + str(len(buffer)).encode() + b'\r\n\r\n'
                    + buffer.tobytes() + b'\r\n'
                )
                
                await asyncio.sleep(0.03)
            except Exception as e:
                logger.error(f"Stream error for camera {camera_id}: {e}")
                break
    
    return StreamingResponse(
        generate_frames(),
        media_type="multipart/x-mixed-replace; boundary=frame",
        headers={"Cache-Control": "no-cache, no-store, must-revalidate"}
    )

# ============================================================================
# WEBSOCKET DETECTION ENDPOINT - FIXED
# ============================================================================

class ConnectionManager:
    def __init__(self):
        self.active_connections: dict[int, list[WebSocket]] = {}
    
    async def connect(self, camera_id: int, websocket: WebSocket):
        await websocket.accept()
        if camera_id not in self.active_connections:
            self.active_connections[camera_id] = []
        self.active_connections[camera_id].append(websocket)
        logger.info(f"✅ Client connected to camera {camera_id}")
    
    def disconnect(self, camera_id: int, websocket: WebSocket):
        if camera_id in self.active_connections:
            self.active_connections[camera_id].remove(websocket)
    
    async def broadcast(self, camera_id: int, data: dict):
        if camera_id in self.active_connections:
            disconnected = []
            for connection in self.active_connections[camera_id]:
                try:
                    await connection.send_json(data)
                except Exception as e:
                    logger.debug(f"Broadcast error: {e}")
                    disconnected.append(connection)
            
            for conn in disconnected:
                self.disconnect(camera_id, conn)

manager = ConnectionManager()

@router.websocket("/ws/{camera_id}/detection")
async def detection_websocket(websocket: WebSocket, camera_id: int):
    """WebSocket for real-time gesture detection"""
    await manager.connect(camera_id, websocket)
    detection_interval = 0
    
    try:
        while True:
            frame = camera_manager.get_frame(camera_id)
            if frame is None:
                await asyncio.sleep(0.01)
                continue
            
            # ✅ FIX: Run hand_detector in thread pool (non-blocking)
            rgb_frame, results = await asyncio.to_thread(
                hand_detector.detect_hands, frame
            )
            
            hands_info = hand_detector.get_hand_info(results)
            
            detection_interval += 1
            if detection_interval % 5 == 0:
                if hands_info:
                    for hand in hands_info:
                        data = {
                            "gesture": "hand_detected",
                            "confidence": hand.get("confidence", 0.85),
                            "hand_type": hand.get("type", "Unknown"),
                            "timestamp": int(cv2.getTickCount() / cv2.getTickFrequency() * 1000)
                        }
                        await manager.broadcast(camera_id, data)
                
                detection_interval = 0
            
            await asyncio.sleep(0.01)
    
    except WebSocketDisconnect:
        manager.disconnect(camera_id, websocket)
        logger.info(f"Client disconnected from camera {camera_id}")
    except Exception as e:
        logger.error(f"WebSocket error for camera {camera_id}: {e}")
        manager.disconnect(camera_id, websocket)

# ============================================================================
# CAMERA MANAGEMENT ENDPOINTS - FIXED WITH PYDANTIC MODELS
# ============================================================================

@router.get("/")
async def list_cameras():
    """List all cameras"""
    cameras_list = camera_manager.list_cameras()
    return {
        "cameras": cameras_list,
        "count": len(cameras_list)
    }

@router.get("/{camera_id}")
async def get_camera(camera_id: int):
    """Get camera details"""
    info = camera_manager.get_camera_info(camera_id)
    if not info:
        raise HTTPException(status_code=404, detail="Camera not found")
    return info

@router.post("/")
async def add_camera(request: AddCameraRequest):
    """Add a new camera - accepts JSON body"""
    try:
        existing_ids = list(camera_manager.cameras.keys())
        camera_id = max(existing_ids) + 1 if existing_ids else 0
        
        success = camera_manager.add_camera(camera_id, request.source, request.camera_type)
        if not success:
            raise HTTPException(status_code=400, detail="Failed to open camera")
        
        if request.name:
            camera_manager.camera_configs[camera_id]['name'] = request.name
        
        logger.info(f"✅ Camera {camera_id} added: {request.camera_type} from {request.source}")
        return {
            "status": "success",
            "camera_id": camera_id,
            "message": f"Camera {request.name or camera_id} added"
        }
    except Exception as e:
        logger.error(f"Error adding camera: {e}")
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/{camera_id}/settings")
async def update_camera_settings(camera_id: int, request: UpdateSettingsRequest):
    """Update camera settings"""
    
    info = camera_manager.get_camera_info(camera_id)
    if not info:
        raise HTTPException(status_code=404, detail="Camera not found")
    
    try:
        # Update image adjustments
        settings_dict = {}
        if request.brightness is not None:
            settings_dict['brightness'] = request.brightness
        if request.contrast is not None:
            settings_dict['contrast'] = request.contrast
        if request.saturation is not None:
            settings_dict['saturation'] = request.saturation
        
        if settings_dict:
            camera_manager.update_settings(camera_id, settings_dict)
            logger.info(f"✅ Updated image settings for camera {camera_id}: {settings_dict}")
        
        # Update resolution/fps
        if request.width or request.height or request.fps:
            camera_manager.configure_camera(camera_id, request.width, request.height, request.fps)
        
        if request.name:
            camera_manager.camera_configs[camera_id]['name'] = request.name
        
        return {
            "status": "success",
            "camera_id": camera_id,
            "message": "Settings updated"
        }
    except Exception as e:
        logger.error(f"Error updating settings for camera {camera_id}: {e}")
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/{camera_id}")
async def remove_camera(camera_id: int):
    """Remove a camera"""
    try:
        success = camera_manager.remove_camera(camera_id)
        if not success:
            raise HTTPException(status_code=404, detail="Camera not found")
        
        logger.info(f"✅ Camera {camera_id} removed")
        return {"status": "success", "message": f"Camera {camera_id} removed"}
    except Exception as e:
        logger.error(f"Error removing camera {camera_id}: {e}")
        raise HTTPException(status_code=400, detail=str(e))