"""
Train PyTorch Anomaly Detection Model on 50,000-row expanded dataset.

Uses the pre-generated expanded_anomaly_50k.csv dataset with:
- Model-specific anomaly thresholds for accurate labeling
- 10 equipment types, 29 CAT models
- Binary classification: Normal (0) vs Anomaly (1)
"""
import os
import numpy as np
import pandas as pd
import joblib
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.metrics import classification_report, confusion_matrix


def load_expanded_anomaly_dataset():
    """Loads the pre-generated 50,000-row expanded anomaly dataset."""
    csv_path = os.path.join("Datasets", "expanded_anomaly_50k.csv")
    if not os.path.exists(csv_path):
        csv_path = os.path.join("..", "Datasets", "expanded_anomaly_50k.csv")

    if not os.path.exists(csv_path):
        raise FileNotFoundError(
            f"Expanded anomaly dataset not found. Run generate_anomaly_dataset.py first."
        )

    df = pd.read_csv(csv_path)
    print(f"Loaded expanded anomaly dataset: {len(df):,} rows from '{csv_path}'")

    # Create binary target
    df["target_anomaly"] = (df["anomaly_status"] == "Anomaly").astype(int)
    return df


def train_pytorch_anomaly():
    import torch
    import torch.nn as nn
    import torch.optim as optim
    from torch.utils.data import TensorDataset, DataLoader

    df = load_expanded_anomaly_dataset()

    # Feature columns - include 'model' for model-specific behaviors
    cat_cols = ["equipment_type", "model", "machine_status"]
    num_cols = [
        "engine_hours_per_day", "idle_hours_per_day", "fuel_level",
        "engine_temperature", "battery_voltage", "fault_code_count",
        "total_operating_hours", "utilization_rate"
    ]
    target_col = "target_anomaly"

    X = df[num_cols + cat_cols]
    y = df[target_col].values

    # 1. Train-Test Split (80/20) BEFORE fitting scaling/encoding
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    # 2. Fit Preprocessing ONLY on Train Set
    encoder = OneHotEncoder(sparse_output=False, handle_unknown="ignore")
    X_train_cat = encoder.fit_transform(X_train[cat_cols])
    X_test_cat = encoder.transform(X_test[cat_cols])

    scaler = StandardScaler()
    X_train_num = scaler.fit_transform(X_train[num_cols])
    X_test_num = scaler.transform(X_test[num_cols])

    X_train_processed = np.hstack([X_train_num, X_train_cat])
    X_test_processed = np.hstack([X_test_num, X_test_cat])

    input_dim = X_train_processed.shape[1]
    print(f"\nDataset Processed:")
    print(f"  Input Feature Dim = {input_dim}")
    print(f"  Train Samples = {len(X_train):,}")
    print(f"  Test Samples = {len(X_test):,}")
    print(f"  Anomaly Rate (Train) = {y_train.mean()*100:.1f}%")
    print(f"  Anomaly Rate (Test) = {y_test.mean()*100:.1f}%")
    print(f"  Categorical Features encoded: {cat_cols}")
    print(f"  Numeric Features scaled: {num_cols}")

    X_train_tensor = torch.tensor(X_train_processed, dtype=torch.float32)
    y_train_tensor = torch.tensor(y_train, dtype=torch.float32).unsqueeze(1)
    X_test_tensor = torch.tensor(X_test_processed, dtype=torch.float32)
    y_test_tensor = torch.tensor(y_test, dtype=torch.float32).unsqueeze(1)

    train_dataset = TensorDataset(X_train_tensor, y_train_tensor)
    train_loader = DataLoader(train_dataset, batch_size=256, shuffle=True)

    # 3. PyTorch Binary Classification Neural Network
    class AnomalyPyTorchNet(nn.Module):
        def __init__(self, input_size):
            super(AnomalyPyTorchNet, self).__init__()
            self.net = nn.Sequential(
                nn.Linear(input_size, 128),
                nn.ReLU(),
                nn.BatchNorm1d(128),
                nn.Dropout(0.2),
                nn.Linear(128, 64),
                nn.ReLU(),
                nn.BatchNorm1d(64),
                nn.Dropout(0.1),
                nn.Linear(64, 32),
                nn.ReLU(),
                nn.BatchNorm1d(32),
                nn.Linear(32, 1),
                nn.Sigmoid()
            )

        def forward(self, x):
            return self.net(x)

    model = AnomalyPyTorchNet(input_dim)
    criterion = nn.BCELoss()
    optimizer = optim.Adam(model.parameters(), lr=0.002, weight_decay=1e-4)
    scheduler = optim.lr_scheduler.StepLR(optimizer, step_size=15, gamma=0.5)

    print(f"\nTraining PyTorch Anomaly Detection Model on {len(X_train):,} samples...")
    print(f"Architecture: {input_dim} -> 128 -> 64 -> 32 -> 1 (Sigmoid)")
    epochs = 50
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

        scheduler.step()

        if (epoch + 1) % 5 == 0 or epoch == 0:
            avg_loss = total_loss / len(X_train)
            print(f"  Epoch [{epoch+1:02d}/{epochs}] - Train BCE Loss: {avg_loss:.4f} - LR: {scheduler.get_last_lr()[0]:.6f}")

    # 4. Evaluate Test Set
    model.eval()
    with torch.no_grad():
        test_probs = model(X_test_tensor).numpy()
        test_preds = (test_probs > 0.5).astype(int)
        accuracy = np.mean(test_preds.flatten() == y_test)

        print(f"\n{'='*60}")
        print(f"TEST SET ANOMALY DETECTION EVALUATION (50,000 Dataset)")
        print(f"{'='*60}")
        print(f"Classification Accuracy: {accuracy * 100:.2f}%")
        print(f"\nClassification Report:")
        print(classification_report(
            y_test, test_preds,
            target_names=["Normal", "Anomaly"]
        ))
        print(f"Confusion Matrix:")
        cm = confusion_matrix(y_test, test_preds)
        print(f"  TN={cm[0,0]:,}  FP={cm[0,1]:,}")
        print(f"  FN={cm[1,0]:,}  TP={cm[1,1]:,}")

    # 5. Save Artifacts
    output_dir = "ml_prediction"
    os.makedirs(output_dir, exist_ok=True)

    torch.save(model.state_dict(), os.path.join(output_dir, "anomaly_pytorch_model.pt"))
    joblib.dump(scaler, os.path.join(output_dir, "anomaly_scaler.joblib"))
    joblib.dump(encoder, os.path.join(output_dir, "anomaly_encoder.joblib"))
    joblib.dump(input_dim, os.path.join(output_dir, "anomaly_input_dim.joblib"))

    print(f"\nSuccessfully trained & saved PyTorch Anomaly model to '{output_dir}'!")
    print(f"  - anomaly_pytorch_model.pt")
    print(f"  - anomaly_scaler.joblib")
    print(f"  - anomaly_encoder.joblib")
    print(f"  - anomaly_input_dim.joblib")


if __name__ == "__main__":
    train_pytorch_anomaly()
