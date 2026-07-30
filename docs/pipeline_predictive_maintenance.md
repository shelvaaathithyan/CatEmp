# Predictive Maintenance Pipeline Specification

## 1. Overview & Business Value
The **Predictive Maintenance Pipeline** leverages machinery telemetry and historical service records to estimate equipment breakdown risk, calculate recommended service dates, and provide confidence metrics. This enables proactive maintenance scheduling prior to catastrophic mechanical failures, extending machine asset lifespans and reducing emergency downtime costs.

---

## 2. Dataset & Input Features

The model is trained on a 50,000-sample Caterpillar maintenance dataset (`Datasets/expanded_maintenance_50k.csv`).

### Categorical Features (OneHotEncoded)
- `equipment_type`: Machinery type (`Excavator`, `Wheel Loader`, `Bulldozer`, etc.)
- `model`: Caterpillar model (`320 GC`, `336`, `950 GC`, `966`, `D6`, `D8`, `140`, `745`, `259D3`, `420`)

### Numerical Features (StandardScaled)
- `equipment_age`: Machine age in years (1–12)
- `engine_hours_per_day`: Daily productive operating hours
- `idle_hours_per_day`: Daily idle hours
- `fuel_level`: Remaining fuel percentage (10–100%)
- `engine_temperature`: Engine operating temperature in °C
- `battery_voltage`: Electrical system voltage (11.5V – 14.5V)
- `days_since_last_service`: Elapsed days since last scheduled maintenance
- `fault_code_count`: Active diagnostic fault codes logged (0–8)
- `total_operating_hours`: Cumulative total lifetime operating hours (500 – 12,000 hrs)

### Multi-Output Targets
1. `target_maintenance_probability`: Probability score (0.01 – 0.99) representing failure risk.
2. `target_days_until_service`: Predicted number of days remaining until mandatory maintenance.
3. `target_confidence`: Statistical confidence score (0.50 – 0.99).

---

## 3. PyTorch Neural Network Architecture

The pipeline utilizes a multi-output PyTorch network (`MaintenancePyTorchNet`):

```
Input Features (11 Features: 9 Numerical + 2 Categorical)
       │
[ Linear (Input_Dim ➔ 128) ] ➔ [ ReLU ] ➔ [ BatchNorm1d(128) ] ➔ [ Dropout(0.15) ]
       │
[ Linear (128 ➔ 64) ] ➔ [ ReLU ] ➔ [ BatchNorm1d(64) ]
       │
[ Output Layer: Linear(64 ➔ 3) ] ➔ [ Probability, Days_Until_Service, Confidence ]
```

- **Loss Function**: Multi-Task MSE Loss
- **Optimizer**: Adam (`lr=0.001`)

---

## 4. Risk Level Thresholds & Notification Triggers

- **HIGH Risk (Probability ≥ 70%)**: Triggered in red badge. Automatically generates a high-priority Maintenance Alert.
- **MEDIUM Risk (40% ≤ Probability < 70%)**: Triggered in orange badge.
- **LOW Risk (Probability < 40%)**: Triggered in green badge.

---

## 5. Database Schema & API Integration

- **REST API Route**: `GET /api/v1/predictions/maintenance` & `POST /api/v1/predictions/maintenance`
- **Database Schema**: `maintenance_predictions` table (`id`, `equipment_id`, `prediction_timestamp`, `maintenance_probability`, `predicted_service_date`, `confidence`)
- **Deduplication**: Automatically deduplicated to return strictly the single latest maintenance prediction per active machine.
- **Model Enrichment**: Populates `model` (e.g. `320 GC`) and `equipment_type` (e.g. `Excavator`) dynamically from `Machine`.

---

## 6. Frontend Presentation

- Displayed on **Customer**, **Fleet Manager**, and **Dealer** prediction dashboards under the **Maintenance** tab.
- Formatted with color-coded risk pills, calculated service date, confidence percentage, and Caterpillar Model numbers.
