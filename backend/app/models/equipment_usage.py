from sqlalchemy import Column, Integer, String, Date, Numeric, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base

class EquipmentUsage(Base):
    __tablename__ = "equipment_usage"

    id = Column(Integer, primary_key=True, index=True)
    rental_id = Column(Integer, ForeignKey("rentals.id"), nullable=False)
    equipment_id = Column(String(50), ForeignKey("machines.equipment_id"), nullable=False)
    site_id = Column(Integer, ForeignKey("sites.id"), nullable=False)

    usage_date = Column(Date, nullable=False)

    engine_hours_per_day = Column(Numeric(10, 2))
    idle_hours_per_day = Column(Numeric(10, 2))
    rental_days = Column(Integer)

    last_operator_id = Column(String(20), ForeignKey("operators.operator_id"))

    # Relationships
    rental = relationship("Rental", back_populates="equipment_usages")
    site = relationship("Site")
    last_operator = relationship("Operator", back_populates="equipment_usages")
