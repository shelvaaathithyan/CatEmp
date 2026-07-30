from pydantic import BaseModel
from datetime import date, datetime
from typing import Optional
from decimal import Decimal

class RentalBase(BaseModel):
    equipment_id: str
    customer_id: int
    site_id: int
    fleet_manager_id: int
    check_in_date: Optional[date] = None
    expected_return_date: Optional[date] = None
    rental_cost: Optional[Decimal] = None
    rental_status: str

class RentalCreate(RentalBase):
    pass

class RentalUpdate(BaseModel):
    rental_status: Optional[str] = None
    actual_return_date: Optional[date] = None
    site_id: Optional[int] = None

class RentalResponse(RentalBase):
    id: int
    actual_return_date: Optional[date] = None
    created_at: datetime

    class Config:
        from_attributes = True
