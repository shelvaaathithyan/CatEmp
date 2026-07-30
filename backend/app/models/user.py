from sqlalchemy import Column, Integer, String, Text, TIMESTAMP, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.core.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    role = Column(String(30), nullable=False)
    name = Column(String(100), nullable=False)
    email = Column(String(150), unique=True, index=True, nullable=False)
    password_hash = Column(Text, nullable=False)
    phone = Column(String(20))
    created_at = Column(TIMESTAMP, default=lambda: datetime.now(timezone.utc))

    # Relationships
    dealer = relationship("Dealer", back_populates="user", uselist=False)
    customer = relationship("Customer", back_populates="user", uselist=False)
    fleet_manager = relationship("FleetManager", back_populates="user", uselist=False)
    notifications = relationship("Notification", back_populates="user")
