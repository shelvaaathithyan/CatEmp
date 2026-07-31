# Anomaly Detection Pipeline Specification

## 1. Overview & Business Value
The **Anomaly Detection Pipeline** continuously monitors telemetry data streams to detect operational anomalies and **asset misuse**. It identifies:
- **Sensor anomalies**: Engine temperature spikes, abnormal fuel depletion, electrical voltage drops, fault code bursts
- **Asset misuse**: Long idle hours (equipment sitting unused), very low utilization rates (unassigned/abandoned equipment)

By flagging irregular equipment behaviors early, operations teams can investigate root causes before major breakdowns or rental contract violations occur.

> **Challenge Requirement**: *"Use the historical data to detect any misuse of assets e.g.) long idle hours, unassigned equipment etc."*

---

## 2. Dataset & Input Features

The model is trained on a 50,000-sample Caterpillar anomaly dataset (`Datasets/expanded_anomaly_50k.csv`) with a **bimodal distribution** (75% normal operating / 25% stressed/misused machines) producing ~37% anomaly rate.

### Categorical Features (OneHotEncoded)
- `equipment_type`: Machinery category (`Excavator`, `Wheel Loader`, `Bulldozer`, etc.)
- `model`: Caterpillar model designation (`320 GC`, `336`, `950 GC`, `966`, `D6`, `D8`, `140`, `745`, `259D3`, `420`, etc.)
- `machine_status`: Operational telemetry state (`Running`, `Idle`)

### Numerical Features (StandardScaled)
- `engine_hours_per_day`: Daily operating hours
- `idle_hours_per_day`: Daily idle hours (**key misuse indicator**)
- `fuel_level`: Remaining fuel percentage
- `engine_temperature`: Engine operating temperature in °C
- `battery_voltage`: Electrical system voltage (11.5V – 14.5V)
- `fault_code_count`: Active diagnostic fault codes logged
- `total_operating_hours`: Total lifetime operating hours
- `utilization_rate`: Operating utilization index (**key misuse indicator**)

### Binary Target
- `target_anomaly`: Binary classification target (`0` = Normal, `1` = Anomaly)

---

## 3. Anomaly Classification Rules

A sample is labeled as **Anomaly** if ANY of these model-specific conditions are met:

| Rule | Description | Example Threshold (CAT 320 GC) |
|---|---|---|
| Engine Overheating | `engine_temperature > temp_max` | > 100°C |
| Low Battery | `battery_voltage < volt_min` | < 12.0V |
| Excess Fault Codes | `fault_code_count >= fault_threshold` | >= 4 codes |
| Critical Low Fuel | `fuel_level < fuel_min` | < 12% |
| **Long Idle Hours** | `idle_hours_per_day > idle_max` | **> 8.0 hrs** |
| **Unassigned/Abandoned** | `utilization_rate < 0.15` | **< 15%** |

> Each of the 29 CAT models has its own specific thresholds (e.g., heavy machines like D8/D10 tolerate higher temps but lower idle thresholds).

---

## 4. PyTorch Binary Classification Neural Network Architecture

```
Input Features (49 Features: 8 Numerical + 3 Categorical OneHot → 49 dims)
       │
[ Linear (49 ➔ 128) ] ➔ [ ReLU ] ➔ [ BatchNorm1d(128) ] ➔ [ Dropout(0.20) ]
       │
[ Linear (128 ➔ 64) ] ➔ [ ReLU ] ➔ [ BatchNorm1d(64) ] ➔ [ Dropout(0.10) ]
       │
[ Linear (64 ➔ 32) ] ➔ [ ReLU ] ➔ [ BatchNorm1d(32) ]
       │
[ Linear (32 ➔ 1) ] ➔ [ Sigmoid ] ➔ Anomaly Probability (0.00 – 1.00)
```

- **Loss Function**: Binary Cross Entropy Loss (`BCELoss`)
- **Optimizer**: Adam (`lr=0.002`, `weight_decay=1e-4`)
- **LR Scheduler**: StepLR (step=15, gamma=0.5)
- **Batch Size**: 256
- **Epochs**: 50
- **Test Accuracy**: **99.78%** (TN=6,266, FP=17, FN=5, TP=3,712)

---

## 5. Anomaly Scoring & Severity Categorization

| Probability Range | Anomaly Status | Severity Level | Alert Action |
|---|---|---|---|
| `Prob > 0.85` | **Anomaly** | **CRITICAL** | 🔴 RabbitMQ HIGH Alert → Dealer + Fleet Manager |
| `0.65 < Prob ≤ 0.85` | **Anomaly** | **HIGH** | 🔴 RabbitMQ HIGH Alert → Dealer + Fleet Manager |
| `0.50 < Prob ≤ 0.65` | **Anomaly** | **MEDIUM** | 🟠 Logged, visible in dashboard |
| `Prob ≤ 0.50` | **Normal** | **LOW** | 🟢 Normal operation |

---

## 6. Real-Time Alert Pipeline

When the anomaly model detects a HIGH or CRITICAL severity:

```
Telemetry → ML Predictor → POST /api/v1/predictions/anomaly
                                      │
                           severity == HIGH or CRITICAL?
                                      │ YES
                                      ▼
                           RabbitMQ Alert Published
                           ├── Fleet Manager notification
                           └── Dealer notification
                                      │
                                      ▼
                           WebSocket Push → Real-time UI Alert
```

The alert message includes: Equipment ID, Anomaly Status, Score, Severity, and actionable guidance ("check for long idle hours or sensor failures").

---

## 7. Database Schema & API Integration

- **REST API Route**: `GET /api/v1/predictions/anomaly` & `POST /api/v1/predictions/anomaly`
- **Database Schema**: `anomaly_predictions` table (`id`, `equipment_id`, `prediction_timestamp`, `anomaly_status`, `anomaly_score`, `severity`)
- **Deduplication**: `_enrich_and_deduplicate` returns strictly the latest anomaly evaluation per equipment
- **Model Enrichment**: Enriches every record with `model` (e.g. `320 GC`) and `equipment_type` (e.g. `Excavator`)

---

## 8. Frontend Presentation

- Displayed on **Customer**, **Fleet Manager**, and **Dealer** prediction dashboards in the **Anomaly Detection** tab
- Shows: Equipment ID, CAT Model Number, Anomaly Status, Score (progress bar 0–100%), Severity Badge, Timestamp
