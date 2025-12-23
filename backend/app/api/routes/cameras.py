"""
Camera management routes - FINAL WORKING VERSION
"""
from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import cv2
import asyncio
import logging

from app.services.camera_manager import camera_manager
from app.services.hand_detector import hand_detector
from app.services.feature_processor import feature_processor
from app.services.gesture_recognizer import gesture_recognizer
from app.services.gesture_controller import gesture_controller

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/cameras", tags=["cameras"])



# ============================================================================
# PYDANTIC MODELS
# ============================================================================

class CameraSettings(BaseModel):
    """Settings for camera image adjustment"""
    brightness: int = 50
    contrast: int = 50
    saturation: int = 50


class AddCameraRequest(BaseModel):
    """Request model for adding a new camera"""
    name: str
    source: str
    type: str


class ModeRequest(BaseModel):
    """Request model for setting detection mode"""
    mode: str


# ============================================================================
# GET ENDPOINTS
# ============================================================================

@router.get("/")
async def list_cameras():
    """List all cameras"""
    cameras = camera_manager.list_cameras()
    print(f"📹 Listing {len(cameras)} cameras")
    return {
        "cameras": cameras,
        "count": len(cameras),
        "message": "Active cameras listed"
    }


@router.get("/detect")
async def detect_cameras():
    """Detect available USB cameras"""
    available = camera_manager.detect_usb_cameras()
    print(f"🔍 Detected {len(available)} USB cameras")
    return {
        "detected": available,
        "count": len(available),
        "message": f"Detected {len(available)} cameras"
    }


@router.get("/{camera_id}/info")
async def get_camera_info(camera_id: int):
    """Get detailed camera information"""
    info = camera_manager.get_camera_info(camera_id)
    
    if info is None:
        raise HTTPException(status_code=404, detail="Camera not found")
    
    return info


@router.get("/{camera_id}/stream")
async def video_stream(camera_id: int):
    """Stream video from camera"""
    print(f"📹 Starting stream for camera {camera_id}")
    return StreamingResponse(
        generate_frames(camera_id),
        media_type="multipart/x-mixed-replace; boundary=frame"
    )


# ============================================================================
# POST ENDPOINTS
# ============================================================================

@router.post("/")
async def add_camera(request: AddCameraRequest):
    """Add a new camera"""
    try:
        # Determine camera ID based on type
        if request.type == 'usb':
            camera_id = int(request.source)
        else:
            camera_id = len(camera_manager.cameras)
        
        # Add camera to manager
        success = camera_manager.add_camera(camera_id, request.source, request.type)
        
        print(f"➕ Adding camera: id={camera_id}, type={request.type}, source={request.source}, success={success}")
        
        return {
            "id": camera_id,
            "name": request.name,
            "source": request.source,
            "type": request.type,
            "enabled": success,
            "message": "Camera added successfully" if success else "Failed to add camera"
        }
    except Exception as e:
        print(f"❌ Error adding camera: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{camera_id}/settings")
async def update_camera_settings(camera_id: int, settings: CameraSettings):
    """Update camera image settings (brightness, contrast, saturation)"""
    success = camera_manager.update_settings(camera_id, settings.dict())
    
    if not success:
        print(f"❌ Failed to update settings for camera {camera_id}")
        raise HTTPException(status_code=404, detail="Camera not active")
    
    print(f"⚙️ Updated settings for camera {camera_id}: {settings.dict()}")
    return {
        "status": "updated",
        "camera_id": camera_id,
        "settings": settings.dict()
    }


@router.post("/mode")
async def set_mode(request: ModeRequest):
    """Set detection mode (standard, safe, all)"""
    print(f"🔄 Setting mode to: {request.mode}")
    success = gesture_controller.set_mode(request.mode)
    print(f"✅ Mode set to: {gesture_controller.mode}")
    return {
        "success": success,
        "mode": gesture_controller.mode
    }


# ============================================================================
# DELETE ENDPOINTS
# ============================================================================

@router.delete("/{camera_id}")
async def remove_camera(camera_id: int):
    """Remove a camera"""
    success = camera_manager.remove_camera(camera_id)
    
    if success:
        print(f"🗑️ Camera {camera_id} removed")
        return {"status": "removed", "camera_id": camera_id}
    else:
        print(f"❌ Camera {camera_id} not found")
        raise HTTPException(status_code=404, detail="Camera not found")


# ============================================================================
# WEBSOCKET ENDPOINTS
# ============================================================================

