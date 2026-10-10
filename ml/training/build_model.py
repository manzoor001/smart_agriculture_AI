import tensorflow as tf
from tensorflow.keras import layers, models


# ============================================================
# Configuration
# ============================================================

IMAGE_SIZE = (224, 224)
NUM_CLASSES = 15


# ============================================================
# Load MobileNetV2
# ============================================================

base_model = tf.keras.applications.MobileNetV2(
    input_shape=(224, 224, 3),
    include_top=False,
    weights="imagenet"
)


# Freeze the pre-trained layers
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
# Compile
# ============================================================

model.compile(
    optimizer=tf.keras.optimizers.Adam(
        learning_rate=0.001
    ),
    loss="sparse_categorical_crossentropy",
    metrics=["accuracy"]
)


# ============================================================
# Display model
# ============================================================

model.summary()