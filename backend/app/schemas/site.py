from pydantic import BaseModel
from typing import Optional, List

class FleetManagerUser(BaseModel):
    name: str
    email: str
    phone: Optional[str] = None
    
    class Config:
        from_attributes = True

class FleetManagerSiteSchema(BaseModel):
    id: int
    user: FleetManagerUser

    class Config:
        from_attributes = True

class SiteBase(BaseModel):
    site_code: str
    site_name: str
    location: Optional[str] = None

class SiteCreate(SiteBase):
    customer_id: int

class SiteResponse(SiteBase):
    id: int
    customer_id: int
    fleet_managers: List[FleetManagerSiteSchema] = []

    class Config:
        from_attributes = True
