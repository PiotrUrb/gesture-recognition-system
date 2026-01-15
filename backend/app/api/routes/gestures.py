"""
Gesture management routes
"""
from fastapi import APIRouter
from app.services.gesture_controller import gesture_controller

router = APIRouter(prefix="/gestures", tags=["gestures"])

@router.get("/")
async def list_gestures():
    """List all gestures"""
    return {
        "gestures": [],
        "count": 0,
        "message": "Gesture listing not yet implemented"
    }

@router.get("/default")
async def get_default_gestures():
    """Get default gestures"""
    default_gestures = [
        {"name": "fist", "category": "static", "action": "STOP_MACHINE"},
        {"name": "open_hand", "category": "static", "action": "START_MACHINE"},
        {"name": "one_finger", "category": "static", "action": "MODE_1"},
        {"name": "two_fingers", "category": "static", "action": "MODE_2"},
        {"name": "three_fingers", "category": "static", "action": "MODE_3"},
        {"name": "four_fingers", "category": "static", "action": "MODE_4"},
        {"name": "five_fingers", "category": "static", "action": "MODE_5"},
        {"name": "ok_sign", "category": "static", "action": "CONFIRM"},
        {"name": "swipe_left", "category": "dynamic", "action": "MOVE_LEFT"},
        {"name": "swipe_right", "category": "dynamic", "action": "MOVE_RIGHT"},
        {"name": "swipe_up", "category": "dynamic", "action": "MOVE_UP"},
        {"name": "swipe_down", "category": "dynamic", "action": "MOVE_DOWN"},
    ]
    return {
        "gestures": default_gestures,
        "count": len(default_gestures)
    }

@router.get("/logs")
async def get_action_logs():
    """Get recent action logs"""
    return gesture_controller.get_logs()