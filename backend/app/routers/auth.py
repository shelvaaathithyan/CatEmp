from datetime import timedelta
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.core.deps import get_db, get_current_user
from app.core.security import create_access_token
from app.schemas.user import UserCreate, UserResponse
from app.services.auth import auth_service
from app.models.user import User
from app.models.rental import Rental
from app.models.machine import Machine

router = APIRouter()

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(user_in: UserCreate, db: Session = Depends(get_db)):
    """Registers a new user in the system."""
    return auth_service.register_user(db, user_in)

@router.post("/login")
def login(db: Session = Depends(get_db), form_data: OAuth2PasswordRequestForm = Depends()):
    """Authenticates a user and returns a JWT token."""
    user = auth_service.authenticate_user(db, form_data.username, form_data.password)
    access_token = create_access_token(
        subject=user.id, role=user.role, expires_delta=timedelta(minutes=1440)
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me", response_model=UserResponse)
def get_current_user_profile(current_user: User = Depends(get_current_user)):
    """Returns the profile of the currently authenticated user."""
    return current_user

@router.get("/network", response_model=List[UserResponse])
def get_user_network(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Returns a list of users connected to the current user via active rentals."""
    connected_users = {}
    
    if current_user.role == 'Customer' and current_user.customer:
        rentals = db.query(Rental).filter(Rental.customer_id == current_user.customer.id).all()
        for r in rentals:
            if r.fleet_manager and r.fleet_manager.user:
                connected_users[r.fleet_manager.user.id] = r.fleet_manager.user
            if r.machine and r.machine.dealer and r.machine.dealer.user:
                connected_users[r.machine.dealer.user.id] = r.machine.dealer.user
                
    elif current_user.role == 'Dealer' and current_user.dealer:
        machines = db.query(Machine).filter(Machine.dealer_id == current_user.dealer.id).all()
        machine_ids = [m.equipment_id for m in machines]
        if machine_ids:
            rentals = db.query(Rental).filter(Rental.equipment_id.in_(machine_ids)).all()
            for r in rentals:
                if r.customer and r.customer.user:
                    connected_users[r.customer.user.id] = r.customer.user
                    
    elif current_user.role == 'Fleet Manager' and current_user.fleet_manager:
        rentals = db.query(Rental).filter(Rental.fleet_manager_id == current_user.fleet_manager.id).all()
        for r in rentals:
            if r.customer and r.customer.user:
                connected_users[r.customer.user.id] = r.customer.user
            if r.machine and r.machine.dealer and r.machine.dealer.user:
                connected_users[r.machine.dealer.user.id] = r.machine.dealer.user
                
    return list(connected_users.values())
