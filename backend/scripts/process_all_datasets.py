# backend/scripts/process_all_datasets.py

"""
Process all downloaded datasets in batch
Dopasowany do Twoich struktur
"""
import sys
import os
from pathlib import Path

backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, backend_dir)

from app.services.hand_detector import HandDetector
from app.services.feature_processor import FeatureProcessor
from app.utils.image_processor import ImageProcessor

def main():
    print("\n" + "="*60)
    print("🔄 BATCH DATASET PROCESSOR")
    print("="*60)
    
    # Define dataset locations with correct structure
    datasets = [
        # === TWOJE DANE ===
        {
            'name': '🖐️ Collected Data (Your hands)',
            'path': './data/collected',
            'type': 'collected',
            'enabled': True,
            'max_per_gesture': None,  # All
            'priority': 1
        },
        
        # === LEAP (Twój Kaggle) ===
        {
            'name': '📦 LeapGestRecog (Kaggle)',
            'path': './data/external/leap',
            'type': 'leap',  # Używa mappingu
            'enabled': False,
            'max_per_gesture': 2000,  # Limit dla szybszego przetwarzania
            'priority': 2
        },
        
        # === ASL ALPHABET ===
        {
            'name': '🔤 ASL Alphabet',
            'path': './data/external/asl_alphabet',
            'type': 'asl',
            'enabled': False,
            'max_per_gesture': 1000,  # Limit (87k to za dużo!)
            'priority': 3
        },
        
        # === EGOHANDS ===
        {
            'name': '👁️ EgoHands',
            'path': './data/external/egohands/_LABELLED_SAMPLES',
            'type': 'egohands',
            'enabled': False,  # Włącz jeśli chcesz
            'max_per_gesture': 500,
            'priority': 4
        },
        
        # === ISL ===
        {
            'name': '🇮🇳 ISL Indian Sign',
            'path': './data/external/isl',
            'type': 'isl',
            'enabled': False,  # Włącz jeśli chcesz
            'max_per_gesture': 100,
            'priority': 5
        },
        
        # === NUS HANDS ===
        {
            'name': '🎯 NUS Hand Posture',
            'path': './data/external/nus_hands',
            'type': 'nus',
            'enabled': False,
            'max_per_gesture': None,
            'priority': 6
        },
        
        # === SENZ3D ===
        {
            'name': '📹 Senz3D Gesture',
            'path': './data/external/senz3d',
            'type': 'senz3d',
            'enabled': False,
            'max_per_gesture': 200,
            'priority': 7
        }
    ]

    
    print("\nAvailable datasets:")
    for i, ds in enumerate(datasets, 1):
        path_obj = Path(ds['path'])
        exists = "✅" if path_obj.exists() else "❌"
        enabled = "ENABLED" if ds['enabled'] else "DISABLED"
        max_info = f"(max {ds['max_per_gesture']}/gesture)" if ds['max_per_gesture'] else "(all)"
        
        print(f"  {i}. {ds['name']}: {exists} {enabled} {max_info}")
        print(f"     Path: {ds['path']}")
        
        # Show folder count if exists
        if path_obj.exists():
            subfolders = [d for d in path_obj.iterdir() if d.is_dir()]
            print(f"     Folders: {len(subfolders)}")
    
    print("\n💡 Note:")
    print("  - ENABLED datasets will be processed")
    print("  - max_per_gesture limits samples (speeds up processing)")
    print("  - ASL has 87k images - limited to 1000/gesture!")
    
    response = input("\nProceed with enabled datasets? (y/n): ").lower()
    if response != 'y':
        print("Cancelled.")
        return
    
    # Initialize processors
    print("\n🔧 Initializing components...")
    hand_detector = HandDetector()
    feature_processor = FeatureProcessor()
    image_processor = ImageProcessor(
        hand_detector=hand_detector,
        feature_processor=feature_processor,
        output_dir='./data/processed'
    )
    print("✅ Ready\n")
    
    # Process each enabled dataset
    all_stats = []
    
    for dataset in datasets:
        if not dataset['enabled']:
            print(f"⏭️  Skipping {dataset['name']} (disabled)")
            continue
        
        path_obj = Path(dataset['path'])
        if not path_obj.exists():
            print(f"⚠️  Skipping {dataset['name']} (path not found: {dataset['path']})")
            continue
        
        print("\n" + "="*60)
        print(f"Processing: {dataset['name']}")
        print("="*60)
        
        stats = image_processor.process_dataset_structure(
            dataset_root=dataset['path'],
            dataset_type=dataset['type'],
            max_images_per_gesture=dataset['max_per_gesture']
        )
        all_stats.extend(stats)
    
    # Combine all processed data
    if all_stats:
        print("\n" + "="*60)
        print("🔗 COMBINING ALL DATASETS")
        print("="*60)
        
        combined_stats = image_processor.combine_processed_data(
            output_file='combined_all_datasets.npz'
        )
        
        print("\n✅ ALL DATASETS PROCESSED!")
        print("\n📊 Final Statistics:")
        print(f"   Total samples: {combined_stats['total_samples']}")
        print(f"   Features per sample: {combined_stats['num_features']}")
        print(f"   Unique gestures: {combined_stats['num_gestures']}")
        print(f"\n💾 Combined dataset: {combined_stats['output_file']}")
        print("\n🚀 Ready for training!")
        print("\nNext step: python scripts/train_model.py")
    else:
        print("\n⚠️  No datasets were processed.")
    
    # Cleanup
    hand_detector.cleanup()

if __name__ == "__main__":
    main()
