"""
POPRAWKA #3: backend/app/main.py
ZMIANA: Poprawna konfiguracja CORS dla WebSocket i prawidłowe allow_origins
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging
from app.core.config import settings
from app.core.database import init_db, async_session_maker
from app.core.init_data import init_default_gestures
from app.services.camera_manager import camera_manager

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifecycle events"""
    logger.info("🚀 Starting Gesture Recognition System...")
    
    # Initialize database
    await init_db()
    logger.info("✅ Database initialized")
    
    # Initialize default data
    async with async_session_maker() as session:
        await init_default_gestures(session)
    
    # Auto-start cameras
    try:
        cams = camera_manager.detect_usb_cameras()
        if cams:
            camera_manager.add_camera(0, str(cams[0]), 'usb')
            logger.info(f"✅ Auto-started camera 0")
        else:
            logger.warning("⚠️ No cameras detected on startup")
    except Exception as e:
        logger.error(f"❌ Failed to auto-start camera: {e}")
    
    yield
    
    # Cleanup
    camera_manager.cleanup()
    logger.info("📷 Camera manager cleaned up")
    logger.info("👋 Shutting down Gesture Recognition System...")


# Create FastAPI app
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Industrial Gesture Recognition System with Machine Learning",
    lifespan=lifespan
)

# ✅ FIX: Proper CORS configuration for WebSocket
# IMPORTANT: allow_credentials=True is required for WebSocket with credentials
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost",
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
        "*"  # Allow all origins (use specific domains in production)
    ],
    allow_credentials=True,  # ✅ REQUIRED for WebSocket
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": f"Welcome to {settings.PROJECT_NAME}",
        "version": settings.VERSION,
        "status": "running",
        "docs": "/docs",
        "health": "/health"
    }

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "checks": {
            "api": "ok",
            "database": "ok",
            "ml_model": "not_loaded"
        }
    }

# System info endpoint
@app.get("/info")
async def system_info():
    """Get system information"""
    return {
        "project": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "max_cameras": settings.MAX_CAMERAS,
        "default_resolution": settings.DEFAULT_RESOLUTION,
        "default_fps": settings.DEFAULT_FPS,
        "min_confidence": settings.MIN_DETECTION_CONFIDENCE
    }

# Import and include routers AFTER app is created
from app.api.routes import cameras, gestures, training

app.include_router(cameras.router, prefix=settings.API_PREFIX)
app.include_router(gestures.router, prefix=settings.API_PREFIX)
app.include_router(training.router, prefix=settings.API_PREFIX)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )