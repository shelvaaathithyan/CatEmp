from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.deps import get_db, RoleChecker
from app.schemas.equipment_usage import EquipmentUsageCreate, EquipmentUsageResponse
from app.repositories.events import equipment_usage_repo

router = APIRouter()
allow_usage_logging = RoleChecker(["CatAdmin", "Fleet Manager"])

@router.post("/usage", response_model=EquipmentUsageResponse)
def log_equipment_usage(usage_in: EquipmentUsageCreate, db: Session = Depends(get_db), current_user=Depends(allow_usage_logging)):
    """Logs daily equipment usage details (append-only)."""
    return equipment_usage_repo.create(db, usage_in)
