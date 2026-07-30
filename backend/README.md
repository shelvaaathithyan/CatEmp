# Caterpillar Smart Rental Tracking System Backend

This repository contains the FastAPI backend for the Smart Rental Tracking System, designed with a clean, modular, and layered architecture. 

It uses PostgreSQL for data persistence and SQLAlchemy for ORM modeling.

## Architecture

The application is structured into the following layers:
- **Routers (`app/routers/`)**: Defines the RESTful API endpoints and handles HTTP requests/responses.
- **Services (`app/services/`)**: Contains the core business logic, including validations and transaction orchestration.
- **Repositories (`app/repositories/`)**: Manages direct database queries and CRUD operations.
- **Schemas (`app/schemas/`)**: Pydantic models for request validation and response serialization.
- **Models (`app/models/`)**: SQLAlchemy definitions corresponding exactly to the database schema.
- **Core (`app/core/`)**: Configuration, database connection setup, security (JWT, hashing), and dependencies.

## Features

- **RBAC Authentication**: Secure JWT-based authentication supporting four distinct roles: `CatAdmin`, `Dealer`, `Customer`, `Fleet Manager`.
- **Modular Design**: File structure split logically to prevent overly large code files, making the codebase maintainable and readable.
- **Rental Lifecycle**: Supports the entire rental process including creation, active tracking, site transfers, and QR/RFID check-in/out events.
- **Historical Immutability**: All equipment usage, maintenance, and predictions are stored in append-only tables to maintain a permanent record.
- **Machine Timeline Audit**: A robust endpoint that aggregates all events for a machine into a single, chronologically sorted timeline payload.
- **ML Predictions Integration**: Provides REST APIs for injecting Demand, Utilization, and Maintenance prediction data from external ML services.

## Local Setup

### 1. Prerequisites
- Python 3.8+
- PostgreSQL database (e.g. Render)

### 2. Environment Configuration
Create a `.env` file in the root directory by copying `.env.example`:
```bash
cp .env.example .env
```
Fill in the `DATABASE_URL` with your PostgreSQL connection string and define a secure `SECRET_KEY`.

### 3. Install Dependencies
Set up a virtual environment and install the required packages:
```bash
python -m venv venv
# Windows:
.\venv\Scripts\Activate.ps1
# Linux/Mac:
source venv/bin/activate

pip install -r requirements.txt
```

### 4. Database Migrations
Initialize the database tables using Alembic:
```bash
alembic upgrade head
```

### 5. Start RabbitMQ (Optional but required for Notifications)
The backend uses RabbitMQ to process real-time notifications asynchronously. You can spin up a local instance easily using Docker:
```bash
docker run -d --name rabbitmq -p 5672:5672 -p 15672:15672 rabbitmq:3-management
```
The web dashboard will be available at `http://localhost:15672` (login: `guest`/`guest`).

### 6. Running the Application
Start the FastAPI server via Uvicorn:
```bash
uvicorn app.main:app --reload
```
Once started, navigate to `http://127.0.0.1:8000/api/v1/openapi.json` to view the raw OpenAPI spec, or `http://127.0.0.1:8000/docs` to interact with the interactive Swagger UI.
