"""
Camera Manager Service
Handles multiple camera sources (USB, IP, File)
with extended settings support for UI sliders.
"""

from typing import List, Optional, Dict

import cv2
import numpy as np
import logging

logger = logging.getLogger(__name__)


class CameraManager:
    """Manages multiple camera sources - USB, IP (RTSP), and video files"""

    def __init__(self):
        self.cameras: Dict[int, cv2.VideoCapture] = {}
        self.camera_configs: Dict[int, dict] = {}
        self.camera_settings: Dict[int, dict] = {}

    # ---------- discovery ----------

    def detect_usb_cameras(self, max_cameras: int = 5) -> List[int]:
        """
        Detect available USB cameras by attempting to open them.
        Returns: list of available indices.
        """
        available_cameras: List[int] = []
        logger.info(f"Scanning for USB cameras (checking indices 0-{max_cameras - 1})...")

        for i in range(max_cameras):
            try:
                cap = cv2.VideoCapture(i)
                if cap.isOpened():
                    ret, _ = cap.read()
                    if ret:
                        available_cameras.append(i)
                        logger.info(f"✅ Camera {i} detected")
                cap.release()
            except Exception as e:
                logger.debug(f"Camera {i} check failed: {e}")
                continue

        if not available_cameras:
            logger.warning("⚠️ No USB cameras detected")
        return available_cameras

    # ---------- lifecycle ----------

    def add_camera(
        self,
        camera_id: int,
        source: str,
        camera_type: str = "usb",
        resolution: tuple[int, int] = (640, 480),
        fps: int = 30,
    ) -> bool:
        """Add a camera source"""
        try:
            logger.info(f"Adding camera {camera_id}: type={camera_type}, source={source}")

            if camera_type == "usb":
                cap = cv2.VideoCapture(int(source))
            elif camera_type in {"ip", "file"}:
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
                "source": source,
                "type": camera_type,
                "resolution": resolution,
                "fps": fps,
                "name": f"Camera {camera_id}",
            }

            # settings na skali 0‑200 – pod UI
            self.camera_settings[camera_id] = {
                "brightness": 100,
                "contrast": 100,
                "saturation": 100,
                "gamma": 100,
                "hue": 0,
                "blur": 0,
                "exposure": 100,
            }

            logger.info(f"✅ Camera {camera_id} added successfully")
            return True
        except Exception as e:
            logger.error(f"Error adding camera {camera_id}: {e}", exc_info=True)
            return False

    def remove_camera(self, camera_id: int) -> bool:
        """Remove a camera"""
        if camera_id in self.cameras:
            logger.info(f"Removing camera {camera_id}")
            self.cameras[camera_id].release()
            del self.cameras[camera_id]
            self.camera_configs.pop(camera_id, None)
            self.camera_settings.pop(camera_id, None)
            logger.info(f"✅ Camera {camera_id} removed")
            return True

        logger.warning(f"Camera {camera_id} not found")
        return False

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

    # ---------- frames ----------

    def get_frame(self, camera_id: int) -> Optional[np.ndarray]:
        """Get a frame from camera"""
        if camera_id not in self.cameras:
            logger.warning(f"Camera {camera_id} not found")
            return None

        try:
            ret, frame = self.cameras[camera_id].read()
            if ret:
                return frame
            logger.warning(f"Failed to read frame from camera {camera_id}")
            return None
        except Exception as e:
            logger.error(f"Error reading frame from camera {camera_id}: {e}", exc_info=True)
            return None

    # ---------- configuration ----------

    def configure_camera(
        self,
        camera_id: int,
        width: Optional[int] = None,
        height: Optional[int] = None,
        fps: Optional[int] = None,
    ) -> bool:
        """
        Configure camera resolution and FPS.
        """
        if camera_id not in self.cameras:
            logger.warning(f"Camera {camera_id} not found")
            return False

        try:
            cap = self.cameras[camera_id]
            config = self.camera_configs[camera_id]

            cur_w, cur_h = config["resolution"]

            if width is not None:
                cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
                cur_w = width
                logger.info(f"Camera {camera_id} width set to {width}")

            if height is not None:
                cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
                cur_h = height
                logger.info(f"Camera {camera_id} height set to {height}")

            config["resolution"] = (cur_w, cur_h)

            if fps is not None:
                cap.set(cv2.CAP_PROP_FPS, fps)
                config["fps"] = fps
                logger.info(f"Camera {camera_id} FPS set to {fps}")

            return True
        except Exception as e:
            logger.error(f"Error configuring camera {camera_id}: {e}", exc_info=True)
            return False

    def update_settings(self, camera_id: int, settings: dict) -> bool:
        """
        Update camera settings (0–200 UI scale -> OpenCV ranges).
        """
        if camera_id not in self.cameras:
            logger.warning(f"Camera {camera_id} not found")
            return False

        try:
            cap = self.cameras[camera_id]
            cur = self.camera_settings.setdefault(camera_id, {})

            if "brightness" in settings:
                v = float(settings["brightness"])
                opencv_v = (v / 100.0) * 64.0 - 64.0
                cap.set(cv2.CAP_PROP_BRIGHTNESS, opencv_v)
                cur["brightness"] = v
                logger.info(f"Camera {camera_id} brightness: {v}%")

            if "contrast" in settings:
                v = float(settings["contrast"])
                opencv_v = (v / 100.0) * 64.0
                cap.set(cv2.CAP_PROP_CONTRAST, opencv_v)
                cur["contrast"] = v
                logger.info(f"Camera {camera_id} contrast: {v}%")

            if "saturation" in settings:
                v = float(settings["saturation"])
                opencv_v = (v / 100.0) * 128.0
                cap.set(cv2.CAP_PROP_SATURATION, opencv_v)
                cur["saturation"] = v
                logger.info(f"Camera {camera_id} saturation: {v}%")

            if "gamma" in settings:
                cur["gamma"] = float(settings["gamma"])
                logger.info(f"Camera {camera_id} gamma: {settings['gamma']}%")

            if "hue" in settings:
                cur["hue"] = float(settings["hue"])
                logger.info(f"Camera {camera_id} hue: {settings['hue']}°")

            if "blur" in settings:
                cur["blur"] = float(settings["blur"])
                logger.info(f"Camera {camera_id} blur: {settings['blur']}")

            if "exposure" in settings:
                v = float(settings["exposure"])
                opencv_v = (v / 100.0) * 2.0 - 2.0
                try:
                    cap.set(cv2.CAP_PROP_EXPOSURE, opencv_v)
                except Exception:
                    logger.warning(
                        f"Camera {camera_id} doesn't support exposure adjustment"
                    )
                cur["exposure"] = v
                logger.info(f"Camera {camera_id} exposure: {v}%")

            logger.info(f"✅ Updated settings for camera {camera_id}")
            return True
        except Exception as e:
            logger.error(f"Error updating settings for camera {camera_id}: {e}", exc_info=True)
            return False

    # ---------- info ----------

    def get_camera_settings(self, camera_id: int) -> Optional[dict]:
        """Get current camera settings"""
        return self.camera_settings.get(camera_id)

    def get_camera_info(self, camera_id: int) -> Optional[dict]:
        """Get camera information"""
        if camera_id not in self.cameras:
            return None

        cap = self.cameras[camera_id]
        config = self.camera_configs[camera_id]

        return {
            "id": camera_id,
            "name": config.get("name", f"Camera {camera_id}"),
            "source": config["source"],
            "type": config["type"],
            "resolution": config["resolution"],
            "fps": config["fps"],
            "is_opened": cap.isOpened(),
            "width": config["resolution"][0],
            "height": config["resolution"][1],
            "actual_width": int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
            "actual_height": int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)),
            "actual_fps": int(cap.get(cv2.CAP_PROP_FPS)),
        }

    def list_cameras(self) -> List[dict]:
        """List all active cameras"""
        return [self.get_camera_info(cam_id) for cam_id in self.cameras.keys()]


# Global instance
camera_manager = CameraManager()
