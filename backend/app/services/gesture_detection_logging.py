"""
Gesture Detection Log Model - Database
"""

from datetime import datetime, timedelta
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, create_engine, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
import logging

logger = logging.getLogger(__name__)

Base = declarative_base()

class GestureDetectionLog(Base):
    """Model for gesture detection logs - stored in SQLite database"""
    __tablename__ = "gesture_detection_logs"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    gesture = Column(String(50), nullable=False)
    gesture_label = Column(String(100))
    confidence = Column(Float, default=0.0)
    hand_type = Column(String(20))
    mode = Column(String(50))
    success = Column(Boolean, default=True)
    message = Column(String(255))
    camera_id = Column(Integer)
    camera_name = Column(String(100))
    action_triggered = Column(String(100))
    progress = Column(Integer, default=0)

    def __repr__(self):
        return f"<GestureDetectionLog {self.gesture} {self.confidence:.2f}>"

    def to_dict(self):
        return {
            "id": self.id,
            "timestamp": self.timestamp.isoformat(),
            "gesture": self.gesture,
            "gesture_label": self.gesture_label,
            "confidence": self.confidence,
            "hand_type": self.hand_type,
            "mode": self.mode,
            "success": self.success,
            "message": self.message,
            "camera_id": self.camera_id,
            "camera_name": self.camera_name,
            "action_triggered": self.action_triggered,
            "progress": self.progress,
        }


class LoggingService:
    """Service for managing gesture detection logs"""
    
    def __init__(self, database_url: str = "sqlite:///./gesture_logs.db"):
        self.engine = create_engine(
            database_url,
            connect_args={"check_same_thread": False} if "sqlite" in database_url else {}
        )
        Base.metadata.create_all(bind=self.engine)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        logger.info(f"✅ Logging service initialized with database: {database_url}")

    def get_db(self) -> Session:
        return self.SessionLocal()

    def log_gesture(
        self,
        gesture: str,
        confidence: float,
        hand_type: str,
        mode: str,
        success: bool = True,
        message: str = "",
        camera_id: int = 0,
        camera_name: str = "Unknown",
        action_triggered: str = None,
        progress: int = 0,
        gesture_label: str = None,
    ):
        try:
            db = self.get_db()
            log_entry = GestureDetectionLog(
                gesture=gesture,
                gesture_label=gesture_label or gesture,
                confidence=confidence,
                hand_type=hand_type,
                mode=mode,
                success=success,
                message=message,
                camera_id=camera_id,
                camera_name=camera_name,
                action_triggered=action_triggered,
                progress=progress,
            )
            db.add(log_entry)
            db.commit()
            db.refresh(log_entry)
            logger.debug(f"📝 Logged gesture: {gesture} ({confidence:.2f})")
            return log_entry
        except Exception as e:
            logger.error(f"❌ Error logging gesture: {e}")
            db.rollback()
            return None
        finally:
            db.close()

    def get_recent_logs(self, limit: int = 50) -> list:
        try:
            db = self.get_db()
            logs = (
                db.query(GestureDetectionLog)
                .order_by(GestureDetectionLog.timestamp.desc())
                .limit(limit)
                .all()
            )
            result = [log.to_dict() for log in logs]
            return result
        except Exception as e:
            logger.error(f"❌ Error fetching recent logs: {e}")
            return []
        finally:
            db.close()

    def get_all_logs(self, limit: int = 100, offset: int = 0) -> dict:
        try:
            db = self.get_db()
            total = db.query(GestureDetectionLog).count()
            logs = (
                db.query(GestureDetectionLog)
                .order_by(GestureDetectionLog.timestamp.desc())
                .limit(limit)
                .offset(offset)
                .all()
            )
            return {
                "logs": [log.to_dict() for log in logs],
                "total": total,
                "limit": limit,
                "offset": offset,
            }
        except Exception as e:
            logger.error(f"❌ Error fetching all logs: {e}")
            return {"logs": [], "total": 0, "limit": limit, "offset": offset}
        finally:
            db.close()

    def get_statistics(self) -> dict:
        try:
            db = self.get_db()
            total = db.query(GestureDetectionLog).count()
            successful = db.query(GestureDetectionLog).filter(GestureDetectionLog.success == True).count()
            
            top_gesture = db.query(
                GestureDetectionLog.gesture,
                func.count(GestureDetectionLog.id).label("count")
            ).group_by(GestureDetectionLog.gesture).order_by(func.count(GestureDetectionLog.id).desc()).first()
            
            avg_conf_result = db.query(func.avg(GestureDetectionLog.confidence)).scalar()
            avg_confidence = float(avg_conf_result) if avg_conf_result else 0.0

            success_rate = (successful / total * 100) if total > 0 else 0.0

            return {
                "total": total,
                "successful": successful,
                "success_rate": success_rate / 100,
                "top_gesture": top_gesture[0] if top_gesture else "N/A",
                "avg_confidence": avg_confidence,
            }
        except Exception as e:
            logger.error(f"❌ Error fetching statistics: {e}")
            return {
                "total": 0,
                "successful": 0,
                "success_rate": 0.0,
                "top_gesture": "N/A",
                "avg_confidence": 0.0,
            }
        finally:
            db.close()

    def clear_old_logs(self, days: int = 7) -> int:
        try:
            db = self.get_db()
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            deleted = db.query(GestureDetectionLog).filter(
                GestureDetectionLog.timestamp < cutoff_date
            ).delete()
            db.commit()
            logger.info(f"🗑️ Deleted {deleted} logs older than {days} days")
            return deleted
        except Exception as e:
            logger.error(f"❌ Error clearing old logs: {e}")
            db.rollback()
            return 0
        finally:
            db.close()

    def clear_all_logs(self) -> int:
        try:
            db = self.get_db()
            deleted = db.query(GestureDetectionLog).delete()
            db.commit()
            logger.info(f"🗑️ Deleted ALL {deleted} logs")
            return deleted
        except Exception as e:
            logger.error(f"❌ Error clearing all logs: {e}")
            db.rollback()
            return 0
        finally:
            db.close()

    def get_logs_after_date(self, timestamp: datetime) -> list:
        try:
            db = self.get_db()
            logs = (
                db.query(GestureDetectionLog)
                .filter(GestureDetectionLog.timestamp > timestamp)
                .order_by(GestureDetectionLog.timestamp.desc())
                .all()
            )
            return [log.to_dict() for log in logs]
        except Exception as e:
            logger.error(f"❌ Error fetching logs after date: {e}")
            return []
        finally:
            db.close()


logging_service: LoggingService = None

def init_logging_service(database_url: str = "sqlite:///./gesture_logs.db"):
    global logging_service
    logging_service = LoggingService(database_url)
    return logging_service

def get_logging_service() -> LoggingService:
    global logging_service
    if logging_service is None:
        logging_service = LoggingService()
    return logging_service
