import json
from pathlib import Path

import numpy as np
import tensorflow as tf
from PIL import Image


BASE_DIR = Path(__file__).resolve().parents[2]

MODEL_PATH = BASE_DIR / "ml" / "models" / "plant_disease_model.keras"
CLASS_NAMES_PATH = BASE_DIR / "ml" / "models" / "class_names.json"

IMAGE_SIZE = (224, 224)


print("Loading plant disease model...")

model = tf.keras.models.load_model(MODEL_PATH)

print("Plant disease model loaded successfully!")


with open(CLASS_NAMES_PATH, "r", encoding="utf-8") as file:
    class_names = json.load(file)


def predict_disease(image: Image.Image):

    image = image.convert("RGB")

    image = image.resize(IMAGE_SIZE)

    image_array = np.array(image)

    image_array = image_array / 255.0

    image_array = np.expand_dims(image_array, axis=0)

    predictions = model.predict(image_array, verbose=0)

    predicted_index = int(np.argmax(predictions[0]))

    predicted_class = class_names[predicted_index]

    confidence = float(predictions[0][predicted_index])

    return {
        "predicted_disease": predicted_class,
        "confidence": confidence
    }
