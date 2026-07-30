from typing import Optional
from sqlalchemy.orm import Session
from app.repositories.base import BaseRepository
from app.models.machine import Machine
from app.schemas.machine import MachineCreate, MachineBase

class MachineRepository(BaseRepository[Machine, MachineCreate, MachineBase]):
    def get_by_equipment_id(self, db: Session, equipment_id: str) -> Optional[Machine]:
        """Fetch a machine by its unique equipment ID."""
        return db.query(Machine).filter(Machine.equipment_id == equipment_id).first()

    def get_all(self, db: Session, skip: int = 0, limit: int = 100, dealer_id: Optional[int] = None, status: Optional[str] = None):
        """Fetch machines with optional filtering."""
        query = db.query(self.model)
        if dealer_id:
            query = query.filter(self.model.dealer_id == dealer_id)
        if status:
            query = query.filter(self.model.status == status)
        return query.offset(skip).limit(limit).all()

machine_repo = MachineRepository(Machine)
