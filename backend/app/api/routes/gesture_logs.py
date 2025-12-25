"""
Gesture Detection API routes - with Database logging
"""

from fastapi import APIRouter, HTTPException, Query
from datetime import datetime
import logging
from app.services.gesture_detection_logging import get_logging_service

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/gesture-logs", tags=["gesture-logs"])

logging_service = get_logging_service()

@router.get("/recent")
async def get_recent_logs(limit: int = Query(50, ge=1, le=100)):
    """Get recent gesture detection logs from database"""
    try:
        logs = logging_service.get_recent_logs(limit=limit)
        return {
            "status": "success",
            "count": len(logs),
            "logs": logs
        }
    except Exception as e:
        logger.error(f"Error fetching recent gesture logs: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/all")
async def get_all_logs(
    limit: int = Query(50, ge=1, le=1000),
    offset: int = Query(0, ge=0)
):
    """Get all gesture detection logs with pagination from database"""
    try:
        result = logging_service.get_all_logs(limit=limit, offset=offset)
        return {
            "status": "success",
            "count": len(result["logs"]),
            "total": result["total"],
            "limit": limit,
            "offset": offset,
            "logs": result["logs"]
        }
    except Exception as e:
        logger.error(f"Error fetching gesture logs: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/stats")
async def get_stats():
    """Get gesture detection statistics"""
    try:
        stats = logging_service.get_statistics()
        return {
            "status": "success",
            "stats": stats
        }
    except Exception as e:
        logger.error(f"Error fetching stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/since/{timestamp}")
async def get_logs_since(timestamp: str):
    """Get logs since specific timestamp (ISO format)"""
    try:
        dt = datetime.fromisoformat(timestamp)
        logs = logging_service.get_logs_after_date(dt)
        return {
            "status": "success",
            "count": len(logs),
            "since": timestamp,
            "logs": logs
        }
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid timestamp format. Use ISO format (YYYY-MM-DDTHH:MM:SS)")
    except Exception as e:
        logger.error(f"Error fetching logs since: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/clear-old")
async def clear_old_logs(days: int = Query(7, ge=1)):
    """Clear logs older than N days"""
    try:
        deleted = logging_service.clear_old_logs(days=days)
        return {
            "status": "success",
            "message": f"Deleted {deleted} logs older than {days} days",
            "deleted_count": deleted
        }
    except Exception as e:
        logger.error(f"Error clearing old logs: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/clear-all")
async def clear_all_logs():
    """Clear ALL logs - CAREFUL!"""
    try:
        deleted = logging_service.clear_all_logs()
        return {
            "status": "success",
            "message": f"Deleted ALL {deleted} logs",
            "deleted_count": deleted
        }
    except Exception as e:
        logger.error(f"Error clearing all logs: {e}")
        raise HTTPException(status_code=500, detail=str(e))
