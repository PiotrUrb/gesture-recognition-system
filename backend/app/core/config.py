"""
Application configuration
"""
from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    """Application settings"""
    
    # API
    PROJECT_NAME: str = "Gesture Recognition System"
    VERSION: str = "1.0.0"
    API_PREFIX: str = "/api/v1"
    
    # Database
    DATABASE_URL: str = "sqlite+aiosqlite:///./gesture_recognition.db"
    
    # ML
    MODEL_PATH: str = "./data/models"
    DATASET_PATH: str = "./data/datasets"
    
    # Camera
    MAX_CAMERAS: int = 9
    DEFAULT_RESOLUTION: str = "640x480"
    DEFAULT_FPS: int = 30
    
    # Detection
    MIN_DETECTION_CONFIDENCE: float = 0.7
    MIN_TRACKING_CONFIDENCE: float = 0.5
    
    # CORS
    BACKEND_CORS_ORIGINS: list = ["*"]
    
    class Config:
        case_sensitive = True

settings = Settings()
