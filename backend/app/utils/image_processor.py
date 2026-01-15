import cv2
import numpy as np
from pathlib import Path
import logging
from typing import List, Tuple, Optional, Dict
import json
from tqdm import tqdm

from app.services.hand_detector import hand_detector
from app.services.feature_processor import feature_processor



logger = logging.getLogger(__name__)

class ImageProcessor:
    
    # Gesture mappings for different datasets
    GESTURE_MAPPINGS = {
        'leap': {
            '00': 'palm',
            '01': 'fist',
            '02': 'thumb',
            '03': 'index',
            '04': 'ok',
            '05': 'palm_moved',
            '06': 'c_shape',
            '07': 'down',
            '08': 'l_shape',
            '09': 'fist_moved'
        },
        'isl': {
            '1': 'one_finger',
            '2': 'two_fingers',
            '3': 'three_fingers',
            '4': 'four_fingers',
            '5': 'five_fingers',
            '6': 'six',
            '7': 'seven',
            '8': 'eight',
            '9': 'nine',
            '0': 'zero'
        },
        'asl': {
            'A': 'fist',
            'B': 'four_fingers',
            'C': 'c_shape',
            'O': 'ok_sign',
            'nothing': 'no_gesture'
        },
        'senz3d': {
            'G1': 'gesture_1',
            'G2': 'gesture_2',
            'G3': 'gesture_3',
            'G4': 'gesture_4',
            'G5': 'gesture_5',
            'G6': 'gesture_6',
            'G7': 'gesture_7',
            'G8': 'gesture_8',
            'G9': 'gesture_9',
            'G10': 'gesture_10',
            'G11': 'gesture_11'
        }
    }
    
    def __init__(
        self,
        hand_detector,
        feature_processor,
        output_dir: str = './data/processed'
    ):
        """
        Initialize processor
        
        Args:
            hand_detector: HandDetector instance
            feature_processor: FeatureProcessor instance
            output_dir: Where to save processed data
        """
        self.hand_detector = hand_detector
        self.feature_processor = feature_processor
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info("ImageProcessor initialized")
    
    def get_gesture_name(self, folder_name: str, dataset_type: str = None) -> str:
        """
        Map folder name to gesture name based on dataset type
        
        Args:
            folder_name: Original folder name
            dataset_type: Dataset type (leap, isl, asl, etc.)
            
        Returns:
            Mapped gesture name or original folder name
        """
        if dataset_type and dataset_type in self.GESTURE_MAPPINGS:
            mapping = self.GESTURE_MAPPINGS[dataset_type]
            return mapping.get(folder_name, folder_name)
        return folder_name
    
    def process_image(
        self,
        image_path: str
    ) -> Optional[Tuple[np.ndarray, dict]]:
        """
        Process single image to features
        
        Args:
            image_path: Path to image
            
        Returns:
            Tuple of (features, metadata) or None if no hand detected
        """
        # Read image
        image = cv2.imread(str(image_path))
        if image is None:
            logger.warning(f"Failed to read: {image_path}")
            return None
        
        # Detect hand
        image_rgb, results = self.hand_detector.detect_hands(image)
        landmarks = self.hand_detector.extract_landmarks(results)
        
        if not landmarks:
            return None
        
        # Use first hand only
        hand_landmarks = landmarks[0]
        
        # Extract features
        try:
            features = self.feature_processor.extract_features(hand_landmarks)
            
            # Metadata
            metadata = {
                'image_path': str(image_path),
                'num_landmarks': len(hand_landmarks),
                'num_features': len(features)
            }
            
            return features, metadata
            
        except Exception as e:
            logger.error(f"Feature extraction failed for {image_path}: {e}")
            return None
    
    def process_folder(
        self,
        folder_path: str,
        gesture_name: str,
        recursive: bool = True,
        max_images: int = None
    ) -> dict:
        """
        Process all images in folder
        
        Args:
            folder_path: Path to folder with images
            gesture_name: Name of gesture (label)
            recursive: Search subfolders
            max_images: Limit number of images to process
            
        Returns:
            Dict with processing statistics
        """
        folder = Path(folder_path)
        
        # Find all images
        if recursive:
            image_files = list(folder.rglob('*.jpg')) + \
                         list(folder.rglob('*.png')) + \
                         list(folder.rglob('*.jpeg'))
        else:
            image_files = list(folder.glob('*.jpg')) + \
                         list(folder.glob('*.png')) + \
                         list(folder.glob('*.jpeg'))
        
        # Limit if specified
        if max_images and len(image_files) > max_images:
            import random
            image_files = random.sample(image_files, max_images)
        
        print(f"\n📂 Processing: {gesture_name}")
        print(f"   Found {len(image_files)} images")
        
        features_list = []
        metadata_list = []
        skipped = 0
        
        # Process each image
        for image_path in tqdm(image_files, desc=gesture_name):
            result = self.process_image(image_path)
            
            if result:
                features, metadata = result
                features_list.append(features)
                metadata_list.append(metadata)
            else:
                skipped += 1
        
        # Save processed data
        if features_list:
            output_file = self.output_dir / f"{gesture_name}.npz"
            
            np.savez_compressed(
                output_file,
                features=np.array(features_list),
                labels=np.array([gesture_name] * len(features_list)),
                metadata=metadata_list
            )
            
            print(f"   ✅ Processed: {len(features_list)} samples")
            print(f"   ⚠️  Skipped: {skipped} (no hand detected)")
            print(f"   💾 Saved to: {output_file}")
        
        return {
            'gesture': gesture_name,
            'total_images': len(image_files),
            'processed': len(features_list),
            'skipped': skipped,
            'output_file': str(output_file) if features_list else None
        }
    
    def process_dataset_structure(
        self,
        dataset_root: str,
        dataset_type: str = None,
        max_images_per_gesture: int = None
    ) -> List[dict]:
        """
        Process dataset with folder structure
        
        Args:
            dataset_root: Root directory of dataset
            dataset_type: Type (leap, isl, asl, senz3d, etc.)
            max_images_per_gesture: Limit images per gesture
            
        Returns:
            List of processing statistics for each gesture
        """
        root = Path(dataset_root)
        
        print("\n" + "="*60)
        print("🔄 PROCESSING DATASET")
        print("="*60)
        print(f"Dataset root: {root}")
        print(f"Dataset type: {dataset_type or 'auto'}")
        
        # Find all gesture folders
        gesture_folders = [d for d in root.iterdir() if d.is_dir()]
        
        # Special handling for Senz3D (nested structure)
        if dataset_type == 'senz3d':
            gesture_folders = []
            acquisitions = root / 'acquisitions'
            if acquisitions.exists():
                for subject_folder in acquisitions.iterdir():
                    if subject_folder.is_dir():
                        gesture_folders.extend([d for d in subject_folder.iterdir() if d.is_dir()])
        
        print(f"Found {len(gesture_folders)} gesture folders:")
        for folder in gesture_folders[:10]:  # Show first 10
            print(f"  - {folder.name}")
        if len(gesture_folders) > 10:
            print(f"  ... and {len(gesture_folders) - 10} more")
        
        # Process each gesture
        all_stats = []
        
        for gesture_folder in gesture_folders:
            original_name = gesture_folder.name
            gesture_name = self.get_gesture_name(original_name, dataset_type)
            
            stats = self.process_folder(
                folder_path=str(gesture_folder),
                gesture_name=gesture_name,
                recursive=True,
                max_images=max_images_per_gesture
            )
            all_stats.append(stats)
        
        # Summary
        print("\n" + "="*60)
        print("📊 PROCESSING SUMMARY")
        print("="*60)
        
        total_processed = sum(s['processed'] for s in all_stats)
        total_images = sum(s['total_images'] for s in all_stats)
        
        print(f"Total images: {total_images}")
        print(f"Successfully processed: {total_processed}")
        if total_images > 0:
            print(f"Success rate: {total_processed/total_images*100:.1f}%")
        
        print("\nPer-gesture breakdown:")
        for stats in all_stats:
            rate = stats['processed'] / stats['total_images'] * 100 if stats['total_images'] > 0 else 0
            print(f"  {stats['gesture']}: {stats['processed']}/{stats['total_images']} ({rate:.1f}%)")
        
        return all_stats
    
    def combine_processed_data(
        self,
        output_file: str = 'combined_dataset.npz'
    ) -> dict:
        """
        Combine all processed gesture files into one dataset
        
        Args:
            output_file: Name of combined output file
            
        Returns:
            Dataset statistics
        """
        print("\n" + "="*60)
        print("🔗 COMBINING PROCESSED DATA")
        print("="*60)
        
        # Find all .npz files
        processed_files = list(self.output_dir.glob('*.npz'))
        processed_files = [f for f in processed_files if f.name != output_file]
        
        if not processed_files:
            print("❌ No processed files found!")
            return {}
        
        print(f"Found {len(processed_files)} processed files")
        
        all_features = []
        all_labels = []
        
        for npz_file in processed_files:
            data = np.load(npz_file, allow_pickle=True)
            features = data['features']
            labels = data['labels']
            
            all_features.append(features)
            all_labels.extend(labels)
            
            print(f"  - {npz_file.name}: {len(features)} samples")
        
        # Combine
        combined_features = np.vstack(all_features)
        combined_labels = np.array(all_labels)
        
        # Save
        output_path = self.output_dir / output_file
        np.savez_compressed(
            output_path,
            features=combined_features,
            labels=combined_labels
        )
        
        print(f"\n✅ Combined dataset saved to: {output_path}")
        print(f"   Total samples: {len(combined_labels)}")
        print(f"   Feature shape: {combined_features.shape}")
        print(f"   Unique gestures: {len(set(combined_labels))}")
        
        # Show gesture distribution
        unique, counts = np.unique(combined_labels, return_counts=True)
        print(f"\n📊 Gesture Distribution:")
        for gesture, count in sorted(zip(unique, counts), key=lambda x: -x[1])[:10]:
            print(f"   {gesture}: {count} samples")
        
        return {
            'total_samples': len(combined_labels),
            'num_features': combined_features.shape[1],
            'num_gestures': len(set(combined_labels)),
            'gestures': list(set(combined_labels)),
            'output_file': str(output_path)
        }

image_processor = ImageProcessor(
    hand_detector=hand_detector,
    feature_processor=feature_processor,
    output_dir='./data/processed'
)

