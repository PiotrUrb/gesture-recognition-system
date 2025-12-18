# backend/app/services/feature_processor.py

"""
Feature Processor
Converts hand landmarks to ML features
"""
import numpy as np
from typing import List, Dict, Tuple
import math
import logging

logger = logging.getLogger(__name__)

class FeatureProcessor:
    """
    Processes hand landmarks into ML features
    """
    
    # MediaPipe Hand landmark indices
    LANDMARK_NAMES = [
        'WRIST',           # 0
        'THUMB_CMC',       # 1
        'THUMB_MCP',       # 2
        'THUMB_IP',        # 3
        'THUMB_TIP',       # 4
        'INDEX_FINGER_MCP', # 5
        'INDEX_FINGER_PIP', # 6
        'INDEX_FINGER_DIP', # 7
        'INDEX_FINGER_TIP', # 8
        'MIDDLE_FINGER_MCP',# 9
        'MIDDLE_FINGER_PIP',# 10
        'MIDDLE_FINGER_DIP',# 11
        'MIDDLE_FINGER_TIP',# 12
        'RING_FINGER_MCP',  # 13
        'RING_FINGER_PIP',  # 14
        'RING_FINGER_DIP',  # 15
        'RING_FINGER_TIP',  # 16
        'PINKY_MCP',        # 17
        'PINKY_PIP',        # 18
        'PINKY_DIP',        # 19
        'PINKY_TIP'         # 20
    ]
    
    def __init__(self):
        """Initialize Feature Processor"""
        logger.info("FeatureProcessor initialized")
    
    def normalize_landmarks(
        self,
        landmarks: List[dict]
    ) -> np.ndarray:
        """
        Normalize landmarks to be translation and scale invariant
        
        Args:
            landmarks: List of 21 landmark dicts with x, y, z
            
        Returns:
            Normalized landmarks as numpy array (21, 3)
        """
        if len(landmarks) != 21:
            raise ValueError(f"Expected 21 landmarks, got {len(landmarks)}")
        
        # Convert to numpy array
        points = np.array([[lm['x'], lm['y'], lm['z']] for lm in landmarks])
        
        # Get wrist point (landmark 0) as reference
        wrist = points[0]
        
        # Translate to wrist origin
        points_centered = points - wrist
        
        # Calculate scale (max distance from wrist)
        distances = np.linalg.norm(points_centered, axis=1)
        max_distance = np.max(distances)
        
        # Scale normalization
        if max_distance > 0:
            points_normalized = points_centered / max_distance
        else:
            points_normalized = points_centered
        
        return points_normalized
    
    def calculate_distances(
        self,
        landmarks: np.ndarray
    ) -> Dict[str, float]:
        """
        Calculate key distances between landmarks
        
        Args:
            landmarks: Normalized landmarks (21, 3)
            
        Returns:
            Dictionary of distances
        """
        distances = {}
        
        # Finger tip to wrist distances
        finger_tips = [4, 8, 12, 16, 20]  # Thumb, Index, Middle, Ring, Pinky
        finger_names = ['thumb', 'index', 'middle', 'ring', 'pinky']
        
        wrist = landmarks[0]
        
        for tip_idx, finger_name in zip(finger_tips, finger_names):
            tip = landmarks[tip_idx]
            distance = np.linalg.norm(tip - wrist)
            distances[f'{finger_name}_tip_to_wrist'] = distance
        
        # Finger tip to palm center distances
        palm_center = np.mean(landmarks[[0, 5, 9, 13, 17]], axis=0)  # Wrist + MCPs
        
        for tip_idx, finger_name in zip(finger_tips, finger_names):
            tip = landmarks[tip_idx]
            distance = np.linalg.norm(tip - palm_center)
            distances[f'{finger_name}_tip_to_palm'] = distance
        
        # Adjacent finger tip distances
        for i in range(len(finger_tips) - 1):
            tip1 = landmarks[finger_tips[i]]
            tip2 = landmarks[finger_tips[i + 1]]
            distance = np.linalg.norm(tip2 - tip1)
            distances[f'{finger_names[i]}_to_{finger_names[i+1]}_tip'] = distance
        
        return distances
    
    def calculate_angles(
        self,
        landmarks: np.ndarray
    ) -> Dict[str, float]:
        """
        Calculate angles between joints
        
        Args:
            landmarks: Normalized landmarks (21, 3)
            
        Returns:
            Dictionary of angles in degrees
        """
        angles = {}
        
        # Finger bend angles (PIP joint angles)
        # For each finger: MCP -> PIP -> DIP
        finger_joints = [
            ([2, 3, 4], 'thumb'),      # Thumb: MCP, IP, TIP
            ([5, 6, 7], 'index_pip'),  # Index: MCP, PIP, DIP
            ([9, 10, 11], 'middle_pip'),
            ([13, 14, 15], 'ring_pip'),
            ([17, 18, 19], 'pinky_pip')
        ]
        
        for joint_indices, joint_name in finger_joints:
            if len(joint_indices) == 3:
                angle = self._calculate_angle_3points(
                    landmarks[joint_indices[0]],
                    landmarks[joint_indices[1]],
                    landmarks[joint_indices[2]]
                )
                angles[f'{joint_name}_angle'] = angle
        
        # Palm orientation angle (thumb to pinky)
        thumb_base = landmarks[2]  # THUMB_MCP
        pinky_base = landmarks[17]  # PINKY_MCP
        wrist = landmarks[0]
        
        palm_vector = pinky_base - thumb_base
        wrist_vector = wrist - thumb_base
        
        palm_angle = self._calculate_angle_vectors(palm_vector, wrist_vector)
        angles['palm_orientation'] = palm_angle
        
        return angles
    
    def _calculate_angle_3points(
        self,
        point1: np.ndarray,
        point2: np.ndarray,
        point3: np.ndarray
    ) -> float:
        """
        Calculate angle at point2 formed by point1-point2-point3
        
        Returns:
            Angle in degrees (0-180)
        """
        vector1 = point1 - point2
        vector2 = point3 - point2
        
        return self._calculate_angle_vectors(vector1, vector2)
    
    def _calculate_angle_vectors(
        self,
        vector1: np.ndarray,
        vector2: np.ndarray
    ) -> float:
        """
        Calculate angle between two vectors
        
        Returns:
            Angle in degrees (0-180)
        """
        # Normalize vectors
        v1_norm = vector1 / (np.linalg.norm(vector1) + 1e-10)
        v2_norm = vector2 / (np.linalg.norm(vector2) + 1e-10)
        
        # Calculate angle
        dot_product = np.clip(np.dot(v1_norm, v2_norm), -1.0, 1.0)
        angle_rad = np.arccos(dot_product)
        angle_deg = np.degrees(angle_rad)
        
        return angle_deg
    
    def extract_features(
        self,
        landmarks: List[dict]
    ) -> np.ndarray:
        """
        Extract complete feature vector from landmarks
        
        Args:
            landmarks: List of 21 landmark dicts
            
        Returns:
            Feature vector as numpy array
        """
        # Normalize landmarks
        normalized_landmarks = self.normalize_landmarks(landmarks)
        
        # Flatten normalized landmarks (21 * 3 = 63 values)
        landmark_features = normalized_landmarks.flatten()
        
        # Calculate distances
        distances = self.calculate_distances(normalized_landmarks)
        distance_features = np.array(list(distances.values()))
        
        # Calculate angles
        angles = self.calculate_angles(normalized_landmarks)
        angle_features = np.array(list(angles.values()))
        
        # Concatenate all features
        features = np.concatenate([
            landmark_features,    # 63 features
            distance_features,    # ~14 features
            angle_features        # ~6 features
        ])
        
        return features
    
    def get_feature_names(self) -> List[str]:
        """
        Get names of all features
        
        Returns:
            List of feature names
        """
        feature_names = []
        
        # Landmark coordinates
        for i, name in enumerate(self.LANDMARK_NAMES):
            feature_names.extend([
                f'{name}_x',
                f'{name}_y',
                f'{name}_z'
            ])
        
        # Distance features
        finger_names = ['thumb', 'index', 'middle', 'ring', 'pinky']
        for finger in finger_names:
            feature_names.append(f'{finger}_tip_to_wrist')
        for finger in finger_names:
            feature_names.append(f'{finger}_tip_to_palm')
        for i in range(len(finger_names) - 1):
            feature_names.append(f'{finger_names[i]}_to_{finger_names[i+1]}_tip')
        
        # Angle features
        feature_names.extend([
            'thumb_angle',
            'index_pip_angle',
            'middle_pip_angle',
            'ring_pip_angle',
            'pinky_pip_angle',
            'palm_orientation'
        ])
        
        return feature_names

# Global instance
feature_processor = FeatureProcessor()
