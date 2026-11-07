
from pathlib import Path
import math

import joblib
import pandas as pd

from src.feature_engineering.features import FEATURE_COLUMNS


# --------------------------------------------------
# MODEL FILE PATH
# Must match train_model.py
# --------------------------------------------------

MODEL_PATH = (
    Path(__file__).resolve().parents[2]
    / "models"
    / "model_registry"
    / "performance_model.joblib"
)


# --------------------------------------------------
# 1. LOAD TRAINED MODEL
# --------------------------------------------------

def load_model():

    if not MODEL_PATH.exists():
        raise FileNotFoundError(
            "Trained model not found. Please train a model first."
        )

    artifact = joblib.load(MODEL_PATH)

    if not isinstance(artifact, dict):
        raise ValueError("Invalid model artifact format.")

    model = artifact.get("model")
    features = artifact.get("features")

    if model is None:
        raise ValueError("Model is missing from saved artifact.")

    if features != FEATURE_COLUMNS:
        raise ValueError(
            "Saved model features do not match current feature columns. "
            "Please retrain the model."
        )

    return artifact


# --------------------------------------------------
# 2. CHECK MODEL STATUS
# --------------------------------------------------

def model_status():

    if not MODEL_PATH.exists():

        return {
            "ready": False,
            "model": None,
            "message": "No trained model available."
        }

    try:

        artifact = load_model()

        return {
            "ready": True,
            "model": artifact.get("name", "Unknown"),
            "message": "Trained model loaded successfully."
        }

    except Exception as exc:

        return {
            "ready": False,
            "model": None,
            "message": str(exc)
        }


# --------------------------------------------------
# 3. VALIDATE STUDENT RECORD
# --------------------------------------------------

def validate_student_record(record):

    if not isinstance(record, dict):
        raise ValueError(
            "Student record must be provided as a dictionary."
        )

    validated = {}

    for feature in FEATURE_COLUMNS:

        if feature not in record:
            raise ValueError(
                f"Missing required feature: {feature}"
            )

        value = record[feature]

        if value is None:
            raise ValueError(
                f"{feature} cannot be empty."
            )

        try:
            numeric_value = float(value)

        except (TypeError, ValueError):
            raise ValueError(
                f"{feature} must contain a numeric value."
            )

        if not math.isfinite(numeric_value):
            raise ValueError(
                f"{feature} must be a finite number."
            )

        validated[feature] = numeric_value

    # Attendance validation
    if not 0 <= validated["Attendance"] <= 100:
        raise ValueError(
            "Attendance must be between 0 and 100."
        )

    # Marks validation
    mark_features = [
        "Internal_Marks",
        "Assignment_Marks",
        "Quiz_Marks"
    ]

    for feature in mark_features:

        if not 0 <= validated[feature] <= 100:
            raise ValueError(
                f"{feature} must be between 0 and 100."
            )

    # Study hours validation
    if validated["Study_Hours"] < 0:
        raise ValueError(
            "Study hours cannot be negative."
        )

    if validated["Study_Hours"] > 24:
        raise ValueError(
            "Study hours cannot exceed 24 per day."
        )

    # CGPA validation
    if validated["Previous_CGPA"] < 0:
        raise ValueError(
            "Previous CGPA cannot be negative."
        )

    # Backlog validation
    if (
        validated["Backlogs"] < 0
        or not validated["Backlogs"].is_integer()
    ):
        raise ValueError(
            "Backlogs must be a non-negative integer."
        )

    validated["Backlogs"] = int(
        validated["Backlogs"]
    )

    return validated


# --------------------------------------------------
# 4. PREDICT STUDENT PERFORMANCE
# --------------------------------------------------

def predict_student(record):

    # Validate input
    validated = validate_student_record(record)

    # Load trained model
    artifact = load_model()

    model = artifact["model"]

    # Arrange input in training feature order
    input_df = pd.DataFrame(
        [validated],
        columns=FEATURE_COLUMNS
    )

    # Generate prediction
    prediction = model.predict(input_df)

    predicted_marks = float(prediction[0])

    if not math.isfinite(predicted_marks):
        raise ValueError(
            "Model returned an invalid prediction."
        )

    # Final marks are on a 0-100 scale in the current model
    predicted_marks = max(
        0.0,
        min(100.0, predicted_marks)
    )

    return predicted_marks


# --------------------------------------------------
# 5. GET MODEL INFORMATION
# --------------------------------------------------

def get_model_info():

    artifact = load_model()

    return {
        "model": artifact.get("name", "Unknown"),
        "features": artifact.get("features", []),
        "background": artifact.get("background"),
        "model_path": str(MODEL_PATH)
    }
