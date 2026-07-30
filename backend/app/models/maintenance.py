from sqlalchemy import Column, Integer, String, Date, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base

class MaintenanceHistory(Base):
    __tablename__ = "maintenance_history"

    id = Column(Integer, primary_key=True, index=True)
    equipment_id = Column(String(50), ForeignKey("machines.equipment_id"), nullable=False)
    service_date = Column(Date, nullable=False)
    service_type = Column(String(100))
    remarks = Column(Text)

    # Relationships
    machine = relationship("Machine", back_populates="maintenance_history")
