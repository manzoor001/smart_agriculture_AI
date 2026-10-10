import json
from pathlib import Path

import numpy as np


# --------------------------------------------------
# Paths
# --------------------------------------------------

BASE_DIR = Path(__file__).resolve().parents[1]

MODEL_PATH = BASE_DIR / "ml" / "models" / "fertilizer_model_numpy.npz"


# --------------------------------------------------
# Load model data
# --------------------------------------------------

data = np.load(
    MODEL_PATH,
    allow_pickle=False
)

X = data["X"]
y = data["y"]

metadata = json.loads(
    str(data["metadata"])
)

soil_mapping = metadata["soil_mapping"]
crop_mapping = metadata["crop_mapping"]
fertilizer_mapping = metadata["fertilizer_mapping"]

means = np.array(metadata["means"])
stds = np.array(metadata["stds"])


# Reverse fertilizer mapping

fertilizer_names = {
    value: key
    for key, value in fertilizer_mapping.items()
}


# --------------------------------------------------
# Prediction function
# --------------------------------------------------

def predict_fertilizer(
    temperature,
    humidity,
    moisture,
    soil_type,
    crop_type,
    nitrogen,
    potassium,
    phosphorus
):

    # Check soil type
    if soil_type not in soil_mapping:
        raise ValueError(
            f"Unknown soil type: {soil_type}"
        )

    # Check crop type
    if crop_type not in crop_mapping:
        raise ValueError(
            f"Unknown crop type: {crop_type}"
        )


    # Create input

    input_data = np.array([
        temperature,
        humidity,
        moisture,
        soil_mapping[soil_type],
        crop_mapping[crop_type],
        nitrogen,
        potassium,
        phosphorus
    ], dtype=float)


    # Normalize input

    input_normalized = (
        input_data - means
    ) / stds


    # --------------------------------------------------
    # Calculate distances
    # --------------------------------------------------

    distances = np.sqrt(
        np.sum(
            (X - input_normalized) ** 2,
            axis=1
        )
    )


    # Find nearest records

    k = 5

    nearest_indices = np.argsort(distances)[:k]

    nearest_labels = y[nearest_indices]


    # --------------------------------------------------
    # Majority vote
    # --------------------------------------------------

    counts = np.bincount(
        nearest_labels,
        minlength=len(fertilizer_mapping)
    )

    predicted_label = int(
        np.argmax(counts)
    )


    fertilizer_name = fertilizer_names[
        predicted_label
    ]


    return {
        "recommended_fertilizer": fertilizer_name,
        "nearest_records": k
    }