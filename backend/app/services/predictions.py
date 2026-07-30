from sqlalchemy.orm import Session
from app.models.predictions import DemandPrediction, UtilizationPrediction, MaintenancePrediction, AnomalyPrediction
from app.schemas.predictions import DemandPredictionCreate, UtilizationPredictionCreate, MaintenancePredictionCreate, AnomalyPredictionCreate
from app.models.user import User
from app.models.machine import Machine
from app.models.rental import Rental

def _enrich_and_deduplicate(db: Session, records, key_attr="equipment_id"):
    seen = set()
    result = []
    equip_ids = [getattr(r, key_attr, None) for r in records if getattr(r, key_attr, None)]
    machines = {}
    if equip_ids:
        for m in db.query(Machine).filter(Machine.equipment_id.in_(equip_ids)).all():
            machines[m.equipment_id] = (m.model, m.equipment_type)

    for r in records:
        val = getattr(r, key_attr, None)
        if val not in seen:
            seen.add(val)
            if val in machines:
                r.model = machines[val][0]
                r.equipment_type = machines[val][1]
            result.append(r)
    return result

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
    def get_demand_predictions(db: Session, current_user: User):
        """Fetches demand predictions, visible globally for Dealers and Fleet Managers."""
        if current_user.role not in ["Dealer", "Fleet Manager", "CatAdmin"]:
            return []
        records = db.query(DemandPrediction).order_by(DemandPrediction.prediction_timestamp.desc()).all()
        seen = set()
        result = []
        for r in records:
            key = (r.equipment_type, r.site_id)
            if key not in seen:
                seen.add(key)
                # Map model if not set
                if not getattr(r, 'model', None):
                    model_map = {
                        'CAT 320 GC (Excavator)': '320 GC',
                        'CAT 950 GC (Wheel Loader)': '950 GC',
                        'CAT D6 LMT (Bulldozer)': 'D6 LMT',
                        'CAT 777 OHT (Off-Highway Truck)': '777 OHT',
                        'Excavator': '320 GC',
                        'Wheel Loader': '950 GC',
                        'Bulldozer': 'D6 LMT'
                    }
                    r.model = model_map.get(r.equipment_type, '320 GC')
                result.append(r)
        return result

    @staticmethod
    def get_utilization_predictions(db: Session, current_user: User):
        """Fetches utilization predictions filtered by user's related machines (latest per equipment)."""
        query = db.query(UtilizationPrediction)
        
        if current_user.role == "CatAdmin":
            pass
        elif current_user.role == "Dealer" and current_user.dealer:
            machines = db.query(Machine.equipment_id).filter(
                Machine.dealer_id == current_user.dealer.id,
                Machine.status == "RENTED"
            ).subquery()
            query = query.filter(UtilizationPrediction.equipment_id.in_(machines))
        elif current_user.role == "Customer" and current_user.customer:
            rentals = db.query(Rental.equipment_id).filter(
                Rental.customer_id == current_user.customer.id,
                Rental.rental_status == "ACTIVE"
            ).subquery()
            query = query.filter(UtilizationPrediction.equipment_id.in_(rentals))
        elif current_user.role == "Fleet Manager" and current_user.fleet_manager:
            rentals = db.query(Rental.equipment_id).filter(
                Rental.fleet_manager_id == current_user.fleet_manager.id,
                Rental.rental_status == "ACTIVE"
            ).subquery()
            query = query.filter(UtilizationPrediction.equipment_id.in_(rentals))
        else:
            return []
            
        records = query.order_by(UtilizationPrediction.prediction_timestamp.desc()).all()
        return _enrich_and_deduplicate(db, records)

    @staticmethod
    def get_maintenance_predictions(db: Session, current_user: User):
        """Fetches maintenance predictions filtered by user's related machines (latest per equipment)."""
        query = db.query(MaintenancePrediction)
        
        if current_user.role == "CatAdmin":
            pass
        elif current_user.role == "Dealer" and current_user.dealer:
            machines = db.query(Machine.equipment_id).filter(
                Machine.dealer_id == current_user.dealer.id,
                Machine.status == "RENTED"
            ).subquery()
            query = query.filter(MaintenancePrediction.equipment_id.in_(machines))
        elif current_user.role == "Customer" and current_user.customer:
            rentals = db.query(Rental.equipment_id).filter(
                Rental.customer_id == current_user.customer.id,
                Rental.rental_status == "ACTIVE"
            ).subquery()
            query = query.filter(MaintenancePrediction.equipment_id.in_(rentals))
        elif current_user.role == "Fleet Manager" and current_user.fleet_manager:
            rentals = db.query(Rental.equipment_id).filter(
                Rental.fleet_manager_id == current_user.fleet_manager.id,
                Rental.rental_status == "ACTIVE"
            ).subquery()
            query = query.filter(MaintenancePrediction.equipment_id.in_(rentals))
        else:
            return []
            
        records = query.order_by(MaintenancePrediction.prediction_timestamp.desc()).all()
        return _enrich_and_deduplicate(db, records)

    @staticmethod
    def get_anomaly_predictions(db: Session, current_user: User):
        """Fetches anomaly detection predictions filtered by user's related machines (latest per equipment)."""
        query = db.query(AnomalyPrediction)
        
        if current_user.role == "CatAdmin":
            pass
        elif current_user.role == "Dealer" and current_user.dealer:
            machines = db.query(Machine.equipment_id).filter(
                Machine.dealer_id == current_user.dealer.id,
                Machine.status == "RENTED"
            ).subquery()
            query = query.filter(AnomalyPrediction.equipment_id.in_(machines))
        elif current_user.role == "Customer" and current_user.customer:
            rentals = db.query(Rental.equipment_id).filter(
                Rental.customer_id == current_user.customer.id,
                Rental.rental_status == "ACTIVE"
            ).subquery()
            query = query.filter(AnomalyPrediction.equipment_id.in_(rentals))
        elif current_user.role == "Fleet Manager" and current_user.fleet_manager:
            rentals = db.query(Rental.equipment_id).filter(
                Rental.fleet_manager_id == current_user.fleet_manager.id,
                Rental.rental_status == "ACTIVE"
            ).subquery()
            query = query.filter(AnomalyPrediction.equipment_id.in_(rentals))
        else:
            return []
            
        records = query.order_by(AnomalyPrediction.prediction_timestamp.desc()).all()
        return _enrich_and_deduplicate(db, records)


prediction_service = PredictionService()



