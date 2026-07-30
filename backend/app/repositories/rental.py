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

rental_repo = RentalRepository(Rental)
