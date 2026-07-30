import os
import numpy as np
import pandas as pd
import joblib
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder, StandardScaler

CAT_CATALOG = [
    {'equipment_type': 'Excavator', 'model': '320 GC'},
    {'equipment_type': 'Excavator', 'model': '336'},
    {'equipment_type': 'Wheel Loader', 'model': '950 GC'},
    {'equipment_type': 'Wheel Loader', 'model': '966'},
    {'equipment_type': 'Bulldozer', 'model': 'D6'},
    {'equipment_type': 'Bulldozer', 'model': 'D8'},
    {'equipment_type': 'Motor Grader', 'model': '140'},
    {'equipment_type': 'Articulated Truck', 'model': '745'},
    {'equipment_type': 'Compact Track Loader', 'model': '259D3'},
    {'equipment_type': 'Backhoe Loader', 'model': '420'}
]

def generate_cat_maintenance_dataset(num_samples: int = 50000, random_seed: int = 42):
    """Generates expanded 50,000 sample Caterpillar maintenance dataset with equipment_type and model."""
    np.random.seed(random_seed)
    print(f"Generating expanded Caterpillar maintenance dataset with {num_samples:,} samples using equipment_type and model...")

    data = []
    for _ in range(num_samples):
        cat_item = CAT_CATALOG[np.random.choice(len(CAT_CATALOG))]
        eq_type = cat_item['equipment_type']
        model_name = cat_item['model']

        eq_age = np.random.randint(1, 12)
        engine_hours = np.random.uniform(2.0, 14.0)
        idle_hours = np.random.uniform(0.5, 6.0)
        fuel_level = np.random.uniform(10.0, 100.0)

        # Model specific temperature & wear characteristics (heavy models run hotter under load)
        temp_base = 92.0 if model_name in ['336', 'D8', '745'] else 82.0
        engine_temp = np.random.uniform(temp_base - 10.0, temp_base + 20.0)

        battery_volt = np.random.uniform(11.5, 14.5)
        days_since_service = np.random.randint(5, 300)
        fault_codes = np.random.randint(0, 8)
        total_hours = np.random.uniform(500.0, 12000.0)

        risk_factor = (
            (days_since_service / 300.0) * 0.35 +
            (fault_codes / 8.0) * 0.30 +
            (max(0, engine_temp - 95.0) / 20.0) * 0.20 +
            (eq_age / 12.0) * 0.15
        )

        maint_prob = float(np.clip(risk_factor + np.random.normal(0, 0.02), 0.01, 0.99))
        days_until_service = float(max(1.0, round(90.0 * (1.0 - maint_prob) + np.random.normal(0, 1.5), 1)))
        confidence = float(np.clip(0.70 + (0.30 * (1.0 - abs(maint_prob - 0.5) * 2)) + np.random.normal(0, 0.01), 0.50, 0.99))

        data.append({
            'equipment_type': eq_type,
            'model': model_name,
            'equipment_age': eq_age,
            'engine_hours_per_day': round(engine_hours, 2),
            'idle_hours_per_day': round(idle_hours, 2),
            'fuel_level': round(fuel_level, 2),
            'engine_temperature': round(engine_temp, 2),
            'battery_voltage': round(battery_volt, 2),
            'days_since_last_service': days_since_service,
            'fault_code_count': fault_codes,
            'total_operating_hours': round(total_hours, 2),
            'target_maintenance_probability': round(maint_prob, 4),
            'target_days_until_service': days_until_service,
            'target_confidence': round(confidence, 4)
        })

    df = pd.DataFrame(data)
    os.makedirs("Datasets", exist_ok=True)
    df.to_csv(os.path.join("Datasets", "expanded_maintenance_50k.csv"), index=False)
    return df

