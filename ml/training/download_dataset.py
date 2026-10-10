import kagglehub
import shutil
from pathlib import Path

# Download PlantVillage dataset
dataset_path = kagglehub.dataset_download(
    "emmarex/plantdisease"
)

print("Dataset downloaded to:")
print(dataset_path)

# Project dataset directory
project_dataset = Path(__file__).resolve().parent.parent / "dataset" / "raw"

# Create raw dataset directory
project_dataset.mkdir(parents=True, exist_ok=True)

# Copy downloaded dataset into our project
source = Path(dataset_path)

for item in source.iterdir():
    destination = project_dataset / item.name

    if item.is_dir():
        shutil.copytree(item, destination, dirs_exist_ok=True)
    else:
        shutil.copy2(item, destination)

print("\nDataset copied to:")
print(project_dataset)