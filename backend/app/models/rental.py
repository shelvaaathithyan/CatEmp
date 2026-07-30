from sqlalchemy import Column, Integer, String, Date, Numeric, TIMESTAMP, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.core.database import Base

class Rental(Base):
    __tablename__ = "rentals"

    id = Column(Integer, primary_key=True, index=True)
    equipment_id = Column(String(50), ForeignKey("machines.equipment_id"), nullable=False)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False)
    site_id = Column(Integer, ForeignKey("sites.id"), nullable=False)
    fleet_manager_id = Column(Integer, ForeignKey("fleet_managers.id"), nullable=False)

    check_in_date = Column(Date)
    expected_return_date = Column(Date)
    actual_return_date = Column(Date)

    rental_cost = Column(Numeric(10, 2))
    rental_status = Column(String(30)) # e.g. PENDING, ACTIVE, COMPLETED, CANCELLED

    created_at = Column(TIMESTAMP, default=lambda: datetime.now(timezone.utc))

    # Relationships
    machine = relationship("Machine", back_populates="rentals")
    customer = relationship("Customer", back_populates="rentals")
    site = relationship("Site", back_populates="rentals")
    fleet_manager = relationship("FleetManager", back_populates="rentals")
    
    site_transfers = relationship("SiteTransfer", back_populates="rental")
    checkin_checkouts = relationship("CheckinCheckout", back_populates="rental")
    equipment_usages = relationship("EquipmentUsage", back_populates="rental")
