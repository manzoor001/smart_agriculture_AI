import json
from pathlib import Path

import tensorflow as tf
from tensorflow.keras import layers, models


# ============================================================
# Configuration
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

TRAIN_DIR = BASE_DIR / "dataset" / "train"
VALIDATION_DIR = BASE_DIR / "dataset" / "validation"
MODEL_DIR = BASE_DIR / "models"

IMAGE_SIZE = (224, 224)
BATCH_SIZE = 32
EPOCHS = 10
SEED = 42
NUM_CLASSES = 15


# ============================================================
# Create model directory
# ============================================================

MODEL_DIR.mkdir(parents=True, exist_ok=True)


# ============================================================
# Load datasets
# ============================================================

train_dataset = tf.keras.utils.image_dataset_from_directory(
    TRAIN_DIR,
    image_size=IMAGE_SIZE,
    batch_size=BATCH_SIZE,
    shuffle=True,
    seed=SEED
)

validation_dataset = tf.keras.utils.image_dataset_from_directory(
    VALIDATION_DIR,
    image_size=IMAGE_SIZE,
    batch_size=BATCH_SIZE,
    shuffle=False
)


# ============================================================
# Get class names
# ============================================================

class_names = train_dataset.class_names

print("\nClasses:")

for index, name in enumerate(class_names):
    print(f"{index}: {name}")


# ============================================================
# Data augmentation
# ============================================================

data_augmentation = tf.keras.Sequential([
    layers.RandomFlip("horizontal"),
    layers.RandomRotation(0.1),
    layers.RandomZoom(0.1),
    layers.RandomContrast(0.1),
])


# ============================================================
# Normalization
# ============================================================

normalization_layer = layers.Rescaling(1.0 / 255)


# ============================================================
# Apply preprocessing
# ============================================================

train_dataset = train_dataset.map(
    lambda images, labels: (
        normalization_layer(
            data_augmentation(images, training=True)
        ),
        labels
    ),
    num_parallel_calls=tf.data.AUTOTUNE
)

validation_dataset = validation_dataset.map(
    lambda images, labels: (
        normalization_layer(images),
        labels
    ),
    num_parallel_calls=tf.data.AUTOTUNE
)


# ============================================================
# Optimize input pipeline
# ============================================================

train_dataset = train_dataset.prefetch(tf.data.AUTOTUNE)
validation_dataset = validation_dataset.prefetch(tf.data.AUTOTUNE)


# ============================================================
# Load MobileNetV2
# ============================================================

base_model = tf.keras.applications.MobileNetV2(
    input_shape=(224, 224, 3),
    include_top=False,
    weights="imagenet"
)

base_model.trainable = False


# ============================================================
# Build model
# ============================================================

model = models.Sequential([
    layers.Input(shape=(224, 224, 3)),

    base_model,

    layers.GlobalAveragePooling2D(),

    layers.Dropout(0.2),

    layers.Dense(NUM_CLASSES, activation="softmax")
])


# ============================================================
# Compile model
# ============================================================

model.compile(
    optimizer=tf.keras.optimizers.Adam(
        learning_rate=0.001
    ),
    loss="sparse_categorical_crossentropy",
    metrics=["accuracy"]
)


# ============================================================
# Save best model
# ============================================================

best_model_path = MODEL_DIR / "plant_disease_model.keras"

checkpoint = tf.keras.callbacks.ModelCheckpoint(
    filepath=best_model_path,
    monitor="val_accuracy",
    save_best_only=True,
    mode="max",
    verbose=1
)


# ============================================================
# Early stopping
# ============================================================

early_stopping = tf.keras.callbacks.EarlyStopping(
    monitor="val_accuracy",
    patience=3,
    mode="max",
    restore_best_weights=True,
    verbose=1
)


# ============================================================
# Train
# ============================================================

print("\nStarting training...\n")

history = model.fit(
    train_dataset,
    validation_data=validation_dataset,
    epochs=EPOCHS,
    callbacks=[
        checkpoint,
        early_stopping
    ]
)


# ============================================================
# Save class names
# ============================================================

class_names_path = MODEL_DIR / "class_names.json"

with open(class_names_path, "w", encoding="utf-8") as file:
    json.dump(class_names, file, indent=4)


# ============================================================
# Training complete
# ============================================================

print("\n========================================")
print("Training completed!")
print("========================================")

print(f"\nBest model saved to:")
print(best_model_path)

print(f"\nClass names saved to:")
print(class_names_path)