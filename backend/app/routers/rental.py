from typing import List, Optional
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.deps import get_db, RoleChecker
from app.schemas.rental import RentalCreate, RentalResponse
from app.schemas.site_transfer import SiteTransferCreate, SiteTransferResponse
from app.schemas.checkin_checkout import CheckinCheckoutCreate, CheckinCheckoutResponse
from app.services.rental import rental_service

router = APIRouter()

# Restrict actions to specific roles
allow_rental_creation = RoleChecker(["CatAdmin", "Dealer"])
allow_transfers = RoleChecker(["CatAdmin", "Fleet Manager"])
allow_view = RoleChecker(["CatAdmin", "Dealer", "Customer", "Fleet Manager"])

@router.get("/", response_model=List[RentalResponse])
def get_rentals(
    customer_id: Optional[int] = None,
    site_id: Optional[int] = None,
    rental_status: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user=Depends(allow_view)
):
    """List all rentals with optional filters."""
    return rental_repo.get_all(db, skip=skip, limit=limit, customer_id=customer_id, site_id=site_id, rental_status=rental_status)

@router.post("/", response_model=RentalResponse)
def create_rental(rental_in: RentalCreate, db: Session = Depends(get_db), current_user=Depends(allow_rental_creation)):
    """Creates a new rental contract."""
    return rental_service.create_rental(db, rental_in)

@router.post("/transfer", response_model=SiteTransferResponse)
def transfer_site(transfer_in: SiteTransferCreate, db: Session = Depends(get_db), current_user=Depends(allow_transfers)):
    """Transfers a machine to a new site during an active rental."""
    return rental_service.transfer_site(db, transfer_in)

@router.post("/check-action", response_model=CheckinCheckoutResponse)
def checkin_checkout(action_in: CheckinCheckoutCreate, db: Session = Depends(get_db), current_user=Depends(allow_transfers)):
    """Performs a check-in or check-out operation on an active rental."""
    return rental_service.process_checkin_checkout(db, action_in)
