from pydantic import BaseModel

class CustomerBase(BaseModel):
    company_name: str

class CustomerCreate(CustomerBase):
    user_id: int

class CustomerResponse(CustomerBase):
    id: int
    user_id: int

    class Config:
        from_attributes = True
