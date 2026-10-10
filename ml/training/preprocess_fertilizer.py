import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder


# 1. Load dataset
DATASET_PATH = "../dataset/fertilizer.csv"

df = pd.read_csv(DATASET_PATH)

print("Dataset loaded successfully!")
print("Shape:", df.shape)


# 2. Clean column names
df.columns = df.columns.str.strip()

print("\nColumns:")
print(df.columns.tolist())


# 3. Separate features and target
X = df.drop("Fertilizer Name", axis=1)
y = df["Fertilizer Name"]


# 4. Encode categorical columns
soil_encoder = LabelEncoder()
crop_encoder = LabelEncoder()

X["Soil Type"] = soil_encoder.fit_transform(X["Soil Type"])
X["Crop Type"] = crop_encoder.fit_transform(X["Crop Type"])


# 5. Encode target labels
fertilizer_encoder = LabelEncoder()
y = fertilizer_encoder.fit_transform(y)


# 6. Split dataset
X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42,
    stratify=y
)


# 7. Display results
print("\nPreprocessing completed!")

print("Training samples:", len(X_train))
print("Testing samples:", len(X_test))

print("\nFeature columns:")
print(X.columns.tolist())

print("\nFertilizer classes:")
print(fertilizer_encoder.classes_)