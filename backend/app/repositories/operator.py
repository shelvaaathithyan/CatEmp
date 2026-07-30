from sqlalchemy.orm import Session
from app.models.operator import Operator
from app.schemas.operator import OperatorCreate
from app.repositories.base import BaseRepository

class OperatorRepository(BaseRepository[Operator, OperatorCreate, OperatorCreate]):
    def get_by_customer(self, db: Session, customer_id: int):
        return db.query(self.model).filter(self.model.customer_id == customer_id).all()

    def get_by_operator_id(self, db: Session, operator_id: str):
        return db.query(self.model).filter(self.model.operator_id == operator_id).first()
