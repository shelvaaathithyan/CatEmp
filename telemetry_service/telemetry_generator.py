import random
from datetime import datetime, timezone
import uuid
from ml_predictor import MLPredictor
from typing import List, Dict

class TelemetryGenerator:
    def __init__(self):
        self.predictor = MLPredictor()
        # Initialize realistic state for some machines
        self.machines = [
            {
                "equipment_id": "EX-001",
                "equipment_type": "Excavator",
                "model": "320 GC",
                "dealer_id": 1,
                "site_id": 1,
                "engine_hours_per_day": 8.5,
                "idle_hours_per_day": 2.0,
                "fuel_level": 90.0,
                "engine_temperature": 85.0,
                "battery_voltage": 12.8,
                "total_operating_hours": 1250.0,
                "machine_status": "Running",
                "gps_latitude": 34.0522,
                "gps_longitude": -118.2437,
                "equipment_age": 3,
                "days_since_last_service": 45,
                "fault_code_count": 0,
                "operator_experience": 5,
                "weather": "Sunny",
                "project_phase": "Excavation",
                "season": "Summer",
                "region": "West",
                "rental_days": 30,
                "previous_rental_count": 12,
                "avg_engine_hours": 7.5,
                "avg_idle_hours": 2.5
            },
            {
                "equipment_id": "EX-002",
                "equipment_type": "Excavator",
                "model": "336",
                "dealer_id": 1,
                "site_id": 2,
                "engine_hours_per_day": 1.0,
                "idle_hours_per_day": 6.5,
                "fuel_level": 45.0,
                "engine_temperature": 65.0,
                "battery_voltage": 12.2,
                "total_operating_hours": 3400.0,
                "machine_status": "Idle",
                "gps_latitude": 40.7128,
                "gps_longitude": -74.0060,
                "equipment_age": 7,
                "days_since_last_service": 120,
                "fault_code_count": 2,
                "operator_experience": 2,
                "weather": "Rainy",
                "project_phase": "Foundation",
                "season": "PostMonsoon",
                "region": "East",
                "rental_days": 15,
                "previous_rental_count": 25,
                "avg_engine_hours": 4.5,
                "avg_idle_hours": 5.0
            },
            {
                "equipment_id": "WL-001",
                "equipment_type": "Wheel Loader",
                "model": "950 GC",
                "dealer_id": 2,
                "site_id": 3,
                "engine_hours_per_day": 7.0,
                "idle_hours_per_day": 1.5,
                "fuel_level": 80.0,
                "engine_temperature": 80.0,
                "battery_voltage": 12.5,
                "total_operating_hours": 1800.0,
                "machine_status": "Running",
                "gps_latitude": 41.8781,
                "gps_longitude": -87.6298,
                "equipment_age": 4,
                "days_since_last_service": 60,
                "fault_code_count": 1,
                "operator_experience": 4,
                "weather": "Cloudy",
                "project_phase": "Structural",
                "season": "Winter",
                "region": "North",
                "rental_days": 20,
                "previous_rental_count": 18,
                "avg_engine_hours": 6.5,
                "avg_idle_hours": 3.0
            },
            {
                "equipment_id": "BD-001",
                "equipment_type": "Bulldozer",
                "model": "D6",
                "dealer_id": 1,
                "site_id": 1,
                "engine_hours_per_day": 6.0,
                "idle_hours_per_day": 2.0,
                "fuel_level": 70.0,
                "engine_temperature": 75.0,
                "battery_voltage": 12.6,
                "total_operating_hours": 2100.0,
                "machine_status": "Idle",
                "gps_latitude": 29.7604,
                "gps_longitude": -95.3698,
                "equipment_age": 5,
                "days_since_last_service": 90,
                "fault_code_count": 0,
                "operator_experience": 8,
                "weather": "Sunny",
                "project_phase": "Clearing",
                "season": "Summer",
                "region": "South",
                "rental_days": 40,
                "previous_rental_count": 30,
                "avg_engine_hours": 7.0,
                "avg_idle_hours": 2.0
            }
        ]

    def _evolve_running(self, machine: dict):
        machine["engine_hours_per_day"] += random.uniform(0.05, 0.1)
        machine["total_operating_hours"] += random.uniform(0.05, 0.1)
        machine["fuel_level"] = max(0.0, machine["fuel_level"] - random.uniform(0.5, 2.0))
        machine["engine_temperature"] = min(105.0, max(75.0, machine["engine_temperature"] + random.uniform(-1.0, 3.0)))
        machine["battery_voltage"] = round(random.uniform(13.5, 14.2), 1)
        machine["gps_latitude"] += random.uniform(-0.00005, 0.00005)
        machine["gps_longitude"] += random.uniform(-0.00005, 0.00005)

    def _evolve_idle(self, machine: dict):
        machine["idle_hours_per_day"] += random.uniform(0.05, 0.1)
        machine["fuel_level"] = max(0.0, machine["fuel_level"] - random.uniform(0.05, 0.2))
        machine["engine_temperature"] = max(60.0, machine["engine_temperature"] - random.uniform(1.0, 3.0))
        machine["battery_voltage"] = round(random.uniform(12.0, 12.6), 1)

    def generate_telemetry(self) -> List[Dict]:
        records = []
        for machine in self.machines:
            # Evolve states based on rules
            if machine["machine_status"] == "Running":
                self._evolve_running(machine)
                if random.random() < 0.1:  # 10% chance to become Idle
                    machine["machine_status"] = "Idle"
            else:
                self._evolve_idle(machine)
                if random.random() < 0.3:  # 30% chance to start Running
                    machine["machine_status"] = "Running"
            
            # Calculate utilization rate
            total_hours = machine["engine_hours_per_day"] + machine["idle_hours_per_day"]
            util_rate = machine["engine_hours_per_day"] / total_hours if total_hours > 0 else 0.0
            machine["utilization_rate"] = round(util_rate, 4)

            # Assign timestamp and dynamic month
            machine["timestamp"] = datetime.now(timezone.utc).isoformat()
            machine["month"] = datetime.now().month

            records.append(machine.copy())
            
        return records

    def build_demand_payload(self, record: dict) -> dict:
        return self.predictor.predict_demand(record)

    def build_maintenance_payload(self, record: dict) -> dict:
        return self.predictor.predict_maintenance(record)

    def build_utilization_payload(self, record: dict) -> dict:
        return self.predictor.predict_utilization(record)

    def build_anomaly_payload(self, record: dict) -> dict:
        return self.predictor.predict_anomaly(record)

