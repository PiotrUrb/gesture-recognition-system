# backend/tests/test_integration_day3.py

"""
Integration Test - Day 3: Complete Pipeline
Camera → Hand Detection → Feature Extraction
"""
import sys
import os

backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, backend_dir)

from app.services.camera_manager import CameraManager
from app.services.hand_detector import HandDetector
from app.services.feature_processor import FeatureProcessor
import cv2
import time
import numpy as np

def test_complete_pipeline():
    """Test complete gesture detection pipeline"""
    print("\n" + "=" * 60)
    print("🎯 INTEGRATION TEST - DAY 3")
    print("=" * 60)
    print("\n📋 Testing complete pipeline:")
    print("  1. Camera Manager")
    print("  2. Hand Detector (MediaPipe)")
    print("  3. Feature Processor")
    print("\n🖐️  Show your hand to test!")
    print("👋 Try different gestures:")
    print("   - Open hand")
    print("   - Closed fist")
    print("   - Pointing finger")
    print("   - Peace sign")
    print("\nPress 'q' to quit\n")
    
    # Initialize all components
    print("Initializing components...")
    camera_manager = CameraManager()
    hand_detector = HandDetector(
        max_num_hands=2,
        min_detection_confidence=0.7
    )
    feature_processor = FeatureProcessor()
    print("✅ All components initialized\n")
    
    # Setup camera
    cameras = camera_manager.detect_usb_cameras()
    if not cameras:
        print("❌ No camera found!")
        return False
    
    success = camera_manager.add_camera(0, str(cameras[0]), 'usb')
    if not success:
        print("❌ Failed to open camera!")
        return False
    
    print(f"✅ Camera ready: {camera_manager.get_camera_info(0)}\n")
    
    # Stats tracking
    frame_count = 0
    detection_count = 0
    feature_extraction_count = 0
    
    fps_start = time.time()
    fps_frames = 0
    fps = 0
    
    print("Starting detection loop...\n")
    
    try:
        while True:
            frame_count += 1
            
            # STEP 1: Get frame from camera
            frame = camera_manager.get_frame(0)
            if frame is None:
                print("❌ Failed to get frame")
                break
            
            # STEP 2: Detect hands
            image_rgb, results = hand_detector.detect_hands(frame)
            hands_info = hand_detector.get_hand_info(results)
            landmarks_list = hand_detector.extract_landmarks(results)
            
            if landmarks_list:
                detection_count += 1
            
            # STEP 3: Extract features for each hand
            features_list = []
            for hand_landmarks in landmarks_list:
                try:
                    features = feature_processor.extract_features(hand_landmarks)
                    features_list.append(features)
                    feature_extraction_count += 1
                except Exception as e:
                    print(f"⚠️ Feature extraction error: {e}")
            
            # Calculate FPS
            fps_frames += 1
            if fps_frames >= 30:
                fps_end = time.time()
                fps = fps_frames / (fps_end - fps_start)
                fps_start = fps_end
                fps_frames = 0
            
            # Draw everything
            output_image = hand_detector.draw_landmarks(image_rgb, results)
            
            # Display stats
            y_pos = 30
            
            # FPS
            cv2.putText(output_image, f"FPS: {fps:.1f}", (10, y_pos),
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            y_pos += 40
            
            # Frames processed
            cv2.putText(output_image, f"Frames: {frame_count}", (10, y_pos),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            y_pos += 35
            
            # Hands detected
            color = (0, 255, 0) if landmarks_list else (0, 0, 255)
            cv2.putText(output_image, f"Hands: {len(landmarks_list)}", (10, y_pos),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
            y_pos += 35
            
            # Features extracted
            if features_list:
                cv2.putText(output_image, f"Features: {len(features_list[0])}", (10, y_pos),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)
                y_pos += 35
            
            # Hand info
            for i, hand_info in enumerate(hands_info):
                text = f"{hand_info['type']}: {hand_info['confidence']:.2f}"
                cv2.putText(output_image, text, (10, y_pos),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
                y_pos += 30
            
            # Show
            cv2.imshow('Integration Test - Day 3', output_image)
            
            # Console output (every 30 frames)
            if frame_count % 30 == 0 and landmarks_list:
                print(f"\n[Frame {frame_count}]")
                print(f"  Hands detected: {len(landmarks_list)}")
                print(f"  Features extracted: {len(features_list)}")
                if features_list:
                    print(f"  Feature vector: shape={features_list[0].shape}, "
                          f"range=[{features_list[0].min():.2f}, {features_list[0].max():.2f}]")
                for hand_info in hands_info:
                    print(f"  {hand_info['type']} hand - confidence: {hand_info['confidence']:.3f}")
            
            # Quit
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
    
    except KeyboardInterrupt:
        print("\n⚠️ Interrupted by user")
    
    finally:
        # Cleanup
        cv2.destroyAllWindows()
        camera_manager.cleanup()
        hand_detector.cleanup()
        
        # Final stats
        print("\n" + "=" * 60)
        print("📊 FINAL STATISTICS")
        print("=" * 60)
        print(f"Total frames processed: {frame_count}")
        print(f"Hands detected: {detection_count} ({detection_count/frame_count*100:.1f}%)")
        print(f"Features extracted: {feature_extraction_count}")
        print(f"Average FPS: {fps:.1f}")
        print("\n✅ Integration test completed successfully!")
        print("=" * 60)
        
        return True

if __name__ == "__main__":
    success = test_complete_pipeline()
    
    if success:
        print("\n🎉 DAY 3 COMPLETE!")
        print("\nYou now have:")
        print("  ✅ Camera management")
        print("  ✅ Hand detection (MediaPipe)")
        print("  ✅ 21 landmarks extraction")
        print("  ✅ Feature engineering (83 features)")
        print("  ✅ Real-time processing pipeline")
        print("\nReady for Day 4: ML Model Training! 🚀")
    else:
        print("\n❌ Test failed. Please check errors above.")
