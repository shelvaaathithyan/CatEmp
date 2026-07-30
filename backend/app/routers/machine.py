from typing import List, Optional
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.deps import get_db, RoleChecker
from app.schemas.machine import MachineResponse, MachineCreate
from app.repositories.machine import machine_repo
from app.services.timeline import timeline_service

router = APIRouter()

# CatAdmin has access to everything. Dealers have access to their machines.
allow_view_timeline = RoleChecker(["CatAdmin", "Dealer", "Fleet Manager", "Customer"])

@router.get("/", response_model=List[MachineResponse])
def get_machines(
    dealer_id: Optional[int] = None,
    status: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user=Depends(allow_view_timeline)
):
    """List all machines with optional filters."""
    return machine_repo.get_all(db, skip=skip, limit=limit, dealer_id=dealer_id, status=status)

@router.get("/{equipment_id}/timeline")
def get_machine_timeline(equipment_id: str, db: Session = Depends(get_db), current_user=Depends(allow_view_timeline)):
    """Retrieves the complete historical timeline of a machine."""
    return timeline_service.get_machine_timeline(db, equipment_id)
