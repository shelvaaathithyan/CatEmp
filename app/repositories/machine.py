from typing import Optional
from sqlalchemy.orm import Session
from app.repositories.base import BaseRepository
from app.models.machine import Machine
from app.schemas.machine import MachineCreate, MachineBase

class MachineRepository(BaseRepository[Machine, MachineCreate, MachineBase]):
    def get_by_equipment_id(self, db: Session, equipment_id: str) -> Optional[Machine]:
        """Fetch a machine by its unique equipment ID."""
        return db.query(Machine).filter(Machine.equipment_id == equipment_id).first()

machine_repo = MachineRepository(Machine)
