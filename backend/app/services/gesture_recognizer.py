#   backend/app/services/gesture_recognizer.py

"""
Gesture Recognizer Service
Loads trained model and performs inference
"""
import joblib
import numpy as np
import os
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

class GestureRecognizer:
    def __init__(self, model_dir='./models'):
        self.model = None
        self.label_encoder = None
        self.model_dir = Path(model_dir)
        self.load_model()

    def load_model(self):
        """Load model from disk"""
        try:
            model_path = self.model_dir / 'gesture_model.pkl'
            encoder_path = self.model_dir / 'label_encoder.pkl'

            if not model_path.exists():
                logger.warning(f"Model not found at {model_path}. Please train model first.")
                return

            self.model = joblib.load(model_path)
            self.label_encoder = joblib.load(encoder_path)
            logger.info("✅ ML Model loaded successfully")
        except Exception as e:
            logger.error(f"❌ Failed to load model: {e}")

    def predict(self, features: np.ndarray):
        """
        Predict gesture from features
        Returns: (label, confidence)
        """
        if not self.model or not self.label_encoder:
            return "Model Not Loaded", 0.0

        try:
            # Reshape for single sample
            features = features.reshape(1, -1)
            
            # Predict
            prediction_idx = self.model.predict(features)[0]
            probabilities = self.model.predict_proba(features)[0]
            
            # Decode label
            label = self.label_encoder.inverse_transform([prediction_idx])[0]
            confidence = probabilities[prediction_idx]
            
            return label, float(confidence)
            
        except Exception as e:
            logger.error(f"Prediction error: {e}")
            return "Error", 0.0

# Global instance
gesture_recognizer = GestureRecognizer()
