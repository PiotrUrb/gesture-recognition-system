"""
System Status Model
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class SystemStatus(Base):
    """System status log"""
    __tablename__ = "system_status"

    id = Column(Integer, primary_key=True, index=True)
    status = Column(String, default="online")
    timestamp = Column(DateTime, default=datetime.utcnow)
    cpu_usage = Column(Float, default=0.0)
    memory_usage = Column(Float, default=0.0)
    uptime_seconds = Column(Integer, default=0)
    active_cameras = Column(Integer, default=0)
    error_message = Column(String, nullable=True)
    last_restart = Column(DateTime, nullable=True)

class SystemOperation(Base):
    """System operation log"""
    __tablename__ = "system_operations"

    id = Column(Integer, primary_key=True, index=True)
    operation = Column(String)
    status = Column(String)
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    progress = Column(Float, default=0.0)
    message = Column(String, nullable=True)