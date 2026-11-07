
from pathlib import Path

import numpy as np
import pandas as pd
import joblib

from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split, cross_val_score, KFold
from sklearn.metrics import (
    mean_absolute_error,
    mean_squared_error,
    r2_score
)

from src.feature_engineering.features import FEATURE_COLUMNS
from database.database import get_connection


MODEL_PATH = (
    Path(__file__).resolve().parents[2]
    / "models"
    / "model_registry"
    / "performance_model.joblib"
)


def _fit(X, y):

    # Validate training data
    X = X.copy()
    y = pd.Series(y).copy()

    X = X.apply(pd.to_numeric, errors="coerce")
    y = pd.to_numeric(y, errors="coerce")

    X = X.replace([np.inf, -np.inf], np.nan)
    y = y.replace([np.inf, -np.inf], np.nan)

    valid_rows = X.notna().all(axis=1) & y.notna()

    X = X.loc[valid_rows].reset_index(drop=True)
    y = y.loc[valid_rows].reset_index(drop=True)

    if len(X) < 20:
        raise ValueError(
            "At least 20 valid student records are required for training."
        )

    if not np.isfinite(X.to_numpy()).all():
        raise ValueError("Invalid feature values found.")

    if not np.isfinite(y.to_numpy()).all():
        raise ValueError("Invalid target values found.")

    # Split training and testing data
    Xtr, Xte, ytr, yte = train_test_split(
        X,
        y,
        test_size=0.2,
        random_state=42
    )

    candidates = {
        "Linear Regression": LinearRegression(),

        "Random Forest": RandomForestRegressor(
            n_estimators=180,
            min_samples_leaf=2,
            random_state=42,
            n_jobs=-1
        )
    }

    # Cross-validation on training data only
    kfold = KFold(
        n_splits=5,
        shuffle=True,
        random_state=42
    )

    results = {}
    best_name = None
    best_cv_mae = float("inf")
    best_model = None

    for name, model in candidates.items():

        cv_scores = -cross_val_score(
            model,
            Xtr,
            ytr,
            cv=kfold,
            scoring="neg_mean_absolute_error",
            n_jobs=-1
        )

        cv_mae = float(cv_scores.mean())

        # Fit on training portion for final test evaluation
        model.fit(Xtr, ytr)

        predictions = model.predict(Xte)

        mae = mean_absolute_error(yte, predictions)

        rmse = np.sqrt(
            mean_squared_error(yte, predictions)
        )

        r2 = r2_score(yte, predictions)

        results[name] = {
            "MAE": float(mae),
            "RMSE": float(rmse),
            "R2": float(r2),
            "CV_MAE": cv_mae
        }

        # Select model using cross-validation, not test results
        if cv_mae < best_cv_mae:

            best_cv_mae = cv_mae
            best_name = name
            best_model = candidates[name]

    # Retrain selected model using all valid records
    best_model.fit(X, y)

    # Prepare SHAP background data
    background = X.sample(
        n=min(100, len(X)),
        random_state=42
    ).copy()

    # Save trained model bundle
    MODEL_PATH.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    joblib.dump(
        {
            "model": best_model,
            "features": FEATURE_COLUMNS,
            "name": best_name,
            "background": background,
            "metrics": results[best_name]
        },
        MODEL_PATH
    )

    return {
        "MAE": results[best_name]["MAE"],
        "RMSE": results[best_name]["RMSE"],
        "R2": results[best_name]["R2"],
        "CV_MAE": results[best_name]["CV_MAE"],
        "model": best_name,
        "comparison": results
    }


def train_model_from_database():

    connection = get_connection()

    try:
        df = pd.read_sql_query(
            """
            SELECT
                attendance AS Attendance,
                internal_marks AS Internal_Marks,
                assignment_marks AS Assignment_Marks,
                quiz_marks AS Quiz_Marks,
                study_hours AS Study_Hours,
                previous_cgpa AS Previous_CGPA,
                backlogs AS Backlogs,
                final_marks AS Final_Marks
            FROM academic_records
            WHERE final_marks IS NOT NULL
            """,
            connection
        )

    finally:
        connection.close()

    df = df.replace([np.inf, -np.inf], np.nan)
    df = df.dropna(
        subset=FEATURE_COLUMNS + ["Final_Marks"]
    )

    if len(df) < 20:
        return None

    return _fit(
        df[FEATURE_COLUMNS],
        df["Final_Marks"]
    )


def train_demo_model():

    rng = np.random.default_rng(42)

    n = 700

    X = pd.DataFrame({
        "Attendance": rng.uniform(40, 100, n),
        "Internal_Marks": rng.uniform(20, 100, n),
        "Assignment_Marks": rng.uniform(20, 100, n),
        "Quiz_Marks": rng.uniform(20, 100, n),
        "Study_Hours": rng.uniform(0, 7, n),
        "Previous_CGPA": rng.uniform(4, 10, n),
        "Backlogs": rng.integers(0, 4, n)
    })

    y = (
        0.20 * X.Attendance
        + 0.22 * X.Internal_Marks
        + 0.15 * X.Assignment_Marks
        + 0.13 * X.Quiz_Marks
        + 1.5 * X.Study_Hours
        + 2 * X.Previous_CGPA
        - 2 * X.Backlogs
        + rng.normal(0, 6, n)
    ).clip(0, 100)

    return _fit(X, y)
