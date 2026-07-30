from sqlalchemy import Column, Integer, String, Text, TIMESTAMP, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.core.database import Base

class CheckinCheckout(Base):
    __tablename__ = "checkin_checkout"

    id = Column(Integer, primary_key=True, index=True)
    rental_id = Column(Integer, ForeignKey("rentals.id"), nullable=False)
    performed_by = Column(Integer, ForeignKey("fleet_managers.id"), nullable=False)
    action = Column(String(20), nullable=False) # e.g. CHECK-IN, CHECK-OUT
    timestamp = Column(TIMESTAMP, default=lambda: datetime.now(timezone.utc))
    remarks = Column(Text)

    # Relationships
    rental = relationship("Rental", back_populates="checkin_checkouts")
    fleet_manager = relationship("FleetManager")
