from sqlalchemy import Column, Integer, String, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base

class Site(Base):
    __tablename__ = "sites"

    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False)
    site_code = Column(String(20), nullable=False)
    site_name = Column(String(100), nullable=False)
    location = Column(Text)

    # Relationships
    customer = relationship("Customer", back_populates="sites")
    fleet_managers = relationship("FleetManager", back_populates="site")
    rentals = relationship("Rental", back_populates="site")
