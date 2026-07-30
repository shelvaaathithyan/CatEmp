from pydantic import BaseModel

class OperatorBase(BaseModel):
    operator_id: str
    operator_name: str

class OperatorCreate(OperatorBase):
    customer_id: int

class OperatorResponse(OperatorBase):
    customer_id: int

    class Config:
        from_attributes = True
