"""
Service for logging gesture detection to database during camera/WebSocket operations
"""

from app.services.gesture_detection_logging import get_logging_service
import logging

logger = logging.getLogger(__name__)

def log_gesture_event(
    gesture: str,
    confidence: float,
    hand_type: str,
    mode: str,
    success: bool = True,
    message: str = "",
    camera_id: int = 0,
    camera_name: str = "Unknown",
    action_triggered: str = None,
    progress: int = 0,
    gesture_label: str = None,
):
    """
    Log gesture event to database
    Call this from camera routes or gesture controller
    """
    try:
        logging_service = get_logging_service()
        logging_service.log_gesture(
            gesture=gesture,
            confidence=confidence,
            hand_type=hand_type,
            mode=mode,
            success=success,
            message=message,
            camera_id=camera_id,
            camera_name=camera_name,
            action_triggered=action_triggered,
            progress=progress,
            gesture_label=gesture_label,
        )
    except Exception as e:
        logger.error(f"Error logging gesture event: {e}")
