# Caterpillar Smart Rental Tracking System 🚜⚡

An enterprise-grade, AI-driven equipment tracking and rental management platform built for **Caterpillar**. The system integrates real-time IoT telemetry, four **PyTorch Machine Learning models**, strict multi-tenant role-based data isolation, QR-code physical verification, and automated exploitation prevention.

---

## 🌟 Key Features & Unique Selling Points

- **🤖 4-Model PyTorch ML Engine**: Deep Neural Networks for Demand Forecasting, Utilization & Exploitation Prediction, Predictive Maintenance, and Anomaly Detection.
- **🛡️ Strict Multi-Tenant Data Isolation**: Role-based scoping ensures Dealers, Customers, and Fleet Managers only access equipment and telemetry relevant to their active contracts.
- **📱 QR Scanner & Physical Check-In**: Built-in webcam scanner and image reader (`html5-qrcode`) for logging machine arrivals/departures with real-time operator assignment.
- **🚨 Overutilization & Exploitation Alerts**: Real-time RabbitMQ notification triggers when a machine's utilization exceeds 90%.
- **📊 Global Single-Row Deduplication**: Clean dashboard presentation displaying strictly the **latest prediction snapshot per machine** across all role views.
- **🏷️ Caterpillar Model Mapping**: Full support for Caterpillar model designations (`CAT 320 GC`, `CAT 950 GC`, `CAT D6 LMT`, `CAT 777 OHT`, `CAT 745 LMT`).

---

## 🛠️ Summary of Schema & Table Enhancements

Below is a detailed log of the structural and API schema changes implemented in this version:

### 1. Prediction Tables & Schemas (`backend/app/schemas/predictions.py`)
- **Added `model` and `equipment_type` fields** to `UtilizationPredictionResponse`, `MaintenancePredictionResponse`, `DemandPredictionResponse`, and `AnomalyPredictionResponse`.
- **Backend Service Layer (`backend/app/services/predictions.py`)**: Implemented `_enrich_and_deduplicate` to dynamically query the `Machine` model table and populate `r.model` (e.g. `320 GC`) and `r.equipment_type` (e.g. `Excavator`) for every prediction record.

### 2. Prediction Deduplication Logic (`predictions.py`)
- Replaced historical query dumps with **single-row latest snapshot deduplication**.
- Predictions are grouped by `equipment_id` (or `equipment_type` + `site_id` for demand), returning only the most recent forecast to keep UI tables clean and actionable.

### 3. Data Isolation Scoping (`backend/app/routers/rental.py`)
- Fixed `GET /api/v1/rentals/` to strictly filter returned contracts by `current_user.role`:
  - **Customers**: Filtered by `Rental.customer_id == customer.id`.
  - **Fleet Managers**: Filtered by `Rental.fleet_manager_id == fm.id`.
  - **Dealers**: Filtered by `Rental.equipment_id.in_(dealer_machines)`.
- Eliminates cross-tenant data leakage between dealers and customers.

### 4. Operator Table Integration during Check-In (`FleetCheckin.jsx`, `operators.py`)
- Added **Operator Registration & Assignment** directly into the QR Check-in modal.
- Fleet Managers can select an existing operator or register a new operator (`operator_id`, `operator_name`), linking the operator table directly to the check-in audit log.

### 5. Corrected Anomaly UI Schema Mapping
- Fixed table columns across `CustomerPredictions.jsx`, `FleetPredictions.jsx`, and `DealerPredictions.jsx` to map to actual API fields (`anomaly_score` and `severity`) instead of CSV training attributes.

---

## 🚀 Quickstart Guide

### 1. Start RabbitMQ (Message Broker)
```bash
docker run -d --name rabbitmq -p 5672:5672 -p 15672:15672 rabbitmq:3-management
```
*(Management UI available at `http://localhost:15672` — `guest` / `guest`).*

### 2. Start the Backend (FastAPI)
```bash
cd backend
# Activate virtual environment
.\venv\Scripts\Activate.ps1   # Windows
source venv/bin/activate      # Mac/Linux

uvicorn app.main:app --reload --port 8000
```
*(API Docs available at `http://127.0.0.1:8000/docs`).*

### 3. Start the Frontend (React / Vite)
```bash
cd frontend
npm install
npm run dev
```
*(Application UI available at `http://localhost:5173`).*

### 4. Start Telemetry Simulation Service (Optional)
```bash
cd telemetry_service
python scheduler.py
```

---

## 🔑 Seeded Demo Credentials

| Role | Email | Password | Scope / Permissions |
|---|---|---|---|
| **Cat Admin** | `admin@cat.com` | `password123` | Global system control |
| **Dealer 1** | `dealer1@cat.com` | `password123` | Caterpillar Global fleet |
| **Dealer 2** | `dealer2@cat.com` | `password123` | Regional Cat Rentals fleet |
| **Customer (Charlie)** | `customer1@cat.com` | `password123` | Mega Construction Inc. |
| **Customer (Diana)** | `customer2@cat.com` | `password123` | BuildIt Right Corp. |
| **Fleet Manager** | `fleet1@cat.com` | `password123` | Downtown Skyscraper Site |

---

## 📂 Project Structure

```
CatEmp/
├── backend/                  # FastAPI Application
│   ├── app/
│   │   ├── core/            # Database, Security, RabbitMQ, Scheduler config
│   │   ├── models/          # SQLAlchemy ORM Database Models
│   │   ├── routers/         # REST API Route Controllers
│   │   ├── schemas/         # Pydantic Data Validation Schemas
│   │   └── services/        # Business Logic & ML Service Integrations
│   └── seed_db.py           # Database Seeder
├── frontend/                 # React (Vite) Web Application
│   ├── src/
│   │   ├── api.js           # Axios API Client
│   │   ├── components/      # Reusable Cards, Tables, Navbars
│   │   └── pages/           # Role-based Dashboards & Views
├── ml_prediction/            # PyTorch Models & Training Scripts
├── telemetry_service/        # Telemetry Generator & ML Predictor
├── SystemDesign.md           # System Architecture & Design Spec
└── README.md                 # Project Overview & Setup Guide
```
