from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.repositories.operator import OperatorRepository
from app.schemas.operator import OperatorCreate
from app.models.operator import Operator
from app.models.customer import Customer

operator_repo = OperatorRepository(Operator)

def get_operators_for_customer(db: Session, user_id: int):
    # Get the customer profile
    customer = db.query(Customer).filter(Customer.user_id == user_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer profile not found")
    
    return operator_repo.get_by_customer(db, customer.id)

def create_operator(db: Session, user_id: int, operator_in: OperatorCreate):
    # Verify the customer is creating this for themselves
    customer = db.query(Customer).filter(Customer.user_id == user_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer profile not found")
        
    if operator_in.customer_id != customer.id:
        raise HTTPException(status_code=403, detail="Not authorized to create operators for another customer")
        
    # Check duplicate
    existing = operator_repo.get_by_operator_id(db, operator_in.operator_id)
    if existing:
        raise HTTPException(status_code=400, detail="Operator ID already exists")
        
    return operator_repo.create(db, obj_in=operator_in)
