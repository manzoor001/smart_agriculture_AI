from pathlib import Path
import random
import shutil

# Paths
BASE_DIR = Path(__file__).resolve().parent.parent
SOURCE_DIR = BASE_DIR / "dataset" / "raw" / "PlantVillage"

TRAIN_DIR = BASE_DIR / "dataset" / "train"
VALIDATION_DIR = BASE_DIR / "dataset" / "validation"
TEST_DIR = BASE_DIR / "dataset" / "test"

# Split ratios
TRAIN_RATIO = 0.70
VALIDATION_RATIO = 0.20
TEST_RATIO = 0.10

# Reproducible random split
random.seed(42)

# Image extensions
IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".JPG", ".JPEG", ".PNG"}

# Make sure destination directories exist
TRAIN_DIR.mkdir(parents=True, exist_ok=True)
VALIDATION_DIR.mkdir(parents=True, exist_ok=True)
TEST_DIR.mkdir(parents=True, exist_ok=True)

# Get class folders
class_dirs = [folder for folder in SOURCE_DIR.iterdir() if folder.is_dir()]

print(f"Found {len(class_dirs)} classes.")

total_images = 0

for class_dir in class_dirs:
    images = [
        image for image in class_dir.iterdir()
        if image.is_file() and image.suffix in IMAGE_EXTENSIONS
    ]

    random.shuffle(images)

    total = len(images)

    train_end = int(total * TRAIN_RATIO)
    validation_end = train_end + int(total * VALIDATION_RATIO)

    train_images = images[:train_end]
    validation_images = images[train_end:validation_end]
    test_images = images[validation_end:]

    # Create class folders
    train_class_dir = TRAIN_DIR / class_dir.name
    validation_class_dir = VALIDATION_DIR / class_dir.name
    test_class_dir = TEST_DIR / class_dir.name

    train_class_dir.mkdir(parents=True, exist_ok=True)
    validation_class_dir.mkdir(parents=True, exist_ok=True)
    test_class_dir.mkdir(parents=True, exist_ok=True)

    # Copy images
    for image in train_images:
        shutil.copy2(image, train_class_dir / image.name)

    for image in validation_images:
        shutil.copy2(image, validation_class_dir / image.name)

    for image in test_images:
        shutil.copy2(image, test_class_dir / image.name)

    total_images += total

    print(
        f"{class_dir.name}: "
        f"{len(train_images)} train, "
        f"{len(validation_images)} validation, "
        f"{len(test_images)} test"
    )

print("\nDataset split completed!")
print(f"Total images processed: {total_images}")