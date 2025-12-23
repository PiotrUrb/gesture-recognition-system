"""
Gesture Recognizer Service - POPRAWIONA WERSJA
Loads trained model and performs inference
"""
import joblib
import numpy as np
import os
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

class GestureRecognizer:
    def __init__(self, model_dir=None):
        self.model = None
        self.label_encoder = None
        
        # ✅ POPRAWIONA ŚCIEŻKA - ZAWSZE SZUKA W backend/models
        if model_dir is None:
            # Znajdź backend folder relatywnie do tego pliku
            current_file = os.path.abspath(__file__)  # /backend/app/services/gesture_recognizer.py
            services_dir = os.path.dirname(current_file)  # /backend/app/services
            app_dir = os.path.dirname(services_dir)  # /backend/app
            backend_dir = os.path.dirname(app_dir)  # /backend
            model_dir = os.path.join(backend_dir, 'models')  # /backend/models
        
        self.model_dir = Path(model_dir)
        self.load_model()

    def load_model(self):
        """Load model from disk"""
        try:
            model_path = self.model_dir / 'gesture_model.pkl'
            encoder_path = self.model_dir / 'label_encoder.pkl'
            
            # ✅ DODANE LOGOWANIE
            logger.info(f"🔍 Looking for model at: {model_path.absolute()}")
            
            if not model_path.exists():
                logger.warning(f"❌ Model not found at {model_path}. Please train model first.")
                return
            
            if not encoder_path.exists():
                logger.warning(f"❌ Label encoder not found at {encoder_path}. Please train model first.")
                return
            
            self.model = joblib.load(model_path)
            self.label_encoder = joblib.load(encoder_path)
            
            logger.info(f"✅ ML Model loaded successfully from {model_path}")
            logger.info(f"   Classes: {len(self.label_encoder.classes_)}")
            
        except Exception as e:
            logger.error(f"❌ Failed to load model: {e}")

    def predict(self, features: np.ndarray):
        """
        Predict gesture from features
        Returns: (label, confidence)
        """
        if self.model is None or self.label_encoder is None:
            logger.warning("⚠️ Model not loaded! Returning default.")
            return "Model Not Loaded", 0.0

        try:
            # ✅ DODANE SPRAWDZENIE FORMATU
            if not isinstance(features, np.ndarray):
                logger.error(f"❌ Features must be numpy array, got {type(features)}")
                return "Invalid Input", 0.0
            
            if features.size == 0:
                logger.warning("⚠️ Empty features array")
                return "Empty Features", 0.0
            
            # Reshape for single sample
            if features.ndim == 1:
                features = features.reshape(1, -1)
            
            # ✅ DODANE LOGOWANIE
            logger.debug(f"Predicting with features shape: {features.shape}")
            
            # Predict
            prediction_idx = self.model.predict(features)[0]
            probabilities = self.model.predict_proba(features)[0]

            # Decode label
            label = self.label_encoder.inverse_transform([prediction_idx])[0]
            confidence = float(probabilities[prediction_idx])
            
            # ✅ DODANE LOGOWANIE WYNIKU
            logger.debug(f"🎯 Predicted: {label} (confidence: {confidence:.2f})")
            
            return label, confidence
            
        except Exception as e:
            logger.error(f"❌ Prediction error: {e}")
            return "Error", 0.0

# Global instance
gesture_recognizer = GestureRecognizer()