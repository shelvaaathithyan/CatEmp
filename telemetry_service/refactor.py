import sys

with open('e:/Repositories/CatEmp/CatEmp/telemetry_service/telemetry_generator.py', 'r') as f:
    lines = f.readlines()

new_content = """        # Initialize realistic state for some machines dynamically
        base_configs = [
            {"equipment_id": "EX-001", "equipment_type": "Excavator", "model": "320 GC", "dealer_id": 1, "site_id": 1, "machine_status": "Running"},
            {"equipment_id": "EX-002", "equipment_type": "Excavator", "model": "336", "dealer_id": 1, "site_id": 2, "machine_status": "Idle"},
            {"equipment_id": "WL-001", "equipment_type": "Wheel Loader", "model": "950 GC", "dealer_id": 2, "site_id": 3, "machine_status": "Running"},
            {"equipment_id": "BD-001", "equipment_type": "Bulldozer", "model": "D6", "dealer_id": 1, "site_id": 1, "machine_status": "Idle"},
            {"equipment_id": "EX-003", "equipment_type": "Excavator", "model": "320 GC", "dealer_id": 1, "site_id": 4, "machine_status": "Running"},
            {"equipment_id": "EX-004", "equipment_type": "Excavator", "model": "336", "dealer_id": 2, "site_id": 5, "machine_status": "Running"},
            {"equipment_id": "WL-002", "equipment_type": "Wheel Loader", "model": "950 GC", "dealer_id": 2, "site_id": 3, "machine_status": "Idle"},
            {"equipment_id": "BD-002", "equipment_type": "Bulldozer", "model": "D6", "dealer_id": 1, "site_id": 4, "machine_status": "Running"},
            {"equipment_id": "AT-001", "equipment_type": "Articulated Truck", "model": "745", "dealer_id": 1, "site_id": 1, "machine_status": "Running"},
            {"equipment_id": "MG-001", "equipment_type": "Motor Grader", "model": "140 GC", "dealer_id": 2, "site_id": 5, "machine_status": "Running"}
        ]
        
        self.machines = []
        for cfg in base_configs:
            is_running = cfg["machine_status"] == "Running"
            cfg.update({
                "engine_hours_per_day": round(random.uniform(6.0, 10.0) if is_running else random.uniform(0.0, 2.0), 1),
                "idle_hours_per_day": round(random.uniform(1.0, 3.0) if is_running else random.uniform(4.0, 8.0), 1),
                "fuel_level": round(random.uniform(20.0, 95.0), 1),
                "engine_temperature": round(random.uniform(70.0, 95.0) if is_running else random.uniform(40.0, 60.0), 1),
                "battery_voltage": round(random.uniform(12.2, 12.8), 1),
                "total_operating_hours": round(random.uniform(500, 5000), 1),
                "gps_latitude": round(random.uniform(30.0, 45.0), 4),
                "gps_longitude": round(random.uniform(-120.0, -70.0), 4),
                "equipment_age": random.randint(1, 10),
                "days_since_last_service": random.randint(5, 180),
                "fault_code_count": random.choices([0, 1, 2, 3], weights=[80, 10, 5, 5])[0],
                "operator_experience": random.randint(1, 15),
                "weather": random.choice(["Sunny", "Cloudy", "Rainy", "Snowy"]),
                "project_phase": random.choice(["Excavation", "Foundation", "Structural", "Finishing", "Cleanup"]),
                "season": random.choice(["Spring", "Summer", "Autumn", "Winter"]),
                "region": random.choice(["North", "South", "East", "West"]),
                "rental_days": random.randint(5, 90),
                "previous_rental_count": random.randint(1, 40)
            })
            cfg["avg_engine_hours"] = round(cfg["engine_hours_per_day"] * random.uniform(0.8, 1.2), 1)
            cfg["avg_idle_hours"] = round(cfg["idle_hours_per_day"] * random.uniform(0.8, 1.2), 1)
            self.machines.append(cfg)
"""

with open('e:/Repositories/CatEmp/CatEmp/telemetry_service/telemetry_generator.py', 'w') as f:
    f.writelines(lines[:9])
    f.write(new_content)
    f.writelines(lines[291:])
