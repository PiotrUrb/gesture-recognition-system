"""
Gesture Controller
Manages detection modes, executes actions, and detects dynamic gestures (swipes)
"""
import time
import logging
from datetime import datetime
from typing import Optional, List, Dict, Tuple
import numpy as np

logger = logging.getLogger(__name__)

class MovementAnalyzer:
    """
    Analyzes hand movement over time to detect dynamic gestures (swipes)
    """
    def __init__(self, buffer_size=15): # Zwiększony bufor
        self.buffer_size = buffer_size
        self.position_buffer: List[Tuple[float, float]] = [] # (x, y) history
        self.last_dynamic_gesture_time = 0
        self.cooldown = 0.8 # Krótszy cooldown
        
        # Progi czułości (Dostosowane)
        self.swipe_threshold = 0.10  # Zmniejszony próg (10% ekranu)
        self.min_velocity = 0.02     # Minimalna prędkość

    def add_position(self, landmarks):
        """Add wrist position to buffer"""
        if not landmarks:
            return

        # Wrist is index 0
        wrist = landmarks[0]
        self.position_buffer.append((wrist['x'], wrist['y']))
        
        # Keep buffer size fixed
        if len(self.position_buffer) > self.buffer_size:
            self.position_buffer.pop(0)

    def analyze_movement(self) -> Optional[str]:
        """Check for dynamic gestures based on buffer"""
        current_time = time.time()
        if current_time - self.last_dynamic_gesture_time < self.cooldown:
            return None

        if len(self.position_buffer) < 5:
            return None

        # Get start and end points (średnia z 3 pierwszych i 3 ostatnich dla stabilności)
        start_x = np.mean([p[0] for p in self.position_buffer[:3]])
        start_y = np.mean([p[1] for p in self.position_buffer[:3]])
        end_x = np.mean([p[0] for p in self.position_buffer[-3:]])
        end_y = np.mean([p[1] for p in self.position_buffer[-3:]])
        
        dx = end_x - start_x
        dy = end_y - start_y
        
        abs_dx = abs(dx)
        abs_dy = abs(dy)

        # Debug log (opcjonalnie odkomentuj, żeby widzieć wartości w konsoli)
        # logger.info(f"Movement: dx={dx:.2f}, dy={dy:.2f}")

        # Check Swipe Left / Right (Dominujący ruch w poziomie)
        if abs_dx > self.swipe_threshold and abs_dx > abs_dy * 1.5:
            self.last_dynamic_gesture_time = current_time
            self.position_buffer.clear()
            direction = "swipe_left" if dx < 0 else "swipe_right" # X rośnie w prawo, więc dx > 0 to right
            # Uwaga: W kamerze (lustro) może być odwrotnie!
            return direction

        # Check Swipe Up / Down (Dominujący ruch w pionie)
        if abs_dy > self.swipe_threshold and abs_dy > abs_dx * 1.5:
            self.last_dynamic_gesture_time = current_time
            self.position_buffer.clear()
            return "swipe_up" if dy < 0 else "swipe_down" # Y rośnie w dół, więc dy < 0 to up

        return None

class GestureController:
    def __init__(self):
        self.mode = "standard"  # standard, safe, all
        self.active_gesture = None
        self.gesture_start_time = 0
        self.hold_duration = 2.0
        self.last_action_time = 0
        self.cooldown = 1.0
        self.history: List[Dict] = []
        
        # Analizator Ruchu
        self.movement_analyzer = MovementAnalyzer()

    def set_mode(self, mode: str):
        if mode in ["standard", "safe", "all"]:
            self.mode = mode
            self.reset_state()
            logger.info(f"Mode changed to: {mode}")
            return True
        return False

    def reset_state(self):
        self.active_gesture = None
        self.gesture_start_time = 0
        self.movement_analyzer.position_buffer.clear()

    def log_action(self, gesture_name: str, confidence: float):
        entry = {
            "id": len(self.history) + 1,
            "timestamp": datetime.now().isoformat(),
            "gesture": gesture_name,
            "confidence": float(confidence),
            "mode": self.mode
        }
        self.history.insert(0, entry)
        self.history = self.history[:100]
        logger.info(f"Action logged: {gesture_name}")

    def get_logs(self):
        return self.history

    def process_gesture(self, gesture_name: str, confidence: float, landmarks=None) -> dict:
        """
        Process detected gesture AND movement
        """
        current_time = time.time()
        result = {
            "action_triggered": False,
            "progress": 0.0,
            "message": ""
        }

        if landmarks:
            self.movement_analyzer.add_position(landmarks)
            dynamic_gesture = self.movement_analyzer.analyze_movement()
            
            if dynamic_gesture:
                result["action_triggered"] = True
                result["message"] = f"DYNAMIC: {dynamic_gesture.upper()}"
                self.log_action(dynamic_gesture, 1.0)
                return result

        if confidence < 0.7:
            self.reset_state()
            return result

        if self.mode == "all":
            if current_time - self.last_action_time > 0.5:
                result["action_triggered"] = True
                result["message"] = f"Detected: {gesture_name}"
                self.last_action_time = current_time
            return result

        if self.mode == "safe":
            if self.active_gesture != gesture_name:
                self.active_gesture = gesture_name
                self.gesture_start_time = current_time
                result["progress"] = 0.0
            else:
                elapsed = current_time - self.gesture_start_time
                progress = min(elapsed / self.hold_duration, 1.0)
                result["progress"] = progress

                if progress >= 1.0 and (current_time - self.last_action_time > self.cooldown):
                    result["action_triggered"] = True
                    result["message"] = f"ACTION EXECUTED: {gesture_name}"
                    self.log_action(gesture_name, confidence)
                    self.last_action_time = current_time
                    self.reset_state()

        if self.mode == "standard":
            if current_time - self.last_action_time > self.cooldown:
                result["action_triggered"] = True
                result["message"] = f"Quick Action: {gesture_name}"
                self.log_action(gesture_name, confidence)
                self.last_action_time = current_time

        return result

# Global instance
gesture_controller = GestureController()
