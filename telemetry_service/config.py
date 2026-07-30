import os

# API Configuration
FASTAPI_BASE_URL = os.getenv("FASTAPI_BASE_URL", "http://127.0.0.1:8000")
DEMAND_ENDPOINT = f"{FASTAPI_BASE_URL}/api/v1/predictions/demand"
MAINTENANCE_ENDPOINT = f"{FASTAPI_BASE_URL}/api/v1/predictions/maintenance"
UTILIZATION_ENDPOINT = f"{FASTAPI_BASE_URL}/api/v1/predictions/utilization"

# Scheduler Configuration
SCHEDULER_INTERVAL_MINUTES = int(os.getenv("SCHEDULER_INTERVAL_MINUTES", "5"))
