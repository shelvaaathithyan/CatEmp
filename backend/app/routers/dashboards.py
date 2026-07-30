from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user, RoleChecker
from app.models.user import User
from app.schemas.dashboard import DealerDashboardResponse, CustomerDashboardResponse, FleetManagerDashboardResponse
from app.services import dashboard as dashboard_service

router = APIRouter(prefix="/dashboards", tags=["Dashboards"])

@router.get("/dealer", response_model=DealerDashboardResponse)
def get_dealer_dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(RoleChecker(["CatAdmin", "Dealer"]))
):
    kpis = dashboard_service.get_dealer_kpis(db, current_user.id)
    if not kpis:
        raise HTTPException(status_code=404, detail="Dealer profile not found")
    return kpis

@router.get("/customer", response_model=CustomerDashboardResponse)
def get_customer_dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(RoleChecker(["CatAdmin", "Customer"]))
):
    kpis = dashboard_service.get_customer_kpis(db, current_user.id)
    if not kpis:
        raise HTTPException(status_code=404, detail="Customer profile not found")
    return kpis

@router.get("/fleet-manager", response_model=FleetManagerDashboardResponse)
def get_fleet_manager_dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(RoleChecker(["CatAdmin", "Fleet Manager"]))
):
    kpis = dashboard_service.get_fleet_manager_kpis(db, current_user.id)
    if not kpis:
        raise HTTPException(status_code=404, detail="Fleet Manager profile not found")
    return kpis
