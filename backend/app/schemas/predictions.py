from pydantic import BaseModel
from datetime import date, datetime
from typing import Optional
from decimal import Decimal

# Maintenance Prediction
class MaintenancePredictionBase(BaseModel):
    equipment_id: str
    prediction_timestamp: datetime
    maintenance_probability: Optional[Decimal] = None
    predicted_service_date: Optional[date] = None
    confidence: Optional[Decimal] = None
    model: Optional[str] = None
    equipment_type: Optional[str] = None

class MaintenancePredictionCreate(MaintenancePredictionBase):
    pass

class MaintenancePredictionResponse(MaintenancePredictionBase):
    id: int

    class Config:
        from_attributes = True

# Utilization Prediction
class UtilizationPredictionBase(BaseModel):
    prediction_timestamp: datetime
    equipment_id: str
    utilization_score: Optional[Decimal] = None
    predicted_idle_hours: Optional[Decimal] = None
    status: Optional[str] = None
    model: Optional[str] = None
    equipment_type: Optional[str] = None

class UtilizationPredictionCreate(UtilizationPredictionBase):
    pass

class UtilizationPredictionResponse(UtilizationPredictionBase):
    id: int

    class Config:
        from_attributes = True

# Demand Prediction
class DemandPredictionBase(BaseModel):
    prediction_timestamp: datetime
    equipment_type: str
    site_id: int
    prediction_period: Optional[str] = None
    expected_demand: Optional[int] = None
    model: Optional[str] = None

class DemandPredictionCreate(DemandPredictionBase):
    pass

class DemandPredictionResponse(DemandPredictionBase):
    id: int

    class Config:
        from_attributes = True

# Anomaly Prediction
class AnomalyPredictionBase(BaseModel):
    prediction_timestamp: datetime
    equipment_id: str
    anomaly_status: str
    anomaly_score: Optional[Decimal] = None
    severity: Optional[str] = None
    insight_message: Optional[str] = None
    model: Optional[str] = None
    equipment_type: Optional[str] = None

class AnomalyPredictionCreate(AnomalyPredictionBase):
    pass

class AnomalyPredictionResponse(AnomalyPredictionBase):
    id: int

    class Config:
        from_attributes = True
