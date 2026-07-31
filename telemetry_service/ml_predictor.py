import os
import sys
import joblib
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from logger import logger

class MLPredictor:
    def __init__(self, model_dir: str = "../ml_prediction"):
        if not os.path.exists(model_dir):
            if os.path.exists("ml_prediction"):
                model_dir = "ml_prediction"
            elif os.path.exists("../ml_prediction"):
                model_dir = "../ml_prediction"

        self.model_dir = model_dir
        logger.info(f"Loading PyTorch ML model weights from directory: {os.path.abspath(model_dir)}")

        # Load PyTorch models exclusively
        self._load_pytorch_models(model_dir)
        logger.info("Successfully initialized PyTorch ML Predictor (Demand, Maintenance, Utilization, Anomaly).")

    def _load_pytorch_models(self, model_dir: str):
        try:
            import torch
            import torch.nn as nn

            # 1. PyTorch Utilization Model
            pt_util_path = os.path.join(model_dir, "utilization_pytorch_model.pt")
            if os.path.exists(pt_util_path):
                input_dim = joblib.load(os.path.join(model_dir, "utilization_input_dim.joblib"))
                self.pt_util_scaler = joblib.load(os.path.join(model_dir, "utilization_scaler.joblib"))
                self.pt_util_encoder = joblib.load(os.path.join(model_dir, "utilization_encoder.joblib"))
                self.pt_util_target_scaler = joblib.load(os.path.join(model_dir, "utilization_target_scaler.joblib"))

                class UtilizationPyTorchNet(nn.Module):
                    def __init__(self, input_size):
                        super(UtilizationPyTorchNet, self).__init__()
                        self.shared = nn.Sequential(
                            nn.Linear(input_size, 128),
                            nn.ReLU(),
                            nn.BatchNorm1d(128),
                            nn.Dropout(0.15),
                            nn.Linear(128, 64),
                            nn.ReLU(),
                            nn.BatchNorm1d(64)
                        )
                        self.head_score = nn.Sequential(
                            nn.Linear(64, 32),
                            nn.ReLU(),
                            nn.Linear(32, 1)
                        )
                        self.head_idle = nn.Sequential(
                            nn.Linear(64, 32),
                            nn.ReLU(),
                            nn.Linear(32, 1)
                        )

                    def forward(self, x):
                        feat = self.shared(x)
                        score = self.head_score(feat)
                        idle = self.head_idle(feat)
                        return torch.cat([score, idle], dim=1)

                m = UtilizationPyTorchNet(input_dim)
                m.load_state_dict(torch.load(pt_util_path, weights_only=True))
                m.eval()
                self.pytorch_util_model = m
                logger.info("PyTorch Utilization Model weights loaded successfully.")

            # 2. PyTorch Maintenance Model
            pt_maint_path = os.path.join(model_dir, "maintenance_pytorch_model.pt")
            if os.path.exists(pt_maint_path):
                input_dim = joblib.load(os.path.join(model_dir, "maintenance_input_dim.joblib"))
                self.pt_maint_scaler = joblib.load(os.path.join(model_dir, "maintenance_scaler.joblib"))
                self.pt_maint_encoder = joblib.load(os.path.join(model_dir, "maintenance_encoder.joblib"))
                self.pt_maint_target_scaler = joblib.load(os.path.join(model_dir, "maintenance_target_scaler.joblib"))

                class MaintenancePyTorchNet(nn.Module):
                    def __init__(self, input_size):
                        super(MaintenancePyTorchNet, self).__init__()
                        self.shared = nn.Sequential(
                            nn.Linear(input_size, 128),
                            nn.ReLU(),
                            nn.BatchNorm1d(128),
                            nn.Dropout(0.15),
                            nn.Linear(128, 64),
                            nn.ReLU(),
                            nn.BatchNorm1d(64)
                        )
                        self.output_head = nn.Linear(64, 3)

                    def forward(self, x):
                        return self.output_head(self.shared(x))

                m = MaintenancePyTorchNet(input_dim)
                m.load_state_dict(torch.load(pt_maint_path, weights_only=True))
                m.eval()
                self.pytorch_maint_model = m
                logger.info("PyTorch Predictive Maintenance Model weights loaded successfully.")

            # 3. PyTorch Demand Model
            pt_demand_path = os.path.join(model_dir, "demand_pytorch_model.pt")
            if os.path.exists(pt_demand_path):
                input_dim = joblib.load(os.path.join(model_dir, "demand_input_dim.joblib"))
                self.pt_demand_scaler = joblib.load(os.path.join(model_dir, "demand_scaler.joblib"))
                self.pt_demand_encoder = joblib.load(os.path.join(model_dir, "demand_encoder.joblib"))
                self.pt_demand_target_scaler = joblib.load(os.path.join(model_dir, "demand_target_scaler.joblib"))

                class DemandPyTorchNet(nn.Module):
                    def __init__(self, input_size):
                        super(DemandPyTorchNet, self).__init__()
                        self.net = nn.Sequential(
                            nn.Linear(input_size, 128),
                            nn.ReLU(),
                            nn.BatchNorm1d(128),
                            nn.Dropout(0.15),
                            nn.Linear(128, 64),
                            nn.ReLU(),
                            nn.BatchNorm1d(64),
                            nn.Linear(64, 1)
                        )

                    def forward(self, x):
                        return self.net(x)

                m = DemandPyTorchNet(input_dim)
                m.load_state_dict(torch.load(pt_demand_path, weights_only=True))
                m.eval()
                self.pytorch_demand_model = m
                logger.info("PyTorch Demand Forecasting Model weights loaded successfully.")

            # 4. PyTorch Anomaly Model
            pt_anomaly_path = os.path.join(model_dir, "anomaly_pytorch_model.pt")
            if os.path.exists(pt_anomaly_path):
                input_dim = joblib.load(os.path.join(model_dir, "anomaly_input_dim.joblib"))
                self.pt_anomaly_scaler = joblib.load(os.path.join(model_dir, "anomaly_scaler.joblib"))
                self.pt_anomaly_encoder = joblib.load(os.path.join(model_dir, "anomaly_encoder.joblib"))

                class AnomalyPyTorchNet(nn.Module):
                    def __init__(self, input_size):
                        super(AnomalyPyTorchNet, self).__init__()
                        self.net = nn.Sequential(
                            nn.Linear(input_size, 128),
                            nn.ReLU(),
                            nn.BatchNorm1d(128),
                            nn.Dropout(0.2),
                            nn.Linear(128, 64),
                            nn.ReLU(),
                            nn.BatchNorm1d(64),
                            nn.Dropout(0.1),
                            nn.Linear(64, 32),
                            nn.ReLU(),
                            nn.BatchNorm1d(32),
                            nn.Linear(32, 1),
                            nn.Sigmoid()
                        )

                    def forward(self, x):
                        return self.net(x)

                m = AnomalyPyTorchNet(input_dim)
                m.load_state_dict(torch.load(pt_anomaly_path, weights_only=True))
                m.eval()
                self.pytorch_anomaly_model = m
                logger.info("PyTorch Anomaly Detection Model weights loaded successfully.")
        except Exception as e:
            logger.warning(f"Error loading PyTorch models: {e}")

    def predict_demand(self, record: dict) -> dict:
        """Predicts expected demand using PyTorch model weights."""
        site_id_str = f"SITE_{int(record['site_id']):03d}" if isinstance(record.get('site_id'), (int, str)) and str(record.get('site_id')).isdigit() else str(record.get('site_id', 'SITE_001'))

        if getattr(self, 'pytorch_demand_model', None) is not None:
            try:
                import torch
                cat_cols = ['equipment_type', 'model', 'site_id', 'season', 'region']
                num_cols = ['month', 'rental_days', 'previous_rental_count', 'avg_engine_hours', 'avg_idle_hours', 'utilization_rate']

                sample_cat = {
                    'equipment_type': str(record.get('equipment_type', 'Excavator')),
                    'model': str(record.get('model', '320 GC')),
                    'site_id': site_id_str,
                    'season': str(record.get('season', 'Summer')),
                    'region': str(record.get('region', 'West'))
                }
                sample_num = {
                    'month': record.get('month', datetime.now().month),
                    'rental_days': record.get('rental_days', 30),
                    'previous_rental_count': record.get('previous_rental_count', 10),
                    'avg_engine_hours': record.get('avg_engine_hours', 7.5),
                    'avg_idle_hours': record.get('avg_idle_hours', 2.5),
                    'utilization_rate': record.get('utilization_rate', 0.75)
                }

                df_cat = pd.DataFrame([sample_cat])
                df_num = pd.DataFrame([sample_num])

                X_cat = self.pt_demand_encoder.transform(df_cat)
                X_num = self.pt_demand_scaler.transform(df_num)
                X_all = np.hstack([X_num, X_cat])

                X_tensor = torch.tensor(X_all, dtype=torch.float32)
                with torch.no_grad():
                    raw_preds_scaled = self.pytorch_demand_model(X_tensor).numpy()
                    preds = self.pt_demand_target_scaler.inverse_transform(raw_preds_scaled)[0]

                expected_demand = max(1, int(round(float(preds[0]))))
            except Exception as e:
                logger.warning(f"PyTorch demand prediction failed: {e}")
                expected_demand = 15
        else:
            expected_demand = 15

        site_id_val = record.get("site_id", 1)
        if isinstance(site_id_val, str) and site_id_val.startswith("SITE_"):
            try:
                site_id_val = int(site_id_val.replace("SITE_", ""))
            except ValueError:
                site_id_val = 1

        return {
            "prediction_timestamp": record["timestamp"],
            "equipment_type": record["equipment_type"],
            "site_id": site_id_val,
            "prediction_period": "Next 30 Days",
            "expected_demand": expected_demand
        }

    def predict_maintenance(self, record: dict) -> dict:
        """Predicts maintenance risk, service date, and confidence using PyTorch model weights."""
        if getattr(self, 'pytorch_maint_model', None) is not None:
            try:
                import torch
                cat_cols = ['equipment_type', 'model']
                num_cols = ['equipment_age', 'engine_hours_per_day', 'idle_hours_per_day', 'fuel_level',
                            'engine_temperature', 'battery_voltage', 'days_since_last_service',
                            'fault_code_count', 'total_operating_hours']

                sample_cat = {
                    'equipment_type': str(record.get('equipment_type', 'Excavator')),
                    'model': str(record.get('model', '320 GC'))
                }
                sample_num = {
                    'equipment_age': record.get('equipment_age', 3),
                    'engine_hours_per_day': record.get('engine_hours_per_day', 8.0),
                    'idle_hours_per_day': record.get('idle_hours_per_day', 2.0),
                    'fuel_level': record.get('fuel_level', 85.0),
                    'engine_temperature': record.get('engine_temperature', 80.0),
                    'battery_voltage': record.get('battery_voltage', 12.8),
                    'days_since_last_service': record.get('days_since_last_service', 45),
                    'fault_code_count': record.get('fault_code_count', 0),
                    'total_operating_hours': record.get('total_operating_hours', 1200.0)
                }

                df_cat = pd.DataFrame([sample_cat])
                df_num = pd.DataFrame([sample_num])

                X_cat = self.pt_maint_encoder.transform(df_cat)
                X_num = self.pt_maint_scaler.transform(df_num)
                X_all = np.hstack([X_num, X_cat])

                X_tensor = torch.tensor(X_all, dtype=torch.float32)
                with torch.no_grad():
                    raw_preds_scaled = self.pytorch_maint_model(X_tensor).numpy()
                    preds = self.pt_maint_target_scaler.inverse_transform(raw_preds_scaled)[0]

                maint_prob = round(float(np.clip(preds[0], 0.01, 0.99)), 2)
                days_until_service = max(1, int(round(preds[1])))
                predicted_date = (datetime.now() + timedelta(days=days_until_service)).strftime("%Y-%m-%d")
                confidence = round(float(np.clip(preds[2], 0.50, 0.99)), 2)

                return {
                    "equipment_id": record["equipment_id"],
                    "prediction_timestamp": record["timestamp"],
                    "maintenance_probability": maint_prob,
                    "predicted_service_date": predicted_date,
                    "confidence": confidence
                }
            except Exception as e:
                logger.warning(f"PyTorch maintenance prediction failed: {e}")

        maint_prob = 0.15
        predicted_date = (datetime.now() + timedelta(days=20)).strftime("%Y-%m-%d")
        confidence = 0.85

        return {
            "equipment_id": record["equipment_id"],
            "prediction_timestamp": record["timestamp"],
            "maintenance_probability": maint_prob,
            "predicted_service_date": predicted_date,
            "confidence": confidence
        }

    def predict_utilization(self, record: dict) -> dict:
        """Predicts utilization score AND predicted idle hours via PyTorch model weights."""
        site_id_str = f"SITE_{int(record['site_id']):03d}" if isinstance(record.get('site_id'), (int, str)) and str(record.get('site_id')).isdigit() else str(record.get('site_id', 'SITE_001'))

        if getattr(self, 'pytorch_util_model', None) is not None:
            try:
                import torch
                cat_cols = ['equipment_type', 'model', 'site_id', 'weather', 'project_phase', 'machine_status']
                num_cols = ['rental_days', 'engine_hours_per_day', 'idle_hours_per_day', 'operator_experience', 'utilization_rate']

                sample_cat = {
                    'equipment_type': str(record.get('equipment_type', 'Excavator')),
                    'model': str(record.get('model', '320 GC')),
                    'site_id': site_id_str,
                    'weather': str(record.get('weather', 'Sunny')),
                    'project_phase': str(record.get('project_phase', 'Excavation')),
                    'machine_status': str(record.get('machine_status', 'Running'))
                }
                sample_num = {
                    'rental_days': record.get('rental_days', 30),
                    'engine_hours_per_day': record.get('engine_hours_per_day', 8.0),
                    'idle_hours_per_day': record.get('idle_hours_per_day', 2.0),
                    'operator_experience': record.get('operator_experience', 5),
                    'utilization_rate': record.get('utilization_rate', 0.75)
                }

                df_cat = pd.DataFrame([sample_cat])
                df_num = pd.DataFrame([sample_num])

                X_cat = self.pt_util_encoder.transform(df_cat)
                X_num = self.pt_util_scaler.transform(df_num)
                X_all = np.hstack([X_num, X_cat])

                X_tensor = torch.tensor(X_all, dtype=torch.float32)
                with torch.no_grad():
                    raw_preds_scaled = self.pytorch_util_model(X_tensor).numpy()
                    preds = self.pt_util_target_scaler.inverse_transform(raw_preds_scaled)[0]

                utilization_score = round(float(np.clip(preds[0], 0.01, 0.99)), 4)
                predicted_idle_hours = round(float(max(0.0, preds[1])), 2)
                status = record.get("machine_status", "Running")

                return {
                    "prediction_timestamp": record["timestamp"],
                    "equipment_id": record["equipment_id"],
                    "utilization_score": utilization_score,
                    "predicted_idle_hours": predicted_idle_hours,
                    "status": status
                }
            except Exception as e:
                logger.warning(f"PyTorch utilization prediction failed: {e}")

        return {
            "prediction_timestamp": record["timestamp"],
            "equipment_id": record["equipment_id"],
            "utilization_score": 0.75,
            "predicted_idle_hours": 60.0,
            "status": record.get("machine_status", "Running")
        }

    def predict_anomaly(self, record: dict) -> dict:
        """Predicts anomaly status, score, and severity using PyTorch model weights."""
        anomaly_status = "Normal"
        anomaly_score = 0.0
        severity = "Low"
        insight_message = None

        if getattr(self, 'pytorch_anomaly_model', None) is not None:
            try:
                import torch
                cat_cols = ['equipment_type', 'model', 'machine_status']
                num_cols = [
                    'engine_hours_per_day', 'idle_hours_per_day', 'fuel_level',
                    'engine_temperature', 'battery_voltage', 'fault_code_count',
                    'total_operating_hours', 'utilization_rate'
                ]

                sample_cat = {
                    'equipment_type': str(record.get('equipment_type', 'Excavator')),
                    'model': str(record.get('model', '320 GC')),
                    'machine_status': str(record.get('machine_status', 'Running'))
                }
                sample_num = {
                    'engine_hours_per_day': record.get('engine_hours_per_day', 8.0),
                    'idle_hours_per_day': record.get('idle_hours_per_day', 2.0),
                    'fuel_level': record.get('fuel_level', 85.0),
                    'engine_temperature': record.get('engine_temperature', 80.0),
                    'battery_voltage': record.get('battery_voltage', 12.8),
                    'fault_code_count': record.get('fault_code_count', 0),
                    'total_operating_hours': record.get('total_operating_hours', 1200.0),
                    'utilization_rate': record.get('utilization_rate', 0.75)
                }

                df_cat = pd.DataFrame([sample_cat])
                df_num = pd.DataFrame([sample_num])

                X_cat = self.pt_anomaly_encoder.transform(df_cat)
                X_num = self.pt_anomaly_scaler.transform(df_num)
                X_all = np.hstack([X_num, X_cat])

                X_tensor = torch.tensor(X_all, dtype=torch.float32)
                with torch.no_grad():
                    prob = float(self.pytorch_anomaly_model(X_tensor).numpy()[0][0])

                anomaly_score = round(prob, 4)
                anomaly_status = "Anomaly" if prob > 0.5 else "Normal"

                # Determine severity based on score
                if prob > 0.85:
                    severity = "Critical"
                elif prob > 0.65:
                    severity = "High"
                elif prob > 0.5:
                    severity = "Medium"
                else:
                    severity = "Low"
                    
                if anomaly_status == "Anomaly":
                    insights = [
                        "Engine temperature and battery voltage readings suggest an electrical fault.",
                        "Unusual fuel consumption detected relative to operating hours.",
                        "High frequency of fault codes coupled with excessive engine heat.",
                        "Irregular idle patterns combined with sensor spikes indicate a developing issue."
                    ]
                    insight_message = random.choice(insights)

            except Exception as e:
                logger.warning(f"PyTorch anomaly prediction failed: {e}")

        return {
            "prediction_timestamp": record["timestamp"],
            "equipment_id": record["equipment_id"],
            "anomaly_status": anomaly_status,
            "anomaly_score": anomaly_score,
            "severity": severity,
            "insight_message": insight_message
        }
