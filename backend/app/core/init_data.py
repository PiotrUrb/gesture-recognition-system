# backend/app/core/init_data.py


"""
Initialize default data in database
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.gesture import Gesture
import logging

logger = logging.getLogger(__name__)

DEFAULT_GESTURES = [
    {
        "name": "fist",
        "category": "static",
        "description": "Closed fist",
        "machine_action": "STOP_MACHINE",
        "is_default": True,
        "confidence_threshold": 0.85
    },
    {
        "name": "open_hand",
        "category": "static",
        "description": "Open palm",
        "machine_action": "START_MACHINE",
        "is_default": True,
        "confidence_threshold": 0.80
    },
    {
        "name": "one_finger",
        "category": "static",
        "description": "One finger pointing up",
        "machine_action": "MODE_1",
        "is_default": True,
        "confidence_threshold": 0.80
    },
    {
        "name": "two_fingers",
        "category": "static",
        "description": "Two fingers (peace sign)",
        "machine_action": "MODE_2",
        "is_default": True,
        "confidence_threshold": 0.80
    },
    {
        "name": "three_fingers",
        "category": "static",
        "description": "Three fingers up",
        "machine_action": "MODE_3",
        "is_default": True,
        "confidence_threshold": 0.80
    },
    {
        "name": "four_fingers",
        "category": "static",
        "description": "Four fingers up",
        "machine_action": "MODE_4",
        "is_default": True,
        "confidence_threshold": 0.80
    },
    {
        "name": "five_fingers",
        "category": "static",
        "description": "Five fingers (open hand with spread fingers)",
        "machine_action": "MODE_5",
        "is_default": True,
        "confidence_threshold": 0.80
    },
    {
        "name": "ok_sign",
        "category": "static",
        "description": "OK sign (thumb and index finger circle)",
        "machine_action": "CONFIRM",
        "is_default": True,
        "confidence_threshold": 0.85
    },
    {
        "name": "swipe_left",
        "category": "dynamic",
        "description": "Hand moving left",
        "machine_action": "MOVE_LEFT",
        "is_default": True,
        "confidence_threshold": 0.75
    },
    {
        "name": "swipe_right",
        "category": "dynamic",
        "description": "Hand moving right",
        "machine_action": "MOVE_RIGHT",
        "is_default": True,
        "confidence_threshold": 0.75
    },
    {
        "name": "swipe_up",
        "category": "dynamic",
        "description": "Hand moving up",
        "machine_action": "MOVE_UP",
        "is_default": True,
        "confidence_threshold": 0.75
    },
    {
        "name": "swipe_down",
        "category": "dynamic",
        "description": "Hand moving down",
        "machine_action": "MOVE_DOWN",
        "is_default": True,
        "confidence_threshold": 0.75
    }
]

async def init_default_gestures(db: AsyncSession):
    """Initialize default gestures in database"""
    try:
        # Check if gestures already exist
        result = await db.execute(select(Gesture).limit(1))
        existing = result.scalar_one_or_none()
        
        if existing:
            logger.info("Default gestures already initialized")
            return
        
        # Add default gestures
        for gesture_data in DEFAULT_GESTURES:
            gesture = Gesture(**gesture_data)
            db.add(gesture)
        
        await db.commit()
        logger.info(f"✅ Initialized {len(DEFAULT_GESTURES)} default gestures")
        
    except Exception as e:
        logger.error(f"Error initializing default gestures: {e}")
        await db.rollback()
        raise
