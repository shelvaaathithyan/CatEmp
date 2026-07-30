"""
Generate 50,000-row Anomaly Detection Dataset for PyTorch Training.

Expands the base 5,000-row anomaly_detection.csv with:
- Model-specific anomaly thresholds (different CAT models have different behaviors)
- Realistic Gaussian noise on numeric features
- Balanced Normal/Anomaly class distribution (~40% anomaly)
- Exact Caterpillar equipment types and models from the machines table
"""
import os
import numpy as np
import pandas as pd

# ---------------------------------------------------------------
# Caterpillar Equipment Types + Models (matching machines table)
# ---------------------------------------------------------------
EQUIPMENT_CATALOG = {
    "Excavator": ["320 GC", "336", "330", "323", "352"],
    "Wheel Loader": ["950 GC", "966", "980", "938"],
    "Bulldozer": ["D6", "D8", "D5", "D10"],
    "Motor Grader": ["140", "120", "160"],
    "Articulated Truck": ["745", "730", "740"],
    "Backhoe Loader": ["420", "430", "416"],
    "Telehandler": ["TH514D", "TH357D"],
    "Skid Steer Loader": ["262D3", "272D3"],
    "Compactor": ["CS56B", "CB2.7"],
    "Crane": ["None"],  # Generic crane
}

# Model-specific anomaly thresholds — different models tolerate different limits
MODEL_ANOMALY_THRESHOLDS = {
    # Excavators
    "320 GC": {"temp_max": 100, "volt_min": 12.0, "fault_threshold": 4, "fuel_min": 12},
    "336":    {"temp_max": 105, "volt_min": 11.8, "fault_threshold": 5, "fuel_min": 10},
    "330":    {"temp_max": 102, "volt_min": 11.9, "fault_threshold": 4, "fuel_min": 11},
    "323":    {"temp_max": 98,  "volt_min": 12.0, "fault_threshold": 3, "fuel_min": 13},
    "352":    {"temp_max": 108, "volt_min": 11.7, "fault_threshold": 5, "fuel_min": 9},
    # Wheel Loaders
    "950 GC": {"temp_max": 100, "volt_min": 12.0, "fault_threshold": 4, "fuel_min": 12},
    "966":    {"temp_max": 103, "volt_min": 11.8, "fault_threshold": 5, "fuel_min": 10},
    "980":    {"temp_max": 105, "volt_min": 11.7, "fault_threshold": 5, "fuel_min": 9},
    "938":    {"temp_max": 98,  "volt_min": 12.1, "fault_threshold": 3, "fuel_min": 14},
    # Bulldozers
    "D6":     {"temp_max": 102, "volt_min": 11.9, "fault_threshold": 4, "fuel_min": 11},
    "D8":     {"temp_max": 108, "volt_min": 11.6, "fault_threshold": 5, "fuel_min": 8},
    "D5":     {"temp_max": 98,  "volt_min": 12.0, "fault_threshold": 3, "fuel_min": 13},
    "D10":    {"temp_max": 110, "volt_min": 11.5, "fault_threshold": 6, "fuel_min": 7},
    # Motor Graders
    "140":    {"temp_max": 100, "volt_min": 12.0, "fault_threshold": 4, "fuel_min": 12},
    "120":    {"temp_max": 98,  "volt_min": 12.1, "fault_threshold": 3, "fuel_min": 14},
    "160":    {"temp_max": 105, "volt_min": 11.8, "fault_threshold": 5, "fuel_min": 10},
    # Articulated Trucks
    "745":    {"temp_max": 105, "volt_min": 11.8, "fault_threshold": 5, "fuel_min": 10},
    "730":    {"temp_max": 100, "volt_min": 12.0, "fault_threshold": 4, "fuel_min": 12},
    "740":    {"temp_max": 103, "volt_min": 11.9, "fault_threshold": 4, "fuel_min": 11},
    # Backhoe Loaders
    "420":    {"temp_max": 95,  "volt_min": 12.2, "fault_threshold": 3, "fuel_min": 15},
    "430":    {"temp_max": 98,  "volt_min": 12.0, "fault_threshold": 4, "fuel_min": 13},
    "416":    {"temp_max": 93,  "volt_min": 12.3, "fault_threshold": 2, "fuel_min": 16},
    # Telehandlers
    "TH514D": {"temp_max": 95, "volt_min": 12.2, "fault_threshold": 3, "fuel_min": 15},
    "TH357D": {"temp_max": 93, "volt_min": 12.3, "fault_threshold": 2, "fuel_min": 16},
    # Skid Steer Loaders
    "262D3":  {"temp_max": 95, "volt_min": 12.2, "fault_threshold": 3, "fuel_min": 15},
    "272D3":  {"temp_max": 98, "volt_min": 12.0, "fault_threshold": 4, "fuel_min": 13},
    # Compactors
    "CS56B":  {"temp_max": 95, "volt_min": 12.2, "fault_threshold": 3, "fuel_min": 15},
    "CB2.7":  {"temp_max": 93, "volt_min": 12.3, "fault_threshold": 2, "fuel_min": 16},
    # Crane (default)
    "None":   {"temp_max": 100, "volt_min": 12.0, "fault_threshold": 4, "fuel_min": 12},
}

