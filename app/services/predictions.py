from sqlalchemy.orm import Session
from app.models.predictions import DemandPrediction, UtilizationPrediction, MaintenancePrediction
from app.schemas.predictions import DemandPredictionCreate, UtilizationPredictionCreate, MaintenancePredictionCreate

class PredictionService:
    @staticmethod
    def create_demand_prediction(db: Session, prediction_in: DemandPredictionCreate) -> DemandPrediction:
        """Stores a demand forecasting prediction."""
        db_obj = DemandPrediction(**prediction_in.model_dump())
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    @staticmethod
    def create_utilization_prediction(db: Session, prediction_in: UtilizationPredictionCreate) -> UtilizationPrediction:
        """Stores a utilization prediction."""
        db_obj = UtilizationPrediction(**prediction_in.model_dump())
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    @staticmethod
    def create_maintenance_prediction(db: Session, prediction_in: MaintenancePredictionCreate) -> MaintenancePrediction:
        """Stores a predictive maintenance record."""
        db_obj = MaintenancePrediction(**prediction_in.model_dump())
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

prediction_service = PredictionService()
