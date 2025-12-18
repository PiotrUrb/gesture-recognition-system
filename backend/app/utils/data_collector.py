# backend/app/utils/data_collector.py

"""
Data Collector - Collect training data from camera
"""
import cv2
import numpy as np
from pathlib import Path
import time
import logging
from typing import Optional

logger = logging.getLogger(__name__)

class DataCollector:
    """
    Collects training data from camera
    """
    
    def __init__(self, output_dir: str = './data/collected'):
        """
        Initialize data collector
        
        Args:
            output_dir: Directory to save collected data
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"DataCollector initialized: {self.output_dir}")
    
    def collect_gesture_data(
        self,
        gesture_name: str,
        num_samples: int = 100,
        camera_manager=None,
        hand_detector=None
    ) -> dict:
        """
        Collect training data for a gesture
        
        Args:
            gesture_name: Name of gesture to collect
            num_samples: Number of samples to collect
            camera_manager: CameraManager instance
            hand_detector: HandDetector instance
            
        Returns:
            Dict with collection statistics
        """
        gesture_dir = self.output_dir / gesture_name
        gesture_dir.mkdir(exist_ok=True)
        
        print(f"\n{'='*60}")
        print(f"📸 COLLECTING DATA: {gesture_name}")
        print(f"{'='*60}")
        print(f"Target samples: {num_samples}")
        print(f"\n👉 Show '{gesture_name}' gesture to camera")
        print("   Press SPACE to capture")
        print("   Press 'q' to stop early\n")
        
        collected = 0
        skipped = 0
        
        try:
            while collected < num_samples:
                # Get frame
                frame = camera_manager.get_frame(0)
                if frame is None:
                    break
                
                # Detect hands
                image_rgb, results = hand_detector.detect_hands(frame)
                landmarks = hand_detector.extract_landmarks(results)
                
                # Draw
                output_image = hand_detector.draw_landmarks(image_rgb, results)
                
                # Status overlay
                progress = f"{collected}/{num_samples}"
                cv2.putText(output_image, f"Gesture: {gesture_name}", (10, 30),
                           cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                cv2.putText(output_image, f"Collected: {progress}", (10, 70),
                           cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)
                cv2.putText(output_image, "Press SPACE to capture", (10, 110),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
                
                if landmarks:
                    cv2.putText(output_image, "Hand detected!", (10, 150),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                else:
                    cv2.putText(output_image, "No hand detected", (10, 150),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                
                cv2.imshow('Data Collection', output_image)
                
                key = cv2.waitKey(1) & 0xFF
                
                # Capture on SPACE
                if key == ord(' '):
                    if landmarks:
                        # Save image
                        timestamp = int(time.time() * 1000)
                        filename = f"{gesture_name}_{timestamp}_{collected}.jpg"
                        filepath = gesture_dir / filename
                        
                        cv2.imwrite(str(filepath), frame)
                        collected += 1
                        
                        print(f"✅ Captured {collected}/{num_samples}")
                        time.sleep(0.2)  # Debounce
                    else:
                        skipped += 1
                        print(f"⚠️  No hand detected, skipped")
                
                # Quit
                elif key == ord('q'):
                    print(f"\n⚠️  Collection stopped early")
                    break
        
        except KeyboardInterrupt:
            print(f"\n⚠️  Collection interrupted")
        
        finally:
            cv2.destroyAllWindows()
        
        # Statistics
        stats = {
            'gesture': gesture_name,
            'collected': collected,
            'skipped': skipped,
            'target': num_samples,
            'completion': collected / num_samples * 100
        }
        
        print(f"\n{'='*60}")
        print("📊 COLLECTION SUMMARY")
        print(f"{'='*60}")
        print(f"Collected: {collected}/{num_samples} ({stats['completion']:.1f}%)")
        print(f"Skipped: {skipped}")
        print(f"Saved to: {gesture_dir}")
        
        return stats

# Global instance
data_collector = DataCollector()
