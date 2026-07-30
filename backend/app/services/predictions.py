from sqlalchemy.orm import Session
from app.models.predictions import DemandPrediction, UtilizationPrediction, MaintenancePrediction, AnomalyPrediction
from app.schemas.predictions import DemandPredictionCreate, UtilizationPredictionCreate, MaintenancePredictionCreate, AnomalyPredictionCreate

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

    @staticmethod
    def create_anomaly_prediction(db: Session, prediction_in: AnomalyPredictionCreate) -> AnomalyPrediction:
        """Stores an anomaly detection prediction."""
        db_obj = AnomalyPrediction(**prediction_in.model_dump())
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    @staticmethod
    def get_demand_predictions(db: Session):
        """Fetches all demand predictions, most recent first."""
        return db.query(DemandPrediction).order_by(DemandPrediction.prediction_timestamp.desc()).all()

    @staticmethod
    def get_utilization_predictions(db: Session):
        """Fetches all utilization predictions, most recent first."""
        return db.query(UtilizationPrediction).order_by(UtilizationPrediction.prediction_timestamp.desc()).all()

    @staticmethod
    def get_maintenance_predictions(db: Session):
        """Fetches all maintenance predictions, most recent first."""
        return db.query(MaintenancePrediction).order_by(MaintenancePrediction.prediction_timestamp.desc()).all()

    @staticmethod
    def get_anomaly_predictions(db: Session):
        """Fetches all anomaly detection predictions, most recent first."""
        return db.query(AnomalyPrediction).order_by(AnomalyPrediction.prediction_timestamp.desc()).all()

prediction_service = PredictionService()

