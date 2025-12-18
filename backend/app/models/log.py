# backend/app/models/log.py

from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy.sql import func
from app.core.database import Base

class ActionLog(Base):
    __tablename__ = "action_logs"

    id = Column(Integer, primary_key=True, index=True)
    gesture_name = Column(String, nullable=False)
    confidence = Column(Float, nullable=False)
    mode = Column(String, nullable=False) # standard, safe
    action_type = Column(String, default="trigger") 
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
