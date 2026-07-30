# Anomaly Detection Pipeline Specification

## 1. Overview & Business Value
The **Anomaly Detection Pipeline** continuously monitors telemetry data stream to detect operational anomalies, unusual engine temperature spikes, abnormal fuel depletion rates, electrical voltage drops, and sudden fault code bursts. By flagging irregular equipment behaviors early, operations teams can investigate root causes before major system breakdowns occur.

---

## 2. Dataset & Input Features

The model is trained on a 50,000-sample Caterpillar anomaly dataset (`Datasets/expanded_anomaly_50k.csv`).

### Categorical Features (OneHotEncoded)
- `equipment_type`: Machinery category (`Excavator`, `Wheel Loader`, `Bulldozer`, etc.)
- `model`: Caterpillar model designation (`320 GC`, `336`, `950 GC`, `966`, `D6`, `D8`, `140`, `745`, `259D3`, `420`)
- `machine_status`: Operational telemetry state (`Running`, `Idle`)

### Numerical Features (StandardScaled)
- `engine_hours_per_day`: Daily operating hours
- `idle_hours_per_day`: Daily idle hours
- `fuel_level`: Remaining fuel percentage
- `engine_temperature`: Engine operating temperature in °C
- `battery_voltage`: Electrical system voltage (11.5V – 14.5V)
- `fault_code_count`: Active diagnostic fault codes logged
- `total_operating_hours`: Total lifetime operating hours
- `utilization_rate`: Operating utilization index

### Binary Target
- `target_anomaly`: Binary classification target (`0` = Normal, `1` = Anomaly).

---

## 3. PyTorch Binary Classification Neural Network Architecture

The pipeline utilizes a deep PyTorch classifier network (`AnomalyPyTorchNet`):

```
Input Features (11 Features: 8 Numerical + 3 Categorical)
       │
[ Linear (Input_Dim ➔ 128) ] ➔ [ ReLU ] ➔ [ BatchNorm1d(128) ] ➔ [ Dropout(0.20) ]
       │
[ Linear (128 ➔ 64) ] ➔ [ ReLU ] ➔ [ BatchNorm1d(64) ] ➔ [ Dropout(0.10) ]
       │
[ Linear (64 ➔ 32) ] ➔ [ ReLU ] ➔ [ BatchNorm1d(32) ]
       │
[ Linear Layer (32 ➔ 1) ] ➔ [ Sigmoid Activation ] ➔ Anomaly Probability (0.00 – 1.00)
```

- **Loss Function**: Binary Cross Entropy Loss (`BCELoss`)
- **Optimizer**: Adam (`lr=0.001`)
- **Batch Size**: 256
- **Epochs**: 30

---

## 4. Anomaly Scoring & Severity Categorization

The predicted probability is mapped into actionable status and severity categories:

| Probability Range | Anomaly Status | Severity Level | UI Badge & Alert Action |
|---|---|---|---|
| `Prob > 0.85` | **Anomaly** | **CRITICAL** | Pulsing Red Badge + High Priority Alert |
| `0.65 < Prob ≤ 0.85` | **Anomaly** | **HIGH** | Red Badge + Alert Notification |
| `0.50 < Prob ≤ 0.65` | **Anomaly** | **MEDIUM** | Orange Badge |
| `Prob ≤ 0.50` | **Normal** | **LOW** | Green Badge |

---

## 5. Database Schema & API Integration

- **REST API Route**: `GET /api/v1/predictions/anomaly` & `POST /api/v1/predictions/anomaly`
- **Database Schema**: `anomaly_predictions` table (`id`, `equipment_id`, `prediction_timestamp`, `anomaly_status`, `anomaly_score`, `severity`)
- **Deduplication**: Dynamically deduplicated via `_enrich_and_deduplicate` to present strictly the latest anomaly evaluation per equipment.
- **Model Enrichment**: Enriches every record with `r.model` (e.g. `320 GC`) and `r.equipment_type` (e.g. `Excavator`).

---

## 6. Frontend Presentation

- Displayed on **Customer**, **Fleet Manager**, and **Dealer** prediction dashboards in the **Anomaly Detection** tab.
- Displays Equipment ID, Caterpillar Model Number, Anomaly Status, Anomaly Score Progress Ring/Bar (0–100%), Severity Level, and Timestamp.
