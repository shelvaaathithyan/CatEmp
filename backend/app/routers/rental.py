from typing import List, Optional
from fastapi import APIRouter, Depends, BackgroundTasks
from sqlalchemy.orm import Session
from app.core.deps import get_db, RoleChecker
from app.schemas.rental import RentalCreate, RentalResponse
from app.schemas.site_transfer import SiteTransferCreate, SiteTransferResponse
from app.schemas.checkin_checkout import CheckinCheckoutCreate, CheckinCheckoutResponse
from app.services.rental import rental_service
from app.repositories.rental import rental_repo

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
    """List rentals with strict role-based data isolation."""
    from app.models.customer import Customer
    from app.models.fleet_manager import FleetManager
    from app.models.dealer import Dealer
    from app.models.machine import Machine

    query = db.query(rental_repo.model)

    if current_user.role == "Customer":
        customer = db.query(Customer).filter(Customer.user_id == current_user.id).first()
        if not customer:
            return []
        query = query.filter(rental_repo.model.customer_id == customer.id)
    elif current_user.role == "Fleet Manager":
        fm = db.query(FleetManager).filter(FleetManager.user_id == current_user.id).first()
        if not fm:
            return []
        query = query.filter(rental_repo.model.site_id == fm.site_id)
    elif current_user.role == "Dealer":
        dealer = db.query(Dealer).filter(Dealer.user_id == current_user.id).first()
        if not dealer:
            return []
        dealer_machines = db.query(Machine.equipment_id).filter(Machine.dealer_id == dealer.id).subquery()
        query = query.filter(rental_repo.model.equipment_id.in_(dealer_machines))
    elif current_user.role == "CatAdmin":
        if customer_id:
            query = query.filter(rental_repo.model.customer_id == customer_id)

    if site_id:
        query = query.filter(rental_repo.model.site_id == site_id)
    if rental_status:
        query = query.filter(rental_repo.model.rental_status == rental_status)

    return query.offset(skip).limit(limit).all()

@router.get("/{rental_id}", response_model=RentalResponse)
def get_rental(rental_id: int, db: Session = Depends(get_db), current_user=Depends(allow_view)):
    """Get details of a specific rental."""
    from fastapi import HTTPException
    from app.models.customer import Customer
    from app.models.fleet_manager import FleetManager
    from app.models.dealer import Dealer
    from app.models.machine import Machine
    
    rental = rental_repo.get(db, rental_id)
    if not rental:
        raise HTTPException(status_code=404, detail="Rental not found")
        
    if current_user.role == "Customer":
        customer = db.query(Customer).filter(Customer.user_id == current_user.id).first()
        if not customer or rental.customer_id != customer.id:
            raise HTTPException(status_code=403, detail="Not authorized")
    elif current_user.role == "Fleet Manager":
        fm = db.query(FleetManager).filter(FleetManager.user_id == current_user.id).first()
        if not fm or rental.site_id != fm.site_id:
            raise HTTPException(status_code=403, detail="Not authorized")
    elif current_user.role == "Dealer":
        dealer = db.query(Dealer).filter(Dealer.user_id == current_user.id).first()
        machine = db.query(Machine).filter(Machine.equipment_id == rental.equipment_id).first()
        if not dealer or not machine or machine.dealer_id != dealer.id:
            raise HTTPException(status_code=403, detail="Not authorized")
            
    return rental

@router.post("/", response_model=RentalResponse)
def create_rental(rental_in: RentalCreate, db: Session = Depends(get_db), current_user=Depends(allow_rental_creation)):
    """Creates a new rental contract."""
    return rental_service.create_rental(db, rental_in)

@router.post("/transfer", response_model=SiteTransferResponse)
def transfer_site(
    transfer_in: SiteTransferCreate, 
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db), 
    current_user=Depends(allow_transfers)
):
    """Transfers a machine to a new site during an active rental."""
    from app.models.fleet_manager import FleetManager
    from app.models.customer import Customer
    from app.models.rental import Rental
    from fastapi import HTTPException
    
    fm = db.query(FleetManager).filter(FleetManager.user_id == current_user.id).first()
    if not fm:
        raise HTTPException(status_code=403, detail="User is not a Fleet Manager.")
        
    # Override transferred_by with the actual FleetManager ID (not the User ID)
    transfer_in.transferred_by = fm.id
    
    # Process the transfer synchronously
    transfer = rental_service.transfer_site(db, transfer_in)
    
    # Find the customer ID to notify
    rental = db.query(Rental).filter(Rental.id == transfer.rental_id).first()
    if rental:
        customer = db.query(Customer).filter(Customer.id == rental.customer_id).first()
        if customer:
            payload = {
                "user_id": customer.user_id,
                "title": "Machine Transferred",
                "message": f"Machine {rental.equipment_id} was moved to site {transfer_in.to_site_id}",
                "equipment_id": rental.equipment_id,
                "priority": "MEDIUM",
                "notification_type": "SITE_TRANSFER"
            }
            
            async def publish_notification():
                from app.core.rabbitmq import rabbitmq
                print(f"[API] Publishing background notification to user {customer.user_id}")
                await rabbitmq.publish_message(payload)
                
            background_tasks.add_task(publish_notification)
            
    return transfer

@router.post("/check-action", response_model=CheckinCheckoutResponse)
def checkin_checkout(action_in: CheckinCheckoutCreate, db: Session = Depends(get_db), current_user=Depends(allow_transfers)):
    """Performs a check-in or check-out operation on an active rental."""
    return rental_service.process_checkin_checkout(db, action_in)

@router.get("/transfer", response_model=List[SiteTransferResponse])
def get_transfers(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user=Depends(allow_view)
):
    """Get history of site transfers."""
    from app.repositories.events import site_transfer_repo
    from app.models.fleet_manager import FleetManager
    
    fleet_manager_id = None
    if current_user.role == "Fleet Manager":
        fm = db.query(FleetManager).filter(FleetManager.user_id == current_user.id).first()
        if fm:
            fleet_manager_id = fm.id
        else:
            return []
            
    return site_transfer_repo.get_all(db, skip=skip, limit=limit, fleet_manager_id=fleet_manager_id)

@router.get("/check-action", response_model=List[CheckinCheckoutResponse])
def get_check_actions(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user=Depends(allow_view)
):
    """Get history of check-in and check-out actions."""
    from app.repositories.events import checkin_checkout_repo
    from app.models.fleet_manager import FleetManager
    
    fleet_manager_id = None
    if current_user.role == "Fleet Manager":
        fm = db.query(FleetManager).filter(FleetManager.user_id == current_user.id).first()
        if fm:
            fleet_manager_id = fm.id
        else:
            return []
            
    return checkin_checkout_repo.get_all(db, skip=skip, limit=limit, fleet_manager_id=fleet_manager_id)
