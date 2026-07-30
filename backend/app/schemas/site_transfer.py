from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class SiteTransferBase(BaseModel):
    rental_id: int
    equipment_id: str
    to_site_id: int
    remarks: Optional[str] = None

class SiteTransferCreate(SiteTransferBase):
    from_site_id: int
    transferred_by: int

class SiteTransferResponse(SiteTransferBase):
    id: int
    from_site_id: int
    transferred_by: int
    transfer_date: datetime

    class Config:
        from_attributes = True
