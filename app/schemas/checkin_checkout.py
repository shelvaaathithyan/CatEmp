from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class CheckinCheckoutBase(BaseModel):
    rental_id: int
    action: str
    remarks: Optional[str] = None

class CheckinCheckoutCreate(CheckinCheckoutBase):
    performed_by: int

class CheckinCheckoutResponse(CheckinCheckoutBase):
    id: int
    performed_by: int
    timestamp: datetime

    class Config:
        from_attributes = True
