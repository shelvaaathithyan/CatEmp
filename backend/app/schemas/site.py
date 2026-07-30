from pydantic import BaseModel
from typing import Optional

class SiteBase(BaseModel):
    site_code: str
    site_name: str
    location: Optional[str] = None

class SiteCreate(SiteBase):
    customer_id: int

class SiteResponse(SiteBase):
    id: int
    customer_id: int

    class Config:
        from_attributes = True
