from pydantic import BaseModel
from typing import Optional

class MachineBase(BaseModel):
    equipment_id: str
    equipment_type: str
    model: Optional[str] = None
    serial_number: Optional[str] = None
    status: str

class MachineCreate(MachineBase):
    dealer_id: int

class MachineResponse(MachineBase):
    dealer_id: int
    current_renter: Optional[str] = None

    class Config:
        from_attributes = True
