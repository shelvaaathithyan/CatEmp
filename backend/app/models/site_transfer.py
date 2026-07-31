from sqlalchemy import Column, Integer, String, Text, TIMESTAMP, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.core.database import Base

class SiteTransfer(Base):
    __tablename__ = "site_transfers"

    id = Column(Integer, primary_key=True, index=True)
    rental_id = Column(Integer, ForeignKey("rentals.id"), nullable=False)
    equipment_id = Column(String(50), ForeignKey("machines.equipment_id"), nullable=False)

    from_site_id = Column(Integer, ForeignKey("sites.id"), nullable=False)
    to_site_id = Column(Integer, ForeignKey("sites.id"), nullable=False)

    transfer_date = Column(TIMESTAMP, default=lambda: datetime.now(timezone.utc))
    transferred_by = Column(Integer, ForeignKey("fleet_managers.id"), nullable=False)
    status = Column(String(50), default="PENDING")

    remarks = Column(Text)

    # Relationships
    rental = relationship("Rental", back_populates="site_transfers")
    from_site = relationship("Site", foreign_keys=[from_site_id])
    to_site = relationship("Site", foreign_keys=[to_site_id])
