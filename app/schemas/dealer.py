from pydantic import BaseModel
from typing import Optional

class DealerBase(BaseModel):
    company_name: str
    address: Optional[str] = None

class DealerCreate(DealerBase):
    user_id: int

class DealerResponse(DealerBase):
    id: int
    user_id: int

    class Config:
        from_attributes = True
