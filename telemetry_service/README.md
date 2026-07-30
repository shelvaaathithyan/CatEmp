# Telemetry Simulator Service

A standalone Python service that generates realistic synthetic telemetry every 5 minutes and sends it to the FastAPI prediction backend.

## Features

- Generates realistic machine telemetry.
- Simulates realistic behaviors for Running and Idle heavy equipment.
- Automatically pushes payloads to Demand, Maintenance, and Utilization Prediction APIs.
- Operates on a scheduled cron job using `APScheduler`.
- Supports asynchronous, non-blocking HTTP requests using `httpx`.

## Setup

1. Create and activate a virtual environment (optional but recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # Or `venv\Scripts\activate` on Windows
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the service:
   ```bash
   python main.py
   ```

## Configuration
Endpoints are configured in `config.py`. By default, they target `http://127.0.0.1:8000`. You can override the base URL by exporting the `FASTAPI_BASE_URL` environment variable.
