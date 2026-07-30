from sqlalchemy import Column, Integer, String, Text, Boolean, TIMESTAMP, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.core.database import Base

class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    equipment_id = Column(String(50), ForeignKey("machines.equipment_id"))
    notification_type = Column(String(30))
    title = Column(String(150), nullable=False)
    message = Column(Text)
    priority = Column(String(20))
    is_read = Column(Boolean, default=False)
    created_at = Column(TIMESTAMP, default=lambda: datetime.now(timezone.utc))

    # Relationships
    user = relationship("User", back_populates="notifications")
    machine = relationship("Machine", back_populates="notifications")
