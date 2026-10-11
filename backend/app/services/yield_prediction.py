import os

import joblib
import pandas as pd
import xgboost as xgb


# ============================================================
# Paths
# ============================================================

BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.dirname(os.path.abspath(__file__))
    )
)

MODEL_PATH = os.path.join(
    BASE_DIR,
    "ml",
    "models",
    "yield_model.json"
)

FEATURE_PATH = os.path.join(
    BASE_DIR,
    "ml",
    "models",
    "yield_features.pkl"
)


# ============================================================
# Load model
# ============================================================

model = xgb.Booster()
model.load_model(MODEL_PATH)

features = joblib.load(FEATURE_PATH)


# ============================================================
# Prediction function
# ============================================================

def predict_yield(data):

    input_data = {
        "Year": data.year,
        "Region": data.region,
        "Crop": data.crop,
        "Season": data.season,
        "Temperature": data.temperature,
        "Rainfall": data.rainfall,
        "Humidity": data.humidity,
        "Soil Type": data.soil_type,
        "pH": data.ph,
        "Nitrogen": data.nitrogen,
        "Phosphorus": data.phosphorus,
        "Potassium": data.potassium,
        "Fertilizer": data.fertilizer,
        "Pesticide": data.pesticide
    }

    df = pd.DataFrame([input_data])

    # One-Hot Encoding
    df = pd.get_dummies(
        df,
        columns=[
            "Region",
            "Crop",
            "Season",
            "Soil Type"
        ]
    )

    # Make sure we have exactly the same
    # 349 features used during training
    df = df.reindex(
        columns=features,
        fill_value=0
    )

    # Convert to XGBoost DMatrix
    dmatrix = xgb.DMatrix(df)

    # Prediction
    prediction = model.predict(dmatrix)

    return float(prediction[0])