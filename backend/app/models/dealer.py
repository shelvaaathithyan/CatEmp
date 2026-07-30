from sqlalchemy import Column, Integer, String, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base

class Dealer(Base):
    __tablename__ = "dealers"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    company_name = Column(String(150), nullable=False)
    address = Column(Text)

    # Relationships
    user = relationship("User", back_populates="dealer")
    machines = relationship("Machine", back_populates="dealer")
