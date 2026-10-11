import pandas as pd
import numpy as np
import json
from pathlib import Path


# --------------------------------------------------
# 1. Paths
# --------------------------------------------------

BASE_DIR = Path(__file__).resolve().parents[2]

DATASET_PATH = BASE_DIR / "ml" / "dataset" / "fertilizer.csv"
MODEL_PATH = BASE_DIR / "ml" / "models" / "fertilizer_model_numpy.npz"


# --------------------------------------------------
# 2. Load dataset
# --------------------------------------------------

df = pd.read_csv(DATASET_PATH)

df.columns = df.columns.str.strip()

print("Dataset loaded successfully!")
print("Rows:", len(df))
print("Columns:", list(df.columns))


# --------------------------------------------------
# 3. Clean categorical values
# --------------------------------------------------

df["Soil Type"] = df["Soil Type"].astype(str).str.strip()
df["Crop Type"] = df["Crop Type"].astype(str).str.strip()
df["Fertilizer Name"] = df["Fertilizer Name"].astype(str).str.strip()


# --------------------------------------------------
# 4. Create mappings
# --------------------------------------------------

soil_types = sorted(df["Soil Type"].unique())
crop_types = sorted(df["Crop Type"].unique())
fertilizers = sorted(df["Fertilizer Name"].unique())

soil_mapping = {
    name: index
    for index, name in enumerate(soil_types)
}

crop_mapping = {
    name: index
    for index, name in enumerate(crop_types)
}

fertilizer_mapping = {
    name: index
    for index, name in enumerate(fertilizers)
}


# --------------------------------------------------
# 5. Convert categorical values to numbers
# --------------------------------------------------

df["Soil Type"] = df["Soil Type"].map(soil_mapping)
df["Crop Type"] = df["Crop Type"].map(crop_mapping)
df["Fertilizer Name"] = df["Fertilizer Name"].map(fertilizer_mapping)


# --------------------------------------------------
# 6. Prepare features
# --------------------------------------------------

feature_columns = [
    "Temparature",
    "Humidity",
    "Moisture",
    "Soil Type",
    "Crop Type",
    "Nitrogen",
    "Potassium",
    "Phosphorous"
]

X = df[feature_columns].values.astype(float)

y = df["Fertilizer Name"].values.astype(int)


# --------------------------------------------------
# 7. Normalize numeric features
# --------------------------------------------------

means = X.mean(axis=0)
stds = X.std(axis=0)

stds[stds == 0] = 1

X_normalized = (X - means) / stds


# --------------------------------------------------
# 8. Save model data
# --------------------------------------------------

metadata = {
    "soil_mapping": soil_mapping,
    "crop_mapping": crop_mapping,
    "fertilizer_mapping": fertilizer_mapping,
    "feature_columns": feature_columns,
    "means": means.tolist(),
    "stds": stds.tolist()
}

MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)

np.savez(
    MODEL_PATH,
    X=X_normalized,
    y=y,
    metadata=json.dumps(metadata)
)


# --------------------------------------------------
# 9. Display information
# --------------------------------------------------

print("\nModel data prepared successfully!")

print("Soil types:", soil_types)
print("Crop types:", crop_types)
print("Fertilizers:", fertilizers)

print("\nFeature count:", X.shape[1])
print("Training records:", X.shape[0])

print("\nModel saved to:")
print(MODEL_PATH)