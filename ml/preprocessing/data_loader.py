import tensorflow as tf
from pathlib import Path

# ============================================================
# Configuration
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent
DATASET_DIR = BASE_DIR / "dataset"

TRAIN_DIR = DATASET_DIR / "train"
VALIDATION_DIR = DATASET_DIR / "validation"
TEST_DIR = DATASET_DIR / "test"

IMAGE_SIZE = (224, 224)
BATCH_SIZE = 32
SEED = 42


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

test_dataset = tf.keras.utils.image_dataset_from_directory(
    TEST_DIR,
    image_size=IMAGE_SIZE,
    batch_size=BATCH_SIZE,
    shuffle=False
)


# ============================================================
# Class names
# ============================================================

class_names = train_dataset.class_names

print("\nClasses:")
for index, name in enumerate(class_names):
    print(f"{index}: {name}")


# ============================================================
# Data augmentation
# ============================================================

data_augmentation = tf.keras.Sequential([
    tf.keras.layers.RandomFlip("horizontal"),
    tf.keras.layers.RandomRotation(0.1),
    tf.keras.layers.RandomZoom(0.1),
    tf.keras.layers.RandomContrast(0.1),
])


# ============================================================
# Normalization
# ============================================================

normalization_layer = tf.keras.layers.Rescaling(
    1.0 / 255
)


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

test_dataset = test_dataset.map(
    lambda images, labels: (
        normalization_layer(images),
        labels
    ),
    num_parallel_calls=tf.data.AUTOTUNE
)


# ============================================================
# Performance optimization
# ============================================================

train_dataset = train_dataset.prefetch(
    tf.data.AUTOTUNE
)

validation_dataset = validation_dataset.prefetch(
    tf.data.AUTOTUNE
)

test_dataset = test_dataset.prefetch(
    tf.data.AUTOTUNE
)


# ============================================================
# Test one batch
# ============================================================

if __name__ == "__main__":

    images, labels = next(iter(train_dataset))

    print("\nPreprocessing test:")
    print("Image shape:", images.shape)
    print("Label shape:", labels.shape)
    print("Pixel minimum:", tf.reduce_min(images).numpy())
    print("Pixel maximum:", tf.reduce_max(images).numpy())

    print("\nData preprocessing is working correctly!")