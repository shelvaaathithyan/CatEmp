from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base

class Operator(Base):
    __tablename__ = "operators"

    operator_id = Column(String(20), primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False)
    operator_name = Column(String(100), nullable=False)

    # Relationships
    customer = relationship("Customer", back_populates="operators")
    equipment_usages = relationship("EquipmentUsage", back_populates="last_operator")
