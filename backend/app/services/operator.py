from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.repositories.operator import OperatorRepository
from app.schemas.operator import OperatorCreate
from app.models.operator import Operator
from app.models.customer import Customer

operator_repo = OperatorRepository(Operator)

def get_operators_for_user(db: Session, user):
    if user.role == "Fleet Manager":
        # Fleet Managers can view all operators across their site (simplified to all for now)
        return operator_repo.get_multi(db)
    
    # Customer logic
    customer = db.query(Customer).filter(Customer.user_id == user.id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer profile not found")
    return operator_repo.get_by_customer(db, customer.id)

def create_operator(db: Session, current_user, operator_in: OperatorCreate):
    # CatAdmin can create for any customer
    if current_user.role == "CatAdmin":
        pass
    elif current_user.role == "Customer":
        # Customer can only create operators for themselves
        customer = db.query(Customer).filter(Customer.user_id == current_user.id).first()
        if not customer:
            raise HTTPException(status_code=404, detail="Customer profile not found")
        if operator_in.customer_id != customer.id:
            raise HTTPException(status_code=403, detail="Not authorized to create operators for another customer")
    elif current_user.role == "Fleet Manager":
        # Fleet Managers can create operators for the customers whose rentals they manage
        pass
    else:
        raise HTTPException(status_code=403, detail="Not authorized to create operators")
        
    # Check duplicate
    existing = operator_repo.get_by_operator_id(db, operator_in.operator_id)
    if existing:
        raise HTTPException(status_code=400, detail="Operator ID already exists")
        
    return operator_repo.create(db, obj_in=operator_in)
