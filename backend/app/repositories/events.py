from app.repositories.base import BaseRepository
from app.models.site_transfer import SiteTransfer
from app.models.checkin_checkout import CheckinCheckout
from app.models.equipment_usage import EquipmentUsage
from app.schemas.site_transfer import SiteTransferCreate, SiteTransferBase
from app.schemas.checkin_checkout import CheckinCheckoutCreate, CheckinCheckoutBase
from app.schemas.equipment_usage import EquipmentUsageCreate, EquipmentUsageBase

from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.rental import Rental

class SiteTransferRepository(BaseRepository[SiteTransfer, SiteTransferCreate, SiteTransferBase]):
    def get_all(self, db: Session, skip: int = 0, limit: int = 100, fleet_manager_id: Optional[int] = None) -> List[SiteTransfer]:
        query = db.query(self.model)
        if fleet_manager_id:
            query = query.join(Rental, Rental.id == self.model.rental_id).filter(Rental.fleet_manager_id == fleet_manager_id)
        return query.order_by(self.model.transfer_date.desc()).offset(skip).limit(limit).all()

site_transfer_repo = SiteTransferRepository(SiteTransfer)

class CheckinCheckoutRepository(BaseRepository[CheckinCheckout, CheckinCheckoutCreate, CheckinCheckoutBase]):
    def get_all(self, db: Session, skip: int = 0, limit: int = 100, fleet_manager_id: Optional[int] = None) -> List[CheckinCheckout]:
        query = db.query(self.model)
        if fleet_manager_id:
            query = query.join(Rental, Rental.id == self.model.rental_id).filter(Rental.fleet_manager_id == fleet_manager_id)
        return query.order_by(self.model.timestamp.desc()).offset(skip).limit(limit).all()

checkin_checkout_repo = CheckinCheckoutRepository(CheckinCheckout)

class EquipmentUsageRepository(BaseRepository[EquipmentUsage, EquipmentUsageCreate, EquipmentUsageBase]):
    def get_all(self, db: Session, skip: int = 0, limit: int = 100, customer_id: Optional[int] = None, fleet_manager_id: Optional[int] = None) -> List[EquipmentUsage]:
        """Fetch equipment usage records, optionally filtering by customer's rentals or fleet manager."""
        query = db.query(self.model)
        
        if customer_id or fleet_manager_id:
            query = query.join(Rental, Rental.id == self.model.rental_id)
            if customer_id:
                query = query.filter(Rental.customer_id == customer_id)
            if fleet_manager_id:
                query = query.filter(Rental.fleet_manager_id == fleet_manager_id)
            
        return query.order_by(self.model.usage_date.desc()).offset(skip).limit(limit).all()

equipment_usage_repo = EquipmentUsageRepository(EquipmentUsage)
