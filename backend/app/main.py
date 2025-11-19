"""
Main FastAPI application
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

from app.core.config import settings
from app.core.database import init_db, async_session_maker
from app.core.init_data import init_default_gestures

# Configure logging
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
    
    yield
    
    logger.info("👋 Shutting down Gesture Recognition System...")

# Create FastAPI app
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Industrial Gesture Recognition System with Machine Learning",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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
from app.api.routes import cameras, gestures

app.include_router(cameras.router, prefix=settings.API_PREFIX)
app.include_router(gestures.router, prefix=settings.API_PREFIX)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
