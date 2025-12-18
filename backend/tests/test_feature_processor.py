# backend/tests/test_feature_processor.py

"""
Test Feature Processor
"""
import sys
import os

backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, backend_dir)

from app.services.hand_detector import HandDetector
from app.services.camera_manager import CameraManager
from app.services.feature_processor import FeatureProcessor
import cv2
import numpy as np

def test_feature_extraction():
    """Test feature extraction on live camera"""
    print("\n=== Test: Feature Extraction ===")
    print("Show your hand to camera!")
    print("Press 'q' to quit\n")
    
    # Initialize
    camera_manager = CameraManager()
    hand_detector = HandDetector()
    feature_processor = FeatureProcessor()
    
    # Setup camera
    cameras = camera_manager.detect_usb_cameras()
    if not cameras:
        print("❌ No camera found!")
        return
    
    camera_manager.add_camera(0, str(cameras[0]), 'usb')
    
    print(f"✅ Camera ready\n")
    print(f"Feature names ({len(feature_processor.get_feature_names())}):")
    for i, name in enumerate(feature_processor.get_feature_names()[:10]):
        print(f"  {i}: {name}")
    print("  ...")
    print()
    
    try:
        while True:
            # Get frame
            frame = camera_manager.get_frame(0)
            if frame is None:
                break
            
            # Detect hands
            image_rgb, results = hand_detector.detect_hands(frame)
            landmarks = hand_detector.extract_landmarks(results)
            
            # Process features if hand detected
            if landmarks:
                for i, hand_landmarks in enumerate(landmarks):
                    # Extract features
                    features = feature_processor.extract_features(hand_landmarks)
                    
                    # Normalize landmarks
                    normalized = feature_processor.normalize_landmarks(hand_landmarks)
                    
                    # Calculate distances
                    distances = feature_processor.calculate_distances(normalized)
                    
                    # Calculate angles
                    angles = feature_processor.calculate_angles(normalized)
                    
                    print(f"\n--- Hand {i+1} ---")
                    print(f"Total features: {len(features)}")
                    print(f"Feature vector shape: {features.shape}")
                    print(f"Feature range: [{features.min():.3f}, {features.max():.3f}]")
                    print(f"\nDistances (first 5):")
                    for key, value in list(distances.items())[:5]:
                        print(f"  {key}: {value:.3f}")
                    print(f"\nAngles:")
                    for key, value in angles.items():
                        print(f"  {key}: {value:.1f}°")
            
            # Draw and show
            output_image = hand_detector.draw_landmarks(image_rgb, results)
            
            # Add info text
            cv2.putText(
                output_image,
                f"Hands: {len(landmarks)}",
                (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                (0, 255, 0),
                2
            )
            
            if landmarks:
                cv2.putText(
                    output_image,
                    f"Features: {len(features)}",
                    (10, 70),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.7,
                    (255, 255, 0),
                    2
                )
            
            cv2.imshow('Feature Extraction Test', output_image)
            
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
    
    except KeyboardInterrupt:
        print("\n⚠️ Interrupted")
    
    finally:
        cv2.destroyAllWindows()
        camera_manager.cleanup()
        hand_detector.cleanup()
        print("\n✅ Test completed!")

if __name__ == "__main__":
    print("🧮 Feature Processor Test")
    print("=" * 50)
    
    test_feature_extraction()
    
    print("\n" + "=" * 50)
    print("✅ All tests completed!")
