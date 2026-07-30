import os
import numpy as np
import pandas as pd
import joblib
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder, StandardScaler

# Official Caterpillar Machinery Catalog (Type -> Models)
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

def generate_cat_utilization_dataset(num_samples: int = 50000, random_seed: int = 42):
    """Generates expanded 50,000 sample Caterpillar telemetry dataset with equipment_type & specific model."""
    np.random.seed(random_seed)
    print(f"Generating expanded Caterpillar dataset with {num_samples:,} samples using equipment_type and specific model...")

    sites = [f"SITE_{i:03d}" for i in range(1, 51)]
    weathers = ['Sunny', 'Cloudy', 'Rainy']
    phases = ['Excavation', 'Foundation', 'Structural', 'Finishing', 'Clearing']
    statuses = ['Running', 'Idle']

    data = []
    for _ in range(num_samples):
        cat_item = CAT_CATALOG[np.random.choice(len(CAT_CATALOG))]
        eq_type = cat_item['equipment_type']
        model_name = cat_item['model']

        site_id = np.random.choice(sites)
        weather = np.random.choice(weathers)
        phase = np.random.choice(phases)
        status = np.random.choice(statuses, p=[0.7, 0.3])

        rental_days = np.random.randint(7, 90)
        operator_exp = np.random.randint(1, 15)

        # Model-specific engine profiles (e.g. 336 heavy excavator vs 320 GC light excavator)
        model_power_factor = 1.3 if model_name in ['336', 'D8', '966', '745'] else 1.0

        if status == 'Running':
            engine_hours = np.random.uniform(5.0, 11.5) * model_power_factor
            idle_hours = np.random.uniform(0.5, 2.8) / model_power_factor
        else:
            engine_hours = np.random.uniform(0.5, 3.0)
            idle_hours = np.random.uniform(4.0, 8.5)

        if weather == 'Rainy':
            idle_hours += np.random.uniform(1.0, 3.0)
            engine_hours = max(0.5, engine_hours - np.random.uniform(1.0, 2.5))
        elif weather == 'Cloudy':
            idle_hours += np.random.uniform(0.2, 0.8)

        total_hours = engine_hours + idle_hours
        utilization_rate = engine_hours / total_hours
        utilization_score = np.clip(utilization_rate + np.random.normal(0, 0.01), 0.01, 0.99)
        predicted_idle_hours = max(2.0, round(idle_hours * 30.0 + (15 - operator_exp) * 1.2 + np.random.normal(0, 3.0), 2))

        data.append({
            'equipment_type': eq_type,
            'model': model_name,
            'rental_days': rental_days,
            'engine_hours_per_day': round(engine_hours, 2),
            'idle_hours_per_day': round(idle_hours, 2),
            'operator_experience': operator_exp,
            'utilization_rate': round(utilization_rate, 4),
            'site_id': site_id,
            'weather': weather,
            'project_phase': phase,
            'machine_status': status,
            'target_utilization_score': round(utilization_score, 4),
            'target_predicted_idle_hours': predicted_idle_hours
        })

    df = pd.DataFrame(data)
    os.makedirs("Datasets", exist_ok=True)
    df.to_csv(os.path.join("Datasets", "expanded_utilization_50k.csv"), index=False)
    return df

def train_pytorch_model():
    import torch
    import torch.nn as nn
    import torch.optim as optim
    from torch.utils.data import TensorDataset, DataLoader

    df = generate_cat_utilization_dataset(50000)
    print(f"Cat Model Dataset Loaded: Total Rows = {len(df):,}")

    cat_cols = ['equipment_type', 'model', 'site_id', 'weather', 'project_phase', 'machine_status']
    num_cols = ['rental_days', 'engine_hours_per_day', 'idle_hours_per_day', 'operator_experience', 'utilization_rate']
    target_cols = ['target_utilization_score', 'target_predicted_idle_hours']

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

    input_dim = X_train_processed.shape[1]
    print(f"Preprocessing Complete: Input Feature Dim = {input_dim}, Train Samples = {len(X_train):,}, Test Samples = {len(X_test):,}")

    y_scaler = StandardScaler()
    y_train_scaled = y_scaler.fit_transform(y_train)
    y_test_scaled = y_scaler.transform(y_test)

    # Tensors
    X_train_tensor = torch.tensor(X_train_processed, dtype=torch.float32)
    y_train_tensor = torch.tensor(y_train_scaled, dtype=torch.float32)
    X_test_tensor = torch.tensor(X_test_processed, dtype=torch.float32)

    train_dataset = TensorDataset(X_train_tensor, y_train_tensor)
    train_loader = DataLoader(train_dataset, batch_size=128, shuffle=True)

    # 3. Define PyTorch Multi-Output Neural Network
    class UtilizationPyTorchNet(nn.Module):
        def __init__(self, input_size):
            super(UtilizationPyTorchNet, self).__init__()
            self.shared = nn.Sequential(
                nn.Linear(input_size, 128),
                nn.ReLU(),
                nn.BatchNorm1d(128),
                nn.Dropout(0.15),
                nn.Linear(128, 64),
                nn.ReLU(),
                nn.BatchNorm1d(64)
            )
            self.head_score = nn.Sequential(
                nn.Linear(64, 32),
                nn.ReLU(),
                nn.Linear(32, 1)
            )
            self.head_idle = nn.Sequential(
                nn.Linear(64, 32),
                nn.ReLU(),
                nn.Linear(32, 1)
            )

        def forward(self, x):
            feat = self.shared(x)
            score = self.head_score(feat)
            idle = self.head_idle(feat)
            return torch.cat([score, idle], dim=1)

    model = UtilizationPyTorchNet(input_dim)
    criterion = nn.MSELoss()
    optimizer = optim.Adam(model.parameters(), lr=0.003)

    print("Training PyTorch Neural Network with equipment_type + model features...")
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

        mae_score = np.mean(np.abs(test_preds[:, 0] - y_test[:, 0]))
        mae_idle = np.mean(np.abs(test_preds[:, 1] - y_test[:, 1]))

        print("\n--- Test Set Evaluation Results (equipment_type + model) ---")
        print(f"Utilization Score MAE: {mae_score:.4f}")
        print(f"Predicted Idle Hours MAE: {mae_idle:.2f} hours")

    # 5. Save Artifacts
    output_dir = "ml_prediction"
    os.makedirs(output_dir, exist_ok=True)

    torch.save(model.state_dict(), os.path.join(output_dir, "utilization_pytorch_model.pt"))
    joblib.dump(scaler, os.path.join(output_dir, "utilization_scaler.joblib"))
    joblib.dump(encoder, os.path.join(output_dir, "utilization_encoder.joblib"))
    joblib.dump(y_scaler, os.path.join(output_dir, "utilization_target_scaler.joblib"))
    joblib.dump(input_dim, os.path.join(output_dir, "utilization_input_dim.joblib"))

    print(f"\nSuccessfully trained on 50,000 Cat equipment_type + model dataset & saved to '{output_dir}'!")

if __name__ == "__main__":
    train_pytorch_model()
