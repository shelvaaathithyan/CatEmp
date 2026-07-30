from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.deps import get_db, get_current_user, RoleChecker
from app.models.user import User
from app.schemas.predictions import (
    DemandPredictionCreate, DemandPredictionResponse,
    UtilizationPredictionCreate, UtilizationPredictionResponse,
    MaintenancePredictionCreate, MaintenancePredictionResponse,
    AnomalyPredictionCreate, AnomalyPredictionResponse
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

@router.post("/anomaly", response_model=AnomalyPredictionResponse)
def create_anomaly_prediction(prediction_in: AnomalyPredictionCreate, db: Session = Depends(get_db)):
    """Stores a new anomaly detection prediction."""
    return prediction_service.create_anomaly_prediction(db, prediction_in)

@router.get("/demand", response_model=List[DemandPredictionResponse])
def get_demand_predictions(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Fetches all demand predictions."""
    return prediction_service.get_demand_predictions(db)

@router.get("/utilization", response_model=List[UtilizationPredictionResponse])
def get_utilization_predictions(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Fetches all utilization predictions."""
    return prediction_service.get_utilization_predictions(db)

@router.get("/maintenance", response_model=List[MaintenancePredictionResponse])
def get_maintenance_predictions(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Fetches all maintenance predictions."""
    return prediction_service.get_maintenance_predictions(db)

@router.get("/anomaly", response_model=List[AnomalyPredictionResponse])
def get_anomaly_predictions(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Fetches all anomaly detection predictions."""
    return prediction_service.get_anomaly_predictions(db)
