import pandas as pd
import joblib

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score


# 1. Load dataset
DATASET_PATH = "../dataset/fertilizer.csv"

df = pd.read_csv(DATASET_PATH)

print("Dataset loaded successfully!")
print("Shape:", df.shape)


# 2. Clean column names
df.columns = df.columns.str.strip()


# 3. Separate features and target
X = df.drop("Fertilizer Name", axis=1)
y = df["Fertilizer Name"]


# 4. Encode categorical features
soil_encoder = LabelEncoder()
crop_encoder = LabelEncoder()

X["Soil Type"] = soil_encoder.fit_transform(X["Soil Type"])
X["Crop Type"] = crop_encoder.fit_transform(X["Crop Type"])


# 5. Encode target
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


# 7. Create Random Forest model
model = RandomForestClassifier(
    n_estimators=100,
    random_state=42
)


# 8. Train model
print("\nTraining model...")

model.fit(X_train, y_train)

print("Model training completed!")


# 9. Make predictions
y_pred = model.predict(X_test)


# 10. Evaluate accuracy
accuracy = accuracy_score(y_test, y_pred)

print("\nModel Accuracy:", accuracy)
print("Model Accuracy (%):", round(accuracy * 100, 2), "%")


# 11. Save model and encoders
MODEL_PATH = "../models/fertilizer_model.pkl"

joblib.dump(
    {
        "model": model,
        "soil_encoder": soil_encoder,
        "crop_encoder": crop_encoder,
        "fertilizer_encoder": fertilizer_encoder
    },
    MODEL_PATH
)

print("\nModel saved successfully!")
print("Location:", MODEL_PATH)