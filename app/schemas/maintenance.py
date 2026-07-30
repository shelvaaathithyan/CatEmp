from pydantic import BaseModel
from datetime import date
from typing import Optional

class MaintenanceHistoryBase(BaseModel):
    equipment_id: str
    service_date: date
    service_type: Optional[str] = None
    remarks: Optional[str] = None

class MaintenanceHistoryCreate(MaintenanceHistoryBase):
    pass

class MaintenanceHistoryResponse(MaintenanceHistoryBase):
    id: int

    class Config:
        from_attributes = True
