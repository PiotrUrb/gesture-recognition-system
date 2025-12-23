"""
Camera management routes - FINAL WORKING VERSION
"""
from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import cv2
import asyncio

from app.services.camera_manager import camera_manager
from app.services.hand_detector import hand_detector
from app.services.feature_processor import feature_processor
from app.services.gesture_recognizer import gesture_recognizer
from app.services.gesture_controller import gesture_controller

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
    """WebSocket for real-time gesture detection"""
    await websocket.accept()
    print(f"🔌 WebSocket connected for camera {camera_id}")
    
    try:
        while True:
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
                        
                        print(f"🎯 Hand {i} detected: {label} (confidence: {confidence:.2f})")
                        
                        # Process controller logic (only for first hand)
                        if i == 0:
                            controller_result = gesture_controller.process_gesture(label, confidence)
                            detection_data["controller"] = {
                                "mode": gesture_controller.mode,
                                "triggered": controller_result["action_triggered"],
                                "progress": controller_result["progress"],
                                "message": controller_result["message"]
                            }
                            
                            # Log high-confidence gestures
                            if confidence >= 0.5:
                                print(f"✅ Gesture recognized: {label} (conf: {confidence:.2f})")
                        
                    except Exception as e:
                        print(f"❌ Prediction error: {e}")

                    # Add gesture info to response
                    detection_data["gestures"].append({
                        "type": hand["type"],
                        "label": label,
                        "confidence": confidence
                    })

            # Send detection data via WebSocket
            await websocket.send_json(detection_data)
            await asyncio.sleep(0.05)  # ~20 FPS

    except WebSocketDisconnect:
        print(f"❌ WebSocket disconnected for camera {camera_id}")
    except Exception as e:
        print(f"❌ WebSocket error: {e}")
        await websocket.close()


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def generate_frames(camera_id: int):
    """Generate video frames for streaming"""
    while True:
        frame = camera_manager.get_frame(camera_id)
        if frame is None:
            break
        
        ret, buffer = cv2.imencode('.jpg', frame)
        if not ret:
            continue
            
        frame_bytes = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
