from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base

class Machine(Base):
    __tablename__ = "machines"

    equipment_id = Column(String(50), primary_key=True, index=True)
    dealer_id = Column(Integer, ForeignKey("dealers.id"), nullable=False)
    equipment_type = Column(String(50), nullable=False)
    model = Column(String(100))
    serial_number = Column(String(100))
    status = Column(String(30), nullable=False) # e.g. AVAILABLE, RENTED, MAINTENANCE

    # Relationships
    dealer = relationship("Dealer", back_populates="machines")
    rentals = relationship("Rental", back_populates="machine")
    maintenance_history = relationship("MaintenanceHistory", back_populates="machine")
    maintenance_predictions = relationship("MaintenancePrediction", back_populates="machine")
    utilization_predictions = relationship("UtilizationPrediction", back_populates="machine")
    notifications = relationship("Notification", back_populates="machine")
    anomaly_predictions = relationship("AnomalyPrediction", back_populates="machine")
