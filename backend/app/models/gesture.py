# backend/app/models/gesture.py

"""
Gesture database model
"""

from sqlalchemy import Column, Integer, String, Boolean, Float, DateTime
from sqlalchemy.sql import func

from app.core.database import Base


class Gesture(Base):
    """Gesture model"""

    __tablename__ = "gestures"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False, index=True)
    category = Column(String, nullable=False)
    description = Column(String)
    machine_action = Column(String)
    is_default = Column(Boolean, default=False)
    enabled = Column(Boolean, default=True)
    confidence_threshold = Column(Float, default=0.75)
    samples_count = Column(Integer, default=0)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def __repr__(self) -> str:
        return f"<Gesture {self.name}>"

    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return {
            "id": self.id,
            "name": self.name,
            "category": self.category,
            "description": self.description,
            "machine_action": self.machine_action,
            "is_default": self.is_default,
            "enabled": self.enabled,
            "confidence_threshold": self.confidence_threshold,
            "samples_count": self.samples_count,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
