# backend/tests/test_hand_detector.py

"""
Test Hand Detector
"""
import sys
import os

# Add backend directory to Python path
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, backend_dir)

from app.services.hand_detector import HandDetector
from app.services.camera_manager import CameraManager
import cv2
import time

def test_hand_detection_on_camera():
    """Test hand detection on live camera feed"""
    print("\n=== Test: Hand Detection on Camera ===")
    print("Show your hand to the camera!")
    print("Press 'q' to quit\n")
    
    # Initialize
    camera_manager = CameraManager()
    hand_detector = HandDetector(
        max_num_hands=2,
        min_detection_confidence=0.7
    )
    
    # Detect and add camera
    cameras = camera_manager.detect_usb_cameras()
    if not cameras:
        print("❌ No camera found!")
        return
    
    success = camera_manager.add_camera(
        camera_id=0,
        source=str(cameras[0]),
        camera_type='usb'
    )
    
    if not success:
        print("❌ Failed to open camera!")
        return
    
    print(f"✅ Camera opened: {camera_manager.get_camera_info(0)}\n")
    
    # FPS calculation
    fps_start_time = time.time()
    fps_frame_count = 0
    fps = 0
    
    try:
        while True:
            # Get frame
            frame = camera_manager.get_frame(0)
            if frame is None:
                print("❌ Failed to get frame")
                break
            
            # Detect hands
            image_rgb, results = hand_detector.detect_hands(frame)
            
            # Extract info
            hands_info = hand_detector.get_hand_info(results)
            landmarks = hand_detector.extract_landmarks(results)
            
            # Draw landmarks
            output_image = hand_detector.draw_landmarks(
                image_rgb,
                results,
                draw_connections=True
            )
            
            # Calculate FPS
            fps_frame_count += 1
            if fps_frame_count >= 10:
                fps_end_time = time.time()
                fps = fps_frame_count / (fps_end_time - fps_start_time)
                fps_start_time = fps_end_time
                fps_frame_count = 0
            
            # Display info on image
            cv2.putText(
                output_image,
                f"FPS: {fps:.1f}",
                (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                (0, 255, 0),
                2
            )
            
            cv2.putText(
                output_image,
                f"Hands detected: {len(hands_info)}",
                (10, 70),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                (0, 255, 0),
                2
            )
            
            # Display hand info
            y_offset = 110
            for hand_info in hands_info:
                text = f"{hand_info['type']} hand: {hand_info['confidence']:.2f}"
                cv2.putText(
                    output_image,
                    text,
                    (10, y_offset),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.7,
                    (255, 255, 0),
                    2
                )
                y_offset += 40
            
            # Show image
            cv2.imshow('Hand Detection Test', output_image)
            
            # Print to console
            if len(hands_info) > 0:
                print(f"Detected {len(hands_info)} hand(s): {hands_info}")
                print(f"Landmarks: {len(landmarks)} hands, "
                      f"{len(landmarks[0]) if landmarks else 0} points each")
            
            # Quit on 'q'
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
    
    except KeyboardInterrupt:
        print("\n⚠️ Interrupted by user")
    
    finally:
        # Cleanup
        cv2.destroyAllWindows()
        camera_manager.cleanup()
        hand_detector.cleanup()
        print("\n✅ Test completed!")

if __name__ == "__main__":
    print("🖐️ Hand Detection Test")
    print("=" * 50)
    
    test_hand_detection_on_camera()
    
    print("\n" + "=" * 50)
    print("✅ All tests completed!")
