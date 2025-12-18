# backend/scripts/improve_model_live.py

"""
Live Model Improvement Tool (Active Learning)
Test the model and instantly save 'hard examples' to improve accuracy.
"""
import sys
import os
import cv2
import joblib
import time
import numpy as np
from pathlib import Path

# Setup paths
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, backend_dir)

from app.services.camera_manager import CameraManager
from app.services.hand_detector import HandDetector
from app.services.feature_processor import FeatureProcessor

def load_model(model_dir='./models'):
    path = Path(model_dir)
    try:
        model = joblib.load(path / 'gesture_model.pkl')
        le = joblib.load(path / 'label_encoder.pkl')
        return model, le
    except Exception as e:
        print(f"❌ Error loading model: {e}")
        return None, None

def save_correction(frame, gesture_name, base_dir='./data/collected'):
    """Save the current frame as a training sample for the correct gesture"""
    save_dir = Path(base_dir) / gesture_name
    save_dir.mkdir(parents=True, exist_ok=True)
    
    timestamp = int(time.time() * 1000)
    filename = f"correction_{timestamp}.jpg"
    filepath = save_dir / filename
    
    cv2.imwrite(str(filepath), frame)
    print(f"✅ Saved correction for: [{gesture_name}] -> {filename}")

def main():
    print("\n" + "="*60)
    print("🧠 ACTIVE LEARNING TOOL")
    print("="*60)
    
    model, label_encoder = load_model()
    if not model:
        print("First run: python scripts/train_model.py")
        return

    camera = CameraManager()
    detector = HandDetector(max_num_hands=1, min_detection_confidence=0.7)
    processor = FeatureProcessor()
    
    # Get camera
    cams = camera.detect_usb_cameras()
    if not cams: return
    camera.add_camera(0, str(cams[0]), 'usb')
    
    # Mapowanie klawiszy do gestów (dla szybkiej korekty)
    # Dostosuj to do swoich nazw gestów!
    key_mapping = {
        ord('0'): 'fist',
        ord('1'): 'one_finger',
        ord('2'): 'two_fingers',
        ord('3'): 'three_fingers',
        ord('4'): 'four_fingers',
        ord('5'): 'five_fingers', # lub 'open_hand' zależnie jak nazwałeś
        ord('o'): 'ok_sign',
        ord('p'): 'open_hand'
    }
    
    print("\n🎮 CONTROLS:")
    print("  [q] - Quit")
    print("  CORRECTION KEYS (Press if model is wrong):")
    print("  [0] - Fist")
    print("  [1] - One Finger")
    print("  [2] - Two Fingers")
    print("  [3] - Three Fingers")
    print("  [4] - Four Fingers")
    print("  [5] - Five Fingers")
    print("  [p] - Open Hand (Palm)")
    print("  [o] - OK Sign")
    print("\n🚀 Starting...")

    last_pred_time = time.time()
    current_prediction = "None"
    confidence = 0.0

    try:
        while True:
            frame = camera.get_frame(0)
            if frame is None: break
            
            # Detection
            rgb, results = detector.detect_hands(frame)
            landmarks = detector.extract_landmarks(results)
            output_image = detector.draw_landmarks(rgb, results)
            
            # Prediction (every few ms to be stable)
            if landmarks and (time.time() - last_pred_time > 0.05):
                features = processor.extract_features(landmarks[0])
                features = features.reshape(1, -1)
                
                pred_idx = model.predict(features)[0]
                probs = model.predict_proba(features)[0]
                
                current_prediction = label_encoder.inverse_transform([pred_idx])[0]
                confidence = probs[pred_idx]
                last_pred_time = time.time()

            # UI Display
            color = (0, 255, 0) if confidence > 0.8 else (0, 165, 255) # Green or Orange
            if confidence < 0.5: color = (0, 0, 255) # Red
            
            cv2.putText(output_image, f"AI: {current_prediction}", (10, 50), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)
            cv2.putText(output_image, f"Conf: {confidence*100:.1f}%", (10, 90), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
            
            cv2.putText(output_image, "Press 0-5, o, p to correct", (10, 460), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200, 200, 200), 1)

            cv2.imshow('Active Learning Mode', output_image)
            
            # Handle Inputs
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
            
            # Check if key is in our mapping
            if key in key_mapping:
                correct_label = key_mapping[key]
                print(f"📝 Correction: Model saw '{current_prediction}', User said '{correct_label}'")
                # Save raw frame (without drawings) for retraining
                save_correction(frame, correct_label)
                
                # Visual feedback
                cv2.putText(output_image, "SAVED!", (300, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 3)
                cv2.imshow('Active Learning Mode', output_image)
                cv2.waitKey(200) # Brief pause to show saved status

    finally:
        cv2.destroyAllWindows()
        camera.cleanup()
        detector.cleanup()

if __name__ == "__main__":
    main()