def train_pytorch_maintenance():
    import torch
    import torch.nn as nn
    import torch.optim as optim
    from torch.utils.data import TensorDataset, DataLoader

    df = generate_cat_maintenance_dataset(50000)

    cat_cols = ['equipment_type', 'model']
    num_cols = ['equipment_age', 'engine_hours_per_day', 'idle_hours_per_day', 'fuel_level',
                'engine_temperature', 'battery_voltage', 'days_since_last_service',
                'fault_code_count', 'total_operating_hours']
    target_cols = ['target_maintenance_probability', 'target_days_until_service', 'target_confidence']

    X = df[num_cols + cat_cols]
    y = df[target_cols].values

    # 1. Train-Test Split (80/20) BEFORE fitting scaling/encoding
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # 2. Fit Preprocessing ONLY on Train Set
    encoder = OneHotEncoder(sparse_output=False, handle_unknown='ignore')
    X_train_cat = encoder.fit_transform(X_train[cat_cols])
    X_test_cat = encoder.transform(X_test[cat_cols])

    scaler = StandardScaler()
    X_train_num = scaler.fit_transform(X_train[num_cols])
    X_test_num = scaler.transform(X_test[num_cols])

    X_train_processed = np.hstack([X_train_num, X_train_cat])
    X_test_processed = np.hstack([X_test_num, X_test_cat])

    y_scaler = StandardScaler()
    y_train_scaled = y_scaler.fit_transform(y_train)
    y_test_scaled = y_scaler.transform(y_test)

    input_dim = X_train_processed.shape[1]
    print(f"Dataset Processed: Input Feature Dim = {input_dim}, Train Samples = {len(X_train):,}, Test Samples = {len(X_test):,}")

    X_train_tensor = torch.tensor(X_train_processed, dtype=torch.float32)
    y_train_tensor = torch.tensor(y_train_scaled, dtype=torch.float32)
    X_test_tensor = torch.tensor(X_test_processed, dtype=torch.float32)

    train_dataset = TensorDataset(X_train_tensor, y_train_tensor)
    train_loader = DataLoader(train_dataset, batch_size=128, shuffle=True)

    # 3. PyTorch Multi-Output Maintenance Neural Network
    class MaintenancePyTorchNet(nn.Module):
        def __init__(self, input_size):
            super(MaintenancePyTorchNet, self).__init__()
            self.shared = nn.Sequential(
                nn.Linear(input_size, 128),
                nn.ReLU(),
                nn.BatchNorm1d(128),
                nn.Dropout(0.15),
                nn.Linear(128, 64),
                nn.ReLU(),
                nn.BatchNorm1d(64)
            )
            self.output_head = nn.Linear(64, 3)

        def forward(self, x):
            return self.output_head(self.shared(x))

    model = MaintenancePyTorchNet(input_dim)
    criterion = nn.MSELoss()
    optimizer = optim.Adam(model.parameters(), lr=0.003)

    print("Training PyTorch Neural Network for Predictive Maintenance with equipment_type + model...")
    epochs = 40
    for epoch in range(epochs):
        model.train()
        total_loss = 0.0
        for batch_x, batch_y in train_loader:
            optimizer.zero_grad()
            outputs = model(batch_x)
            loss = criterion(outputs, batch_y)
            loss.backward()
            optimizer.step()
            total_loss += loss.item() * batch_x.size(0)

        if (epoch + 1) % 10 == 0 or epoch == 0:
            avg_loss = total_loss / len(X_train)
            print(f"Epoch [{epoch+1:02d}/{epochs}] - Train MSE Loss: {avg_loss:.4f}")

    # 4. Evaluate Test Set
    model.eval()
    with torch.no_grad():
        test_preds_scaled = model(X_test_tensor).numpy()
        test_preds = y_scaler.inverse_transform(test_preds_scaled)

        mae_prob = np.mean(np.abs(test_preds[:, 0] - y_test[:, 0]))
        mae_days = np.mean(np.abs(test_preds[:, 1] - y_test[:, 1]))
        mae_conf = np.mean(np.abs(test_preds[:, 2] - y_test[:, 2]))

        print("\n--- Test Set Maintenance Evaluation Results (equipment_type + model) ---")
        print(f"Maintenance Probability MAE: {mae_prob:.4f}")
        print(f"Days Until Next Service MAE: {mae_days:.2f} days")
        print(f"Confidence Score MAE: {mae_conf:.4f}")

    # 5. Save Artifacts
    output_dir = "ml_prediction"
    os.makedirs(output_dir, exist_ok=True)

    torch.save(model.state_dict(), os.path.join(output_dir, "maintenance_pytorch_model.pt"))
    joblib.dump(scaler, os.path.join(output_dir, "maintenance_scaler.joblib"))
    joblib.dump(encoder, os.path.join(output_dir, "maintenance_encoder.joblib"))
    joblib.dump(y_scaler, os.path.join(output_dir, "maintenance_target_scaler.joblib"))
    joblib.dump(input_dim, os.path.join(output_dir, "maintenance_input_dim.joblib"))

    print(f"\nSuccessfully trained on 50,000 Cat equipment_type + model dataset & saved to '{output_dir}'!")

if __name__ == "__main__":
    train_pytorch_maintenance()
