import xgboost as xgb
import pandas as pd
import joblib


# ============================================================
# 1. File paths
# ============================================================

MODEL_PATH = "ml/models/yield_model.json"
FEATURE_PATH = "ml/models/yield_features.pkl"


# ============================================================
# 2. Load XGBoost model WITHOUT sklearn
# ============================================================

model = xgb.Booster()
model.load_model(MODEL_PATH)

print("Yield model loaded successfully!")


# ============================================================
# 3. Load feature list
# ============================================================

features = joblib.load(FEATURE_PATH)

print("Feature list loaded successfully!")
print("Number of features:", len(features))


# ============================================================
# 4. Sample farmer input
# ============================================================

sample_data = {
    "Year": 2026,
    "Region": "Anantapur, AndhraPradesh",
    "Crop": "Rice",
    "Season": "Kharif",
    "Temperature": 28,
    "Rainfall": 900,
    "Humidity": 75,
    "Soil Type": "Black",
    "pH": 6.5,
    "Nitrogen": 80,
    "Phosphorus": 40,
    "Potassium": 40,
    "Fertilizer": 100,
    "Pesticide": 20
}


# ============================================================
# 5. Convert input into DataFrame
# ============================================================

input_df = pd.DataFrame([sample_data])

print("\nOriginal input:")
print(input_df)


# ============================================================
# 6. One-Hot Encoding
# ============================================================

input_df = pd.get_dummies(
    input_df,
    columns=["Region", "Crop", "Season", "Soil Type"]
)


# ============================================================
# 7. Make sure input has exactly the same features
# ============================================================

input_df = input_df.reindex(
    columns=features,
    fill_value=0
)


print("\nPrepared input shape:")
print(input_df.shape)


# ============================================================
# 8. Create XGBoost DMatrix
# ============================================================

data = xgb.DMatrix(input_df)


# ============================================================
# 9. Make prediction
# ============================================================

prediction = model.predict(data)


# ============================================================
# 10. Display result
# ============================================================

print("\n========================================")
print("       YIELD PREDICTION")
print("========================================")

print(f"Predicted Yield: {prediction[0]:.2f}")

print("========================================")