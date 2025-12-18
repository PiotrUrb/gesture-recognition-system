# backend/scripts/test_model_live.py

"""
Test trained model with live camera
"""
import sys
import os
import numpy as np
import cv2
import joblib
from pathlib import Path
import time

backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, backend_dir)

from app.services.camera_manager import CameraManager
from app.services.hand_detector import HandDetector
from app.services.feature_processor import FeatureProcessor

def load_model(model_dir='./models'):
    """Load trained model"""
    print("📦 Loading model...")
    
    model_path = Path(model_dir)
    
    model = joblib.load(model_path / 'gesture_model.pkl')
    label_encoder = joblib.load(model_path / 'label_encoder.pkl')
    
    print(f"✅ Model loaded!")
    print(f"   Classes: {len(label_encoder.classes_)}")
    
    return model, label_encoder

def predict_gesture(features, model, label_encoder):
    """Predict gesture from features"""
    # Reshape for single prediction
    features_reshaped = features.reshape(1, -1)
    
    # Predict
    prediction = model.predict(features_reshaped)[0]
    probabilities = model.predict_proba(features_reshaped)[0]
    
    # Get gesture name and confidence
    gesture_name = label_encoder.inverse_transform([prediction])[0]
    confidence = probabilities[prediction]
    
    return gesture_name, confidence

def main():
    print("\n" + "="*60)
    print("🎥 LIVE GESTURE RECOGNITION TEST")
    print("="*60)
    
    # Load model
    model, label_encoder = load_model()
    
    # Initialize components
    print("\n🔧 Initializing components...")
    camera_manager = CameraManager()
    hand_detector = HandDetector(max_num_hands=1)
    feature_processor = FeatureProcessor()
    
    # Setup camera
    cameras = camera_manager.detect_usb_cameras()
    if not cameras:
        print("❌ No camera found!")
        return
    
    camera_manager.add_camera(0, str(cameras[0]), 'usb')
    print("✅ Camera ready!")
    
    print("\n" + "="*60)
    print("👋 Show gestures to camera!")
    print("Press 'q' to quit")
    print("="*60 + "\n")
    
    # FPS tracking
    fps_start = time.time()
    fps_frames = 0
    fps = 0
    
    # Prediction smoothing
    last_predictions = []
    smooth_window = 5
    
    try:
        while True:
            # Get frame
            frame = camera_manager.get_frame(0)
            if frame is None:
                break
            
            # Detect hand
            image_rgb, results = hand_detector.detect_hands(frame)
            landmarks = hand_detector.extract_landmarks(results)
            
            # Draw landmarks
            output_image = hand_detector.draw_landmarks(image_rgb, results)
            
            # Predict if hand detected
            gesture_text = "No hand detected"
            confidence_text = ""
            text_color = (0, 0, 255)  # Red
            
            if landmarks:
                try:
                    # Extract features
                    features = feature_processor.extract_features(landmarks[0])
                    
                    # Predict
                    gesture_name, confidence = predict_gesture(
                        features, model, label_encoder
                    )
                    
                    # Smoothing
                    last_predictions.append((gesture_name, confidence))
                    if len(last_predictions) > smooth_window:
                        last_predictions.pop(0)
                    
                    # Get most common prediction
                    if len(last_predictions) >= 3:
                        gestures = [p[0] for p in last_predictions]
                        from collections import Counter
                        most_common = Counter(gestures).most_common(1)[0][0]
                        avg_confidence = np.mean([p[1] for p in last_predictions if p[0] == most_common])
                        
                        gesture_name = most_common
                        confidence = avg_confidence
                    
                    gesture_text = f"Gesture: {gesture_name}"
                    confidence_text = f"Confidence: {confidence*100:.1f}%"
                    text_color = (0, 255, 0) if confidence > 0.7 else (0, 255, 255)
                    
                except Exception as e:
                    gesture_text = f"Error: {e}"
            
            # Calculate FPS
            fps_frames += 1
            if fps_frames >= 30:
                fps_end = time.time()
                fps = fps_frames / (fps_end - fps_start)
                fps_start = fps_end
                fps_frames = 0
            
            # Display info
            cv2.putText(output_image, f"FPS: {fps:.1f}", (10, 30),
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
            
            cv2.putText(output_image, gesture_text, (10, 80),
                       cv2.FONT_HERSHEY_SIMPLEX, 1.2, text_color, 3)
            
            if confidence_text:
                cv2.putText(output_image, confidence_text, (10, 130),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.8, text_color, 2)
            
            # Show
            cv2.imshow('Live Gesture Recognition', output_image)
            
            # Quit on 'q'
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
    
    except KeyboardInterrupt:
        print("\n⚠️ Interrupted")
    
    finally:
        cv2.destroyAllWindows()
        camera_manager.cleanup()
        hand_detector.cleanup()
        print("\n✅ Test complete!")

if __name__ == "__main__":
    main()
