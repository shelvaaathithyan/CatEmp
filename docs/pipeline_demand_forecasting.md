# Demand Forecasting Pipeline Specification

## 1. Overview & Business Value
The **Demand Forecasting Pipeline** predicts upcoming regional and site-level equipment rental demand for Caterpillar machinery over a 30-day forecast horizon. This enables Dealers and Fleet Managers to proactively rebalance fleet inventory, position high-demand equipment models at key job sites, and minimize lost rental revenue due to stockouts.

---

## 2. Dataset & Input Features

The model is trained on a 50,000-sample Caterpillar regional demand dataset (`Datasets/expanded_demand_50k.csv`).

### Categorical Features (OneHotEncoded)
- `equipment_type`: Machinery category (e.g., `Excavator`, `Wheel Loader`, `Bulldozer`, `Articulated Truck`, `Motor Grader`)
- `model`: Caterpillar specific model designation (e.g., `320 GC`, `336`, `950 GC`, `966`, `D6`, `D8`, `140`, `745`)
- `site_id`: Target construction site identifier (e.g., `SITE_001` through `SITE_050`)
- `season`: Environmental season (`Summer`, `Monsoon`, `PostMonsoon`, `Winter`)
- `region`: Geographical region (`West`, `East`, `North`, `South`)

### Numerical Features (StandardScaled)
- `month`: Numerical month of the year (1–12)
- `rental_days`: Contract duration in days
- `previous_rental_count`: Historical rentals recorded at the site
- `avg_engine_hours`: Average daily operating engine hours
- `avg_idle_hours`: Average daily idle hours
- `utilization_rate`: Engine hours ratio `(avg_engine_hours / (avg_engine_hours + avg_idle_hours))`

### Target Output
- `target_expected_demand`: Regression output representing the predicted number of units required (integer count).

---

## 3. Data Preprocessing & Pipeline

1. **Train-Test Split**: 80/20 stratified split (`random_state=42`).
2. **Categorical Processing**: `OneHotEncoder(handle_unknown='ignore', sparse_output=False)` fitted **only** on the training split to prevent data leakage.
3. **Numerical Processing**: `StandardScaler()` fitted **only** on the training split.
4. **Target Processing**: `StandardScaler()` for scaling regression targets during training, with inverse transformation applied during inference.

---

## 4. PyTorch Deep Neural Network Architecture

```
Input Features (Numerical + OneHot Categoricals)
       │
[ Linear Layer (Input_Dim ➔ 128) ] ➔ [ ReLU ] ➔ [ BatchNorm1d(128) ] ➔ [ Dropout(0.15) ]
       │
[ Linear Layer (128 ➔ 64) ] ➔ [ ReLU ] ➔ [ BatchNorm1d(64) ]
       │
[ Linear Layer (64 ➔ 1) ] (Regression Output)
```

- **Loss Function**: Mean Squared Error (`MSELoss`)
- **Optimizer**: Adam (`lr=0.001`)
- **Batch Size**: 256
- **Epochs**: 40 with early stopping monitoring test MSE.

---

## 5. Backend Service & API Integration

- **REST API Route**: `GET /api/v1/predictions/demand` & `POST /api/v1/predictions/demand`
- **Database Schema**: `demand_predictions` table (`id`, `prediction_timestamp`, `equipment_type`, `site_id`, `prediction_period`, `expected_demand`)
- **Deduplication**: `PredictionService.get_demand_predictions()` applies Python-level deduplication per `(equipment_type, site_id)` to return strictly the single latest forecast snapshot.
- **Model Enrichment**: Equipment types are automatically mapped to Caterpillar model designations (`CAT 320 GC (Excavator)`, `CAT 950 GC (Wheel Loader)`, `CAT D6 LMT (Bulldozer)`, `CAT 777 OHT`).

---

## 6. Frontend Presentation

- **Dealer & Fleet Dashboards**: Displayed on `DealerPredictions.jsx` in the **Demand Forecast** tab.
- **Visuals**: Color-coded demand badges (Red: High demand > 5 units; Orange: Medium demand 3–4 units; Green: Stable demand < 3 units).
