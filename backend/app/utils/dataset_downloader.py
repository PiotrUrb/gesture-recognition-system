import requests
import zipfile
import os
from pathlib import Path
import logging
from tqdm import tqdm

logger = logging.getLogger(__name__)

class HaGRIDDownloader:
    
    # Subset URLs (using sample version for quick start)
    DATASET_URLS = {
        'call': 'https://github.com/hukenovs/hagrid/releases/download/v1.0/call.zip',
        'dislike': 'https://github.com/hukenovs/hagrid/releases/download/v1.0/dislike.zip',
        'fist': 'https://github.com/hukenovs/hagrid/releases/download/v1.0/fist.zip',
        'four': 'https://github.com/hukenovs/hagrid/releases/download/v1.0/four.zip',
        'like': 'https://github.com/hukenovs/hagrid/releases/download/v1.0/like.zip',
        'mute': 'https://github.com/hukenovs/hagrid/releases/download/v1.0/mute.zip',
        'ok': 'https://github.com/hukenovs/hagrid/releases/download/v1.0/ok.zip',
        'one': 'https://github.com/hukenovs/hagrid/releases/download/v1.0/one.zip',
        'palm': 'https://github.com/hukenovs/hagrid/releases/download/v1.0/palm.zip',
        'peace': 'https://github.com/hukenovs/hagrid/releases/download/v1.0/peace.zip',
        'peace_inverted': 'https://github.com/hukenovs/hagrid/releases/download/v1.0/peace_inverted.zip',
        'rock': 'https://github.com/hukenovs/hagrid/releases/download/v1.0/rock.zip',
        'stop': 'https://github.com/hukenovs/hagrid/releases/download/v1.0/stop.zip',
        'stop_inverted': 'https://github.com/hukenovs/hagrid/releases/download/v1.0/stop_inverted.zip',
        'three': 'https://github.com/hukenovs/hagrid/releases/download/v1.0/three.zip',
        'three2': 'https://github.com/hukenovs/hagrid/releases/download/v1.0/three2.zip',
        'two_up': 'https://github.com/hukenovs/hagrid/releases/download/v1.0/two_up.zip',
        'two_up_inverted': 'https://github.com/hukenovs/hagrid/releases/download/v1.0/two_up_inverted.zip',
    }
    
    # Map HaGRID gestures to our gesture names
    GESTURE_MAPPING = {
        'fist': 'fist',
        'palm': 'open_hand',
        'one': 'one_finger',
        'two_up': 'two_fingers',
        'three': 'three_fingers',
        'four': 'four_fingers',
        'palm': 'five_fingers',  # Open palm = 5 fingers
        'ok': 'ok_sign',
    }
    
    def __init__(self, data_dir: str = './data/hagrid'):
        """
        Initialize downloader
        
        Args:
            data_dir: Directory to store dataset
        """
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"HaGRID Downloader initialized: {self.data_dir}")
    
    def download_gesture(self, gesture_name: str) -> bool:
        """
        Download a specific gesture dataset
        
        Args:
            gesture_name: Name of gesture to download
            
        Returns:
            True if successful
        """
        if gesture_name not in self.DATASET_URLS:
            logger.error(f"Unknown gesture: {gesture_name}")
            return False
        
        url = self.DATASET_URLS[gesture_name]
        zip_path = self.data_dir / f"{gesture_name}.zip"
        extract_path = self.data_dir / gesture_name
        
        # Check if already downloaded
        if extract_path.exists():
            logger.info(f"✅ {gesture_name} already downloaded")
            return True
        
        try:
            logger.info(f"⬇️  Downloading {gesture_name}...")
            
            # Download with progress bar
            response = requests.get(url, stream=True)
            response.raise_for_status()
            
            total_size = int(response.headers.get('content-length', 0))
            
            with open(zip_path, 'wb') as f, tqdm(
                total=total_size,
                unit='B',
                unit_scale=True,
                desc=gesture_name
            ) as pbar:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
                    pbar.update(len(chunk))
            
            # Extract
            logger.info(f"📦 Extracting {gesture_name}...")
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(extract_path)
            
            # Remove zip file to save space
            zip_path.unlink()
            
            logger.info(f"✅ {gesture_name} downloaded and extracted")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error downloading {gesture_name}: {e}")
            return False
    
    def download_basic_gestures(self) -> dict:
        """
        Download basic gestures needed for our system
        
        Returns:
            Dict with download status for each gesture
        """
        # Gestures we need
        gestures_to_download = [
            'fist',
            'palm',
            'one',
            'two_up',
            'three',
            'four',
            'ok'
        ]
        
        results = {}
        
        print("\n" + "=" * 60)
        print("📥 DOWNLOADING HAGRID DATASET")
        print("=" * 60)
        print(f"\nGestures to download: {len(gestures_to_download)}")
        print("This may take 5-10 minutes depending on connection...\n")
        
        for gesture in gestures_to_download:
            success = self.download_gesture(gesture)
            results[gesture] = success
        
        # Summary
        successful = sum(results.values())
        print("\n" + "=" * 60)
        print("📊 DOWNLOAD SUMMARY")
        print("=" * 60)
        print(f"Successfully downloaded: {successful}/{len(gestures_to_download)}")
        
        for gesture, success in results.items():
            status = "✅" if success else "❌"
            print(f"  {status} {gesture}")
        
        return results
    
    def get_dataset_stats(self) -> dict:
        """
        Get statistics about downloaded dataset
        
        Returns:
            Dict with stats for each gesture
        """
        stats = {}
        
        for gesture in os.listdir(self.data_dir):
            gesture_path = self.data_dir / gesture
            if gesture_path.is_dir():
                # Count images
                image_count = len(list(gesture_path.glob('**/*.jpg'))) + \
                             len(list(gesture_path.glob('**/*.png')))
                stats[gesture] = image_count
        
        return stats

# Global instance
hagrid_downloader = HaGRIDDownloader()
