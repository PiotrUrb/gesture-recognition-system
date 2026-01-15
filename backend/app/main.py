from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import asyncio
import logging
import sys
import os
from datetime import datetime, timedelta


from app.core.config import settings
from app.core.database import init_db, async_session_maker
from app.core.init_data import init_default_gestures
from app.services.camera_manager import camera_manager


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


logger = logging.getLogger(__name__)


# ============================================================================
# IMPORTS - Gesture Detection Logging
# ============================================================================


try:
    from app.services.gesture_detection_logging import init_logging_service, get_logging_service
    HAS_LOGGING_SERVICE = True
except ImportError:
    HAS_LOGGING_SERVICE = False
    logger.warning("⚠️ gesture_detection_logging service not found")


# ============================================================================
# BACKGROUND TASKS
# ============================================================================


async def cleanup_old_logs():
    """Background task to clean up logs older than 7 days"""
    if not HAS_LOGGING_SERVICE:
        logger.warning("Cleanup task skipped - logging service not available")
        return
        
    while True:
        try:
            # Run cleanup every 24 hours
            await asyncio.sleep(86400)
            
            logging_service = get_logging_service()
            if logging_service:
                deleted = logging_service.clear_old_logs(days=7)
                logger.info(f"✅ Background cleanup: Deleted {deleted} logs older than 7 days")
        except asyncio.CancelledError:
            logger.info("Cleanup task cancelled")
            break
        except Exception as e:
            logger.error(f"❌ Background cleanup error: {e}")
            await asyncio.sleep(60)


# ============================================================================
# APP LIFECYCLE
# ============================================================================


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifecycle events"""
    logger.info("🚀 Starting Gesture Recognition System...")


    # Initialize database
    await init_db()
    logger.info("✅ Database initialized")


    # Initialize default gestures
    async with async_session_maker() as session:
        await init_default_gestures(session)


    # Initialize logging service
    cleanup_task = None
    if HAS_LOGGING_SERVICE:
        try:
            init_logging_service(database_url="sqlite:///./gesture_logs.db")
            logger.info("✅ Gesture logging service initialized")
            
            # Start background cleanup task
            cleanup_task = asyncio.create_task(cleanup_old_logs())
            logger.info("✅ Background cleanup task started")
        except Exception as e:
            logger.error(f"❌ Error initializing logging service: {e}")


    # Auto-start camera
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
    
    if cleanup_task:
        try:
            cleanup_task.cancel()
            await cleanup_task
        except asyncio.CancelledError:
            pass
        logger.info("✅ Cleanup task cancelled")
    
    logger.info("👋 Shutting down Gesture Recognition System...")


# ============================================================================
# APP SETUP
# ============================================================================


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Industrial Gesture Recognition System with Machine Learning",
    lifespan=lifespan
)


# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost",
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
        "*"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)


# ============================================================================
# ENDPOINTS
# ============================================================================


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


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        gesture_logs_count = 0
        if HAS_LOGGING_SERVICE:
            logging_service = get_logging_service()
            if logging_service:
                stats = logging_service.get_statistics()
                gesture_logs_count = stats.get("total", 0)
        
        return {
            "status": "healthy",
            "service": settings.PROJECT_NAME,
            "version": settings.VERSION,
            "timestamp": datetime.utcnow().isoformat(),
            "gesture_logs_count": gesture_logs_count,
            "checks": {
                "api": "ok",
                "database": "ok",
                "ml_model": "not_loaded"
            }
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "status": "unhealthy",
            "error": str(e)
        }


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


# ============================================================================
# INCLUDE ROUTERS
# ============================================================================


try:
    from app.api.routes import cameras
    app.include_router(cameras.router, prefix=settings.API_PREFIX)
    logger.info("✅ Cameras router included")
except Exception as e:
    logger.error(f"❌ Error including cameras router: {e}")


try:
    from app.api.routes import gestures
    app.include_router(gestures.router, prefix=settings.API_PREFIX)
    logger.info("✅ Gestures router included")
except Exception as e:
    logger.error(f"❌ Error including gestures router: {e}")


try:
    from app.api.routes import training
    app.include_router(training.router, prefix=settings.API_PREFIX)
    logger.info("✅ Training router included")
except Exception as e:
    logger.error(f"❌ Error including training router: {e}")


# Include gesture logs router
if HAS_LOGGING_SERVICE:
    try:
        from app.api.routes import gesture_logs
        app.include_router(gesture_logs.router, prefix=settings.API_PREFIX)
        logger.info("✅ Gesture logs router included")
    except Exception as e:
        logger.error(f"❌ Error including gesture logs router: {e}")


# ============================================================================
# NEW: Include system router (CONFIG ENDPOINT)
# ============================================================================

try:
    from app.api.routes import system
    app.include_router(system.router, prefix=settings.API_PREFIX)
    logger.info("✅ System router included")
except Exception as e:
    logger.error(f"❌ Error including system router: {e}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
