# backend/scripts/process_images.py

"""
Process images from any source to training data
"""
import sys
import os

backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, backend_dir)

from app.services.hand_detector import HandDetector
from app.services.feature_processor import FeatureProcessor
from app.utils.image_processor import ImageProcessor

def main():
    print("\n" + "="*60)
    print("🔄 IMAGE PROCESSOR")
    print("="*60)
    
    print("\nThis script processes gesture images to training data.")
    print("\nSupported folder structures:")
    print("  Option A: dataset/gesture_name/*.jpg")
    print("  Option B: dataset/subfolder/gesture_name/*.jpg")
    
    print("\nWhat do you want to process?")
    print("  1. Collected data (./data/collected)")
    print("  2. Custom folder (specify path)")
    print("  3. Both")
    
    choice = input("\nChoice (1/2/3): ").strip()
    
    # Initialize
    print("\n🔧 Initializing components...")
    hand_detector = HandDetector()
    feature_processor = FeatureProcessor()
    image_processor = ImageProcessor(
        hand_detector=hand_detector,
        feature_processor=feature_processor,
        output_dir='./data/processed'
    )
    print("✅ Components ready\n")
    
    if choice == '1' or choice == '3':
        # Process collected data
        print("Processing collected data...")
        stats = image_processor.process_dataset_structure('./data/collected')
    
    if choice == '2' or choice == '3':
        # Process custom folder
        custom_path = input("\nEnter path to dataset folder: ").strip()
        if os.path.exists(custom_path):
            print(f"Processing {custom_path}...")
            stats = image_processor.process_dataset_structure(custom_path)
        else:
            print(f"❌ Path not found: {custom_path}")
    
    # Combine all processed data
    print("\n" + "="*60)
    combined_stats = image_processor.combine_processed_data()
    
    # Cleanup
    hand_detector.cleanup()
    
    print("\n✅ Processing complete!")
    print("Next step: python scripts/train_model.py")

if __name__ == "__main__":
    main()