DEFAULT_THRESHOLD = {"temp_max": 100, "volt_min": 12.0, "fault_threshold": 4, "fuel_min": 12}


def classify_anomaly(row):
    """Determines anomaly status based on model-specific thresholds."""
    model = str(row.get("model", ""))
    thresholds = MODEL_ANOMALY_THRESHOLDS.get(model, DEFAULT_THRESHOLD)

    if (row["engine_temperature"] > thresholds["temp_max"]
        or row["battery_voltage"] < thresholds["volt_min"]
        or row["fault_code_count"] >= thresholds["fault_threshold"]
        or row["fuel_level"] < thresholds["fuel_min"]):
        return "Anomaly"
    return "Normal"


def generate_expanded_anomaly_dataset(num_samples: int = 50000, seed: int = 42):
    np.random.seed(seed)

    base_csv = os.path.join(os.path.dirname(__file__), "..", "Datasets", "anomaly_detection.csv")
    if not os.path.exists(base_csv):
        base_csv = os.path.join("Datasets", "anomaly_detection.csv")

    # Load base dataset
    if os.path.exists(base_csv):
        df_base = pd.read_csv(base_csv)
        print(f"Loaded base anomaly dataset: {len(df_base)} rows from '{base_csv}'")
    else:
        df_base = None
        print("No base dataset found. Generating entirely from scratch.")

    statuses = ["Running", "Idle"]
    rows = []

    # 1) Augment from base dataset (first ~25,000 rows)
    if df_base is not None:
        augment_count = min(num_samples // 2, 25000)
        repeats = (augment_count // len(df_base)) + 1
        df_aug = pd.concat([df_base] * repeats, ignore_index=True).iloc[:augment_count].copy()

        # Add Gaussian noise to numeric columns
        noise_cols = {
            "engine_hours_per_day": 0.3,
            "idle_hours_per_day": 0.3,
            "fuel_level": 2.0,
            "engine_temperature": 1.5,
            "battery_voltage": 0.15,
            "total_operating_hours": 50.0,
            "utilization_rate": 0.02,
        }
        for col, noise_std in noise_cols.items():
            if col in df_aug.columns:
                df_aug[col] = df_aug[col] + np.random.normal(0, noise_std, size=len(df_aug))

        # Clip to realistic ranges
        df_aug["engine_hours_per_day"] = df_aug["engine_hours_per_day"].clip(0.5, 16.0)
        df_aug["idle_hours_per_day"] = df_aug["idle_hours_per_day"].clip(0.0, 12.0)
        df_aug["fuel_level"] = df_aug["fuel_level"].clip(2.0, 100.0)
        df_aug["engine_temperature"] = df_aug["engine_temperature"].clip(55.0, 120.0)
        df_aug["battery_voltage"] = df_aug["battery_voltage"].clip(10.5, 15.0)
        df_aug["fault_code_count"] = df_aug["fault_code_count"].clip(0, 10).astype(int)
        df_aug["total_operating_hours"] = df_aug["total_operating_hours"].clip(100, 15000)
        df_aug["utilization_rate"] = df_aug["utilization_rate"].clip(0.05, 0.99)

        # Re-classify anomaly based on model-specific thresholds
        df_aug["anomaly_status"] = df_aug.apply(classify_anomaly, axis=1)

        for _, row in df_aug.iterrows():
            rows.append(row.to_dict())

    # 2) Generate fresh synthetic samples for remaining count
    remaining = num_samples - len(rows)
    print(f"Generating {remaining} fresh synthetic anomaly samples...")

    for _ in range(remaining):
        eq_type = np.random.choice(list(EQUIPMENT_CATALOG.keys()))
        model = np.random.choice(EQUIPMENT_CATALOG[eq_type])
        status = np.random.choice(statuses, p=[0.55, 0.45])

        engine_hours = np.random.uniform(0.5, 14.0)
        idle_hours = np.random.uniform(0.0, 10.0)
        fuel = np.random.uniform(5.0, 100.0)
        temp = np.random.uniform(60.0, 118.0)
        volt = np.random.uniform(10.8, 14.8)
        faults = np.random.randint(0, 10)
        total_hours = np.random.uniform(200, 14000)
        util_rate = engine_hours / max(engine_hours + idle_hours, 0.01)

        sample = {
            "equipment_type": eq_type,
            "engine_hours_per_day": round(engine_hours, 4),
            "idle_hours_per_day": round(idle_hours, 4),
            "fuel_level": round(fuel, 4),
            "engine_temperature": round(temp, 4),
            "battery_voltage": round(volt, 4),
            "fault_code_count": int(faults),
            "total_operating_hours": round(total_hours, 2),
            "machine_status": status,
            "utilization_rate": round(util_rate, 4),
            "model": model,
        }

        # Classify using model-specific thresholds
        sample["anomaly_status"] = classify_anomaly(sample)
        rows.append(sample)

    df = pd.DataFrame(rows)

    # Ensure column order matches base dataset
    col_order = [
        "equipment_type", "engine_hours_per_day", "idle_hours_per_day",
        "fuel_level", "engine_temperature", "battery_voltage",
        "fault_code_count", "total_operating_hours", "machine_status",
        "utilization_rate", "anomaly_status", "model"
    ]
    df = df[col_order]

    # Save
    output_path = os.path.join(os.path.dirname(__file__), "..", "Datasets", "expanded_anomaly_50k.csv")
    if not os.path.exists(os.path.dirname(output_path)):
        output_path = os.path.join("Datasets", "expanded_anomaly_50k.csv")

    df.to_csv(output_path, index=False)

    # Stats
    anomaly_count = (df["anomaly_status"] == "Anomaly").sum()
    normal_count = (df["anomaly_status"] == "Normal").sum()
    print(f"\n--- Expanded Anomaly Dataset Generated ---")
    print(f"Total Samples: {len(df):,}")
    print(f"Anomaly: {anomaly_count:,} ({anomaly_count/len(df)*100:.1f}%)")
    print(f"Normal:  {normal_count:,} ({normal_count/len(df)*100:.1f}%)")
    print(f"Equipment Types: {df['equipment_type'].nunique()}")
    print(f"Models: {df['model'].nunique()}")
    print(f"\nSample distribution by equipment_type:")
    print(df["equipment_type"].value_counts().to_string())
    print(f"\nSample distribution by model:")
    print(df["model"].value_counts().to_string())
    print(f"\nSaved to: {os.path.abspath(output_path)}")

    return df


if __name__ == "__main__":
    generate_expanded_anomaly_dataset(50000)
