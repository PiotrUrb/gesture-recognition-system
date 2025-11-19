"""
Test Camera Manager
"""
import sys
import os

# Add backend directory to Python path
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, backend_dir)

from app.services.camera_manager import CameraManager
import cv2

def test_camera_detection():
    """Test USB camera detection"""
    print("\n=== Test 1: Camera Detection ===")
    manager = CameraManager()
    
    cameras = manager.detect_usb_cameras()
    print(f"✅ Found {len(cameras)} USB cameras: {cameras}")
    
    return cameras

def test_add_camera(camera_index=0):
    """Test adding a camera"""
    print("\n=== Test 2: Add Camera ===")
    manager = CameraManager()
    
    success = manager.add_camera(
        camera_id=0,
        source=str(camera_index),
        camera_type='usb',
        resolution=(640, 480),
        fps=30
    )
    
    if success:
        print("✅ Camera added successfully")
        
        # Get camera info
        info = manager.get_camera_info(0)
        print(f"Camera info: {info}")
        
        # Get a frame
        frame = manager.get_frame(0)
        if frame is not None:
            print(f"✅ Frame captured: shape={frame.shape}")
            
            # Display frame (optional - comment out if no display)
            try:
                cv2.imshow('Test Frame', frame)
                cv2.waitKey(2000)  # Show for 2 seconds
                cv2.destroyAllWindows()
            except:
                print("⚠️ Cannot display frame (no GUI available)")
        else:
            print("❌ Failed to capture frame")
        
        # Cleanup
        manager.cleanup()
    else:
        print("❌ Failed to add camera")

def test_multiple_cameras():
    """Test multiple cameras"""
    print("\n=== Test 3: Multiple Cameras ===")
    manager = CameraManager()
    
    # Detect available cameras
    available = manager.detect_usb_cameras()
    
    if not available:
        print("⚠️ No cameras found")
        return
    
    # Add all available cameras
    for i, cam_index in enumerate(available):
        success = manager.add_camera(
            camera_id=i,
            source=str(cam_index),
            camera_type='usb'
        )
        print(f"Camera {i} (index {cam_index}): {'✅ Added' if success else '❌ Failed'}")
    
    # List all cameras
    cameras = manager.list_cameras()
    print(f"\n✅ Active cameras: {len(cameras)}")
    for cam in cameras:
        print(f"  - Camera {cam['id']}: {cam['resolution']}, {cam['fps']} FPS")
    
    # Cleanup
    manager.cleanup()

if __name__ == "__main__":
    print("🎥 Camera Manager Tests")
    print("=" * 50)
    
    # Test 1: Detection
    cameras = test_camera_detection()
    
    if cameras:
        # Test 2: Add single camera
        test_add_camera(cameras[0])
        
        # Test 3: Multiple cameras
        test_multiple_cameras()
    else:
        print("\n⚠️ No cameras detected. Tests skipped.")
        print("💡 This is OK - we'll work with simulation!")
    
    print("\n" + "=" * 50)
    print("✅ Tests completed!")
