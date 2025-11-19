"""
Camera Manager Service
Handles multiple camera sources (USB, IP, File)
"""
import cv2
from typing import List, Optional, Dict
import numpy as np
import logging

logger = logging.getLogger(__name__)

class CameraManager:
    """
    Manages multiple camera sources
    Supports USB cameras, IP cameras (RTSP), and video files
    """
    
    def __init__(self):
        self.cameras: Dict[int, cv2.VideoCapture] = {}
        self.camera_configs: Dict[int, dict] = {}
        
    def detect_usb_cameras(self, max_cameras: int = 5) -> List[int]:
        """
        Detect available USB cameras
        
        Args:
            max_cameras: Maximum number of cameras to check
            
        Returns:
            List of camera indices that are available
        """
        available = []
        logger.info(f"Detecting USB cameras (checking {max_cameras} indices)...")
        
        for i in range(max_cameras):
            cap = cv2.VideoCapture(i)
            if cap.isOpened():
                available.append(i)
                logger.info(f"✅ Found USB camera at index {i}")
                cap.release()
            else:
                logger.debug(f"No camera at index {i}")
        
        logger.info(f"Detected {len(available)} USB cameras: {available}")
        return available
    
    def add_camera(
        self,
        camera_id: int,
        source: str,
        camera_type: str = 'usb',
        resolution: tuple = (640, 480),
        fps: int = 30
    ) -> bool:
        """
        Add a camera source
        
        Args:
            camera_id: Unique ID for this camera
            source: Camera source (index for USB, URL for IP, path for file)
            camera_type: 'usb', 'ip', or 'file'
            resolution: (width, height) tuple
            fps: Frames per second
            
        Returns:
            True if camera added successfully, False otherwise
        """
        try:
            logger.info(f"Adding camera {camera_id}: type={camera_type}, source={source}")
            
            # Create VideoCapture based on type
            if camera_type == 'usb':
                cap = cv2.VideoCapture(int(source))
            elif camera_type == 'ip':
                cap = cv2.VideoCapture(source)  # RTSP URL
            elif camera_type == 'file':
                cap = cv2.VideoCapture(source)  # Video file path
            else:
                logger.error(f"Unknown camera type: {camera_type}")
                return False
            
            if not cap.isOpened():
                logger.error(f"Failed to open camera {camera_id}")
                return False
            
            # Configure camera
            width, height = resolution
            cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
            cap.set(cv2.CAP_PROP_FPS, fps)
            
            # Store camera and config
            self.cameras[camera_id] = cap
            self.camera_configs[camera_id] = {
                'source': source,
                'type': camera_type,
                'resolution': resolution,
                'fps': fps
            }
            
            logger.info(f"✅ Camera {camera_id} added successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error adding camera {camera_id}: {e}")
            return False
    
    def remove_camera(self, camera_id: int) -> bool:
        """
        Remove a camera
        
        Args:
            camera_id: ID of camera to remove
            
        Returns:
            True if removed successfully, False if not found
        """
        if camera_id in self.cameras:
            logger.info(f"Removing camera {camera_id}")
            self.cameras[camera_id].release()
            del self.cameras[camera_id]
            del self.camera_configs[camera_id]
            logger.info(f"✅ Camera {camera_id} removed")
            return True
        else:
            logger.warning(f"Camera {camera_id} not found")
            return False
    
    def get_frame(self, camera_id: int) -> Optional[np.ndarray]:
        """
        Get a frame from camera
        
        Args:
            camera_id: ID of camera
            
        Returns:
            Frame as numpy array or None if error
        """
        if camera_id not in self.cameras:
            logger.warning(f"Camera {camera_id} not found")
            return None
        
        try:
            ret, frame = self.cameras[camera_id].read()
            if ret:
                return frame
            else:
                logger.warning(f"Failed to read frame from camera {camera_id}")
                return None
        except Exception as e:
            logger.error(f"Error reading frame from camera {camera_id}: {e}")
            return None
    
    def configure_camera(
        self,
        camera_id: int,
        width: Optional[int] = None,
        height: Optional[int] = None,
        fps: Optional[int] = None
    ) -> bool:
        """
        Configure camera parameters
        
        Args:
            camera_id: ID of camera
            width: New width (optional)
            height: New height (optional)
            fps: New FPS (optional)
            
        Returns:
            True if configured successfully
        """
        if camera_id not in self.cameras:
            logger.warning(f"Camera {camera_id} not found")
            return False
        
        try:
            cap = self.cameras[camera_id]
            
            if width is not None and height is not None:
                cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
                cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
                self.camera_configs[camera_id]['resolution'] = (width, height)
                logger.info(f"Camera {camera_id} resolution set to {width}x{height}")
            
            if fps is not None:
                cap.set(cv2.CAP_PROP_FPS, fps)
                self.camera_configs[camera_id]['fps'] = fps
                logger.info(f"Camera {camera_id} FPS set to {fps}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error configuring camera {camera_id}: {e}")
            return False
    
    def get_camera_info(self, camera_id: int) -> Optional[dict]:
        """
        Get camera information
        
        Args:
            camera_id: ID of camera
            
        Returns:
            Dictionary with camera info or None
        """
        if camera_id not in self.cameras:
            return None
        
        cap = self.cameras[camera_id]
        config = self.camera_configs[camera_id]
        
        return {
            'id': camera_id,
            'source': config['source'],
            'type': config['type'],
            'resolution': config['resolution'],
            'fps': config['fps'],
            'is_opened': cap.isOpened(),
            'actual_width': int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
            'actual_height': int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)),
            'actual_fps': int(cap.get(cv2.CAP_PROP_FPS))
        }
    
    def list_cameras(self) -> List[dict]:
        """
        List all active cameras
        
        Returns:
            List of camera info dictionaries
        """
        return [
            self.get_camera_info(cam_id)
            for cam_id in self.cameras.keys()
        ]
    
    def cleanup(self):
        """Release all cameras"""
        logger.info("Cleaning up cameras...")
        for camera_id, cap in self.cameras.items():
            cap.release()
            logger.info(f"Released camera {camera_id}")
        self.cameras.clear()
        self.camera_configs.clear()
        logger.info("✅ All cameras released")

# Global instance
camera_manager = CameraManager()
