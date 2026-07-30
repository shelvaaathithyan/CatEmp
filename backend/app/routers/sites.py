from typing import List, Optional
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.deps import get_db, RoleChecker, get_current_user
from app.models.user import User
from app.schemas.site import SiteResponse
from app.repositories.site import site_repo
from app.models.customer import Customer

router = APIRouter()

allow_view_sites = RoleChecker(["CatAdmin", "Dealer", "Customer", "Fleet Manager"])

@router.get("/", response_model=List[SiteResponse])
def get_sites(
    customer_id: Optional[int] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(allow_view_sites)
):
    """List all sites. Customers automatically only see their own sites."""
    
    if current_user.role == "Customer":
        # Force customer_id filter for Customers
        customer = db.query(Customer).filter(Customer.user_id == current_user.id).first()
        if customer:
            customer_id = customer.id
        else:
            return [] # Edge case where user is Customer but has no profile
            
    site_ids = None
    if current_user.role == "Fleet Manager":
        from app.models.fleet_manager import FleetManager
        fm = db.query(FleetManager).filter(FleetManager.user_id == current_user.id).first()
        if fm:
            site_ids = [fm.site_id]
        else:
            return []
            
    query = db.query(site_repo.model)
    if customer_id:
        query = query.filter(site_repo.model.customer_id == customer_id)
    if site_ids:
        query = query.filter(site_repo.model.id.in_(site_ids))
        
    return query.offset(skip).limit(limit).all()
