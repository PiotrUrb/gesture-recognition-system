# backend/scripts/download_hagrid.py

"""
Script to download HaGRID dataset
Run this once to get training data
"""
import sys
import os

# Add backend to path
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, backend_dir)

from app.utils.dataset_downloader import HaGRIDDownloader

def main():
    print("\n🎯 HaGRID Dataset Download Script")
    print("=" * 60)
    print("\nThis script will download gesture images from HaGRID dataset.")
    print("Dataset info: https://github.com/hukenovs/hagrid")
    print("\n⚠️  Note: Total download size ~500MB - 1GB")
    print("Make sure you have stable internet connection!\n")
    
    response = input("Continue? (y/n): ").lower()
    
    if response != 'y':
        print("Download cancelled.")
        return
    
    # Initialize downloader
    downloader = HaGRIDDownloader(data_dir='./data/hagrid')
    
    # Download basic gestures
    results = downloader.download_basic_gestures()
    
    # Show statistics
    print("\n" + "=" * 60)
    print("📊 DATASET STATISTICS")
    print("=" * 60)
    
    stats = downloader.get_dataset_stats()
    total_images = 0
    
    for gesture, count in stats.items():
        print(f"  {gesture}: {count} images")
        total_images += count
    
    print(f"\nTotal images: {total_images}")
    print("\n✅ Dataset ready for processing!")
    print("Next step: Run process_hagrid_dataset.py")

if __name__ == "__main__":
    main()
