# backend/app/services/hand_detector.py

"""
Hand Detection Service using MediaPipe Hands
"""
import cv2
import mediapipe as mp
import numpy as np
from typing import Optional, List, Tuple
import logging

logger = logging.getLogger(__name__)

class HandDetector:
    """
    Detects hands and extracts landmarks using MediaPipe Hands
    """
    
    def __init__(
        self,
        static_image_mode: bool = False,
        max_num_hands: int = 4,
        min_detection_confidence: float = 0.7,
        min_tracking_confidence: float = 0.3
    ):
        """
        Initialize MediaPipe Hands
        
        Args:
            static_image_mode: If True, treats each image independently
            max_num_hands: Maximum number of hands to detect
            min_detection_confidence: Minimum confidence for detection
            min_tracking_confidence: Minimum confidence for tracking
        """
        self.mp_hands = mp.solutions.hands
        self.mp_drawing = mp.solutions.drawing_utils
        self.mp_drawing_styles = mp.solutions.drawing_styles
        
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=max_num_hands,
            min_detection_confidence=min_detection_confidence,
            min_tracking_confidence=0.3,
            model_complexity=0
        )

        
        logger.info(f"HandDetector initialized: max_hands={max_num_hands}, "
                   f"detection_conf={min_detection_confidence}, "
                   f"tracking_conf={min_tracking_confidence}")
    
    def detect_hands(self, image: np.ndarray) -> Tuple[np.ndarray, Optional[any]]:
        """
        Detect hands in image
        
        Args:
            image: Input image (BGR format from OpenCV)
            
        Returns:
            Tuple of (processed_image, results)
            - processed_image: Image in RGB format
            - results: MediaPipe results object or None
        """
        # Convert BGR to RGB (MediaPipe expects RGB)
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        
        # To improve performance, mark image as not writeable
        image_rgb.flags.writeable = False
        
        # Process image
        results = self.hands.process(image_rgb)
        
        # Mark image as writeable again
        image_rgb.flags.writeable = True
        
        return image_rgb, results
    
    def extract_landmarks(self, results: any) -> List[List[dict]]:
        """
        Extract hand landmarks from results
        
        Args:
            results: MediaPipe results object
            
        Returns:
            List of hands, each hand is a list of 21 landmark dicts
            Each landmark dict: {'x': float, 'y': float, 'z': float}
        """
        if not results.multi_hand_landmarks:
            return []
        
        all_hands = []
        for hand_landmarks in results.multi_hand_landmarks:
            landmarks = []
            for landmark in hand_landmarks.landmark:
                landmarks.append({
                    'x': landmark.x,
                    'y': landmark.y,
                    'z': landmark.z
                })
            all_hands.append(landmarks)
        
        return all_hands
    
    def draw_landmarks(
        self,
        image: np.ndarray,
        results: any,
        draw_connections: bool = True
    ) -> np.ndarray:
        """
        Draw hand landmarks on image
        
        Args:
            image: Input image (RGB format)
            results: MediaPipe results object
            draw_connections: Whether to draw connections between landmarks
            
        Returns:
            Image with drawn landmarks
        """
        if not results.multi_hand_landmarks:
            return image
        
        # Convert back to BGR for OpenCV
        image_bgr = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
        
        for hand_landmarks in results.multi_hand_landmarks:
            if draw_connections:
                # Draw landmarks and connections
                self.mp_drawing.draw_landmarks(
                    image_bgr,
                    hand_landmarks,
                    self.mp_hands.HAND_CONNECTIONS,
                    self.mp_drawing_styles.get_default_hand_landmarks_style(),
                    self.mp_drawing_styles.get_default_hand_connections_style()
                )
            else:
                # Draw only landmarks (no connections)
                self.mp_drawing.draw_landmarks(
                    image_bgr,
                    hand_landmarks,
                    None
                )
        
        return image_bgr
    
    def get_hand_info(self, results: any) -> List[dict]:
        """
        Get detailed hand information
        
        Args:
            results: MediaPipe results object
            
        Returns:
            List of hand info dictionaries
        """
        if not results.multi_hand_landmarks or not results.multi_handedness:
            return []
        
        hands_info = []
        for i, (hand_landmarks, handedness) in enumerate(
            zip(results.multi_hand_landmarks, results.multi_handedness)
        ):
            # MediaPipe labels are mirrored (from camera perspective)
            # Flip them to match user's actual hands
            detected_label = handedness.classification[0].label
            
            # Flip the label: Left -> Right, Right -> Left
            actual_hand_type = 'Right' if detected_label == 'Left' else 'Left'
            
            hand_score = handedness.classification[0].score
            
            hands_info.append({
                'index': i,
                'type': actual_hand_type,  # Now shows correct hand
                'detected_type': detected_label,  # Original MediaPipe label
                'confidence': hand_score,
                'num_landmarks': len(hand_landmarks.landmark)
            })
        
        return hands_info

    
    def cleanup(self):
        """Release MediaPipe resources"""
        self.hands.close()
        logger.info("HandDetector cleaned up")

# Global instance
hand_detector = HandDetector()
