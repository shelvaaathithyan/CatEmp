from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import RoleChecker
from app.models.user import User
from app.schemas.operator import OperatorResponse, OperatorCreate
from app.services import operator as operator_service

router = APIRouter(prefix="/operators", tags=["Operators"])

@router.get("/", response_model=List[OperatorResponse])
def list_operators(
    db: Session = Depends(get_db),
    current_user: User = Depends(RoleChecker(["CatAdmin", "Customer", "Fleet Manager"]))
):
    """List operators based on role."""
    return operator_service.get_operators_for_user(db, current_user)

@router.post("/", response_model=OperatorResponse)
def create_operator(
    operator_in: OperatorCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(RoleChecker(["CatAdmin", "Customer", "Fleet Manager"]))
):
    """Create a new operator. Fleet Managers can register operators during check-in."""
    return operator_service.create_operator(db, current_user, operator_in)
