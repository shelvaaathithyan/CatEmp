from pydantic import BaseModel
from datetime import date
from typing import Optional
from decimal import Decimal

class EquipmentUsageBase(BaseModel):
    rental_id: int
    equipment_id: str
    site_id: int
    usage_date: date
    engine_hours_per_day: Decimal
    idle_hours_per_day: Decimal
    rental_days: int
    last_operator_id: Optional[str] = None

class EquipmentUsageCreate(EquipmentUsageBase):
    pass

class EquipmentUsageResponse(EquipmentUsageBase):
    id: int

    class Config:
        from_attributes = True
