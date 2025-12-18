"""
ZMIANA #1: backend/app/services/camera_manager.py
Konwersja 0-200 + nowe parametry (gamma, hue, blur, exposure)
"""

import cv2
from typing import List, Optional, Dict
import numpy as np
import logging

logger = logging.getLogger(__name__)

class CameraManager:
    """Manages multiple camera sources - USB, IP (RTSP), and video files"""
    
    def __init__(self):
        self.cameras: Dict[int, cv2.VideoCapture] = {}
        self.camera_configs: Dict[int, dict] = {}
        self.camera_settings: Dict[int, dict] = {}  # Store current settings
    
    def add_camera(self, camera_id: int, source: str, camera_type: str = 'usb', 
                   resolution: tuple = (640, 480), fps: int = 30) -> bool:
        """Add a camera source"""
        try:
            logger.info(f"Adding camera {camera_id}: type={camera_type}, source={source}")
            
            if camera_type == 'usb':
                cap = cv2.VideoCapture(int(source))
            elif camera_type == 'ip':
                cap = cv2.VideoCapture(source)
            elif camera_type == 'file':
                cap = cv2.VideoCapture(source)
            else:
                logger.error(f"Unknown camera type: {camera_type}")
                return False
            
            if not cap.isOpened():
                logger.error(f"Failed to open camera {camera_id}")
                return False
            
            width, height = resolution
            cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
            cap.set(cv2.CAP_PROP_FPS, fps)
            
            self.cameras[camera_id] = cap
            self.camera_configs[camera_id] = {
                'source': source,
                'type': camera_type,
                'resolution': resolution,
                'fps': fps,
                'name': f"Camera {camera_id}"
            }
            
            # Initialize default settings (0-200 scale)
            self.camera_settings[camera_id] = {
                'brightness': 100,      # 0-200 (100=normal)
                'contrast': 100,        # 0-200 (100=normal)
                'saturation': 100,      # 0-200 (100=normal)
                'gamma': 100,           # 0-200 (100=normal)
                'hue': 0,              # -180 do 180
                'blur': 0,             # 0-50
                'exposure': 100        # 0-200 (100=normal)
            }
            
            logger.info(f"✅ Camera {camera_id} added successfully")
            return True
        except Exception as e:
            logger.error(f"Error adding camera {camera_id}: {e}")
            return False
    
    def get_frame(self, camera_id: int) -> Optional[np.ndarray]:
        """Get a frame from camera"""
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
    
    def update_settings(self, camera_id: int, settings: dict) -> bool:
        """
        Update camera settings (0-200 scale)
        
        Parameters:
        - brightness: 0-200 (100=normal, 0=very dark, 200=very bright)
        - contrast: 0-200 (100=normal, 0=flat, 200=high)
        - saturation: 0-200 (100=normal, 0=grayscale, 200=super saturated)
        - gamma: 0-200 (100=normal, <100=darker, >100=brighter)
        - hue: -180 to 180 (color shift)
        - blur: 0-50 (smoothing effect)
        - exposure: 0-200 (100=normal)
        """
        if camera_id not in self.cameras:
            logger.warning(f"Camera {camera_id} not found")
            return False
        
        try:
            cap = self.cameras[camera_id]
            
            # ✅ BRIGHTNESS: 0-200 → OpenCV -64 to 64
            if 'brightness' in settings:
                brightness_val = settings['brightness']
                # Map: 0 → -64, 100 → 0, 200 → 64
                opencv_brightness = (brightness_val / 100.0) * 64.0 - 64.0
                cap.set(cv2.CAP_PROP_BRIGHTNESS, opencv_brightness)
                self.camera_settings[camera_id]['brightness'] = brightness_val
                logger.info(f"Camera {camera_id} brightness: {brightness_val}% → OpenCV: {opencv_brightness:.2f}")
            
            # ✅ CONTRAST: 0-200 → OpenCV 0 to 128
            if 'contrast' in settings:
                contrast_val = settings['contrast']
                # Map: 0 → 0, 100 → 64, 200 → 128
                opencv_contrast = (contrast_val / 100.0) * 64.0
                cap.set(cv2.CAP_PROP_CONTRAST, opencv_contrast)
                self.camera_settings[camera_id]['contrast'] = contrast_val
                logger.info(f"Camera {camera_id} contrast: {contrast_val}% → OpenCV: {opencv_contrast:.2f}")
            
            # ✅ SATURATION: 0-200 → OpenCV 0 to 256
            # FIX: Nie ograniczaj saturacji aby obraz nie był czarno-biały!
            if 'saturation' in settings:
                saturation_val = settings['saturation']
                # Map: 0 → 0, 100 → 128, 200 → 256
                opencv_saturation = (saturation_val / 100.0) * 128.0
                cap.set(cv2.CAP_PROP_SATURATION, opencv_saturation)
                self.camera_settings[camera_id]['saturation'] = saturation_val
                logger.info(f"Camera {camera_id} saturation: {saturation_val}% → OpenCV: {opencv_saturation:.2f}")
            
            # ✅ GAMMA: 0-200 (przetworzyć w frame processing)
            if 'gamma' in settings:
                self.camera_settings[camera_id]['gamma'] = settings['gamma']
                logger.info(f"Camera {camera_id} gamma: {settings['gamma']}%")
            
            # ✅ HUE: -180 to 180 (przetworzyć w frame processing)
            if 'hue' in settings:
                self.camera_settings[camera_id]['hue'] = settings['hue']
                logger.info(f"Camera {camera_id} hue: {settings['hue']}°")
            
            # ✅ BLUR: 0-50 (przetworzyć w frame processing)
            if 'blur' in settings:
                self.camera_settings[camera_id]['blur'] = settings['blur']
                logger.info(f"Camera {camera_id} blur: {settings['blur']}")
            
            # ✅ EXPOSURE: 0-200 (mapować na EV)
            if 'exposure' in settings:
                exposure_val = settings['exposure']
                # Map: 0 → -2, 100 → 0, 200 → 2
                opencv_exposure = (exposure_val / 100.0) * 2.0 - 2.0
                # Note: Not all cameras support this
                try:
                    cap.set(cv2.CAP_PROP_EXPOSURE, opencv_exposure)
                except:
                    logger.warning(f"Camera {camera_id} doesn't support exposure adjustment")
                self.camera_settings[camera_id]['exposure'] = exposure_val
                logger.info(f"Camera {camera_id} exposure: {exposure_val}% → EV: {opencv_exposure:.2f}")
            
            logger.info(f"✅ Updated settings for camera {camera_id}")
            return True
        except Exception as e:
            logger.error(f"Error updating settings for camera {camera_id}: {e}")
            return False
    
    def get_camera_settings(self, camera_id: int) -> Optional[dict]:
        """Get current camera settings"""
        return self.camera_settings.get(camera_id)
    
    def remove_camera(self, camera_id: int) -> bool:
        """Remove a camera"""
        if camera_id in self.cameras:
            logger.info(f"Removing camera {camera_id}")
            self.cameras[camera_id].release()
            del self.cameras[camera_id]
            del self.camera_configs[camera_id]
            if camera_id in self.camera_settings:
                del self.camera_settings[camera_id]
            logger.info(f"✅ Camera {camera_id} removed")
            return True
        else:
            logger.warning(f"Camera {camera_id} not found")
            return False
    
    def get_camera_info(self, camera_id: int) -> Optional[dict]:
        """Get camera information"""
        if camera_id not in self.cameras:
            return None
        
        cap = self.cameras[camera_id]
        config = self.camera_configs[camera_id]
        
        return {
            'id': camera_id,
            'name': config.get('name', f"Camera {camera_id}"),
            'source': config['source'],
            'type': config['type'],
            'resolution': config['resolution'],
            'fps': config['fps'],
            'is_opened': cap.isOpened(),
            'width': config['resolution'][0],
            'height': config['resolution'][1],
            'actual_width': int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
            'actual_height': int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)),
            'actual_fps': int(cap.get(cv2.CAP_PROP_FPS))
        }
    
    def list_cameras(self) -> List[dict]:
        """List all active cameras"""
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
        self.camera_settings.clear()
        logger.info("✅ All cameras released")


# Global instance
camera_manager = CameraManager()