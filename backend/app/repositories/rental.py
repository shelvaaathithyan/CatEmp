from typing import Optional
from sqlalchemy.orm import Session
from app.repositories.base import BaseRepository
from app.models.rental import Rental
from app.schemas.rental import RentalCreate, RentalUpdate

class RentalRepository(BaseRepository[Rental, RentalCreate, RentalUpdate]):
    def get_active_rental_for_machine(self, db: Session, equipment_id: str) -> Optional[Rental]:
        """Check if a machine is currently in an active rental."""
        return db.query(Rental).filter(
            Rental.equipment_id == equipment_id,
            Rental.rental_status.in_(["PENDING", "ACTIVE"]),
            Rental.actual_return_date.is_(None)
        ).first()

    def get_all(self, db: Session, skip: int = 0, limit: int = 100, customer_id: Optional[int] = None, site_id: Optional[int] = None, rental_status: Optional[str] = None):
        """Fetch rentals with optional filtering."""
        query = db.query(self.model)
        if customer_id:
            query = query.filter(self.model.customer_id == customer_id)
        if site_id:
            query = query.filter(self.model.site_id == site_id)
        if rental_status:
            query = query.filter(self.model.rental_status == rental_status)
        return query.offset(skip).limit(limit).all()

rental_repo = RentalRepository(Rental)
