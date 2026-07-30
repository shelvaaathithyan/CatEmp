from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base

class FleetManager(Base):
    __tablename__ = "fleet_managers"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    site_id = Column(Integer, ForeignKey("sites.id"), nullable=False)

    # Relationships
    user = relationship("User", back_populates="fleet_manager")
    site = relationship("Site", back_populates="fleet_managers")
    rentals = relationship("Rental", back_populates="fleet_manager")
