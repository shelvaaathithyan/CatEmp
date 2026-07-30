from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.deps import get_db, RoleChecker
from app.schemas.predictions import (
    DemandPredictionCreate, DemandPredictionResponse,
    UtilizationPredictionCreate, UtilizationPredictionResponse,
    MaintenancePredictionCreate, MaintenancePredictionResponse
)
from app.services.predictions import prediction_service

router = APIRouter()

@router.post("/demand", response_model=DemandPredictionResponse)
def create_demand_prediction(prediction_in: DemandPredictionCreate, db: Session = Depends(get_db)):
    """Stores a new demand prediction."""
    return prediction_service.create_demand_prediction(db, prediction_in)

@router.post("/utilization", response_model=UtilizationPredictionResponse)
def create_utilization_prediction(prediction_in: UtilizationPredictionCreate, db: Session = Depends(get_db)):
    """Stores a new utilization prediction."""
    return prediction_service.create_utilization_prediction(db, prediction_in)

@router.post("/maintenance", response_model=MaintenancePredictionResponse)
def create_maintenance_prediction(prediction_in: MaintenancePredictionCreate, db: Session = Depends(get_db)):
    """Stores a new predictive maintenance prediction."""
    return prediction_service.create_maintenance_prediction(db, prediction_in)