@router.websocket("/{camera_id}/ws/detection")
async def detection_websocket(websocket: WebSocket, camera_id: int):
    """WebSocket for real-time gesture detection - OPTIMIZED"""
    await websocket.accept()
    print(f"🔌 WebSocket connected for camera {camera_id}")
    logger.info(f"WebSocket connected for camera {camera_id}")
    
    frame_counter = 0
    
    try:
        while True:
            try:
                # OPTYMALIZACJA: Przetwarzaj co 3 frame (oszczędność CPU)
                frame_counter += 1
                if frame_counter % 3 != 0:
                    await asyncio.sleep(0.01)
                    continue
                
                # Get frame from camera
                frame = camera_manager.get_frame(camera_id)
                
                if frame is None:
                    await asyncio.sleep(0.01)
                    continue

                # 1. Detect hands
                rgb_frame, results = hand_detector.detect_hands(frame)
                hands_info = hand_detector.get_hand_info(results)
                landmarks_list = hand_detector.extract_landmarks(results)
                
                detection_data = {
                    "timestamp": cv2.getTickCount(),
                    "hands_detected": len(hands_info),
                    "gestures": [],
                    "controller": None
                }

                # 2. Process gestures if hands detected
                if hands_info and landmarks_list:
                    for i, hand in enumerate(hands_info):
                        label = "Unknown"
                        confidence = 0.0
                        
                        try:
                            # Extract features from landmarks
                            landmarks = landmarks_list[i]
                            features = feature_processor.extract_features(landmarks)
                            
                            # Predict gesture using ML model
                            label, confidence = gesture_recognizer.predict(features)
                            
                            # Process controller logic (only for first hand)
                            if i == 0:
                                controller_result = gesture_controller.process_gesture(label, confidence)
                                detection_data["controller"] = {
                                    "mode": gesture_controller.mode,
                                    "triggered": controller_result["action_triggered"],
                                    "progress": controller_result["progress"],
                                    "message": controller_result["message"]
                                }
                                
                                # Log tylko ważne eventy
                                if confidence >= 0.7 and frame_counter % 60 == 0:
                                    print(f"✅ {label} ({confidence:.2f})")
                            
                        except Exception as e:
                            if frame_counter % 100 == 0:
                                logger.error(f"Prediction error: {e}")

                        # Add gesture info to response
                        detection_data["gestures"].append({
                            "type": hand["type"],
                            "label": label,
                            "confidence": confidence
                        })

                # Send detection data via WebSocket
                try:
                    await websocket.send_json(detection_data)
                except Exception as ws_send_error:
                    logger.warning(f"WebSocket send error: {ws_send_error}")
                    break
                    
                # OPTYMALIZACJA: Krótszy sleep = szybsza reakcja
                await asyncio.sleep(0.01)  # ~30 FPS
                
            except Exception as inner_error:
                logger.error(f"Inner loop error: {inner_error}")
                break

    except WebSocketDisconnect:
        print(f"❌ WebSocket disconnected for camera {camera_id}")
    except Exception as e:
        print(f"❌ WebSocket error: {e}")
        try:
            await websocket.close(code=1011, reason="Internal server error")
        except:
            pass



# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def generate_frames(camera_id: int):
    """Generate video frames for streaming - ULTRA OPTIMIZED"""
    import time
    
    last_frame_time = time.time()
    target_fps = 30  # Docelowe FPS
    frame_interval = 1.0 / target_fps
    
    while True:
        try:
            current_time = time.time()
            
            # Rate limiting - nie wysyłaj częściej niż 30 FPS
            if current_time - last_frame_time < frame_interval:
                continue
            
            frame = camera_manager.get_frame(camera_id)
            if frame is None:
                break
            
            # OPTYMALIZACJA: Encode z niższą jakością ale szybko
            encode_params = [
                cv2.IMWRITE_JPEG_QUALITY, 75,
                cv2.IMWRITE_JPEG_PROGRESSIVE, 1,
                cv2.IMWRITE_JPEG_OPTIMIZE, 1
            ]
            
            ret, buffer = cv2.imencode('.jpg', frame, encode_params)
            if not ret:
                continue
            
            frame_bytes = buffer.tobytes()
            
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n'
                   b'Cache-Control: no-cache\r\n'
                   b'\r\n' + frame_bytes + b'\r\n')
            
            last_frame_time = current_time
            
        except Exception as e:
            logger.error(f"Frame generation error: {e}")
            break


