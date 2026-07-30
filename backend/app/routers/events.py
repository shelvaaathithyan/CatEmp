from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.deps import get_db, RoleChecker
from app.schemas.equipment_usage import EquipmentUsageCreate, EquipmentUsageResponse
from app.repositories.events import equipment_usage_repo

router = APIRouter()
allow_usage_logging = RoleChecker(["CatAdmin", "Fleet Manager"])

from typing import List, Optional
from app.models.user import User
from app.models.customer import Customer

@router.post("/usage", response_model=EquipmentUsageResponse)
def log_equipment_usage(usage_in: EquipmentUsageCreate, db: Session = Depends(get_db), current_user=Depends(allow_usage_logging)):
    """Logs daily equipment usage details (append-only)."""
    return equipment_usage_repo.create(db, usage_in)

allow_view_usage = RoleChecker(["CatAdmin", "Dealer", "Customer", "Fleet Manager"])

@router.get("/usage", response_model=List[EquipmentUsageResponse])
def get_usage(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(allow_view_usage)
):
    """Retrieves equipment usage logs. Customers only see usage for their rentals."""
    customer_id = None
    fleet_manager_id = None
    
    if current_user.role == "Customer":
        customer = db.query(Customer).filter(Customer.user_id == current_user.id).first()
        if customer:
            customer_id = customer.id
        else:
            return []
            
    if current_user.role == "Fleet Manager":
        from app.models.fleet_manager import FleetManager
        fm = db.query(FleetManager).filter(FleetManager.user_id == current_user.id).first()
        if fm:
            fleet_manager_id = fm.id
        else:
            return []
            
    return equipment_usage_repo.get_all(db, skip=skip, limit=limit, customer_id=customer_id, fleet_manager_id=fleet_manager_id)
