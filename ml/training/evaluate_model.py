import json
from pathlib import Path

import tensorflow as tf
from sklearn.metrics import classification_report, confusion_matrix

BASE_DIR = Path(__file__).resolve().parent.parent

TEST_DIR = BASE_DIR / "dataset" / "test"
MODEL_PATH = BASE_DIR / "models" / "plant_disease_model.keras"
CLASS_NAMES_PATH = BASE_DIR / "models" / "class_names.json"

IMAGE_SIZE = (224, 224)
BATCH_SIZE = 32

print("Loading trained model...")

model = tf.keras.models.load_model(MODEL_PATH)

print("Model loaded successfully!")

print("\nLoading test dataset...")

test_dataset = tf.keras.utils.image_dataset_from_directory(
    TEST_DIR,
    image_size=IMAGE_SIZE,
    batch_size=BATCH_SIZE,
    shuffle=False
)

with open(CLASS_NAMES_PATH, "r", encoding="utf-8") as file:
    class_names = json.load(file)

normalization_layer = tf.keras.layers.Rescaling(1.0 / 255)

test_dataset = test_dataset.map(
    lambda images, labels: (
        normalization_layer(images),
        labels
    ),
    num_parallel_calls=tf.data.AUTOTUNE
)

test_dataset = test_dataset.prefetch(tf.data.AUTOTUNE)

print("\nEvaluating model on test dataset...")

test_loss, test_accuracy = model.evaluate(test_dataset)

print("\n========================================")
print("TEST RESULTS")
print("========================================")

print(f"Test Loss: {test_loss:.4f}")
print(f"Test Accuracy: {test_accuracy * 100:.2f}%")

print("\nGenerating predictions...")

y_true = []
y_pred = []

for images, labels in test_dataset:
    predictions = model.predict(images, verbose=0)

    predicted_classes = tf.argmax(
        predictions,
        axis=1
    ).numpy()

    y_true.extend(labels.numpy())
    y_pred.extend(predicted_classes)

print("\n========================================")
print("CLASSIFICATION REPORT")
print("========================================")

print(
    classification_report(
        y_true,
        y_pred,
        target_names=class_names,
        digits=4
    )
)

print("\n========================================")
print("CONFUSION MATRIX")
print("========================================")

cm = confusion_matrix(y_true, y_pred)

print(cm)

print("\n========================================")
print("Evaluation completed!")
print("========================================")
