# Caterpillar ML Pipeline Documentation Index

This directory contains technical specifications for the four **PyTorch Machine Learning Pipelines** powering the Caterpillar Smart Rental Tracking System:

1. 📈 **[Demand Forecasting Pipeline](pipeline_demand_forecasting.md)**  
   *Predicts monthly regional and site-level machinery demand counts using deep neural regression networks.*

2. ⚡ **[Utilization & Exploitation Prediction Pipeline](pipeline_utilization_prediction.md)**  
   *Multi-head neural network predicting utilization rates and cumulative idle hours, triggering real-time RabbitMQ exploitation alerts when utilization exceeds 90%.*

3. 🔧 **[Predictive Maintenance Pipeline](pipeline_predictive_maintenance.md)**  
   *Predicts maintenance risk probabilities, recommended service dates, and model confidence scores from machinery sensor telemetry.*

4. 🔍 **[Anomaly Detection Pipeline](pipeline_anomaly_detection.md)**  
   *Deep binary classifier detecting operational anomalies, engine temperature spikes, voltage drops, and fault code bursts, with severity ranking (Low, Medium, High, Critical).*

---

## Shared Architecture & Pipeline Principles

- **Framework**: PyTorch Deep Learning Framework.
- **Preprocessing**: Stratified 80/20 train-test splits with `StandardScaler` and `OneHotEncoder` fitted exclusively on training splits to prevent data leakage.
- **Data Enrichment**: All prediction endpoints dynamically map `equipment_id` to Caterpillar model numbers (`CAT 320 GC`, `CAT 950 GC`, `CAT D6 LMT`, `CAT 777 OHT`, etc.).
- **Global Single-Row Deduplication**: API responses perform python-level deduplication (`_enrich_and_deduplicate`), returning strictly the **single latest prediction snapshot per machine** across all role dashboards.
