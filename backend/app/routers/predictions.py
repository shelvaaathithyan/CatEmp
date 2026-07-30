from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.deps import get_db, get_current_user, RoleChecker
from app.models.user import User
from app.models.machine import Machine
from app.models.rental import Rental
from app.core.rabbitmq import rabbitmq
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
async def create_utilization_prediction(prediction_in: UtilizationPredictionCreate, db: Session = Depends(get_db)):
    """Stores a new utilization prediction and alerts if overutilized."""
    db_obj = prediction_service.create_utilization_prediction(db, prediction_in)
    
    if float(prediction_in.utilization_score) > 0.90:
        # Find who to notify (Dealer and Fleet Manager)
        machine = db.query(Machine).filter(Machine.equipment_id == prediction_in.equipment_id).first()
        active_rental = db.query(Rental).filter(
            Rental.equipment_id == prediction_in.equipment_id,
            Rental.rental_status == "ACTIVE"
        ).first()

        message = f"Machine {prediction_in.equipment_id} is severely overutilized (Score: {prediction_in.utilization_score}). Immediate action recommended."
        
        if active_rental and active_rental.fleet_manager:
            await rabbitmq.publish_message({
                "user_id": active_rental.fleet_manager.user_id,
                "title": "Machine Overutilization Alert",
                "message": message,
                "equipment_id": prediction_in.equipment_id,
                "priority": "HIGH",
                "notification_type": "ALERT"
            })
            
        if machine and machine.dealer:
            await rabbitmq.publish_message({
                "user_id": machine.dealer.user_id,
                "title": "Machine Overutilization Alert",
                "message": message,
                "equipment_id": prediction_in.equipment_id,
                "priority": "HIGH",
                "notification_type": "ALERT"
            })
            
    return db_obj

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
    """Fetches demand predictions based on role."""
    return prediction_service.get_demand_predictions(db, current_user)

@router.get("/utilization", response_model=List[UtilizationPredictionResponse])
def get_utilization_predictions(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Fetches utilization predictions based on role."""
    return prediction_service.get_utilization_predictions(db, current_user)

@router.get("/maintenance", response_model=List[MaintenancePredictionResponse])
def get_maintenance_predictions(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Fetches maintenance predictions based on role."""
    return prediction_service.get_maintenance_predictions(db, current_user)

@router.get("/anomaly", response_model=List[AnomalyPredictionResponse])
def get_anomaly_predictions(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Fetches anomaly detection predictions based on role."""
    return prediction_service.get_anomaly_predictions(db, current_user)
