from sqlalchemy import Column, Integer, String, Date, Numeric, TIMESTAMP, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base

class MaintenancePrediction(Base):
    __tablename__ = "maintenance_predictions"

    id = Column(Integer, primary_key=True, index=True)
    equipment_id = Column(String(50), ForeignKey("machines.equipment_id"), nullable=False)
    prediction_timestamp = Column(TIMESTAMP, nullable=False)
    maintenance_probability = Column(Numeric(5, 4))
    predicted_service_date = Column(Date)
    confidence = Column(Numeric(5, 4))

    # Relationships
    machine = relationship("Machine", back_populates="maintenance_predictions")

class UtilizationPrediction(Base):
    __tablename__ = "utilization_predictions"

    id = Column(Integer, primary_key=True, index=True)
    prediction_timestamp = Column(TIMESTAMP, nullable=False)
    equipment_id = Column(String(50), ForeignKey("machines.equipment_id"), nullable=False)
    utilization_score = Column(Numeric(5, 4))
    predicted_idle_hours = Column(Numeric(10, 2))
    status = Column(String(30))

    # Relationships
    machine = relationship("Machine", back_populates="utilization_predictions")

class DemandPrediction(Base):
    __tablename__ = "demand_predictions"

    id = Column(Integer, primary_key=True, index=True)
    prediction_timestamp = Column(TIMESTAMP, nullable=False)
    equipment_type = Column(String(50), nullable=False)
    site_id = Column(Integer, ForeignKey("sites.id"), nullable=False)
    prediction_period = Column(String(30))
    expected_demand = Column(Integer)

    # Relationships
    site = relationship("Site")
