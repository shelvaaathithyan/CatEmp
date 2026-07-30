from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.deps import get_db, RoleChecker
from app.schemas.machine import MachineResponse
from app.repositories.machine import machine_repo
from app.services.timeline import timeline_service

router = APIRouter()

# CatAdmin has access to everything. Dealers have access to their machines.
allow_view_timeline = RoleChecker(["CatAdmin", "Dealer", "Fleet Manager", "Customer"])

@router.get("/{equipment_id}/timeline")
def get_machine_timeline(equipment_id: str, db: Session = Depends(get_db), current_user=Depends(allow_view_timeline)):
    """Retrieves the complete historical timeline of a machine."""
    return timeline_service.get_machine_timeline(db, equipment_id)
