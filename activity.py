from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.base import Base

class Activity(Base):
    __tablename__ = "activities"

    id = Column(Integer, primary_key=True, index=True)
    event = Column(String, nullable=False)  # e.g., "user_created", "user_updated", "user_deleted", "session_created", "session_ended"
    username = Column(String, nullable=False)
    details = Column(String, nullable=True)  # Additional details about the event
    created_at = Column(DateTime, default=datetime.utcnow) 