# Caterpillar Smart Rental Tracking System — System Architecture & Design Document

## 1. Executive Summary & Core Objective
The **Caterpillar Smart Rental Tracking System** is an end-to-end, AI-powered platform designed to optimize heavy equipment rental operations across **Dealers**, **Customers**, and **Fleet Managers**. By combining real-time IoT telemetry, PyTorch machine learning models, strict role-based data isolation, and physical QR/RFID verification, the system provides total operational visibility, proactive maintenance, and automated exploitation prevention.

---

## 2. Technology Stack & Infrastructure

| Layer | Technologies & Tools |
|---|---|
| **Backend API** | **FastAPI** (Python 3.14), Uvicorn async ASGI server |
| **Database & ORM** | **PostgreSQL**, **SQLAlchemy** ORM, Alembic migrations |
| **Machine Learning** | **PyTorch** (Deep Neural Networks), Scikit-Learn, Joblib |
| **Frontend UI** | **React** (Vite), Vanilla CSS design system, Recharts |
| **Event Bus & Messaging** | **RabbitMQ** (AMQP message broker for real-time alerts) |
| **Task Scheduling** | **APScheduler** (Background cron jobs for overdue checks) |
| **Real-Time Communication** | **FastAPI WebSockets** for push notifications |
| **Physical Verification** | **HTML5 QR Code Scanner** (Webcam & Image Upload parser) |

---

## 3. System Architecture & Component Interaction

```
[ Frontend (React/Vite) ] 
       │  ▲
 HTTP  │  │ WebSockets / QR Scan
       ▼  │
[ FastAPI Backend ] ─── (APScheduler) ───► [ Overdue Rental Cron Job ]
       │  ▲
       │  │ ORM Queries
       ▼  │
[ PostgreSQL DB ] ◄─── [ PyTorch ML Pipeline ] ───► [ RabbitMQ Event Bus ]
                            (4 Models)                (Real-time Overutilization Alerts)
```

---

## 4. Machine Learning Services (PyTorch Deep Learning Engine)

The platform integrates **four specialized PyTorch neural networks** running in parallel:

### A. Demand Forecasting Model
- **Input Features**: `equipment_type`, `model`, `site_id`, `season`, `region`, `month`, `avg_engine_hours`
- **Output**: Expected monthly demand count per equipment type and site.
- **Enrichment**: Displays Caterpillar model numbers (`CAT 320 GC`, `CAT 950 GC`, `CAT D6 LMT`, `CAT 777 OHT`).

### B. Utilization & Exploitation Prediction Model
- **Input Features**: `rental_days`, `engine_hours_per_day`, `idle_hours_per_day`, `operator_experience`
- **Outputs**:
  1. `utilization_score` (0–100%)
  2. `predicted_idle_hours`
  3. `status` (`Running`, `Idle`, `Overutilized`)
- **Automated Exploitation Alert**: When `utilization_score > 0.90`, an instant **HIGH priority Overutilization Alert** is pushed to RabbitMQ for Dealer and Fleet Manager intervention.

### C. Predictive Maintenance Model
- **Input Features**: `equipment_age`, `engine_temperature`, `battery_voltage`, `days_since_last_service`, `fault_code_count`
- **Outputs**: `maintenance_probability` (Risk % level), `predicted_service_date`, `confidence` score.

### D. Anomaly Detection Model
- **Architecture**: Deep Neural Network Classifier with Sigmoid output.
- **Outputs**: `anomaly_status` (`Normal` vs `Anomaly`), `anomaly_score` (0–100%), `severity` (`LOW`, `MEDIUM`, `HIGH`, `CRITICAL`).

---

## 5. Security & Role-Based Data Isolation Architecture

To prevent cross-tenant data leakage, strict data isolation is enforced across both REST APIs and ML Prediction services:

| Role | Permitted Access & Data Boundaries |
|---|---|
| **CatAdmin** | Unrestricted global access across all dealers, customers, sites, and ML predictions. |
| **Dealer** | Scoped strictly to equipment owned by the dealer. Predictions are filtered to machines with `status == "RENTED"`. Dealer 1 cannot view Dealer 2's customers or telemetry. |
| **Customer** | Scoped strictly to active rentals linked to their `customer_id`. Cannot view other customer's equipment or predictions. |
| **Fleet Manager** | Scoped strictly to the active machines operating on their assigned `site_id`. |

---

## 6. Physical Equipment Check-In / Check-Out & Operator Tracking

1. **QR & Image Upload Scanner**: Integrated into `FleetCheckin.jsx` using `html5-qrcode`. Fleet Managers can scan physical machine QR codes using a device camera or upload a QR image.
2. **Operator Assignment**: Upon checking in a machine, the Fleet Manager can assign an existing operator or register a new operator (`operator_name`, `operator_id`), maintaining an unbroken audit chain between machines and operators.
3. **Machine Transfers**: Site-to-site machine transfers update rental site associations in real time and trigger notification alerts to the customer.

---

## 7. Global Data Presentation & Deduplication Strategy

- **Single-Row Latest Prediction Deduplication**: To eliminate noisy historical telemetry snapshots, prediction endpoints (`/predictions/*`) execute dynamic Python-level deduplication (`_enrich_and_deduplicate`), returning only the **single latest prediction per machine**.
- **Model Number Enrichment**: Every prediction record automatically resolves and displays the exact Caterpillar Model (e.g., `CAT 320 GC`, `CAT 950 GC`, `CAT D6 LMT`, `CAT 777 OHT`).

---

## 8. Summary of Milestones Completed

- [x] **Milestone 1**: System Architecture & Role-Based Access Scoping.
- [x] **Milestone 2**: Normalized PostgreSQL Database Schema & SQLAlchemy ORM mapping.
- [x] **Milestone 3**: Training and validation of PyTorch Models (Demand, Utilization, Maintenance, Anomaly).
- [x] **Milestone 4**: FastAPI REST API Layer, Authentication, and RabbitMQ / APScheduler integration.
- [x] **Milestone 5**: Role-based Frontend Dashboards with Recharts, QR Scanner, and Data Isolation.
- [x] **Milestone 6**: End-to-End System Testing, Bug Fixes (Deduplication, Active Rental filtering, Operator creation).
- [x] **Milestone 7**: System Design Specification & Complete Chat Documentation.