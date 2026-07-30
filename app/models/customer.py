from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base

class Customer(Base):
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    company_name = Column(String(150), nullable=False)

    # Relationships
    user = relationship("User", back_populates="customer")
    sites = relationship("Site", back_populates="customer")
    rentals = relationship("Rental", back_populates="customer")
    operators = relationship("Operator", back_populates="customer")
