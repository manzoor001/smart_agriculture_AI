import pandas as pd
import joblib

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix
)


# 1. Load dataset
DATASET_PATH = "../dataset/fertilizer.csv"

df = pd.read_csv(DATASET_PATH)

print("Dataset loaded successfully!")


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


# 6. Split dataset using the same random state
X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42,
    stratify=y
)


# 7. Load trained model
MODEL_PATH = "../models/fertilizer_model.pkl"

saved_data = joblib.load(MODEL_PATH)

model = saved_data["model"]


# 8. Make predictions
y_pred = model.predict(X_test)


# 9. Accuracy
accuracy = accuracy_score(y_test, y_pred)

print("\n==============================")
print("MODEL EVALUATION")
print("==============================")

print("\nAccuracy:")
print(round(accuracy * 100, 2), "%")


# 10. Classification report
print("\nClassification Report:")
print(
    classification_report(
        y_test,
        y_pred,
        target_names=fertilizer_encoder.classes_
    )
)


# 11. Confusion matrix
print("Confusion Matrix:")

cm = confusion_matrix(y_test, y_pred)

print(cm)