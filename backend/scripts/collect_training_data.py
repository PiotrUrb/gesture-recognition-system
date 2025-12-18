# backend/scripts/collect_training_data.py

"""
Collect training data from camera
"""
import sys
import os

backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, backend_dir)

from app.services.camera_manager import CameraManager
from app.services.hand_detector import HandDetector
from app.utils.data_collector import DataCollector

def main():
    print("\n" + "="*60)
    print("📸 TRAINING DATA COLLECTION")
    print("="*60)
    
    # Gestures to collect
    gestures = [
        ('fist', 'Closed fist'),
        ('open_hand', 'Open palm, fingers spread'),
        ('one_finger', 'Index finger pointing up'),
        ('two_fingers', 'Peace sign (index + middle)'),
        ('three_fingers', 'Three fingers up'),
        ('four_fingers', 'Four fingers up'),
        ('five_fingers', 'All five fingers spread'),
        ('ok_sign', 'OK sign (thumb + index circle)'),
    ]
    
    print("\nWe will collect data for these gestures:")
    for i, (name, desc) in enumerate(gestures, 1):
        print(f"  {i}. {name}: {desc}")
    
    print("\nFor each gesture:")
    print("  - 50 samples will be collected")
    print("  - Show the gesture clearly to camera")
    print("  - Press SPACE to capture each sample")
    print("  - Press 'q' to skip to next gesture")
    
    response = input("\nReady to start? (y/n): ").lower()
    if response != 'y':
        print("Collection cancelled.")
        return
    
    # Initialize
    print("\n🔧 Initializing components...")
    camera_manager = CameraManager()
    hand_detector = HandDetector(max_num_hands=1)
    data_collector = DataCollector(output_dir='./data/collected')
    
    # Setup camera
    cameras = camera_manager.detect_usb_cameras()
    if not cameras:
        print("❌ No camera found!")
        return
    
    camera_manager.add_camera(0, str(cameras[0]), 'usb')
    print("✅ Camera ready\n")
    
    # Collect data for each gesture
    all_stats = []
    
    for i, (gesture_name, description) in enumerate(gestures, 1):
        print(f"\n{'='*60}")
        print(f"GESTURE {i}/{len(gestures)}: {gesture_name}")
        print(f"Description: {description}")
        print(f"{'='*60}")
        
        input("\nPress ENTER when ready to collect this gesture...")
        
        stats = data_collector.collect_gesture_data(
            gesture_name=gesture_name,
            num_samples=50,
            camera_manager=camera_manager,
            hand_detector=hand_detector
        )
        
        all_stats.append(stats)
        
        if i < len(gestures):
            print("\n⏭️  Moving to next gesture in 3 seconds...")
            import time
            time.sleep(3)
    
    # Cleanup
    camera_manager.cleanup()
    hand_detector.cleanup()
    
    # Final summary
    print("\n" + "="*60)
    print("🎉 DATA COLLECTION COMPLETE!")
    print("="*60)
    
    total_collected = sum(s['collected'] for s in all_stats)
    total_target = sum(s['target'] for s in all_stats)
    
    print(f"\nTotal collected: {total_collected}/{total_target} samples")
    print("\nPer-gesture breakdown:")
    
    for stats in all_stats:
        completion = stats['completion']
        status = "✅" if completion >= 80 else "⚠️"
        print(f"  {status} {stats['gesture']}: {stats['collected']}/{stats['target']} ({completion:.1f}%)")
    
    print(f"\n📁 Data saved to: ./data/collected/")
    print("\n✅ Ready for model training!")
    print("Next step: python scripts/train_model.py")

if __name__ == "__main__":
    main()
