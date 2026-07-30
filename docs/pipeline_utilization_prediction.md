# Utilization & Exploitation Prediction Pipeline Specification

## 1. Overview & Business Value
The **Utilization Prediction Pipeline** monitors daily telemetry streams to evaluate equipment efficiency, forecast cumulative idle hours, and detect machine exploitation. By identifying severely underutilized or overutilized machinery in real-time, fleet operators can prevent premature engine wear, reduce unnecessary fuel burn, and reallocate assets to high-productivity project phases.

---

## 2. Dataset & Input Features

The model is trained on a 50,000-sample Caterpillar machine telemetry dataset (`Datasets/expanded_utilization_50k.csv`).

### Categorical Features (OneHotEncoded)
- `equipment_type`: Machine category (`Excavator`, `Wheel Loader`, `Bulldozer`, `Articulated Truck`, etc.)
- `model`: Caterpillar model (`320 GC`, `336`, `950 GC`, `966`, `D6`, `D8`, `140`, `745`, `259D3`, `420`)
- `site_id`: Active construction site (`SITE_001` to `SITE_050`)
- `weather`: Ambient weather condition (`Sunny`, `Cloudy`, `Rainy`)
- `project_phase`: Site construction phase (`Excavation`, `Foundation`, `Structural`, `Finishing`, `Clearing`)
- `machine_status`: Operational telemetry state (`Running`, `Idle`)

### Numerical Features (StandardScaled)
- `rental_days`: Active contract duration in days
- `engine_hours_per_day`: Daily productive operating hours
- `idle_hours_per_day`: Daily non-productive idle hours
- `operator_experience`: Operator experience rating in years (1–15)
- `utilization_rate`: Direct ratio `engine_hours / (engine_hours + idle_hours)`

### Multi-Output Targets
1. `target_utilization_score`: Continuous utilization index (0.01 – 0.99)
2. `target_predicted_idle_hours`: Forecasted 30-day cumulative idle hours

---

## 3. PyTorch Multi-Head Neural Network Architecture

The pipeline utilizes a **Multi-Head PyTorch Neural Network** (`UtilizationPyTorchNet`) to simultaneously predict utilization score and idle hours:

```
                  Input Features (Numerical + Categorical)
                                    │
               [ Linear (Input_Dim ➔ 128) ] ➔ [ ReLU ] ➔ [ BatchNorm ] ➔ [ Dropout(0.15) ]
                                    │
               [ Linear (128 ➔ 64) ] ➔ [ ReLU ] ➔ [ BatchNorm(64) ] (Shared Feature Vector)
                                ┌───┴───┐
                                ▼       ▼
                   [ Head 1: Score ]   [ Head 2: Idle Hours ]
                   Linear(64 ➔ 32)      Linear(64 ➔ 32)
                   Linear(32 ➔ 1)       Linear(32 ➔ 1)
```

- **Loss Function**: Multi-Task Composite MSE Loss (`Loss = Score_Loss + 0.01 * Idle_Loss`)
- **Optimizer**: Adam (`lr=0.001`)

---

## 4. Exploitation Detection & Real-Time Alerting Workflow

1. Telemetry data is ingested via `POST /api/v1/predictions/utilization`.
2. The PyTorch model computes `utilization_score`.
3. **Threshold Check**: If `utilization_score > 0.90` (90% capacity), the backend automatically generates a **HIGH Priority Machine Overutilization Alert**.
4. The alert payload is published to **RabbitMQ**, broadcasting real-time notification warnings to both the Dealer and Fleet Manager to prevent machine damage or contract exploitation.

---

## 5. Database Schema & API Integration

- **REST API Route**: `GET /api/v1/predictions/utilization` & `POST /api/v1/predictions/utilization`
- **Database Schema**: `utilization_predictions` table (`id`, `prediction_timestamp`, `equipment_id`, `utilization_score`, `predicted_idle_hours`, `status`)
- **Deduplication & Scoping**:
  - `_enrich_and_deduplicate` ensures only the single latest prediction per machine is returned.
  - Dynamically attaches `r.model` (e.g. `320 GC`) from the `Machine` table.
  - Scoped strictly to `ACTIVE` rentals for Customers/Fleet Managers and `RENTED` status for Dealers.

---

## 6. Frontend Presentation

- Displayed on **Customer**, **Fleet Manager**, and **Dealer** prediction dashboards.
- Features custom progress bars and status badges (Green: Healthy 40–85%, Yellow: Underutilized < 40%, Red: Overutilized > 90%).
