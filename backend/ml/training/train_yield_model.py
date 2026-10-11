import pandas as pd
import numpy as np
import joblib
import os

import xgboost as xgb


# ============================================================
# 1. Load Dataset
# ============================================================

DATASET_PATH = "ml/data/crop_yield_dataset.csv"

df = pd.read_csv(DATASET_PATH)

print("Dataset loaded successfully!")
print("Rows:", len(df))
print("Columns:", len(df.columns))


# ============================================================
# 2. Define Features
# ============================================================

numerical_features = [
    "Year",
    "Temperature",
    "Rainfall",
    "Humidity",
    "pH",
    "Nitrogen",
    "Phosphorus",
    "Potassium",
    "Fertilizer",
    "Pesticide"
]

categorical_features = [
    "Region",
    "Crop",
    "Season",
    "Soil Type"
]

all_features = numerical_features + categorical_features

target = "Yield"


# ============================================================
# 3. Create X and y
# ============================================================

X = df[all_features].copy()

y = df[target].copy()


# ============================================================
# 4. One-Hot Encoding
# ============================================================

print("\nApplying One-Hot Encoding...")

X = pd.get_dummies(
    X,
    columns=categorical_features,
    dtype=int
)

print("One-Hot Encoding completed!")
print("Total features after encoding:", X.shape[1])


# ============================================================
# 5. Train/Test Split
# ============================================================

print("\nSplitting dataset...")

split_index = int(len(X) * 0.80)

X_train = X.iloc[:split_index].copy()
X_test = X.iloc[split_index:].copy()

y_train = y.iloc[:split_index].copy()
y_test = y.iloc[split_index:].copy()

print("Training data:", X_train.shape)
print("Testing data:", X_test.shape)


# ============================================================
# 6. Convert Data to XGBoost DMatrix
# ============================================================

print("\nPreparing data for XGBoost...")

dtrain = xgb.DMatrix(
    X_train,
    label=y_train,
    feature_names=list(X.columns)
)

dtest = xgb.DMatrix(
    X_test,
    label=y_test,
    feature_names=list(X.columns)
)

print("XGBoost data preparation completed!")


# ============================================================
# 7. Define XGBoost Parameters
# ============================================================

params = {
    "objective": "reg:squarederror",
    "max_depth": 8,
    "learning_rate": 0.05,
    "subsample": 0.8,
    "colsample_bytree": 0.8,
    "eval_metric": "rmse",
    "seed": 42
}


# ============================================================
# 8. Train XGBoost Model
# ============================================================

print("\nTraining XGBoost model...")

model = xgb.train(
    params=params,
    dtrain=dtrain,
    num_boost_round=300,
    evals=[
        (dtrain, "train"),
        (dtest, "test")
    ],
    verbose_eval=50
)

print("XGBoost model training completed!")


# ============================================================
# 9. Make Predictions
# ============================================================

print("\nMaking predictions on test data...")

y_pred = model.predict(dtest)

print("Predictions completed!")


# ============================================================
# 10. Calculate Evaluation Metrics
# ============================================================

mae = np.mean(
    np.abs(y_test.values - y_pred)
)

rmse = np.sqrt(
    np.mean(
        (y_test.values - y_pred) ** 2
    )
)

ss_res = np.sum(
    (y_test.values - y_pred) ** 2
)

ss_tot = np.sum(
    (y_test.values - np.mean(y_test.values)) ** 2
)

r2 = 1 - (ss_res / ss_tot)


# ============================================================
# 11. Display Results
# ============================================================

print("\n========================================")
print("XGBOOST YIELD PREDICTION MODEL RESULTS")
print("========================================")

print(f"MAE  : {mae:.2f}")
print(f"RMSE : {rmse:.2f}")
print(f"R²   : {r2:.4f}")

print("========================================")


# ============================================================
# 12. Save Trained Model
# ============================================================

model_path = "ml/models/yield_model.json"

os.makedirs(
    "ml/models",
    exist_ok=True
)

model.save_model(model_path)

print("\nModel saved successfully!")
print(f"Model path: {model_path}")


# ============================================================
# 13. Save Feature Names
# ============================================================

features_path = "ml/models/yield_features.pkl"

joblib.dump(
    list(X.columns),
    features_path
)

print("\nFeature list saved successfully!")
print(f"Feature path: {features_path}")
