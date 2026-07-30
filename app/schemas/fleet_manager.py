from pydantic import BaseModel

class FleetManagerBase(BaseModel):
    site_id: int

class FleetManagerCreate(FleetManagerBase):
    user_id: int

class FleetManagerResponse(FleetManagerBase):
    id: int
    user_id: int

    class Config:
        from_attributes = True
