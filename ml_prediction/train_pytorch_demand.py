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

def generate_cat_demand_dataset(num_samples: int = 50000, random_seed: int = 42):
    """Generates expanded 50,000 sample Caterpillar demand forecasting dataset with equipment_type and model."""
    np.random.seed(random_seed)
    print(f"Generating expanded Caterpillar demand forecasting dataset with {num_samples:,} samples using equipment_type and model...")

    sites = [f"SITE_{i:03d}" for i in range(1, 51)]
    seasons = ['Summer', 'Monsoon', 'PostMonsoon', 'Winter']
    regions = ['West', 'East', 'North', 'South']

    data = []
    for _ in range(num_samples):
        cat_item = CAT_CATALOG[np.random.choice(len(CAT_CATALOG))]
        eq_type = cat_item['equipment_type']
        model_name = cat_item['model']

        site_id = np.random.choice(sites)
        season = np.random.choice(seasons)
        region = np.random.choice(regions)

        month = np.random.randint(1, 13)
        rental_days = np.random.randint(7, 90)
        previous_rental_count = np.random.randint(2, 50)
        avg_engine_hours = np.random.uniform(4.0, 11.0)
        avg_idle_hours = np.random.uniform(1.0, 4.0)
        utilization_rate = np.clip(avg_engine_hours / (avg_engine_hours + avg_idle_hours), 0.1, 0.95)

        type_weight = {
            '320 GC': 28, '336': 35,
            '950 GC': 24, '966': 29,
            'D6': 22, 'D8': 27,
            '140': 18, '745': 20,
            '259D3': 15, '420': 16
        }[model_name]
        season_multiplier = {'Summer': 1.2, 'PostMonsoon': 1.1, 'Winter': 0.9, 'Monsoon': 0.7}[season]

        expected_demand = float(max(1, round((type_weight * season_multiplier + (previous_rental_count * 0.4) + (utilization_rate * 10)) + np.random.normal(0, 2.0))))

        data.append({
            'equipment_type': eq_type,
            'model': model_name,
            'site_id': site_id,
            'season': season,
            'region': region,
            'month': month,
            'rental_days': rental_days,
            'previous_rental_count': previous_rental_count,
            'avg_engine_hours': round(avg_engine_hours, 2),
            'avg_idle_hours': round(avg_idle_hours, 2),
            'utilization_rate': round(utilization_rate, 4),
            'target_expected_demand': expected_demand
        })

    df = pd.DataFrame(data)
    os.makedirs("Datasets", exist_ok=True)
    df.to_csv(os.path.join("Datasets", "expanded_demand_50k.csv"), index=False)
    return df

def train_pytorch_demand():
    import torch
    import torch.nn as nn
    import torch.optim as optim
    from torch.utils.data import TensorDataset, DataLoader

    df = generate_cat_demand_dataset(50000)

    cat_cols = ['equipment_type', 'model', 'site_id', 'season', 'region']
    num_cols = ['month', 'rental_days', 'previous_rental_count', 'avg_engine_hours', 'avg_idle_hours', 'utilization_rate']
    target_cols = ['target_expected_demand']

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

    # 3. PyTorch Demand Forecasting Neural Network
    class DemandPyTorchNet(nn.Module):
        def __init__(self, input_size):
            super(DemandPyTorchNet, self).__init__()
            self.net = nn.Sequential(
                nn.Linear(input_size, 128),
                nn.ReLU(),
                nn.BatchNorm1d(128),
                nn.Dropout(0.15),
                nn.Linear(128, 64),
                nn.ReLU(),
                nn.BatchNorm1d(64),
                nn.Linear(64, 1)
            )

        def forward(self, x):
            return self.net(x)

    model = DemandPyTorchNet(input_dim)
    criterion = nn.MSELoss()
    optimizer = optim.Adam(model.parameters(), lr=0.003)

    print("Training PyTorch Neural Network for Demand Forecasting with equipment_type + model...")
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

        mae_demand = np.mean(np.abs(test_preds[:, 0] - y_test[:, 0]))

        print("\n--- Test Set Demand Evaluation Results (equipment_type + model) ---")
        print(f"Expected Demand MAE: {mae_demand:.2f} machines")

    # 5. Save Artifacts
    output_dir = "ml_prediction"
    os.makedirs(output_dir, exist_ok=True)

    torch.save(model.state_dict(), os.path.join(output_dir, "demand_pytorch_model.pt"))
    joblib.dump(scaler, os.path.join(output_dir, "demand_scaler.joblib"))
    joblib.dump(encoder, os.path.join(output_dir, "demand_encoder.joblib"))
    joblib.dump(y_scaler, os.path.join(output_dir, "demand_target_scaler.joblib"))
    joblib.dump(input_dim, os.path.join(output_dir, "demand_input_dim.joblib"))

    print(f"\nSuccessfully trained on 50,000 Cat equipment_type + model dataset & saved to '{output_dir}'!")

if __name__ == "__main__":
    train_pytorch_demand()
